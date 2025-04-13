import tomllib
from datetime import timedelta
from pathlib import Path

from oura_bot.dtos import DiffMeasure
from oura_bot.models import SleepMeasure
from oura_bot.settings import BASE_DIR, MESSAGE_FORMAT


def load_users(
    data_path: Path = BASE_DIR / 'users.toml',
) -> list[dict[str, str]]:
    """Get user data from TOML users file."""
    with open(data_path, 'rb') as f:
        users = tomllib.load(f)

    if 'users' not in users:
        return []
    return users['users']


def second_to_hms(seconds: int) -> str:
    """Convert seconds to HMS."""
    return str(timedelta(seconds=seconds))


def convert_data(measure: SleepMeasure, diff: DiffMeasure, name: str) -> str:
    """Convert user data to str to send."""
    return MESSAGE_FORMAT.format(
        name=name,
        total_sleep=second_to_hms(measure.total_sleep_duration),
        sleep_diff=second_to_hms(diff.total_sleep),
        deep_s=second_to_hms(measure.deep_sleep_duration),
        deep_diff=second_to_hms(diff.deep_sleep),
        score=measure.score,
        score_diff=diff.score,
        average_hrv=int(measure.average_hrv),
        average_hrv_diff=int(diff.average_hrv),
        average_hr=int(measure.average_heart_rate),
        average_hr_diff=int(diff.average_heart_rate),
        recovery=measure.recovery_index,
        recovery_diff=diff.recovery_index,
    )
