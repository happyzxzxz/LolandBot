import discord
import responses
from discord.ext import commands
from discord import app_commands
import settings


logger = settings.logging.getLogger("bot")


class CustomView(discord.ui.View):

    @discord.ui.button(label="Добавить еще раз", style=discord.ButtonStyle.primary)
    async def one_more(self, ctx, button: discord.ui.Button):
        # Сделать так чтобы функция play исполнялась тут еще раз (переделать run_discord_bot под класс?)
        await ctx.response.send_message('lol')


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
    async def is_owner(interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id

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
    @app_commands.describe(link="Enter url (music.yandex/vk.com/youtube.com)")
    async def play(ctx, link):
        """Plays music or playlist by the given link"""

        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title="Название трека (украсть)",
            description="Добавить автора трека (украсть)",
            url=link
        )

        view = CustomView()

        embed.set_author(name="Трек добавлен")
        embed.add_field(name="Длительность", value="Добавить длительность (украсть)")
        #embed.set_thumbnail(url="Украсть если есть, если нет вставить затычку")                   !!!!!!!!!!!!!

        await ctx.send(embed=embed, view=view)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)