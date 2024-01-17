from twitchAPI import twitch

from Cozyfications import secrets


class Twitch(twitch.Twitch):
    """Async context manager for the Twitch API."""

    def __init__(self):
        """Initializes the Twitch API."""
        super().__init__(app_id=secrets.Twitch.ID, app_secret=secrets.Twitch.SECRET)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
