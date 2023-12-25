from Cozyfications import database


class TwitchDatabase:
    def __init__(self, guild_id):
        self.guild_id = guild_id

    def exists(self):
        return database.select(
            f"""SELECT `guild_id`
            FROM `cozyfications`.`twitch`
            WHERE guild_id = '{self.guild_id}'"""
        ).value is not None

    def get_streamers(self):
        return database.select(
            f"""SELECT `streamers`
            FROM `cozyfications`.`twitch`
            WHERE guild_id = '{self.guild_id}'"""
        ).value

    def add_streamer(self, streamer: str):
        streamers = self.get_streamers()
        if not self.exists():
            database.update(
                f"""INSERT INTO `cozyfications`.`twitch` (`guild_id`, `streamers`)
                VALUES ('{self.guild_id}', '[\"{streamer}\"]')"""
            )
        else:
            streamers = [] if streamers is None else streamers
            streamers.append(streamer)
            streamers = str(streamers).replace("'", '"')
            database.update(
                f"""UPDATE `cozyfications`.`twitch`
                SET `streamers` = '{streamers}'
                WHERE (`guild_id` = '{self.guild_id}')"""
            )

    def remove_streamer(self, streamer: str):
        streamers = self.get_streamers()
        streamers.remove(streamer)
        streamers = str(streamers).replace("'", '"')
        if streamers is not None:
            database.update(
                f"""UPDATE `cozyfications`.`twitch`
                SET `streamers` = '{streamers}'
                WHERE (`guild_id` = '{self.guild_id}')"""
            )

    def get_message(self):
        return database.select(
            f"""SELECT `message`
            FROM `cozyfications`.`twitch`
            WHERE guild_id = '{self.guild_id}'"""
        ).value

    def set_message(self, message: str = None):
        if not self.exists():
            database.update(
                f"""INSERT INTO `cozyfications`.`twitch` (`guild_id`, `message`)
                VALUES ('{self.guild_id}', '{message}')"""
            )
        else:
            database.update(
                f"""UPDATE `cozyfications`.`twitch`
                SET `message` = '{message}'
                WHERE (`guil_did` = '{self.guild_id}')"""
            )

    def remove_message(self):
        if self.exists():
            database.update(
                f"""UPDATE `cozyfications`.`twitch`
                SET `message` = '{None}'
                WHERE (`guild_id` = '{self.guild_id}')"""
            )

    def get_channel(self):
        return database.select(
            f"""SELECT `channel`
            FROM `cozyfications`.`twitch`
            WHERE guild_id = '{self.guild_id}'"""
        ).value

    def set_channel(self, channel: int = None):
        if not self.exists():
            database.update(
                f"""INSERT INTO `cozyfications`.`twitch` (`guild_id`, `channel`)
                VALUES ('{self.guild_id}', '{channel}')"""
            )
        else:
            database.update(
                f"""UPDATE `cozyfications`.`twitch`
                SET `channel` = '{channel}'
                WHERE (`guild_id` = '{self.guild_id}')"""
            )

    def remove_channel(self):
        if self.exists():
            database.update(
                f"""UPDATE `cozyfications`.`twitch`
                SET `channel` = '{None}'
                WHERE (`guild_id` = '{self.guild_id}')"""
            )


class StreamerDatabase:
    def __init__(self, streamer):
        self.streamer = streamer

    @staticmethod
    def get_streamers():
        return database.select(
            f"""SELECT `streamer`
            FROM `cozyfications`.`subscriptions`"""
        ).value_all

    def get_subscription_ids(self, guild_id):
        return database.select(
            f"""SELECT `sub_id`
            FROM `cozyfications`.`subscriptions`
            WHERE `streamer` = '{self.streamer}' AND guildid = '{guild_id}'"""
        ).value_all

    def get_guilds(self):
        return database.select(
            f"""SELECT `guild_id`
            FROM `cozyfications`.`subscriptions`
            WHERE `streamer` = '{self.streamer}'"""
        ).value_all

    def add_guild(self, guild_id, subscription_id):
        database.update(
            f"""INSERT INTO `cozyfications`.`subscriptions` (`streamer`, `guild_id`, `subscription_id`)
            VALUES ('{self.streamer}', '{guild_id}', '{subscription_id}')"""
        )

    def remove_guild(self, guild_id):
        database.update(
            f"""DELETE FROM `cozyfications`.`subscriptions`
            WHERE `streamer` = '{self.streamer}' AND guildid = '{guild_id}'"""
        )


class MessageDatabase:
    def __init__(self, guild_id, streamer, channel_id):
        self.guild_id = guild_id
        self.streamer = streamer
        self.channel_id = channel_id

    def get_message(self):
        return database.select(
            f"""SELECT `message_id`
            FROM `cozyfications`.`messages`
            WHERE guild_id = '{self.guild_id}' AND streamer = '{self.streamer}' AND channel_id = '{self.channel_id}'"""
        ).value

    def exists(self) -> bool:
        return self.get_message() is not None

    def create_message(self, message_id):
        if not self.exists():
            return database.update(
                f"""INSERT INTO `cozyfications`.`messages` (`message_id`, `guild_id`, `streamer`, `channel_id`)
                VALUES ('{message_id}', '{self.guild_id}', '{self.streamer}', '{self.channel_id}')"""
            )
        return database.update(
            f"""UPDATE `cozyfications`.`messages`
            SET `message_id` = '{message_id}'
            WHERE (`guild_id` = '{self.guild_id}' AND `streamer` = '{self.streamer}'
            AND `channel_id` = '{self.channel_id}')"""
        )

    def delete_message(self, message_id):
        database.update(
            f"""DELETE FROM `cozyfications`.`messages`
            WHERE `message_id` = '{message_id}' AND `guild_id` = '{self.guild_id}'
            AND `streamer` = '{self.streamer}' AND `channel_id` = '{self.channel_id}'"""
        )
