MAX_DIFF_LINES = int(__import__("os").environ.get("MAX_DIFF_LINES", 500))

SYSTEM_PROMPT = """You are an expert code reviewer. Analyze the provided git diff and return a JSON array of review comments.

Each comment must be a JSON object with:
- "path": file path (string)
- "line": line number in the diff (integer)
- "severity": one of "bug", "style", "performance", "security" (string)
- "message": concise, actionable feedback (string)
- "suggestion": optional improved code snippet (string or null)

Rules:
- Only flag real issues — avoid false positives
- Be specific: reference variable names, function names, patterns
- Suggest fixes where possible
- Return ONLY the JSON array, no other text
"""


def build_prompt(diff: str, pr_title: str, pr_body: str) -> str:
    lines = diff.splitlines()
    if len(lines) > MAX_DIFF_LINES:
        lines = lines[:MAX_DIFF_LINES]
        diff = "\n".join(lines) + "\n... (diff truncated)"

    return f"""PR Title: {pr_title}
PR Description: {pr_body or "No description provided"}

Git Diff:
```
{diff}
```

Review the diff above and return your findings as a JSON array."""
