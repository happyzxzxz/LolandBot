from discord.ext import commands
from discord import app_commands
import wavelink
from bot import logger


class skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="skip")
    @app_commands.describe(count="How many to skip")
    async def skip(self, ctx, count=1):
        """Skip tracks in the queue"""

        await ctx.defer(ephemeral=True)

        vc: wavelink.Player = ctx.voice_client
        if vc:
            if ctx.author.voice:
                if len(vc.queue) == 0 and vc.playing:
                    await vc.skip()
                    await ctx.reply('Skipped', delete_after=1, ephemeral=True)
                else:
                    for _ in range(count - 1):
                        vc.queue.delete(0)
                    await vc.skip()
                    await ctx.reply('Skipped', delete_after=1, ephemeral=True)
                    logger.info(f'Skipped {count} tracks')
            else:
                await ctx.reply('Connect to the voice channel', delete_after=1, ephemeral=True)
        else:
            await ctx.reply('I am not in the voice channel', delete_after=1, ephemeral=True)


async def setup(bot):
    await bot.add_cog(skip(bot))
