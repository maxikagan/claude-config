# Savio Setup Instructions

Run these commands to sync your Claude Code configuration on Savio:

```bash
# 1. Create repos directory if it doesn't exist
mkdir -p ~/repos

# 2. Clone your config repo
git clone https://github.com/maxikagan/claude-config.git ~/repos/claude-config

# 3. Create .claude directory if needed
mkdir -p ~/.claude

# 4. Create symlinks
ln -sf ~/repos/claude-config/commands ~/.claude/commands
ln -sf ~/repos/claude-config/skills ~/.claude/skills
ln -sf ~/repos/claude-config/agents ~/.claude/agents
ln -sf ~/repos/claude-config/settings.json ~/.claude/settings.json

# 5. Verify setup
ls -la ~/.claude/
```

Done! Your commands (`/conda`, `/jupyter`) and skills are now available.

To update after making changes on another machine:
```bash
cd ~/repos/claude-config && git pull
```
