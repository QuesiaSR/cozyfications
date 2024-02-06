from typing import Type, List

import discord
from discord.ext import tasks

from Cozyfications import database, twitch
from Cozyfications.bot import core


class Tasks(core.Cog):
    """Background tasks for the bot."""

    def __init__(self, bot: core.Cozyfications) -> None:
        """Initializes the Tasks cog."""
        self.bot: core.Cozyfications = bot

        self.update_channels.start()

    def cog_unload(self) -> None:
        """Cancels all background tasks."""
        self.update_channels.cancel()

    @tasks.loop(minutes=3)
    async def update_channels(self):
        """Updates the embeds of Twitch channels in subscribed guilds every 3 minutes."""
        channels: list[Type[database.TwitchChannel]] = await database.get_twitch_channels()
        for twitch_channel in channels:
            await notify_guilds(twitch_channel=twitch_channel, bot=self.bot)

    @update_channels.before_loop
    async def before_update_channels(self):
        """Waits for the bot to be ready before starting the update_channels task."""
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tasks(bot))


async def notify_guilds(twitch_channel: Type[database.TwitchChannel], bot: core.Cozyfications) -> None:
    """Notifies subscribed guilds of a Twitch channel's live status.

    Parameters
    ----------
    twitch_channel : Type[database.TwitchChannel]
        The Twitch channel to notify subscribed guilds of.
    bot : core.Cozyfications
        The bot instance."""
    subscribed_guilds: List[Type[database.Guild]] = await database.get_subscribed_guilds(
        broadcaster_id=twitch_channel.id
    )
    stream: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
        broadcaster_id=twitch_channel.id
    )

    for guild in subscribed_guilds:
        channel: discord.TextChannel = await discord.utils.get_or_fetch(
            obj=bot,
            attr='channel',
            id=guild.channel_id,
            default=None
        )
        if not channel:
            continue

        message = await channel.fetch_message(guild.message_id)
        if not message:
            continue

        if stream.live:
            embed = core.LiveStreamEmbed(bot=bot, stream=stream)
        else:
            embed = core.OfflineStreamEmbed(bot=bot, stream=stream)

        embeds: list[discord.Embed] = core.create_embeds_list(
            message=message,
            twitch_channel=twitch_channel,
            new_embed=embed
        )
        await message.edit(embeds=embeds)
