from Cozyfications import database

class TwitchDatabase:
    def __init__(self, guildid):
        self.guildid = guildid
    
    def exists(self): return database.select(f"SELECT `guildid` FROM `cozyfications`.`twitch` WHERE guildid = '{self.guildid}'").value != None

    def get_streamers(self): return database.select(f"SELECT `streamers` FROM `cozyfications`.`twitch` WHERE guildid = '{self.guildid}'").value
    def add_streamer(self, streamer: str):
        streamers = self.get_streamers()
        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `streamers`) VALUES ('{self.guildid}', '[\"{streamer}\"]')")
        else:
            streamers.append(streamer)
            streamers = str(streamers).replace("'", '"')
            database.update(f"UPDATE `cozyfications`.`twitch` SET `streamers` = '{streamers}' WHERE (`guildid` = '{self.guildid}')")
    def remove_streamer(self, streamer: str):
        streamers = self.get_streamers()
        streamers.remove(streamer)
        streamers = str(streamers).replace("'", '"')
        if streamers != None: database.update(f"UPDATE `cozyfications`.`twitch` SET `streamers` = '{streamers}' WHERE (`guildid` = '{self.guildid}')")
    
    def get_messages(self): return database.select(f"SELECT `messages` FROM `cozyfications`.`twitch` WHERE guildid = '{self.guildid}'").value
    def set_messages(self, live_message: str=None, clip_message: str=None):
        messages = self.get_messages()
        obj = {}
        if not messages == None: obj = messages
        if not live_message == None: obj["live"] = live_message
        if not clip_message == None: obj["clip"] = clip_message
        obj = str(obj).replace("'", '"')

        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `messages`) VALUES ('{self.guildid}', '{obj}')")
        else: database.update(f"UPDATE `cozyfications`.`twitch` SET `messages` = '{obj}' WHERE (`guildid` = '{self.guildid}')")
    def remove_messages(self, live_message: bool=False, clip_message: bool=False):
        messages = self.get_messages()
        obj = {}
        if not messages == None: obj = messages
        if live_message and not obj.get("live") == None: obj.pop("live")
        if clip_message and not obj.get("clip") == None: obj.pop("clip")
        obj = str(obj).replace("'", '"')
        
        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `messages`) VALUES ('{self.guildid}', '{obj}')")
        else: database.update(f"UPDATE `cozyfications`.`twitch` SET `messages` = '{obj}' WHERE (`guildid` = '{self.guildid}')")
    
    def get_channels(self): return database.select(f"SELECT `channels` FROM `cozyfications`.`twitch` WHERE guildid = '{self.guildid}'").value
    def set_channels(self, live_channel: str=None, clip_channel: str=None):
        channels = self.get_channels()
        obj = {}
        if not channels == None: obj = channels
        if not live_channel == None: obj["live"] = live_channel
        if not clip_channel == None: obj["clip"] = clip_channel
        obj = str(obj).replace("'", '"')

        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `channels`) VALUES ('{self.guildid}', '{obj}')")
        else: database.update(f"UPDATE `cozyfications`.`twitch` SET `channels` = '{obj}' WHERE (`guildid` = '{self.guildid}')")
    def remove_channels(self, live_channel: bool=False, clip_channel: bool=False):
        channels = self.get_channels()
        obj = {}
        if not channels == None: obj = channels
        if live_channel and not obj.get("live") == None: obj.pop("live")
        if clip_channel and not obj.get("clip") == None: obj.pop("clip")
        obj = str(obj).replace("'", '"')

        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `channels`) VALUES ('{self.guildid}', '{obj}')")
        else: database.update(f"UPDATE `cozyfications`.`twitch` SET `channels` = '{obj}' WHERE (`guildid` = '{self.guildid}')")

class StreamerDatabase:
    def __init__(self, streamer):
        self.streamer = streamer
    
    def get_streamers(self): return database.select(f"SELECT `streamer` FROM `cozyfications`.`subscriptions`").value_all
    def get_subids(self, guildid): return database.select(f"SELECT `subid` FROM `cozyfications`.`subscriptions` WHERE `streamer` = '{self.streamer}' AND guildid = '{guildid}'").value_all
    def get_guilds(self): return database.select(f"SELECT `guildid` FROM `cozyfications`.`subscriptions` WHERE `streamer` = '{self.streamer}'").value_all

    def add_guild(self, guildid, subid): database.update(f"INSERT INTO `cozyfications`.`subscriptions` (`streamer`, `guildid`, `subid`) VALUES ('{self.streamer}', '{guildid}', '{subid}')")
    def remove_guild(self, guildid): database.update(f"DELETE FROM `cozyfications`.`subscriptions` WHERE `streamer` = '{self.streamer}' AND guildid = '{guildid}'")

class MessageDatabase:
    def __init__(self, guildid, streamer, channelid):
        self.guildid = guildid
        self.streamer = streamer
        self.channelid = channelid
    
    def get_message(self): return database.select(f"SELECT `message` FROM `cozyfications`.`messages` WHERE guildid = '{self.guildid}' AND streamer = '{self.streamer}' AND channelid = '{self.channelid}'").value
    def create_message(self, messageid): database.update(f"INSERT INTO `cozyfications`.`messages` (`messageid`, `guildid`, `streamer`, `channelid`) VALUES ('{messageid}', '{self.guildid}', '{self.streamer}', '{self.channelid}'")
    def delete_message(self, messageid): database.update(f"DELETE FROM `cozyfications`.`messages` WHERE messageid = `{messageid}` AND guildid = `{self.guildid}` AND streamer = '{self.streamer}' AND channelid = '{self.channelid}'")
