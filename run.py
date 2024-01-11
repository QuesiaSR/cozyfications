from Cozyfications import database
from Cozyfications.bot.core import Cozyfications

if __name__ == "__main__":
    database.create()
    Cozyfications().run()
