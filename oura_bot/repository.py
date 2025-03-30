from oura_bot.client import OuraClient
from oura_bot.dtos import DiffMeasure, SleepData
from oura_bot.models import SleepMeasure, User
from oura_bot.utils import convert_data


class OuraRepository:
    """Repo for Oura API."""

    async def get_total_sleep(self, *, user_client: OuraClient) -> SleepData:
        """Call sleep user api."""
        json_data = await user_client.get_total_sleep()
        return SleepData(**json_data)


class UserMeasureRepository:
    """Repo for Measures and users."""

    async def create_user_measure(
        self, *, measure: SleepData, user: User
    ) -> SleepMeasure | None:
        if not measure.data:
            return None
        data = measure.data[0]
        return await SleepMeasure.create(
            user=user,
            deep_sleep_duration=data.deep_sleep_duration,
            total_sleep_duration=data.total_sleep_duration,
            average_hrv=data.average_hrv,
            average_heart_rate=data.average_heart_rate,
            score=data.readiness.score,
            recovery_index=data.readiness.contributors.recovery_index,
        )

    async def get_user(self, *, user_data: dict[str, str]) -> User:
        user, _ = await User.get_or_create(
            name=user_data['name'],
            timezone=user_data['timezone'],
        )
        return user

    async def get_user_last_measure(self, *, user: User) -> SleepMeasure:
        return await SleepMeasure.filter(user=user).last()

    async def get_diff_measure_by_user(self, *, user: User) -> DiffMeasure:
        last = await self.get_user_last_measure(user=user)
        if last is None:
            return DiffMeasure(
                deep_sleep=0,
                total_sleep=0,
                average_hrv=0,
                average_heart_rate=0,
                score=0,
                recovery_index=0,
            )
        if await SleepMeasure.filter(user=user).count() <= 1:
            pre_last = last
        else:
            pre_last = (await SleepMeasure.filter(user=user))[-2]
        deep_sleep_diff = (
            last.deep_sleep_duration - pre_last.deep_sleep_duration
        )
        total_sleep_diff = (
            last.total_sleep_duration - pre_last.total_sleep_duration
        )
        average_hrv_diff = last.average_hrv - pre_last.average_hrv
        average_heart_rate_diff = (
            last.average_heart_rate - pre_last.average_heart_rate
        )
        score_diff = last.score - pre_last.score
        recovery_index_diff = last.recovery_index - pre_last.recovery_index
        return DiffMeasure(
            deep_sleep=deep_sleep_diff,
            total_sleep=total_sleep_diff,
            average_hrv=average_hrv_diff,
            average_heart_rate=average_heart_rate_diff,
            score=score_diff,
            recovery_index=recovery_index_diff,
        )

    async def get_user_measure_with_diff(self, user: User) -> str | None:
        measure = await self.get_user_last_measure(user=user)
        if measure is None:
            return None
        diff = await self.get_diff_measure_by_user(user=user)
        return convert_data(measure=measure, diff=diff, name=user.name)
