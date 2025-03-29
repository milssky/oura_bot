import logging
import os
from typing import Coroutine

from telegram import Bot

from oura_bot.client import OuraClient
from oura_bot.models import User
from oura_bot.provider import container
from oura_bot.repository import OuraRepository, UserMeasureRepository
from oura_bot.utils import load_users

logging.basicConfig(level=logging.INFO)


async def get_and_save_measures_by_user(
    user_data: dict[str, str],
    client: OuraClient,
) -> Coroutine | None:
    """Save to DB user measurements."""
    user_repo = container.get(UserMeasureRepository)
    user = await user_repo.get_user(user_data=user_data)
    logging.info(f'Pulling for {user.name}')
    oura_repo = container.get(OuraRepository)
    measure = await oura_repo.get_total_sleep(user_client=client)
    user_measure = await user_repo.create_user_measure(measure=measure, user=user)
    if user_measure is None:
        pass  # TODO: новая задача по перепуллу, если пустое измерение пришло


async def send_all_data_task() -> None:
    """Collect and send all data to tg admin."""
    users = await User.all()
    user_repo = container.get(UserMeasureRepository)
    output_data = []
    for user in users:
        measure = await user_repo.get_user_measure_with_diff(user=user)
        output_data.append(measure if measure is not None else '')
    bot = container.get(Bot)
    await bot.send_message(
        chat_id=os.environ.get('ADMIN_TG_CHAT_ID'),
        text=''.join(output_data),
    )


async def pull_and_send_task() -> None:
    """Send pulled data to admin chat."""
    logging.info('Pulling data...')

    clients = [(OuraClient(token=user['token']), user) for user in load_users()]

    for client, user in clients:
        await get_and_save_measures_by_user(user, client)
    await send_all_data_task()
