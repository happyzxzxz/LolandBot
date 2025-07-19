from discord.ext import commands
from discord import app_commands
import wavelink
import re
import time
from bot import logger


class seek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="seek")
    @app_commands.describe(stime="Time to seek for (can type in seconds or 00:00 format)")
    async def seek(self, ctx, stime):
        """Seek current track for certain time"""
        await ctx.defer(ephemeral=True)

        vc: wavelink.Player = ctx.voice_client
        if vc:
            if ctx.author.voice:
                if vc.playing:
                    if re.match(r'^\d+(:\d+)?$', stime) is None:
                        await ctx.reply('Wrong formatting', ephemeral=True, delete_after=1)
                        return
                    if ':' in stime:
                        stime = time.strptime(stime, '%M:%S')
                        stime = str(int(stime[4])*60 + int(stime[5]))
                    await vc.seek(stime + '000')
                    await ctx.reply('All done', delete_after=1, ephemeral=True)
                    logger.info("Successfully seeked the track")
            else:
                await ctx.reply('Enter the voice channel', delete_after=1, ephemeral=True)
        else:
            await ctx.reply('I am not in the voice channel', delete_after=1, ephemeral=True)


async def setup(bot):
    await bot.add_cog(seek(bot))
