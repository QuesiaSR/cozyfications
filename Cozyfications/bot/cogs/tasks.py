from discord.ext import tasks

from Cozyfications.bot import core


class Tasks(core.Cog):
    """Background tasks for the bot."""

    def __init__(self, bot: core.Cozyfications) -> None:
        self.bot: core.Cozyfications = bot

        self.execute.start()
        self.alerts.start()

    def cog_unload(self) -> None:
        self.execute.cancel()
        self.alerts.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=0.1)
    async def execute(self):
        index = 0
        for info in core.Cozyfications.QUEUE:
            await info["callback"](info["data"], self.bot)
            core.Cozyfications.QUEUE.pop(index)
            index += 1

    @tasks.loop(hours=3)
    async def alerts(self):
        if self.bot.new_subscriptions != 0:
            print(f"Added {self.bot.new_subscriptions} new subscriptions.")
            self.bot.new_subscriptions = 0

        if self.bot.new_subscriptions != 0:
            print(f"Deleted {self.bot.new_subscriptions} subscriptions.")
            self.bot.new_subscriptions = 0


def setup(bot):
    bot.add_cog(Tasks(bot))
