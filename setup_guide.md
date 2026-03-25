# Messaging App Integration — Setup Guide

Control Claude Code from Telegram, Slack, or Discord.

## Prerequisites

- Python 3.10+
- Claude Code CLI installed and on PATH (`claude --version` should work)
- A server/machine that stays online (VPS, home server, etc.)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit the config
cp .env.example .env
# Edit .env with your tokens (see platform sections below)

# Start the server
python server.py
```

---

## Telegram (Easiest)

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`, follow the prompts to name your bot
3. Copy the **bot token** BotFather gives you
4. (Optional) Send a message to your bot, then visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to find your **user ID** in the response JSON
5. Edit `.env`:
   ```
   ENABLED_ADAPTERS=telegram
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   ALLOWED_TELEGRAM_USERS=your_user_id
   ```
6. Run `python server.py` — message your bot and it will respond with Claude Code output

---

## Slack

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Under **OAuth & Permissions**, add these Bot Token Scopes:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
3. Under **Event Subscriptions**, enable events and subscribe to:
   - `app_mention`
   - `message.im`
4. Install the app to your workspace
5. Copy the **Bot User OAuth Token** (`xoxb-...`) and **Signing Secret**
6. Edit `.env`:
   ```
   ENABLED_ADAPTERS=slack
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_SIGNING_SECRET=abc123...
   ALLOWED_SLACK_USERS=U01ABCDEF
   ```
7. Run `python server.py` — mention the bot or DM it in Slack

---

## Discord

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. Go to **Bot** tab → click **Add Bot**
3. Enable **Message Content Intent** under Privileged Gateway Intents
4. Copy the **bot token**
5. Go to **OAuth2 → URL Generator**, select `bot` scope with permissions:
   - Send Messages
   - Read Message History
6. Use the generated URL to invite the bot to your server
7. Edit `.env`:
   ```
   ENABLED_ADAPTERS=discord
   DISCORD_BOT_TOKEN=your-token-here
   ALLOWED_DISCORD_USERS=your_discord_user_id
   ```
8. Run `python server.py` — mention the bot or DM it in Discord

---

## Multiple Platforms

Enable multiple adapters at once:

```
ENABLED_ADAPTERS=telegram,slack,discord
```

## Security Notes

- **Always set ALLOWED_*_USERS** in production to restrict who can trigger Claude Code
- **ALLOWED_DIRECTORIES** limits which directories Claude can operate in
- The bot runs Claude Code with the same permissions as the server process
- Consider running on a private network or behind a firewall
