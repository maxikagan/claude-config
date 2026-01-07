# Claude Code Configuration

Personal Claude Code configuration files for syncing across machines.

## Structure

```
.claude/
├── commands/           # Slash commands (invoke with /command-name)
│   ├── conda.md       # /conda - activate conda environments
│   └── jupyter.md     # /jupyter - start Jupyter Lab
├── skills/            # Auto-applied capabilities
│   └── academic-research.md
├── agents/            # Custom subagents (empty for now)
├── settings.json      # Shared settings (permissions, env vars)
└── README.md          # This file
```

## Syncing Across Machines

### Option 1: Symlink Approach (Recommended)

Keep this repo separate and symlink the shareable directories:

```bash
# Clone your config repo somewhere
git clone https://github.com/YOUR_USERNAME/claude-config.git ~/repos/claude-config

# Create symlinks (run on each machine)
# Linux/macOS:
ln -sf ~/repos/claude-config/commands ~/.claude/commands
ln -sf ~/repos/claude-config/skills ~/.claude/skills
ln -sf ~/repos/claude-config/agents ~/.claude/agents
ln -sf ~/repos/claude-config/settings.json ~/.claude/settings.json

# Windows (run as admin, or enable developer mode):
mklink /D "%USERPROFILE%\.claude\commands" "%USERPROFILE%\repos\claude-config\commands"
mklink /D "%USERPROFILE%\.claude\skills" "%USERPROFILE%\repos\claude-config\skills"
mklink /D "%USERPROFILE%\.claude\agents" "%USERPROFILE%\repos\claude-config\agents"
mklink "%USERPROFILE%\.claude\settings.json" "%USERPROFILE%\repos\claude-config\settings.json"
```

### Option 2: Direct Clone

Clone directly into a subfolder and copy files as needed.

## Files NOT to Sync

These are machine-specific and should stay local:
- `.credentials.json` - Authentication tokens
- `settings.local.json` - Machine-specific settings
- `cache/`, `projects/`, `history.jsonl` - Local state

## Adding New Commands

Create a markdown file in `commands/`:

```markdown
# Command Title

Description of what this command does.

Instructions for Claude to follow when /command-name is invoked.
$ARGUMENTS contains any text after the command name.
```

## Adding New Skills

Create a markdown file in `skills/`:

```markdown
# Skill Name

When [trigger condition], Claude should:
- Do this
- Do that
```

Skills are automatically applied when relevant (no explicit invocation needed).
