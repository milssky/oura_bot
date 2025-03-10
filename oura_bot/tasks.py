import logging
from typing import Coroutine

from telegram import Bot

from oura_bot.client import OuraClient
from oura_bot.models import ReadinessMeasure, SleepMeasure, User
from oura_bot.provider import container
from oura_bot.repository import OuraRepository
from oura_bot.utils import load_users

logging.basicConfig(level=logging.INFO)


async def get_and_save_measures_by_user(
    username: str, repository: OuraRepository, client: OuraClient
) -> Coroutine | None:
    """Save to DB user measurements."""
    logging.info(f'Pulling data for {username}')
    user, _ = await User.get_or_create(name=username)
    readiness = await repository.get_daily_readiness(client)
    sleep = await repository.get_total_sleep(client)

    if readiness is None or sleep is None:
        return None  # TODO: new pull task
    readiness = readiness.contributors.model_dump(exclude={'id'})
    sleep = sleep.contributors.model_dump(exclude={'id'})

    await ReadinessMeasure.create(user=user, **readiness)
    await SleepMeasure.create(user=user, **sleep)


async def pull_and_send_task() -> None:
    """Send pulled data to admin chat."""
    logging.info('Pulling data...')
    container.get(Bot)
    repository = OuraRepository()

    clients = [(OuraClient(token=user['token']), user['name']) for user in load_users()]

    for client, username in clients:
        await get_and_save_measures_by_user(username, repository, client)
