from Cozyfications import database, secrets
from Cozyfications.bot import main

if __name__ == "__main__":
    database.create()
    main.Cozyfications().run(secrets.Discord.TOKEN)
