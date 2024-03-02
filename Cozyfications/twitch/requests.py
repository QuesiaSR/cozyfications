from typing import Type

import discord
from twitchAPI import helper
from twitchAPI.object.api import Stream, TwitchUser

from Cozyfications import database, errors
from Cozyfications.database import TwitchChannel
from Cozyfications.twitch.streams import LiveStream, OfflineStream
from Cozyfications.twitch.twitch import Twitch


async def get_broadcaster_id(*, channel: str) -> int:
    """Returns the Twitch channel's broadcaster ID.

    Parameters
    ----------
    channel: str
        The Twitch channel.

    Returns
    ----------
    int
        The Twitch channel's broadcaster ID."""
    async with await Twitch() as twitch:
        try:
            broadcaster_id: int = int((await helper.first(twitch.get_users(logins=[channel]))).id)
        except AttributeError:
            raise errors.TwitchChannelNotFound(channel=channel)
        return broadcaster_id


async def get_channel(*, broadcaster_id: int) -> LiveStream | OfflineStream:
    """Returns the Twitch channel.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel.

    Returns
    ----------
    LiveStream | OfflineStream
        The Twitch channel."""
    async with await Twitch() as twitch:
        stream: Stream = await helper.first(twitch.get_streams(user_id=str(broadcaster_id)))
        streamer: TwitchUser = await helper.first(twitch.get_users(user_ids=[str(broadcaster_id)]))
        if stream:
            thumbnail: str = stream.thumbnail_url.replace("{width}", "1920").replace("{height}", "1080")
            twitch_channel = LiveStream(
                streamer=stream.user_name,
                url=f"https://www.twitch.tv/{stream.user_name}",
                profile_picture=streamer.profile_image_url,
                title=stream.title,
                thumbnail=thumbnail,
                game=stream.game_name,
                viewers=stream.viewer_count,
                started_at=stream.started_at
            )
        else:
            try:
                title = (await database.get_twitch_channel(broadcaster_id=broadcaster_id)).stream_title
            except errors.TwitchChannelNotFoundInDatabase:
                title = "No title available."
            twitch_channel = OfflineStream(
                streamer=streamer.display_name,
                url=f"https://www.twitch.tv/{streamer.display_name}",
                profile_picture=streamer.profile_image_url,
                title=title
            )
        return twitch_channel


# TODO: Use cache to reduce API calls.
async def get_channels_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    """Returns 10 Twitch channels matching the ctx requests.

    Parameters
    ----------
    ctx: discord.AutocompleteContext
        The context used for autocomplete invocation

    Returns
    ----------
    list[str]
        The Twitch channels matching the ctx requests."""
    if ctx.value == "":
        return []
    async with await Twitch() as twitch:
        channels: list[str] = [channel.broadcaster_login async for channel in helper.limit(
            twitch.search_channels(query=ctx.value),
            num=10
        )]
        return channels


async def update_channels() -> None:
    """Updates the Twitch channels in the database."""
    async with await Twitch() as twitch:
        twitch_channels: list[Type[TwitchChannel]] = await database.get_twitch_channels()
        for twitch_channel in twitch_channels:
            stream: Stream = await helper.first(twitch.get_streams(user_id=str(twitch_channel.id)))
            if stream:
                await database.set_twitch_channel(
                    broadcaster_id=twitch_channel.id,
                    streamer=twitch_channel.streamer,
                    live=True,
                    stream_title=stream.title
                )
            else:
                await database.set_twitch_channel(
                    broadcaster_id=twitch_channel.id,
                    streamer=twitch_channel.streamer,
                    live=False,
                    stream_title=twitch_channel.stream_title
                )


async def add_subscription(*, broadcaster_id: int) -> None:
    """Adds an event subscription to a Twitch channel.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel."""
    # TODO: Implement Event Sub: Subscribe
    pass


async def remove_subscription(*, broadcaster_id: int) -> None:
    """Removes an event subscription from a Twitch channel.

    Parameters
    ----------
    broadcaster_id: int
        The ID of the Twitch channel."""
    # TODO: Implement Event Sub: Unsubscribe
    pass
