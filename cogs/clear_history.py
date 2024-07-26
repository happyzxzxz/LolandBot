from discord.ext import commands
from bot import logger
import os


class clear_history(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear_history")
    async def clear_history(self, ctx: commands.Context):
        """Deletes your chatgpt history"""
        if ('chatgptlog' + str(ctx.author.id) + '.json') in os.listdir('chatgptlogs'):
            os.remove('chatgptlogs/chatgptlog' + str(ctx.author.id) + '.json')
            await ctx.reply('Deleted')
            logger.info(f'{ctx.author} successfully deleted his openai chatgpt history')
        else:
            await ctx.reply('There are no history')


async def setup(bot):
    await bot.add_cog(clear_history(bot))
