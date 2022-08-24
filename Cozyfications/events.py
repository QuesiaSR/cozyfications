from twitchAPI import EventSub, Twitch as TwitchAPI
from Cozyfications.secrets import Twitch
from Cozyfications.database.classes import MessageDatabase, StreamerDatabase, TwitchDatabase
from Cozyfications.bot import main

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
        guilds = await Callbacks.get_guilds(data)
        print("update")

        for guild in guilds:
            guild: TwitchDatabase
            channels = guild.get_channels()

            if channels != None:
                msgdb = MessageDatabase(guild.guildid, data["subscription"]["condition"]["broadcaster_user_id"], channels["live"])
                msgid = msgdb.get_message()

                if msgid != None:
                    msg = main.INSTANCE.get_message(msgid)

                    if msg != None:
                        await msg.edit("Edited")

    async def online(data):
        guilds = await Callbacks.get_guilds(data)

        for guild in guilds:
            guild: TwitchDatabase
            channels = guild.get_channels()
            messages = guild.get_messages()

            if channels != None and channels["live"] != None:
                channel = channels["live"]
                message = "Offline."
                if messages != None and messages["live"] != None:
                    message = messages["live"]

                await main.INSTANCE.get_channel(channel).send(message)
                
    async def offline(data):
        guilds = await Callbacks.get_guilds(data)

        for guild in guilds:
            guild: TwitchDatabase
            channels = guild.get_channels()
            messages = guild.get_messages()

            if channels != None and messages != None:
                channel = channels["live"]

                await main.INSTANCE.get_channel(channel).send("Offline")

subscriptions = {
    "channel.update": Callbacks.update,
    "stream.online": Callbacks.online,
    "stream.offline": Callbacks.offline
}

class Globals:
    HOOK: EventSub = None
    TTV: TwitchAPI = None
    NEW_SUBSCRIPTIONS = 0
    DEL_SUBSCRIPTIONS = 0

def subscribe(user, guildid):
    if Globals.HOOK != None:
        Globals.NEW_SUBSCRIPTIONS += 1
        for subscription in subscriptions:
            subid = Globals.HOOK._subscribe(subscription, "1", {"broadcaster_user_id": str(user)}, subscriptions[subscription])
            StreamerDatabase(user).add_guild(guildid, subid)

def unsubscribe(user, guildid):
    if Globals.TTV != None:
        Globals.DEL_SUBSCRIPTIONS += 1
        strdb = StreamerDatabase(user)
        subids = strdb.get_subids(guildid)
        for subid in subids:
            Globals.TTV.delete_eventsub_subscription(subid)
        strdb.remove_guild(guildid)

def run_event_hook(url):
    print("Starting event hook...")
    twitch = TwitchAPI(Twitch.ID, Twitch.SECRET)
    twitch.authenticate_app([])

    hook = EventSub(url, Twitch.ID, 6001, twitch)
    (hook.unsubscribe_all(), print("  Unsubscribed from all events"))
    (hook.start(), print("  Started event hook"))

    print("Subscribing to events...")
    print("  Fetching users")
    users = StreamerDatabase("").get_streamers()
    
    for user in users:
        for subscription in subscriptions:
            hook._subscribe(subscription, "1", {"broadcaster_user_id": str(user)}, subscriptions[subscription])

            if user == users[len(users) - 1]:
                print(f"  Finished subscribing to '{subscription}' for all users")
    Globals.HOOK = hook
    Globals.TTV = twitch

def close_event_hook():
    Globals.HOOK.stop()
