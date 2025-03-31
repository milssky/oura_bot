import os
from datetime import time, timedelta
from pathlib import Path

RETRY_PERIOD_DAYS = 5
RETRY_ATTEMPTS = 1


DELTA_TIME = timedelta(hours=5)

MESSAGE_FORMAT = """#{name}:
    sleep: {total_sleep} ({sleep_diff})
    deep_s: {deep_s} ({deep_diff})
    score: {score} ({score_diff})

    HRV: {average_hrv} ({average_hrv_diff})
    HR: {average_hr} ({average_hr_diff})
    Recovery: {recovery} ({recovery_diff})

"""

RETRY_FINISH_HOUR = time(hour=13, minute=0, second=0, microsecond=0).hour

BASE_DIR = Path(__file__).resolve().parent.parent


DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.environ.get('POSTGRES_DB', 'postgres')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
