import discord

import Cozyfications.bot.core.embeds as embeds
from Cozyfications.bot.core.bot import Cozyfications


class BugReportModal(discord.ui.Modal):
    """Modal for reporting a bug to the bot developer."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Bug Name:",
                placeholder="Please enter a name for the bug...",
                style=discord.InputTextStyle.short,
                max_length=2000,
            ),
            discord.ui.InputText(
                label="Bug Description:",
                placeholder="Please enter a description of the bug...",
                style=discord.InputTextStyle.long,
                max_length=2000,
            ),
            discord.ui.InputText(
                label="Steps to Reproduce:",
                placeholder="Please enter the steps to reproduce the bug...",
                style=discord.InputTextStyle.long,
                max_length=2000,
                required=False,
            ),
            *args,
            title="Bug Report",
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Callback for when the modal is submitted.

        Parameters
        ------------
        interaction: discord.Interaction
            The interaction that submitted the modal."""
        bug_name: str = self.children[0].value
        bug_description: str = self.children[1].value
        steps_to_reproduce: str | None = self.children[2].value
        author: discord.Member | discord.User = interaction.user

        bug_report_embed = embeds.BugReportEmbed(bug_name=bug_name, bug_description=bug_description,
                                                 steps_to_reproduce=steps_to_reproduce, author=author)

        await interaction.client.errors_webhook.send(
            embed=bug_report_embed,
            avatar_url=interaction.client.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embeds.GreenEmbed(
            title="Bug Reported",
            description=f"My developers have been notified of the bug!"
        ), ephemeral=True)


class FeatureRequestModal(discord.ui.Modal):
    """Modal for requesting a feature."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Feature Name:",
                placeholder="Please enter a name for the feature...",
                style=discord.InputTextStyle.short,
                max_length=2000,
            ),
            discord.ui.InputText(
                label="Feature Description:",
                placeholder="Please enter a description of the feature...",
                style=discord.InputTextStyle.long,
                max_length=2000,
            ),
            *args,
            title="Feature Request",
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Callback for when the modal is submitted.

        Parameters
        ------------
        interaction: discord.Interaction
            The interaction that submitted the modal."""
        name = self.children[0].value
        description = self.children[1].value
        author = interaction.user

        feature_request_embed = embeds.FeatureRequestEmbed(feature_name=name, feature_description=description,
                                                           author=author)

        await interaction.client.errors_webhook.send(
            embed=feature_request_embed,
            avatar_url=interaction.client.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embeds.GreenEmbed(
            title="Feature Requested",
            description=f"My developers have been notified of the feature request!"
        ), ephemeral=True)


class HelpSelect(discord.ui.Select):
    """Represents a custom PyCord UI help select menu."""

    def __init__(self, *, bot: Cozyfications) -> None:
        """Initialises a new help select menu.

        Parameters
        ----------
        bot: :class:`Cozyfications`
            The bot instance."""
        self.bot: Cozyfications = bot
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name,
                    description=cog.__doc__,
                )
                for cog_name, cog in self.bot.cogs.items()
                if cog.__cog_commands__ and cog_name not in ["Help"]
            ],
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Handles the callback for the help select menu.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction instance."""
        cog = self.bot.get_cog(self.values[0])
        embed = embeds.HelpSelectEmbed(bot=self.bot, cog=cog)
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
