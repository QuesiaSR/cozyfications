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

        cozyfications_message: discord.Message | None = None

        if message_id is None:
            cozyfications_message = await channel.send(embed=core.CozyficationsEmbed(
                title="Live Stream Notifications",
                description="This message will be edited when a stream goes live!",
                bot=self.bot
            ))
            message_id: int = cozyfications_message.id

        try:
            message_id: int = int(message_id)
        except ValueError:
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description="Invalid message ID!"
            ), ephemeral=True)
            return

        if cozyfications_message is None:
            cozyfications_message = await channel.fetch_message(message_id)

        if cozyfications_message.author != self.bot.user:
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description="The message must be sent by the bot!"
            ), ephemeral=True)
            return

        database.set_guild(guild_id=ctx.guild.id, channel_id=channel.id, message_id=message_id)

        success_embed: core.GreenEmbed = core.GreenEmbed(
            title="Success!",
            description="Successfully set up the channel and message for live stream notifications!"
        )
        success_embed.add_field(
            name="Channel",
            value=channel.mention
        )
        success_embed.add_field(
            name="Message",
            value=f"[Click Here]({cozyfications_message.jump_url})"
        )
        await ctx.followup.send(embed=success_embed, ephemeral=True)

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
                                       channel: discord.Option(
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
        channel: str
            The Twitch channel to subscribe to."""
        await ctx.defer(ephemeral=True)

        try:
            broadcaster_id: int = await twitch.get_broadcaster_id(channel=channel)
        except errors.TwitchChannelNotFound:
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description="Invalid Twitch channel!"
            ), ephemeral=True)
            return

        twitch_channel: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
            broadcaster_id=broadcaster_id
        )

        try:
            database.add_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)

        except errors.GuildNotFoundInDatabase:
            setup_command = self.bot.get_application_command("setup")
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description=f"""The guild has not been set up yet!
                Use </{setup_command.qualified_name}:{setup_command.qualified_id}> to set up the guild."""
            ), ephemeral=True)
            return

        except errors.TwitchChannelNotFoundInDatabase:
            database.set_twitch_channel(
                broadcaster_id=broadcaster_id,
                streamer=twitch_channel.streamer,
                live=twitch_channel.live,
                stream_title=twitch_channel.title
            )
            database.add_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)

        except errors.DuplicateSubscription:
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description=f"Already subscribed to [{twitch_channel.streamer}]({twitch_channel.url})!"
            ), ephemeral=True)
            return

        guild = database.get_guild(guild_id=ctx.guild.id)
        channel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id, default=None)
        message = await channel.fetch_message(guild.message_id)
        if twitch_channel.live:
            embed: core.LiveStreamEmbed = core.LiveStreamEmbed(bot=self.bot, stream=twitch_channel)
        else:
            embed: core.OfflineStreamEmbed = core.OfflineStreamEmbed(bot=self.bot, stream=twitch_channel)
        # TODO: Support multiple subscriptions per guild.
        await message.edit(embed=embed)

        await ctx.followup.send(embed=core.GreenEmbed(
            title="Success!",
            description=f"Successfully subscribed to [{twitch_channel.streamer}]({twitch_channel.url})!"
        ), ephemeral=True)

    @twitch_channel_group.command(name="unsubscribe", description="Unsubscribe from a Twitch channel!")
    async def twitch_channel_unsubscribe(self, ctx: discord.ApplicationContext,
                                         channel: discord.Option(
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
        channel: str
            The Twitch channel to unsubscribe from."""
        await ctx.defer(ephemeral=True)

        try:
            broadcaster_id: int = await twitch.get_broadcaster_id(channel=channel)
        except errors.TwitchChannelNotFound:
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description="Invalid Twitch channel!"
            ), ephemeral=True)
            return

        twitch_channel: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
            broadcaster_id=broadcaster_id
        )

        try:
            database.remove_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)

        except errors.GuildNotFoundInDatabase:
            setup_command = self.bot.get_application_command("setup")
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description=f"""The guild has not been set up yet!
                Use </{setup_command.qualified_name}:{setup_command.qualified_id}> to set up the guild."""
            ), ephemeral=True)
            return

        except errors.TwitchChannelNotFoundInDatabase or errors.SubscriptionNotFound:
            await ctx.followup.send(embed=core.RedEmbed(
                title="Error",
                description=f"Not subscribed to [{twitch_channel.streamer}]({twitch_channel.url})!"
            ), ephemeral=True)
            return

        guild = database.get_guild(guild_id=ctx.guild.id)
        if len(database.get_subscribed_channels(guild_id=guild.id)) == 0:
            channel = await utils.get_or_fetch(obj=self.bot, attr='channel', id=guild.channel_id, default=None)
            message = await channel.fetch_message(guild.message_id)
            await message.edit(embed=core.CozyficationsEmbed(
                title="Live Stream Notifications",
                description="This message will be edited when a stream goes live!",
                bot=self.bot
            ))

        await ctx.followup.send(embed=core.GreenEmbed(
            title="Success!",
            description=f"Successfully unsubscribed from [{twitch_channel.streamer}]({twitch_channel.url})!"
        ), ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Delete the guild from the database when the bot leaves the guild.

        Parameters
        ----------
        guild: discord.Guild
            The guild that the bot left."""
        try:
            database.delete_guild(guild_id=guild.id)
        except errors.GuildNotFoundInDatabase:
            pass


def setup(bot):
    bot.add_cog(Settings(bot))
