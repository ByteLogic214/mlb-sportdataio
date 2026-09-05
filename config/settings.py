"""
Configuración centralizada del pipeline de proyección MLB.
Todas las constantes, URLs y parámetros del modelo se definen aquí.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class SportsDataConfig:
    """Configuración de la API de SportsData.io"""
    BASE_URL: str = "https://api.sportsdata.io/v3/mlb"
    API_KEY: str = ""
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 1.5
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60


@dataclass(frozen=True)
class Endpoints:
    """Endpoints MLB v3 de SportsData.io"""
    SCHEDULES: str = "/scores/json/Games/{season}"
    GAMES_BY_DATE: str = "/scores/json/GamesByDate/{date}"
    GAMES_BY_DATE_LIVE: str = "/scores/json/GamesByDateLive/{date}"
    TEAM_SEASON_STATS: str = "/stats/json/TeamSeasonStats/{season}/{team}"
    PLAYER_SEASON_STATS: str = "/stats/json/PlayerSeasonStats/{season}/{team}"
    PLAYER_SEASON_SPLIT: str = "/stats/json/PlayerSeasonSplitStats/{season}/{split}"
    PLAYER_GAME_LOGS: str = "/stats/json/PlayerGameLogsBySeason/{season}/{playerid}/{numberofgames}"
    BOX_SCORE_BY_DATE: str = "/stats/json/BoxScoresByDate/{date}"
    BOX_SCORE: str = "/stats/json/BoxScore/{gameid}"
    TEAM_GAME_LOGS: str = "/stats/json/TeamGameLogsBySeason/{season}/{teamid}/{numberofgames}"
    STARTING_LINEUPS: str = "/projections/json/StartingLineupsByDate/{date}"
    TEAM_HITTING_VS_SP: str = "/stats/json/TeamHittingVsStartingPitcher/{gameid}/{team}"
    BATTER_VS_PITCHER: str = "/stats/json/BatterVsPitcherStats/{hitterid}/{pitcherid}"
    DEPTH_CHARTS: str = "/scores/json/DepthCharts"
    PROJECTED_PLAYER_STATS: str = "/projections/json/PlayerGameProjectionStatsByDate/{date}"
    TEAMS: str = "/scores/json/Teams"
    PLAYERS_BY_TEAM: str = "/scores/json/Players/{team}"
    PLAYER_DETAILS: str = "/scores/json/Player/{playerid}"


@dataclass(frozen=True)
class ModelConfig:
    """Hiperparámetros y configuración de los modelos de proyección"""
    MC_SIMULATIONS: int = 10_000
    MC_SEED: int = 42
    RUNS_MEAN_ADJUSTMENT: float = 0.0
    RUNS_DISPERSION_FACTOR: float = 1.05
    BULLPEN_FATIGUE_WINDOW: int = 5
    BULLPEN_FATIGUE_IP_THRESHOLD: float = 15.0
    BULLPEN_FATIGUE_PENALTY: float = 0.08

    PARK_FACTORS: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "COL": {"runs": 1.25, "hits": 1.18, "hrs": 1.32, "doubles": 1.22},
        "BOS": {"runs": 1.08, "hits": 1.05, "hrs": 1.02, "doubles": 1.18},
        "NYY": {"runs": 0.98, "hits": 0.97, "hrs": 1.12, "doubles": 0.95},
        "LAD": {"runs": 0.96, "hits": 0.98, "hrs": 1.08, "doubles": 0.92},
        "HOU": {"runs": 1.02, "hits": 1.01, "hrs": 1.06, "doubles": 1.00},
        "CHC": {"runs": 1.04, "hits": 1.02, "hrs": 1.05, "doubles": 1.08},
        "CIN": {"runs": 1.06, "hits": 1.03, "hrs": 1.14, "doubles": 1.05},
        "TEX": {"runs": 1.03, "hits": 1.01, "hrs": 1.04, "doubles": 0.98},
        "ARI": {"runs": 1.05, "hits": 1.03, "hrs": 1.10, "doubles": 1.06},
        "BAL": {"runs": 0.99, "hits": 0.98, "hrs": 1.08, "doubles": 0.96},
        "TB":  {"runs": 0.94, "hits": 0.95, "hrs": 0.88, "doubles": 0.93},
        "SEA": {"runs": 0.93, "hits": 0.94, "hrs": 0.96, "doubles": 0.91},
        "SF":  {"runs": 0.92, "hits": 0.96, "hrs": 0.85, "doubles": 0.98},
        "SD":  {"runs": 0.91, "hits": 0.93, "hrs": 0.90, "doubles": 0.89},
        "MIA": {"runs": 0.90, "hits": 0.94, "hrs": 0.82, "doubles": 0.88},
        "OAK": {"runs": 0.88, "hits": 0.92, "hrs": 0.80, "doubles": 0.85},
        "default": {"runs": 1.00, "hits": 1.00, "hrs": 1.00, "doubles": 1.00},
    })

    WOBA_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        "walk": 0.69, "hbp": 0.72, "single": 0.89,
        "double": 1.27, "triple": 1.62, "home_run": 2.10,
    })

    LG_WOBA: float = 0.318
    LG_WOBA_SCALE: float = 1.200
    OFFENSE_WEIGHT: float = 0.52
    DEFENSE_WEIGHT: float = 0.48
    MIN_IP_PITCHER: float = 20.0
    MIN_PA_HITTER: int = 100
    REGRESSION_PA: int = 300
    REGRESSION_IP: float = 60.0
    CMP_NU_DEFAULT: float = 0.85
    HITS_OVER_0_5_THRESHOLD: float = 0.55
    HITS_OVER_1_5_THRESHOLD: float = 0.35


@dataclass(frozen=True)
class PipelineConfig:
    """Configuración general del pipeline"""
    SEASON: str = "2026REG"
    DATA_CACHE_TTL_HOURS: int = 2
    LOG_LEVEL: str = "INFO"
    OUTPUT_FORMAT: str = "dataframe"


SPORTSDATA_CFG = SportsDataConfig()
ENDPOINTS = Endpoints()
MODEL_CFG = ModelConfig()
PIPELINE_CFG = PipelineConfig()
