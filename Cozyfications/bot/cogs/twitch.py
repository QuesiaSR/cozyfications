import discord

from Cozyfications.bot import core
from Cozyfications.database.classes import TwitchDatabase
from Cozyfications.errors import *


class Twitch(core.Cog):
    """Manage your server's Twitch Cozyfication settings."""

    def __init__(self, bot: core.Cozyfications):
        self.bot = bot
        # TODO: Fix Twitch API
        #  self.twitch = self.bot.ttv

    twitch_group = discord.SlashCommandGroup(
        name="twitch",
        description="Manage your server's Twitch settings!"
    )
    streamer_group = twitch_group.create_subgroup(
        name="directory",
        description="Manage the selected streamers!",
    )

    @streamer_group.command(name="add", description="Add a streamer you want to receive notifications from.")
    async def add_streamer(self, ctx: discord.ApplicationContext,
                           user: discord.Option(str, description="The streamer's username.", required=True)):
        """Add a streamer you want to receive notifications from.

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        user: str
            The streamer's username."""
        await ctx.defer()
        db: TwitchDatabase = TwitchDatabase(ctx.guild.id)
        fetch = self.twitch.get_users(logins=[user.lower()])

        if len(fetch["data"]) <= 0 or not fetch["data"][0]["login"].lower() == user.lower():
            raise TwitchChannelNotFound()

        userid = fetch["data"][0]["id"]
        streamers = db.get_streamers()

        if streamers is not None and userid in streamers:
            raise TwitchChannelAlreadySelected()

        await self.bot.subscribe(userid, ctx.guild.id)
        db.add_streamer(userid)
        await ctx.followup.send(
            content=f"`{user.lower()}` has been added as a streamer! 🎉",
            ephemeral=True
        )

    @streamer_group.command(name="remove",
                            description="Remove a streamer you no longer want to receive notifications from!")
    async def s_remove(self, ctx: discord.ApplicationContext,
                       user: discord.Option(str, description="The streamer's username.", required=True)):
        """Remove a streamer you no longer want to receive notifications from.

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        user: str
            The streamer's username."""
        await ctx.defer()
        db: TwitchDatabase = TwitchDatabase(ctx.guild.id)
        fetch = self.twitch.get_users(logins=[user.lower()])

        if len(fetch["data"]) <= 0 or not fetch["data"][0]["login"].lower() == user.lower():
            raise TwitchChannelNotFound()

        userid = fetch["data"][0]["id"]
        streamers = db.get_streamers()

        if streamers is not None and userid not in streamers:
            raise TwitchChannelNotSelected()

        await self.bot.unsubscribe(userid, ctx.guild.id)
        db.remove_streamer(userid)
        return await ctx.followup.send(
            content=f"`{user.lower()}` has been removed from the list. :(",
            ephemeral=True
        )

    set_group = twitch_group.create_subgroup(
        name="set",
        description="Manage the settings for your server's Twitch Cozyfication",
    )

    @set_group.command(name="message", description="Manage the message that's sent when a streamer goes live.")
    async def set_message(self, ctx: discord.ApplicationContext,
                          message: discord.Option(str, description="The message for Cozyfications", required=False)):
        """Manage the message that's sent when a streamer goes live.

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        message: str
            The message to send when a streamer goes live."""
        await ctx.defer()
        db: TwitchDatabase = TwitchDatabase(ctx.guild.id)
        if message:
            db.set_message(message)
            return await ctx.followup.send(
                content=f"The live message has been updated! 🎉",
                ephemeral=True
            )

        dialog = core.views.ConfirmDialog()

        await ctx.followup.send(
            content="Are you sure you want to remove the live message?",
            view=dialog,
            ephemeral=True
        )
        await dialog.wait()

        if dialog.value:
            db.remove_message()
            return await ctx.followup.send(
                content="The live message has been removed. :(",
                ephemeral=True
            )

        elif not dialog.value:
            return await ctx.followup.send(
                content="Removal has been cancelled.",
                ephemeral=True
            )
        else:
            return await ctx.followup.send(
                content="Dialog timed out.",
                ephemeral=True
            )

    @set_group.command(name="channel",
                       description="Manage the Discord channel where the message is sent when a streamer goes live.")
    async def set_channel(self, ctx: discord.ApplicationContext,
                          channel: discord.Option(discord.TextChannel, description="The channel for Cozyfications.",
                                                  required=False)):
        """Manage the Discord channel where the message is sent when a streamer goes live.

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation.
        channel: discord.TextChannel
            The channel where the message is sent when a streamer goes live."""
        await ctx.defer()
        db = TwitchDatabase(ctx.guild.id)
        if channel:
            db.set_channel(channel.id)
            return await ctx.followup.send(
                content="The live channel has been updated! 🎉",
                ephemeral=True
            )

        dialog = core.views.ConfirmDialog()

        await ctx.followup.send(
            content="Are you sure you want to remove the live channel?",
            view=dialog,
            ephemeral=True
        )
        await dialog.wait()

        if dialog.value:
            db.remove_channel()
            return await ctx.followup.send(
                content="The live channel has been removed. :(",
                ephemeral=True
            )

        elif not dialog.value:
            return await ctx.followup.send(
                content="Removal has been cancelled.",
                ephemeral=True
            )
        else:
            return await ctx.followup.send(
                content="Dialog timed out.",
                ephemeral=True
            )


def setup(bot):
    bot.add_cog(Twitch(bot))
