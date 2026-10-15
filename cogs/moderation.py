import secrets
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
from database import now

def staff_check():
    async def predicate(ctx):
        return bool(ctx.guild and (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild))
    return commands.check(predicate)

def setup(bot):
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def warn(ctx, member: discord.Member, *, reason: str="No reason supplied"):
        i=bot.db.execute("INSERT INTO warnings(guild_id,target_id,actor_id,reason,created_at) VALUES(?,?,?,?,?)",(str(ctx.guild.id),str(member.id),str(ctx.author.id),reason[:1000],now()))
        bot.db.audit(ctx.guild.id,ctx.author.id,"warn",member.id,reason,{"warning_id":i})
        await ctx.reply(f"Recorded warning `#{i}` for {member.mention}.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def warnings(ctx, member: discord.Member):
        rows=bot.db.all("SELECT id,reason,actor_id,created_at FROM warnings WHERE guild_id=? AND target_id=? ORDER BY id DESC LIMIT 15",(str(ctx.guild.id),str(member.id)))
        await ctx.reply("\n".join(f"`#{r['id']}` {r['created_at'][:10]} · {r['reason']} (by <@{r['actor_id']}>)" for r in rows) or "No recorded warnings.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, *, reason: str="No reason supplied"):
        if member.top_role >= ctx.guild.me.top_role or member == ctx.guild.owner:
            return await ctx.reply("I can't kick a member whose role is at or above my top role, or the server owner.", mention_author=False)
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.reply("You can't kick a member whose top role is at or above yours.", mention_author=False)
        await member.kick(reason=f"{ctx.author} ({ctx.author.id}): {reason}")
        bot.db.audit(ctx.guild.id,ctx.author.id,"kick",member.id,reason)
        await ctx.reply(f"Kicked {member}. Reason: {reason}", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason: str="No reason supplied"):
        if member.top_role >= ctx.guild.me.top_role or member == ctx.guild.owner:
            return await ctx.reply("I can't ban a member whose role is at or above my top role, or the server owner.", mention_author=False)
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.reply("You can't ban a member whose top role is at or above yours.", mention_author=False)
        await member.ban(reason=f"{ctx.author} ({ctx.author.id}): {reason}", delete_message_seconds=0)
        bot.db.audit(ctx.guild.id,ctx.author.id,"ban",member.id,reason)
        await ctx.reply(f"Banned {member}. Reason: {reason}", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(ctx, member: discord.Member, minutes: int, *, reason: str="No reason supplied"):
        if not 1 <= minutes <= 40320: return await ctx.reply("Timeout duration must be 1–40,320 minutes.", mention_author=False)
        if member.top_role >= ctx.guild.me.top_role or (member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner):
            return await ctx.reply("Role hierarchy prevents that timeout.", mention_author=False)
        await member.timeout(timedelta(minutes=minutes), reason=f"{ctx.author}: {reason}")
        bot.db.audit(ctx.guild.id,ctx.author.id,"timeout",member.id,reason,{"minutes":minutes})
        await ctx.reply(f"Timed out {member.mention} for {minutes} minutes.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(ctx, member: discord.Member, *, reason: str="No reason supplied"):
        await member.timeout(None, reason=f"{ctx.author}: {reason}")
        bot.db.audit(ctx.guild.id,ctx.author.id,"untimeout",member.id,reason)
        await ctx.reply(f"Removed timeout for {member.mention}.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(ctx, amount: int):
        if not 1 <= amount <= 100: return await ctx.reply("Choose 1–100 messages.", mention_author=False)
        deleted=await ctx.channel.purge(limit=amount+1)
        bot.db.audit(ctx.guild.id,ctx.author.id,"purge",ctx.channel.id,f"Deleted {max(0,len(deleted)-1)} messages")
        await ctx.send(f"Deleted {max(0,len(deleted)-1)} messages.", delete_after=5)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def addrole(ctx, member: discord.Member, role: discord.Role):
        if role >= ctx.guild.me.top_role or role.managed or role.permissions.administrator:
            return await ctx.reply("I can't assign that role: it's above my role, managed, or grants Administrator.", mention_author=False)
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.reply("You can't assign a role at or above your top role.", mention_author=False)
        await member.add_roles(role, reason=f"Requested by {ctx.author}")
        bot.db.audit(ctx.guild.id,ctx.author.id,"addrole",member.id,details={"role_id":role.id})
        await ctx.reply(f"Added {role.mention} to {member.mention}.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def removerole(ctx, member: discord.Member, role: discord.Role):
        if role >= ctx.guild.me.top_role or role.managed:
            return await ctx.reply("I can't remove that role due to hierarchy or managed-role restrictions.", mention_author=False)
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.reply("You can't remove a role at or above your top role.", mention_author=False)
        await member.remove_roles(role, reason=f"Requested by {ctx.author}")
        bot.db.audit(ctx.guild.id,ctx.author.id,"removerole",member.id,details={"role_id":role.id})
        await ctx.reply(f"Removed {role.mention} from {member.mention}.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def roleinfo(ctx, *, role: discord.Role):
        await ctx.reply(f"**{role.name}** · ID `{role.id}` · Members {len(role.members)} · Managed {role.managed} · Mentionable {role.mentionable} · Color `{role.color}`", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setlogchannel(ctx, channel: discord.TextChannel):
        bot.db.config(ctx.guild.id,"log_channel_id",channel.id)
        bot.db.audit(ctx.guild.id,ctx.author.id,"setlogchannel",channel.id)
        await ctx.reply(f"Log channel set to {channel.mention}.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def auditlogs(ctx, limit: int=10):
        rows=bot.db.all("SELECT actor_id,action,target,reason,created_at FROM audit WHERE guild_id=? ORDER BY id DESC LIMIT ?",(str(ctx.guild.id),max(1,min(limit,20))))
        await ctx.reply("\n".join(f"{r['created_at'][:19]} · <@{r['actor_id']}> `{r['action']}` target `{r['target'] or '-'}` · {r['reason'] or ''}" for r in rows) or "No audit entries.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setstaffrole(ctx, role: discord.Role):
        bot.db.config(ctx.guild.id,"staff_role_id",role.id)
        bot.db.audit(ctx.guild.id,ctx.author.id,"setstaffrole",role.id)
        await ctx.reply(f"Staff role configured as {role.mention}. Promotion/demotion workflows should use only approved roles.", mention_author=False)
    @bot.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def confirm(ctx, token: str):
        row=bot.db.one("SELECT * FROM confirmations WHERE token=? AND guild_id=? AND actor_id=?",(token,str(ctx.guild.id),str(ctx.author.id)))
        if not row: return await ctx.reply("No matching pending confirmation for you.", mention_author=False)
        # Deliberately do not execute arbitrary serialized actions; each sensitive workflow must implement its own validator.
        bot.db.execute("DELETE FROM confirmations WHERE token=?",(token,))
        await ctx.reply("Confirmation token consumed. No generic action was executed; wire this token to a specific validated workflow before using it for destructive operations.", mention_author=False)
    @bot.command()
    async def cancel(ctx, token: str):
        bot.db.execute("DELETE FROM confirmations WHERE token=? AND actor_id=?",(token,str(ctx.author.id)))
        await ctx.reply("Cancelled the pending confirmation if it existed.", mention_author=False)
