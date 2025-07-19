import json

import responses
import openai
from json import loads
from discord import Embed
import re
import settings
import struct
import wavelink
import functools
import logging
from bot import bot
import requests


async def get_chat_response(session, result, messages):
    """Gets response from LLM api"""

    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    async with session.post(
        settings.chatgpt_settings["text_api_endpoint"],
        headers=headers,
        json={
            "model": settings.chatgpt_settings["text_model"],
            "messages": [{"role": "system", "content": result}] + messages
        },
    ) as response:
        response_data = await response.json()
        print(response_data)
        return response_data


async def get_image_response(session, result, size, model):
    """Gets response from image generator api"""

    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    async with session.post(
        settings.chatgpt_settings["image_api_endpoint"],
        headers=headers,
        json={
            "model": model,
            "prompt": result,
            "n": 1,
            "size": size
        },
    ) as response:
        response_data = await response.json()
        return response_data


async def send_message(message, user_message, is_private):
    """Sends a message in response to the another message"""
    try:
        response = responses.handle_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        logging.error(e)


def parse_embed_json(json_file):
    """Parses embed and returns a list generator"""
    embeds_json = loads(json_file)['embeds']

    for embed_json in embeds_json:
        embed = Embed().from_dict(embed_json)
        yield embed


async def run_blocking(blocking_func, *args, **kwargs):
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)
