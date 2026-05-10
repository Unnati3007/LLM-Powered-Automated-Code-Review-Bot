import hashlib
import hmac
import os

from fastapi import FastAPI, Header, HTTPException, Request

from app.cache import get_cached_review, set_cached_review
from app.github_client import GitHubClient
from app.llm_client import LLMClient
from app.prompt_builder import build_prompt

app = FastAPI(title="Code Review Bot")
github = GitHubClient(token=os.environ["GITHUB_TOKEN"])
llm = LLMClient()


def verify_signature(payload: bytes, sig_header: str) -> bool:
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, sig_header or "")


@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=""),
):
    body = await request.body()
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    if x_github_event not in ("pull_request",):
        return {"status": "ignored"}

    payload = await request.json()
    action = payload.get("action", "")
    if action not in ("opened", "synchronize"):
        return {"status": "ignored"}

    repo_full = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    pr_title = payload["pull_request"]["title"]
    pr_body = payload["pull_request"].get("body", "")

    # Fetch the diff
    diff = await github.get_pr_diff(repo_full, pr_number)
    if not diff:
        return {"status": "empty diff"}

    # Cache key based on diff content
    cache_key = hashlib.sha256(diff.encode()).hexdigest()
    cached = await get_cached_review(cache_key)
    if cached:
        await github.post_review(repo_full, pr_number, cached)
        return {"status": "cached"}

    # Build prompt and call LLM
    prompt = build_prompt(diff, pr_title, pr_body)
    review_comments = await llm.review(prompt)

    # Cache for future identical diffs
    await set_cached_review(cache_key, review_comments)

    # Post to GitHub
    await github.post_review(repo_full, pr_number, review_comments)
    return {"status": "reviewed", "comments": len(review_comments)}


@app.get("/health")
async def health():
    return {"status": "ok"}
