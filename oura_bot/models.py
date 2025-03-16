from tortoise import fields
from tortoise.fields.relational import ForeignKeyField
from tortoise.models import Model


class IDMixin(Model):
    id = fields.IntField(pk=True)

    class Meta:
        abstract = True


class TimeStampedMixin(Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class User(IDMixin, Model):
    name = fields.CharField(max_length=254)
    timezone = fields.CharField(max_length=254)

    class Meta:
        ordering = ('name',)


class ReadinessMeasure(IDMixin, TimeStampedMixin, Model):
    user = ForeignKeyField(
        model_name='models.User',
        related_name='readiness_measures',
        on_delete=fields.CASCADE,
    )
    activity_balance = fields.IntField(null=True)
    body_temperature = fields.IntField(null=True)
    hrv_balance = fields.IntField(null=True)
    previous_day_activity = fields.IntField(null=True)
    previous_night = fields.IntField(null=True)
    recovery_index = fields.IntField(null=True)
    resting_heart_rate = fields.IntField(null=True)
    sleep_balance = fields.IntField(null=True)

    class Meta:
        ordering = ('-created_at',)


class SleepMeasure(IDMixin, TimeStampedMixin, Model):
    user = ForeignKeyField(
        model_name='models.User',
        related_name='sleep_measures',
        on_delete=fields.CASCADE,
    )
    deep_sleep = fields.IntField(null=True)
    efficiency = fields.IntField(null=True)
    latency = fields.IntField(null=True)
    rem_sleep = fields.IntField(null=True)
    restfulness = fields.IntField(null=True)
    timing = fields.IntField(null=True)
    total_sleep = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
