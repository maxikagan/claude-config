#!/bin/bash
# Claude Config Sync Setup Script (Linux/macOS)
# Run this after cloning your claude-config repo to set up symlinks

REPO_PATH="${1:-$HOME/repos/claude-config}"
CLAUDE_DIR="$HOME/.claude"

# Check if repo exists
if [ ! -d "$REPO_PATH" ]; then
    echo "Error: Repo not found at $REPO_PATH"
    echo "Clone your repo first, or specify path: ./setup-sync.sh /path/to/repo"
    exit 1
fi

# Create .claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Remove existing and create symlinks
for item in commands skills agents; do
    target="$CLAUDE_DIR/$item"
    source="$REPO_PATH/$item"

    if [ -e "$target" ] || [ -L "$target" ]; then
        echo "Removing existing $target..."
        rm -rf "$target"
    fi

    echo "Creating symlink: $target -> $source"
    ln -sf "$source" "$target"
done

# Symlink settings.json
settings_target="$CLAUDE_DIR/settings.json"
settings_source="$REPO_PATH/settings.json"

if [ -e "$settings_target" ] || [ -L "$settings_target" ]; then
    rm -f "$settings_target"
fi
echo "Creating symlink: $settings_target -> $settings_source"
ln -sf "$settings_source" "$settings_target"

echo ""
echo "Sync setup complete!"
