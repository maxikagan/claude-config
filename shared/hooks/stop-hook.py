#!/usr/bin/env python3
"""
Ralph Loop Stop Hook - Cross-platform Python version
Prevents session exit when a ralph-loop is active.
Feeds Claude's output back as input to continue the loop.

This is a Python port of the ralph-loop plugin's stop-hook.sh for Windows/Linux compatibility.
"""

import sys
import json
import re
import os
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        return {}

    frontmatter_lines = []
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            break
        frontmatter_lines.append(line)

    result = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            result[key.strip()] = value

    return result


def extract_prompt(content: str) -> str:
    """Extract prompt text after the closing --- of frontmatter."""
    lines = content.split('\n')
    dash_count = 0
    prompt_start = 0

    for i, line in enumerate(lines):
        if line.strip() == '---':
            dash_count += 1
            if dash_count == 2:
                prompt_start = i + 1
                break

    if dash_count < 2:
        return ""

    return '\n'.join(lines[prompt_start:])


def extract_promise_text(output: str) -> str:
    """Extract text from <promise> tags."""
    match = re.search(r'<promise>(.*?)</promise>', output, re.DOTALL)
    if match:
        return ' '.join(match.group(1).split())
    return ""


def main():
    try:
        hook_input = sys.stdin.read()
        data = json.loads(hook_input) if hook_input.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    state_file = Path(".claude/ralph-loop.local.md")

    if not state_file.exists():
        sys.exit(0)

    try:
        content = state_file.read_text(encoding='utf-8')
    except Exception:
        sys.exit(0)

    frontmatter = parse_frontmatter(content)
    iteration_str = frontmatter.get('iteration', '')
    max_iterations_str = frontmatter.get('max_iterations', '')
    completion_promise = frontmatter.get('completion_promise', '')

    if not iteration_str.isdigit():
        print(f"Warning: Ralph loop state file corrupted (invalid iteration: '{iteration_str}')", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    if not max_iterations_str.isdigit():
        print(f"Warning: Ralph loop state file corrupted (invalid max_iterations: '{max_iterations_str}')", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    iteration = int(iteration_str)
    max_iterations = int(max_iterations_str)

    if max_iterations > 0 and iteration >= max_iterations:
        print(f"Ralph loop: Max iterations ({max_iterations}) reached.")
        state_file.unlink()
        sys.exit(0)

    transcript_path = data.get('transcript_path', '')

    if not transcript_path or not Path(transcript_path).exists():
        print(f"Warning: Ralph loop transcript file not found: {transcript_path}", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Warning: Failed to read transcript: {e}", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    assistant_lines = [l for l in lines if '"role":"assistant"' in l or '"role": "assistant"' in l]

    if not assistant_lines:
        print("Warning: No assistant messages found in transcript", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    try:
        last_message = json.loads(assistant_lines[-1])
        content_blocks = last_message.get('message', {}).get('content', [])
        text_parts = [b.get('text', '') for b in content_blocks if b.get('type') == 'text']
        last_output = '\n'.join(text_parts)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to parse assistant message: {e}", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    if not last_output:
        print("Warning: Assistant message contained no text content", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    if completion_promise and completion_promise != 'null':
        promise_text = extract_promise_text(last_output)
        if promise_text and promise_text == completion_promise:
            print(f"Ralph loop: Detected <promise>{completion_promise}</promise>")
            state_file.unlink()
            sys.exit(0)

    next_iteration = iteration + 1
    prompt_text = extract_prompt(content)

    if not prompt_text.strip():
        print("Warning: Ralph loop state file corrupted (no prompt text found)", file=sys.stderr)
        state_file.unlink()
        sys.exit(0)

    updated_content = re.sub(
        r'^iteration:\s*\d+',
        f'iteration: {next_iteration}',
        content,
        count=1,
        flags=re.MULTILINE
    )

    try:
        state_file.write_text(updated_content, encoding='utf-8')
    except Exception as e:
        print(f"Warning: Failed to update state file: {e}", file=sys.stderr)

    if completion_promise and completion_promise != 'null':
        system_msg = f"Ralph iteration {next_iteration} | To stop: output <promise>{completion_promise}</promise> (ONLY when statement is TRUE)"
    else:
        system_msg = f"Ralph iteration {next_iteration} | No completion promise set - loop runs infinitely"

    result = {
        "decision": "block",
        "reason": prompt_text,
        "systemMessage": system_msg
    }

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
