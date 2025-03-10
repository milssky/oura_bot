import asyncio
import os
from typing import Coroutine

from telegram import Bot

from oura_bot.provider import container
from oura_bot.client import OuraClient
from oura_bot.repository import OuraRepository
from oura_bot.utils import load_users


def collect_sleep_tasks(repository: OuraRepository, clients: list[OuraClient]) -> list[Coroutine]:
    """Generate sleep api call tasks list."""
    return [repository.get_total_sleep(client) for client in clients]


def collect_readiness_tasks(
    repository: OuraRepository, clients: list[OuraClient]
) -> list[Coroutine]:
    """Generate readiness api call tasks list."""
    return [repository.get_daily_readiness(client) for client in clients]


async def pull_and_send_task() -> None:
    """Send pulled data to admin chat."""
    bot = container.get(Bot)
    clients = [OuraClient(token=user['token']) for user in load_users()]
    repository = OuraRepository()
    tasks = collect_sleep_tasks(repository, clients)
    tasks.extend(collect_readiness_tasks(repository, clients))
    result = await asyncio.gather(*tasks)
    for result in result:
        if result is None:
            pass  # TODO: запланировать новую таску
            continue
        await bot.send_message(chat_id=os.environ.get('ADMIN_TG_CHAT_ID'), text=str(result))
