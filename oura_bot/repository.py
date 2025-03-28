from datetime import datetime, timedelta
import re

from oura_bot.client import OuraClient
from oura_bot.dtos import Datum, SleepData
from oura_bot.models import SleepMeasure, User


class OuraRepository:
    """Repo for Oura API."""

    async def get_total_sleep(self, user_client: OuraClient) -> SleepData:
        """Call sleep user api."""
        json_data = await user_client.get_total_sleep(
            start_date=datetime.now() - timedelta(days=1), end_date=datetime.now()
        )
        print(json_data)
        return SleepData(**json_data)

    async def create_user_measure(self, data: Datum, user: User) -> SleepMeasure:
        return await SleepMeasure.create(
            user=user,
            deep_sleep_duration=data.deep_sleep_duration,
            total_sleep_duration=data.total_sleep_duration,
            average_hrv=data.average_hrv,
            average_heart_rate=data.average_heart_rate,
            score=data.readiness.score,
            recovery_index=data.readiness.contributors.recovery_index,
        )
