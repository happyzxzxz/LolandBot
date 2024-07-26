from discord.ext import commands
from discord import app_commands
import os
import json
from bot import logger
import settings
import aiohttp
import functions
import discord


class chate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="chate")
    @app_commands.describe(prompt="Your prompt")
    async def chate(self, ctx: commands.Context, prompt):
        """Ask anything from chatgpt (Only you can see)"""
        await ctx.defer(ephemeral=True)
        logger.info(f'Starting openai chatgpt request.... AUTHOR - {ctx.author}')

        result = str(prompt)
        author_log = 'chatgptlog' + str(ctx.author.id) + '.json'

        if author_log not in os.listdir('chatgptlogs'):
            with open('chatgptlogs/' + author_log, 'w', encoding='UTF-8') as file:
                json.dump(
                    [
                        {"role": "system",
                         "content": settings.decensor_prompt}
                    ], file
                )

        with open('chatgptlogs/' + author_log, 'r', encoding='UTF-8') as messages_file:
            messages = json.load(messages_file)

        messages.append({'role': "user", 'content': result})

        if len(messages) > 8:
            messages = messages[-8:]
            messages[0] = {"role": "system", "content": settings.decensor_prompt}

        async with aiohttp.ClientSession() as session:
            chatgpt = await functions.get_chat_response(session, result, messages)

        logger.info(f'Chatgpt response: {chatgpt["choices"][0]["message"]}. AUTHOR - {ctx.author}')

        reply = chatgpt["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})

        with open('chatgptlogs/' + author_log, 'w', encoding='UTF-8') as messages_file:
            json.dump(messages, messages_file, ensure_ascii=False)

        await ctx.reply(embed=discord.Embed(title=f'{result[:255]}', description=reply), ephemeral=True)
        logger.info(f'Finished Openai chatgpt request. AUTHOR - {ctx.author}')


async def setup(bot):
    await bot.add_cog(chate(bot))
