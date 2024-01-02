import dotenv
import os

dotenv.load_dotenv()


class Discord:
    ID = os.getenv("DISCORD_ID")
    SECRET = os.getenv("DISCORD_SECRET")
    TOKEN = os.getenv("DISCORD_TOKEN")


class Twitch:
    ID = os.getenv("TWITCH_ID")
    SECRET = os.getenv("TWITCH_SECRET")


class Database:
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")


class Ngrok:
    TOKEN = os.getenv("NGROK_TOKEN")
