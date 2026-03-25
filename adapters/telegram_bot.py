"""Telegram adapter — receives messages via python-telegram-bot and forwards them
to the Claude CLI runner."""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from claude_runner import run_claude

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def _is_authorized(user_id: int) -> bool:
    """Return True when the user is in the allow-list (or the list is empty)."""
    if not config.ALLOWED_TELEGRAM_USERS:
        return True
    return user_id in config.ALLOWED_TELEGRAM_USERS


def _split_message(text: str, limit: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """Split *text* into chunks that fit within the Telegram character limit."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Try to split at the last newline within the limit
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "Hello! Send me any message and I will forward it to Claude Code CLI "
        "and return the response.\n\n"
        "Just type your prompt as a regular message."
    )


async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward a user message to Claude CLI and reply with the result."""
    user = update.effective_user
    if not _is_authorized(user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    prompt = update.message.text
    if not prompt:
        return

    logger.info("Telegram user %s (%s) sent: %s", user.id, user.username, prompt[:80])

    await update.message.chat.send_action("typing")
    response = await run_claude(prompt)

    for chunk in _split_message(response):
        await update.message.reply_text(chunk)


def create_application() -> Application:
    """Build and return the Telegram Application (does NOT start polling)."""
    if not config.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", _start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_message))
    return app


async def start() -> None:
    """Initialize and start the Telegram bot (polling mode)."""
    app = create_application()
    logger.info("Starting Telegram bot (polling)…")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()


async def stop() -> None:
    """Gracefully stop the Telegram bot if it was started."""
    # Stopping is handled by the Application context; provided for symmetry.
    pass
