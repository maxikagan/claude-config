# Claude Code Configuration

Personal Claude Code configuration files, organized by environment.

## Structure

```
claude-config/
├── shared/                     # Universal configs (all machines)
│   ├── agents/                 # Custom subagents
│   ├── rules/                  # Auto-applied rules
│   ├── skills/                 # Skills and slash commands
│   └── hooks/                  # Python hooks (cross-platform)
├── windows/                    # Windows-specific
│   ├── hooks/                  # PowerShell/VBS hooks
│   └── setup-sync.ps1
├── savio/                      # UC Berkeley Savio HPC
│   ├── skills/                 # estimate, status, savio-login
│   ├── settings.json
│   └── SAVIO_SETUP.md
├── psc/                        # PSC Bridges-2 HPC
│   ├── skills/                 # estimate, status (PSC-tailored)
│   └── settings.json
├── setup-sync.sh               # Auto-detecting setup script
└── README.md
```

## How It Works

The `setup-sync.sh` script auto-detects your environment and symlinks:
1. **shared/** configs (always)
2. **Platform-specific** configs (PSC, Savio, or Windows)

Platform skills override shared skills of the same name (e.g., PSC's `/estimate` replaces the shared one).

## Setup

```bash
# Clone the repo
git clone https://github.com/maxikagan/claude-config.git ~/claude-config

# Run the setup script (auto-detects environment)
cd ~/claude-config && ./setup-sync.sh

# Or specify repo path explicitly
./setup-sync.sh ~/claude-config
```

To update after changes on another machine:
```bash
cd ~/claude-config && git pull && ./setup-sync.sh
```

## Environment Detection

| Environment | Detection Method |
|-------------|-----------------|
| PSC Bridges-2 | Hostname contains `bridges2`, `psc.edu`, or `/jet/home` exists |
| Savio | Hostname contains `brc`, `savio`, or `/global/home/users` exists |
| Generic | Fallback (shared configs only) |

## Shared Skills

| Skill | Description |
|-------|-------------|
| `/conda` | Activate conda environments |
| `/jupyter` | Start Jupyter Lab |
| `/estimate` | Estimate SLURM job resources (overridden per-cluster) |
| `/status` | Job and session status dashboard (overridden per-cluster) |
| `/interview` | Interview to flesh out a plan/spec |
| `/humanizer` | Remove AI writing patterns |
| `/literature-review` | Academic literature search via OpenAlex/Zotero |
| `/review-paper` | Comprehensive academic paper review |
| `/paper-reader` | Read and summarize large academic papers |
| `/verify-citations` | Verify citations against Zotero/OpenAlex |
| `/fin-extract` | Extract financial tables from PDFs |
| `/project-checkin` | Review active project status |

## Hooks

**Cross-platform (Python, in shared/hooks/):**
- `keyword-detector.py` — Injects mode instructions on keywords (ultrawork, search, analyze)
- `check-comments.py` — Warns about excessive code comments
- `todo-enforcer.py` — Blocks exit when incomplete todos exist
- `stop-hook.py` — Ralph loop continuation hook

**Windows-only (in windows/hooks/):**
- PowerShell/VBS hooks for notifications, focus, git status

## Files NOT to Sync

These are machine-specific and should stay local:
- `.credentials.json` — Authentication tokens
- `settings.local.json` — Machine-specific permission overrides
- `cache/`, `projects/`, `history.jsonl` — Local state
