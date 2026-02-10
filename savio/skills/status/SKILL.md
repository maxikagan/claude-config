---
name: status
description: Check running jobs and recent session status
user-invocable: true
allowed-tools: Bash, Read, Grep
---

# Status Dashboard

Provides a quick status report of running jobs and recent session activity.

## Usage

```
/status
```

## Report Contents

1. **Running SLURM jobs**: Run `squeue -u maxkagan -o "%.10i %.20j %.10P %.8T %.10M %.6D %R"` and summarize what's running, pending, or recently completed.

2. **Recent session log**: Read the last 30 lines of `~/.claude/SESSION_LOG.md` and summarize:
   - What was I last working on?
   - Any pending tasks or jobs to check?
   - Any blockers noted?

3. **Quick disk check**: Run `df -h /global/scratch/users/maxkagan | tail -1` to show scratch space.

## Output Style

Present this as a concise dashboard - no verbose explanations, just the facts.
