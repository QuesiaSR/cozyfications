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
            streamers = [] if streamers is None else streamers
            streamers.append(streamer)
            streamers = str(streamers).replace("'", '"')
            database.update(f"UPDATE `cozyfications`.`twitch` SET `streamers` = '{streamers}' WHERE (`guildid` = '{self.guildid}')")
    def remove_streamer(self, streamer: str):
        streamers = self.get_streamers()
        streamers.remove(streamer)
        streamers = str(streamers).replace("'", '"')
        if streamers != None: database.update(f"UPDATE `cozyfications`.`twitch` SET `streamers` = '{streamers}' WHERE (`guildid` = '{self.guildid}')")
    
    def get_message(self): return database.select(f"SELECT `message` FROM `cozyfications`.`twitch` WHERE guildid = '{self.guildid}'").value
    def set_message(self, message: str=None):
        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `message`) VALUES ('{self.guildid}', '{message}')")
        else: database.update(f"UPDATE `cozyfications`.`twitch` SET `message` = '{message}' WHERE (`guildid` = '{self.guildid}')")
    def remove_message(self):
        if self.exists():
            database.update(f"UPDATE `cozyfications`.`twitch` SET `message` = '{None}' WHERE (`guildid` = '{self.guildid}')")
    
    def get_channel(self): return database.select(f"SELECT `channel` FROM `cozyfications`.`twitch` WHERE guildid = '{self.guildid}'").value
    def set_channel(self, channel: int=None):
        if not self.exists(): database.update(f"INSERT INTO `cozyfications`.`twitch` (`guildid`, `channel`) VALUES ('{self.guildid}', '{channel}')")
        else: database.update(f"UPDATE `cozyfications`.`twitch` SET `channel` = '{channel}' WHERE (`guildid` = '{self.guildid}')")
    def remove_channel(self):
        if self.exists():
            database.update(f"UPDATE `cozyfications`.`twitch` SET `channel` = '{None}' WHERE (`guildid` = '{self.guildid}')")

class StreamerDatabase:
    def __init__(self, streamer):
        self.streamer = streamer
    
    @staticmethod
    def get_streamers(): return database.select(f"SELECT `streamer` FROM `cozyfications`.`subscriptions`").value_all
    
    def get_subids(self, guildid): return database.select(f"SELECT `subid` FROM `cozyfications`.`subscriptions` WHERE `streamer` = '{self.streamer}' AND guildid = '{guildid}'").value_all
    def get_guilds(self): return database.select(f"SELECT `guildid` FROM `cozyfications`.`subscriptions` WHERE `streamer` = '{self.streamer}'").value_all

    def add_guild(self, guildid, subid): database.update(f"INSERT INTO `cozyfications`.`subscriptions` (`streamer`, `guildid`, `subid`) VALUES ('{self.streamer}', '{guildid}', '{subid}')")
    def remove_guild(self, guildid): database.update(f"DELETE FROM `cozyfications`.`subscriptions` WHERE `streamer` = '{self.streamer}' AND guildid = '{guildid}'")

class MessageDatabase:
    def __init__(self, guildid, streamer, channelid):
        self.guildid = guildid
        self.streamer = streamer
        self.channelid = channelid
    
    def get_message(self): return database.select(f"SELECT `messageid` FROM `cozyfications`.`messages` WHERE guildid = '{self.guildid}' AND streamer = '{self.streamer}' AND channelid = '{self.channelid}'").value
    def exists(self) -> bool: return self.get_message() != None
    def create_message(self, messageid):
        if not self.exists():
            return database.update(f"INSERT INTO `cozyfications`.`messages` (`messageid`, `guildid`, `streamer`, `channelid`) VALUES ('{messageid}', '{self.guildid}', '{self.streamer}', '{self.channelid}')")
        return database.update(f"UPDATE `cozyfications`.`messages` SET `messageid` = '{messageid}' WHERE (`guildid` = '{self.guildid}' and `streamer` = '{self.streamer}' and `channelid` = '{self.channelid}')")
    def delete_message(self, messageid): database.update(f"DELETE FROM `cozyfications`.`messages` WHERE `messageid` = '{messageid}' AND `guildid` = '{self.guildid}' AND `streamer` = '{self.streamer}' AND `channelid` = '{self.channelid}'")
