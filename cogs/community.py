import json
from datetime import datetime, timezone
import discord
from discord.ext import commands
from database import now

def setup(bot):
    @bot.command()
    async def suggest(ctx, *, body: str):
        if len(body.strip())<8: return await ctx.reply("Please include a little more detail.", mention_author=False)
        i=bot.db.execute("INSERT INTO suggestions(guild_id,user_id,body,created_at) VALUES(?,?,?,?)",(str(ctx.guild.id if ctx.guild else 0),str(ctx.author.id),body[:1800],now()))
        await ctx.reply(f"Suggestion saved as `#{i}`. Thanks for the feedback!", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def suggestions(ctx, status: str="pending"):
        rows=bot.db.all("SELECT id,user_id,body,status,created_at FROM suggestions WHERE guild_id=? AND status=? ORDER BY id DESC LIMIT 15",(str(ctx.guild.id),status))
        await ctx.reply("\n".join(f"`#{r['id']}` <@{r['user_id']}> · {r['body'][:180]} (`{r['status']}`)" for r in rows) or "No suggestions match that status.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def suggestionapprove(ctx, suggestion_id: int):
        bot.db.execute("UPDATE suggestions SET status='approved' WHERE id=? AND guild_id=?",(suggestion_id,str(ctx.guild.id)))
        bot.db.audit(ctx.guild.id,ctx.author.id,"suggestionapprove",suggestion_id)
        await ctx.reply("Suggestion marked approved if it exists.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def suggestiondeny(ctx, suggestion_id: int, *, reason: str="No reason supplied"):
        bot.db.execute("UPDATE suggestions SET status='denied' WHERE id=? AND guild_id=?",(suggestion_id,str(ctx.guild.id)))
        bot.db.audit(ctx.guild.id,ctx.author.id,"suggestiondeny",suggestion_id,reason)
        await ctx.reply("Suggestion marked denied if it exists.", mention_author=False)
    @bot.command()
    async def partner(ctx):
        await ctx.reply("Partnerships track mutual server collaborations. Use `!partnerrequest name | link | details` to submit a record.", mention_author=False)
    @bot.command()
    async def partnerrequest(ctx, *, data: str):
        parts=[x.strip() for x in data.split("|",2)]
        if not parts[0]: return await ctx.reply("Syntax: `!partnerrequest Server Name | Invite/URL | Details`", mention_author=False)
        payload={"link":parts[1] if len(parts)>1 else "", "details":parts[2] if len(parts)>2 else ""}
        i=bot.db.execute("INSERT INTO records(guild_id,kind,name,status,payload,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",(str(ctx.guild.id if ctx.guild else 0),"partner",parts[0][:100],"pending",json.dumps(payload),now(),now()))
        await ctx.reply(f"Partnership request saved as `#{i}` for staff review.", mention_author=False)
    @bot.command()
    async def partners(ctx): await list_records(ctx, "partner")
    @bot.command()
    async def partnerlist(ctx): await list_records(ctx, "partner")
    @bot.command()
    async def affiliate(ctx): await ctx.reply("Affiliates track referral relationships and affiliate agreements, separately from mutual partnerships.", mention_author=False)
    @bot.command()
    async def affiliaterequest(ctx, *, data: str):
        parts=[x.strip() for x in data.split("|",2)]
        i=bot.db.execute("INSERT INTO records(guild_id,kind,name,status,payload,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",(str(ctx.guild.id if ctx.guild else 0),"affiliate",parts[0][:100],"pending",json.dumps({"details":parts[1:] }),now(),now()))
        await ctx.reply(f"Affiliate request saved as `#{i}`.", mention_author=False)
    @bot.command()
    async def affiliates(ctx): await list_records(ctx, "affiliate")
    @bot.command()
    async def affiliatelist(ctx): await list_records(ctx, "affiliate")
    async def list_records(ctx, kind):
        gid=str(ctx.guild.id if ctx.guild else 0)
        rows=bot.db.all("SELECT id,name,status,created_at FROM records WHERE guild_id=? AND kind=? ORDER BY id DESC LIMIT 15",(gid,kind))
        await ctx.reply("\n".join(f"`#{r['id']}` **{r['name']}** — {r['status']}" for r in rows) or f"No {kind} records yet.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def partneraccept(ctx, record_id: int):
        bot.db.execute("UPDATE records SET status='active',updated_at=? WHERE id=? AND guild_id=? AND kind='partner'",(now(),record_id,str(ctx.guild.id)))
        bot.db.audit(ctx.guild.id,ctx.author.id,"partneraccept",record_id)
        await ctx.reply("Partnership marked active if the record exists.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def partnerdeny(ctx, record_id: int, *, reason: str="No reason supplied"):
        bot.db.execute("UPDATE records SET status='denied',updated_at=? WHERE id=? AND guild_id=? AND kind='partner'",(now(),record_id,str(ctx.guild.id)))
        bot.db.audit(ctx.guild.id,ctx.author.id,"partnerdeny",record_id,reason)
        await ctx.reply("Partnership request marked denied if it exists.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def createticket(ctx, *, topic: str="Support request"):
        guild=ctx.guild
        overwrites={guild.default_role:discord.PermissionOverwrite(view_channel=False),
                    ctx.author:discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True),
                    guild.me:discord.PermissionOverwrite(view_channel=True,send_messages=True,manage_channels=True)}
        category=None
        channel=await guild.create_text_channel(f"ticket-{ctx.author.name}".lower().replace(" ","-")[:90], overwrites=overwrites, category=category, reason=f"Ticket created by {ctx.author}")
        i=bot.db.execute("INSERT INTO tickets(guild_id,user_id,channel_id,created_at) VALUES(?,?,?,?)",(str(guild.id),str(ctx.author.id),str(channel.id),now()))
        await channel.send(f"{ctx.author.mention} — ticket `#{i}`\nTopic: {discord.utils.escape_mentions(topic[:500])}\nStaff can use `!ticketclose` here.")
        await ctx.reply(f"Ticket created: {channel.mention}", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def ticketclose(ctx):
        row=bot.db.one("SELECT id FROM tickets WHERE channel_id=? AND status='open'",(str(ctx.channel.id),))
        if not row: return await ctx.reply("This channel isn't a tracked open ticket.", mention_author=False)
        bot.db.execute("UPDATE tickets SET status='closed' WHERE id=?",(row["id"],))
        bot.db.audit(ctx.guild.id,ctx.author.id,"ticketclose",row["id"])
        await ctx.reply("Ticket marked closed. A staff member can archive or delete the channel separately.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def tickets(ctx):
        rows=bot.db.all("SELECT id,user_id,channel_id,status FROM tickets WHERE guild_id=? ORDER BY id DESC LIMIT 20",(str(ctx.guild.id),))
        await ctx.reply("\n".join(f"`#{r['id']}` <@{r['user_id']}> · <#{r['channel_id']}> · {r['status']}" for r in rows) or "No tickets recorded.", mention_author=False)
    @bot.command()
    async def truth(ctx): await ctx.reply("What's something you're proud of that you rarely talk about?", mention_author=False)
    @bot.command()
    async def dare(ctx): await ctx.reply("Give someone a genuine, specific compliment — only if you're comfortable.", mention_author=False)
    @bot.command()
    async def truthordare(ctx):
        import random
        await ctx.invoke(bot.get_command(random.choice(["truth","dare"])))
    @bot.command()
    async def wouldyourather(ctx): await ctx.reply("Would you rather explore the deep ocean or travel through space?", mention_author=False)
    @bot.command()
    async def thisorthat(ctx): await ctx.reply("Tea 🍵 or coffee ☕?", mention_author=False)
    @bot.command()
    async def icebreaker(ctx): await ctx.reply("What's a tiny thing that instantly improves your day?", mention_author=False)
    @bot.command()
    async def questionoftheday(ctx): await icebreaker(ctx)
