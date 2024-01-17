from typing import Type

from discord import utils
from discord.ext import tasks

from Cozyfications import database, twitch
from Cozyfications.bot import core


class Tasks(core.Cog):
    """Background tasks for the bot."""

    def __init__(self, bot: core.Cozyfications) -> None:
        """Initializes the Tasks cog."""
        self.bot: core.Cozyfications = bot

        self.update_live_channels.start()

    def cog_unload(self) -> None:
        """Cancels all background tasks."""
        self.update_live_channels.cancel()

    @tasks.loop(minutes=5)
    async def update_live_channels(self):
        """Updates the embeds of live Twitch channels in subscribed guilds every 5 minutes."""
        live_channels: list[Type[database.TwitchChannel]] | None = database.get_live_twitch_channels()
        if live_channels is None:
            return
        for twitch_channel in live_channels:
            subscribed_guilds = database.get_subscribed_guilds(broadcaster_id=twitch_channel.id)
            if subscribed_guilds is None:
                continue
            for guild in subscribed_guilds:
                channel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id, default=None)
                if channel is None:
                    continue
                message = await channel.fetch_message(guild.message_id)
                if message is None:
                    continue
                live_stream: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
                    broadcaster_id=twitch_channel.id
                )
                if not live_stream.live:
                    continue
                live_embed: core.LiveStreamEmbed = core.LiveStreamEmbed(bot=self.bot, stream=live_stream)
                # TODO: Support multiple subscriptions per guild.
                await message.edit(embed=live_embed)

    @update_live_channels.before_loop
    async def before_update_live_channels(self):
        """Waits for the bot to be ready before starting the update_live_channels task."""
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tasks(bot))
