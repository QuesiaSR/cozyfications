from discord.ext import tasks
from discord.ext.commands import Cog

from Cozyfications.bot.main import Cozyfications


class Tasks(Cog):
    def __init__(self, bot: Cozyfications):
        self.bot = bot

        self.execute.start()
        self.alerts.start()

    def cog_unload(self):
        self.execute.cancel()
        self.alerts.cancel()
        return super().cog_unload()

    @tasks.loop(seconds=0.1)
    async def execute(self):
        index = 0
        for info in Cozyfications.QUEUE:
            await info["callback"](info["data"], self.bot)
            Cozyfications.QUEUE.pop(index)
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
