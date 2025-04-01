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


class SleepMeasure(IDMixin, TimeStampedMixin, Model):
    user = ForeignKeyField(
        model_name='models.User',
        related_name='sleep_measures',
        on_delete=fields.CASCADE,
    )
    deep_sleep_duration = fields.IntField(null=True)
    total_sleep_duration = fields.IntField(null=True)
    average_hrv = fields.FloatField(null=True)
    average_heart_rate = fields.FloatField(null=True)
    score = fields.IntField()
    recovery_index = fields.IntField()

    class Meta:
        ordering = ('-created_at',)
