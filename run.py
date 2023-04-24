from Cozyfications.bot import main
from Cozyfications import database, secrets

if __name__ == "__main__":
    database.create()
    main.Cozyfications().run(secrets.Discord.TOKEN)
