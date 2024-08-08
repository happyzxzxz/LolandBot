import typing
from discord.ext import commands
from bot import logger
import wavelink
import json
from discord import app_commands


class create_new_equalizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.equalizer_gains = ["-0.25", "-0.2", "-0.15", "-0.1", "-0.05", "0", "0.1", "0.15", "0.2", "0.25", "0.3", "0.35", "0.4", "0.45", "0.5", "0.55", "0.6", "0.65", "0.7", "0.75", "0.8", "0.85", "0.9", "0.95", "1.0"]

    @commands.hybrid_command(name="create_new_equalizer")
    @app_commands.describe(
        name="Name of your equalizer preset", delete="Delete equalizer by the given name (1 for yes)")
    async def create_new_equalizer(self, ctx, name, delete: typing.Literal[0, 1] = 0, hz25="0", hz40="0",
                                   hz63="0", hz100="0", hz160="0", hz250="0", hz400="0", hz630="0", hz1k="0",
                                   hz1_6k="0", hz2_5k="0", hz4k="0", hz6_3k="0", hz10k="0", hz16k="0"):
        await ctx.defer(ephemeral=True)

        if delete:
            with open("jsons/equalizer_bands.json", "r") as file:
                equalizers = json.loads(file.read())

            if f'{name}_{ctx.message.guild.id}' in equalizers:
                del equalizers[f'{name}_{ctx.message.guild.id}']

                with open("jsons/equalizer_bands.json", "w") as file:
                    file.write(json.dumps(equalizers, indent=3))

                await ctx.send(f"Deleted {name} equalizer", ephemeral=True)

            else:
                await ctx.send("There are no such equalizer")
                return
        else:

            frequencies = [hz25, hz40, hz63, hz100, hz160, hz250, hz400, hz630, hz1k, hz1_6k, hz2_5k, hz4k, hz6_3k, hz10k, hz16k]
            if not all(freq.replace('.', '').replace('-', '').isdigit() for freq in frequencies):
                await ctx.send("Wrong arguments")
                return

            with open("jsons/equalizer_bands.json", "r") as file:
                equalizers = json.loads(file.read())

            if f'{name}_{ctx.message.guild.id}' not in equalizers:
                equalizers.update({f'{name}_{ctx.message.guild.id}': [
                    {"band": 0, "gain": float(hz25)},
                    {"band": 1, "gain": float(hz40)},
                    {"band": 2, "gain": float(hz63)},
                    {"band": 3, "gain": float(hz100)},
                    {"band": 4, "gain": float(hz160)},
                    {"band": 5, "gain": float(hz250)},
                    {"band": 6, "gain": float(hz400)},
                    {"band": 7, "gain": float(hz630)},
                    {"band": 8, "gain": float(hz1k)},
                    {"band": 9, "gain": float(hz1_6k)},
                    {"band": 10, "gain": float(hz2_5k)},
                    {"band": 11, "gain": float(hz4k)},
                    {"band": 12, "gain": float(hz6_3k)},
                    {"band": 13, "gain": float(hz10k)},
                    {"band": 14, "gain": float(hz16k)}
                ]})
            else:
                await ctx.send("This equalizer name has already been taken")
                return

            with open("jsons/equalizer_bands.json", "w") as file:
                file.write(json.dumps(equalizers, indent=3))

            await ctx.send(f"Added {name} equalizer", ephemeral=True)

    # Yea I know, but it seems like the only way to make choises with ability to enter custom values

    @create_new_equalizer.autocomplete("hz25")
    @create_new_equalizer.autocomplete("hz40")
    @create_new_equalizer.autocomplete("hz63")
    @create_new_equalizer.autocomplete("hz100")
    @create_new_equalizer.autocomplete("hz160")
    @create_new_equalizer.autocomplete("hz250")
    @create_new_equalizer.autocomplete("hz400")
    @create_new_equalizer.autocomplete("hz630")
    @create_new_equalizer.autocomplete("hz1k")
    @create_new_equalizer.autocomplete("hz1_6k")
    @create_new_equalizer.autocomplete("hz2_5k")
    @create_new_equalizer.autocomplete("hz4k")
    @create_new_equalizer.autocomplete("hz6_3k")
    @create_new_equalizer.autocomplete("hz10k")
    @create_new_equalizer.autocomplete("hz16k")
    async def hz_autocompletion(self, interaction, current):
        data = []

        equalizer_gains = self.equalizer_gains

        for gain in equalizer_gains:
            data.append(app_commands.Choice(name=gain, value=gain))
        return data


async def setup(bot):
    await bot.add_cog(create_new_equalizer(bot))