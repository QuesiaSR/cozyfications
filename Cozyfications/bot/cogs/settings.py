import discord
from discord.ext import commands

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
            await ctx.respond(embed=core.RedEmbed(
                title="Error",
                description="Invalid message ID!"
            ), ephemeral=True)
            return

        if cozyfications_message is None:
            cozyfications_message = await channel.fetch_message(message_id)

        if cozyfications_message.author != self.bot.user:
            await ctx.respond(embed=core.RedEmbed(
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
        await ctx.respond(embed=success_embed, ephemeral=True)

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
                                           required=True
                                       )) -> None:
        """Subscribe to a Twitch channel!

        Parameters
        ----------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        channel: str
            The Twitch channel to subscribe to."""
        try:
            broadcaster_id: int = await twitch.get_broadcaster_id(channel=channel)
        except errors.TwitchChannelNotFound:
            await ctx.respond(embed=core.RedEmbed(
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
            print(f"Command: {setup_command}")
            await ctx.respond(embed=core.RedEmbed(
                title="Error",
                description=f"""The guild has not been set up yet!
                Use </{setup_command.qualified_name}:{setup_command.qualified_id}> to set up the guild."""
            ), ephemeral=True)
            return

        except errors.TwitchChannelNotFoundInDatabase:
            database.set_twitch_channel(
                broadcaster_id=broadcaster_id,
                live=twitch_channel.live,
                stream_title=twitch_channel.title
            )

        except errors.DuplicateSubscription:
            await ctx.respond(embed=core.RedEmbed(
                title="Error",
                description=f"Already subscribed to [{twitch_channel.streamer}]({twitch_channel.url})!"
            ), ephemeral=True)
            return

        await ctx.respond(embed=core.GreenEmbed(
            title="Success!",
            description=f"Successfully subscribed to [{twitch_channel.streamer}]({twitch_channel.url})!"
        ), ephemeral=True)

    @twitch_channel_group.command(name="unsubscribe", description="Unsubscribe from a Twitch channel!")
    async def twitch_channel_unsubscribe(self, ctx: discord.ApplicationContext,
                                         channel: discord.Option(
                                             str,
                                             description="The Twitch channel to unsubscribe from!",
                                             required=True
                                         )) -> None:
        """Unsubscribe from a Twitch channel!

        Parameters
        ----------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        channel: str
            The Twitch channel to unsubscribe from."""
        broadcaster_id: int = await twitch.get_broadcaster_id(channel=channel)

        if broadcaster_id is None:
            await ctx.respond(embed=core.RedEmbed(
                title="Error",
                description="Invalid Twitch channel!"
            ), ephemeral=True)
            return

        twitch_channel: twitch.LiveStream | twitch.OfflineStream = await twitch.get_channel(
            broadcaster_id=broadcaster_id
        )

        try:
            database.remove_subscription(guild_id=ctx.guild.id, broadcaster_id=broadcaster_id)
        except errors.SubscriptionNotFound:
            await ctx.respond(embed=core.RedEmbed(
                title="Error",
                description=f"Not subscribed to [{twitch_channel.streamer}]({twitch_channel.url})!"
            ), ephemeral=True)
            return
        await ctx.respond(embed=core.GreenEmbed(
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
