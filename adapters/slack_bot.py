"""Slack adapter — uses slack_bolt to listen for mentions and DMs, then forwards
prompts to the Claude CLI runner."""

import asyncio
import logging
import re

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

import config
from claude_runner import run_claude

logger = logging.getLogger(__name__)

_app: AsyncApp | None = None


def _is_authorized(user_id: str) -> bool:
    if not config.ALLOWED_SLACK_USERS:
        return True
    return user_id in config.ALLOWED_SLACK_USERS


def _strip_mention(text: str) -> str:
    """Remove the leading ``<@BOT_ID>`` mention from the message text."""
    return re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()


def _build_app() -> AsyncApp:
    if not config.SLACK_BOT_TOKEN or not config.SLACK_SIGNING_SECRET:
        raise ValueError("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set.")

    app = AsyncApp(
        token=config.SLACK_BOT_TOKEN,
        signing_secret=config.SLACK_SIGNING_SECRET,
    )

    @app.event("app_mention")
    async def handle_mention(event: dict, say) -> None:
        user = event.get("user", "")
        if not _is_authorized(user):
            await say("Sorry, you are not authorized to use this bot.")
            return

        prompt = _strip_mention(event.get("text", ""))
        if not prompt:
            await say("Please include a prompt after mentioning me.")
            return

        logger.info("Slack user %s mentioned bot: %s", user, prompt[:80])
        response = await run_claude(prompt)
        await say(response)

    @app.event("message")
    async def handle_dm(event: dict, say) -> None:
        # Only respond to direct messages (channel type "im") that are not bot messages
        if event.get("channel_type") != "im":
            return
        if event.get("bot_id"):
            return

        user = event.get("user", "")
        if not _is_authorized(user):
            await say("Sorry, you are not authorized to use this bot.")
            return

        prompt = event.get("text", "").strip()
        if not prompt:
            return

        logger.info("Slack DM from %s: %s", user, prompt[:80])
        response = await run_claude(prompt)
        await say(response)

    return app


async def start() -> None:
    """Start the Slack bot using Socket Mode."""
    global _app
    _app = _build_app()
    handler = AsyncSocketModeHandler(_app)
    logger.info("Starting Slack bot (socket mode)…")
    await handler.start_async()


async def stop() -> None:
    """Stop the Slack bot."""
    pass
