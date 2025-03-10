import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tortoise import Tortoise

from oura_bot.provider import container
from oura_bot.settings import RETRY_PERIOD_SEC
from oura_bot.tasks import pull_and_send_task


async def run() -> None:
    """Entry point."""
    scheduler = container.get(AsyncIOScheduler)
    scheduler.add_job(pull_and_send_task, IntervalTrigger(seconds=RETRY_PERIOD_SEC))

    await Tortoise.init(db_url='sqlite://storage.sqlite', modules={'models': ['oura_bot.models']})
    await Tortoise.generate_schemas()

    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        await Tortoise.close_connections()
