import discord

from Cozyfications.bot import core


class General(core.Cog):
    """Utility commands for general information and interactions!"""

    @discord.slash_command(name="stats", description="View the bot's statistics.")
    async def stats(self, ctx: discord.ApplicationContext):
        """View the bot's statistics.

        Parameters
        ------------
        ctx: discord.ApplicationContext
            The context used for command invocation."""
        stats_embed = core.StatsEmbed(bot=self.bot)
        return await ctx.respond(embed=stats_embed, ephemeral=True)


def setup(bot):
    bot.add_cog(General(bot))
