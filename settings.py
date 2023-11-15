import os
import pathlib
from dotenv import load_dotenv
from logging.config import dictConfig
import logging

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
OPENAI_API_SECRET = os.getenv("OPENAI_API_TOKEN")
GELBOORU_API_SECRET = os.getenv("GELBOORU_API_TOKEN")
GELBOORU_USER_ID = os.getenv("GELBOORU_USER_ID")

BASE_DIR = pathlib.Path(__file__).parent

COGS_DIR = BASE_DIR / "cogs"

list_of_paths = (BASE_DIR / "logs").glob('*.log')
latest_path = max(list_of_paths, key=lambda p: p.stat().st_ctime)

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(name)-15s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": f"{latest_path}",
            "mode": "a+"
        }
    },
    "loggers": {
        "bot": {
            "handlers": ['console'],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            "handlers": ['console', 'console2', "file"],
            "level": "INFO",
            "propagate": False,
            "encoding": "utf-8",
        }
    }
}

dictConfig(LOGGING_CONFIG)
