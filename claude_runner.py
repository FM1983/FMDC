"""Run Claude Code CLI as a subprocess and return the output."""

import asyncio
import os
from pathlib import Path

import config


async def run_claude(prompt: str, working_dir: str | None = None) -> str:
    """Execute `claude -p "prompt"` and return stdout.

    Args:
        prompt: The prompt string to send to Claude CLI.
        working_dir: Directory to run the command in.  Defaults to
            ``config.CLAUDE_WORKING_DIR``.

    Returns:
        The CLI stdout as a string, or an error message.
    """
    cwd = working_dir or config.CLAUDE_WORKING_DIR

    # Security: ensure the working directory is within allowed paths
    resolved = str(Path(cwd).resolve())
    if not any(
        resolved == allowed or resolved.startswith(allowed + os.sep)
        for allowed in (str(Path(d).resolve()) for d in config.ALLOWED_DIRECTORIES)
    ):
        return f"Error: directory '{cwd}' is not in the allowed directories list."

    if not Path(resolved).is_dir():
        return f"Error: directory '{cwd}' does not exist."

    try:
        process = await asyncio.create_subprocess_exec(
            "claude",
            "-p",
            prompt,
            cwd=resolved,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=config.CLAUDE_TIMEOUT,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            return (
                f"Error: Claude CLI timed out after {config.CLAUDE_TIMEOUT} seconds."
            )

        if process.returncode != 0:
            err = stderr.decode().strip()
            return f"Error (exit {process.returncode}): {err}" if err else (
                f"Error: Claude CLI exited with code {process.returncode}."
            )

        return stdout.decode().strip() or "(no output)"

    except FileNotFoundError:
        return "Error: 'claude' CLI not found. Make sure it is installed and on PATH."
    except Exception as exc:
        return f"Error running Claude CLI: {exc}"
