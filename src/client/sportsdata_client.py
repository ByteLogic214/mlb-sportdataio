"""
Cliente HTTP robusto para SportsData.io MLB v3 API.
Incluye rate limiting, retries con backoff exponencial, manejo de errores.
"""

import os
import time
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import SPORTSDATA_CFG, ENDPOINTS

logger = logging.getLogger(__name__)
T = TypeVar("T")


class SportsDataAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class RateLimitError(SportsDataAPIError):
    pass


class AuthenticationError(SportsDataAPIError):
    pass


class NotFoundError(SportsDataAPIError):
    pass


class ServerError(SportsDataAPIError):
    pass


class SportsDataClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("SPORTSDATA_API_KEY", SPORTSDATA_CFG.API_KEY)
        if not self.api_key:
            raise AuthenticationError(
                "API Key no proporcionada. Establece SPORTSDATA_API_KEY o pasa api_key al constructor."
            )
        self.base_url = base_url or SPORTSDATA_CFG.BASE_URL
        self.timeout = timeout or SPORTSDATA_CFG.TIMEOUT
        self.max_retries = max_retries or SPORTSDATA_CFG.MAX_RETRIES
        self.backoff_factor = backoff_factor or SPORTSDATA_CFG.BACKOFF_FACTOR
        self._rate_limit_calls = SPORTSDATA_CFG.RATE_LIMIT_CALLS
        self._rate_limit_period = SPORTSDATA_CFG.RATE_LIMIT_PERIOD
        self._call_timestamps: List[float] = []
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        logger.info(
            "SportsDataClient | base_url=%s | timeout=%ds | max_retries=%d",
            self.base_url, self.timeout, self.max_retries,
        )

    def _enforce_rate_limit(self) -> None:
        now = time.time()
        cutoff = now - self._rate_limit_period
        self._call_timestamps = [t for t in self._call_timestamps if t > cutoff]
        if len(self._call_timestamps) >= self._rate_limit_calls:
            sleep_time = self._call_timestamps[0] + self._rate_limit_period - now
            if sleep_time > 0:
                logger.debug("Rate limit. Esperando %.2fs", sleep_time)
                time.sleep(sleep_time)
                self._enforce_rate_limit()
        self._call_timestamps.append(time.time())

    def _build_url(self, endpoint: str, **path_params: Any) -> str:
        formatted = endpoint.format(**path_params)
        return urljoin(self.base_url + "/", formatted.lstrip("/"))

    def _handle_response(self, response: requests.Response, endpoint_name: str) -> Any:
        status = response.status_code
        body_preview = response.text[:500] if response.text else "<empty>"
        if status == 200:
            try:
                return response.json()
            except ValueError as e:
                raise SportsDataAPIError(f"JSON inválido: {e}", status_code=status, response_body=body_preview)
        if status == 401:
            raise AuthenticationError(f"API Key inválida: {endpoint_name}", status_code=status, response_body=body_preview)
        elif status == 404:
            raise NotFoundError(f"No encontrado: {endpoint_name}", status_code=status, response_body=body_preview)
        elif status == 429:
            raise RateLimitError(f"Rate limit: {endpoint_name}", status_code=status, response_body=body_preview)
        elif 500 <= status < 600:
            raise ServerError(f"Server error {status}: {endpoint_name}", status_code=status, response_body=body_preview)
        else:
            raise SportsDataAPIError(f"HTTP {status}: {endpoint_name}", status_code=status, response_body=body_preview)

    def get(self, endpoint: str, endpoint_name: str = "unknown",
            path_params: Optional[Dict[str, Any]] = None,
            query_params: Optional[Dict[str, Any]] = None) -> Any:
        self._enforce_rate_limit()
        path_params = path_params or {}
        query_params = query_params or {}
        url = self._build_url(endpoint, **path_params)
        params = {"key": self.api_key, **query_params}
        try:
            response = self.session.get(url, params=params, timeout=self.timeout, headers={"Accept": "application/json"})
        except requests.exceptions.Timeout:
            raise SportsDataAPIError(f"Timeout {self.timeout}s en {endpoint_name}")
        except requests.exceptions.ConnectionError as e:
            raise SportsDataAPIError(f"Conexión fallida: {endpoint_name}: {e}")
        data = self._handle_response(response, endpoint_name)
        n_items = len(data) if isinstance(data, list) else 1
        logger.info("OK %s | status=%d | items=%d", endpoint_name, status, n_items)
        return data

    def get_parsed(self, endpoint: str, model_class: Type[T], endpoint_name: str = "unknown",
                   path_params: Optional[Dict[str, Any]] = None,
                   query_params: Optional[Dict[str, Any]] = None) -> List[T]:
        raw_data = self.get(endpoint, endpoint_name, path_params, query_params)
        if not isinstance(raw_data, list):
            raw_data = [raw_data]
        parsed = []
        errors = 0
        for idx, item in enumerate(raw_data):
            try:
                parsed.append(model_class.model_validate(item))
            except Exception as e:
                errors += 1
                logger.warning("Parse error item %d en %s: %s", idx, endpoint_name, e)
        if errors:
            logger.warning("%d/%d fallaron en %s", errors, len(raw_data), endpoint_name)
        return parsed

    def get_games_by_date(self, date_str: str) -> List[Any]:
        return self.get(ENDPOINTS.GAMES_BY_DATE, "games_by_date", path_params={"date": date_str})

    def get_schedules(self, season: str) -> List[Any]:
        return self.get(ENDPOINTS.SCHEDULES, "schedules", path_params={"season": season})

    def get_starting_lineups(self, date_str: str) -> List[Any]:
        return self.get(ENDPOINTS.STARTING_LINEUPS, "starting_lineups", path_params={"date": date_str})

    def get_team_season_stats(self, season: str, team: str) -> List[Any]:
        return self.get(ENDPOINTS.TEAM_SEASON_STATS, "team_season_stats", path_params={"season": season, "team": team})

    def get_player_season_stats_by_team(self, season: str, team: str) -> List[Any]:
        return self.get(ENDPOINTS.PLAYER_SEASON_STATS, "player_season_stats_by_team", path_params={"season": season, "team": team})

    def get_player_season_split_stats(self, season: str, split: str) -> List[Any]:
        return self.get(ENDPOINTS.PLAYER_SEASON_SPLIT, "player_season_split", path_params={"season": season, "split": split})

    def get_box_scores_by_date(self, date_str: str) -> List[Any]:
        return self.get(ENDPOINTS.BOX_SCORE_BY_DATE, "box_scores_by_date", path_params={"date": date_str})

    def get_projected_player_stats(self, date_str: str) -> List[Any]:
        return self.get(ENDPOINTS.PROJECTED_PLAYER_STATS, "projected_player_stats", path_params={"date": date_str})

    def get_team_hitting_vs_sp(self, gameid: int, team: str) -> List[Any]:
        return self.get(ENDPOINTS.TEAM_HITTING_VS_SP, "team_hitting_vs_sp", path_params={"gameid": gameid, "team": team})

    def get_batter_vs_pitcher(self, hitterid: int, pitcherid: int) -> List[Any]:
        return self.get(ENDPOINTS.BATTER_VS_PITCHER, "batter_vs_pitcher", path_params={"hitterid": hitterid, "pitcherid": pitcherid})

    def get_depth_charts(self) -> List[Any]:
        return self.get(ENDPOINTS.DEPTH_CHARTS, "depth_charts")

    def get_teams(self) -> List[Any]:
        return self.get(ENDPOINTS.TEAMS, "teams")

    def get_team_game_logs(self, season: str, teamid: int, numberofgames: str = "all") -> List[Any]:
        return self.get(ENDPOINTS.TEAM_GAME_LOGS, "team_game_logs", path_params={"season": season, "teamid": teamid, "numberofgames": numberofgames})
