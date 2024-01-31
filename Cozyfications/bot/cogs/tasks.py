from typing import Type

import discord
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
        live_channels: list[Type[database.TwitchChannel]] = database.get_all_live_channels()
        for twitch_channel in live_channels:
            subscribed_guilds = database.get_subscribed_guilds(broadcaster_id=twitch_channel.id)
            for guild in subscribed_guilds:
                channel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id, default=None)
                message = await channel.fetch_message(guild.message_id)
                live_stream: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
                    broadcaster_id=twitch_channel.id
                )
                live_embed: core.LiveStreamEmbed = core.LiveStreamEmbed(bot=self.bot, stream=live_stream)

                embeds: list[discord.Embed] = core.create_embeds_list(
                    message=message,
                    twitch_channel=twitch_channel,
                    new_embed=live_embed
                )
                await message.edit(embeds=embeds)

    @update_live_channels.before_loop
    async def before_update_live_channels(self):
        """Waits for the bot to be ready before starting the update_live_channels task."""
        await self.bot.wait_until_ready()
        channels: list[Type[database.TwitchChannel]] = database.get_all_channels()
        for twitch_channel in channels:
            subscribed_guilds = database.get_subscribed_guilds(broadcaster_id=twitch_channel.id)
            stream: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
                broadcaster_id=twitch_channel.id
            )
            if stream.live:
                continue
            for guild in subscribed_guilds:
                channel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id, default=None)
                message = await channel.fetch_message(guild.message_id)
                offline_embed: core.OfflineStreamEmbed = core.OfflineStreamEmbed(bot=self.bot, stream=stream)

                embeds: list[discord.Embed] = core.create_embeds_list(
                    message=message,
                    twitch_channel=twitch_channel,
                    new_embed=offline_embed
                )
                await message.edit(embeds=embeds)


def setup(bot):
    bot.add_cog(Tasks(bot))
