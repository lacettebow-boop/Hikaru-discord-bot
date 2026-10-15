# Command status

The project includes working handlers for the core utilities, greetings, random games, user-owned notes and to-dos, timezone, birthday month/day storage, AI text helpers (when configured), selected moderation actions, audit logs, suggestions, basic partner/affiliate records, and basic tickets.

The reference list is much larger than a single safe first-pass implementation. To make the command surface navigable, remaining names are registered as **planned scaffolds** that clearly say they are not implemented yet. They do not fake success. Search for `PLANNED` in `cogs/planned.py` to see the list. Implement each feature in its relevant cog and remove its name from the scaffold list.

Before enabling this in a live server, test with a private test guild and minimal bot permissions. Some Discord features require intents, API support, server boosts, or Discord-side permissions.
