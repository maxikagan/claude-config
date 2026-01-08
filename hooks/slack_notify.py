#!/usr/bin/env python3
"""
Slack notification hook for Claude Code.
Posts notifications to Slack and maintains session<->thread mapping.
Supports bidirectional communication with the listener.
"""

import sys
import os
import json

# Add paths for imports
home = os.environ.get('USERPROFILE', os.path.expanduser('~'))
claude_slack_dir = os.path.join(home, '.claude', 'claude-slack')
claude_slack_cross_dir = os.path.join(home, '.claude', 'claude-slack-cross')
sys.path.insert(0, os.path.join(claude_slack_dir, 'core'))
sys.path.insert(0, claude_slack_cross_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(claude_slack_dir, '.env'))

from slack_sdk import WebClient

# Try to import registry for bidirectional support
try:
    from registry import get_registry
    HAS_REGISTRY = True
except ImportError:
    HAS_REGISTRY = False

# Cache for session threads (session_id -> thread_ts)
THREAD_CACHE_FILE = os.path.join(home, '.claude', 'claude-slack-cross', 'thread_cache.json')

def load_thread_cache():
    """Load thread cache from disk"""
    try:
        if os.path.exists(THREAD_CACHE_FILE):
            with open(THREAD_CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_thread_cache(cache):
    """Save thread cache to disk"""
    try:
        os.makedirs(os.path.dirname(THREAD_CACHE_FILE), exist_ok=True)
        with open(THREAD_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Failed to save thread cache: {e}", file=sys.stderr)

def main():
    try:
        # Read hook input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            return

        hook_data = json.loads(input_data)
        message = hook_data.get('message', 'Claude needs your attention')
        project_dir = hook_data.get('project_dir', os.getcwd())
        session_id = hook_data.get('session_id', os.environ.get('CLAUDE_SESSION_ID', 'unknown'))[:8]

        # Get project name from path
        project_name = os.path.basename(project_dir)

        # Format the message
        slack_message = f"*[{project_name}]* {message}"

        # Post to Slack
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        channel_name = os.getenv("SLACK_CHANNEL", "#claude").lstrip("#")

        if not bot_token:
            print("SLACK_BOT_TOKEN not set", file=sys.stderr)
            return

        client = WebClient(token=bot_token)

        # Find channel ID
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response.get("channels", [])
        channel_info = next((ch for ch in channels if ch['name'] == channel_name), None)

        if not channel_info:
            print(f"Channel #{channel_name} not found", file=sys.stderr)
            return

        channel_id = channel_info['id']

        # Load thread cache
        thread_cache = load_thread_cache()

        # Check if we have an existing thread for this session
        thread_ts = thread_cache.get(session_id)

        if thread_ts:
            # Post to existing thread
            response = client.chat_postMessage(
                channel=channel_id,
                text=slack_message,
                thread_ts=thread_ts,
                unfurl_links=False
            )
        else:
            # Create new thread with session header
            header = f"*Claude Session: {session_id}*\nProject: `{project_name}`\nPath: `{project_dir}`\n\n_Reply to this thread to send input to Claude_"
            response = client.chat_postMessage(
                channel=channel_id,
                text=header,
                unfurl_links=False
            )
            thread_ts = response['ts']

            # Save thread mapping
            thread_cache[session_id] = thread_ts
            save_thread_cache(thread_cache)

            # Update registry if available
            if HAS_REGISTRY:
                try:
                    registry = get_registry()
                    registry.update_slack_thread(session_id, channel_id, thread_ts)
                except Exception as e:
                    print(f"Failed to update registry: {e}", file=sys.stderr)

            # Now post the actual message in the thread
            client.chat_postMessage(
                channel=channel_id,
                text=slack_message,
                thread_ts=thread_ts,
                unfurl_links=False
            )

        print(f"Posted to Slack thread {thread_ts}", file=sys.stderr)

    except Exception as e:
        # Don't block Claude on errors
        print(f"Slack notification error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
