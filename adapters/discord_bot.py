"""Discord adapter — uses discord.py to respond to mentions and DMs, forwarding
prompts to the Claude CLI runner."""

import logging

import discord

import config
from claude_runner import run_claude

logger = logging.getLogger(__name__)

DISCORD_MAX_MESSAGE_LENGTH = 2000

_client: discord.Client | None = None


def _is_authorized(user_id: int) -> bool:
    if not config.ALLOWED_DISCORD_USERS:
        return True
    return user_id in config.ALLOWED_DISCORD_USERS


def _split_message(text: str, limit: int = DISCORD_MAX_MESSAGE_LENGTH) -> list[str]:
    """Split text into chunks that fit within the Discord character limit."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def _build_client() -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info("Discord bot logged in as %s", client.user)

    @client.event
    async def on_message(message: discord.Message) -> None:
        # Ignore own messages
        if message.author == client.user:
            return

        # Respond to DMs or when mentioned in a server
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = client.user in message.mentions if not is_dm else False

        if not is_dm and not is_mentioned:
            return

        if not _is_authorized(message.author.id):
            await message.reply("Sorry, you are not authorized to use this bot.")
            return

        # Strip the bot mention from the prompt
        prompt = message.content
        if client.user:
            prompt = prompt.replace(f"<@{client.user.id}>", "").strip()

        if not prompt:
            await message.reply("Please include a prompt in your message.")
            return

        logger.info(
            "Discord user %s (%s) sent: %s",
            message.author.id,
            message.author.name,
            prompt[:80],
        )

        async with message.channel.typing():
            response = await run_claude(prompt)

        for chunk in _split_message(response):
            await message.reply(chunk)

    return client


async def start() -> None:
    """Start the Discord bot."""
    global _client
    if not config.DISCORD_BOT_TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN is not set.")

    _client = _build_client()
    logger.info("Starting Discord bot…")
    await _client.start(config.DISCORD_BOT_TOKEN)


async def stop() -> None:
    """Gracefully close the Discord client."""
    if _client and not _client.is_closed():
        await _client.close()
