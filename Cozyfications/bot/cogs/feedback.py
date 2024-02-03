import discord

from Cozyfications.bot import core


class Feedback(core.Cog):
    """Report bugs and request features!"""

    report_group: discord.SlashCommandGroup = discord.SlashCommandGroup(
        name="report",
        description="Group of report commands!",
    )

    @report_group.command(name="bug", description="Report a bug to the bot developers!")
    async def report_bug(self, ctx: discord.ApplicationContext):
        """Report a bug to the bot developers!

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation."""
        await ctx.send_modal(core.BugReportModal())

    request_group: discord.SlashCommandGroup = discord.SlashCommandGroup(
        name="request",
        description="Group of request commands!",
    )

    @request_group.command(name="feature", description="Request a feature to be added to the bot!")
    async def request_feature(self, ctx: discord.ApplicationContext):
        """Request a feature to be added to the bot!

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation."""
        await ctx.send_modal(core.FeatureRequestModal())


def setup(bot):
    bot.add_cog(Feedback(bot))
