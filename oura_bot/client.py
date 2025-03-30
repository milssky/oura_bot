from typing import Any

from httpx import AsyncClient, HTTPError, Response
from stamina import retry

from oura_bot.auth import BearerAuth
from oura_bot.settings import RETRY_ATTEMPTS
from oura_bot.urls import API_ROOT, TOTAL_SLEEP_URL


class OuraClient(AsyncClient):
    """HTTP client to handle Oura API."""

    def __init__(
        self, token: str, *args: Any, **kwargs: dict[str, Any]
    ) -> None:
        super().__init__(*args, **kwargs)
        self.base_url = API_ROOT
        self.auth = BearerAuth(token=token)

    @retry(on=HTTPError, attempts=RETRY_ATTEMPTS)
    async def get_total_sleep(self) -> Response:
        response = await self.get(
            url=TOTAL_SLEEP_URL,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()
