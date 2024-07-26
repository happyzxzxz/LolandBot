from discord.ext import commands
from discord import app_commands
from bot import logger
import aiohttp
import functions
import discord


class image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="image")
    @app_commands.describe(
        prompt="Your prompt",
        size="Image size (only 256x526, 512x512, 1024x1024, default is 256x256, for dall-e-3 only 1024x1024)",
        model="Choose model. 2 for DALL-E-2, 3 for DALL-E-3. Default 2"
    )
    async def image(self, ctx: commands.Context, prompt, size="256x256", model="dall-e-2"):
        """Use openai diffusion models"""
        try:
            await ctx.defer()
            logger.info(f'Starting openai DALL-E-2/3 request.... AUTHOR - {ctx.author}')

            result = str(prompt)

            if model == "3":
                size = "1024x1024"
                model = "dall-e-3"
            else:
                model = "dall-e-2"

            if size not in ["256x526", "512x512", "1024x1024"]:
                size = "256x256"

            async with aiohttp.ClientSession() as session:
                chatgpt = await functions.get_image_response(session, result, size, model)

            image_url = chatgpt['data'][0]['url']

            logger.info(f'DALL-E-2/3 response: {image_url}. AUTHOR - {ctx.author}')

            embed = discord.Embed()
            embed.set_image(url=image_url)

            await ctx.reply(result, embed=embed)
            logger.info(f'Finished Openai DALL-E-2/3 request. AUTHOR - {ctx.author}')
        except KeyError:
            embed = discord.Embed()
            embed.set_image(
                url="https://static.wikia.nocookie.net/lobotomycorp/images/c/cb/CENSOREDPortrait.png/revision/latest?cb=20171119115551")

            await ctx.reply("Do not try this.", embed=embed)
            logger.info(f'Censored Openai DALL-E-2/3 request. AUTHOR - {ctx.author}. Response: {chatgpt}')


async def setup(bot):
    await bot.add_cog(image(bot))
