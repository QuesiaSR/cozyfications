from discord.ext import tasks
from discord.ext.commands import Cog
from Cozyfications import events
from Cozyfications.bot import main

class Tasks(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.task.start()
        self.alerts.start()
    
    def cog_unload(self):
        self.task.cancel()
        self.alerts.cancel()
        return super().cog_unload()
    
    @tasks.loop(seconds=20)
    async def task(self):
        main.INSTANCE = self.bot
    
    @tasks.loop(hours=3)
    async def alerts(self):
        if events.Globals.NEW_SUBSCRIPTIONS != 0:
            print(f"Added {events.NEW_SUBSCRIPTIONS} new subscriptions.")
            events.Globals.NEW_SUBSCRIPTIONS = 0

        if events.Globals.DEL_SUBSCRIPTIONS != 0:
            print(f"Deleted {events.DEL_SUBSCRIPTIONS} subscriptions.")
            events.Globals.DEL_SUBSCRIPTIONS = 0

def setup(bot):
    bot.add_cog(Tasks(bot))
