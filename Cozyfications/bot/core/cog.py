from discord.ext import commands

from Cozyfications.bot.core import Cozyfications


class Cog(commands.Cog):
    """Base class for all cogs"""

    def __init__(self, bot: Cozyfications) -> None:
        self.bot: Cozyfications = bot
