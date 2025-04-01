from oura_bot.logger import setup_root_logger
from oura_bot.schedule import run

if __name__ == '__main__':
    import asyncio

    setup_root_logger()
    asyncio.run(run())
