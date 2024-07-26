import responses
import openai
from json import loads
from discord import Embed
import vk_api
import re
import settings


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


def set_playable_vk(vk_track, track, ctx):

    track = track[0]
    track.ctx = ctx
    track.track_title = vk_track['title']
    track.track_author = vk_track['artist']

    if any(key == 'album' for key in vk_track):
        track.track_artwork = vk_track['album']['thumb']['photo_300']
    else:
        track.track_artwork = None

    if any('access_key' in key for key in vk_track):
        track.track_uri = 'https://vk.com/audio' + vk_track['ads']['content_id'] + '_' + vk_track['access_key']
    else:
        track.track_uri = 'https://vk.com/audio' + vk_track['ads']['content_id']

    return track
