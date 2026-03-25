"""Send prompts to Claude via the Anthropic API and return the response."""

import anthropic

import config


async def run_claude(prompt: str, working_dir: str | None = None) -> str:
    """Send a prompt to Claude via the Anthropic API.

    Args:
        prompt: The user's message.
        working_dir: Unused (kept for interface compatibility).

    Returns:
        Claude's response text, or an error message.
    """
    try:
        client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

        message = await client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from the response
        text_parts = [
            block.text for block in message.content if block.type == "text"
        ]
        return "\n".join(text_parts) or "(no response)"

    except anthropic.AuthenticationError:
        return "Error: Invalid ANTHROPIC_API_KEY. Check your .env file."
    except anthropic.RateLimitError:
        return "Error: Rate limited by the API. Try again in a moment."
    except Exception as exc:
        return f"Error calling Claude API: {exc}"
