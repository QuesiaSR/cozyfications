import datetime
from typing import Type, List

import discord

from Cozyfications import twitch, database
from Cozyfications.bot.core.__init__ import Cog
from Cozyfications.bot.core.bot import Cozyfications


class Embed(discord.Embed):
    """Represents a custom PyCord embed with the current timestamp.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
        Must be 256 characters or fewer.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
        Must be 4096 characters or fewer.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation.
    colour: Union[:class:`Colour`, :class:`int`]
        The colour code of the embed. Aliased to ``color`` as well.
        This can be set during initialisation."""

    def __init__(self, **kwargs) -> None:
        """Initialises a new embed.

        Parameters
        ----------
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.timestamp: datetime.datetime = discord.utils.utcnow()


class GreenEmbed(Embed):
    """Represents a custom PyCord embed with the current timestamp and green color.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
        Must be 256 characters or fewer.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
        Must be 4096 characters or fewer.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation."""

    def __init__(self, **kwargs) -> None:
        """Initialises a new green embed.

        Parameters
        ----------
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.color: discord.Color = discord.Color.green()


class YellowEmbed(Embed):
    """Represents a custom PyCord embed with the current timestamp and yellow color.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
        Must be 256 characters or fewer.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
        Must be 4096 characters or fewer.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation."""

    def __init__(self, **kwargs) -> None:
        """Initialises a new yellow embed.

        Parameters
        ----------
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.color: discord.Color = discord.Color.yellow()


class RedEmbed(Embed):
    """Represents a custom PyCord embed with the current timestamp and red color.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
        Must be 256 characters or fewer.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
        Must be 4096 characters or fewer.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation."""

    def __init__(self, **kwargs) -> None:
        """Initialises a new red embed.

        Parameters
        ----------
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.color: discord.Color = discord.Color.red()


class CozyficationsEmbed(Embed):
    """Represents a custom PyCord embed with the current timestamp.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.
    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
        Must be 256 characters or fewer.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
        Must be 4096 characters or fewer.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation."""

    def __init__(self, *, bot: Cozyfications, **kwargs) -> None:
        """Initialises a new Cozyfications embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.color: discord.Color = bot.color


class HelpEmbed(CozyficationsEmbed):
    """Represents a custom PyCord help embed."""

    def __init__(self, *, bot: Cozyfications, **kwargs) -> None:
        """Initialises a new help embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        **kwargs: Any"""
        super().__init__(bot=bot, **kwargs)
        self.title: str = bot.user.name
        self.description: str = "Use the menu below to view commands."
        self.set_thumbnail(url=bot.user.display_avatar.url)
        self.add_field(name="Server Count:", value=str(len(bot.guilds)))
        self.add_field(name="User Count:", value=str(len(bot.users)))
        self.add_field(name="Ping:", value=f"{bot.latency * 1000:.2f} ms")


class HelpSelectEmbed(CozyficationsEmbed):
    """Represents a custom PyCord help select embed."""

    def __init__(self, *, bot: Cozyfications, cog: Cog, **kwargs) -> None:
        """Initialises a new help select embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        cog: :class:`Cog`
            The cog to get the commands from.
        **kwargs: Any"""
        super().__init__(bot=bot, **kwargs)
        self.title: str = f"{cog.__cog_name__} Commands"
        self.description: str = "\n".join(
            f"</{command.qualified_name}:{command.qualified_id}> - {command.description}"
            for command in cog.walk_commands()
        )


class BugReportEmbed(YellowEmbed):
    """Represents a custom PyCord bug report embed."""

    def __init__(self, *, bug_name: str, bug_description: str, steps_to_reproduce: str | None,
                 author: discord.Member | discord.User, **kwargs) -> None:
        """Initialises a new bug report embed.

        Parameters
        ----------
        bug_name: :class:`str`
            The name of the bug.
        bug_description: :class:`str`
            The description of the bug.
        steps_to_reproduce: Optional[:class:`str`]
            The steps to reproduce the bug.
        author: Union[:class:`discord.Member`, :class:`discord.User`]
            The author of the bug report.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = f"Bug Report: {bug_name}"
        self.description: str = bug_description
        if steps_to_reproduce:
            self.add_field(name="Steps to Reproduce:", value=steps_to_reproduce, inline=False)
        self.set_author(name=author.display_name, icon_url=author.display_avatar.url)


class FeatureRequestEmbed(YellowEmbed):
    """Represents a custom PyCord feature request embed."""

    def __init__(self, *, feature_name: str, feature_description: str, author: discord.Member | discord.User,
                 **kwargs) -> None:
        """Initialises a new feature request embed.

        Parameters
        ----------
        feature_name: :class:`str`
            The name of the feature.
        feature_description: :class:`str`
            The description of the feature.
        author: Union[:class:`discord.Member`, :class:`discord.User`]
            The author of the feature request.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = f"Feature Request: {feature_name}"
        self.description: str = feature_description
        self.set_author(name=author.display_name, icon_url=author.display_avatar.url)


class NotificationEmbed(CozyficationsEmbed):
    """Represents a custom PyCord notification embed."""

    def __init__(self, *, bot: Cozyfications, **kwargs) -> None:
        """Initialises a new notification embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        **kwargs: Any"""
        super().__init__(bot=bot, **kwargs)
        self.title: str = "Live Stream Notifications"
        self.description: str = "This message will be edited when a stream goes live!"
        self.set_thumbnail(url=bot.user.display_avatar.url)


class LiveStreamEmbed(CozyficationsEmbed):
    """Represents a custom PyCord live stream embed."""

    def __init__(self, *, bot: Cozyfications, stream: twitch.LiveStream, **kwargs) -> None:
        """Initialises a new live stream embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        stream: :class:`LiveStream`
            The live stream instance.
        **kwargs: Any"""
        super().__init__(bot=bot, **kwargs)
        self.title: str = f"{stream.streamer} is LIVE!"
        self.url: str = stream.url
        self.set_thumbnail(url=stream.profile_picture)
        self.set_image(url=f"{stream.thumbnail}?t={datetime.datetime.utcnow().timestamp()}")
        self.add_field(name="Stream Title:", value=stream.title, inline=False)
        self.add_field(name="Game:", value=stream.game, inline=True)
        self.add_field(name="Viewers:", value=str(stream.viewers), inline=True)
        self.add_field(name="Live Since:", value=discord.utils.format_dt(stream.started_at, style="R"),
                       inline=True)


class OfflineStreamEmbed(CozyficationsEmbed):
    """Represents a custom PyCord offline stream embed."""

    def __init__(self, *, bot: Cozyfications, stream: twitch.OfflineStream, **kwargs) -> None:
        """Initialises a new offline stream embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        stream: :class:`OfflineStream`
            The offline stream instance.
        **kwargs: Any"""
        super().__init__(bot=bot, **kwargs)
        self.title: str = f"{stream.streamer} is OFFLINE!"
        self.url: str = stream.url
        self.add_field(name="Last Stream Title:", value=stream.title, inline=False)
        self.set_thumbnail(url=stream.profile_picture)


class InvalidMessageIDEmbed(RedEmbed):
    """Represents a custom PyCord invalid message ID embed."""

    def __init__(self, *, message_id: int, **kwargs) -> None:
        """Initialises a new invalid message ID embed.

        Parameters
        ----------
        message_id: :class:`int`
            The invalid message ID the user tried to set up.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Invalid Message ID"
        self.description: str = "Failed to set up the channel and message for live stream notifications!"
        self.add_field(
            name="Message ID:",
            value=str(message_id)
        )


class MessageNotSentByBotEmbed(RedEmbed):
    """Represents a custom PyCord message not sent by bot embed."""

    def __init__(self, *, channel: discord.TextChannel, message: discord.Message, **kwargs) -> None:
        """Initialises a new message not sent by bot embed.

        Parameters
        ----------
        channel: :class:`discord.TextChannel`
            The channel the user tried to set up.
        message: :class:`discord.Message`
            The message the user tried to set up.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Message Not Sent By Bot"
        self.description: str = "Failed to set up the channel and message for live stream notifications!"
        self.add_field(
            name="Channel:",
            value=channel.mention
        )
        self.add_field(
            name="Message:",
            value=f"[Click Here]({message.jump_url})"
        )


class SuccessfulSetupEmbed(GreenEmbed):
    """Represents a custom PyCord successful setup embed."""

    def __init__(self, *, channel: discord.TextChannel, message: discord.Message, **kwargs) -> None:
        """Initialises a new successful setup embed.

        Parameters
        ----------
        channel: :class:`discord.TextChannel`
            The channel notifications will be sent to.
        message: :class:`discord.Message`
            The message notifications will be sent to.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Setup Successful"
        self.description: str = "Successfully set up the channel and message for live stream notifications!"
        self.add_field(
            name="Channel:",
            value=channel.mention
        )
        self.add_field(
            name="Message:",
            value=f"[Click Here]({message.jump_url})"
        )


class GuildNotSetupEmbed(RedEmbed):
    """Represents a custom PyCord guild not setup embed."""

    def __init__(self, *, bot: Cozyfications, **kwargs) -> None:
        """Initialises a new guild not setup embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        **kwargs: Any"""
        super().__init__(**kwargs)
        setup_command = bot.get_application_command("setup")
        self.title: str = "Guild Not Set Up"
        self.description: str = f"""The guild has not been set up yet!
        Use </{setup_command.qualified_name}:{setup_command.qualified_id}> to set up the guild."""


class SubscriptionLimitEmbed(RedEmbed):
    """Represents a custom PyCord subscription limit embed."""

    def __init__(self, *, bot: Cozyfications, **kwargs) -> None:
        """Initialises a new subscription limit embed.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        **kwargs: Any"""
        super().__init__(**kwargs)
        unsubscribe_command: discord.ApplicationCommand = bot.get_application_command("twitch channel unsubscribe")
        self.title: str = "Subscription Limit Reached"
        self.description: str = f"""You can only subscribe to 10 Twitch channels per server!
        Use </{unsubscribe_command.qualified_name}:{unsubscribe_command.qualified_id}> to unsubscribe from a channel."""


class InvalidTwitchChannelEmbed(RedEmbed):
    """Represents a custom PyCord invalid Twitch channel embed."""

    def __init__(self, *, twitch_channel: str, **kwargs) -> None:
        """Initialises a new invalid Twitch channel embed.

        Parameters
        ----------
        twitch_channel: :class:`str`
            The Twitch channel the user tried to subscribe to.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Invalid Twitch Channel"
        self.description: str = "Failed to subscribe to/unsubscribe from the Twitch channel!"
        self.add_field(
            name="Twitch Channel:",
            value=twitch_channel
        )


class DuplicateSubscriptionEmbed(RedEmbed):
    """Represents a custom PyCord duplicate subscription embed."""

    def __init__(self, *, twitch_channel: twitch.LiveStream | twitch.OfflineStream, **kwargs) -> None:
        """Initialises a new duplicate subscription embed.

        Parameters
        ----------
        twitch_channel: Union[:class:`LiveStream`, :class:`OfflineStream`]
            The Twitch channel the user tried to subscribe to.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Duplicate Subscription"
        self.description: str = "Failed to subscribe to the Twitch channel!"
        self.add_field(
            name="Twitch Channel:",
            value=f"[{twitch_channel.streamer}]({twitch_channel.url})"
        )


class SuccessfulSubscriptionEmbed(GreenEmbed):
    """Represents a custom PyCord successful subscription embed."""

    def __init__(self, *, twitch_channel: twitch.LiveStream | twitch.OfflineStream, **kwargs) -> None:
        """Initialises a new successful subscription embed.

        Parameters
        ----------
        twitch_channel: Union[:class:`LiveStream`, :class:`OfflineStream`]
            The Twitch channel the user successfully subscribed to.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Subscription Successful"
        self.description: str = "Successfully subscribed to the Twitch channel!"
        self.add_field(
            name="Twitch Channel:",
            value=f"[{twitch_channel.streamer}]({twitch_channel.url})"
        )


class NotSubscribedEmbed(RedEmbed):
    """Represents a custom PyCord not subscribed embed."""

    def __init__(self, *, twitch_channel: twitch.LiveStream | twitch.OfflineStream, **kwargs) -> None:
        """Initialises a new not subscribed embed.

        Parameters
        ----------
        twitch_channel: Union[:class:`LiveStream`, :class:`OfflineStream`]
            The Twitch channel the user tried to unsubscribe from.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Not Subscribed"
        self.description: str = "Failed to unsubscribe from the Twitch channel!"
        self.add_field(
            name="Twitch Channel:",
            value=f"[{twitch_channel.streamer}]({twitch_channel.url})"
        )


class SuccessfulUnsubscriptionEmbed(GreenEmbed):
    """Represents a custom PyCord successful unsubscription embed."""

    def __init__(self, *, twitch_channel: twitch.LiveStream | twitch.OfflineStream, **kwargs) -> None:
        """Initialises a new successful unsubscription embed.

        Parameters
        ----------
        twitch_channel: Union[:class:`LiveStream`, :class:`OfflineStream`]
            The Twitch channel the user successfully unsubscribed from.
        **kwargs: Any"""
        super().__init__(**kwargs)
        self.title: str = "Unsubscription Successful"
        self.description: str = "Successfully unsubscribed from the Twitch channel!"
        self.add_field(
            name="Twitch Channel:",
            value=f"[{twitch_channel.streamer}]({twitch_channel.url})"
        )


def create_embeds_list(*, message: discord.Message, twitch_channel: Type[database.TwitchChannel],
                       new_embed: discord.Embed) -> list[discord.Embed]:
    """Creates a list of embeds with the new embed inserted at the correct index.

    Arguments
    ---------
    message : discord.Message
        The message to edit.
    twitch_channel : database.TwitchChannel
        The Twitch channel to get the index from.
    new_embed : discord.Embed
        The embed to insert.

    Returns
    -------
    list[discord.Embed]
        The list of embeds."""
    index_to_insert: int | None = None
    embeds: List[discord.Embed] = []
    for index, embed in enumerate(message.embeds):
        if twitch_channel.streamer in embed.title:
            index_to_insert = index
        elif embed.title == "Live Stream Notifications":
            continue
        else:
            embeds.append(embed)
    if index_to_insert is not None:
        embeds.insert(index_to_insert, new_embed)
    else:
        embeds.append(new_embed)
    return embeds
