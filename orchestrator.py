"""
Orquestador principal del pipeline de proyección MLB.
Ejecuta el flujo completo: ingestión → features → modelado → output.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import asdict

import pandas as pd
from tabulate import tabulate

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from config.settings import PIPELINE_CFG, MODEL_CFG
from src.client.sportsdata_client import SportsDataClient
from src.ingestion.data_fetcher import MLBDataIngestor
from src.features.feature_engineering import FeatureEngineer, TeamFeatureVector, HitterFeatureVector
from src.features.sabermetrics import SabermetricsCalculator
from src.modeling.projection_models import RunProjectionModel, HitsProjectionModel
from src.models.schemas import (
    Game, MoneylineProjection, TeamProjection, PlayerHitProjection,
    PlayerSeasonStats, StartingLineup, PlayerBasic,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("MLBProjectionPipeline")


class MLBProjectionPipeline:
    """
    Pipeline end-to-end para proyección de mercados MLB.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        season: Optional[str] = None,
        n_simulations: int = 10_000,
    ) -> None:
        self.client = SportsDataClient(api_key=api_key)
        self.ingestor = MLBDataIngestor(client=self.client, season=season)
        self.feature_engineer = FeatureEngineer()
        self.run_model = RunProjectionModel()
        self.hits_model = HitsProjectionModel()
        self.n_sims = n_simulations
        self.season = season or PIPELINE_CFG.SEASON

    def run(self, date_str: str) -> Dict:
        """
        Ejecuta el pipeline completo para una fecha dada.
        Formato fecha: '2026-SEP-05'
        """
        logger.info("=" * 70)
        logger.info("INICIANDO PIPELINE MLB | Fecha: %s | Season: %s", date_str, self.season)
        logger.info("=" * 70)

        # -----------------------------------------------------------------
        # 1. INGESTA
        # -----------------------------------------------------------------
        logger.info("[1/4] INGESTA DE DATOS")
        games = self.ingestor.get_scheduled_games(date_str)
        if not games:
            logger.warning("No hay juegos programados para %s", date_str)
            return {"games_projected": 0}

        logger.info("Juegos encontrados: %d", len(games))

        # Precarga de datos comunes
        teams = self.ingestor.get_teams()
        lineups_map = self.ingestor.build_lineup_map(date_str)
        projected_stats = self.ingestor.get_projected_player_stats(date_str)

        # Mapas de lookups
        player_stats_by_team: Dict[str, List[PlayerSeasonStats]] = {}
        team_season_stats: Dict[str, Optional[PlayerSeasonStats]] = {}

        team_keys_needed = set()
        for g in games:
            team_keys_needed.add(g.AwayTeam)
            team_keys_needed.add(g.HomeTeam)

        for tk in team_keys_needed:
            player_stats_by_team[tk] = self.ingestor.get_player_season_stats_by_team(tk)
            team_season_stats[tk] = self.ingestor.get_team_season_stats(tk)

        # Splits L/R
        split_stats_l = {s.PlayerID: s for s in self.ingestor.get_player_season_split_stats("L")}
        split_stats_r = {s.PlayerID: s for s in self.ingestor.get_player_season_split_stats("R")}

        # -----------------------------------------------------------------
        # 2. FEATURE ENGINEERING
        # -----------------------------------------------------------------
        logger.info("[2/4] INGENIERÍA DE CARACTERÍSTICAS")

        moneyline_projections: List[MoneylineProjection] = []
        team_projections: List[TeamProjection] = []
        player_hit_projections: List[PlayerHitProjection] = []

        for game in games:
            away_key = game.AwayTeam
            home_key = game.HomeTeam

            if not away_key or not home_key:
                continue

            # Obtener SP IDs
            away_sp_id = game.AwayTeamStartingPitcherID
            home_sp_id = game.HomeTeamStartingPitcherID

            # Buscar stats de SP
            away_sp_stats = None
            home_sp_stats = None
            for ps in player_stats_by_team.get(away_key, []):
                if ps.PlayerID == away_sp_id:
                    away_sp_stats = ps
            for ps in player_stats_by_team.get(home_key, []):
                if ps.PlayerID == home_sp_id:
                    home_sp_stats = ps

            # Team season stats (bateo + pitcheo agregado)
            away_team_stats = team_season_stats.get(away_key)
            home_team_stats = team_season_stats.get(home_key)

            # Construir feature vectors
            away_offense = self.feature_engineer.build_team_features(
                team_key=away_key,
                team_stats=away_team_stats,
                starter_stats=home_sp_stats,  # El SP oponente es la defensa
                bullpen_stats=home_team_stats,
                game=game,
                is_home=False,
                opponent_team_key=home_key,
            )
            home_offense = self.feature_engineer.build_team_features(
                team_key=home_key,
                team_stats=home_team_stats,
                starter_stats=away_sp_stats,
                bullpen_stats=away_team_stats,
                game=game,
                is_home=True,
                opponent_team_key=away_key,
            )

            # -----------------------------------------------------------------
            # 3. MODELO MONEYLINE / TEAM TOTALS
            # -----------------------------------------------------------------
            ml_proj = self.run_model.simulate_moneyline(
                away_offense=away_offense,
                home_offense=home_offense,
                away_defense=home_offense,  # Defensa away = ofensiva home (invertido)
                home_defense=away_offense,
                game=game,
                n_sims=self.n_sims,
            )
            moneyline_projections.append(ml_proj)

            # Team totals individuales
            away_proj = self.run_model.project_team_runs(away_offense, home_offense)
            home_proj = self.run_model.project_team_runs(home_offense, away_offense)
            team_projections.extend([away_proj, home_proj])

            # -----------------------------------------------------------------
            # 4. PLAYER PROPS - HITS
            # -----------------------------------------------------------------
            # Obtener lineup del equipo away
            away_lineup = lineups_map.get(away_key)
            home_lineup = lineups_map.get(home_key)

            pitcher_hand_home = "R"
            pitcher_hand_away = "R"
            if home_sp_stats and home_sp_stats.ThrowHand:
                pitcher_hand_home = home_sp_stats.ThrowHand
            if away_sp_stats and away_sp_stats.ThrowHand:
                pitcher_hand_away = away_sp_stats.ThrowHand

            # Procesar bateadores away
            if away_lineup:
                for lu_player in away_lineup.Players:
                    player_stats = None
                    for ps in player_stats_by_team.get(away_key, []):
                        if ps.PlayerID == lu_player.PlayerID:
                            player_stats = ps
                            break

                    if not player_stats:
                        continue

                    # Split stats
                    split_stats = None
                    if pitcher_hand_home == "L":
                        split_stats = split_stats_l.get(lu_player.PlayerID)
                    else:
                        split_stats = split_stats_r.get(lu_player.PlayerID)

                    hitter_vec = self.feature_engineer.build_hitter_features(
                        player_stats=player_stats,
                        player_splits=split_stats,
                        pitcher_stats=home_sp_stats,
                        game=game,
                        batting_order=lu_player.BattingOrder,
                        bat_hand=lu_player.BatHand or player_stats.BatHand or "R",
                        pitcher_hand=pitcher_hand_home,
                        is_home=False,
                        team_key=away_key,
                        opponent_team_key=home_key,
                    )

                    hit_proj = self.hits_model.project_hits(hitter_vec, game, self.n_sims)
                    player_hit_projections.append(hit_proj)

            # Procesar bateadores home
            if home_lineup:
                for lu_player in home_lineup.Players:
                    player_stats = None
                    for ps in player_stats_by_team.get(home_key, []):
                        if ps.PlayerID == lu_player.PlayerID:
                            player_stats = ps
                            break

                    if not player_stats:
                        continue

                    split_stats = None
                    if pitcher_hand_away == "L":
                        split_stats = split_stats_l.get(lu_player.PlayerID)
                    else:
                        split_stats = split_stats_r.get(lu_player.PlayerID)

                    hitter_vec = self.feature_engineer.build_hitter_features(
                        player_stats=player_stats,
                        player_splits=split_stats,
                        pitcher_stats=away_sp_stats,
                        game=game,
                        batting_order=lu_player.BattingOrder,
                        bat_hand=lu_player.BatHand or player_stats.BatHand or "R",
                        pitcher_hand=pitcher_hand_away,
                        is_home=True,
                        team_key=home_key,
                        opponent_team_key=away_key,
                    )

                    hit_proj = self.hits_model.project_hits(hitter_vec, game, self.n_sims)
                    player_hit_projections.append(hit_proj)

        # -----------------------------------------------------------------
        # 5. OUTPUT
        # -----------------------------------------------------------------
        logger.info("[4/4] GENERANDO OUTPUT")
        logger.info("Moneyline projections: %d", len(moneyline_projections))
        logger.info("Team total projections: %d", len(team_projections))
        logger.info("Player hit projections: %d", len(player_hit_projections))

        return {
            "date": date_str,
            "games_projected": len(games),
            "moneyline_projections": moneyline_projections,
            "team_total_projections": team_projections,
            "player_hit_projections": player_hit_projections,
            "generated_at": datetime.now(),
        }

    def to_dataframe(self, results: Dict) -> Dict[str, pd.DataFrame]:
        """Convierte resultados a DataFrames de pandas para visualización"""
        dfs = {}

        # Moneyline
        if results.get("moneyline_projections"):
            ml_data = []
            for p in results["moneyline_projections"]:
                ml_data.append({
                    "GameID": p.game_id,
                    "Date": p.date,
                    "Away": p.away_team,
                    "Home": p.home_team,
                    "xRuns_Away": p.away_x_runs,
                    "xRuns_Home": p.home_x_runs,
                    "WinProb_Away": f"{p.away_win_prob:.1%}",
                    "WinProb_Home": f"{p.home_win_prob:.1%}",
                    "FairOdds_Away": p.away_ml_fair_odds,
                    "FairOdds_Home": p.home_ml_fair_odds,
                    "Total_xRuns": p.total_x_runs,
                    "OverProb": f"{p.over_prob:.1%}",
                    "UnderProb": f"{p.under_prob:.1%}",
                    "OU_Line": p.over_under_line,
                    "Edge_Away": p.away_edge,
                    "Edge_Home": p.home_edge,
                    "Confidence": p.confidence_score,
                })
            dfs["moneyline"] = pd.DataFrame(ml_data)

        # Team Totals
        if results.get("team_total_projections"):
            tt_data = []
            for p in results["team_total_projections"]:
                tt_data.append({
                    "Team": p.team,
                    "xRuns": p.x_runs,
                    "StdDev": p.x_runs_std,
                    "OffenseRating": p.offense_rating,
                    "DefenseRating": p.defense_rating,
                    "ParkFactor": p.park_factor_runs,
                    "WeatherFactor": p.weather_factor,
                })
            dfs["team_totals"] = pd.DataFrame(tt_data)

        # Player Hits
        if results.get("player_hit_projections"):
            ph_data = []
            for p in results["player_hit_projections"]:
                ph_data.append({
                    "Player": p.player_name,
                    "Team": p.team,
                    "Opp": p.opponent,
                    "BatOrder": p.batting_order,
                    "xPA": p.x_pa,
                    "xHits": p.x_hits,
                    "HitProb/PA": f"{p.hit_prob_per_pa:.1%}",
                    "P(Over 0.5)": f"{p.hit_prob_over_0_5:.1%}",
                    "P(Over 1.5)": f"{p.hit_prob_over_1_5:.1%}",
                    "P(Exactly 0)": f"{p.hit_prob_exactly_0:.1%}",
                    "P(Exactly 1)": f"{p.hit_prob_exactly_1:.1%}",
                    "P(2+)": f"{p.hit_prob_exactly_2 + p.hit_prob_exactly_3_plus:.1%}",
                    "wOBA_vs_Hand": p.woba_vs_hand,
                    "PlatoonAdv": p.platoon_advantage,
                    "ParkFactor": p.park_factor_hits,
                    "Recommendation": p.recommendation,
                    "Edge_O0.5": p.edge_over_0_5,
                    "Confidence": p.confidence_score,
                })
            dfs["player_hits"] = pd.DataFrame(ph_data)

        return dfs


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Proyección MLB")
    parser.add_argument("--date", type=str, required=True, help="Fecha en formato YYYY-MMM-DD (ej. 2026-SEP-05)")
    parser.add_argument("--api-key", type=str, default=None, help="SportsData.io API Key")
    parser.add_argument("--sims", type=int, default=10_000, help="Número de simulaciones Monte Carlo")
    parser.add_argument("--output", type=str, default="console", choices=["console", "csv", "json"])
    args = parser.parse_args()

    pipeline = MLBProjectionPipeline(api_key=args.api_key, n_simulations=args.sims)
    results = pipeline.run(args.date)

    if results["games_projected"] == 0:
        print(f"No se encontraron juegos programados para {args.date}")
        return

    dfs = pipeline.to_dataframe(results)

    print("\n" + "=" * 100)
    print("PROYECCIONES MONEYLINE & TEAM TOTALS")
    print("=" * 100)
    print(tabulate(dfs.get("moneyline", pd.DataFrame()), headers="keys", tablefmt="grid", showindex=False))

    print("\n" + "=" * 100)
    print("PROYECCIONES CARRERAS POR EQUIPO")
    print("=" * 100)
    print(tabulate(dfs.get("team_totals", pd.DataFrame()), headers="keys", tablefmt="grid", showindex=False))

    print("\n" + "=" * 100)
    print("PLAYER PROPS - HITS (Top 30 por confianza)")
    print("=" * 100)
    ph_df = dfs.get("player_hits", pd.DataFrame())
    if not ph_df.empty:
        ph_df = ph_df.sort_values("Confidence", ascending=False).head(30)
    print(tabulate(ph_df, headers="keys", tablefmt="grid", showindex=False))

    # Exportar si se solicita
    if args.output == "csv":
        for name, df in dfs.items():
            fname = f"mlb_projections_{args.date}_{name}.csv"
            df.to_csv(fname, index=False)
            print(f"\nGuardado: {fname}")
    elif args.output == "json":
        import json
        with open(f"mlb_projections_{args.date}.json", "w") as f:
            json.dump({k: v.to_dict("records") for k, v in dfs.items()}, f, indent=2, default=str)
        print(f"\nGuardado: mlb_projections_{args.date}.json")


if __name__ == "__main__":
    main()
