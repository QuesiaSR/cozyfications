import discord, os
from datetime import datetime
from discord import ApplicationContext, commands, AutoShardedBot
from discord.errors import NotFound, Forbidden, HTTPException
from Cozyfications.bot.ui import views
from Cozyfications.database.classes import StreamerDatabase, TwitchDatabase, MessageDatabase
from Cozyfications.secrets import Twitch, Ngrok
from twitchAPI import EventSub, Twitch as TwitchAPI, EventSubSubscriptionConflict
from pyngrok import ngrok

class Callbacks:
    async def get_guilds(data):
        streamer = data["subscription"]["condition"]["broadcaster_user_id"]
        strdb = StreamerDatabase(streamer)
        guilds = strdb.get_guilds()

        ret = []

        for guild in guilds:
            ret.append(TwitchDatabase(guild))
        return ret

    async def update(data):
        print("update")
        async def callback(data, bot: AutoShardedBot):
            guilds = await Callbacks.get_guilds(data)

            for guild in guilds:
                guild: TwitchDatabase
                channel = guild.get_channel()

                if not channel is None:
                    msgdb = MessageDatabase(guild.guildid, data["subscription"]["condition"]["broadcaster_user_id"], channel)
                    msgid = msgdb.get_message()

                    if msgid != None:
                        sent = await bot.get_channel(channel).fetch_message(int(msgid))
                        if sent != None:
                            await sent.edit("Updated.")
                        else: print("no msg")
                    else: print("no msgid")
                else: print("no channels")
        Cozyfications.QUEUE.append({"data": data, "callback": callback})

    async def online(data):
        print("online")
        async def callback(data, bot: AutoShardedBot):
            guilds = await Callbacks.get_guilds(data)

            for guild in guilds:
                guild: TwitchDatabase
                channel = guild.get_channel()

                if not channel is None:
                    channel = bot.get_channel(channel)
                    message = guild.get_message()
                    message = "Online." if message is None else message

                    sent = await channel.send(message)
                    msgdb = MessageDatabase(guild.guildid, data["subscription"]["condition"]["broadcaster_user_id"], channel)
                    msgdb.create_message(sent.id)
        Cozyfications.QUEUE.append({"data": data, "callback": callback})
                
    async def offline(data):
        print("offline")
        async def callback(data, bot: AutoShardedBot):
            guilds = await Callbacks.get_guilds(data)

            for guild in guilds:
                guild: TwitchDatabase
                channel = guild.get_channel()

                if not channel is None:
                    message = "Offline."

                    msgdb = MessageDatabase(guild.guildid, data["subscription"]["condition"]["broadcaster_user_id"], channel)
                    msgid = msgdb.get_message()
                    
                    channel = bot.get_channel(channel)
                    if msgid != None:
                        msgdb.delete_message(msgid)
                        try:
                            sent = await channel.fetch_message(int(msgid))
                            if sent != None:
                                return await sent.edit(message)
                        except NotFound | Forbidden | HTTPException: pass
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
        self.del_subscriptions = 0
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
        if folder != None: self.path = os.path.join(self.path, folder)
        formatted_path = self.path.strip("./").replace("/", ".").replace("\\", ".")

        for file in os.listdir(self.path):
            if not os.path.isdir(os.path.join(self.path, file)):
                if not file in self.cog_blacklist:
                    try:
                        self.load_extension(f"{formatted_path}.{file[:-3]}")
                        print(f"  Loaded '{file}'")
                    except Exception as e: print(e)
            else:
                if not file in self.cog_folder_blacklist:
                    self.load_cogs(file)

    async def run_server(self) -> None:
        ngrok.set_auth_token(Ngrok.TOKEN)
        ngrok.connect(self.port)
        tunnels = ngrok.get_tunnels()
        self.url = tunnels[1].public_url if tunnels[1].public_url.startswith("https://") else tunnels[0].public_url
        print(f"  Started ngrok server at '{self.url}'")

    async def subscribe(self, user, guildid) -> None:
        if self.hook != None:
            self.new_subscriptions += 1
            for subscription in self.subscriptions:
                try:
                    subid = self.hook._subscribe(subscription, "1", {"broadcaster_user_id": str(user)}, self.subscriptions[subscription])
                    StreamerDatabase(user).add_guild(guildid, subid)
                except EventSubSubscriptionConflict: pass

    async def unsubscribe(self, user, guildid) -> None:
        if self.ttv != None:
            self.del_subscriptions += 1
            strdb = StreamerDatabase(user)
            subids = strdb.get_subids(guildid)
            for subid in subids:
                self.ttv.delete_eventsub_subscription(subid)
            strdb.remove_guild(guildid)

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
                self.hook._subscribe(subscription, "1", {"broadcaster_user_id": str(user)}, self.subscriptions[subscription])
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
