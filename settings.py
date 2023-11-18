import os
import pathlib
from dotenv import load_dotenv
from logging.config import dictConfig
import logging
import yaml

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
OPENAI_API_SECRET = os.getenv("OPENAI_API_TOKEN")
GELBOORU_API_SECRET = os.getenv("GELBOORU_API_TOKEN")
GELBOORU_USER_ID = os.getenv("GELBOORU_USER_ID")
YANDEX_API_SECRET = os.getenv("YANDEX_MUSIC_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

BASE_DIR = pathlib.Path(__file__).parent

COGS_DIR = BASE_DIR / "cogs"

with open(BASE_DIR / "Lavalink" / "application.yml", 'r') as file:
    config_data = yaml.safe_load(file)

config_data['plugins']['lavasrc']['spotify']['clientId'] = SPOTIFY_CLIENT_ID
config_data['plugins']['lavasrc']['spotify']['clientSecret'] = SPOTIFY_CLIENT_SECRET
config_data['plugins']['lavasrc']['yandexmusic']['accessToken'] = YANDEX_API_SECRET

with open(BASE_DIR / "Lavalink" / "application.yml", 'w') as file:
    yaml.dump(config_data, file)

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
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "verbose",
            "filename": "logs/BotLog.log",
            "backupCount": 10,
            "when": "midnight",
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
