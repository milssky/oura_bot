from pydantic import BaseModel


class SleepContributorsDTO(BaseModel):
    deep_sleep: int
    efficiency: int
    latency: int
    rem_sleep: int
    restfulness: int
    timing: int
    total_sleep: int


class SleepDTO(BaseModel):
    id: str
    contributors: SleepContributorsDTO | None = None
    day: str
    score: int
    timestamp: str


class ReadinessContributorsDTO(BaseModel):
    activity_balance: int
    body_temperature: int
    hrv_balance: int
    previous_day_activity: int
    previous_night: int
    recovery_index: int
    resting_heart_rate: int
    sleep_balance: int

class ReadinessDTO(BaseModel):
    id: str
    contributors: ReadinessContributorsDTO | None = None
    day: str
    score: int
    timestamp: str
    temperature_deviation: int | float
    temperature_trend_deviation: int | float
