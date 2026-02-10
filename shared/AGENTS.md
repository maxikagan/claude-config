# Specialized Agents for Claude Code

## Code Reviewer Agent

**Purpose**: Critically review code before execution to identify errors, bugs, and inefficiencies.

**When to use**: Before running ANY new or modified code (Python scripts, shell commands, etc.)

**Review checklist**:
1. **Syntax errors**: Missing imports, typos, incorrect function calls
2. **Case sensitivity**: Column names, file paths, variable names (especially for parquet/pandas)
3. **Data type mismatches**: String vs int, timestamps, nullable fields
4. **Memory issues**: Large file handling, unnecessary data loading, missing chunking
5. **Path errors**: Hardcoded paths, missing directories, incorrect file extensions
6. **Logic errors**: Off-by-one errors, incorrect filters, wrong aggregations
7. **Edge cases**: Empty dataframes, null values, missing files

**How to invoke**:
Use Task tool with subagent_type="general-purpose" and prompt:
"CODE REVIEW: Critically review the following code for errors, bugs, and inefficiencies before execution. Check for: syntax errors, case sensitivity issues, data type mismatches, memory problems, path errors, logic errors, and edge cases. Code to review: [file path or code snippet]"

**Output**: List of issues found with severity (critical/warning/suggestion) and recommended fixes.

---

## Session Logger Agent

**Purpose**: Maintain a running log of plans, progress, and task status to enable seamless resumption after interruptions.

**Log file location**: `~/.claude/SESSION_LOG.md`

**When to invoke** (MANDATORY):
1. **Session start**: Log current objectives and resume context
2. **Before major tasks**: Log what you're about to do
3. **After task completion**: Log results, outputs, any issues encountered
4. **Periodically during complex work**: Every 3-5 major steps, update the log
5. **When plans change**: Log new direction and reasoning

**Log entry format**:
```
[YYYY-MM-DD HH:MM] - Entry Type

Status: [STARTED | IN_PROGRESS | COMPLETED | BLOCKED | INTERRUPTED]
Task: Brief description
Details:
- What was done
- Key outputs/results
- Next steps if interrupted
Resume info: How to pick up if session ends
```

**How to invoke**:
Use Task tool with subagent_type="general-purpose" and prompt:
"SESSION LOG: [ACTION] - [DETAILS]"

Actions:
- "SESSION LOG: START - [objectives for this session]"
- "SESSION LOG: TASK_BEGIN - [task description]"
- "SESSION LOG: TASK_COMPLETE - [task] - [results summary]"
- "SESSION LOG: UPDATE - [progress update]"
- "SESSION LOG: CHECKPOINT - [current state, how to resume]"
- "SESSION LOG: COMPACT - Summarize and compact old entries"

**Compaction rules**:
- Keep last 10 detailed entries
- Summarize older entries into a "Previous Sessions Summary" section
- Always preserve: incomplete tasks, critical decisions made
- Compact when log exceeds ~200 lines

**Output**: Updated SESSION_LOG.md with new entry or compacted log

---

## SLURM Scheduler Agent

**Purpose**: Optimize SLURM job configuration and monitor job status on Savio HPC.

**When to use**:
1. Before writing any SLURM script (to select optimal partition/resources)
2. After submitting jobs (to check queue status)
3. Proactively during long-running jobs (to report status)

**Partition reference**:
| Partition | Cores | RAM | Use Case |
|-----------|-------|-----|----------|
| savio2 | 24 | ~64 GB | Small jobs, light data |
| savio3 | 32 | ~95 GB | Medium jobs |
| savio3_bigmem | 32 | ~386 GB | Large memory operations |
| savio3_xlmem | - | - | Only if absolutely necessary |

**How to invoke**:
Use Task tool with subagent_type="general-purpose" and prompt:
"SLURM SCHEDULER: [REQUEST]"

Requests:
- "SLURM SCHEDULER: ANALYZE - [job description] - recommend partition and resources"
- "SLURM SCHEDULER: STATUS - check queue for my jobs"
- "SLURM SCHEDULER: TEMPLATE - [job type] - generate SLURM script"

**Output**: Partition recommendation with reasoning, or job status report

---

## Deep Analysis Agent (Zen MCP)

**Purpose**: Multi-model analysis for complex architectural decisions, planning, and difficult debugging.

**When to use**:
- Complex architectural decisions requiring multiple perspectives
- Multi-step project planning with branching possibilities
- Difficult debugging that standard review can't solve
- When you need a "second opinion" from external AI models

**When NOT to use**:
- Routine code review (use general-purpose CODE REVIEW instead)
- Simple tasks or quick checks
- First-pass analysis (try standard approach first)

**Available tools** (invoke directly, not via Task):
| Tool | Purpose |
|------|---------|
| `mcp__zen__planner` | Complex project planning with revision/branching |
| `mcp__zen__thinkdeep` | Multi-stage investigation and reasoning |
| `mcp__zen__codereview` | Deep code review with expert validation |
| `mcp__zen__debug` | Systematic debugging with hypothesis testing |
| `mcp__zen__consensus` | Multi-model debate for architectural decisions |

**Model availability**:
- ✅ **Gemini**: `flash` (fast), `pro` (deep reasoning)
- ❌ **OpenAI**: API key invalid (401 error as of 2026-01-12)

**How to invoke**:
Call zen tools directly with appropriate model:
- Use `flash` or `gemini-2.5-flash` for speed
- Use `pro` or `gemini-2.5-pro` for depth

**Output**: Structured analysis with expert validation from external model
