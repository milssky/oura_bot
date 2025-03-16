import logging
import os
from datetime import date, datetime
from typing import Any, Coroutine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot

from oura_bot.client import OuraClient
from oura_bot.models import ReadinessMeasure, SleepMeasure, User
from oura_bot.provider import container
from oura_bot.repository import OuraRepository
from oura_bot.utils import load_users

logging.basicConfig(level=logging.INFO)


async def get_and_save_measures_by_user(
    user: dict[str, str] | User, repository: OuraRepository, client: OuraClient
) -> Coroutine | None:
    """Save to DB user measurements."""
    if isinstance(user, dict):
        logging.info(f'Pulling data for {user["name"]}')
        user, _ = await User.get_or_create(name=user['name'], timezone=user['timezone'])
    readiness = await repository.get_daily_readiness(client)
    sleep = await repository.get_total_sleep(client)

    if readiness is None or sleep is None:
        scheduler = container.get(AsyncIOScheduler)
        scheduler.add_job(
            get_and_save_measures_by_user,
            kwargs={'user': user, 'repository': repository, 'client': client},
            trigger=IntervalTrigger(seconds=10),
        )
        logging.warning(f'new pull task for {user.name}')
        return None
    readiness = readiness.contributors.model_dump(exclude={'id'})
    sleep = sleep.contributors.model_dump(exclude={'id'})

    await ReadinessMeasure.all().delete()
    await SleepMeasure.all().delete()

    await ReadinessMeasure.create(user=user, **readiness)
    await SleepMeasure.create(user=user, **sleep)


async def collect_data_to_send(
    clients: list[tuple[OuraClient, dict[str, str]]], date: date
) -> dict[str, Any]:
    """Do main task."""
    from tortoise.contrib.pydantic import pydantic_model_creator

    sleep_measure_dto = pydantic_model_creator(SleepMeasure, exclude=('user',))
    readiness_measure_dto = pydantic_model_creator(ReadinessMeasure, exclude=('user',))

    data = {}
    for _, user in clients:
        data[user['name']] = dict()
        sleep_out = [
            (await sleep_measure_dto.from_tortoise_orm(sleep)).model_dump(
                exclude={
                    'id',
                    'created_at',
                    'updated_at',
                    'user_id',
                    'efficiency',
                    'latency',
                    'rem_sleep',
                    'restfulness',
                    'timing',
                }
            )
            for sleep in await SleepMeasure.filter(user__name=user['name']).prefetch_related('user')
        ]
        readiness_out = [
            (await readiness_measure_dto.from_tortoise_orm(measure)).model_dump(
                exclude={
                    'id',
                    'created_at',
                    'updated_at',
                    'user_id',
                    'activity_balance',
                    'body_temperature',
                    'previous_day_activity',
                    'previous_night',
                    'sleep_balance',
                }
            )
            for measure in await ReadinessMeasure.filter(user__name=user['name']).prefetch_related(
                'user'
            )
        ]
        data[user['name']]['sleep'] = sleep_out
        data[user['name']]['readiness'] = readiness_out
    return data


def format_data(data: dict[str, Any]):  # noqa
    from oura_bot.settings import MESSAGE_FORMAT

    result = ''
    for user, user_data in data.items():
        sleep_data = user_data['sleep']
        readiness_data = user_data['readiness']
        sleep = (
            ', '.join([f'{k}: {v}' for k, v in sleep_data[0].items()]) if sleep_data else 'empty'
        )
        readiness = (
            ' '.join([f'{k}: {v}' for k, v in readiness_data[0].items()])
            if readiness_data
            else 'empty'
        )
        result += MESSAGE_FORMAT.format(name=user, sleep=sleep, readiness=readiness)
    return result


async def pull_and_send_task() -> None:
    """Send pulled data to admin chat."""
    logging.info('Pulling data...')
    container.get(Bot)
    repository = OuraRepository()

    clients = [(OuraClient(token=user['token']), user) for user in load_users()]

    for client, user in clients:
        await get_and_save_measures_by_user(user, repository, client)

    data = await collect_data_to_send(clients, date=datetime.now())
    data = format_data(data)
    bot = container.get(Bot)
    await bot.send_message(
        chat_id=os.environ.get('ADMIN_TG_CHAT_ID'),
        text=data,
    )
