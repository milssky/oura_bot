import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tortoise import Tortoise

from oura_bot.provider import container
from oura_bot.settings import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_PORT,
    DB_USER,
    RETRY_PERIOD_DAYS,
)
from oura_bot.tasks import pull_and_send_task


async def run() -> None:
    """Entry point."""
    scheduler = container.get(AsyncIOScheduler)
    scheduler.add_job(
        pull_and_send_task,
        IntervalTrigger(
            days=RETRY_PERIOD_DAYS,
            start_date=datetime(
                2025, 3, 31, 10, 0, 0, tzinfo=ZoneInfo('Europe/Moscow')
            ),
        ),
    )

    await Tortoise.init(
        db_url=f'asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        modules={'models': ['oura_bot.models']},
    )
    await Tortoise.generate_schemas()

    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        await Tortoise.close_connections()
