# Hikaru Discord Bot

A modular Discord bot starter for the ! prefix, built with Python 3.11+, discord.py, SQLite, and optional Google Gemini text helpers through its OpenAI-compatible API.

## Important scope note
This is a substantial, runnable foundation, not a claim that every item in the reference list is already a bespoke feature. The command registry registers supported commands and provides safe generic help for planned commands. Sensitive and destructive actions are permission-gated, audited, and confirmation-protected where implemented. Extend cogs/ to complete planned workflows.

## Quick start
1. Install Python 3.11 or newer.
2. Create a Discord application and bot at https://discord.com/developers/applications.
3. Enable **Message Content Intent** in the Developer Portal (needed for prefix commands).
4. Copy .env.example to .env; set your Discord bot token and optional Gemini API key.
5. Install dependencies: python -m pip install -r requirements.txt
6. Run: python bot.py

Never commit .env. Git ignores it. Keep bot tokens and API keys private.

## Configuration
- DISCORD_TOKEN — required Discord bot token.
- GEMINI_API_KEY — optional; enables AI commands. Create it in Google AI Studio.
- GEMINI_MODEL — optional; defaults to gemini-3.8-flash.
- BOT_PREFIX — optional; defaults to !.
- OWNER_IDS — comma-separated Discord user IDs for owner-only actions.
- DATABASE_PATH — SQLite file path; defaults to data/hikaru.sqlite3.
- SUPPORT_URL, INVITE_URL, BOT_VERSION — optional display settings.

## Deploy to Render
The repository includes render.yaml for a Render Background Worker. Create a new Blueprint from this repository in Render, then provide DISCORD_TOKEN and (optionally) GEMINI_API_KEY as private environment variables when prompted. The configuration uses python bot.py and a 1 GB persistent disk mounted at data/ for SQLite. The worker and disk require a paid Render plan; see Render's current pricing.

## Included features
- Prefix command framework and help/info/utility commands.
- Greeting, random choice, dice, coin flip, 8-ball, jokes, comfort and prompt helpers.
- SQLite persistence for notes, todos, reminders, timezones, birthday month/day, warnings, audit entries, config, partners/affiliates, suggestions, reports, and tickets.
- Permission checks for moderation/configuration and role/channel operations.
- Hierarchy checks for role assignment and staff promotion/demotion.
- Audit logging and confirmation tokens for destructive operations.
- Optional Gemini text generation with a graceful message when no key is configured.
- .env.example, .gitignore, schema, and modular command cogs.

## Security and operational notes
- Invite the bot with only the permissions it needs.
- The bot cannot manage roles at or above its highest role. Keep its role below roles it should manage.
- Do not grant Administrator unless you have a specific need.
- Back up data/hikaru.sqlite3. On Render, keep it under the persistent disk mount.
- SQLite is suitable for a small bot; use managed PostgreSQL for larger deployments.
- This bot does not collect birth years. Birthday records default to month/day.
- Notes and journal-like content are private to the invoking user at command level; server administrators should still protect database/filesystem access.
- Do not use the virtual economy for real-money transactions or gambling.
