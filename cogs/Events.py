from discord.ext import commands
from bot import check_voice_channels, logger
from classes.NaviPanelView import NaviPanelView
import functions
import discord
import json
from discord.utils import get
import wavelink
import settings
import time
from classes import Player


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'User: {self.bot.user} (ID: {self.bot.user.id}) is now running!')

        check_voice_channels.start()

        await self.bot.tree.sync()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, Exception):
            logger.error(error)
            await ctx.send(error)

    @commands.Cog.listener()
    async def is_owner(self, interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        try:
            with open("jsons/reaction_messages.json", "r") as file:
                data = json.load(file)

                for item in data:
                    if message.id == int(item["message"]):
                        for emoj in item["emoji"]:
                            if str(payload.emoji) == emoj:
                                guild = message.guild
                                member = guild.get_member(payload.user_id)
                                role = get(guild.roles, id=item["emoji"][emoj])

                                await member.add_roles(role)
                                logger.info(
                                    f"{member.name} reacted on the message {message.content} and earned role {role}")

        except FileNotFoundError:
            return

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        # Payload original is the "original" track that was added to the queue, with all custom attributes we set.

        if not payload.player.reading:

            embed = discord.Embed(
                colour=discord.Colour.from_rgb(240, 200, 89),
                title=payload.original.title,
                description=payload.original.author,
                url=payload.original.uri
            )

            if "vk.com" in payload.original.uri:
                embed.colour = discord.Colour.dark_blue()
                minutes, seconds = divmod(payload.original.length, 60)
            else:
                minutes, seconds = divmod(payload.original.length / 1000, 60)

            embed.set_thumbnail(url=payload.original.artwork)

            embed.set_author(name='Now playing')
            embed.add_field(name="Length", value=f"{int(minutes):02d}:{int(seconds):02d}")

            if payload.player.queue.mode == wavelink.QueueMode.normal:
                view = NaviPanelView(ctx=payload.original.ctx, embed=embed, loop=False)
            else:
                view = NaviPanelView(ctx=payload.original.ctx, embed=embed, loop=True)

            if payload.original:
                if payload.player.player_message:
                    await payload.player.player_message.edit(embed=embed, view=view)
                else:
                    player_message = await payload.original.ctx.channel.send(embed=embed, view=view)
                    payload.player.player_message = player_message

            await view.wait()

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player = payload.player

        # For some reason, bot quits channel before fully reading flowerytts response

        if player is not None:

            if player.queue:
                if player.reading and not 'Text to Speech' == player.queue[0].title:
                    player.reading = False
                    time.sleep(1)

                await player.play(player.queue.get())
            else:
                if player.reading:
                    player.reading = False
                    time.sleep(1)

                player.cleanup()
                await player.disconnect()
                logger.info(f'Disconnected from the voice channel at the {player.guild}')

async def setup(bot):
    await bot.add_cog(Events(bot))
