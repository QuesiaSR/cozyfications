import discord

from Cozyfications.database.classes import StreamerDatabase, TwitchDatabase, MessageDatabase
from bot import Cozyfications


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

        async def callback(data, bot: discord.Bot):
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

        async def callback(data, bot: Cozyfications):
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

        async def callback(data, bot: Cozyfications):
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
                        except discord.NotFound | discord.Forbidden | discord.HTTPException:
                            pass
                    await channel.send(message)

        Cozyfications.QUEUE.append({"data": data, "callback": callback})
