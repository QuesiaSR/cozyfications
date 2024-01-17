__all__ = (
    "DuplicateSubscription",
    "GuildNotFoundInDatabase",
    "SubscriptionNotFound",
    "TwitchChannelNotFoundInDatabase"
)


class CozyException(Exception):
    def __init__(self, *, message):
        self.args = (message,)


class DatabaseException(CozyException):
    def __init__(self, *, message):
        super().__init__(message=message)


class TwitchException(CozyException):
    def __init__(self, *, message):
        super().__init__(message=message)


class ItemNotFoundInDatabase(DatabaseException):
    def __init__(self, *, item: str):
        message = f"Could not find the requested item in the database: {item}"
        super().__init__(message=message)


class TwitchChannelNotFoundInDatabase(ItemNotFoundInDatabase):
    def __init__(self, *, broadcaster_id: int):
        item = f"Twitch Channel (ID = {broadcaster_id})."
        super().__init__(item=item)


class GuildNotFoundInDatabase(ItemNotFoundInDatabase):
    def __init__(self, *, guild_id: int):
        item = f"Guild (ID = {guild_id})."
        super().__init__(item=item)


class DuplicateSubscription(DatabaseException):
    def __init__(self, *, guild_id: int, broadcaster_id: int):
        message = f"Twitch Channel (ID = {broadcaster_id}) is already subscribed to Guild (ID = {guild_id})."
        super().__init__(message=message)


class SubscriptionNotFound(DatabaseException):
    def __init__(self, *, guild_id: int, broadcaster_id: int):
        message = f"Twitch Channel (ID = {broadcaster_id}) is not subscribed to Guild (ID = {guild_id})."
        super().__init__(message=message)


class TwitchChannelNotFound(TwitchException):
    def __init__(self, *, channel: str):
        message = f"Could not find the requested Twitch channel: {channel}"
        super().__init__(message=message)
