"""
Módulo de ingesta de datos: orquesta llamadas API, gestiona caché local,
y construye datasets para el pipeline de proyección.
"""

import json
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config.settings import PIPELINE_CFG
from src.client.sportsdata_client import SportsDataClient
from src.models.schemas import (
    Game, PlayerSeasonStats, PlayerGameStats, TeamGameStats,
    StartingLineup, PlayerGameProjection, BoxScore, Team, PlayerBasic,
)

logger = logging.getLogger(__name__)


class DataCache:
    def __init__(self, cache_dir: str = "./data/cache", ttl_hours: int = 2):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self._memory_cache: Dict[str, Tuple[datetime, Any]] = {}

    def _cache_key(self, endpoint: str, **params: Any) -> str:
        key_data = {"endpoint": endpoint, "params": params}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        import hashlib
        return hashlib.md5(key_str.encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.pkl"

    def get(self, endpoint: str, **params: Any) -> Optional[Any]:
        key = self._cache_key(endpoint, **params)
        if key in self._memory_cache:
            ts, data = self._memory_cache[key]
            if datetime.now() - ts < self.ttl:
                return data
            del self._memory_cache[key]
        cache_file = self._cache_path(key)
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    ts, data = pickle.load(f)
                if datetime.now() - ts < self.ttl:
                    self._memory_cache[key] = (ts, data)
                    return data
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.warning("Error leyendo caché: %s", e)
        return None

    def set(self, endpoint: str, data: Any, **params: Any) -> None:
        key = self._cache_key(endpoint, **params)
        ts = datetime.now()
        self._memory_cache[key] = (ts, data)
        try:
            with open(self._cache_path(key), "wb") as f:
                pickle.dump((ts, data), f)
        except Exception as e:
            logger.warning("Error escribiendo caché: %s", e)

    def invalidate(self, endpoint: str, **params: Any) -> None:
        key = self._cache_key(endpoint, **params)
        self._memory_cache.pop(key, None)
        cache_file = self._cache_path(key)
        if cache_file.exists():
            cache_file.unlink()


class MLBDataIngestor:
    def __init__(self, client: Optional[SportsDataClient] = None,
                 cache: Optional[DataCache] = None,
                 season: Optional[str] = None) -> None:
        self.client = client or SportsDataClient()
        self.cache = cache or DataCache(ttl_hours=PIPELINE_CFG.DATA_CACHE_TTL_HOURS)
        self.season = season or PIPELINE_CFG.SEASON
        self._teams_cache: Optional[Dict[int, Team]] = None
        self._players_cache: Optional[Dict[int, PlayerBasic]] = None
        logger.info("MLBDataIngestor | season=%s", self.season)

    def _fetch_or_cache(self, fetch_fn, endpoint_name: str, **cache_params: Any) -> Any:
        cached = self.cache.get(endpoint_name, **cache_params)
        if cached is not None:
            return cached
        data = fetch_fn()
        self.cache.set(endpoint_name, data, **cache_params)
        return data

    def get_games_by_date(self, date_str: str) -> List[Game]:
        raw = self._fetch_or_cache(lambda: self.client.get_games_by_date(date_str), "games_by_date", date=date_str)
        games = []
        for item in raw:
            try:
                games.append(Game.model_validate(item))
            except Exception as e:
                logger.warning("Error validando Game: %s", e)
        return games

    def get_scheduled_games(self, date_str: str) -> List[Game]:
        all_games = self.get_games_by_date(date_str)
        scheduled = [g for g in all_games if g.Status in ("Scheduled", "PreGame", "Warmup", "InProgress") and not g.IsClosed]
        logger.info("Programados %s: %d/%d", date_str, len(scheduled), len(all_games))
        return scheduled

    def get_teams(self) -> Dict[int, Team]:
        if self._teams_cache is not None:
            return self._teams_cache
        raw = self._fetch_or_cache(self.client.get_teams, "teams")
        teams = {}
        for item in raw:
            try:
                team = Team.model_validate(item)
                teams[team.TeamID] = team
            except Exception as e:
                logger.warning("Error validando Team: %s", e)
        self._teams_cache = teams
        logger.info("Equipos: %d", len(teams))
        return teams

    def get_team_by_key(self, team_key: str) -> Optional[Team]:
        teams = self.get_teams()
        for team in teams.values():
            if team.Key == team_key:
                return team
        return None

    def get_team_season_stats(self, team_key: str) -> Optional[TeamGameStats]:
        raw = self._fetch_or_cache(lambda: self.client.get_team_season_stats(self.season, team_key),
                                   "team_season_stats", season=self.season, team=team_key)
        if raw and len(raw) > 0:
            try:
                return TeamGameStats.model_validate(raw[0])
            except Exception as e:
                logger.warning("Error validando TeamSeasonStats: %s", e)
        return None

    def get_player_season_stats_by_team(self, team_key: str) -> List[PlayerSeasonStats]:
        raw = self._fetch_or_cache(lambda: self.client.get_player_season_stats_by_team(self.season, team_key),
                                   "player_season_stats_by_team", season=self.season, team=team_key)
        stats = []
        for item in raw:
            try:
                stats.append(PlayerSeasonStats.model_validate(item))
            except Exception as e:
                logger.warning("Error validando PlayerSeasonStats: %s", e)
        return stats

    def get_player_season_split_stats(self, split: str) -> List[PlayerSeasonStats]:
        raw = self._fetch_or_cache(lambda: self.client.get_player_season_split_stats(self.season, split),
                                   "player_season_split", season=self.season, split=split)
        stats = []
        for item in raw:
            try:
                stats.append(PlayerSeasonStats.model_validate(item))
            except Exception as e:
                logger.warning("Error validando PlayerSeasonSplit: %s", e)
        return stats

    def get_starting_lineups(self, date_str: str) -> List[StartingLineup]:
        raw = self._fetch_or_cache(lambda: self.client.get_starting_lineups(date_str), "starting_lineups", date=date_str)
        lineups = []
        for item in raw:
            try:
                lineups.append(StartingLineup.model_validate(item))
            except Exception as e:
                logger.warning("Error validando StartingLineup: %s", e)
        return lineups

    def get_projected_player_stats(self, date_str: str) -> List[PlayerGameProjection]:
        raw = self._fetch_or_cache(lambda: self.client.get_projected_player_stats(date_str), "projected_player_stats", date=date_str)
        projections = []
        for item in raw:
            try:
                projections.append(PlayerGameProjection.model_validate(item))
            except Exception as e:
                logger.warning("Error validando PlayerGameProjection: %s", e)
        return projections

    def get_box_scores_by_date(self, date_str: str) -> List[BoxScore]:
        raw = self._fetch_or_cache(lambda: self.client.get_box_scores_by_date(date_str), "box_scores_by_date", date=date_str)
        box_scores = []
        for item in raw:
            try:
                box_scores.append(BoxScore.model_validate(item))
            except Exception as e:
                logger.warning("Error validando BoxScore: %s", e)
        return box_scores

    def get_team_game_logs(self, teamid: int, numberofgames: str = "all") -> List[TeamGameStats]:
        raw = self._fetch_or_cache(lambda: self.client.get_team_game_logs(self.season, teamid, numberofgames),
                                   "team_game_logs", season=self.season, teamid=teamid, numberofgames=numberofgames)
        logs = []
        for item in raw:
            try:
                logs.append(TeamGameStats.model_validate(item))
            except Exception as e:
                logger.warning("Error validando TeamGameLog: %s", e)
        return logs

    def get_team_hitting_vs_sp(self, gameid: int, team_key: str) -> List[PlayerSeasonStats]:
        raw = self._fetch_or_cache(lambda: self.client.get_team_hitting_vs_sp(gameid, team_key),
                                   "team_hitting_vs_sp", gameid=gameid, team=team_key)
        stats = []
        for item in raw:
            try:
                stats.append(PlayerSeasonStats.model_validate(item))
            except Exception as e:
                logger.warning("Error validando TeamHittingVsSP: %s", e)
        return stats

    def get_batter_vs_pitcher(self, hitterid: int, pitcherid: int) -> List[PlayerSeasonStats]:
        raw = self._fetch_or_cache(lambda: self.client.get_batter_vs_pitcher(hitterid, pitcherid),
                                   "batter_vs_pitcher", hitterid=hitterid, pitcherid=pitcherid)
        stats = []
        for item in raw:
            try:
                stats.append(PlayerSeasonStats.model_validate(item))
            except Exception as e:
                logger.warning("Error validando BatterVsPitcher: %s", e)
        return stats

    def build_team_stats_map(self, team_keys: List[str]) -> Dict[str, TeamGameStats]:
        result = {}
        for key in team_keys:
            stats = self.get_team_season_stats(key)
            if stats:
                result[key] = stats
        return result

    def build_player_stats_map(self, team_keys: List[str]) -> Dict[str, List[PlayerSeasonStats]]:
        result = {}
        for key in team_keys:
            result[key] = self.get_player_season_stats_by_team(key)
        return result

    def build_lineup_map(self, date_str: str) -> Dict[str, StartingLineup]:
        lineups = self.get_starting_lineups(date_str)
        return {lu.Team: lu for lu in lineups if lu.Team}
