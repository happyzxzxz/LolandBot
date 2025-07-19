from discord.ext import commands
from discord import app_commands
import discord
import aiohttp
from classes.Player import Player
import wavelink
from bot import logger


class text_to_speech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ctx_menu = app_commands.ContextMenu(
            name='Read aloud',
            callback=self.text_to_speech,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def text_to_speech(self, interaction: discord.Interaction, message: discord.Message):

        await interaction.response.defer(ephemeral=True)

        if not interaction.guild.voice_client:
            if interaction.user.voice:
                vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=Player)
            else:
                await interaction.followup.send('Enter the voice channel', ephemeral=True)
                return
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        async with aiohttp.ClientSession() as session:
            logger.info('Starting flowerytts api request.....')

            message_content = message.content
            message_content_list = [message_content[x:x+850] for x in range(0, len(message_content), 850)]

            for part in message_content_list:
                async with session.get('https://api.flowery.pw/v1/tts', params={"voice": "Maxim",
                                                                                    "text": part}) as response:
                    data = str(response.url)
                    tracks = await wavelink.Pool.fetch_tracks(data)
                    vc.reading = True

                    await vc.queue.put_wait(tracks[0])

            logger.info('Successfully ended flowerytts api request')

            await interaction.followup.send('Reading...', ephemeral=True)

        if not vc.current:
            await vc.play(vc.queue.get())
            logger.info(f'Connected to the voice channel at the {vc.guild.name}. AUTHOR - {message.author}')

async def setup(bot):
    await bot.add_cog(text_to_speech(bot))
