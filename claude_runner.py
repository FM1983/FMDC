"""Claude API runner with conversation memory, tool use, and vision support."""

import asyncio
import base64
import os
import subprocess
from collections import defaultdict
from pathlib import Path

import anthropic

import config

# Per-user conversation history: user_id -> list of messages
_conversations: dict[str, list[dict]] = defaultdict(list)

# Maximum conversation history to keep (to control token usage)
MAX_HISTORY = 40

SYSTEM_PROMPT = """You are Claude Code, an AI software engineer connected to a live development server via Telegram.
You are the same Claude that powers Anthropic's Claude Code CLI — just accessible from a messaging app.

You have full access to the project filesystem and shell. You can:
- Read, write, and edit any file in the project
- Run any shell command (git, npm, pip, python, make, docker, etc.)
- Search codebases with grep
- Create commits, branches, and manage git workflows
- Run tests, linters, and build tools
- Install packages and manage dependencies

Working directory: {work_dir}

## How to behave
- Be concise — the user is on a phone. Short paragraphs, no walls of text.
- When asked to do something, DO IT with tools. Don't just describe what to do.
- After making changes, briefly confirm what you did (e.g. "Edited config.py — added the new endpoint").
- When showing code, keep snippets short and relevant. Use the read_file tool instead of pasting entire files.
- For multi-step tasks, work through them sequentially using tools.
- If a command fails, diagnose and fix it. Don't just report the error.
- Always read a file before editing it.
- When making git commits, write clear commit messages.

## Git workflow
- Check status before committing: run `git status` and `git diff`
- Stage specific files rather than `git add -A`
- Write descriptive commit messages
- Push when asked, always to the current branch

## Safety
- Never delete files without confirming with the user first
- Never force-push or reset --hard without asking
- Never expose secrets, API keys, or credentials in responses
""".strip()

# Tool definitions for the Claude API
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file. Returns the file content as text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of lines to read. Defaults to 200.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating it if it doesn't exist or overwriting if it does.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file.",
                },
                "content": {
                    "type": "string",
                    "description": "The full content to write to the file.",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace a specific string in a file with new content. The old_string must match exactly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit.",
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact string to find and replace.",
                },
                "new_string": {
                    "type": "string",
                    "description": "The replacement string.",
                },
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories at a given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to the working directory.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return its output. Use for git, grep, tests, builds, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Defaults to 60.",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "search_files",
        "description": "Search for a pattern in files using grep. Returns matching lines with file paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search in. Defaults to working directory.",
                },
                "file_glob": {
                    "type": "string",
                    "description": "File glob pattern to filter (e.g. '*.py', '*.js').",
                },
            },
            "required": ["pattern"],
        },
    },
]


def _resolve_path(path: str) -> str:
    """Resolve a path relative to the working directory, with security check."""
    if not os.path.isabs(path):
        path = os.path.join(config.CLAUDE_WORKING_DIR, path)
    resolved = str(Path(path).resolve())
    allowed = any(
        resolved == a or resolved.startswith(a + os.sep)
        for a in (str(Path(d).resolve()) for d in config.ALLOWED_DIRECTORIES)
    )
    if not allowed:
        raise PermissionError(f"Access denied: {path} is outside allowed directories.")
    return resolved


def _execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool and return the result as a string."""
    try:
        if name == "read_file":
            path = _resolve_path(input_data["path"])
            limit = input_data.get("limit", 200)
            with open(path) as f:
                lines = f.readlines()[:limit]
            return "".join(lines) or "(empty file)"

        elif name == "write_file":
            path = _resolve_path(input_data["path"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(input_data["content"])
            return f"Written to {input_data['path']}"

        elif name == "edit_file":
            path = _resolve_path(input_data["path"])
            with open(path) as f:
                content = f.read()
            old = input_data["old_string"]
            if old not in content:
                return f"Error: old_string not found in {input_data['path']}"
            content = content.replace(old, input_data["new_string"], 1)
            with open(path, "w") as f:
                f.write(content)
            return f"Edited {input_data['path']}"

        elif name == "list_directory":
            path = _resolve_path(input_data.get("path", config.CLAUDE_WORKING_DIR))
            entries = sorted(os.listdir(path))
            result = []
            for e in entries:
                full = os.path.join(path, e)
                prefix = "d " if os.path.isdir(full) else "f "
                result.append(prefix + e)
            return "\n".join(result) or "(empty directory)"

        elif name == "run_command":
            timeout = min(input_data.get("timeout", 60), 120)
            result = subprocess.run(
                input_data["command"],
                shell=True,
                cwd=config.CLAUDE_WORKING_DIR,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            if result.returncode != 0:
                output += f"\n(exit code {result.returncode})"
            return output.strip() or "(no output)"

        elif name == "search_files":
            cmd = ["grep", "-rn", input_data["pattern"]]
            if "file_glob" in input_data:
                cmd += ["--include", input_data["file_glob"]]
            path = _resolve_path(input_data.get("path", config.CLAUDE_WORKING_DIR))
            cmd.append(path)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
            )
            return result.stdout.strip()[:3000] or "(no matches)"

        else:
            return f"Unknown tool: {name}"

    except PermissionError as e:
        return str(e)
    except subprocess.TimeoutExpired:
        return "Error: command timed out."
    except Exception as e:
        return f"Error: {e}"


def clear_history(user_id: str) -> None:
    """Clear conversation history for a user."""
    _conversations.pop(user_id, None)


def _build_user_content(prompt: str, image_data: list[dict] | None = None) -> list[dict]:
    """Build a user message content array, optionally with images."""
    content = []
    if image_data:
        for img in image_data:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img["media_type"],
                    "data": img["data"],
                },
            })
    content.append({"type": "text", "text": prompt})
    return content


async def run_claude(
    prompt: str,
    user_id: str = "default",
    image_data: list[dict] | None = None,
    progress_callback=None,
) -> str:
    """Send a prompt to Claude with conversation history and tool use.

    Args:
        prompt: The user's message.
        user_id: Unique user identifier for conversation memory.
        image_data: Optional list of {"media_type": "image/jpeg", "data": "base64..."}.
        progress_callback: Optional async callable(str) for progress updates.

    Returns:
        Claude's final text response.
    """
    try:
        client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        history = _conversations[user_id]

        # Build user message with optional images
        user_content = _build_user_content(prompt, image_data)
        history.append({"role": "user", "content": user_content})

        # Trim history if too long
        if len(history) > MAX_HISTORY:
            history[:] = history[-MAX_HISTORY:]

        system = SYSTEM_PROMPT.format(work_dir=config.CLAUDE_WORKING_DIR)

        # Tool use loop — Claude may call tools multiple times
        for iteration in range(10):
            response = await client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=4096,
                system=system,
                tools=TOOLS,
                messages=history,
            )

            # If no tool use, extract final text and return
            if response.stop_reason != "tool_use":
                text_parts = [
                    block.text for block in response.content
                    if block.type == "text"
                ]
                assistant_msg = "\n".join(text_parts) or "(no response)"
                history.append({"role": "assistant", "content": response.content})
                return assistant_msg

            # Process tool calls
            history.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Send progress update
                    if progress_callback:
                        tool_desc = f"Using {block.name}..."
                        if block.name == "run_command":
                            cmd = block.input.get("command", "")
                            tool_desc = f"Running: {cmd[:60]}"
                        elif block.name == "read_file":
                            tool_desc = f"Reading: {block.input.get('path', '')}"
                        elif block.name == "edit_file":
                            tool_desc = f"Editing: {block.input.get('path', '')}"
                        elif block.name == "write_file":
                            tool_desc = f"Writing: {block.input.get('path', '')}"
                        elif block.name == "search_files":
                            tool_desc = f"Searching: {block.input.get('pattern', '')}"
                        elif block.name == "list_directory":
                            tool_desc = f"Listing: {block.input.get('path', '.')}"
                        await progress_callback(tool_desc)

                    result = _execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            history.append({"role": "user", "content": tool_results})

        return "Error: too many tool calls in a row."

    except anthropic.BadRequestError as exc:
        # Auto-recover from corrupted conversation history
        if "tool_result" in str(exc) or "tool_use" in str(exc):
            _conversations[user_id] = []
            # Retry with clean history
            _conversations[user_id].append({"role": "user", "content": user_content})
            try:
                response = await client.messages.create(
                    model=config.CLAUDE_MODEL,
                    max_tokens=4096,
                    system=system,
                    tools=TOOLS,
                    messages=_conversations[user_id],
                )
                text_parts = [
                    block.text for block in response.content
                    if block.type == "text"
                ]
                _conversations[user_id].append({"role": "assistant", "content": response.content})
                return "(History auto-cleared due to corruption)\n\n" + ("\n".join(text_parts) or "(no response)")
            except Exception as retry_exc:
                return f"Error after history reset: {retry_exc}"
        return f"Error: {exc}"
    except anthropic.AuthenticationError:
        return "Error: Invalid ANTHROPIC_API_KEY. Check your .env file."
    except anthropic.RateLimitError:
        return "Error: Rate limited by the API. Try again in a moment."
    except Exception as exc:
        return f"Error: {exc}"
