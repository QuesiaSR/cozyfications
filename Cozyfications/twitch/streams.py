import abc
from dataclasses import dataclass
from datetime import datetime

__all__ = (
    "LiveStream",
    "OfflineStream"
)


@dataclass
class Stream(abc.ABC):
    """Base class for all Twitch streams

    Attributes
    ------------
    streamer: str
        The streamer's username.
    url: str
        The streamer's Twitch URL.
    profile_picture: str
        The streamer's profile picture.
    title: str
        The title of the stream."""
    streamer: str
    url: str
    profile_picture: str
    title: str

    @property
    @abc.abstractmethod
    def live(self) -> bool:
        """Returns whether the stream is live or not.

        Returns
        --------
        bool
            Whether the stream is live or not."""
        pass


@dataclass
class LiveStream(Stream):
    """Dataclass for a live Twitch stream

    Attributes
    ------------
    streamer: str
        The streamer's username.
    url: str
        The streamer's Twitch URL.
    profile_picture: str
        The streamer's profile picture.
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
    thumbnail: str
    game: str
    viewers: int
    started_at: datetime

    @property
    def live(self) -> bool:
        return True


@dataclass
class OfflineStream(Stream):
    """Dataclass for an offline Twitch stream

    Attributes
    ------------
    streamer: str
        The streamer's username.
    url: str
        The streamer's Twitch URL.
    profile_picture: str
        The streamer's profile picture.
    title: str
        The title of the stream."""

    @property
    def live(self) -> bool:
        return False
