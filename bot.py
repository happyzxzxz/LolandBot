import discord
import responses
from discord.ext import commands
import settings


logger = settings.logging.getLogger("bot")


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():

    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def is_owner(ctx):
        return ctx.author.id == ctx.guild.owner_id

    # @bot.event
    # async def setup_hook():

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

    @bot.hybrid_command(name="play")
    async def play(ctx, name):
        """Plays music or playlist by the given link"""
        response = "иди нахуй " + name
        await ctx.send(response)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
