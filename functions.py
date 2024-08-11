import responses
import openai
from json import loads
from discord import Embed
import vk_api
import re
import settings
import struct
from base64 import b64encode
import wavelink
from classes.DataWriter import DataWriter
import functools
from bot import bot


async def get_chat_response(session, result, messages):

    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    async with session.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": result}] + messages
        },
    ) as response:
        response_data = await response.json()
        return response_data


async def get_image_response(session, result, size, model):

    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    async with session.post(
        "https://api.openai.com/v1/images/generations",
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
    try:
        response = responses.handle_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def parse_embed_json(json_file):
    embeds_json = loads(json_file)['embeds']

    for embed_json in embeds_json:
        embed = Embed().from_dict(embed_json)
        yield embed


def fetch_vk(token, music_url):
    session = vk_api.VkApi(app_id=2685278,  token=token)

    if "vk.com/audio" in music_url:
        match = re.search(r'audio(-?\d+_\d+)', music_url)

        if match:
            extracted_string = match.group(1)
            audio = session.method("audio.getById", {"audios": extracted_string})

    if "vk.com/music/album" in music_url:
        match = re.search(r'album/(-?\d+_\d+_\w+)', music_url)

        if match:
            extracted_string = match.group(0)[6:].split("_")  # Extracting the substring and removing the trailing underscore

            audio = session.method("audio.get", {"owner_id": extracted_string[0], "playlist_id": extracted_string[1], "access_key": extracted_string[2]})

    if "vk.com/music/playlist" in music_url:
        match_regular = re.search(r'playlist/(-?\d+_\d+)', music_url)
        match_owner = re.search(r'playlist/(-?\d+_\d+_\w+)', music_url)

        if match_owner:
            extracted_string = match_owner.group(1).split('_')
        else:
            extracted_string = match_regular.group(1).split('_')

        if len(extracted_string) != 3:
            audio = session.method("audio.get", {"owner_id": extracted_string[0], "playlist_id": extracted_string[1]})
        else:
            audio = session.method("audio.get", {"owner_id": extracted_string[0], "playlist_id": extracted_string[1], "access_key": extracted_string[2]})

    return audio


def vk_get_playlist_title(token, music_url):
    session = vk_api.VkApi(app_id=2685278, token=token)
    playlist_title = "Unknown"

    match_regular = re.search(r'playlist/(-?\d+_\d+)', music_url)
    match_owner = re.search(r'playlist/(-?\d+_\d+_\w+)', music_url)

    if match_owner or match_regular:
        if match_owner:
            extracted_string = match_owner.group(1).split('_')
        else:
            extracted_string = match_regular.group(1).split('_')

        if len(extracted_string) != 3:
            playlist = session.method("audio.getPlaylistById",{"owner_id": extracted_string[0], "playlist_id": extracted_string[1]})
        else:
            playlist = session.method("audio.getPlaylistById", {"owner_id": extracted_string[0], "playlist_id": extracted_string[1], "access_key": extracted_string[2]})

        playlist_title = playlist["title"]

    return playlist_title


def lavalink_encode_tracks(track):

    writer = DataWriter()
    version = struct.pack('B', 3)
    writer.write_byte(version)
    _write_track_common(track, writer)
    writer.write_nullable_utf(track['artworkUrl'])
    writer.write_nullable_utf(track['isrc'])
    writer.write_utf(track['sourceName'])

    writer.write_utf('mp3')
    writer.write_long(track['position'])

    enc = writer.finish()
    return b64encode(enc).decode()


def _write_track_common(track, writer: DataWriter):
    writer.write_utf(track['title'])
    writer.write_utf(track['author'])
    writer.write_long(track['length'])
    writer.write_utf(track['identifier'])
    writer.write_boolean(track['isStream'])
    writer.write_nullable_utf(track['uri'])


def wavelink_create_playable(vk_track, ctx):
    """
    I know that that's not very good, but it seems like the most sane option here
    to maintain low latency and not get rate limited by vk when there are too many tracks
    because lavalink makes a request to the url when creating Playable with search
    """

    if any(key == 'album' for key in vk_track):
        track_artwork = vk_track['album']['thumb']['photo_300']
    else:
        track_artwork = None

    if any('access_key' in key for key in vk_track):
        track_uri = 'https://vk.com/audio' + vk_track['ads']['content_id'] + '_' + vk_track['access_key']
    else:
        track_uri = 'https://vk.com/audio' + vk_track['ads']['content_id']

    info = {
        'identifier': vk_track['url'],
        'isSeekable': True,
        'author': vk_track['artist'],
        'length': vk_track['duration'],
        'isStream': False,
        'position': 0,
        'title': vk_track['title'],
        'uri': track_uri,
        'sourceName': 'http',
        'artworkUrl': track_artwork,
        'isrc': None
    }

    data = {
        'encoded': lavalink_encode_tracks(info),
        'info': info,
        'pluginInfo': {
            'probeInfo': 'mp3'
        },
        'userData': {}
    }

    track = wavelink.Playable(data=data)
    track.ctx = ctx

    return track


async def run_blocking(blocking_func, *args, **kwargs):
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)
