---
name: literature-review
description: Conducts academic literature reviews using OpenAlex and Zotero. Use this when the user needs to find related papers, search for citations, explore citation networks, check what papers are in their Zotero library, identify gaps in literature, or flesh out a theory section of an academic paper.
user-invocable: true
argument-hint: "[topic, research question, or seminal paper]"
---

# Literature Review Skill

Conduct systematic literature reviews by combining real database searches (OpenAlex, Zotero) with structured output templates.

## Available MCP Tools

### OpenAlex Tools (via `openalex` MCP server)
- `search_works` - Search papers with Boolean queries, filter by year, journal, citations
- `get_related_works` - Find papers related to a specific work
- `search_by_topic` - Discover papers by research topic
- `get_work_citations` - Papers that cite a work (forward citations)
- `get_work_references` - Papers cited by a work (backward citations)
- `get_citation_network` - Build citation network graphs
- `get_top_cited_works` - Most-cited papers in a field

### Zotero Tools (via `zotero` MCP server)
- `zotero_search_items` - Keyword search in user's library
- `zotero_semantic_search` - Semantic search across the library
- `zotero_get_item_metadata` - Full metadata for a paper
- `zotero_get_item_fulltext` - Full text of a paper
- `zotero_get_annotations` - User's highlights and annotations

## Workflow

### Step 1: Define the Research Domain

Ask the user:
1. What is your specific research question?
2. Which disciplines to prioritize? (Management, Political Science, Economics, Sociology, or all)
3. What time period is relevant?
4. Are there seminal papers to start from?

### Step 2: Structure the Search

Define search terms before querying:
- **Primary terms**: Core concepts (e.g., "minimum wage", "employment")
- **Methodological filters**: (RCT, IV, difference-in-differences)
- **Outcome terms**: What effects are measured
- **Geographic/temporal scope**: If relevant

### Step 3: Search Existing Library First

Check Zotero for papers the user already has:
```
mcp__zotero__zotero_search_items(query="topic keywords")
mcp__zotero__zotero_semantic_search(query="research question in natural language")
```

### Step 4: Expand Discovery via OpenAlex

Find additional relevant papers:
```
mcp__openalex__search_works(query="topic AND keywords", filter="from_publication_date:2015-01-01")
```

Build citation networks from seminal papers:
1. Start with 2-3 seminal papers
2. `get_work_citations` — who cites them? (forward citations)
3. `get_work_references` — who do they cite? (backward citations)
4. Identify clusters of related work

### Step 5: Identify Missing Papers

Cross-reference OpenAlex results against Zotero library. Flag papers that should be cited but aren't in the user's collection. Provide DOIs for easy import.

### Step 6: Synthesize Using Templates

Use the output templates below to organize findings.

## Output Templates

### Literature Summary

```markdown
# Literature Review: [TOPIC]

## Search Strategy

**Databases:** OpenAlex, Zotero, [others]
**Date range:** [years]
**Search terms:**
- [term group 1]
- [term group 2]

**Inclusion criteria:**
- [criterion 1]
- [criterion 2]

---

## Papers in Your Zotero Library
[List papers already in the user's collection with brief relevance notes]

## Key Papers Found via OpenAlex
[Papers NOT in Zotero that should be added]

---

## Synthesis

| Finding | Evidence Quality | Consensus Level |
|---------|-----------------|-----------------|
| [finding 1] | Strong / Medium / Limited | High / Growing / Low |
| [finding 2] | ... | ... |

## Research Gaps

1. [Unanswered question 1]
2. [Unanswered question 2]
3. [Methods not yet applied]

## Connection to Your Project

Your study of [SPECIFIC QUESTION] can contribute by:
- [How your work fills a gap]
- [What new data/method you bring]
```

### Per-Paper Summary

Use this format for each paper worth discussing in detail:

```markdown
## [Author(s)] ([Year])

**Title:** [Full title]
**Published in:** [Journal]
**DOI:** [doi]
**In Zotero:** Yes / No

**Research Question:** [One sentence]

**Data:**
- Source: [Dataset name]
- Period: [Years]
- Sample: [N observations, unit of analysis]

**Identification Strategy:** [Method in one sentence]

**Main Findings:**
1. [Key result 1 with magnitude]
2. [Key result 2]

**Limitations:**
- [Main concern 1]
- [Main concern 2]

**Relevance to your project:** [One sentence]
```

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

## Common Pitfalls

- Only citing papers that support the argument
- Not engaging with contradictory findings
- Missing work in adjacent disciplines (econ paper ignoring poli sci, or vice versa)
- Citing papers not actually read — always verify via Zotero fulltext or OpenAlex abstract
- Literature review that reads as a list rather than a synthesis

## Example Queries

- "Find papers on employee political mobilization"
- "What papers in my Zotero discuss constituency building?"
- "Search for CPA papers citing Hillman & Hitt 1999"
- "Find political science papers on voter turnout and workplace effects"
- "Build a citation network around Card and Krueger 1994"
