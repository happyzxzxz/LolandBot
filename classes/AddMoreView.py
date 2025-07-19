import discord
from .Player import Player
import wavelink
import settings


class AddMoreView(discord.ui.View):
    """Discord View for 'Add More' Button"""

    def __init__(self, ctx, search):
        super().__init__(timeout=10800)

        self.ctx = ctx
        self.search = search

    @discord.ui.button(label="One more time", style=discord.ButtonStyle.primary)
    async def one_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if not self.ctx.voice_client:
            if self.ctx.author.voice:
                vc: wavelink.Player = await self.ctx.author.voice.channel.connect(cls=Player)
            else:
                await self.ctx.send('Enter the voice channel', ephemeral=True)
                return
        else:
            vc: wavelink.Player = self.ctx.voice_client

        tracks: wavelink.Search = await wavelink.Playable.search(self.search)

        if isinstance(tracks, wavelink.Playlist):
            tracks.track_extras(ctx=self.ctx)
            added: int = await vc.queue.put_wait(tracks)

            await interaction.message.edit(content=f'Added {added} tracks from the playlist {tracks.name} into the queue.', view=AddMoreView(ctx=self.ctx, search=self.search))
        else:
            track: wavelink.Playable = tracks[0]
            track.ctx = self.ctx
            await vc.queue.put_wait(track)

            await interaction.message.edit(content=f'Added {track} to the queue.', view=AddMoreView(ctx=self.ctx, search=self.search))
                
        if not vc.current:
            await vc.play(vc.queue.get())
        self.stop()
