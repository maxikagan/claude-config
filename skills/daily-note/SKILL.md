---
name: daily-note
description: Create or update the daily note in Obsidian with calendar events and structure
user-invocable: true
allowed-tools: mcp__obsidian__*, mcp__google-calendar__*
---

# Daily Note Skill

Updates or creates the daily note in Obsidian, populating it with calendar events and the standard template structure.

## Usage

```
/daily-note           # Update today's daily note
/daily-note tomorrow  # Create tomorrow's daily note
/daily-note 2026-01-28  # Create/update a specific date
```

## What This Skill Does

1. **Fetches calendar events** from all Google Calendars:
   - General (primary)
   - UC Berkeley
   - Columbia
   - wandapai lyfe (shared)
   - Holidays

2. **Populates the daily note** at `Daily/YYYY-MM-DD.md` with:
   - Today's events formatted with times
   - Week ahead preview (next 7 days' key events)
   - Standard template sections (Next Actions, Admin, Inbox, Notes)

3. **Preserves user content** - If sections like Inbox or Notes have content, preserve it

## Execution Steps

### Step 1: Determine the target date

- Default: today's date
- If argument provided: parse it (e.g., "tomorrow", "2026-01-28")
- Format: `YYYY-MM-DD`

### Step 2: Fetch calendar events

Use `mcp__google-calendar__list-events` to fetch:

**Today's events:**
```
calendarId: ["General", "UC Berkeley", "Columbia", "wandapai lyfe"]
timeMin: {target_date}T00:00:00
timeMax: {target_date}T23:59:59
timeZone: America/Los_Angeles
```

**Week ahead events:**
```
calendarId: ["General", "UC Berkeley", "Columbia", "wandapai lyfe"]
timeMin: {target_date + 1 day}T00:00:00
timeMax: {target_date + 7 days}T23:59:59
timeZone: America/Los_Angeles
```

### Step 3: Format calendar data

**Today's events format:**
```markdown
## Calendar
*{Day of week}*

- **9:00 AM** - Meeting with advisor
- **2:00 PM** - Seminar: Topic Name
- *All day* - Conference Day 1
```

- Sort by start time
- All-day events listed first with italic "*All day*"
- Include location if present: `Meeting Name @ Location`
- Skip declined events

**Week ahead format:**
```markdown
### Week Ahead
- **Tue 1/28**: Faculty meeting, Dentist 3pm
- **Wed 1/29**: Paper deadline
- **Thu 1/30**: (nothing scheduled)
```

- Group by day, show day name and date
- Summarize multiple events per day
- Skip days with no events (or show "(nothing scheduled)")

### Step 4: Read existing daily note (if exists)

Check if `Daily/{date}.md` exists:
- If yes: read it and preserve Inbox and Notes content
- If no: start fresh from template

### Step 5: Write the daily note

Use `mcp__obsidian__write_note` to write the complete note:

```markdown
# {YYYY-MM-DD}

## Calendar
{formatted today's events}

### Week Ahead
{formatted week ahead}

## Next Actions

```dataview
TASK
FROM "Organizational Civic Culture (ASQ)" OR "Partisan Sorting (NHB)" OR "Political Segregation (NHB)" OR "Political Stratification" OR "Stakeholder Alignment" OR "VRscores" OR "Voter Mobilization"
WHERE !completed AND contains(tags, "#next")
GROUP BY file.folder
```

## Admin

```dataview
TASK
FROM "Admin"
WHERE !completed
```

## Inbox
{preserved inbox content or empty}

## Notes
{preserved notes content or empty}
```

### Step 6: Offer project check-in

After updating the daily note, ask:
> "Would you like to do a project check-in?"

If yes, run `/project-checkin` to walk through each active project and capture status updates.

### Step 7: Confirm completion

Report what was created/updated:
- Date of the note
- Number of events today
- Key events this week
- Projects updated (if check-in was done)

## Notes

- The Dataview queries run automatically in Obsidian - we just include them as text
- Timezone is America/Los_Angeles (adjust if user changes location)
- Holiday calendar excluded from regular events (too noisy) but can be mentioned if relevant
