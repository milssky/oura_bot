import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, make_container, provide
from telegram import Bot


class ServiceProvider(Provider):
    """TG bot DI provider."""

    @provide(scope=Scope.APP)
    def get_bot(self) -> Bot:
        return Bot(token=os.environ['BOT_TOKEN'])

    @provide(scope=Scope.APP)
    def get_sheduler(self) -> AsyncIOScheduler:
        return AsyncIOScheduler()


container = make_container(ServiceProvider())
