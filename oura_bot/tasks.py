import logging
import os
from datetime import date, datetime, timedelta
from typing import Coroutine, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot
from tortoise.contrib.pydantic import PydanticListModel

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

    await ReadinessMeasure.create(user=user, **readiness)
    await SleepMeasure.create(user=user, **sleep)


async def collect_data_to_send(clients: list[tuple[OuraClient, dict[str, str]]], date: date) -> dict[str, Any]:
    from tortoise.contrib.pydantic import pydantic_model_creator, PydanticListModel

    SleepMeasureDTO = pydantic_model_creator(SleepMeasure)
    ReadinessMeasureDTO = pydantic_model_creator(ReadinessMeasure)

    SleepOutDTO = PydanticListModel[SleepMeasureDTO]
    ReadinessOutDTO = PydanticListModel[ReadinessMeasureDTO]

    data = {}
    for _, user in clients:
        data[user['name']] = dict()
        sleep_out = SleepMeasure.filter(user__name=user['name']).prefetch_related('user')
        readiness_out = ReadinessMeasure.filter(user=user['name']).prefetch_related('user')
        data[user['name']]['sleep'] = await SleepOutDTO.from_queryset(sleep_out)
        data[user['name']]['readiness'] = await ReadinessOutDTO.from_queryset(readiness_out)

    return data

async def pull_and_send_task() -> None:
    """Send pulled data to admin chat."""
    logging.info('Pulling data...')
    container.get(Bot)
    repository = OuraRepository()

    clients = [(OuraClient(token=user['token']), user) for user in load_users()]

    for client, user in clients:
        await get_and_save_measures_by_user(user, repository, client)
        
    data = await collect_data_to_send(clients, date=datetime.now())

    import json

    data = json.dumps(data)
    bot = container.get(Bot)
    bot.send_message(
        chat_id=os.environ.get('ADMIN_TG_CHAT_ID'),
        text=data,
    )


