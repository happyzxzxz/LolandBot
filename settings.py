import os
import pathlib
from dotenv import load_dotenv
from logging.config import dictConfig
import logging
import yaml
from requests import get

load_dotenv()

ENABLED_COMMANDS = {
    "skip": True, # Skip song
    "play": True, # Place song/playlsit/whatever into the queue
    "seek": True, # Seek in the song
    "create_new_equalizer": True, # Create new equalizer preset for this server
    "equalizer": True, # Set equalizer preset
    "filter": True, # Set filters for this current player
    "sauce": True, # You need SAUCENAO_API_KEY. Seek an image source with saucenao.com
    "reaction_role": True, # Add reaction role to a message
    "image": False, # You need OPENAI_API_TOKEN. Generate an image with DALL-E
    "gelbooru": True, # You need GELBOORU_API_TOKEN and GELBOORU_USER_ID. Post an image from gelbooru with tags
    "clear_history": True, # You need OPENAI_API_TOKEN. Clear your personal history with chatbot
    "chat": True, # You need OPENAI_API_TOKEN. Use LMM chatbot
    "text_to_speech": True, # RMB application menu that will read any discord message to the current player
    "Events": True, # DO NOT TURN THIS ONE OFF
}

# CHANGE THIS IF YOU WANT TO USE DIFFERENT API ENDPOINT, FOR EXAMPLE NOT CHATGPT BUT OTHER LLM (may not work with everything)
chatgpt_settings = {
    "text_model": "gpt-4.1", # Set your text model here
    "text_api_endpoint": "https://api.openai.com/v1/chat/completions", # Api endpoint for text generation
    "image_api_endpoint": "https://api.openai.com/v1/images/generations", # Api endpoint for image generation
}

decensor_prompt = ("You are Loland, chat bot and helper.") # for LLM
openai_censored_image_url = "https://static.wikia.nocookie.net/lobotomycorp/images/c/cb/CENSOREDPortrait.png/revision/latest?cb=20171119115551" # when image generator response is censored
excluded_gelbooru_tags = ['loli', 'guro', 'toddler', 'shota'] # very important to not get banned

# PLEASE DON'T TOUCH ANYTHING DOWN BELOW

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
OPENAI_API_SECRET = os.getenv("OPENAI_API_TOKEN")
GELBOORU_API_SECRET = os.getenv("GELBOORU_API_TOKEN")
GELBOORU_USER_ID = os.getenv("GELBOORU_USER_ID")
YANDEX_API_SECRET = os.getenv("YANDEX_MUSIC_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SAUCENAO_API_KEY = os.getenv("SAUCENAO_API_KEY")
VK_API_KEY = os.getenv("VK_API_KEY")
LAVALINK_SERVER_URL = os.getenv("LAVALINK_SERVER_URL")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")
VK_API_KEY = os.getenv("VK_API_KEY")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")

BASE_DIR = pathlib.Path(__file__).parent

COGS_DIR = BASE_DIR / "cogs"

PUBLIC_IP = get('https://api.ipify.org').content.decode('utf8')

with open(BASE_DIR / "Lavalink" / "application.yml", 'r') as file:
    config_data = yaml.safe_load(file)

config_data['plugins']['lavasrc']['spotify']['clientId'] = SPOTIFY_CLIENT_ID
config_data['plugins']['lavasrc']['spotify']['clientSecret'] = SPOTIFY_CLIENT_SECRET
config_data['plugins']['lavasrc']['yandexmusic']['accessToken'] = YANDEX_API_SECRET
config_data['plugins']['lavasrc']['vkmusic']['userToken'] = VK_API_KEY
config_data['plugins']['youtube']['oauth']['refreshToken'] = YOUTUBE_REFRESH_TOKEN
config_data['lavalink']['server']['sources']['local'] = True
config_data['server']['address'] = LAVALINK_SERVER_URL[LAVALINK_SERVER_URL.find('://')+3:LAVALINK_SERVER_URL.rfind(':')]
config_data['server']['port'] = int(LAVALINK_SERVER_URL[LAVALINK_SERVER_URL.rfind(':')+1:])

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
