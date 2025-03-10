from typing import Coroutine

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


async def main() -> None:
    """Entry point."""
    clients = [OuraClient(token=user['token']) for user in load_users()]
    repository = OuraRepository()
    tasks = collect_sleep_tasks(repository, clients)
    tasks.extend(collect_readiness_tasks(repository, clients))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
