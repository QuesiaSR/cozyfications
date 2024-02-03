import os
import platform
import sys
import traceback

import discord
from aiohttp import ClientSession

from Cozyfications import secrets, database, twitch


class Cozyfications(discord.Bot):

    def __init__(self) -> None:
        super().__init__(
            activity=discord.CustomActivity("/help"),
            help_command=None,
            intents=discord.Intents(
                guilds=True,
                members=True,
                messages=True
            ),
            owner_ids=[810863994985250836, 672768917885681678],
            debug_guilds=[1018128160962904114]
        )

        self.on_ready_fired: bool = False

        self.errors_webhook: discord.Webhook | None = None
        self.color = 0xE0B484

        for filename in os.listdir("Cozyfications/bot/cogs"):
            if filename.endswith(".py"):
                self.load_cog(f"Cozyfications.bot.cogs.{filename[:-3]}")

    def load_cog(self, cog: str) -> None:
        try:
            self.load_extension(cog)
        except Exception as error:
            error = getattr(error, "original", error)
            print("".join(traceback.format_exception(type(error), error, error.__traceback__)))

    @property
    def http_session(self) -> ClientSession:
        return self.http._HTTPClient__session

    def get_errors_webhook(self) -> discord.Webhook:
        return discord.Webhook.from_url(
            url=secrets.Discord.ERRORS_WEBHOOK,
            session=self.http_session,
            bot_token=self.http.token,
        )

    async def on_connect(self):
        await database.setup()
        await twitch.update_channels()
        await super().on_connect()

    async def on_ready(self):
        if self.on_ready_fired:
            return
        self.on_ready_fired = True

        self.errors_webhook: discord.Webhook = self.get_errors_webhook()

        msg: str = f"""{self.user.name} is online now!
            BotID: {self.user.id}
            Ping: {round(self.latency * 1000)} ms
            Python Version: {platform.python_version()}
            PyCord Version: {discord.__version__}"""
        print(f"\n{msg}\n")

    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        if isinstance((error := error.original), discord.HTTPException):
            description = f"""An HTTP exception has occurred:
            {error.status} {error.__class__.__name__}"""
            if error.text:
                description += f": {error.text}"
            return await ctx.respond(
                embed=discord.Embed(
                    title="HTTP Exception",
                    description=description,
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
            )

        await ctx.respond(embed=discord.Embed(
            title="Error",
            description="An unexpected error has occurred and I've notified my developers.",
            color=discord.Color.yellow(),
            timestamp=discord.utils.utcnow()
        ), ephemeral=True)
        if ctx.guild is not None:
            guild = f"`{ctx.guild.name} ({ctx.guild_id})`"
        else:
            guild = "None (DMs)"
        formatted_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        error_embed = discord.Embed(
            title=error.__class__.__name__,
            description=str(error),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        error_embed.add_field(name="Command:", value=f"`/{ctx.command.qualified_name}`", inline=True)
        error_embed.add_field(name="Guild:", value=f"`{guild}`", inline=True)
        for i in range(0, len(formatted_error), 1015):
            error_embed.add_field(
                name="Error:" if i == 0 else "",
                value=f"```py\n{formatted_error[i:i + 1015]}```",
                inline=False
            )
        return await self.errors_webhook.send(
            embed=error_embed,
            avatar_url=self.user.display_avatar.url
        )

    async def on_error(self, event: str, *args, **kwargs):
        _, error, error_traceback = sys.exc_info()
        formatted_error = ''.join(traceback.format_exception(type(error), error, error_traceback))
        error_embed = discord.Embed(
            title=error.__class__.__name__,
            description=str(error),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        error_embed.add_field(name="Event:", value=f"```py\n{event}```", inline=True)
        error_embed.add_field(name="Args:", value=f"```py\n{args}```", inline=True)
        for i in range(0, len(formatted_error), 1015):
            error_embed.add_field(
                name="Error:" if i == 0 else "",
                value=f"```py\n{formatted_error[i:i + 1015]}```",
                inline=False
            )
        return await self.errors_webhook.send(
            embed=error_embed,
            avatar_url=self.user.display_avatar.url
        )

    def run(self):
        super().run(secrets.Discord.TOKEN)
