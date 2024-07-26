import discord
from discord.ext import commands
from discord.ext import tasks
import settings
import wavelink
import openai
import asyncio


logger = settings.logging.getLogger("discord")
openai.api_key = settings.OPENAI_API_SECRET


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook():
    for command, status in settings.ENABLED_COMMANDS.items():
        if status:
            await bot.load_extension(f'cogs.{command}')

    node: wavelink.Node = wavelink.Node(uri=settings.LAVALINK_SERVER_URL, password=settings.LAVALINK_PASSWORD)
    await wavelink.Pool.connect(client=bot, nodes=[node])


@tasks.loop(seconds=2)
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
