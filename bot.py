import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import settings
import wavelink
from typing import Any
import emoji
import openai
import json
import aiohttp
from pygelbooru import Gelbooru
import asyncio
import time
import re
import functions


logger = settings.logging.getLogger("discord")
openai.api_key = settings.OPENAI_API_SECRET


class Player(wavelink.Player):
    """A Player with a DJ attribute."""

    def __init__(self, dj: discord.Member, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.dj = dj
        self.queue = wavelink.Queue()


class AddMoreView(discord.ui.View):
    """Handling 'Add one more time' button"""

    def __init__(self, ctx, search):
        super().__init__(timeout=3600)
        self.ctx = ctx
        self.search = search

    @discord.ui.button(label="Add one more time", style=discord.ButtonStyle.primary)
    async def one_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        """'Add one more time button itself'"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:

            if not self.ctx.voice_client:
                if self.ctx.author.voice:
                    vc: wavelink.Player = await self.ctx.author.voice.channel.connect(cls=wavelink.Player)
                else:
                    await self.ctx.send('Please enter the voice channel', ephemeral=True)
                    return
            else:
                vc: wavelink.Player = self.ctx.voice_client

            tracks: wavelink.Search = await wavelink.Playable.search(self.search)

            if isinstance(tracks, wavelink.Playlist):
                tracks.track_extras(ctx=self.ctx)
                added: int = await vc.queue.put_wait(tracks)

                await interaction.message.edit(content=f'Added {added} tracks from the playlist {tracks.name} in the queue.', view=AddMoreView(ctx=self.ctx, search=self.search))
            else:
                track: wavelink.Playable = tracks[0]
                track.ctx = self.ctx
                await vc.queue.put_wait(track)

                await interaction.message.edit(content=f'Added {track} in the queue', view=AddMoreView(ctx=self.ctx, search=self.search))

            if not vc.current:
                await vc.play(vc.queue.get())
        self.stop()


class NaviPanelView(discord.ui.View):
    """Handling all player buttons"""

    def __init__(self, ctx, embed):
        super().__init__(timeout=3600)
        self.ctx = ctx
        self.embed = embed

    @discord.ui.button(emoji=emoji.emojize(':next_track_button:'), style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Skip button"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            if not self.ctx.author.voice:
                await self.ctx.send('Please enter the voice channel', ephemeral=True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                return
            else:
                vc: wavelink.Player = self.ctx.voice_client
            await vc.skip()
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':pause_button:'), style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pause button"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            if not self.ctx.author.voice:
                await self.ctx.send('Please enter the voice channel', ephemeral=True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                return
            else:
                vc: wavelink.Player = self.ctx.voice_client
            if not vc.paused and vc.current:
                await vc.pause(True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
            else:
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':play_button:'), style=discord.ButtonStyle.primary)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Resume button"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            if not self.ctx.author.voice:
                await self.ctx.send('Please enter the voice channel', ephemeral=True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                return
            else:
                vc: wavelink.Player = self.ctx.voice_client
            if vc.paused and vc.current:
                await vc.pause(False)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
            else:
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':input_numbers:'), style=discord.ButtonStyle.primary)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Queue button"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            if not self.ctx.author.voice:
                await self.ctx.send('Please enter the voice channel', ephemeral=True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                return
            else:
                vc: wavelink.Player = self.ctx.voice_client
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                if vc.queue:
                    await self.ctx.send(embed=discord.Embed(title="First 20 tracks in the queue", description='Now playing: ' + str(vc.current) + '\n' + '\n'.join([str(que) for que in vc.queue[:20]])), ephemeral=True)
                else:
                    await self.ctx.send(embed=discord.Embed(title="Now playing:", description=vc.current), ephemeral=True)
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':shuffle_tracks_button:'), style=discord.ButtonStyle.primary)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shuffle button"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            if not self.ctx.author.voice:
                await self.ctx.send('Please enter the voice channel', ephemeral=True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                return
            else:
                vc: wavelink.Player = self.ctx.voice_client
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                if vc:
                    vc.queue.shuffle()
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':cross_mark:'), style=discord.ButtonStyle.primary)
    async def disconnect_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Disconnect button"""
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            if not self.ctx.author.voice:
                await self.ctx.send('Please enter the voice channel', ephemeral=True)
                await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                return
            else:
                vc: wavelink.Player = self.ctx.voice_client
            if vc:
                vc.cleanup()
                await vc.disconnect()
                await interaction.message.edit(content='Was playing before:', embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
                logger.info(f'Disconnected from the voice channel at the {vc.guild}')
            else:
                await self.ctx.send("I'm not in the voice channel", ephemeral=True)
                await interaction.message.edit(content='Was playing before:', embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed))
        self.stop()


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="@!@", intents=intents)


@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload) -> None:
    """Handling bot disconnect on the queue end"""
    player = payload.player

    if player is not None:
        if player.queue:
            await player.play(player.queue.get())
        else:
            player.cleanup()
            await player.disconnect()
            logger.info(f'Disconnected from the voice channel at the {player.guild}')


@bot.event
async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload) -> None:
    """Sending an embed at the start of every track"""

    # Payload original is the "original" track that was added to the queue, with all custom attributes we set.

    embed = discord.Embed(
        colour=discord.Colour.magenta(),
        title=payload.original.title,
        description=payload.original.author,
        url=payload.original.uri
    )

    embed.set_author(name='Now playing')
    minutes, seconds = divmod(payload.original.length / 1000, 60)
    embed.add_field(name="Duration", value=f"{int(minutes):02d}:{int(seconds):02d}")
    embed.set_thumbnail(url=payload.original.artwork)

    view = NaviPanelView(ctx=payload.original.ctx, embed=embed)

    if payload.original:
        await payload.original.ctx.send(embed=embed, view=view)

    await view.wait()


# @bot.event
# async def is_owner(interaction: discord.Interaction):
#     return interaction.user.id == interaction.guild.owner_id


@bot.event
async def on_ready():
    """Starts check_voice_channels and bot.tree.sync()"""
    logger.info(f'User: {bot.user} (ID: {bot.user.id}) is now running!')
    check_voice_channels.start()

    await bot.tree.sync()


@bot.event
async def on_message(message):
    """Handling every message"""
    if message.author == bot.user:
        return

    if message.content:
        user_message = str(message.content)
    else:
        user_message = "image/file"
    username = str(message.author)
    channel = str(message.channel)
    guild = str(message.guild)

    logger.info(f'{username} said {user_message} in the {channel} at the {guild}')

    # Custom message handling instead of the bot.process_commands because it requires prefix

    if user_message[0] == '?':
        user_message = user_message[1:]
        await functions.send_message(message, user_message, is_private=True)
    else:
        await functions.send_message(message, user_message, is_private=False)


@bot.event
async def on_command_error(ctx, error):
    """Sending errors in the discord as messages"""
    if isinstance(error, Exception):
        await ctx.send(error)


@bot.event
async def setup_hook():
    """Connecting to the Lavalink"""
    node: wavelink.Node = wavelink.Node(uri=settings.LAVALINK_SERVER_URL, password=settings.LAVALINK_PASSWORD)
    await wavelink.Pool.connect(client=bot, nodes=[node])


@bot.hybrid_command(name="play")
@app_commands.describe(search="url (yandex/soudcloud/spotify/youtube) or just the search on youtube")
async def connect(ctx: commands.Context, *, search: str):
    """Adding tracks and playlists in the queue"""
    await ctx.defer()
    if not ctx.voice_client:
        if ctx.author.voice:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            await ctx.reply('Please enter the voice channel', ephemeral=True, delete_after=1)
            return
    else:
        vc: wavelink.Player = ctx.voice_client

    # Could be a URL or Plain Search...
    # If the URL is a Spotify URL, make sure you have setup LavaSrc Plugin.
    if "&list=LL&" in search:
        search = search[0:search.index("&list=LL&")]

    try:
        tracks: wavelink.Search = await wavelink.Playable.search(search)
        if not tracks:
            await ctx.reply("Не ищется")
            return
    except wavelink.LavalinkLoadException:
        await ctx.reply("Плейлиста не существует", ephemeral=True, delete_after=1)
        return

    view = AddMoreView(ctx=ctx, search=search)

    if isinstance(tracks, wavelink.Playlist):
        tracks.track_extras(ctx=ctx)
        added: int = await vc.queue.put_wait(tracks)
        await ctx.reply(f'Added {added} tracks from the playlist {tracks.name} in the queue.', view=view)
        logger.info(f'Added {added} tracks from the playlist {tracks.name} in the queue. AUTHOR - {ctx.author}')

    else:
        track: wavelink.Playable = tracks[0]
        track.ctx = ctx

        await vc.queue.put_wait(track)
        await ctx.reply(f'Added {track} in the queue.', view=view)
        logger.info(f'Added {track} in the queue. AUTHOR - {ctx.author}')

    if not vc.current:
        await vc.play(vc.queue.get())
        logger.info(f'Connected to the voice channel at the {vc.guild.name}. AUTHOR - {ctx.author}')

    await view.wait()


@bot.hybrid_command(name="skip")
@app_commands.describe(count="Count of tracks that need to be skipped")
async def skip(ctx, count=1):
    """Skipping tracks"""
    await ctx.defer(ephemeral=True)

    vc: wavelink.Player = ctx.voice_client
    if vc:
        if ctx.author.voice:
            if len(vc.queue) == 0 and vc.playing:
                await vc.skip()
                await ctx.reply('Skipped', delete_after=1, ephemeral=True)
            else:
                for _ in range(count-1):
                    await vc.queue.delete(0)
                await vc.skip()
                await ctx.reply('Skipped', delete_after=1, ephemeral=True)
                logger.info(f'Skipped {count} tracks')
        else:
            await ctx.reply('Please enter the voice channel', delete_after=1, ephemeral=True)
    else:
        await ctx.reply("I'm not in the voice channel", delete_after=1, ephemeral=True)


@bot.hybrid_command(name="seek")
@app_commands.describe(stime="Time to rewind (can be specified in seconds or in 00:00 format)")
async def seek(ctx, stime):
    """Rewind the current track by a specified time"""
    await ctx.defer(ephemeral=True)

    vc: wavelink.Player = ctx.voice_client
    if vc:
        if ctx.author.voice:
            if vc.playing:
                if re.match(r'^\d+(:\d+)?$', stime) is None:
                    await ctx.reply('Please enter seconds or 00:00', ephemeral=True, delete_after=1)
                    return
                if ':' in stime:
                    stime = time.strptime(stime, '%M:%S')
                    stime = str(int(stime[4])*60 + int(stime[5]))
                await vc.seek(stime + '000')
                await ctx.reply('Rewound', delete_after=1, ephemeral=True)
        else:
            await ctx.reply('Please enter the voice channel', delete_after=1, ephemeral=True)
    else:
        await ctx.reply("I'm not in the voice channel", delete_after=1, ephemeral=True)


@bot.hybrid_command(name="chate")
@app_commands.describe(prompt="AI request (if something is serious, then it is better to do it more precisely and with details)")
async def chat(ctx: commands.Context, prompt):
    """Ask AI something (the request and the result are visible only to you)"""
    await ctx.defer(ephemeral=True)
    logger.info(f'Starting openai chatgpt request.... AUTHOR - {ctx.author}')

    result = str(prompt)
    author_log = 'chatgptlog' + str(ctx.author.id) + '.json'

    if author_log not in os.listdir('chatgptlogs'):
        with open('chatgptlogs/' + author_log, 'w', encoding='UTF-8') as file:
            json.dump(
                [
                    {"role": "system",
                     "content": settings.decensor_prompt}
                ], file
            )

    with open('chatgptlogs/' + author_log, 'r', encoding='UTF-8') as messages_file:
        messages = json.load(messages_file)

    messages.append({'role': "user", 'content': result})

    if len(messages) > 8:
        messages = messages[-8:]
        messages[0] = {"role": "system", "content": settings.decensor_prompt}

    async with aiohttp.ClientSession() as session:
        chatgpt = await functions.get_chat_response(session, result, messages)

    logger.info(f'Chatgpt response: {chatgpt["choices"][0]["message"]}. AUTHOR - {ctx.author}')

    reply = chatgpt["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})

    with open('chatgptlogs/' + author_log, 'w', encoding='UTF-8') as messages_file:
        json.dump(messages, messages_file, ensure_ascii=False)

    await ctx.reply(embed=discord.Embed(title=f'{result[:255]}', description=reply), ephemeral=True)
    logger.info(f'Finished Openai chatgpt request. AUTHOR - {ctx.author}')


@bot.hybrid_command(name="chat")
@app_commands.describe(prompt="AI request (if something is serious, then it is better to do it more precisely and with details)")
async def chat(ctx: commands.Context, prompt):
    """Ask AI something (the request and the result are visible to everyone)"""
    await ctx.defer()
    logger.info(f'Starting openai chatgpt request.... AUTHOR - {ctx.author}')

    result = str(prompt)
    author_log = 'chatgptlog' + str(ctx.author.id) + '.json'

    if author_log not in os.listdir('chatgptlogs'):
        with open('chatgptlogs/' + author_log, 'w', encoding='UTF-8') as file:
            json.dump(
                [
                    {"role": "system",
                     "content": settings.decensor_prompt}
                ], file
            )

    with open('chatgptlogs/' + author_log, 'r', encoding='UTF-8') as messages_file:
        messages = json.load(messages_file)

    messages.append({'role': "user", 'content': result})

    if len(messages) > 8:
        messages = messages[-8:]
        messages[0] = {"role": "system", "content": settings.decensor_prompt}

    async with aiohttp.ClientSession() as session:
        chatgpt = await functions.get_chat_response(session, result, messages)

    logger.info(f'Chatgpt response: {chatgpt["choices"][0]["message"]}. AUTHOR - {ctx.author}')

    reply = chatgpt["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})

    with open('chatgptlogs/' + author_log, 'w', encoding='UTF-8') as messages_file:
        json.dump(messages, messages_file, ensure_ascii=False)

    await ctx.reply(embed=discord.Embed(title=f'{result[:255]}', description=reply))
    logger.info(f'Finished Openai chatgpt request. AUTHOR - {ctx.author}')


@bot.hybrid_command(name="image")
@app_commands.describe(
    prompt="Image prompt",
    size="Picture size (allowed 256x526, 512x512, 1024x1024, default 256x256). Only 1024x1024 available for dall-e-3 (default))",
    model="Select a model from two available. 2 to select DALL-E-2, 3 to select DALL-E-3. Default DALL-E-2"
)
async def image(ctx: commands.Context, prompt, size="256x256", model="dall-e-2"):
    """Draw an image with AI"""
    try:
        await ctx.defer()
        logger.info(f'Starting openai DALL-E-2/3 request.... AUTHOR - {ctx.author}')

        result = str(prompt)

        if model == "3":
            size = "1024x1024"
            model = "dall-e-3"
        else:
            model = "dall-e-2"

        if size not in ["256x526", "512x512", "1024x1024"]:
            size = "256x256"

        async with aiohttp.ClientSession() as session:
            chatgpt = await functions.get_image_response(session, result, size, model)

        image_url = chatgpt['data'][0]['url']

        logger.info(f'DALL-E-2/3 response: {image_url}. AUTHOR - {ctx.author}')

        embed = discord.Embed()
        embed.set_image(url=image_url)

        await ctx.reply(result, embed=embed)
        logger.info(f'Finished Openai DALL-E-2/3 request. AUTHOR - {ctx.author}')
    except KeyError:
        embed = discord.Embed()
        embed.set_image(url="https://static.wikia.nocookie.net/lobotomycorp/images/c/cb/CENSOREDPortrait.png/revision/latest?cb=20171119115551")

        await ctx.reply("I don't think so", embed=embed)
        logger.info(f'Censored Openai DALL-E-2/3 request. AUTHOR - {ctx.author}. Response: {chatgpt}')


@bot.hybrid_command(name="clear_history")
async def clear_history(ctx: commands.Context):
    """Deletes your entire message history with AI (for example, if there are too many tokens)"""
    if ('chatgptlog' + str(ctx.author.id) + '.json') in os.listdir('chatgptlogs'):
        os.remove('chatgptlogs/chatgptlog' + str(ctx.author.id) + '.json')
        await ctx.reply('History deleted successfully')
        logger.info(f'{ctx.author} successfully deleted his openai chatgpt history')
    else:
        await ctx.reply('There is no message history')


@bot.hybrid_command(name="gelbooru")
@app_commands.describe(q="Tags (separated by the space)")
async def gelbooru(ctx: commands.Context, q):
    """Random image/GIF/video from gelbooru by tags"""
    if ctx.channel.is_nsfw():
        await ctx.defer()

        logger.info(f'Starting Gelbooru request.... AUTHOR - {ctx.author}')

        gelbooru = Gelbooru(settings.GELBOORU_API_SECRET, settings.GELBOORU_USER_ID)
        q = q.split()

        result = await gelbooru.random_post(tags=q, exclude_tags=['loli', 'guro', 'toddler', 'shota'])

        if result:
            logger.info(f'Gelbooru response: {result}. AUTHOR - {ctx.author}')

            embed = discord.Embed()
            embed.set_image(url=result)

            logger.info(f'Finished Gelbooru request. AUTHOR - {ctx.author}')

            if '.mp4' in result.filename:
                await ctx.reply(result)
            else:
                await ctx.reply(' '.join(q), embed=embed)
        else:
            await ctx.reply(
                "The request was censored (this may happen accidentally if"
                "as a result, a post with censored tags or pictures appeared)"
                "or there are no picture with such tags (tags must be entered accurately)", ephemeral=True)
            logger.info(f'Censored Gelbooru request. AUTHOR - {ctx.author}')
    else:
        await ctx.reply("This is not a NSFW channel", ephemeral=True)


@tasks.loop(seconds=6)
async def check_voice_channels():
    for player in bot.voice_clients:
        if len(player.channel.members) == 1:
            await asyncio.sleep(1)
            if len(player.channel.members) == 1:
                player.cleanup()
                await player.disconnect()
                logger.info(f'Disconnected from the voice channel at the {player.guild}')


def run_discord_bot():
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
