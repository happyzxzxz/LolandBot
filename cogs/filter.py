import typing
from discord.ext import commands
from bot import logger
import wavelink
import json
from discord import app_commands


class filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="filter")
    @app_commands.describe(
        reset="Reset settings", pitch="Default 1", speed="Default 1", rate="Default 1", rotation_hz="Default 0")
    async def filter(self, ctx: commands.Context,
                     reset: typing.Literal["On", "0ff"] = "Off",
                     bassboosted: typing.Literal["On", "0ff"] = None,
                     pitch: typing.Optional[typing.Literal["0.01", "0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2", "3", "4", "5", "10", "20", "30", "40", "50"]] = None,
                     speed: typing.Optional[typing.Literal["0.1", "0.25", "0.5", "0.6", "0.7", "0.8", "0.9", "1", "1.5", "2", "3", "5", "10", "20", "50"]] = None,
                     rate: typing.Optional[typing.Literal["0.1", "0.25", "0.5", "0.6", "0.7", "0.8", "0.9", "1", "1.5", "2", "3", "5", "10", "20", "50"]] = None,
                     rotation_hz: typing.Optional[typing.Literal["0", "0.01", "0.05", "0.1", "0.2", "0.3", "0.4", "0.6", "0.8", "1", "2", "5", "10", "20", "50"]] = None,
                     tremolo_frequency: typing.Optional[typing.Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]] = None,
                     tremolo_depth: typing.Optional[typing.Literal["0", "0.01", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"]] = None,
                     vibrato_frequency: typing.Optional[typing.Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]] = None,
                     vibrato_depth: typing.Optional[typing.Literal["0", "0.01", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"]] = None,
                     ):
        """Set up filter for the current player"""

        await ctx.defer(ephemeral=True)
        bands = None

        for attr in ["pitch", "speed", "rate", "rotation_hz", "tremolo_frequency", "tremolo_depth", "vibrato_frequency", "vibrato_depth"]:
            value = locals().get(attr)
            if value:
                locals()[attr] = float(value)

        if not ctx.voice_client:
            await ctx.reply('I am not in the voice channel', ephemeral=True)
            return
        else:
            vc = ctx.voice_client

        filters: wavelink.Filters = vc.filters

        if reset != "On":

            def set_filter_params(filter_func, **kwargs):
                params = {key: value for key, value in kwargs.items() if value is not None}
                if params:
                    filter_func.set(**params)

            set_filter_params(filters.timescale, pitch=pitch, speed=speed, rate=rate)
            set_filter_params(filters.tremolo, tremolo_frequency=tremolo_frequency, tremolo_depth=tremolo_depth)
            set_filter_params(filters.vibrato, vibrato_frequency=vibrato_frequency, vibrato_depth=vibrato_depth)

            if rotation_hz:
                filters.rotation.set(rotation_hz=rotation_hz)

            with open("jsons/equalizer_bands.json", "r") as file:
                data = json.load(file)

                if bassboosted in ["On", "Off"]:
                    if bassboosted == "On":
                        bands = data["bassboosted_nodelete"]
                    else:
                        bands = data["default_nodelete"]

                    filters.equalizer.set(bands=bands)
        else:
            filters.reset()

        await vc.set_filters(filters)
        logger.info(f"Set new filters for the player {vc.channel} at the guild {ctx.guild}")
        await ctx.send("Filtered", ephemeral=True)


async def setup(bot):
    await bot.add_cog(filter(bot))
