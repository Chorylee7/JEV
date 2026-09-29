from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

API_URL = "https://api.typesafe.ai/v1/systemone"
PRICE_PER_INPUT_TOKEN_USD = 0.042 / 1e6


@dataclass
class CallResult:
    answers: dict[str, Any]
    model: str
    input_tokens: int
    output_tokens: int
    latency_s: float


class JevApiError(Exception):
    pass


class JevClient:
    def __init__(
        self,
        api_key: str,
        model: str = "jev-latest",
        url: str = API_URL,
        timeout: float = 60.0,
        max_retries: int = 6,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries

    def predict(self, state: Any, questions: dict[str, Any]) -> CallResult:
        payload = json.dumps(
            {"state": state, "model": self.model, "questions": questions}
        ).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        attempt = 0
        while True:
            req = urllib.request.Request(self.url, data=payload, headers=headers, method="POST")
            t0 = time.monotonic()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                latency = time.monotonic() - t0
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", errors="replace")[:500]
                if e.code == 429 or e.code >= 500:
                    attempt += 1
                    if attempt > self.max_retries:
                        raise JevApiError(f"重试 {self.max_retries} 次后仍失败：HTTP {e.code} {detail}")
                    time.sleep(self._retry_wait(e, attempt))
                    continue
                raise JevApiError(f"HTTP {e.code}: {detail}")
            except (urllib.error.URLError, TimeoutError) as e:
                attempt += 1
                if attempt > self.max_retries:
                    raise JevApiError(f"网络错误，重试 {self.max_retries} 次后仍失败：{e}")
                time.sleep(min(0.5 * 2**attempt, 20.0))
                continue
            usage = body.get("usage") or {}
            return CallResult(
                answers=body.get("answers") or {},
                model=str(body.get("model") or self.model),
                input_tokens=int(usage.get("input_tokens") or 0),
                output_tokens=int(usage.get("output_tokens") or 0),
                latency_s=latency,
            )

    def _retry_wait(self, err: urllib.error.HTTPError, attempt: int) -> float:
        retry_after = err.headers.get("retry-after") if err.headers else None
        if retry_after:
            try:
                return max(0.1, float(retry_after))
            except ValueError:
                pass
        return min(0.5 * 2**attempt, 30.0)
