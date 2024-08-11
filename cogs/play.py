import typing

from discord.ext import commands
from discord import app_commands
import wavelink
from bot import logger
from classes.AddMoreView import AddMoreView
from classes.Player import Player
import settings
import functions
import asyncio
from discord import app_commands
from youtube_search import YoutubeSearch
import discord


class play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="play")
    @app_commands.describe(search="url (yandex/soundcloud/spotify/youtube/vk/any audiostream or file) or youtube search")
    async def connect(self, ctx: commands.Context, *, search: str, queue_free: typing.Literal[1, 0] = 0):
        """Adds tracks or playlists into the queue"""
        await ctx.defer()
        if not ctx.voice_client:
            if ctx.author.voice:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=Player)
            else:
                await ctx.reply('Connect to the voice channel', ephemeral=True, delete_after=1)
                return
        else:
            vc: wavelink.Player = ctx.voice_client

        # Could be a URL or Plain Search...
        # If the URL is a Spotify URL, make sure you have setup LavaSrc Plugin.
        if "&list=LL&" in search:
            search = search[0:search.index("&list=LL&")]
        if "yandex.kz" in search:
            search = search.replace("yandex.kz", "yandex.ru")

        if not "vk.com" in search:
            try:
                tracks: wavelink.Search = await wavelink.Playable.search(search)
                if not tracks:
                    await ctx.reply("Can't find")
                    return
            except wavelink.LavalinkLoadException:
                await ctx.reply("Lavalink error or no such playlist", ephemeral=True, delete_after=1)
                return

            view = AddMoreView(ctx=ctx, search=search)

            if isinstance(tracks, wavelink.Playlist):
                tracks.track_extras(ctx=ctx)
                if queue_free:
                    for track in tracks[::-1]:
                        vc.queue.put_at(0, track)
                else:
                    await vc.queue.put_wait(tracks)
                await ctx.reply(f'Added {len(tracks)} tracks from the {tracks.name} playlist into the queue.', view=view)
                logger.info(f'Added {len(tracks)} tracks from the {tracks.name} playlist into the queue. AUTHOR - {ctx.author}')

            else:
                track: wavelink.Playable = tracks[0]
                track.ctx = ctx

                if queue_free:
                    vc.queue.put_at(0, tracks[0])
                else:
                    await vc.queue.put_wait(track)
                await ctx.reply(f'Added {track} into the queue.', view=view)
                logger.info(f'Added {track} into the queue. AUTHOR - {ctx.author}')
        else:

            vk_tracks = functions.fetch_vk(token=settings.VK_API_KEY, music_url=search)
            view = None

            async def queue_tracks(vk_tracks, ctx, vc):
                nonlocal view

                async def search_and_queue(vk_track):

                    track = functions.wavelink_create_playable(vk_track, ctx)

                    return track

                if len(vk_tracks) > 1:

                    tasks = [search_and_queue(vk_track) for vk_track in vk_tracks["items"]]
                    search_results = await asyncio.gather(*tasks)

                    if "playlist" in search:
                        playlist_title = functions.vk_get_playlist_title(settings.VK_API_KEY, search)
                    else:
                        playlist_title = vk_tracks["items"][0]["album"]["title"]

                    view = AddMoreView(ctx=ctx, search=search, vk_search_results=search_results, vk_playlist_title=playlist_title)

                    if queue_free:
                        for search_result in search_results[::-1]:
                            vc.queue.put_at(0, search_result)
                    else:
                        await vc.queue.put_wait(search_results)

                    await ctx.reply(
                        f'Added {vk_tracks["count"]} tracks from the {playlist_title} playlist into the queue.',
                        view=view)
                else:
                    vk_track = vk_tracks[0]

                    track = functions.wavelink_create_playable(vk_track, ctx)

                    view = AddMoreView(ctx=ctx, search=search, vk_search_results=[track])

                    if queue_free:
                        vc.queue.put_at(0, track)
                    else:
                        await vc.queue.put_wait(track)
                    await ctx.reply(f"Added {vk_track['title']} into the queue.", view=view)

            await queue_tracks(vk_tracks, ctx, vc)

        if not vc.current:
            await vc.play(vc.queue.get())
            logger.info(f'Connected to the voice channel at the {vc.guild.name}. AUTHOR - {ctx.author}')

        if view:
            await view.wait()

    @connect.autocomplete('search')
    async def search_autocomplete(self, interaction, current):
        data = []

        results = await functions.run_blocking(YoutubeSearch, current, max_results=10)
        results = results.to_dict()
        for result in results:
            name = result['title']
            value = 'https://www.youtube.com' + result['url_suffix']

            data.append(app_commands.Choice(name=name, value=value))

        return data


async def setup(bot):
    await bot.add_cog(play(bot))
