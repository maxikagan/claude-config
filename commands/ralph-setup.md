# Ralph Setup

Set up Ralph - an autonomous AI coding loop that ships features while you sleep.

## What to do:

1. Create the `scripts/ralph/` directory structure
2. Create `ralph.sh` - the main bash loop script that runs Claude Code iteratively
3. Create `prompt.md` - instructions for each Ralph iteration
4. Create `prd.json` - example PRD template with user stories
5. Create `progress.txt` - initial progress log with codebase patterns section
6. Make `ralph.sh` executable with `chmod +x`

## File Contents:

### ralph.sh
```bash
#!/bin/bash
set -e

MAX_ITERATIONS=${1:-10}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting Ralph - Autonomous AI Coding Loop"
echo "   Max iterations: $MAX_ITERATIONS"
echo ""

for i in $(seq 1 $MAX_ITERATIONS); do
  echo "═══════════════════════════════════════════"
  echo "═══ Iteration $i of $MAX_ITERATIONS"
  echo "═══════════════════════════════════════════"
  echo ""

  # Pipe prompt into Claude Code with dangerous skip permissions
  OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" \
    | claude --dangerously-skip-permissions 2>&1 \
    | tee /dev/stderr) || true

  # Check if agent signaled completion
  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo ""
    echo "✅ All tasks complete! Ralph is done."
    exit 0
  fi

  echo ""
  echo "⏸️  Waiting 2 seconds before next iteration..."
  sleep 2
  echo ""
done

echo ""
echo "⚠️  Max iterations reached without completion"
echo "   Check scripts/ralph/prd.json for remaining tasks"
exit 1
```

### prompt.md
```markdown
# Ralph Agent Instructions

## Your Task

1. Read `scripts/ralph/prd.json`
2. Read `scripts/ralph/progress.txt` (check Codebase Patterns first)
3. Check you're on the correct branch
4. Pick highest priority story where `passes: false`
5. Implement that ONE story
6. Run typecheck and tests
7. Update AGENTS.md files with learnings
8. Commit: `feat: [ID] - [Title]`
9. Update prd.json: `passes: true`
10. Append learnings to progress.txt

## Progress Format

APPEND to progress.txt:

## [Date] - [Story ID]
- What was implemented
- Files changed
- **Learnings:**
  - Patterns discovered
  - Gotchas encountered
---

## Codebase Patterns

Add reusable patterns to the TOP of progress.txt:

## Codebase Patterns
- Migrations: Use IF NOT EXISTS
- React: useRef<Timeout | null>(null)

## Stop Condition

If ALL stories pass, reply:
<promise>COMPLETE</promise>

Otherwise end normally.
```

### prd.json (example template)
```json
{
  "branchName": "ralph/feature-name",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add example feature",
      "acceptanceCriteria": [
        "Feature works as expected",
        "Tests pass",
        "typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### progress.txt
```markdown
# Ralph Progress Log
Started: [TODAY'S DATE]

## Codebase Patterns
- Add patterns here as they are discovered

## Key Files
- List important files here

---
```

## After Setup:

Tell the user:
1. Edit `scripts/ralph/prd.json` with their actual user stories
2. Run Ralph with: `./scripts/ralph/ralph.sh 25` (for 25 max iterations)
3. Monitor progress with:
   - `cat scripts/ralph/prd.json | jq '.userStories[] | {id, passes}'`
   - `cat scripts/ralph/progress.txt`
   - `git log --oneline -10`

## Success Factors:
- Keep stories small (must fit in one context window)
- Use explicit acceptance criteria
- Ensure fast feedback loops (typecheck, tests)
- Let learnings compound across iterations
