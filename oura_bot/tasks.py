import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot

from oura_bot.client import OuraClient, TrainingPeaksClient
from oura_bot.models import TrainingPeaksUser, User
from oura_bot.provider import container
from oura_bot.repository import (
    OuraRepository,
    TPRepository,
    UserMeasureRepository,
)
from oura_bot.settings import RETRY_FINISH_HOUR
from oura_bot.utils import load_users

logger = logging.getLogger(__name__)


def schedule_user_get_and_save(
    *, user: User, user_data: dict[str, str], client: OuraClient
) -> None:
    """Schedule new pull task by user after one hour."""
    if datetime.now(tz=ZoneInfo(user.timezone)).hour < RETRY_FINISH_HOUR:
        logger.info(f'Planning retry for {user.name}')
        scheduler = container.get(AsyncIOScheduler)
        scheduler.add_job(
            get_and_save_measures_by_user,
            kwargs={'user_data': user_data, 'client': client},
            run_date=datetime.now(tz=ZoneInfo(user.timezone))
            + timedelta(hours=1),
        )


async def get_and_save_measures_by_user(
    user_data: dict[str, str],
    client: OuraClient,
) -> None:
    """Save to DB user measurements."""
    user_repo = container.get(UserMeasureRepository)
    user = await user_repo.get_user(user_data=user_data)
    logger.info(f'Pulling for {user.name}')
    oura_repo = container.get(OuraRepository)
    measure = await oura_repo.get_total_sleep(user_client=client)
    logger.info(f'Pulled measure: {measure}')
    user_measure = await user_repo.create_user_measure(
        measure=measure, user=user
    )
    if user_measure is None:
        schedule_user_get_and_save(
            user=user, user_data=user_data, client=client
        )
        return
    await send_user_data_task(user=user)


async def send_user_data_task(user: User) -> None:
    """Collect and send all data to tg admin."""
    logger.info(f'Sending {user.name} data.')
    user_repo = container.get(UserMeasureRepository)
    output_data = await user_repo.get_user_measure_with_diff(user=user)
    logger.info(f'User measure output data: {output_data}')
    bot = container.get(Bot)
    await bot.send_message(
        chat_id=os.environ.get('ADMIN_TG_CHAT_ID'),
        text=output_data,
    )


async def _pull_oura_data() -> None:
    """Pull data from Oura for all users."""
    logger.info('Pulling Oura data...')
    clients = [(OuraClient(token=user['token']), user) for user in load_users()]
    for client, user in clients:
        await get_and_save_measures_by_user(user, client)


async def _pull_tp_data() -> None:
    """Pull data from TrainingPeaks for all users."""
    tp_repo = container.get(TPRepository)
    tp_token = await tp_repo.get_token()
    bot = container.get(Bot)
    admin_chat_id = os.environ.get('ADMIN_TG_CHAT_ID')

    if not tp_token:
        logger.warning('TP token not found.')
        await bot.send_message(
            chat_id=admin_chat_id,
            text='⚠️ TrainingPeaks token is missing. Please set it using /set_tp_token.',
        )
        return

    logger.info('Pulling TrainingPeaks data...')
    async with TrainingPeaksClient(token=tp_token) as tp_client:
        tp_users = await TrainingPeaksUser.all()
        for tp_user in tp_users:
            try:
                logger.info(f'Pulling TP data for {tp_user.name}')
                response = await tp_client.get_measure_by_user_id(
                    user_id=tp_user.athlete_id
                )
                logger.info(
                    f'TP data for {tp_user.name}: {response.status_code}'
                )
            except Exception as e:
                logger.error(f'Failed to pull TP data for {tp_user.name}: {e}')
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=(
                        f'❌ Error pulling TrainingPeaks data for {tp_user.name}.\n'
                        'The token might be expired or invalid. Please update it using /set_tp_token.'
                    ),
                )


async def pull_and_send_task() -> None:
    """Send pulled data to admin chat."""
    logger.info('Starting data pull task...')
    await _pull_oura_data()
    await _pull_tp_data()
