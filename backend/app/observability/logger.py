import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_DIR = "logs"
os.makedirs(_LOG_DIR, exist_ok=True)

_FMT = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str = "healthai") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(_FMT)
    logger.addHandler(console)

    file_handler = RotatingFileHandler(
        os.path.join(_LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_FMT)
    logger.addHandler(file_handler)

    return logger
