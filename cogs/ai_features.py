import os
import random

from discord.ext import commands


async def generate_ai_response(ctx, prompt: str, mode: str = "helpful"):
    """Generate a text response through Google's Gemini API."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        await ctx.reply(
            "AI features are disabled. Add your Gemini API key to "
            "`GEMINI_API_KEY` in your private `.env` file, then restart Hikaru. "
            "Never paste your key into Discord or share it with anyone.",
            mention_author=False,
        )
        return

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        response = await client.chat.completions.create(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Hikaru, a helpful Discord community assistant. "
                        "Keep responses friendly, safe, and concise. Do not claim "
                        "to be a real person or professional."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Task: {mode}\nUser request: {prompt[:5000]}",
                },
            ],
            max_tokens=700,
        )
        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            answer = "Gemini returned an empty response. Please try again."

        # Stay under Discord's per-message content limit.
        for i in range(0, len(answer), 1800):
            await ctx.reply(answer[i:i + 1800], mention_author=False)

    except Exception:
        # Avoid exposing API credentials or raw provider error details in Discord.
        await ctx.reply(
            "The AI request failed. Check that your Gemini API key is valid, "
            "the selected model is available to your key, and your connection works. "
            "For technical details, check the bot's private console logs.",
            mention_author=False,
        )


def setup(bot):
    @bot.command()
    async def chat(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "conversational chat")

    @bot.command()
    async def generate(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "text generation")

    @bot.command()
    async def explain(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "explain simply")

    @bot.command()
    async def summarize(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "summarize")

    @bot.command()
    async def rewrite(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "rewrite while preserving meaning")

    @bot.command()
    async def brainstorm(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "brainstorm ideas")

    @bot.command()
    async def ideas(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "generate ideas")

    @bot.command()
    async def translate(ctx, *, prompt: str):
        await generate_ai_response(
            ctx, prompt, "translate; ask a brief clarification if target language is missing"
        )

    @bot.command()
    async def studyhelp(ctx, *, prompt: str):
        await generate_ai_response(
            ctx, prompt, "study coach; explain concepts rather than simply doing all work"
        )

    @bot.command()
    async def codinghelp(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "coding help; explain likely fixes")

    @bot.command()
    async def creativehelp(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "creative project brainstorming")

    @bot.command()
    async def characterchat(ctx, *, prompt: str):
        await generate_ai_response(
            ctx, prompt, "fictional character roleplay; clearly fictional, non-explicit"
        )

    @bot.command()
    async def roleplay(ctx, *, prompt: str):
        await generate_ai_response(
            ctx, prompt, "fictional roleplay scene; safe and non-explicit"
        )

    @bot.command()
    async def headcanon(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "fictional headcanon")

    @bot.command()
    async def dialogue(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "write fictional dialogue")

    @bot.command()
    async def scenario(ctx, *, prompt: str):
        await generate_ai_response(ctx, prompt, "creative scenario")

    @bot.command()
    async def randomprompt(ctx):
        prompts = [
            "Write a scene during a sudden summer storm.",
            "Invent a festival for a tiny fictional town.",
            "Describe a character's most treasured object.",
            "Create a mystery with three clues.",
        ]
        await ctx.reply(random.choice(prompts), mention_author=False)
