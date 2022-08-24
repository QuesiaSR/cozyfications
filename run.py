from Cozyfications.bot import main
from Cozyfications.secrets import Discord
from Cozyfications import database, ngrok, events

if __name__ == "__main__":
    database.create()
    URL = ngrok.run_server()
    events.run_event_hook(URL)
    main.Cozyfications().run(Discord.TOKEN)
