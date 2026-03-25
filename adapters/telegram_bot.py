"""Telegram adapter — Claude Code via Telegram with voice, photos, file
upload/download, progress indicators, and shortcut commands."""

import asyncio
import base64
import io
import logging
import os
import tempfile

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from claude_runner import run_claude, clear_history

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

# Quick-action inline keyboard
QUICK_ACTIONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("git status", callback_data="quick_status"),
        InlineKeyboardButton("git diff", callback_data="quick_diff"),
        InlineKeyboardButton("git log", callback_data="quick_log"),
    ],
    [
        InlineKeyboardButton("list files", callback_data="quick_files"),
        InlineKeyboardButton("run tests", callback_data="quick_test"),
        InlineKeyboardButton("workstreams", callback_data="quick_workstreams"),
    ],
])


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


def _get_prompt_for_command(cmd: str, args: str) -> str:
    """Map a command name to a prompt string."""
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
        "sessions": (
            "List all Claude Code sessions by scanning ~/.claude/projects/. "
            "For each project directory, read the .jsonl files, get the first user message "
            "and the file modification time. Show me: project name, session start time, "
            "and what the session was about (first user message). Sort by most recent first. "
            "Format as a clean list."
        ),
        "workstreams": (
            "Give me an overview of all active workstreams. Do this:\n"
            "1. Run `find ~/.claude/projects -name '*.jsonl' -mmin -1440` to find sessions active in the last 24h\n"
            "2. For each, read the first few lines to get the topic\n"
            "3. Check all git repos under the home directory for recent branch activity: "
            "run `find ~ -maxdepth 3 -name .git -type d 2>/dev/null` then `git -C <dir> branch -v --sort=-committerdate | head -5` for each\n"
            "4. Summarize everything as a brief status report of what's being worked on"
        ),
    }
    return prompt_map.get(cmd, args or cmd)


async def _send_with_progress(update_or_query, user_id: str, prompt: str,
                               image_data=None, chat=None, reply_to=None):
    """Send a prompt to Claude with progress updates in Telegram."""
    # Determine chat to send to
    if chat is None:
        chat = update_or_query.message.chat if hasattr(update_or_query, 'message') else update_or_query.message.chat

    progress_msg = await chat.send_message("Thinking...")
    last_update = ""

    async def progress_callback(status: str):
        nonlocal last_update
        if status != last_update:
            last_update = status
            try:
                await progress_msg.edit_text(f"Working... {status}")
            except Exception:
                pass  # Telegram rate limit or message unchanged

    response = await run_claude(
        prompt,
        user_id=user_id,
        image_data=image_data,
        progress_callback=progress_callback,
    )

    # Delete progress message and send real response
    try:
        await progress_msg.delete()
    except Exception:
        pass

    chunks = _split_message(response)
    for i, chunk in enumerate(chunks):
        # Add quick-action buttons to the last chunk
        reply_markup = QUICK_ACTIONS if i == len(chunks) - 1 else None
        await chat.send_message(chunk, reply_markup=reply_markup)


# ── Command handlers ──

async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Claude Code is connected.\n\n"
        "I can read/edit files, run commands, manage git, search code — "
        "anything you'd do in a terminal.\n\n"
        "You can also:\n"
        "- Send a voice message and I'll act on it\n"
        "- Send a screenshot/photo and I'll analyze it\n"
        "- Send a file to save it to the project\n"
        "- Ask me for a file and I'll send it to you\n\n"
        "Commands:\n"
        "/clear — reset conversation\n"
        "/status /log /diff /files\n"
        "/run <cmd> /commit <msg> /push\n"
        "/test /search <term>\n"
        "/sessions /workstreams\n"
        "/actions — show quick-action buttons\n\n"
        "Or just tell me what to do in plain English.",
        reply_markup=QUICK_ACTIONS,
    )


async def _clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_authorized(user.id):
        return
    clear_history(f"telegram_{user.id}")
    await update.message.reply_text("Conversation cleared.", reply_markup=QUICK_ACTIONS)


async def _actions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show quick-action inline keyboard."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return
    await update.message.reply_text("Quick actions:", reply_markup=QUICK_ACTIONS)


async def _shortcut_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle shortcut commands that map to prompts."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return

    cmd = update.message.text.split()[0].lstrip("/")
    args = update.message.text[len(cmd) + 1:].strip()
    prompt = _get_prompt_for_command(cmd, args)

    logger.info("Telegram user %s cmd: /%s %s", user.id, cmd, args[:50])
    await _send_with_progress(update, f"telegram_{user.id}", prompt, chat=update.message.chat)


# ── Inline button handler ──

async def _button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    if not _is_authorized(user.id):
        return

    cmd = query.data.replace("quick_", "")
    prompt = _get_prompt_for_command(cmd, "")

    logger.info("Telegram user %s button: %s", user.id, cmd)
    await _send_with_progress(update, f"telegram_{user.id}", prompt, chat=query.message.chat)


# ── Message handlers ──

async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    user = update.effective_user
    if not _is_authorized(user.id):
        await update.message.reply_text("Not authorized.")
        return

    prompt = update.message.text
    if not prompt:
        return

    logger.info("Telegram user %s (%s) sent: %s", user.id, user.username, prompt[:80])
    await _send_with_progress(update, f"telegram_{user.id}", prompt, chat=update.message.chat)


async def _handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages — download, transcribe via Claude, and act on it."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return

    logger.info("Telegram user %s sent voice message", user.id)
    progress_msg = await update.message.reply_text("Transcribing voice message...")

    try:
        # Download the voice file
        voice = update.message.voice or update.message.audio
        voice_file = await context.bot.get_file(voice.file_id)

        buf = io.BytesIO()
        await voice_file.download_to_memory(buf)
        buf.seek(0)
        voice_bytes = buf.read()

        # Save temporarily and transcribe via whisper or pass to Claude
        # Claude can't directly process audio, so we use a local transcription
        # First try: use the caption or save as file and use a command
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(voice_bytes)
            tmp_path = tmp.name

        # Try whisper CLI, fall back to describing what we got
        import subprocess
        try:
            result = subprocess.run(
                ["whisper", tmp_path, "--model", "base", "--output_format", "txt", "--output_dir", "/tmp"],
                capture_output=True, text=True, timeout=60,
            )
            txt_path = tmp_path.replace(".ogg", ".txt")
            if os.path.exists(txt_path):
                with open(txt_path) as f:
                    transcription = f.read().strip()
                os.unlink(txt_path)
            else:
                transcription = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # No whisper installed — try macOS say/afplay or just tell user
            try:
                # Try python SpeechRecognition as fallback
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                # Convert ogg to wav first
                wav_path = tmp_path.replace(".ogg", ".wav")
                subprocess.run(
                    ["ffmpeg", "-i", tmp_path, "-ar", "16000", "-ac", "1", wav_path, "-y"],
                    capture_output=True, timeout=30,
                )
                with sr.AudioFile(wav_path) as source:
                    audio = recognizer.record(source)
                transcription = recognizer.recognize_google(audio)
                os.unlink(wav_path)
            except Exception:
                os.unlink(tmp_path)
                await progress_msg.edit_text(
                    "Voice messages need either `whisper` or `ffmpeg` + `SpeechRecognition` installed.\n\n"
                    "Install with:\n"
                    "`pip3 install openai-whisper`\n"
                    "or\n"
                    "`pip3 install SpeechRecognition` and `brew install ffmpeg`"
                )
                return

        os.unlink(tmp_path)

        if not transcription:
            await progress_msg.edit_text("Couldn't transcribe the voice message. Try again or type instead.")
            return

        await progress_msg.edit_text(f"Heard: \"{transcription}\"\n\nProcessing...")

        # Now send the transcription as a regular prompt
        try:
            await progress_msg.delete()
        except Exception:
            pass

        await _send_with_progress(update, f"telegram_{user.id}", transcription, chat=update.message.chat)

    except Exception as e:
        logger.exception("Voice handling error")
        await progress_msg.edit_text(f"Error processing voice: {e}")


async def _handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photos/screenshots — send to Claude Vision for analysis."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return

    logger.info("Telegram user %s sent photo", user.id)

    # Get the highest resolution photo
    photo = update.message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)

    buf = io.BytesIO()
    await photo_file.download_to_memory(buf)
    buf.seek(0)
    photo_bytes = buf.read()

    # Encode as base64 for Claude Vision
    b64_data = base64.b64encode(photo_bytes).decode("utf-8")
    image_data = [{"media_type": "image/jpeg", "data": b64_data}]

    # Use caption as prompt, or default
    prompt = update.message.caption or "What's in this image? If it's a screenshot of code or an error, analyze it and suggest fixes."

    await _send_with_progress(
        update, f"telegram_{user.id}", prompt,
        image_data=image_data, chat=update.message.chat,
    )


async def _handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file uploads — save to project or analyze."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return

    doc = update.message.document
    logger.info("Telegram user %s sent file: %s", user.id, doc.file_name)

    # Download the file
    tg_file = await context.bot.get_file(doc.file_id)
    buf = io.BytesIO()
    await tg_file.download_to_memory(buf)
    buf.seek(0)
    file_bytes = buf.read()

    # Save to project directory
    save_path = os.path.join(config.CLAUDE_WORKING_DIR, doc.file_name)
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    size_kb = len(file_bytes) / 1024
    prompt = (
        update.message.caption
        or f"I just saved the file '{doc.file_name}' ({size_kb:.1f} KB) to the project directory. "
           f"Acknowledge this and briefly describe what it appears to be if you can tell from the filename."
    )

    await _send_with_progress(update, f"telegram_{user.id}", prompt, chat=update.message.chat)


async def _handle_sendfile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /sendfile command — send a project file to the user."""
    user = update.effective_user
    if not _is_authorized(user.id):
        return

    args = update.message.text.replace("/sendfile", "").strip()
    if not args:
        await update.message.reply_text("Usage: /sendfile <path>\nExample: /sendfile server.py")
        return

    # Resolve path
    if not os.path.isabs(args):
        filepath = os.path.join(config.CLAUDE_WORKING_DIR, args)
    else:
        filepath = args

    if not os.path.isfile(filepath):
        await update.message.reply_text(f"File not found: {args}")
        return

    try:
        await update.message.reply_document(
            document=open(filepath, "rb"),
            filename=os.path.basename(filepath),
        )
    except Exception as e:
        await update.message.reply_text(f"Error sending file: {e}")


# ── Application setup ──

def create_application() -> Application:
    if not config.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", _start_command))
    app.add_handler(CommandHandler("clear", _clear_command))
    app.add_handler(CommandHandler("actions", _actions_command))
    app.add_handler(CommandHandler("sendfile", _handle_sendfile))
    for cmd in ("status", "log", "diff", "files", "run", "commit", "push", "test", "search", "sessions", "workstreams"):
        app.add_handler(CommandHandler(cmd, _shortcut_command))

    # Inline button callbacks
    app.add_handler(CallbackQueryHandler(_button_callback))

    # Media handlers
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, _handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, _handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, _handle_document))

    # Text messages (last, as catch-all)
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
