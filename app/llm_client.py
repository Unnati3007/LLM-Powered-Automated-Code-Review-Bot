import json
import os
import httpx


class LLMClient:
    def __init__(self):
        self.provider = os.environ.get("LLM_PROVIDER", "anthropic")
        self.api_key = os.environ["LLM_API_KEY"]

    async def review(self, prompt: str) -> list[dict]:
        if self.provider == "anthropic":
            return await self._call_anthropic(prompt)
        return await self._call_openai(prompt)

    async def _call_anthropic(self, prompt: str) -> list[dict]:
        from app.prompt_builder import SYSTEM_PROMPT
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 2048,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            text = resp.json()["content"][0]["text"]
            return json.loads(text)

    async def _call_openai(self, prompt: str) -> list[dict]:
        from app.prompt_builder import SYSTEM_PROMPT
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "gpt-4-turbo",
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            resp.raise_for_status()
            return json.loads(resp.json()["choices"][0]["message"]["content"])
