import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_root_logger() -> None:
    """Configure root logger."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5),
        ],
    )
