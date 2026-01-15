---
name: paper-reader
description: Reads and analyzes academic papers that may be too large for context window. Extracts key sections (abstract, intro, theory, methods, results, discussion) and provides structured summaries. Use when you need to read a paper from Zotero or PDF that exceeds token limits.
user-invocable: false
---

# Academic Paper Reader Skill

This skill handles reading large academic papers that exceed context window limits by intelligently extracting and summarizing key sections.

## Problem

Academic papers in Zotero often exceed 25,000+ tokens when retrieved via `zotero_get_item_fulltext`. This exhausts context and provides more text than needed for most analysis tasks.

## Solution Strategy

### Step 1: Always Start with Metadata
Use `zotero_get_item_metadata` first - this returns:
- Title, authors, year, journal
- Abstract (usually 150-300 words)
- DOI for additional lookups

This is sufficient for many tasks (finding related work, checking coverage, quick summaries).

### Step 2: For Deeper Analysis - Use Section Extraction

When full paper content is needed, use the **media-interpreter** agent with the actual PDF file:

```
Task tool with subagent_type=media-interpreter
Prompt: "Read this academic paper PDF and extract:
1. Full abstract
2. Key theoretical arguments from the literature review/theory section
3. Hypotheses (numbered list)
4. Methods summary (sample, data sources, analytical approach, key variables)
5. Main findings (key results with effect sizes if available)
6. Limitations acknowledged by authors

Paper: [PDF path from Zotero]"
```

### Step 3: For Theory Section Analysis Specifically

When analyzing theory sections as style guides:

```
Task tool with subagent_type=media-interpreter
Prompt: "Analyze the THEORY/LITERATURE REVIEW section of this paper:
1. How many words approximately in the theory section?
2. What theoretical frameworks are invoked? (RBV, agency theory, institutional theory, etc.)
3. How many hypotheses? List each with the theoretical logic.
4. How many citations in the theory section?
5. What is the organizational structure? (e.g., main argument -> boundary conditions -> moderators)
6. Note any tables or figures that support the theoretical arguments.

Paper: [PDF path]"
```

### Step 4: For Methods Section Analysis

When understanding empirical approaches:

```
Task tool with subagent_type=media-interpreter
Prompt: "Analyze the METHODS section of this paper:
1. Data sources - what data did they use?
2. Sample - how many observations, what time period, what geography?
3. Dependent variable(s) - what are they measuring as outcomes?
4. Independent variable(s) - what treatments or predictors?
5. Control variables - what do they control for?
6. Analytical approach - what statistical method? (OLS, fixed effects, DiD, matching, etc.)
7. Robustness checks - what alternative specifications?

Paper: [PDF path]"
```

## Getting PDF Paths from Zotero

1. Use `zotero_get_item_children` with the item_key to find attachments
2. The PDF attachment will have a path property
3. Zotero stores PDFs in: `C:/Users/kagan/Zotero/storage/[8-char-key]/filename.pdf`

## Workflow Example

```
# For a paper you want to use as style guide:

1. Search Zotero for the paper:
   mcp__zotero__zotero_search_items(query="author name keyword")

2. Get metadata (always fits in context):
   mcp__zotero__zotero_get_item_metadata(item_key="ABC123XY")

3. Get children to find PDF path:
   mcp__zotero__zotero_get_item_children(item_key="ABC123XY")

4. If PDF exists, use media-interpreter agent:
   Task(subagent_type="media-interpreter", prompt="Analyze theory section of [pdf_path]...")

5. If no PDF, try fulltext with truncation awareness:
   - Only request specific sections you need
   - Use semantic search to find relevant passages
```

## Section Patterns in Academic Papers

When parsing raw text, look for these section markers:
- **Abstract**: Usually first paragraph or labeled "Abstract"
- **Introduction**: "Introduction", "1. Introduction", numbered first section
- **Theory/Lit Review**: "Theory", "Literature Review", "Theoretical Background", "Hypothesis Development"
- **Methods**: "Method", "Methods", "Data", "Sample", "Methodology", "Research Design"
- **Results**: "Results", "Findings", "Analysis", "Empirical Results"
- **Discussion**: "Discussion", "Implications", "Contributions"
- **Conclusion**: "Conclusion", "Concluding Remarks"

## Token Budgets by Section

Typical academic paper token distribution:
- Abstract: 200-400 tokens
- Introduction: 1,500-3,000 tokens
- Theory/Lit Review: 4,000-8,000 tokens (longest section usually)
- Methods: 2,000-4,000 tokens
- Results: 3,000-6,000 tokens (can be long with tables)
- Discussion: 2,000-4,000 tokens
- References: 3,000-5,000 tokens (often not needed)

**Recommendation**: For style guide analysis, request Theory section + Methods + hypotheses.

## Handling "Text Too Long" Errors

If you get a token limit error:
1. Do NOT retry with the same request
2. Instead, use media-interpreter agent with the PDF file
3. Or request only metadata + abstract
4. Or break request into specific questions

## Notes

- Always prefer metadata + abstract first (fits in ~500 tokens)
- Use media-interpreter for deep PDF analysis
- For multiple papers, process in parallel with separate agents
- Store summaries in conversation for later reference
