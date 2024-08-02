from discord.ext import commands
from discord import app_commands
from bot import logger
from pygelbooru import Gelbooru
import settings
import discord


class gelbooru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="gelbooru")
    @app_commands.describe(q="Search", count="Count of posts (max 4)")
    async def gelbooru(self, ctx: commands.Context, q, count=1):
        """Gelbooru.com searching with tags"""
        if ctx.channel.is_nsfw():

            if type(count) == int and count <= 4:
                pass
            else:
                await ctx.reply('Max count is 4', ephemeral=True)
                return

            await ctx.defer()

            logger.info(f'Starting Gelbooru request.... AUTHOR - {ctx.author}')

            gelbooru = Gelbooru(settings.GELBOORU_API_SECRET, settings.GELBOORU_USER_ID)
            q = q.split()

            results = []
            for i in range(count):
                result = await gelbooru.random_post(tags=q, exclude_tags=['loli', 'guro', 'toddler', 'shota'])
                if result:
                    if result.filename not in [i.filename for i in results]:
                        results.append(result)

            if results:
                for res in results:

                    temp_embed = discord.Embed()
                    embed = temp_embed.set_image(url=res)

                    if '.mp4' in res.filename:
                        await ctx.reply(res)
                    else:
                        await ctx.reply(' '.join(q), embed=embed)

                    logger.info(f'Finished Gelbooru request. AUTHOR - {ctx.author}')
            else:
                await ctx.reply("Censored", ephemeral=True)
                logger.info(f'Censored Gelbooru request. AUTHOR - {ctx.author}')

        else:
            await ctx.reply("This in not a NSFW channel", ephemeral=True)

    @gelbooru.autocomplete("q")
    async def tags_autocompletion(self, interaction, current):
        gelbooru = Gelbooru(settings.GELBOORU_API_SECRET, settings.GELBOORU_USER_ID)
        data = []

        current_tags = current.split()
        last_tag = current_tags[-1] if current_tags else ""

        gelbooru_tags = await gelbooru.tag_list(name_pattern=f'%{last_tag}%', limit=10)

        if gelbooru_tags and last_tag:
            for tag_choice in gelbooru_tags:
                if last_tag.lower() in tag_choice.name.lower():

                    full_tag_string = ' '.join(current_tags[:-1] + [tag_choice.name])
                    data.append(app_commands.Choice(name=full_tag_string, value=full_tag_string))

        return data


async def setup(bot):
    await bot.add_cog(gelbooru(bot))
