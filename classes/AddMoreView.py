import discord
from .Player import Player
import wavelink
import settings


class AddMoreView(discord.ui.View):
    """Discord View for 'Add More' Button"""

    def __init__(self, ctx, search, vk_search_results=None, vk_playlist_title=None):
        super().__init__(timeout=10800)

        if vk_search_results is None:
            vk_search_results = []

        self.ctx = ctx
        self.search = search
        self.vk_search_results = vk_search_results
        self.vk_playlist_title = vk_playlist_title

    @discord.ui.button(label="Add again", style=discord.ButtonStyle.primary)
    async def one_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:

            if not self.ctx.voice_client:
                if self.ctx.author.voice:
                    vc: wavelink.Player = await self.ctx.author.voice.channel.connect(cls=Player)
                else:
                    await self.ctx.send('Connect to the voice channel', ephemeral=True)
                    return
            else:
                vc: wavelink.Player = self.ctx.voice_client

            if "vk.com" not in self.search:
                tracks: wavelink.Search = await wavelink.Playable.search(self.search)

                if isinstance(tracks, wavelink.Playlist):
                    tracks.track_extras(ctx=self.ctx)
                    added: int = await vc.queue.put_wait(tracks)

                    await interaction.message.edit(content=f'Added {added} tracks from the {tracks.name} playlist into the queue.', view=AddMoreView(ctx=self.ctx, search=self.search))
                else:
                    track: wavelink.Playable = tracks[0]
                    track.ctx = self.ctx
                    await vc.queue.put_wait(track)

                    await interaction.message.edit(content=f'Added {track} into the queue.', view=AddMoreView(ctx=self.ctx, search=self.search))
            else:

                if len(self.vk_search_results) > 1:
                    for result_track in self.vk_search_results:
                        await vc.queue.put_wait(result_track)
                    await interaction.message.edit(content=f'Added {len(self.vk_search_results)} tracks from the {self.vk_playlist_title} playlist into the queue.', view=AddMoreView(ctx=self.ctx, search=self.search, vk_search_results=self.vk_search_results, vk_playlist_title=self.vk_playlist_title))
                else:
                    await vc.queue.put_wait(self.vk_search_results[0])
                    await interaction.message.edit(content=f"Added {self.vk_search_results[0].track_title} into the queue", view=AddMoreView(ctx=self.ctx, search=self.search, vk_search_results=self.vk_search_results))
            if not vc.current:
                await vc.play(vc.queue.get())
        self.stop()
