from typing import Type

import discord

from Cozyfications import database


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
    index_to_insert = None
    embeds = []
    for index, embed in enumerate(message.embeds):
        if twitch_channel.streamer in embed.title:
            index_to_insert = index
        else:
            embeds.append(embed)
    if index_to_insert is not None:
        embeds.insert(index_to_insert, new_embed)
    else:
        embeds.append(new_embed)
    return embeds
