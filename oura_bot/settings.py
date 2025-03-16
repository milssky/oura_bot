from datetime import timedelta

RETRY_PERIOD_SEC = 5
RETRY_ATTEMPTS = 5


DELTA_TIME = timedelta(hours=5)

MESSAGE_FORMAT = """{name}:
    sleep: {sleep}
    readiness: {readiness}

"""
