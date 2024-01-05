from discord.ext import commands

from .bot import Cozyfications
from .callbacks import *
from .embeds import *
from .streams import *
from .views import *

__all__ = (
    "BugReportEmbed",
    "Callbacks",
    "Cog",
    "ConfirmDialog",
    "Cozyfications",
    "CozyficationsEmbed",
    "Embed",
    "FeatureRequestEmbed",
    "GreenEmbed",
    "HelpEmbed",
    "HelpSelect",
    "HelpSelectEmbed",
    "LiveStream",
    "OfflineStream",
    "RedEmbed",
    "YellowEmbed"
)


class Cog(commands.Cog):
    """Base class for all cogs"""

    def __init__(self, bot: Cozyfications) -> None:
        self.bot: Cozyfications = bot
