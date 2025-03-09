import os

from telegram import Bot


def get_bot(token: str) -> Bot:
    """TG bot fabric."""
    return Bot(token=token)



bot = get_bot(
    token=os.environ['BOT_TOKEN']
)
