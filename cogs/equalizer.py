from discord.ext import commands
from bot import logger
import wavelink
import json
from discord import app_commands


class equalizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="equalizer")
    @app_commands.describe(name="Name of your equalizer preset")
    async def equalizer(self, ctx, name):

        await ctx.defer(ephemeral=True)

        if not ctx.voice_client:
            await ctx.reply('I am not in the voice channel', ephemeral=True)
            return
        else:
            vc = ctx.voice_client

        filters: wavelink.Filters = vc.filters

        with open("jsons/equalizer_bands.json", "r") as file:
            equalizers = json.loads(file.read())

        if not(f'{name}_{ctx.message.guild.id}' in equalizers or f'{name}_nodelete' in equalizers):
            await ctx.send("Wrong arguments")
            return

        if f'{name}_nodelete' in equalizers:
            bands = equalizers[f'{name}_nodelete']
        else:
            bands = equalizers[f'{name}_{ctx.message.guild.id}']

        filters.equalizer.set(bands=bands)
        await vc.set_filters(filters)

        await ctx.reply(f"Current equalizer: {name}", ephemeral=True)

    @equalizer.autocomplete("name")
    async def name_autocompletion(self, interaction, current):
        data = []

        with open("jsons/equalizer_bands.json", "r") as file:
            equalizers = json.loads(file.read())
            for key in equalizers.keys():
                name, guild_id = key.split('_')
                if guild_id.isdigit():
                    if interaction.guild_id == int(guild_id):
                        data.append(app_commands.Choice(name=name, value=name))
                else:
                    data.append(app_commands.Choice(name=name, value=name))

        return data


async def setup(bot):
    await bot.add_cog(equalizer(bot))