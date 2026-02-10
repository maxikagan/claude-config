# Citation Integrity: Zero Hallucination Policy

When writing prose that includes academic citations, every citation must be verified against real sources. No exceptions.

## The Problem

LLMs hallucinate citations. They generate plausible-sounding references combining real author names with fake titles, or real titles with wrong metadata. These fake citations look real but don't exist.

## The Rule

**Never cite a paper unless you have verified it exists via:**
1. The user's Zotero library (mcp__zotero__*)
2. OpenAlex database (mcp__openalex__*)
3. A resolved DOI

## When Writing Academic Prose

Before including any citation:

### Option 1: Inline Verification (1-3 citations)
Verify directly using the MCP tools:
```
mcp__zotero__zotero_search_items(query="author title keywords")
mcp__openalex__search_works(query="author title year")
mcp__openalex__get_work(id="DOI")
```

### Option 2: Subagent Verification (4+ citations or literature review)
Spawn an Explore agent to verify citations in parallel:
```
Task(subagent_type="Explore", prompt="Verify these citations using Zotero and OpenAlex: [list]. For each, confirm it exists and provide the correct DOI and full citation.")
```

### Option 3: Use the Skill (comprehensive verification)
For document-wide verification or when user requests:
```
/verify-citations [paste citations or document]
```

## What To Do Instead of Hallucinating

When you want to cite something but don't have a verified source:

1. **Search first**: Use OpenAlex to find real papers on the topic
2. **Use Zotero**: Check if user has relevant papers in their library
3. **Be honest**: Say "research suggests..." without fake citation, then offer to find real sources
4. **Ask**: "Would you like me to search for papers on [topic]?"

## Citation Format

Once verified, cite with DOI:
```
Author, A. B., & Author, C. D. (Year). Title of the paper. Journal Name, Volume(Issue), Pages. https://doi.org/10.xxxx/xxxxx
```

## Red Flags (Signs You're About to Hallucinate)

Stop and verify if you're about to write:
- "Smith et al. (2023) showed that..." without having searched for Smith et al.
- A citation that "sounds right" but you haven't confirmed
- A paper you "remember" exists but can't find
- Any claim starting with "Studies show..." or "Research has found..."

## Verification Checklist

Before finalizing any academic writing, confirm:
- [ ] Every citation has a real DOI
- [ ] Author names match the actual paper
- [ ] Year is correct
- [ ] Journal/venue is correct
- [ ] Title is accurate (not paraphrased)

## When User Provides Citations

If user gives citations to include:
- Still verify them (users can be wrong too)
- Correct errors silently or flag discrepancies
- If a citation doesn't exist, tell the user
