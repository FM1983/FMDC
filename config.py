"""Central configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


# Claude API settings
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
CLAUDE_WORKING_DIR: str = os.getenv("CLAUDE_WORKING_DIR", os.getcwd())
CLAUDE_TIMEOUT: int = int(os.getenv("CLAUDE_TIMEOUT", "300"))

# Security: directories the runner is allowed to operate in
ALLOWED_DIRECTORIES: list[str] = [
    d.strip()
    for d in os.getenv("ALLOWED_DIRECTORIES", CLAUDE_WORKING_DIR).split(",")
    if d.strip()
]

# Enabled adapters (comma-separated: "telegram,slack,discord")
ENABLED_ADAPTERS: list[str] = [
    a.strip().lower()
    for a in os.getenv("ENABLED_ADAPTERS", "").split(",")
    if a.strip()
]

# Telegram
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_TELEGRAM_USERS: list[int] = [
    int(uid.strip())
    for uid in os.getenv("ALLOWED_TELEGRAM_USERS", "").split(",")
    if uid.strip()
]

# Slack
SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
ALLOWED_SLACK_USERS: list[str] = [
    uid.strip()
    for uid in os.getenv("ALLOWED_SLACK_USERS", "").split(",")
    if uid.strip()
]

# Discord
DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
ALLOWED_DISCORD_USERS: list[int] = [
    int(uid.strip())
    for uid in os.getenv("ALLOWED_DISCORD_USERS", "").split(",")
    if uid.strip()
]
