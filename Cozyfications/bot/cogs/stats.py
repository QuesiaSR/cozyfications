import discord
from discord import ApplicationContext, commands
from discord.ext.commands import Cog

from Cozyfications.bot.main import Cozyfications


class Stats(Cog):
    def __init__(self, bot):
        self.bot: Cozyfications = bot

    @commands.slash_command(name="stats", description="View the bot's statistics.")
    async def stats(self, ctx: ApplicationContext):
        await ctx.defer()
        embed = discord.Embed(
            color=self.bot.color,
            title="🤖 Statistics 🤖"
        )
        embed.add_field(
            name="Servers:",
            value=f"`{len(self.bot.guilds)}`",
            inline=False
        )
        embed.add_field(
            name="New Subscriptions:",
            value=f"`{self.bot.new_subscriptions}`",
            inline=True
        )
        embed.add_field(
            name="Deleted Subscriptions:",
            value=f"`{self.bot.delete_subscriptions}`",
            inline=False
        )
        embed.add_field(
            name="Queued Events:",
            value=f"`{len(Cozyfications.QUEUE)}`",
            inline=True
        )
        return await ctx.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
