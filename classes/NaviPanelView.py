import discord
import wavelink
import emoji
from bot import logger


class NaviPanelView(discord.ui.View):
    """Discord View for Message that Represents Interactive Player"""

    def __init__(self, ctx, embed, loop=None):
        super().__init__(timeout=10800)
        self.ctx = ctx
        self.embed = embed
        self.loop = loop
        self.update_button()

    def update_button(self):
        self.loop_emoji_value = ':repeat_single_button:' if self.loop else ':repeat_button:'
        self.loop_button.emoji = emoji.emojize(self.loop_emoji_value)

        if self.ctx.voice_client:
            self.paused_emoji_value = ':play_button:' if self.ctx.voice_client.paused else ':pause_button:'
            self.pause_resume_button.emoji = emoji.emojize(self.paused_emoji_value)

    def check_loop(self):
        if self.ctx.voice_client.queue.mode == wavelink.QueueMode.normal:
            return False
        return True

    @discord.ui.button(emoji=emoji.emojize(':next_track_button:'), style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.author.voice:
            await self.ctx.send('Enter the voice channel', ephemeral=True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            return
        else:
            vc: wavelink.Player = self.ctx.voice_client
        if self.check_loop():
            vc.queue.delete(-1)
            vc.queue.mode = wavelink.QueueMode.normal
        await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
        await vc.skip()
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.author.voice:
            await self.ctx.send('Enter the voice channel', ephemeral=True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            return
        else:
            vc: wavelink.Player = self.ctx.voice_client
        if not vc.paused and vc.current:
            await vc.pause(True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
        else:
            await vc.pause(False)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':shuffle_tracks_button:'), style=discord.ButtonStyle.secondary)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.author.voice:
            await self.ctx.send('Enter the voice channel', ephemeral=True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            return
        else:
            vc: wavelink.Player = self.ctx.voice_client
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            if vc:
                vc.queue.shuffle()
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.secondary)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.author.voice:
            await self.ctx.send('Enter the voice channel', ephemeral=True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            return
        else:
            vc: wavelink.Player = self.ctx.voice_client
            if vc:
                if vc.queue.mode is not wavelink.QueueMode.normal:
                    vc.queue.delete(-1)
                    vc.queue.mode = wavelink.QueueMode.normal
                    await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=False))
                else:
                    await vc.queue.put_wait(vc.current)
                    vc.queue.mode = wavelink.QueueMode.loop
                    await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=True))
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':page_facing_up:'), style=discord.ButtonStyle.secondary)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.author.voice:
            await self.ctx.send('Enter the voice channel', ephemeral=True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            return
        else:
            vc: wavelink.Player = self.ctx.voice_client
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            if vc.queue:
                queue_list = [f'[{que.title}]({que.uri}) - {que.author}' for que in vc.queue[:20]]

                embed = discord.Embed(
                    title="First 20 tracks in the queue:",
                    description='Now playing: ' + f'[{vc.current.title}]({vc.current.uri}) - {vc.current.author}' + '\n' + '\n'.join(queue_list)
                )
                await self.ctx.send(embed=embed, ephemeral=True)
            else:

                embed = discord.Embed(
                    title="Now playing:",
                    description=f'[{vc.current.title}]({vc.current.uri}) - {vc.current.author}'
                )
                await self.ctx.send(embed=embed, ephemeral=True)
        self.stop()

    @discord.ui.button(emoji=emoji.emojize(':cross_mark:'), style=discord.ButtonStyle.secondary)
    async def disconnect_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.author.voice:
            await self.ctx.send('Enter the voice channel', ephemeral=True)
            await interaction.message.edit(embed=self.embed, view=NaviPanelView(ctx=self.ctx, embed=self.embed, loop=self.check_loop()))
            return
        else:
            vc: wavelink.Player = self.ctx.voice_client
        if vc:
            vc.cleanup()
            await vc.disconnect()
            logger.info(f'Disconnected from the voice channel at the {vc.guild}')
        else:
            await self.ctx.send('I am not in the voice channel', ephemeral=True)
        self.stop()
