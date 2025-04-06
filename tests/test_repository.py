from datetime import datetime

from oura_bot.dtos import Datum, DiffMeasure
from oura_bot.models import SleepMeasure, User
from oura_bot.repository import UserMeasureRepository


async def test_user_get_or_create(repo: UserMeasureRepository) -> None:
    user_data = {'name': 'Test', 'timezone': 'America/Phoenix'}
    user = await repo.get_user(user_data=user_data)
    assert await User.all().count() == 1
    assert user.name == user_data['name']
    assert user.timezone == user_data['timezone']
    expecter_user = await User.get(name=user_data['name'])
    assert user.id == expecter_user.id


async def test_get_last_measure(
    user: User, repo: UserMeasureRepository
) -> None:
    measure = await SleepMeasure.create(
        user=user,
        deep_sleep_duration=3000,
        total_sleep_duration=6000,
        average_hrv=56,
        average_heart_rate=55,
        score=89,
        recovery_index=90,
    )
    received = await repo.get_user_last_measure(user=user)
    assert measure == received
    assert measure.deep_sleep_duration == received.deep_sleep_duration
    assert measure.total_sleep_duration == received.total_sleep_duration
    assert measure.average_hrv == received.average_hrv
    assert measure.average_heart_rate == received.average_heart_rate
    assert measure.score == received.score
    assert received.recovery_index == received.recovery_index


async def test_get_diff_measure(
    user: User, repo: UserMeasureRepository
) -> None:
    last_measure = await SleepMeasure.create(
        user=user,
        deep_sleep_duration=3000,
        total_sleep_duration=6000,
        average_hrv=56,
        average_heart_rate=55,
        score=89,
        recovery_index=90,
    )
    last_measure.created_at = datetime(2025, 3, 30, 10, 00, 00)
    await last_measure.save()
    early_measure = await SleepMeasure.create(
        user=user,
        deep_sleep_duration=4000,
        total_sleep_duration=7000,
        average_hrv=60,
        average_heart_rate=60,
        score=100,
        recovery_index=100,
    )
    early_measure.created_at = datetime(2025, 3, 29, 10, 00, 00)
    await early_measure.save()

    diff = await repo.get_diff_measure_by_user(user=user)
    assert isinstance(diff, DiffMeasure)
    assert diff.score == 11
    assert diff.deep_sleep == 1000
    assert diff.total_sleep == 1000
    assert diff.average_hrv == 4
    assert diff.average_heart_rate == 5
    assert diff.recovery_index == 10


def test_get_night_measure(
    sleep_data: list[Datum], repo: UserMeasureRepository
) -> None:
    assert len(sleep_data) == 3
    expected_id = 'da1a32bc-054b-40cd-9c3b-ee2918dd97bb'
    night_measure = repo.get_night_sleep_data(sleep_data=sleep_data)
    assert night_measure.id == expected_id


def test_get_night_measure_if_one_measure_available(
    sleep_data: list[Datum], repo: UserMeasureRepository
) -> None:
    assert len(sleep_data) == 3
    sleep_data = sleep_data[2:]
    assert len(sleep_data) == 1
    expected_id = 'da1a32bc-054b-40cd-9c3b-ee2918dd97bb'
    night_measure = repo.get_night_sleep_data(sleep_data=sleep_data)
    assert night_measure.id == expected_id
