import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, make_container, provide
from telegram import Bot

from oura_bot.repository import OuraRepository, UserMeasureRepository


class ServiceProvider(Provider):
    """TG bot DI provider."""

    @provide(scope=Scope.APP)
    def get_bot(self) -> Bot:
        return Bot(token=os.environ['BOT_TOKEN'])

    @provide(scope=Scope.APP)
    def get_scheduler(self) -> AsyncIOScheduler:
        return AsyncIOScheduler()

    @provide(scope=Scope.APP)
    def get_user_repo(self) -> UserMeasureRepository:
        return UserMeasureRepository()

    @provide(scope=Scope.APP)
    def get_oura_repo(self) -> OuraRepository:
        return OuraRepository()


container = make_container(ServiceProvider())
