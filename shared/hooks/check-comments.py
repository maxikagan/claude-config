#!/usr/bin/env python3
"""
Comment Checker Hook for Claude Code
Analyzes code modifications for excessive or problematic comments.

Usage: Configure in ~/.claude/settings.json under hooks.PostToolUse for Write/Edit tools
"""

import sys
import json
import re
import os

COMMENT_THRESHOLD = 0.25  # 25% comment ratio threshold

COMMENT_PATTERNS = {
    ".ts": ["//", "/*", "*/", "*"],
    ".tsx": ["//", "/*", "*/", "*"],
    ".js": ["//", "/*", "*/", "*"],
    ".jsx": ["//", "/*", "*/", "*"],
    ".py": ["#", '"""', "'''"],
    ".go": ["//", "/*", "*/"],
    ".rs": ["//", "/*", "*/"],
    ".java": ["//", "/*", "*/", "*"],
    ".cpp": ["//", "/*", "*/"],
    ".c": ["//", "/*", "*/"],
    ".sol": ["//", "/*", "*/"],
    ".r": ["#"],
    ".R": ["#"],
}

# Valid comment patterns (exempted from warnings)
VALID_PATTERNS = [
    r"^\s*///",              # Doc comments
    r"^\s*\*\s*@",           # JSDoc/JavaDoc
    r"#\s*(given|when|then)", # BDD
    r"TODO|FIXME|HACK|XXX",  # Task markers
    r"@ts-expect-error",     # TypeScript directives
    r"eslint-disable",       # ESLint directives
    r"type:\s*ignore",       # Type hints
    r"pragma",               # Compiler directives
    r"region|endregion",     # Code folding
    r"noqa",                 # Python linter ignore
    r"pylint:",              # Pylint directives
]


def main():
    try:
        input_data = sys.stdin.read()
        data = json.loads(input_data)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Extract file path and content based on tool type
    file_path = None
    content = None

    if tool_name == "Write":
        file_path = tool_input.get("file_path")
        content = tool_input.get("content")
    elif tool_name == "Edit":
        file_path = tool_input.get("file_path")
        content = tool_input.get("new_string")
    elif tool_name == "MultiEdit":
        file_path = tool_input.get("file_path")
        edits = tool_input.get("edits", [])
        content = "\n".join(e.get("new_string", "") for e in edits)
    else:
        sys.exit(0)

    if not file_path or not content:
        sys.exit(0)

    # Determine language based on extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in COMMENT_PATTERNS:
        sys.exit(0)

    patterns = COMMENT_PATTERNS[ext]
    lines = content.split("\n")

    total_lines = 0
    comment_lines = 0
    flagged_comments = []

    for line_num, line in enumerate(lines, 1):
        trimmed = line.strip()

        if not trimmed:
            continue

        total_lines += 1

        # Check if line is a comment
        is_comment = any(trimmed.startswith(p) for p in patterns)

        if is_comment:
            comment_lines += 1

            # Check if it's a valid/exempted comment
            is_valid = any(re.search(vp, trimmed) for vp in VALID_PATTERNS)

            if not is_valid:
                flagged_comments.append(f"  Line {line_num}: {trimmed[:80]}")

    if total_lines == 0:
        sys.exit(0)

    ratio = comment_lines / total_lines

    if ratio > COMMENT_THRESHOLD and flagged_comments:
        percentage = round(ratio * 100, 1)
        flagged_list = "\n".join(flagged_comments[:10])  # Limit to 10 examples
        if len(flagged_comments) > 10:
            flagged_list += f"\n  ... and {len(flagged_comments) - 10} more"

        warning = f"""
<comment-warning>
WARNING: High comment ratio detected ({percentage}% of non-empty lines are comments)

Flagged comments that may be unnecessary:
{flagged_list}

Consider:
- Using self-documenting code with descriptive names
- Removing comments that repeat what code does
- Keeping only comments that explain WHY, not WHAT
</comment-warning>"""

        result = {
            "continue": True,
            "message": warning
        }
        print(json.dumps(result))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
