from discord.ext import commands
from discord import app_commands
from bot import logger
import json
from discord.utils import get
from bot import bot


class reaction_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="reaction_role")
    @app_commands.describe(
        message_id="Message ID",
        role="Name of the role that bot will give (without @)", emoj="Emoji (like this :nerd:)",
        deleted="1 to delete, 0 to add (default 0)")
    @commands.has_permissions(administrator=True)
    async def create_new_reaction_role(self, ctx, message_id, role, emoj, deleted="0"):
        """Add or delete reaction role"""
        try:

            await ctx.defer(ephemeral=True)

            deleted = int(deleted)
            if not (message_id.isdigit()):
                await ctx.send("Message ID should be digits only", ephemeral=True)
                return

            try:
                with open('jsons/reaction_messages.json', 'r', encoding="utf-8") as file:
                    data = json.load(file)
                    role_id = get(ctx.message.guild.roles, name=role).id
            except FileNotFoundError:
                data = []

            message_exists = False
            for item in data:
                if item['message'] == message_id:
                    message_exists = True

                    if deleted == 1:
                        if emoj in item['emoji']:
                            del item['emoji'][emoj]
                            if not item['emoji']:
                                data.remove(item)
                    else:
                        if emoj not in item['emoji']:
                            item["emoji"][emoj] = role_id
                    break

            if not message_exists and deleted != 1:
                new_message = {
                    'message': message_id,
                    'emoji': {
                        emoj: role_id
                    }
                }
                data.append(new_message)

            with open('jsons/reaction_messages.json', 'w', encoding="utf-8") as file:
                json.dump(data, file, indent=2)

            msg = await ctx.fetch_message(int(message_id))

            if deleted == 1:
                await ctx.send(f"Deleted reaction-role with role {role} and emoji {emoj}, message: '{msg.content}'",
                               ephemeral=True)

                guild = msg.guild
                member = guild.get_member(bot.application_id)

                await msg.remove_reaction(emoj, member)

                logger.info(f"Deleted reaction-role on the message: '{msg.content}' at the {msg.guild} and role {role}")
            else:
                await ctx.send(f"Added reaction-role with role {role} and emoji {emoj}, message: '{msg.content}'",
                               ephemeral=True)
                await msg.add_reaction(emoj)
                logger.info(
                    f"Added new reaction-role on the message: '{msg.content}' at the {msg.guild} and role {role}")

        except Exception as e:
            await ctx.send("Please use this command in the channel with your message", ephemeral=True)
            logger.error(e)


async def setup(bot):
    await bot.add_cog(reaction_role(bot))
