from typing import Type

from sqlalchemy.orm import Session

from Cozyfications import errors
from Cozyfications.database.engine import engine
from Cozyfications.database.models import Guild, TwitchChannel


def get_guild(*, guild_id: int) -> Guild:
    """Returns the guild from the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.

    Returns
    ----------
    Guild
        The guild from the database."""
    with Session(bind=engine) as session:
        guild: Guild | None = session.query(Guild).filter_by(id=guild_id).first()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        return guild


def set_guild(*, guild_id: int, channel_id: int | None, message_id: int | None) -> None:
    """Sets the channel ID and message ID of the guild.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.
    channel_id: int
        The ID of the channel.
    message_id: int
        The ID of the message."""
    with Session(bind=engine) as session:
        if session.query(Guild).filter_by(id=guild_id).first():
            session.query(Guild).filter_by(id=guild_id).update({
                Guild.channel_id: channel_id,
                Guild.message_id: message_id
            })
        else:
            session.add(Guild(id=guild_id, channel_id=channel_id, message_id=message_id))
        session.commit()


def delete_guild(*, guild_id: int) -> None:
    """Deletes the guild from the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild."""
    with Session(bind=engine) as session:
        if not session.query(Guild).filter_by(id=guild_id).first():
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        session.query(Guild).filter_by(id=guild_id).delete()
        session.commit()


def get_twitch_channel(*, broadcaster_id: int) -> TwitchChannel:
    """Returns the Twitch channel from the database.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.

    Returns
    ----------
    TwitchChannel
        The Twitch channel from the database."""
    with Session(bind=engine) as session:
        twitch_channel: TwitchChannel | None = session.query(TwitchChannel).filter_by(id=broadcaster_id).first()
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        return twitch_channel


def set_twitch_channel(*, broadcaster_id: int, live: bool, stream_title: str) -> None:
    """Sets the Twitch channel's live status and stream title.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.
    live: bool
        The Twitch channel's live status.
    stream_title: str
        The Twitch channel's stream title."""
    with Session(bind=engine) as session:
        if session.query(TwitchChannel).filter_by(id=broadcaster_id).first():
            session.query(TwitchChannel).filter_by(id=broadcaster_id).update({
                TwitchChannel.live: live,
                TwitchChannel.stream_title: stream_title
            })
        else:
            session.add(TwitchChannel(id=broadcaster_id, live=live, stream_title=stream_title))
        session.commit()


def delete_twitch_channel(*, broadcaster_id: int) -> None:
    """Deletes the Twitch channel from the database.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel."""
    with Session(bind=engine) as session:
        if not session.query(TwitchChannel).filter_by(id=broadcaster_id).first():
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        session.query(TwitchChannel).filter_by(id=broadcaster_id).delete()
        session.commit()


def add_subscription(*, guild_id: int, broadcaster_id: int) -> None:
    """Adds a Twitch channel subscription to the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.
    broadcaster_id: int
        The ID of the Twitch channel."""
    with Session(bind=engine) as session:
        guild: Guild | None = session.query(Guild).filter_by(id=guild_id).first()
        twitch_channel = session.query(TwitchChannel).filter_by(id=broadcaster_id).first()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        if twitch_channel in guild.subscribed_channels:
            raise errors.DuplicateSubscription(guild_id=guild_id, broadcaster_id=broadcaster_id)
        guild.subscribed_channels.append(twitch_channel)
        session.commit()


def remove_subscription(*, guild_id: int, broadcaster_id: int) -> None:
    """Removes a Twitch channel subscription from the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.
    broadcaster_id: int
        The ID of the Twitch channel."""
    with Session(bind=engine) as session:
        guild: Guild | None = session.query(Guild).filter_by(id=guild_id).first()
        twitch_channel = session.query(TwitchChannel).filter_by(id=broadcaster_id).first()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        if twitch_channel not in guild.subscribed_channels:
            raise errors.SubscriptionNotFound(guild_id=guild_id, broadcaster_id=broadcaster_id)
        guild.subscribed_channels.remove(twitch_channel)
        subscribed_guilds = session.query(Guild).filter(Guild.subscribed_channels.any(id=broadcaster_id)).all()
        if len(subscribed_guilds) == 0:
            session.query(TwitchChannel).filter_by(id=broadcaster_id).delete()
        session.commit()


def get_channels() -> list[Type[TwitchChannel]] | None:
    """Returns a list of Twitch channels.

    Returns
    ----------
    list[Type[TwitchChannel]] | None
        A list of Twitch channels."""
    with Session(bind=engine) as session:
        channels: list[Type[TwitchChannel]] = session.query(TwitchChannel).all()
        if len(channels) == 0:
            return None
        return channels


def get_live_twitch_channels() -> list[Type[TwitchChannel]] | None:
    """Returns a list of Twitch channels that are live.

    Returns
    ----------
    list[Type[TwitchChannel]] | None
        A list of Twitch channels that are live."""
    with Session(bind=engine) as session:
        live_channels: list[Type[TwitchChannel]] = session.query(TwitchChannel).filter_by(live=True).all()
        if len(live_channels) == 0:
            return None
        return live_channels


def get_subscribed_guilds(*, broadcaster_id) -> list[Type[Guild]] | None:
    """Returns a list of guilds that have subscribed to a Twitch channel.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.

    Returns
    ----------
    list[Type[Guild]] | None
        A list of guilds that have subscribed to a Twitch channel."""
    with Session(bind=engine) as session:
        guilds: list[Type[Guild]] = session.query(Guild).filter(Guild.subscribed_channels.any(id=broadcaster_id)).all()
        if len(guilds) == 0:
            return None
        return guilds
