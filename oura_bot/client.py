from typing import Any

from httpx import AsyncClient, Response

from oura_bot.auth import BearerAuth
from oura_bot.urls import API_ROOT, DAILY_READINESS, TOTAL_SLEEP_URL


class OuraClient(AsyncClient):
    """HTTP client to handle Oura API."""

    def __init__(self, token: str, *args: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.base_url = API_ROOT
        self.auth = BearerAuth(token=token)

    async def get_total_sleep(self) -> Response:
        response = await self.get(
            url=TOTAL_SLEEP_URL,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    async def get_daily_readiness(self) -> Response:
        response = await self.get(
            url=DAILY_READINESS,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()
