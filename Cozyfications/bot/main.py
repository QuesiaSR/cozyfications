import discord, os
from discord import AutoShardedBot as asb

INSTANCE: asb = None

class Cozyfications(asb):
    def __init__(self):
        self.cog_blacklist = []
        self.cog_folder_blacklist = ["__pycache__"]
        self.path = "./Cozyfications/bot/cogs"

        super().__init__(
            intents=discord.Intents(members=True),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False),
            owner_ids=[810863994985250836],
            debug_guilds=[834749196967608321]
        )

        INSTANCE = self

    def load_cogs(self, folder=None):
        if folder != None: self.path = os.path.join(self.path, folder)
        formatted_path = self.path.strip("./").replace("/", ".").replace("\\", ".")

        for file in os.listdir(self.path):
            if not os.path.isdir(os.path.join(self.path, file)):
                if not file in self.cog_blacklist:
                    try:
                        self.load_extension(f"{formatted_path}.{file[:-3]}")
                        print(f"  Loaded '{file}'")
                    except Exception as e: print(e)
            else:
                if not file in self.cog_folder_blacklist:
                    self.load_cogs(file)
    
    async def on_connect(self):
        (
            print("Loading cogs..."),
            self.load_cogs()
        )
        (
            print("Registering commands..."),
            await self.register_commands()
        )
        print("\nConnected")
        return await super().on_connect()

    async def on_ready(self): return print("Ready")

if __name__ == "__main__":
    exit("The bot cannot be run directly from the bot file.")
