#!/usr/bin/env python3
"""
Keyword Detector Hook for Claude Code
Detects special keywords in user prompts and injects contextual instructions.

Usage: Configure in ~/.claude/settings.json under hooks.UserPromptSubmit
"""

import sys
import json
import re

MODES = {
    "ultrawork": {
        "keywords": ["ultrawork", "ulw", "ultra work"],
        "instruction": """<ultrawork-mode>
ULTRAWORK MODE ACTIVATED - Maximum capability execution:

1. PARALLEL AGENT LAUNCHING: Launch 3+ subagents simultaneously for research, implementation, and verification
2. COMPREHENSIVE PLANNING: Create detailed todo lists breaking down every step
3. THOROUGH VERIFICATION: Test all code, verify all claims, check all edge cases
4. EVIDENCE-BASED: Provide sources, permalinks, and proof for all assertions
5. NO SHORTCUTS: Complete every aspect of the task fully before marking done

Execute with maximum thoroughness and capability.
</ultrawork-mode>"""
    },
    "search": {
        "keywords": ["search", "find", "locate", "where is"],
        "instruction": """<search-mode>
EXHAUSTIVE SEARCH MODE:

1. Launch multiple parallel searches: grep patterns, glob file matching, LSP symbol lookups
2. Search git history if relevant
3. Cross-reference results from multiple tools
4. Report confidence level in completeness
5. Suggest additional search strategies if results seem incomplete

Find ALL relevant matches, not just the first ones.
</search-mode>"""
    },
    "analyze": {
        "keywords": ["analyze", "investigate", "debug", "diagnose"],
        "instruction": """<analysis-mode>
DEEP ANALYSIS MODE:

1. Surface scan: Quick overview of the problem space
2. Deep dive: Detailed examination of specific components
3. Cross-reference: Connect findings across files and systems
4. Hypothesis formation: Develop and test theories
5. Root cause: Trace issues to their origin

Be thorough and systematic in investigation.
</analysis-mode>"""
    },
    "think": {
        "keywords": ["think deeply", "think hard", "think carefully"],
        "instruction": """<think-mode>
EXTENDED REASONING MODE:

1. Consider broader context and implications
2. Evaluate from multiple perspectives
3. Analyze trade-offs explicitly
4. Assess risks and edge cases
5. Plan validation approach before implementation

Take time to reason thoroughly before acting.
</think-mode>"""
    }
}


def main():
    try:
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        prompt = data.get("prompt") or data.get("message") or ""
    except (json.JSONDecodeError, KeyError):
        sys.exit(0)

    if not prompt:
        sys.exit(0)

    prompt_lower = prompt.lower()

    for mode_name, mode_config in MODES.items():
        for keyword in mode_config["keywords"]:
            if keyword in prompt_lower:
                result = {
                    "continue": True,
                    "message": mode_config["instruction"]
                }
                print(json.dumps(result))
                sys.exit(0)

    # No keywords matched
    sys.exit(0)


if __name__ == "__main__":
    main()
