# Hikaru Discord Bot

A modular Discord bot starter for the `!` prefix, built with Python 3.11+, `discord.py`, SQLite, and optional OpenAI-powered text helpers.

## Important scope note
This is a substantial, runnable foundation, not a claim that every item in the enormous reference list is already a fully bespoke feature. The command registry registers the supported commands below and includes a safe generic help response for planned commands. Sensitive and destructive actions are deliberately permission-gated, audited, and confirmation-protected where implemented. Extend `cogs/` to turn each planned command into its full workflow.

## Quick start
1. Install Python 3.11 or newer.
2. Create a Discord application and bot at https://discord.com/developers/applications.
3. Enable **Message Content Intent** in the Developer Portal (needed for `!` prefix commands).
4. Copy `.env.example` to `.env`; add your bot token and optional AI key.
5. Install dependencies: `python -m pip install -r requirements.txt`
6. Run: `python bot.py`

Never commit `.env`. `.gitignore` excludes it. Keep bot tokens and API keys private.

## Configuration
- `DISCORD_TOKEN` — required Discord bot token.
- `OPENAI_API_KEY` — optional; only used for AI commands.
- `OPENAI_MODEL` — optional, defaults to `gpt-4.1-mini`.
- `BOT_PREFIX` — optional, defaults to `!`.
- `OWNER_IDS` — comma-separated Discord user IDs for owner-only actions.
- `DATABASE_PATH` — SQLite file path, defaults to `data/hikaru.sqlite3`.
- `SUPPORT_URL`, `INVITE_URL`, `BOT_VERSION` — optional display settings.

## Included features
- Prefix command framework and help/info/utility commands.
- Greeting, random choice, dice, coin flip, 8-ball, jokes, comfort and prompt helpers.
- SQLite persistence for notes, todos, reminders, timezones, birthday month/day, warnings, audit entries, config, partners/affiliates, suggestions, reports, and tickets.
- Permission checks for moderation/configuration and role/channel operations.
- Hierarchy checks for role assignment and staff promotion/demotion.
- Audit logging and confirmation tokens for destructive operations.
- Optional OpenAI text generation, with a graceful message when no API key is configured.
- `.env.example`, `.gitignore`, schema, and modular command cogs.

## Security and operational notes
- Invite the bot with only the permissions it needs.
- The bot cannot manage roles at or above its highest role. Keep its role below roles it should manage.
- Do not grant Administrator unless you have a specific need.
- Use a persistent host and back up `data/hikaru.sqlite3`.
- SQLite is suitable for a small bot; use managed PostgreSQL for larger deployments.
- This bot does not collect birth years. Birthday records default to month/day.
- Notes and journal-like content are private to the invoking user at command level; server administrators should still protect database/filesystem access.
- Do not use the virtual economy for real-money transactions or gambling.
