import discord
from twitchAPI import Twitch as TwitchAPI
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from Cozyfications.errors import *
from Cozyfications.secrets import Twitch as Sec
from Cozyfications.database.classes import TwitchDatabase
from Cozyfications.bot.ui import views
from Cozyfications import events

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch = TwitchAPI(Sec.ID, Sec.SECRET)

    group = SlashCommandGroup("twitch", "Manage your server's Twitch settings.")
    streamer = group.create_subgroup("streamer", "Manage the selected streamers.")
    message = group.create_subgroup("message", "Manage the various message types.")
    channel = group.create_subgroup("channel", "Manage the various channel types.")

    @streamer.command(name="add", description="Add a streamer you want to receive notifications from.")
    async def s_add(self, ctx, user: Option(str, description="The streamer's username.")):
        db = TwitchDatabase(ctx.guild.id)
        fetch = self.twitch.get_users(logins=[user.lower()])

        if len(fetch["data"]) <= 0 or not fetch["data"][0]["login"].lower() == user.lower():
            raise TwitchChannelNotFound("Channel not found.")

        userid = fetch["data"][0]["id"]
        streamers = db.get_streamers()

        if not streamers == None and userid in streamers:
            raise TwitchChannelAlreadySelected("Channel already selected.")

        db.add_streamer(userid)
        await ctx.respond(f"`{user.lower()}` has been added as a streamer! 🎉", delete_after=30)
        events.subscribe(userid, ctx.guild.id)
    
    @streamer.command(name="remove", description="Remove a streamer you no longer want to receive notifications from.")
    async def s_remove(self, ctx, user: Option(str, description="The streamer's username.")):
        db = TwitchDatabase(ctx.guild.id)
        fetch = self.twitch.get_users(logins=[user.lower()])

        if len(fetch["data"]) <= 0 or not fetch["data"][0]["login"].lower() == user.lower():
            raise TwitchChannelNotFound("Channel not found.")

        userid = fetch["data"][0]["id"]
        streamers = db.get_streamers()

        if not streamers == None and not userid in streamers:
            raise TwitchChannelNotSelected("Channel not selected.")

        events.unsubscribe(userid, ctx.guild.id)
        db.remove_streamer(userid)
        return await ctx.respond(f"`{user.lower()}` has been removed from the list. :(", delete_after=30)

    @message.command(name="live", description="Manage the message that's sent when a streamer goes live.")
    async def l_m_set(self, ctx, message: Option(str, description="The message", required=False)):
        db = TwitchDatabase(ctx.guild.id)
        if message:
            db.set_messages(live_message=message)
            return await ctx.respond(f"The live message has been updated! 🎉", delete_after=30)
        
        dialog = views.ConfirmDialog()

        await ctx.reply("Are you sure you want to remove the live message?", view=dialog)
        await dialog.wait()

        if dialog.value:
            db.remove_messages(live_message=True)
            return await ctx.respond("The live message has been removed. :(", delete_after=30)

        elif not dialog.value: return await ctx.respond("Removal has been cancelled.", delete_after=30)
        else: return await ctx.respond("Dialog timed out.", delete_after=30)
    
    @message.command(name="clip", description="Manage the message that's sent when a streamer creates a new clip.")
    async def c_m_set(self, ctx, message: Option(str, description="The message.", required=False)):
        db = TwitchDatabase(ctx.guild.id)
        if message:
            db.set_messages(clip_message=message)
            return await ctx.respond(f"The clip message has been updated! 🎉", delete_after=30)
        
        dialog = views.ConfirmDialog()

        await ctx.reply("Are you sure you want to remove the clip message?", view=dialog)
        await dialog.wait()

        if dialog.value:
            db.remove_messages(clip_message=True)
            return await ctx.respond("The clip message has been removed. :(", delete_after=30)

        elif not dialog.value: return await ctx.respond("Removal has been cancelled.", delete_after=30)
        else: return await ctx.respond("Dialog timed out.", delete_after=30)
    
    @channel.command(name="live", description="Manage the Discord channel where the message is sent when a streamer goes live.")
    async def l_c_set(self, ctx, channel: Option(discord.TextChannel, description="The channel.", required=False)):
        db = TwitchDatabase(ctx.guild.id)
        if channel:
            db.set_channels(live_channel=str(channel.id))
            return await ctx.respond(f"The live channel has been updated! 🎉", delete_after=30)

        dialog = views.ConfirmDialog()

        await ctx.reply("Are you sure you want to remove the live channel?", view=dialog)
        await dialog.wait()

        if dialog.value:
            db.remove_channels(live_channel=True)
            return await ctx.respond("The live channel has been removed. :(", delete_after=30)

        elif not dialog.value: return await ctx.respond("Removal has been cancelled.", delete_after=30)
        else: return await ctx.respond("Dialog timed out.", delete_after=30)
    
    @channel.command(name="clip", description="Manage the Discord channel where the message is sent when a streamer goes creates a new clip.")
    async def c_c_set(self, ctx, channel: Option(discord.TextChannel, description="The channel.", required=False)):
        db = TwitchDatabase(ctx.guild.id)
        if channel:
            db.set_channels(clip_channel=str(channel.id))
            return await ctx.respond(f"The clip channel has been updated! 🎉", delete_after=30)
        
        dialog = views.ConfirmDialog()

        await ctx.reply("Are you sure you want to remove the clip channel?", view=dialog)
        await dialog.wait()

        if dialog.value:
            db.remove_channels(clip_channel=True)
            return await ctx.respond("The clip channel has been removed. :(", delete_after=30)

        elif not dialog.value: return await ctx.respond("Removal has been cancelled.", delete_after=30)
        else: return await ctx.respond("Dialog timed out.", delete_after=30)

def setup(bot):
    bot.add_cog(Twitch(bot))
