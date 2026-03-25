"""Main entry point — FastAPI server that starts enabled messaging adapters."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Track background tasks so we can cancel them on shutdown
_adapter_tasks: list[asyncio.Task] = []


async def _start_adapter(name: str) -> None:
    """Import and start a single adapter by name."""
    try:
        if name == "telegram":
            from adapters import telegram_bot
            await telegram_bot.start()
        elif name == "slack":
            from adapters import slack_bot
            await slack_bot.start()
        elif name == "discord":
            from adapters import discord_bot
            await discord_bot.start()
        else:
            logger.warning("Unknown adapter: %s", name)
    except Exception:
        logger.exception("Failed to start %s adapter", name)


async def _stop_adapters() -> None:
    """Stop all running adapter tasks."""
    for task in _adapter_tasks:
        task.cancel()
    if _adapter_tasks:
        await asyncio.gather(*_adapter_tasks, return_exceptions=True)
    _adapter_tasks.clear()

    # Call individual stop helpers
    for name in config.ENABLED_ADAPTERS:
        try:
            if name == "telegram":
                from adapters import telegram_bot
                await telegram_bot.stop()
            elif name == "slack":
                from adapters import slack_bot
                await slack_bot.stop()
            elif name == "discord":
                from adapters import discord_bot
                await discord_bot.stop()
        except Exception:
            logger.exception("Error stopping %s adapter", name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start adapters on startup and tear them down on shutdown."""
    if not config.ENABLED_ADAPTERS:
        logger.warning(
            "No adapters enabled. Set ENABLED_ADAPTERS (e.g. 'telegram,slack,discord')."
        )
    for name in config.ENABLED_ADAPTERS:
        logger.info("Starting adapter: %s", name)
        task = asyncio.create_task(_start_adapter(name))
        _adapter_tasks.append(task)

    yield

    logger.info("Shutting down adapters…")
    await _stop_adapters()


app = FastAPI(title="Claude Code Messaging Bridge", lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Simple health-check endpoint."""
    return {
        "status": "ok",
        "enabled_adapters": config.ENABLED_ADAPTERS,
    }


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
