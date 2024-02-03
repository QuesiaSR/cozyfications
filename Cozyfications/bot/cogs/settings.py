import discord
from discord import utils
from discord.ext import commands
from discord.utils import basic_autocomplete

from Cozyfications import database, errors, twitch
from Cozyfications.bot import core


class Settings(core.Cog):
    """Set up the bot and add/remove subscriptions!"""

    @discord.slash_command(name="setup", description="Set up the channel and message for live stream notifications!",
                           default_member_permissions=discord.Permissions(administrator=True))
    async def setup(self, ctx: discord.ApplicationContext,
                    channel: discord.Option(
                        discord.TextChannel,
                        description="Select a channel to send live stream notifications to!",
                        required=True
                    ),
                    message_id: discord.Option(
                        str,
                        description="Select a message to edit when a stream goes live!",
                        required=False
                    )) -> None:
        """Set up the channel and message for live stream notifications!

        Parameters
        ----------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        channel: discord.abc.TextChannel
            The channel to send live stream notifications to.
        message_id: str
            The message to edit when a stream goes live."""
        await ctx.defer(ephemeral=True)

        message: discord.Message | None = None

        if message_id is None:
            message = await channel.send(embed=core.NotificationEmbed(bot=self.bot))
            message_id: int = message.id

        try:
            message_id: int = int(message_id)
        except ValueError:
            await ctx.followup.send(embed=core.InvalidMessageIDEmbed(message_id=message_id))
            return

        if message is None:
            message = await channel.fetch_message(message_id)

        if message.author != self.bot.user:
            await ctx.followup.send(embed=core.MessageNotSentByBotEmbed(channel=channel, message=message))
            return

        await database.set_guild(guild_id=ctx.guild.id, channel_id=channel.id, message_id=message_id)

        await ctx.followup.send(embed=core.SuccessfulSetupEmbed(channel=channel, message=message), ephemeral=True)

    twitch_group: discord.SlashCommandGroup = discord.SlashCommandGroup(
        name="twitch",
        description="Group of twitch commands!",
        default_member_permissions=discord.Permissions(administrator=True)
    )

    twitch_channel_group: discord.SlashCommandGroup = twitch_group.create_subgroup(
        name="channel",
        description="Group of twitch channel commands!"
    )

    @twitch_channel_group.command(name="subscribe", description="Subscribe to a Twitch channel!")
    async def twitch_channel_subscribe(self, ctx: discord.ApplicationContext,
                                       twitch_channel: discord.Option(
                                           str,
                                           description="The Twitch channel to subscribe to!",
                                           required=True,
                                           autocomplete=twitch.get_channels_autocomplete
                                       )) -> None:
        """Subscribe to a Twitch channel!

        Parameters
        ----------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        twitch_channel: str
            The Twitch channel to subscribe to."""
        await ctx.defer(ephemeral=True)

        try:
            guild: database.Guild = await database.get_guild(guild_id=ctx.guild.id)
        except errors.GuildNotFoundInDatabase:
            await ctx.followup.send(embed=core.GuildNotSetupEmbed(bot=self.bot), ephemeral=True)
            return

        if len(await database.get_subscribed_channels(guild_id=ctx.guild_id)) >= 10:
            await ctx.followup.send(embed=core.SubscriptionLimitEmbed(bot=self.bot), ephemeral=True)
            return

        try:
            broadcaster_id: int = await twitch.get_broadcaster_id(channel=twitch_channel)
        except errors.TwitchChannelNotFound:
            await ctx.followup.send(embed=core.InvalidTwitchChannelEmbed(twitch_channel=twitch_channel), ephemeral=True)
            return

        twitch_channel: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
            broadcaster_id=broadcaster_id
        )

        try:
            await database.add_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)
        except errors.TwitchChannelNotFoundInDatabase:
            await database.set_twitch_channel(
                broadcaster_id=broadcaster_id,
                streamer=twitch_channel.streamer,
                live=twitch_channel.live,
                stream_title=twitch_channel.title
            )
            await database.add_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)
        except errors.DuplicateSubscription:
            await ctx.followup.send(
                embed=core.DuplicateSubscriptionEmbed(twitch_channel=twitch_channel),
                ephemeral=True)
            return

        try:
            channel: discord.TextChannel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id)
            message: discord.Message = await channel.fetch_message(guild.message_id)
        except discord.NotFound:
            await ctx.followup.send(embed=core.GuildNotSetupEmbed(bot=self.bot), ephemeral=True)
            return

        if twitch_channel.live:
            embed: core.LiveStreamEmbed = core.LiveStreamEmbed(bot=self.bot, stream=twitch_channel)
        else:
            embed: core.OfflineStreamEmbed = core.OfflineStreamEmbed(bot=self.bot, stream=twitch_channel)
        embeds = [embed for embed in message.embeds if embed.title != "Live Stream Notifications"]
        embeds.append(embed)
        await message.edit(embeds=embeds)

        await ctx.followup.send(embed=core.SuccessfulSubscriptionEmbed(twitch_channel=twitch_channel), ephemeral=True)

    @twitch_channel_group.command(name="unsubscribe", description="Unsubscribe from a Twitch channel!")
    async def twitch_channel_unsubscribe(self, ctx: discord.ApplicationContext,
                                         twitch_channel: discord.Option(
                                             str,
                                             description="The Twitch channel to unsubscribe from!",
                                             required=True,
                                             autocomplete=basic_autocomplete(
                                                 database.get_subscribed_channels_autocomplete
                                             )
                                         )) -> None:
        """Unsubscribe from a Twitch channel!

        Parameters
        ----------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        twitch_channel: str
            The Twitch channel to unsubscribe from."""
        await ctx.defer(ephemeral=True)

        try:
            guild: database.Guild = await database.get_guild(guild_id=ctx.guild.id)
        except errors.GuildNotFoundInDatabase:
            await ctx.followup.send(embed=core.GuildNotSetupEmbed(bot=self.bot), ephemeral=True)
            return

        try:
            broadcaster_id: int = await twitch.get_broadcaster_id(channel=twitch_channel)
        except errors.TwitchChannelNotFound:
            await ctx.followup.send(embed=core.InvalidTwitchChannelEmbed(twitch_channel=twitch_channel), ephemeral=True)
            return

        twitch_channel: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
            broadcaster_id=broadcaster_id
        )

        try:
            await database.remove_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)
        except errors.TwitchChannelNotFoundInDatabase or errors.SubscriptionNotFound:
            await ctx.followup.send(embed=core.NotSubscribedEmbed(twitch_channel=twitch_channel), ephemeral=True)
            return

        try:
            channel: discord.TextChannel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id)
            message: discord.Message = await channel.fetch_message(guild.message_id)
        except discord.NotFound:
            await ctx.followup.send(embed=core.GuildNotSetupEmbed(bot=self.bot), ephemeral=True)
            return

        if len(await database.get_subscribed_channels(guild_id=guild.id)) == 0:
            await message.edit(embed=core.NotificationEmbed(bot=self.bot))
        else:
            embeds = [embed for embed in message.embeds if twitch_channel.streamer not in embed.title]
            await message.edit(embeds=embeds)

        await ctx.followup.send(embed=core.SuccessfulUnsubscriptionEmbed(twitch_channel=twitch_channel), ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Delete the guild from the database when the bot leaves the guild.

        Parameters
        ----------
        guild: discord.Guild
            The guild that the bot left."""
        try:
            await database.delete_guild(guild_id=guild.id)
        except errors.GuildNotFoundInDatabase:
            pass


def setup(bot):
    bot.add_cog(Settings(bot))
