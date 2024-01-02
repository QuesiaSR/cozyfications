import discord
from discord import ApplicationContext
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands

from Cozyfications.bot.main import Cozyfications
from Cozyfications.bot.ui import views
from Cozyfications.database.classes import TwitchDatabase
from Cozyfications.errors import *


class Twitch(commands.Cog):
    def __init__(self, bot: Cozyfications):
        self.bot = bot
        self.twitch = self.bot.ttv

    group = SlashCommandGroup("twitch", "Manage your server's Twitch settings.")
    streamer = group.create_subgroup("streamer", "Manage the selected streamers.")

    @streamer.command(name="add", description="Add a streamer you want to receive notifications from.")
    async def s_add(self, ctx: ApplicationContext, user: Option(str, description="The streamer's username.")):
        await ctx.defer()
        db = TwitchDatabase(ctx.guild.id)
        fetch = self.twitch.get_users(logins=[user.lower()])

        if len(fetch["data"]) <= 0 or not fetch["data"][0]["login"].lower() == user.lower():
            raise TwitchChannelNotFound()

        userid = fetch["data"][0]["id"]
        streamers = db.get_streamers()

        if streamers is not None and userid in streamers:
            raise TwitchChannelAlreadySelected()

        await self.bot.subscribe(userid, ctx.guild.id)
        db.add_streamer(userid)
        await ctx.followup.send(f"`{user.lower()}` has been added as a streamer! 🎉", delete_after=30)

    @streamer.command(name="remove", description="Remove a streamer you no longer want to receive notifications from.")
    async def s_remove(self, ctx: ApplicationContext, user: Option(str, description="The streamer's username.")):
        await ctx.defer()
        db = TwitchDatabase(ctx.guild.id)
        fetch = self.twitch.get_users(logins=[user.lower()])

        if len(fetch["data"]) <= 0 or not fetch["data"][0]["login"].lower() == user.lower():
            raise TwitchChannelNotFound()

        userid = fetch["data"][0]["id"]
        streamers = db.get_streamers()

        if streamers is not None and userid not in streamers:
            raise TwitchChannelNotSelected()

        await self.bot.unsubscribe(userid, ctx.guild.id)
        db.remove_streamer(userid)
        return await ctx.followup.send(f"`{user.lower()}` has been removed from the list. :(", delete_after=30)

    @group.command(name="message", description="Manage the message that's sent when a streamer goes live.")
    async def m_set(self, ctx: ApplicationContext, message: Option(str, description="The message", required=False)):
        await ctx.defer()
        db = TwitchDatabase(ctx.guild.id)
        if message:
            db.set_message(message)
            return await ctx.followup.send(f"The live message has been updated! 🎉", delete_after=30)

        dialog = views.ConfirmDialog()

        await ctx.reply("Are you sure you want to remove the live message?", view=dialog)
        await dialog.wait()

        if dialog.value:
            db.remove_message()
            return await ctx.followup.send("The live message has been removed. :(", delete_after=30)

        elif not dialog.value:
            return await ctx.followup.send("Removal has been cancelled.", delete_after=30)
        else:
            return await ctx.followup.send("Dialog timed out.", delete_after=30)

    @group.command(name="channel",
                   description="Manage the Discord channel where the message is sent when a streamer goes live.")
    async def c_set(self, ctx: ApplicationContext,
                    channel: Option(discord.TextChannel, description="The channel.", required=False)):
        await ctx.defer()
        db = TwitchDatabase(ctx.guild.id)
        if channel:
            db.set_channel(channel.id)
            return await ctx.followup.send(f"The live channel has been updated! 🎉", delete_after=30)

        dialog = views.ConfirmDialog()

        await ctx.reply("Are you sure you want to remove the live channel?", view=dialog)
        await dialog.wait()

        if dialog.value:
            db.remove_channel()
            return await ctx.followup.send("The live channel has been removed. :(", delete_after=30)

        elif not dialog.value:
            return await ctx.followup.send("Removal has been cancelled.", delete_after=30)
        else:
            return await ctx.followup.send("Dialog timed out.", delete_after=30)


def setup(bot):
    bot.add_cog(Twitch(bot))
