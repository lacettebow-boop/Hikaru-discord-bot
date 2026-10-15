import os, random, time, platform, colorsys
from datetime import datetime, timezone
import discord
from discord.ext import commands

GREETINGS = {
"hi":"Hi there! ✨","hello":"Hello!","hey":"Hey hey!","heya":"Heya!","hiya":"Hiya!","hai":"Hai! 🌸",
"hiii":"Hiiii!","hewwo":"Hewwo!","yo":"Yo!","sup":"Not much — what's up?","greetings":"Greetings!",
"salutations":"Salutations, esteemed human.","howdy":"Howdy!","goodmorning":"Good morning ☀️",
"goodafternoon":"Good afternoon!","goodevening":"Good evening 🌙","goodnight":"Goodnight, rest well!",
"gm":"gm ☀️","gn":"gn 🌙","bye":"Bye! Take care.","cya":"See you later!","seeyou":"See you!",
"goodbye":"Goodbye!","welcome":"Welcome! 🎉"}
FORTUNES = ["A small step will make a big difference.","Curiosity will lead you somewhere interesting.","Give yourself time; progress counts.","A kind word may brighten someone's day.","Try a new approach to an old problem."]
JOKES = ["Why did the computer get cold? It left its Windows open.","I told my keyboard a joke. It didn't react, but the space bar laughed.","Why was the math book worried? It had too many problems."]
FACTS = ["Octopuses have three hearts.","A day on Venus is longer than its year.","Honey can remain stable for a very long time when properly sealed."]
QUOTES = ["Great things are done by a series of small things brought together. — commonly attributed to Vincent van Gogh","It always seems impossible until it's done. — commonly attributed to Nelson Mandela"]
def setup(bot):
    async def say_greeting(ctx): await ctx.reply(GREETINGS.get(ctx.invoked_with.lower(), "Hello!"), mention_author=False)
    for name in GREETINGS:
        bot.command(name=name)(say_greeting)

    @bot.command(name="help")
    async def help_cmd(ctx, page: int = 1):
        pages = [
            "**Hikaru — Help (1/3)**\n`!help`, `!commands`, `!about`, `!info`, `!ping`, `!uptime`, `!botinfo`, `!version`, `!status`\n`!avatar [member]`, `!banner [member]`, `!serverinfo`, `!userinfo [member]`, `!membercount`, `!servericon`, `!serverbanner`\n`!hi`, `!hello`, `!choose`, `!coinflip`, `!dice`, `!8ball`, `!joke`, `!fact`, `!fortune`",
            "**Hikaru — Help (2/3)**\nPersonal: `!addnote`, `!notes`, `!deletenote`, `!addtodo`, `!listtodo`, `!completetodo`, `!settimezone`, `!timezone`, `!birthdayset`\nStaff: `!warn`, `!warnings`, `!kick`, `!ban`, `!timeout`, `!purge`, `!roleinfo`, `!addrole`, `!removerole`\nCommunity: `!suggest`, `!partners`, `!affiliates`, `!ticket`, `!ticketclose`, `!auditlogs`",
            "**Hikaru — Help (3/3)**\nAI: `!chat`, `!generate`, `!explain`, `!summarize`, `!rewrite`, `!brainstorm`, `!translate`\nConfiguration: `!setlogchannel`, `!setwelcomechannel`, `!setstaffrole`, `!setpartnerchannel`, `!setaffiliatechannel`\nUse `!help` for the main menu. Admin-only features require the relevant Discord permission."
        ]
        page=max(1,min(page,len(pages)))
        await ctx.reply(pages[page-1], mention_author=False)

    @bot.command(name="commands")
    async def commands_cmd(ctx):
        names=sorted(c.name for c in bot.commands)
        chunks=[names[i:i+45] for i in range(0,len(names),45)]
        await ctx.reply("**Registered commands**\n" + ", ".join(f"`{n}`" for n in chunks[0]) + (f"\n…and {len(names)-45} more. Use `!help` for categories." if len(names)>45 else ""), mention_author=False)

    @bot.command()
    async def about(ctx): await ctx.reply("Hikaru is a community helper for utility, moderation, productivity, and character fun.", mention_author=False)
    @bot.command()
    async def info(ctx): await about(ctx)
    @bot.command()
    async def botinfo(ctx):
        import discord
        up=discord.utils.utcnow()-bot.started_at
        await ctx.reply(f"**Hikaru** v{os.getenv('BOT_VERSION','0.1.0')} · discord.py {discord.__version__} · Python {platform.python_version()} · Uptime {str(up).split('.')[0]}", mention_author=False)
    @bot.command()
    async def version(ctx): await ctx.reply(f"Hikaru v{os.getenv('BOT_VERSION','0.1.0')}", mention_author=False)
    @bot.command()
    async def status(ctx): await ctx.reply(f"Online · latency {bot.latency*1000:.0f} ms · {len(bot.guilds)} servers", mention_author=False)
    @bot.command()
    async def ping(ctx): await ctx.reply(f"Pong! `{bot.latency*1000:.0f} ms`", mention_author=False)
    @bot.command()
    async def uptime(ctx):
        d=discord.utils.utcnow()-bot.started_at
        await ctx.reply(f"Uptime: {str(d).split('.')[0]}", mention_author=False)
    @bot.command()
    async def invite(ctx):
        await ctx.reply(os.getenv("INVITE_URL") or "Invite link isn't configured. Set INVITE_URL in .env.", mention_author=False)
    @bot.command()
    async def support(ctx):
        await ctx.reply(os.getenv("SUPPORT_URL") or "Support information hasn't been configured yet.", mention_author=False)
    @bot.command()
    async def privacy(ctx):
        await ctx.reply("Hikaru stores only data needed for enabled features in its SQLite database. Notes are user-scoped; birthdays store month/day only. Server owners should protect database backups. Use `!forget` for supported user data deletion.", mention_author=False)
    @bot.command()
    async def credits(ctx): await ctx.reply("Hikaru is a community bot project. Add project acknowledgements here.", mention_author=False)
    @bot.command()
    async def avatar(ctx, member: discord.Member=None):
        user=member or ctx.author
        await ctx.reply(user.display_avatar.url, mention_author=False)
    @bot.command()
    async def banner(ctx, user: discord.User=None):
        user=user or ctx.author
        try: user=await bot.fetch_user(user.id)
        except discord.HTTPException: pass
        await ctx.reply(user.banner.url if user.banner else "No accessible banner found.", mention_author=False)
    @bot.command()
    async def userinfo(ctx, member: discord.Member=None):
        m=member or ctx.author
        joined = m.joined_at.strftime('%Y-%m-%d') if m.joined_at else 'unknown'
        await ctx.reply(f"**{m}** · ID `{m.id}` · joined {joined} · created {m.created_at:%Y-%m-%d}", mention_author=False)
    @bot.command()
    async def serverinfo(ctx):
        if not ctx.guild: return await ctx.reply("Use this in a server.", mention_author=False)
        g=ctx.guild
        await ctx.reply(f"**{g.name}** · ID `{g.id}` · Members {g.member_count} · Channels {len(g.channels)} · Roles {len(g.roles)} · Created {g.created_at:%Y-%m-%d}", mention_author=False)
    @bot.command()
    async def membercount(ctx):
        await ctx.reply(f"Member count: {ctx.guild.member_count if ctx.guild else 'This is a DM.'}", mention_author=False)
    @bot.command()
    async def servericon(ctx):
        await ctx.reply(ctx.guild.icon.url if ctx.guild and ctx.guild.icon else "No server icon available.", mention_author=False)
    @bot.command()
    async def serverbanner(ctx):
        await ctx.reply(ctx.guild.banner.url if ctx.guild and ctx.guild.banner else "No server banner available.", mention_author=False)
    @bot.command()
    async def choose(ctx, *, options: str):
        opts=[x.strip() for x in options.split("|") if x.strip()]
        if len(opts)<2: return await ctx.reply("Provide at least two choices separated by `|`.", mention_author=False)
        await ctx.reply(f"I choose: **{random.choice(opts)}**", mention_author=False)
    @bot.command()
    async def pick(ctx, *, options: str): await choose.callback(ctx, options=options)
    @bot.command()
    async def random_cmd(ctx, *, options: str=""):
        if options:
            opts=[x.strip() for x in options.split("|") if x.strip()]
            return await ctx.reply(random.choice(opts) if opts else "Give me options separated by `|`.", mention_author=False)
        await ctx.reply(f"Random number: {random.randint(1,100)}", mention_author=False)
    bot.add_command(commands.Command(random_cmd, name="random"))
    @bot.command()
    async def coinflip(ctx): await ctx.reply(random.choice(["Heads 🪙","Tails 🪙"]), mention_author=False)
    @bot.command()
    async def dice(ctx, sides: int=6):
        if not 2 <= sides <= 1000000: return await ctx.reply("Sides must be between 2 and 1,000,000.", mention_author=False)
        await ctx.reply(f"🎲 {random.randint(1,sides)} (d{sides})", mention_author=False)
    @bot.command()
    async def roll(ctx, maximum: int=100):
        if not 1 <= maximum <= 1000000: return await ctx.reply("Maximum must be 1–1,000,000.", mention_author=False)
        await ctx.reply(f"🎲 {random.randint(1,maximum)}", mention_author=False)
    @bot.command(name="8ball")
    async def eightball(ctx, *, question: str):
        await ctx.reply(random.choice(["Absolutely.","Probably!","Ask again later.","The outlook is unclear.","I wouldn't count on it.","Very likely."]), mention_author=False)
    bot.add_command(commands.Command(eightball, name="magic8ball"))
    @bot.command()
    async def fortune(ctx): await ctx.reply(random.choice(FORTUNES), mention_author=False)
    @bot.command()
    async def dailyfortune(ctx): await fortune(ctx)
    @bot.command()
    async def joke(ctx): await ctx.reply(random.choice(JOKES), mention_author=False)
    @bot.command()
    async def pun(ctx): await ctx.reply("I used to hate facial hair, but then it grew on me.", mention_author=False)
    @bot.command()
    async def fact(ctx): await ctx.reply(random.choice(FACTS), mention_author=False)
    bot.add_command(commands.Command(lambda: None, name="unused") ) if False else None
    @bot.command()
    async def funfact(ctx): await fact(ctx)
    @bot.command()
    async def quote(ctx): await ctx.reply(random.choice(QUOTES), mention_author=False)
    @bot.command()
    async def dailyquote(ctx): await quote(ctx)
    @bot.command()
    async def inspire(ctx): await ctx.reply(random.choice(FORTUNES), mention_author=False)
    @bot.command()
    async def motivate(ctx): await inspire(ctx)
    @bot.command()
    async def comfort(ctx): await ctx.reply("Take things one step at a time. You don't have to solve everything all at once. 💛", mention_author=False)
    @bot.command()
    async def encourage(ctx): await ctx.reply("You've got this. Small progress is still progress. ✨", mention_author=False)
    @bot.command()
    async def vibecheck(ctx): await ctx.reply(f"Vibe check: {random.choice(['✨ immaculate','🌱 quietly thriving','🌙 mysterious','🎉 delightfully chaotic','☕ cozy'])}", mention_author=False)
    @bot.command()
    async def rate(ctx, *, thing: str): await ctx.reply(f"I rate **{discord.utils.escape_markdown(thing)}** {random.randint(1,10)}/10 — purely for fun!", mention_author=False)
    @bot.command()
    async def color(ctx):
        c="#%06X" % random.randint(0,0xFFFFFF)
        await ctx.reply(f"Random color: `{c}`", mention_author=False)
    @bot.command()
    async def randomcolor(ctx): await color(ctx)
    @bot.command()
    async def say(ctx, *, text: str):
        if ctx.author.guild_permissions.manage_messages:
            await ctx.send(text[:1800], allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.reply("You need Manage Messages to use `!say`.", mention_author=False)
