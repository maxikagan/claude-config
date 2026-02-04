---
name: project-checkin
description: Review and update status on all active projects
user-invocable: true
allowed-tools: mcp__obsidian__*, AskUserQuestion
---

# Project Check-in Skill

Walks through each active project to review status and capture updates.

## Usage

```
/project-checkin           # Check in on all active projects
```

Also triggered as part of `/daily-note` when requested.

## Execution Steps

### Step 1: Load all active projects

Active research projects are at the vault root level. Read `{ProjectName}/_OVERVIEW.md` for each project folder.

**Active project folders** (at root):
- Organizational Civic Culture (ASQ)
- Partisan Sorting (NHB)
- Political Segregation (NHB)
- Political Stratification
- Stakeholder Alignment
- VRscores
- Voter Mobilization

**Excluded folders** (not active projects):
- Daily, Dormant Projects, Old, Personal, Pipeline, Reference, Research Ideas, Templates

Extract from each:
- Project name
- Phase (from frontmatter)
- Current #next action
- Team members
- Target venue
- Key notes

### Step 2: For each project, present and ask

Present a summary:
```
## [Project Name]
**Phase:** [phase] | **Target:** [venue] | **Team:** [names]

**Current #next:**
- [ ] [task description]

**Recent notes:**
[last few bullet points from Notes section if any]
```

Then ask:
1. "Any updates on [Project Name]?" with options:
   - "No change" - keep as is
   - "Update status" - user provides new info
   - "Mark #next complete" - mark done and ask for new #next
   - "Change phase" - update the phase

### Step 3: Apply updates

For each project with updates:
- Use `mcp__obsidian__patch_note` to update the _OVERVIEW.md
- If #next completed, check it off and add new #next
- If phase changed, update frontmatter
- Add any notes to the Notes section with date

### Step 4: Summary

After all projects reviewed, provide:
- Count of projects updated
- Any projects with no #next action (flag these)
- Upcoming deadlines if relevant

## Integration with /daily-note

When `/daily-note` is called, it should ask:
> "Would you like to do a project check-in?"

If yes, run this skill before finalizing the daily note.

## Output Format

Keep it conversational and quick. The goal is low-friction status capture, not comprehensive documentation.
