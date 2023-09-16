import discord
import responses
from discord.ext import commands
from discord import app_commands
import settings
import wavelink
from typing import Any
import time


logger = settings.logging.getLogger("bot")


class Player(wavelink.Player):
    """A Player with a DJ attribute."""

    def __init__(self, dj: discord.Member, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.dj = dj
        self.queue = wavelink.Queue()


class AddMoreView(discord.ui.View):

    def __init__(self, ctx, search):
        super().__init__()
        self.ctx = ctx
        self.search = search

    @discord.ui.button(label="Добавить еще раз", style=discord.ButtonStyle.primary)
    async def one_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:

            if not self.ctx.voice_client:
                if self.ctx.author.voice is None:
                    await self.ctx.send('Зайди в войс ченел, шизоид')
                    return
                vc: wavelink.Player = await self.ctx.author.voice.channel.connect(cls=wavelink.Player)
            else:
                vc: wavelink.Player = self.ctx.voice_client

            tracks: wavelink.Search = await wavelink.Playable.search(self.search)

            if isinstance(tracks, wavelink.Playlist):
                tracks.track_extras(ctx=self.ctx)
                added: int = await vc.queue.put_wait(tracks)

                await interaction.message.edit(content=f'Добавлено {added} треков из плейлиста {tracks.name} в очередь.', view=AddMoreView(ctx=self.ctx, search=self.search))
            else:
                track: wavelink.Playable = tracks[0]
                track.ctx = self.ctx
                await vc.queue.put_wait(track)

                await interaction.message.edit(content=f'Добавил {track} в очередь.', view=AddMoreView(ctx=self.ctx, search=self.search))

            if not vc.current:
                await vc.play(vc.queue.get())
        self.stop()


class NaviPanelView(discord.ui.View):

    foo: bool = None
    foo1: bool = None
    foo2: bool = None
    foo3: bool = None
    foo4: bool = None

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip_button(self, ctx, button: discord.ui.Button):
        self.foo = True
        self.stop()

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary)
    async def pause_button(self, ctx, button: discord.ui.Button):
        self.foo1 = True
        self.stop()

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.primary)
    async def resume_button(self, ctx, button: discord.ui.Button):
        self.foo2 = True
        self.stop()

    @discord.ui.button(label="Loop", style=discord.ButtonStyle.primary)
    async def loop_button(self, ctx, button: discord.ui.Button):
        self.foo3 = True
        self.stop()

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.primary)
    async def disconnect_button(self, ctx, button: discord.ui.Button):
        self.foo4 = True
        self.stop()


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload) -> None:
    player: wavelink.Player | None = payload.player

    if player and player.queue:
        await player.play(player.queue.get())


@bot.event
async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload) -> None:
    # Payload original is the "original" track that was added to the queue, with all custom attributes we set.

    embed = discord.Embed(
        colour=discord.Colour.magenta(),
        title=payload.original.title,
        description=payload.original.author,
        url=payload.original.uri
    )

    embed.set_author(name='Трек добавлен')
    embed.add_field(name="Длительность", value=time.strftime("%M:%S", time.gmtime(payload.original.length/1000)))
    embed.set_thumbnail(url=payload.original.artwork)

    view = NaviPanelView(timeout=3600)

    if payload.original:
        await payload.original.ctx.send('Сейчас играет:', embed=embed, view=view)

    await view.wait()

    if view.foo:
        await skip(payload.original.ctx)
    if view.foo1:
        await pause(payload.original.ctx)
    if view.foo2:
        await resume(payload.original.ctx)
    if view.foo4:
        await disconnect(payload.original.ctx)


@bot.event
async def is_owner(interaction: discord.Interaction):
    return interaction.user.id == interaction.guild.owner_id


@bot.event
async def on_ready():
    logger.info(f'User: {bot.user} (ID: {bot.user.id})')

    print(f"{bot.user} is now running!")

    await bot.tree.sync()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content:
        user_message = str(message.content)
    else:
        user_message = "image/file"
    username = str(message.author)
    channel = str(message.channel)
    guild = str(message.guild)

    print(f'{username} said {user_message} in the {channel} at the {guild}')

    if user_message[0] == '?':
        user_message = user_message[1:]
        await send_message(message, user_message, is_private=True)
    else:
        await send_message(message, user_message, is_private=False)

    await bot.process_commands(message)  # Process commands alongside on_message


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, Exception):
        await ctx.send(error)


@bot.event
async def setup_hook():
    node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
    await wavelink.Pool.connect(client=bot, nodes=[node])


@bot.hybrid_command(name="play")
@app_commands.describe(search="url (music.yandex/vk.com/youtube.com) или поисковой запрос")
async def connect(ctx: commands.Context, *, search: str):
    """Добавляет в очередь треки или плейлисты"""
    if not ctx.voice_client:
        if ctx.author.voice is None:
            await ctx.send('Зайди в войс ченел, шизоид')
            return
        vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        vc: wavelink.Player = ctx.voice_client

    # Could be a URL or Plain Search...
    # If the URL is a Spotify URL, make sure you have setup LavaSrc Plugin.
    tracks: wavelink.Search = await wavelink.Playable.search(search)
    if not tracks:
        await ctx.send("Не ищется")
        return

    view = AddMoreView(ctx=ctx, search=search)

    if isinstance(tracks, wavelink.Playlist):
        tracks.track_extras(ctx=ctx)
        added: int = await vc.queue.put_wait(tracks)
        await ctx.send(f'Добавлено {added} треков из плейлиста {tracks.name} в очередь.', view=view)

    else:
        track: wavelink.Playable = tracks[0]
        track.ctx = ctx

        await vc.queue.put_wait(track)
        await ctx.send(f'Добавил {track} в очередь.', view=view)

    if not vc.current:
        await vc.play(vc.queue.get())

    await view.wait()


@bot.hybrid_command(name="skip")
@app_commands.describe(count="skip {количество}")
async def skip(ctx, count=None):
    """Пропустить текущий трек"""

    if count is None:
        count = 1

    vc: wavelink.Player = ctx.voice_client
    new_queue = list(list(reversed(vc.queue)))[count - 1:]
    vc.queue.clear()
    if vc:
        if ctx.author.voice.channel.id == ctx.bot.voice_clients[0].channel.id:
            for track in new_queue:
                vc.queue.put(track)
            await vc.stop()
        else:
            await ctx.send('Тебя нет в воисе, шизофреник')
    else:
        await ctx.send('Меня нет в воисе, шизофреник')


async def disconnect(ctx):
    """Выйти из войс ченела"""
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()


async def pause(ctx):
    """Поставить на паузу текущий трек"""
    vc = ctx.voice_client
    if vc.paused and not vc.is_paused:
        await vc.pause()


async def resume(ctx):
    """Поставить на паузу текущий трек"""
    vc = ctx.voice_client
    if vc.paused:
        await vc.resume()


def run_discord_bot():
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
