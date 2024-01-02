import os
from datetime import datetime

import discord
from discord import ApplicationContext, commands, AutoShardedBot
from discord.errors import NotFound, Forbidden, HTTPException
from pyngrok import ngrok
from twitchAPI import EventSub, Twitch as TwitchAPI, EventSubSubscriptionConflict

from Cozyfications.bot.ui import views
from Cozyfications.database.classes import StreamerDatabase, TwitchDatabase, MessageDatabase
from Cozyfications.secrets import Twitch


class Callbacks:
    async def get_guilds(self, data):
        streamer = data["subscription"]["condition"]["broadcaster_user_id"]
        streamer_db = StreamerDatabase(streamer)
        guilds = streamer_db.get_guilds()

        return_dict = []

        for guild in guilds:
            return_dict.append(TwitchDatabase(guild))
        return return_dict

    async def update(self, data):
        print("update")

        async def callback(data, bot: AutoShardedBot):
            guilds = await Callbacks.get_guilds(self, data)

            for guild in guilds:
                guild: TwitchDatabase
                channel = guild.get_channel()

                if channel is not None:
                    msg_db = MessageDatabase(guild.guild_id, data["subscription"]["condition"]["broadcaster_user_id"],
                                             channel)
                    msg_id = msg_db.get_message()

                    if msg_id is not None:
                        sent = await bot.get_channel(channel).fetch_message(int(msg_id))
                        if sent is not None:
                            await sent.edit("Updated.")
                        else:
                            print("no msg")
                    else:
                        print("no msg_id")
                else:
                    print("no channels")

        Cozyfications.QUEUE.append({"data": data, "callback": callback})

    async def online(self, data):
        print("online")

        async def callback(data, bot: AutoShardedBot):
            guilds = await Callbacks.get_guilds(self, data)

            for guild in guilds:
                guild: TwitchDatabase
                channel = guild.get_channel()

                if channel is not None:
                    channel = bot.get_channel(channel)
                    message = guild.get_message()
                    message = "Online." if message is None else message

                    sent = await channel.send(message)
                    msg_db = MessageDatabase(guild.guild_id, data["subscription"]["condition"]["broadcaster_user_id"],
                                             channel)
                    msg_db.create_message(sent.id)

        Cozyfications.QUEUE.append({"data": data, "callback": callback})

    async def offline(self, data):
        print("offline")

        async def callback(data, bot: AutoShardedBot):
            guilds = await Callbacks.get_guilds(self, data)

            for guild in guilds:
                guild: TwitchDatabase
                channel = guild.get_channel()

                if channel is not None:
                    message = "Offline."

                    msg_db = MessageDatabase(guild.guild_id, data["subscription"]["condition"]["broadcaster_user_id"],
                                             channel)
                    msg_id = msg_db.get_message()

                    channel = bot.get_channel(channel)
                    if msg_id is not None:
                        msg_db.delete_message(msg_id)
                        try:
                            sent = await channel.fetch_message(int(msg_id))
                            if sent is not None:
                                return await sent.edit(message)
                        except NotFound | Forbidden | HTTPException:
                            pass
                    await channel.send(message)

        Cozyfications.QUEUE.append({"data": data, "callback": callback})


class Cozyfications(AutoShardedBot):
    QUEUE = []

    def __init__(self):
        self.start_time = datetime.utcnow()

        self.persistent_views_added = False
        self.cog_blacklist = []
        self.cog_folder_blacklist = ["__pycache__"]
        self.path = "./Cozyfications/bot/cogs"

        self.new_subscriptions = 0
        self.delete_subscriptions = 0
        self.subscriptions = {
            "channel.update": Callbacks.update,
            "stream.online": Callbacks.online,
            "stream.offline": Callbacks.offline
        }
        self.port = 6001
        self.url = None
        self.hook: EventSub = None
        self.ttv: TwitchAPI = None

        self.color = 0xE0B484

        super().__init__(
            intents=discord.Intents(members=True, guilds=True, messages=True),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False),
            owner_ids=[810863994985250836],
            debug_guilds=[1018128160962904114]
        )

        @commands.slash_command(name="reload", description="Reload the cogs.")
        async def reload_cogs(ctx: ApplicationContext):
            await ctx.defer()
            print("Reloading cogs...")
            for extension in ctx.bot.extensions:
                ctx.bot.reload_extension(extension)
            return await ctx.followup.send(content="Done!")

        self.add_application_command(reload_cogs)

    async def load_cogs(self, folder=None):
        if folder is not None:
            self.path = os.path.join(self.path, folder)
        formatted_path = self.path.strip("./").replace("/", ".").replace("\\", ".")

        for file in os.listdir(self.path):
            if not os.path.isdir(os.path.join(self.path, file)):
                if file not in self.cog_blacklist:
                    try:
                        self.load_extension(f"{formatted_path}.{file[:-3]}")
                        print(f"  Loaded '{file}'")
                    except Exception as e:
                        print(e)
            else:
                if file not in self.cog_folder_blacklist:
                    self.load_cogs(file)

    async def run_server(self) -> None:
        ngrok.update()
        ngrok.connect(self.port)
        tunnels = ngrok.get_tunnels()
        self.url = tunnels[1].public_url if tunnels[1].public_url.startswith("https://") else tunnels[0].public_url
        print(f"  Started ngrok server at '{self.url}'")

    async def subscribe(self, user, guild_id) -> None:
        if self.hook is not None:
            self.new_subscriptions += 1
            for subscription in self.subscriptions:
                try:
                    sub_id = self.hook._subscribe(subscription, "1", {"broadcaster_user_id": str(user)},
                                                 self.subscriptions[subscription])
                    StreamerDatabase(user).add_guild(guild_id, sub_id)
                except EventSubSubscriptionConflict:
                    pass

    async def unsubscribe(self, user, guild_id) -> None:
        if self.ttv is not None:
            self.delete_subscriptions += 1
            streamer_db = StreamerDatabase(user)
            subscription_ids = streamer_db.get_subscription_ids(guild_id)
            for subscription_id in subscription_ids:
                self.ttv.delete_eventsub_subscription(subscription_id)
            streamer_db.remove_guild(guild_id)

    async def run_event_hook(self):
        self.ttv = TwitchAPI(Twitch.ID, Twitch.SECRET)
        self.ttv.authenticate_app([])

        self.hook = EventSub(self.url, Twitch.ID, self.port, self.ttv)
        (self.hook.unsubscribe_all(), print("  Unsubscribed from all events"))
        (self.hook.start(), print("  Started event hook"))

    async def subscribe_events(self):
        print("  Fetching users...")
        users = StreamerDatabase.get_streamers()

        for user in users:
            for subscription in self.subscriptions:
                self.hook._subscribe(subscription, "1", {"broadcaster_user_id": str(user)},
                                     self.subscriptions[subscription])
                if user == users[len(users) - 1]:
                    print(f"  Finished subscribing to '{subscription}' for all users")
        print("  Finished subscribing to all subscriptions for all users")

    async def on_connect(self):
        (
            print("Starting ngrok server..."),
            await self.run_server()
        )
        (
            print("Starting event hook..."),
            await self.run_event_hook()
        )
        (
            print("Subscribing to events..."),
            await self.subscribe_events()
        )
        (
            print("Loading cogs..."),
            await self.load_cogs()
        )
        (
            print("Registering commands..."),
            await self.register_commands()
        )
        print("\nConnected")
        return await super().on_connect()

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(views.ConfirmDialog())
            self.persistent_views_added = True

        return print(f"Ready, took {(datetime.utcnow() - self.start_time).seconds} seconds.")


if __name__ == "__main__":
    exit("The bot cannot be run directly from the bot file.")
