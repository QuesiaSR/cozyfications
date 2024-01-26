from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

__all__ = (
    "Base",
    "Guild",
    "TwitchChannel"
)

# TODO: Make DB async


class Base(sqlalchemy.orm.DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


subscriptions_table = Table(
    "subscriptions",
    Base.metadata,
    Column(
        "guild_id",
        ForeignKey("guilds.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "broadcaster_id",
        ForeignKey("twitch_channels.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Guild(Base):
    """DB class for guilds.

    Attributes
    ----------
    id: int
        The ID of the guild.
    channel_id: int
        The ID of the channel where the Cozyfication message is sent.
    message_id: int
        The ID of the Cozyfication message.
    subscribed_channels: List[TwitchChannel]
        The Twitch channels that the guild has subscribed to."""
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(nullable=False)
    message_id: Mapped[int] = mapped_column(nullable=False)
    subscribed_channels: Mapped[List["TwitchChannel"]] = relationship(
        secondary=subscriptions_table,
        back_populates="guilds"
    )

    def __repr__(self) -> str:
        """Returns a string representation of the guild.

        Returns
        -------
        str
            A string representation of the guild."""
        try:
            subscribed_channels = self.subscribed_channels
        except sqlalchemy.orm.exc.DetachedInstanceError:
            subscribed_channels = "<not loaded>"
        return f"""Guild:
    id={self.id}, 
    channel_id={self.channel_id}, 
    message_id={self.message_id}, 
    subscribed_channels={subscribed_channels}"""


class TwitchChannel(Base):
    """DB class for Twitch channels.

    Attributes
    ----------
    id: int
        The ID of the Twitch channel.
    streamer: str
        The Twitch channel's username.
    live: bool
        Whether the Twitch channel is live.
    stream_title: str
        The title of the Twitch channel's stream.
    guilds: List[Guild]
        The guilds that have subscribed to the Twitch channel."""
    __tablename__ = "twitch_channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    streamer: Mapped[str] = mapped_column(nullable=False)
    live: Mapped[bool] = mapped_column(nullable=False)
    stream_title: Mapped[str] = mapped_column(nullable=False)
    guilds: Mapped[List["Guild"]] = relationship(
        secondary=subscriptions_table,
        back_populates="subscribed_channels"
    )

    def __repr__(self) -> str:
        """Returns a string representation of the Twitch channel.

        Returns
        -------
        str
            A string representation of the Twitch channel."""
        try:
            guilds = self.guilds
        except sqlalchemy.orm.exc.DetachedInstanceError:
            guilds = "<not loaded>"
        return f"""TwitchChannel:
    streamer={self.streamer},
    id={self.id},
    live={self.live},
    stream_title={self.stream_title}
    guilds={guilds}"""
