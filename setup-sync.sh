#!/bin/bash
# Claude Config Sync Setup Script (Linux/macOS)
# Detects environment (PSC Bridges-2, Savio, or generic) and symlinks
# the shared configs plus the correct platform-specific configs.
#
# Usage:
#   ./setup-sync.sh [repo-path]
#   ./setup-sync.sh              # defaults to ~/claude-config or ~/repos/claude-config

set -e

# Find repo path
if [ -n "$1" ]; then
    REPO_PATH="$1"
elif [ -d "$HOME/claude-config" ]; then
    REPO_PATH="$HOME/claude-config"
elif [ -d "$HOME/repos/claude-config" ]; then
    REPO_PATH="$HOME/repos/claude-config"
else
    echo "Error: Could not find claude-config repo."
    echo "Clone it first, or specify path: ./setup-sync.sh /path/to/repo"
    exit 1
fi

CLAUDE_DIR="$HOME/.claude"

# Detect environment
detect_environment() {
    local hostname=$(hostname -f 2>/dev/null || hostname)

    if echo "$hostname" | grep -qi "bridges2\|psc\.edu\|br[0-9]"; then
        echo "psc"
    elif echo "$hostname" | grep -qi "brc\|savio\|berkeley"; then
        echo "savio"
    elif [ -d "/jet/home" ]; then
        echo "psc"
    elif [ -d "/global/home/users" ]; then
        echo "savio"
    else
        echo "generic"
    fi
}

ENV=$(detect_environment)
echo "Detected environment: $ENV"
echo "Repo path: $REPO_PATH"
echo ""

# Create .claude directory
mkdir -p "$CLAUDE_DIR"

# Helper: symlink a directory, merging contents if target already has items
link_dir() {
    local source_dir="$1"
    local target_dir="$2"

    if [ ! -d "$source_dir" ]; then
        return
    fi

    mkdir -p "$target_dir"

    # Symlink each item inside the directory
    for item in "$source_dir"/*; do
        [ -e "$item" ] || continue
        local name=$(basename "$item")
        local target="$target_dir/$name"

        if [ -e "$target" ] || [ -L "$target" ]; then
            rm -rf "$target"
        fi

        ln -sf "$item" "$target"
    done
}

# Helper: symlink a single file
link_file() {
    local source_file="$1"
    local target_file="$2"

    if [ ! -f "$source_file" ]; then
        return
    fi

    if [ -e "$target_file" ] || [ -L "$target_file" ]; then
        rm -f "$target_file"
    fi

    ln -sf "$source_file" "$target_file"
}

# --- Step 1: Symlink shared configs (always) ---
echo "Linking shared configs..."

# Agents: symlink each agent file into ~/.claude/agents/
link_dir "$REPO_PATH/shared/agents" "$CLAUDE_DIR/agents"

# Rules: symlink each rule file into ~/.claude/rules/
link_dir "$REPO_PATH/shared/rules" "$CLAUDE_DIR/rules"

# Skills: symlink each skill into ~/.claude/skills/
link_dir "$REPO_PATH/shared/skills" "$CLAUDE_DIR/skills"

# Hooks: symlink each hook into ~/.claude/hooks/
link_dir "$REPO_PATH/shared/hooks" "$CLAUDE_DIR/hooks"

echo "  Linked: agents, rules, skills, hooks"

# --- Step 2: Symlink platform-specific configs ---
PLATFORM_DIR="$REPO_PATH/$ENV"

if [ -d "$PLATFORM_DIR" ]; then
    echo "Linking $ENV-specific configs..."

    # Platform skills (merge into same ~/.claude/skills/ directory)
    if [ -d "$PLATFORM_DIR/skills" ]; then
        link_dir "$PLATFORM_DIR/skills" "$CLAUDE_DIR/skills"
        echo "  Linked: $ENV skills (merged into skills/)"
    fi

    # Platform settings.json
    if [ -f "$PLATFORM_DIR/settings.json" ]; then
        link_file "$PLATFORM_DIR/settings.json" "$CLAUDE_DIR/settings.json"
        echo "  Linked: settings.json"
    fi

    # Platform hooks (merge into same ~/.claude/hooks/ directory)
    if [ -d "$PLATFORM_DIR/hooks" ]; then
        link_dir "$PLATFORM_DIR/hooks" "$CLAUDE_DIR/hooks"
        echo "  Linked: $ENV hooks (merged into hooks/)"
    fi
else
    echo "No platform-specific configs found for '$ENV'"
    echo "  (Only shared configs were linked)"
fi

echo ""
echo "Sync complete! Environment: $ENV"
echo ""
echo "Linked into $CLAUDE_DIR:"
ls -1 "$CLAUDE_DIR/agents/" 2>/dev/null | sed 's/^/  agents\//' || true
ls -1 "$CLAUDE_DIR/rules/" 2>/dev/null | sed 's/^/  rules\//' || true
ls -1 "$CLAUDE_DIR/skills/" 2>/dev/null | sed 's/^/  skills\//' || true
ls -1 "$CLAUDE_DIR/hooks/" 2>/dev/null | sed 's/^/  hooks\//' || true
