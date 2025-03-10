import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from oura_bot.tasks import pull_and_send_task


async def run() -> None:
    """Entry point."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(pull_and_send_task, IntervalTrigger(seconds=10))
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
