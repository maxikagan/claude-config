---
name: literature-review
description: Conducts academic literature reviews using OpenAlex and Zotero. Use this when the user needs to find related papers, search for citations, explore citation networks, check what papers are in their Zotero library, identify gaps in literature, or flesh out a theory section of an academic paper.
user-invocable: true
---

# Literature Review Skill

This skill helps conduct systematic literature reviews for academic research by leveraging:

1. **OpenAlex** - 240M+ scholarly works database with semantic search
2. **Zotero** - User's personal reference library with full-text access
3. **Semantic Scholar** - Citation analysis and paper recommendations

## Available MCP Tools

### OpenAlex Tools (via `openalex` MCP server)
- `search_works` - Search papers with Boolean queries, filter by year, journal, citations
- `get_related_works` - Find papers related to a specific work
- `search_by_topic` - Discover papers by research topic
- `get_work_citations` - Papers that cite a work
- `get_work_references` - Papers cited by a work
- `get_citation_network` - Build citation network graphs

### Zotero Tools (via `zotero` MCP server)
- Search the user's personal reference library
- Access full-text PDFs stored in Zotero
- Retrieve metadata, abstracts, and notes
- Semantic search across the library

## Workflow

When conducting a literature review:

1. **Understand the research question** - What theory/topic needs to be explored?

2. **Ask about discipline focus** - If unclear, ask the user which disciplines to prioritize:
   - Strategy/Management
   - Political Science (American Politics focus, NOT IR)
   - Economics
   - Sociology
   - All of the above

3. **Search existing library first** - Check Zotero for papers the user already has

4. **Expand discovery via OpenAlex** - Find additional relevant papers

5. **Identify missing papers** - Papers that should be cited but aren't in Zotero

6. **Synthesize findings** - Create structured summaries

## Target Journals by Discipline

### Strategy/Management
- Strategic Management Journal (SMJ)
- Organization Science
- Management Science
- Academy of Management Review (AMR)
- Academy of Management Journal (AMJ)
- Administrative Science Quarterly (ASQ)
- Journal of Management
- Business & Society

### Political Science (American Politics, NOT IR)
- American Political Science Review (APSR)
- American Journal of Political Science (AJPS)
- Journal of Politics (JoP)
- British Journal of Political Science (BJPS)
- Political Science Research and Methods (PSRM)
- Political Analysis
- Political Behavior

### Economics
- American Economic Review (AER)
- Quarterly Journal of Economics (QJE)
- Journal of Political Economy (JPE)
- Review of Economic Studies
- Review of Financial Studies
- Journal of Finance

### Sociology
- American Sociological Review (ASR)
- American Journal of Sociology (AJS)
- Annual Review of Sociology

## Adding Papers to Zotero

When missing papers are identified:
1. Note the DOI or OpenAlex ID
2. User can add via Zotero browser connector
3. Or use Zotero's "Add Item by Identifier" feature (magic wand icon)
4. Batch imports can be done via DOI list

## Example Queries

- "Find papers on employee political mobilization"
- "What papers in my Zotero discuss constituency building?"
- "Search for CPA papers citing Hillman & Hitt 1999"
- "Find political science papers on voter turnout and workplace effects"
