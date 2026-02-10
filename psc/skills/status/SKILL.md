---
name: status
description: Check running jobs and recent session status on PSC Bridges-2
user-invocable: true
allowed-tools: Bash, Read, Grep
---

# Status Dashboard (PSC Bridges-2)

Provides a quick status report of running jobs and recent session activity.

## Usage

```
/status
```

## Report Contents

1. **Running SLURM jobs**: Run `squeue -u mkagan1 -o "%.10i %.20j %.10P %.8T %.10M %.6D %R"` and summarize what's running, pending, or recently completed.

2. **Recent session log**: Read the last 30 lines of `~/.claude/SESSION_LOG.md` and summarize:
   - What was I last working on?
   - Any pending tasks or jobs to check?
   - Any blockers noted?

3. **Quick disk check**: Run `my_quotas` to show storage usage, or fall back to:
   - `df -h /jet/home/mkagan1 | tail -1` (home)
   - `du -sh /ocean/projects/soc260001p/mkagan1/ 2>/dev/null` (project)

4. **Allocation balance**: Run `projects` to show remaining SUs.

## Output Style

Present this as a concise dashboard - no verbose explanations, just the facts.
