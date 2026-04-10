"""LLM call helpers shared by compile-time workflows."""

from __future__ import annotations

import asyncio
import time
from typing import Any


class TokenTracker:
    """Accumulates token usage across multiple LLM calls."""

    def __init__(self) -> None:
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def add(self, usage: Any) -> None:
        if usage:
            try:
                val = getattr(usage, "prompt_tokens", 0)
                self.prompt_tokens += int(val) if val else 0
            except (TypeError, ValueError):
                pass
            try:
                val = getattr(usage, "completion_tokens", 0)
                self.completion_tokens += int(val) if val else 0
            except (TypeError, ValueError):
                pass

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def llm_call_sync(
    client: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    tracker: TokenTracker | None = None,
    _max_retries: int = 3,
) -> str:
    """Synchronous LLM call via the OpenAI SDK with retry on transient failures."""
    from openai import AuthenticationError, NotFoundError

    for attempt in range(_max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            if tracker and hasattr(response, "usage"):
                tracker.add(response.usage)
            if not response.choices:
                raise RuntimeError(f"LLM returned empty response for model {model}")
            return response.choices[0].message.content or ""
        except NotFoundError:
            raise RuntimeError(
                f"Model '{model}' not found on OpenRouter.\n"
                f"Check the model name at https://openrouter.ai/models\n"
                f"Fix: klore config set model.director <valid-model-id>"
            )
        except AuthenticationError:
            raise RuntimeError(
                "OpenRouter API key is invalid or expired.\n"
                "Get a new key at: https://openrouter.ai/keys"
            )
        except Exception:
            if attempt == _max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


async def llm_call(
    client: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    tracker: TokenTracker | None = None,
) -> str:
    """Async wrapper: run the synchronous OpenAI client in a thread."""
    return await asyncio.to_thread(
        llm_call_sync, client, model, system_prompt, user_prompt, tracker
    )
