from typing import Type

import discord
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from Cozyfications import errors, twitch
from Cozyfications.database.models import Guild, TwitchChannel
from Cozyfications.database.setup import async_session


async def get_guild(*, guild_id: int) -> Guild:
    """Returns the guild from the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.

    Returns
    ----------
    Guild
        The guild from the database."""
    async with async_session() as session:
        guild = (await session.execute(select(Guild).filter(Guild.id == guild_id))).scalar_one_or_none()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        return guild


async def set_guild(*, guild_id: int, channel_id: int, message_id: int) -> None:
    """Sets the channel ID and message ID of the guild.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.
    channel_id: int
        The ID of the channel.
    message_id: int
        The ID of the message."""
    async with async_session() as session:
        guild = (await session.execute(select(Guild).filter(Guild.id == guild_id))).scalar_one_or_none()
        if guild:
            guild.channel_id = channel_id
            guild.message_id = message_id
        else:
            session.add(Guild(id=guild_id, channel_id=channel_id, message_id=message_id))
        await session.commit()


async def delete_guild(*, guild_id: int) -> None:
    """Deletes the guild from the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild."""
    async with async_session() as session:
        guild = (await session.execute(select(Guild).filter(Guild.id == guild_id))).scalar_one_or_none()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        await session.delete(guild)
        await session.commit()


async def get_twitch_channel(*, broadcaster_id: int) -> TwitchChannel:
    """Returns the Twitch channel from the database.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.

    Returns
    ----------
    TwitchChannel
        The Twitch channel from the database."""
    async with async_session() as session:
        twitch_channel = (
            await session.execute(select(TwitchChannel).filter(TwitchChannel.id == broadcaster_id))
        ).scalar_one_or_none()
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        return twitch_channel


async def set_twitch_channel(*, broadcaster_id: int, streamer: str, live: bool, stream_title: str) -> None:
    """Sets the Twitch channel's live status and stream title.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.
    streamer: str
        The name of the Twitch channel.
    live: bool
        The Twitch channel's live status.
    stream_title: str
        The Twitch channel's stream title."""
    async with async_session() as session:
        twitch_channel = (
            await session.execute(select(TwitchChannel).filter(TwitchChannel.id == broadcaster_id))
        ).scalar_one_or_none()
        if twitch_channel:
            twitch_channel.streamer = streamer
            twitch_channel.live = live
            twitch_channel.stream_title = stream_title
        else:
            session.add(TwitchChannel(id=broadcaster_id, streamer=streamer, live=live, stream_title=stream_title))
            await twitch.add_subscription(broadcaster_id=broadcaster_id)
        await session.commit()


async def delete_twitch_channel(*, broadcaster_id: int) -> None:
    """Deletes the Twitch channel from the database.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel."""
    async with async_session() as session:
        twitch_channel = (
            await session.execute(select(TwitchChannel).filter(TwitchChannel.id == broadcaster_id))
        ).scalar_one_or_none()
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        await session.delete(twitch_channel)
        await twitch.remove_subscription(broadcaster_id=broadcaster_id)
        await session.commit()


async def get_twitch_channels() -> list[Type[TwitchChannel]]:
    """Returns a list of all Twitch channels.

    Returns
    ----------
    list[Type[TwitchChannel]]
        A list of Twitch channels."""
    async with async_session() as session:
        channels: list[Type[TwitchChannel]] = (await session.execute(select(TwitchChannel))).scalars().all()
        return channels


async def add_subscription(*, guild_id: int, broadcaster_id: int) -> None:
    """Adds a Twitch channel subscription to the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.
    broadcaster_id: int
        The ID of the Twitch channel."""
    async with async_session() as session:
        guild = (await session.execute(select(Guild).options(
            joinedload(Guild.subscribed_channels)
        ).filter(Guild.id == guild_id))).unique().scalar_one_or_none()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        twitch_channel = (
            await session.execute(select(TwitchChannel).filter(TwitchChannel.id == broadcaster_id))
        ).scalar_one_or_none()
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        if twitch_channel in guild.subscribed_channels:
            raise errors.DuplicateSubscription(guild_id=guild_id, broadcaster_id=broadcaster_id)
        guild.subscribed_channels.append(twitch_channel)
        await session.commit()


async def remove_subscription(*, guild_id: int, broadcaster_id: int) -> None:
    """Removes a Twitch channel subscription from the database.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.
    broadcaster_id: int
        The ID of the Twitch channel."""
    async with async_session() as session:
        guild = (await session.execute(select(Guild).options(
            joinedload(Guild.subscribed_channels)
        ).filter(Guild.id == guild_id))).unique().scalar_one_or_none()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        twitch_channel = (
            await session.execute(select(TwitchChannel).filter(TwitchChannel.id == broadcaster_id))
        ).scalar_one_or_none()
        if not twitch_channel:
            raise errors.TwitchChannelNotFoundInDatabase(broadcaster_id=broadcaster_id)
        if twitch_channel not in guild.subscribed_channels:
            raise errors.SubscriptionNotFound(guild_id=guild_id, broadcaster_id=broadcaster_id)
        guild.subscribed_channels.remove(twitch_channel)
        subscribed_guilds = (
            await session.execute(select(Guild).filter(Guild.subscribed_channels.any(id=broadcaster_id)))
        ).scalars().all()
        if len(subscribed_guilds) == 0:
            await session.delete(twitch_channel)
        await session.commit()


async def get_subscribed_guilds(*, broadcaster_id) -> list[Type[Guild]]:
    """Returns a list of guilds that have subscribed to a Twitch channel.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.

    Returns
    ----------
    list[Type[Guild]] | None
        A list of guilds that have subscribed to a Twitch channel."""
    async with async_session() as session:
        guilds: list[Type[Guild]] = (
            await session.execute(select(Guild).filter(Guild.subscribed_channels.any(id=broadcaster_id)))
        ).scalars().all()
        return guilds


async def get_subscribed_channels(*, guild_id: int) -> list[Type[TwitchChannel]]:
    """Returns a list of Twitch channels that a guild has subscribed to.

    Parameters
    ----------
    guild_id: int
        The ID of the guild.

    Returns
    ----------
    list[Type[TwitchChannel]] | None
        A list of Twitch channels that a guild has subscribed to."""
    async with async_session() as session:
        guild: Guild | None = (await session.execute(select(Guild).options(
            joinedload(Guild.subscribed_channels)
        ).filter(Guild.id == guild_id))).unique().scalar_one_or_none()
        if not guild:
            raise errors.GuildNotFoundInDatabase(guild_id=guild_id)
        channels: list[Type[TwitchChannel]] = guild.subscribed_channels
        return channels


# TODO: Use cache to reduce database calls.
async def get_subscribed_channels_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    """Returns the Twitch channels matching the ctx requests.

    Parameters
    ----------
    ctx: discord.AutocompleteContext
        The context used for autocomplete invocation

    Returns
    ----------
    list[str]
        The Twitch channels matching the ctx requests."""
    async with async_session() as session:
        guild: Guild | None = (await session.execute(select(Guild).options(
            joinedload(Guild.subscribed_channels)
        ).filter(Guild.id == ctx.interaction.guild_id))).unique().scalar_one_or_none()
        if not guild:
            return []
        channels: list[str] = [channel.streamer for channel in guild.subscribed_channels]
        return channels
