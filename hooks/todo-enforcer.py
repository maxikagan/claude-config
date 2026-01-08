#!/usr/bin/env python3
"""
Todo Enforcer - Claude Code Stop Hook
Blocks exit when incomplete todos exist in the session.

Usage: Configure in ~/.claude/settings.json under hooks.Stop
"""

import sys
import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".claude" / "hooks" / "todo-enforcer.config.json"
DEBUG_LOG = Path.home() / ".claude" / "hooks" / "todo-enforcer.log"
MAX_CONSECUTIVE_BLOCKS = 10


def log(message, level="INFO"):
    """Write to debug log."""
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DEBUG_LOG, "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    except Exception:
        pass


def load_config():
    """Load configuration from file."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {"enabled": True, "block_count": 0}


def save_config(config):
    """Save configuration to file."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception:
        pass


def allow_exit(reason=None):
    """Allow the session to exit."""
    if reason:
        log(f"Allowing exit: {reason}")
    sys.exit(0)


def main():
    log("Hook started")

    config = load_config()

    # Check if disabled
    if not config.get("enabled", True):
        allow_exit("Disabled via config")

    try:
        input_data = sys.stdin.read()
        data = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        allow_exit(f"Failed to parse input: {e}")

    session_id = data.get("session_id", "unknown")
    transcript_path = data.get("transcript_path", "")
    stop_hook_active = data.get("stop_hook_active", False)

    log(f"Session: {session_id} | stop_hook_active: {stop_hook_active}")

    # Check for ralph-loop override
    if Path(".claude/ralph-loop.local.md").exists():
        allow_exit("Ralph loop active")

    # Handle stop_hook_active flag
    if stop_hook_active:
        if config.get("last_block_session") == session_id:
            config["block_count"] = 0
            save_config(config)

    if not transcript_path:
        allow_exit("No transcript path")

    if not Path(transcript_path).exists():
        allow_exit("Transcript not found")

    # Parse transcript for TodoWrite calls
    try:
        todos_json = None
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    contents = entry.get("message", {}).get("content", [])
                    for content in contents:
                        if (content.get("type") == "tool_use" and
                            content.get("name") == "TodoWrite"):
                            todos_json = content.get("input", {}).get("todos")
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        config["block_count"] = 0
        save_config(config)
        allow_exit(f"Failed to parse transcript: {e}")

    if not todos_json:
        config["block_count"] = 0
        save_config(config)
        allow_exit("No todos found")

    # Count incomplete todos
    pending = sum(1 for t in todos_json if t.get("status") == "pending")
    in_progress = sum(1 for t in todos_json if t.get("status") == "in_progress")
    incomplete = pending + in_progress

    log(f"Pending: {pending}, In progress: {in_progress}")

    if incomplete == 0:
        config["block_count"] = 0
        save_config(config)
        allow_exit("All todos completed")

    # Track consecutive blocks
    if config.get("last_block_session") == session_id:
        block_count = config.get("block_count", 0) + 1
    else:
        block_count = 1

    # Safety valve
    if block_count >= MAX_CONSECUTIVE_BLOCKS:
        log(f"Safety valve triggered after {MAX_CONSECUTIVE_BLOCKS} blocks", "WARN")
        config["block_count"] = 0
        save_config(config)
        allow_exit("Safety valve triggered")

    config["block_count"] = block_count
    config["last_block_session"] = session_id
    save_config(config)

    log(f"Blocking (count: {block_count}): {incomplete} incomplete")

    # Build task list
    task_lines = []
    for todo in todos_json:
        status = todo.get("status")
        content = todo.get("content", "")
        if status == "in_progress":
            task_lines.append(f"  -> [in progress] {content}")
        elif status == "pending":
            task_lines.append(f"  o [pending] {content}")

    task_list = "\n".join(task_lines)

    reason = f"""You have {incomplete} incomplete todo(s):
{task_list}

Complete these tasks before stopping.
Mark each task as 'completed' using TodoWrite when done."""

    result = {
        "decision": "block",
        "reason": reason
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
