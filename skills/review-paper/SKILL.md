---
name: review-paper
description: Comprehensive academic paper review for management and political science. Evaluates theory, empirics (with modern causal inference standards), contribution, literature coverage (including interdisciplinary), and writing quality. Uses OpenAlex for literature search and Zotero integration. Outputs structured journal-style review to markdown file.
user-invocable: true
---

# Academic Paper Review Skill

Provides comprehensive, structured reviews of academic papers with emphasis on:
- **Rigorous causal inference standards** (modern DiD, IV, matching methods)
- **Interdisciplinary literature coverage** (management, econ, poli sci, sociology)
- **Theory evaluation** calibrated to management journal expectations
- **Constructive developmental feedback**

## Invocation

```
/review-paper path/to/paper.pdf
```

## Startup Flow

1. **Parse the paper** using the `paper-reader` skill
2. **Ask the user**:
   - "Is this your own paper or are you reviewing someone else's?"
   - "Where should I save the review?" (output path)
3. **Run analysis agents** in parallel
4. **Synthesize** into final review
5. **Ask**: "Would you like me to dig deeper on any section?"

## Sub-Agents

Launch these using the Task tool with appropriate subagent_type:

### 1. Theory Agent
**Prompt template:**
```
Evaluate the theoretical development in this paper against management journal standards (AMJ, SMJ, ASQ).

Assess:
- Is there a clear causal mechanism? (A → B → C, not just A → C)
- Are boundary conditions articulated?
- Does it build on, extend, or challenge existing theory?
- Is the "why" compelling and non-obvious?
- Do the hypotheses logically follow from the theory?

Paper content:
[THEORY_SECTION]

Provide:
1. Theory assessment (strengths and weaknesses)
2. Specific concerns with location references
3. Suggestions for strengthening theoretical contribution

Note: The user is trained as a political scientist, so explain management theory norms when relevant.
```

### 2. Empirics Agent
**Prompt template:**
```
Evaluate the empirical methods with STATE-OF-THE-ART causal inference standards. No slack for causal claims.

Standards to apply:
- For DiD: Require modern estimators (Callaway-Sant'Anna, Sun-Abraham) for staggered timing
- Pre-trends testing must be formal, not just visual
- TWFE problems with heterogeneous effects must be addressed
- For IV: Exclusion restriction must be plausible, first-stage strong
- For matching: Selection on unobservables must be discussed

Key questions:
1. What is the identification strategy?
2. Are the assumptions stated and defended?
3. Are robustness checks adequate?
4. Do the claims match what the methods can support?
5. Is causal language used appropriately? (Flag "effect," "impact," "leads to" if methods don't support)

Paper methods section:
[METHODS_SECTION]

Paper results section:
[RESULTS_SECTION]

Provide:
1. Methods assessment with specific concerns
2. Overclaiming check (are conclusions calibrated to evidence?)
3. Suggestions for strengthening identification
4. Additional robustness checks that should be conducted
```

### 3. Tables/Figures Agent
**Prompt template:**
```
Evaluate all tables and figures in this paper:

For each table:
1. Statistical interpretation - Are coefficients, SEs, significance interpreted correctly?
2. Presentation quality - Clear labels, readable, complete?
3. Claims alignment - Does this table support what the text claims?
4. Completeness - Are necessary statistics reported?

For each figure:
1. Does it convey information effectively?
2. Are axes, legends, scales appropriate?
3. Does it support or contradict the narrative?

Tables and figures:
[TABLES_FIGURES_CONTENT]

Text claims about results:
[RESULTS_CLAIMS]

Provide table-by-table and figure-by-figure assessment with specific issues.
```

### 4. Literature Agent
**Prompt template:**
```
Evaluate literature engagement with emphasis on INTERDISCIPLINARY coverage.

Use OpenAlex to search for:
1. Papers that might contradict the claimed "gap"
2. Related work in Economics, Political Science, and Sociology that should be cited
3. Foundational papers that are missing

Use Zotero to:
1. Check if relevant papers are already in the user's library
2. Add important missing papers to library (root level)
3. Use citation keys for papers in library

Evaluate:
- Positioning accuracy: Do authors correctly characterize prior work? Any strawmanning?
- Gap validity: Has someone already done this?
- Interdisciplinary engagement: Are they ignoring relevant econ/poli sci/sociology work?

Paper's literature review:
[LIT_REVIEW_SECTION]

Paper's claimed contribution:
[CONTRIBUTION_CLAIMS]

Provide:
1. Assessment of literature engagement
2. Specific missing citations with full references
3. Papers that contradict claimed gap (if any)
4. Interdisciplinary papers being ignored
5. List of papers added to Zotero
```

### 5. Contribution Agent
**Prompt template:**
```
Evaluate the paper's contribution claims:

1. Is the claimed contribution actually novel? (Verify via OpenAlex)
2. Is it incremental ("X but in context Y") or genuinely advances understanding?
3. Is the "so what" clear?
4. Are the claims empirically justified? (Primary skepticism focus)

Paper's stated contribution:
[CONTRIBUTION_SECTION]

Paper's conclusions:
[CONCLUSIONS_SECTION]

Provide:
1. Novelty assessment with evidence
2. Contribution clarity evaluation
3. Framing suggestions - how could this be positioned more compellingly?
4. Journal fit assessment - which journals would this suit?
```

### 6. Writing Agent
**Prompt template (calibrate based on ownership):**

For USER'S OWN PAPER:
```
Provide comprehensive writing feedback:
- Structure and flow
- Paragraph-level clarity
- Sentence-level issues
- Jargon and accessibility
- Abstract effectiveness
- Specific rewrite suggestions

Be thorough and nitpicky - this is the user's own paper.

Paper content:
[FULL_PAPER]
```

For REVIEWING OTHERS:
```
Evaluate writing quality with LIGHT TOUCH - only flag issues that:
- Hamper understanding significantly
- Are egregious errors
- Affect credibility

Skip minor style issues.

Paper content:
[FULL_PAPER]
```

## Output Structure

Generate final review as markdown:

```markdown
# Paper Review: [Paper Title]
**Date**: [Date]
**Reviewer mode**: [Own paper / External review]

## Summary
[2-3 paragraph summary demonstrating understanding of core argument]

## Major Concerns

### 1. [Concern Title]
**Location**: [Section/Page]
**Issue**: [Clear statement]
**Why it matters**: [Explanation]
**Suggestion**: [Constructive path forward]

### 2. [Continue for 2-4 major concerns]

## Minor Concerns
- [List of smaller fixable issues]
- [Clarity issues if reviewing others: only major ones]
- [Missing citations]
- [Presentation issues]

## Developmental Suggestions
- How to strengthen the theory
- Additional analyses that would help
- Reframing suggestions
- Data/method improvements

## Journal Fit Assessment
- **Current fit**: [Journals this could target now]
- **With revisions**: [Higher-tier possibilities]

## Literature Additions
Papers added to Zotero:
- [Author (Year)] - [Brief relevance note]

## Suggested Next Steps
[If user wants deeper analysis on specific sections]
```

## OpenAlex Search Strategy

When searching for literature:

1. **Search terms from paper's keywords and abstract**
2. **Filter by disciplines**:
   - Management: SMJ, Org Sci, Management Science, AMR, AMJ, ASQ
   - Economics: AER, QJE, JPE, RES
   - Political Science: APSR, AJPS, JoP, PSRM
   - Sociology: ASR, AJS
3. **Check citation networks** of key papers mentioned
4. **Search for contradicting work** using negation of main claims

## Zotero Integration

- Use `mcp__zotero__zotero_semantic_search` for finding relevant existing papers
- Use `mcp__zotero__zotero_search_items` for keyword search
- Check if papers found via OpenAlex exist in Zotero before adding
- Add new papers to library root (no collection organization)
- Include citation keys in output for papers already in library

## Causal Inference Standards Reference

### Difference-in-Differences
- **Staggered timing**: Must use Callaway-Sant'Anna, Sun-Abraham, or similar
- **Pre-trends**: Formal testing required (not just visual inspection)
- **Event studies**: Should show dynamic effects
- **TWFE concerns**: Must acknowledge heterogeneous treatment effects issues

### Instrumental Variables
- **Exclusion restriction**: Must argue plausibly, not just assert
- **First stage**: F-stat > 10 minimum, prefer > 20
- **Monotonicity**: Should be discussed for LATE interpretation

### Matching/Weighting
- **Selection on observables**: Justify why unobservables aren't a problem
- **Balance checks**: Must show covariate balance
- **Sensitivity analysis**: How much hidden bias would overturn results?

### Descriptive/Associational Work
- **Acceptable** if language is appropriate
- **Flag** causal language: "effect," "impact," "leads to," "causes"
- **Suggest** hedging: "associated with," "predicts," "correlates with"
