"""Telegram adapter — Claude Code via Telegram with conversation memory,
tool use, and shortcut commands."""

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
from claude_runner import run_claude, clear_history

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def _is_authorized(user_id: int) -> bool:
    if not config.ALLOWED_TELEGRAM_USERS:
        return True
    return user_id in config.ALLOWED_TELEGRAM_USERS


def _split_message(text: str, limit: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
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


async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Claude Code is connected.\n\n"
        "I can read/edit files, run commands, manage git, search code — "
        "anything you'd do in a terminal.\n\n"
        "Commands:\n"
        "/clear — reset conversation\n"
        "/status — git status\n"
        "/log — recent git log\n"
        "/diff — git diff\n"
        "/files — list project files\n"
        "/run <cmd> — run a shell command\n\n"
        "Or just tell me what to do in plain English."
    )


async def _clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_authorized(user.id):
        return
    clear_history(f"telegram_{user.id}")
    await update.message.reply_text("Conversation cleared.")


async def _shortcut_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle shortcut commands that map to prompts."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return

    cmd = update.message.text.split()[0].lstrip("/")
    args = update.message.text[len(cmd) + 1:].strip()

    prompt_map = {
        "status": "Run git status and give me a brief summary.",
        "log": "Run git log --oneline -10 and show me the results.",
        "diff": "Run git diff and summarize the changes.",
        "files": "List the files in the project directory.",
        "run": f"Run this command and show the output: {args}" if args else "What command do you want me to run?",
        "commit": f"Stage the relevant changes and commit with message: {args}" if args else "Run git status, then suggest a commit message for the current changes.",
        "push": "Push the current branch to origin.",
        "test": f"Run the tests: {args}" if args else "Find and run the project's tests.",
        "search": f"Search the codebase for: {args}" if args else "What should I search for?",
    }

    prompt = prompt_map.get(cmd, update.message.text)

    await update.message.chat.send_action("typing")
    response = await run_claude(prompt, user_id=f"telegram_{user.id}")
    for chunk in _split_message(response):
        await update.message.reply_text(chunk)


async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_authorized(user.id):
        await update.message.reply_text("Not authorized.")
        return

    prompt = update.message.text
    if not prompt:
        return

    logger.info("Telegram user %s (%s) sent: %s", user.id, user.username, prompt[:80])

    await update.message.chat.send_action("typing")
    response = await run_claude(prompt, user_id=f"telegram_{user.id}")

    for chunk in _split_message(response):
        await update.message.reply_text(chunk)


def create_application() -> Application:
    if not config.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", _start_command))
    app.add_handler(CommandHandler("clear", _clear_command))
    for cmd in ("status", "log", "diff", "files", "run", "commit", "push", "test", "search"):
        app.add_handler(CommandHandler(cmd, _shortcut_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_message))
    return app


async def start() -> None:
    app = create_application()
    logger.info("Starting Telegram bot (polling)…")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()


async def stop() -> None:
    pass
