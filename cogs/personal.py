from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
from database import now

def setup(bot):
    @bot.command()
    async def addnote(ctx, *, body: str):
        if len(body)>1800: return await ctx.reply("Keep notes under 1,800 characters.", mention_author=False)
        i=bot.db.execute("INSERT INTO notes(user_id,body,created_at) VALUES(?,?,?)",(str(ctx.author.id),body,now()))
        await ctx.reply(f"Saved private note `#{i}`.", mention_author=False)
    @bot.command()
    async def notes(ctx):
        rows=bot.db.all("SELECT id,body,created_at FROM notes WHERE user_id=? ORDER BY id DESC LIMIT 10",(str(ctx.author.id),))
        await ctx.reply("\n".join(f"`#{r['id']}` {r['body'][:160]}" for r in rows) or "You have no saved notes.", mention_author=False)
    @bot.command()
    async def listnotes(ctx): await notes(ctx)
    @bot.command()
    async def note(ctx): await ctx.reply("Use `!addnote your note` to save a private note and `!notes` to list your latest notes.", mention_author=False)
    @bot.command()
    async def deletenote(ctx, note_id: int):
        n=bot.db.one("SELECT id FROM notes WHERE id=? AND user_id=?",(note_id,str(ctx.author.id)))
        if not n: return await ctx.reply("I couldn't find that note belonging to you.", mention_author=False)
        bot.db.execute("DELETE FROM notes WHERE id=?",(note_id,))
        await ctx.reply("Note deleted.", mention_author=False)
    @bot.command()
    async def addtodo(ctx, *, body: str):
        i=bot.db.execute("INSERT INTO todos(user_id,body,created_at) VALUES(?,?,?)",(str(ctx.author.id),body[:500],now()))
        await ctx.reply(f"Added task `#{i}`.", mention_author=False)
    @bot.command()
    async def todo(ctx): await listtodo(ctx)
    @bot.command()
    async def listtodo(ctx):
        rows=bot.db.all("SELECT id,body,done FROM todos WHERE user_id=? ORDER BY done,id DESC LIMIT 20",(str(ctx.author.id),))
        await ctx.reply("\n".join(f"{'✅' if r['done'] else '⬜'} `#{r['id']}` {r['body']}" for r in rows) or "Your to-do list is empty.", mention_author=False)
    @bot.command()
    async def completetodo(ctx, task_id: int):
        cur=bot.db.execute("UPDATE todos SET done=1 WHERE id=? AND user_id=?",(task_id,str(ctx.author.id)))
        await ctx.reply("Marked complete if that task exists and belongs to you.", mention_author=False)
    @bot.command()
    async def clearcompleted(ctx):
        bot.db.execute("DELETE FROM todos WHERE user_id=? AND done=1",(str(ctx.author.id),))
        await ctx.reply("Removed your completed tasks.", mention_author=False)
    @bot.command()
    async def settimezone(ctx, *, zone: str):
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(zone)
        except Exception:
            return await ctx.reply("Use a valid IANA timezone, e.g. `Asia/Singapore` or `Europe/London`.", mention_author=False)
        bot.db.execute("INSERT INTO timezones(user_id,timezone) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET timezone=excluded.timezone",(str(ctx.author.id),zone))
        await ctx.reply(f"Saved timezone: `{zone}`.", mention_author=False)
    @bot.command()
    async def timezone(ctx, member: discord.User=None):
        user=member or ctx.author
        row=bot.db.one("SELECT timezone FROM timezones WHERE user_id=?",(str(user.id),))
        await ctx.reply(f"{user.display_name if hasattr(user,'display_name') else user.name}: `{row['timezone']}`" if row else "No timezone saved. Use `!settimezone Asia/Singapore`.", mention_author=False)
    @bot.command()
    async def time(ctx):
        await ctx.reply(f"UTC now: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}", mention_author=False)
    @bot.command()
    async def remindme(ctx, minutes: int, *, body: str):
        if not 1 <= minutes <= 60*24*30: return await ctx.reply("Choose 1–43,200 minutes.", mention_author=False)
        due=(datetime.now(timezone.utc)+timedelta(minutes=minutes)).isoformat()
        i=bot.db.execute("INSERT INTO reminders(user_id,body,due_at) VALUES(?,?,?)",(str(ctx.author.id),body[:500],due))
        await ctx.reply(f"Reminder `#{i}` saved for {due} UTC. Delivery worker is not enabled yet; use `!reminders` to view saved reminders.", mention_author=False)
    @bot.command()
    async def reminders(ctx):
        rows=bot.db.all("SELECT id,body,due_at FROM reminders WHERE user_id=? AND delivered=0 ORDER BY due_at LIMIT 10",(str(ctx.author.id),))
        await ctx.reply("\n".join(f"`#{r['id']}` {r['body']} — {r['due_at']}" for r in rows) or "No pending reminders.", mention_author=False)
    @bot.command()
    async def reminder(ctx, minutes: int, *, body: str): await remindme(ctx, minutes, body=body)
    @bot.command()
    async def birthdayset(ctx, month: int, day: int):
        import calendar
        if not 1<=month<=12 or not 1<=day<=calendar.monthrange(2024,month)[1]:
            return await ctx.reply("Enter a valid month and day, e.g. `!birthdayset 12 25`.", mention_author=False)
        if not ctx.guild: return await ctx.reply("Use this command in a server.", mention_author=False)
        bot.db.execute("INSERT INTO birthdays(guild_id,user_id,month,day,opted_in) VALUES(?,?,?,?,1) ON CONFLICT(guild_id,user_id) DO UPDATE SET month=excluded.month,day=excluded.day,opted_in=1",(str(ctx.guild.id),str(ctx.author.id),month,day))
        await ctx.reply("Birthday saved as month/day only, with announcements opted in. Use `!birthdayoptout` any time.", mention_author=False)
    @bot.command()
    async def birthday(ctx):
        if not ctx.guild: return await ctx.reply("Use this command in a server.", mention_author=False)
        row=bot.db.one("SELECT month,day,opted_in FROM birthdays WHERE guild_id=? AND user_id=?",(str(ctx.guild.id),str(ctx.author.id)))
        await ctx.reply(f"Saved birthday: {row['month']:02d}-{row['day']:02d} · announcements {'on' if row['opted_in'] else 'off'}" if row else "No birthday saved. Use `!birthdayset MM DD`.", mention_author=False)
    @bot.command()
    async def birthdayoptout(ctx):
        if ctx.guild: bot.db.execute("UPDATE birthdays SET opted_in=0 WHERE guild_id=? AND user_id=?",(str(ctx.guild.id),str(ctx.author.id)))
        await ctx.reply("Birthday announcements opted out.", mention_author=False)
    @bot.command()
    async def birthdayoptin(ctx):
        if ctx.guild: bot.db.execute("UPDATE birthdays SET opted_in=1 WHERE guild_id=? AND user_id=?",(str(ctx.guild.id),str(ctx.author.id)))
        await ctx.reply("Birthday announcements opted in.", mention_author=False)
    @bot.command()
    async def forget(ctx):
        uid=str(ctx.author.id)
        for table in ("notes","todos","reminders","timezones"):
            bot.db.execute(f"DELETE FROM {table} WHERE user_id=?",(uid,))
        if ctx.guild: bot.db.execute("DELETE FROM birthdays WHERE guild_id=? AND user_id=?",(str(ctx.guild.id),uid))
        await ctx.reply("Deleted your notes, to-dos, reminders, timezone, and this server's birthday record where supported.", mention_author=False)
    @bot.command()
    async def mood(ctx, *, value: str):
        bot.db.config(ctx.guild.id if ctx.guild else 0, f"mood:{ctx.author.id}", value[:100])
        await ctx.reply("Mood noted for this session's server configuration. Avoid storing highly sensitive information.", mention_author=False)
