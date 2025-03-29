from datetime import timedelta

RETRY_PERIOD_SEC = 5
RETRY_ATTEMPTS = 1
RETRY_ATTEMPTS = 1


DELTA_TIME = timedelta(hours=5)

MESSAGE_FORMAT = """{name}:
    sleep: {total_sleep} ({sleep_diff})
    deep_s: {deep_s} ({deep_diff})
    score: {score} ({score_diff})
    HRV: {average_hrv} ({average_hrv_diff})
    HR: {average_hr} ({average_hr_diff})
    Recovery: {recovery} ({recovery_diff})

"""
