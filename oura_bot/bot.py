import os

from dishka import Provider, Scope, make_container, provide
from telegram import Bot


class BotProvider(Provider):
    """TG bot DI provider."""

    @provide(scope=Scope.APP)
    def get_bot(self) -> Bot:
        return Bot(token=os.environ['BOT_TOKEN'])


bot_container = make_container(BotProvider())
