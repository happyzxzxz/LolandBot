from discord.ext import commands
from discord import app_commands
from bot import logger
import settings
import discord
from saucenao_api import AIOSauceNao, VideoSauce, BasicSauce, BookSauce


class sauce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="sauce")
    @app_commands.describe(url="Image url")
    async def sauce(self, ctx: commands.Context, url):
        """Find a source of an image/anime/manga/book"""
        if ctx.channel.is_nsfw():
            await ctx.defer()

            logger.info(f'Starting Saucenao request.... AUTHOR - {ctx.author}')

            try:
                async with AIOSauceNao(settings.SAUCENAO_API_KEY) as aio:
                    result = await aio.from_url(url)

                result = result[0]
                if result:
                    logger.info(f'Saucenao response: {result}. AUTHOR - {ctx.author}')
                    embed = discord.Embed()
                    if type(result) == BasicSauce:
                        embed.set_author(name="Author: " + result.author)
                        embed.add_field(name="Links: ", value='\n'.join(result.urls))
                        embed.set_footer(text="Similarity: " + str(result.similarity) + '%')
                    if type(result) == VideoSauce:
                        embed.set_author(name="Anime: " + result.title + ". Year: " + result.year)
                        embed.add_field(name="Exact moment",
                                        value="\nEpisode: " + result.part + "\nTime: " + result.est_time)
                        embed.set_footer(text="Similarity: " + str(result.similarity) + '%')
                    if type(result) == BookSauce:
                        embed.set_author(name="Manga: " + result.title)
                        embed.add_field(name="Chapter: ", value=result.part)
                        embed.set_footer(text="Similarity: " + str(result.similarity) + '%')

                    embed.set_image(url=url)
                    embed.set_thumbnail(url=result.thumbnail)
                    await ctx.reply(embed=embed)
                    logger.info(f'Finished Saucenao request. AUTHOR - {ctx.author}')

            except Exception as e:
                await ctx.reply("Can't find or url is invalid")
                logger.info(f"Finished Saucenao request, can't find. AUTHOR - {ctx.author}")
        else:
            await ctx.reply("This is not a NSFW channel", ephemeral=True)


async def setup(bot):
    await bot.add_cog(sauce(bot))
