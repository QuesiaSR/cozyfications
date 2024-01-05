from dataclasses import dataclass
from datetime import datetime

__all__ = (
    "LiveStream",
    "OfflineStream"
)


@dataclass
class Channel:
    """Base class for all Twitch streams

    Attributes
    ------------
    streamer: str
        The streamer's username.
    url: str
        The streamer's Twitch URL.
    profile_picture: str
        The streamer's profile picture."""
    streamer: str
    url: str
    profile_picture: str


@dataclass
class LiveStream(Channel):
    """Dataclass for a live Twitch stream

    Attributes
    ------------
    title: str
        The title of the stream.
    thumbnail: str
        The thumbnail of the stream.
    game: str
        The game being played in the stream.
    viewers: int
        The number of viewers watching the stream.
    started_at: datetime
        The time the stream started at."""
    title: str
    thumbnail: str
    game: str
    viewers: int
    started_at: datetime


@dataclass
class OfflineStream(Channel):
    """Dataclass for an offline Twitch stream

    Attributes
    ------------
    last_title: str
        The title of the last stream."""
    last_title: str
