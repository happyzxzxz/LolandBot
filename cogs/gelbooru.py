from discord.ext import commands
from discord import app_commands
from bot import logger
from python_gelbooru import AsyncGelbooru
import settings
import discord
from contextlib import suppress


class gelbooru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="gelbooru")
    @app_commands.describe(q="Tags", count="Number of posts (max 4)")
    async def gelbooru(self, ctx: commands.Context, q, count=1):
        """Search on Gelbooru.com with tags"""
        if ctx.channel.is_nsfw():

            if type(count) == int and count <= 4:
                pass
            else:
                await ctx.reply('Max 4', ephemeral=True)
                return

            await ctx.defer()

            logger.info(f'Starting Gelbooru request.... AUTHOR - {ctx.author}')

            gelbooru = AsyncGelbooru(api_key=settings.GELBOORU_API_SECRET, user_id=settings.GELBOORU_USER_ID)
            q = q.split()

            for i in range(count):
                result = await gelbooru.search_posts(tags=q, exclude_tags=settings.excluded_gelbooru_tags,
                                                     limit=count, random=True)

            if result:
                for res in result:

                    temp_embed = discord.Embed()
                    embed = temp_embed.set_image(url=res.file_url)

                    if '.mp4' in res.file_name:
                        await ctx.reply(res.file_url)
                    else:
                        await ctx.reply(' '.join(q), embed=embed)

                    logger.info(f'Finished Gelbooru request. AUTHOR - {ctx.author}')
            else:
                await ctx.reply("Censored or not found", ephemeral=True)
                logger.info(f'Censored Gelbooru request. AUTHOR - {ctx.author}')

        else:
            await ctx.reply("This channel is not NSFW", ephemeral=True)

    @gelbooru.autocomplete("q")
    async def tags_autocompletion(self, interaction, current):
        # Keep in mind that if bot doesn't respond in 3 sec then interaction will delete itself, there is no way to fix it
        gelbooru = AsyncGelbooru(api_key=settings.GELBOORU_API_SECRET, user_id=settings.GELBOORU_USER_ID)
        data = []

        current_tags = current.split()
        last_tag = current_tags[-1] if current_tags else ""

        with suppress(KeyError):
            gelbooru_tags = await gelbooru.search_tags(name_pattern=f'%{last_tag}%', limit=10)

            if gelbooru_tags and last_tag:
                for tag_choice in gelbooru_tags:
                    if last_tag.lower() in tag_choice.name.lower():

                        full_tag_string = ' '.join(current_tags[:-1] + [tag_choice.name])
                        data.append(app_commands.Choice(name=full_tag_string, value=full_tag_string))

        return data


async def setup(bot):
    await bot.add_cog(gelbooru(bot))
