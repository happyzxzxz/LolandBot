import wavelink


class Player(wavelink.Player):
    """Custom Player Class"""

    player_message = 0
    reading = False

    async def _destroy(self):
        # Call the original _destroy method from wavelink.Player
        await super()._destroy()

        # Destroy player message as well
        if hasattr(self, 'player_message') and self.player_message:
            await self.player_message.delete()