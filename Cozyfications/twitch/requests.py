from twitchAPI import helper
from twitchAPI.object.api import Stream, TwitchUser

from Cozyfications import database, errors
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
        if stream:
            twitch_channel = LiveStream(
                streamer=stream.user_name,
                url=f"https://www.twitch.tv/{stream.user_name}",
                profile_picture=stream.thumbnail_url,
                title=stream.title,
                thumbnail=stream.thumbnail_url,
                game=stream.game_name,
                viewers=stream.viewer_count,
                started_at=stream.started_at
            )
        else:
            streamer: TwitchUser = await helper.first(twitch.get_users(user_ids=[str(broadcaster_id)]))
            try:
                title = database.get_twitch_channel(broadcaster_id=broadcaster_id).stream_title
            except errors.TwitchChannelNotFoundInDatabase:
                title = "No title available."
            twitch_channel = OfflineStream(
                streamer=streamer.display_name,
                url=f"https://www.twitch.tv/{streamer}",
                profile_picture=streamer.profile_image_url,
                title=title
            )
        return twitch_channel


async def update_channels() -> None:
    """Updates the Twitch channels in the database."""
    async with await Twitch() as twitch:
        twitch_channels = database.get_channels()
        if twitch_channels is None:
            return
        for twitch_channel in database.get_channels():
            stream: Stream = await helper.first(twitch.get_streams(user_id=str(twitch_channel.id)))
            if stream:
                database.set_twitch_channel(
                    broadcaster_id=twitch_channel.id,
                    live=True,
                    stream_title=stream.title
                )
            else:
                database.set_twitch_channel(
                    broadcaster_id=twitch_channel.id,
                    live=False,
                    stream_title=twitch_channel.stream_title
                )
