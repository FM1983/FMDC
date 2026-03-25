#!/bin/bash
# One-command setup for Claude Code Telegram Bot
set -e

echo "Installing dependencies..."
pip install python-telegram-bot python-dotenv fastapi uvicorn anthropic slack-bolt "discord.py"

echo ""
echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Edit .env with your keys before starting:"
    echo "  nano .env"
    echo ""
    echo "Required:"
    echo "  ANTHROPIC_API_KEY=sk-ant-..."
    echo "  TELEGRAM_BOT_TOKEN=your-bot-token"
    echo "  ENABLED_ADAPTERS=telegram"
else
    echo ".env already exists, skipping."
fi

echo ""
echo "To start the bot:"
echo "  python server.py"
echo ""
echo "To run in background:"
echo "  nohup python server.py > bot.log 2>&1 &"
