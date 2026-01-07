---
allowed-tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
argument-hint: [plan-file]
description: Interview to flesh out a plan/spec
---

Here's the current plan:

@$ARGUMENTS

Interview me in detail using the AskUserQuestion tool about literally anything: technical implementation, UI & UX, concerns, tradeoffs, etc. but make sure the questions are not obvious.

**IMPORTANT: Handling user responses**
- If the user dismisses/rejects the AskUserQuestion dialog, they likely want to type a free-form response instead of selecting multiple choice. Wait for their text response and treat it as a valid answer.
- When a question requires nuanced explanation, consider asking it as a simple prompt in your message text instead of using AskUserQuestion, then wait for the user's reply.
- Mix multiple-choice questions (for clear categorical choices) with open-ended text questions (for complex topics requiring explanation).
- Never treat a rejected dialog as "user declined" - instead, pause and wait for their typed response.

Be very in-depth and continue interviewing me continually until it's complete, then write the spec back to `$ARGUMENTS`.
