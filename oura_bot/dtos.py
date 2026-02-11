from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


class HeartRate(BaseModel):
    interval: int | None
    items: list[int | None]
    timestamp: str


class Hrv(BaseModel):
    interval: int | None
    items: list[int | None]
    timestamp: str


class Contributors(BaseModel):
    activity_balance: int | None
    body_temperature: int | None
    hrv_balance: int | None
    previous_day_activity: int | None
    previous_night: int | None
    recovery_index: int | None
    resting_heart_rate: int | None
    sleep_balance: int | None


class Readiness(BaseModel):
    contributors: Contributors
    score: int | None
    temperature_deviation: float | None
    temperature_trend_deviation: float | None


class Datum(BaseModel):
    id: str
    average_breath: float | None
    average_heart_rate: float | None
    average_hrv: int = Field(default=0)
    awake_time: int | None
    bedtime_end: str | None
    bedtime_start: str | None
    day: str | None
    deep_sleep_duration: int | None
    efficiency: int | None
    heart_rate: HeartRate | None
    hrv: Hrv | None
    latency: int | None
    light_sleep_duration: int | None
    low_battery_alert: bool | None
    lowest_heart_rate: int | None
    movement_30_sec: str | None
    period: int | None
    readiness: Readiness | None
    readiness_score_delta: int | None
    rem_sleep_duration: int | None
    restless_periods: int | None
    sleep_phase_5_min: str | None
    sleep_score_delta: int | None
    sleep_algorithm_version: str | None
    time_in_bed: int | None
    total_sleep_duration: int | None
    type: str | None

    @field_validator('average_hrv', mode='before')
    @classmethod
    def replace_none_with_zero(cls, value: int | None) -> int:
        if value is None:
            return 0
        return value


class SleepData(BaseModel):
    data: list[Datum]
    next_token: str | None


class DiffMeasure(BaseModel):
    deep_sleep: int | None
    total_sleep: int | None
    average_hrv: float | None
    average_heart_rate: float | None
    score: int | None
    recovery_index: int | None


class TrainingPeakMeasureDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    timestamp: str = Field(alias='timeStamp')
    value: float
    mean: float | None
    range_high: float | None = Field(alias='rangeHigh')
    range_low: float | None = Field(alias='rangeLow')


class TrainingPeakMeasure(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    athlete_id: int = Field(alias='athleteId')
    label: str
    type: int
    upload_client: str = Field(alias='uploadClient')
    details: list[TrainingPeakMeasureDetail]


class TrainingPeakMeasures(RootModel):
    root: list[TrainingPeakMeasure]
