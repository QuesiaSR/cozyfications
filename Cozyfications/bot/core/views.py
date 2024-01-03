import discord

from __init__ import Cog
from bot import Cozyfications
from embeds import HelpSelectEmbed


class ConfirmDialog(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ok", style=discord.ButtonStyle.green, custom_id="confirm:confirm")
    async def confirm(self, _: discord.ui.Button, interaction: discord.Interaction):
        return await interaction.response.send_message("hi")


class HelpSelect(discord.ui.Select):
    """Represents a custom PyCord UI help select menu."""

    def __init__(self, *, bot: Cozyfications, cog: Cog) -> None:
        """Initialises a new help select menu.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance.
        cog: :class:`Cog`
            The cog instance."""
        self.bot: Cozyfications = bot
        self.cog: Cog = cog
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name,
                    description=cog.__doc__,
                )
                for cog_name, cog in self.cog.bot.cogs.items()
                if cog.__cog_commands__ and cog_name not in ["Help"]
            ],
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Handles the callback for the help select menu.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction instance."""
        cog = self.cog.bot.get_cog(self.values[0])
        embed = HelpSelectEmbed(bot=self.bot, cog=cog)
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
