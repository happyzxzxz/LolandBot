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
from youtube_search import YoutubeSearch


class play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="play")
    @app_commands.describe(search="url (Any audiostream or file) or youtube search",
                           queue_free="Queue free? (current track is not skipped)")
    async def connect(self, ctx: commands.Context, *, search: str, queue_free: typing.Literal[1, 0] = 0):
        """Add tracks or playlists into the queue"""
        await ctx.defer()
        if not ctx.voice_client:
            if ctx.author.voice:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=Player)
            else:
                await ctx.reply('Enter the voice channel', ephemeral=True, delete_after=1)
                return
        else:
            vc: wavelink.Player = ctx.voice_client

        if "&list=LL&" in search:
            search = search[0:search.index("&list=LL&")]
        if "yandex.kz" in search:
            search = search.replace("yandex.kz", "yandex.ru")

        try:
            tracks: wavelink.Search = await wavelink.Playable.search(search)
            if not tracks:
                await ctx.reply("Can't find")
                return
        except wavelink.LavalinkLoadException:
            await ctx.reply("Something wrong with the node (youtube issue in the most cases). Please report to the bot hoster", ephemeral=True, delete_after=5)
            return

        view = AddMoreView(ctx=ctx, search=search)

        if isinstance(tracks, wavelink.Playlist):
            tracks.track_extras(ctx=ctx)
            if queue_free:
                for track in tracks[::-1]:
                    vc.queue.put_at(0, track)
            else:
                await vc.queue.put_wait(tracks)
            await ctx.reply(f'Added {len(tracks)} tracks from the playlist {tracks.name} into the queue.', view=view)
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

        if not vc.current:
            await vc.play(vc.queue.get())
            logger.info(f'Connected to the voice channel at the {vc.guild.name}. AUTHOR - {ctx.author}')

        if view:
            await view.wait()

    @connect.autocomplete('search')
    async def search_autocomplete(self, interaction, current):
        # Keep in mind that if bot doesn't respond in 3 sec then interaction will delete itself, there is no way to fix it
        data = []

        results = await functions.run_blocking(YoutubeSearch, current, max_results=10)
        results = results.to_dict()
        for result in results:
            name = result['title']

            if len(name) > 100: # Discord limitation is 100 in autocompletions. shit yea
                name = name[:97] + "..."
                
            url_suffix = result['id']

            if len(url_suffix) > 73:  # 100 - len("https://www.youtube.com/watch?v=")
                continue 
                
            value = 'https://www.youtube.com/watch?v=' + url_suffix
            data.append(app_commands.Choice(name=name, value=value))

        return data


async def setup(bot):
    await bot.add_cog(play(bot))
