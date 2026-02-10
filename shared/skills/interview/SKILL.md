---
name: interview
description: Interview to flesh out a plan/spec
user-invocable: true
allowed-tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
---

# Interview Skill

Conduct an in-depth interview to flesh out a plan or specification document.

## Usage

```
/interview <path-to-plan-file>
```

## Behavior

Read the current plan from the specified file, then interview the user in detail using the AskUserQuestion tool about:
- Technical implementation details
- UI & UX considerations
- Concerns and tradeoffs
- Edge cases and error handling
- Any unclear requirements

## Important Guidelines

### Handling User Responses
- If the user dismisses/rejects the AskUserQuestion dialog, they likely want to type a free-form response instead of selecting multiple choice. Wait for their text response and treat it as a valid answer.
- When a question requires nuanced explanation, consider asking it as a simple prompt in your message text instead of using AskUserQuestion, then wait for the user's reply.
- Mix multiple-choice questions (for clear categorical choices) with open-ended text questions (for complex topics requiring explanation).
- Never treat a rejected dialog as "user declined" - instead, pause and wait for their typed response.

### Interview Process
- Make sure the questions are not obvious
- Be very in-depth and continue interviewing continually until it's complete
- After completing the interview, write the updated spec back to the original file
