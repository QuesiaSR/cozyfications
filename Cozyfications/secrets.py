import os

import dotenv

dotenv.load_dotenv()


class Discord:
    TOKEN = os.getenv("DISCORD_TOKEN")
    ERRORS_WEBHOOK = os.getenv("DISCORD_ERRORS_WEBHOOK")


class Twitch:
    ID = os.getenv("TWITCH_ID")
    SECRET = os.getenv("TWITCH_SECRET")
