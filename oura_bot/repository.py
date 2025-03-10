from oura_bot.client import OuraClient
from oura_bot.dtos import ReadinessDTO, SleepDTO


class OuraRepository:
    """Repo for Oura API."""

    async def get_daily_readiness(self, user_client: OuraClient) -> ReadinessDTO | None:
        """Call readiness user api."""
        json_data = await user_client.get_daily_readiness()
        data = json_data['data']
        if not data:
            return None
        return ReadinessDTO(**data[0])

    async def get_total_sleep(self, user_client: OuraClient) -> SleepDTO | None:
        """Call sleep user api."""
        json_data = await user_client.get_total_sleep()
        data = json_data['data']
        if not data:
            return None
        return SleepDTO(**data[0])
