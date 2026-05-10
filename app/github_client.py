import os
import httpx


class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        url = f"{self.BASE}/repos/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={**self.headers, "Accept": "application/vnd.github.v3.diff"},
            )
            resp.raise_for_status()
            return resp.text

    async def post_review(self, repo: str, pr_number: int, comments: list[dict]) -> None:
        if not comments:
            return
        url = f"{self.BASE}/repos/{repo}/pulls/{pr_number}/reviews"
        body_lines = []
        for c in comments:
            icon = {"bug": "🐛", "security": "🔒", "performance": "⚡", "style": "✨"}.get(c.get("severity",""), "💬")
            body_lines.append(f"{icon} **{c.get('severity','info').upper()}** in `{c.get('path','')}`: {c.get('message','')}")
            if c.get("suggestion"):
                body_lines.append(f"```suggestion\n{c['suggestion']}\n```")
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=self.headers, json={
                "body": "\n\n".join(body_lines),
                "event": "COMMENT",
            })
