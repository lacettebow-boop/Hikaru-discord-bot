from __future__ import annotations
import os, logging
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import Database

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("hikaru")

PREFIX = os.getenv("BOT_PREFIX", "!")
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
if not TOKEN or TOKEN == "put_your_discord_bot_token_here":
    raise SystemExit("Set DISCORD_TOKEN in your .env file before starting Hikaru.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class HikaruBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents,
                         help_command=None, case_insensitive=True)
        self.started_at = discord.utils.utcnow()
        self.db = Database(os.getenv("DATABASE_PATH", "data/hikaru.sqlite3"))

    async def setup_hook(self):
        from cogs.core import setup as setup_core
        from cogs.personal import setup as setup_personal
        from cogs.moderation import setup as setup_moderation
        from cogs.community import setup as setup_community
        from cogs.ai_features import setup as setup_ai
        from cogs.planned import setup as setup_planned
        for setup in (setup_core, setup_personal, setup_moderation, setup_community, setup_ai, setup_planned):
            await setup(self)
        log.info("Loaded %s commands", len(self.commands))

    async def on_ready(self):
        log.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "?")
        await self.change_presence(activity=discord.Game(name=f"{PREFIX}help | Hikaru"))

bot = HikaruBot()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Missing argument: `{error.param.name}`. Try `{PREFIX}help`.", mention_author=False)
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("I couldn't understand one of those arguments. Check the command syntax with `!help`.", mention_author=False)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don't have the Discord permissions required for that command.", mention_author=False)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply("I don't have the Discord permissions needed for that action.", mention_author=False)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f"Slow down a little — try again in {error.retry_after:.1f}s.", mention_author=False)
    else:
        log.exception("Command error", exc_info=error)
        await ctx.reply("Something went wrong. The error was logged for the bot operator.", mention_author=False)

bot.run(TOKEN)
