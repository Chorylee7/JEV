from __future__ import annotations

import json
import random
import threading
import time
from typing import Any

from jev_client import CallResult, JevClient


class Provider:
    name = "base"

    def predict(self, sample: dict[str, Any]) -> CallResult:
        raise NotImplementedError


class JevProvider(Provider):
    name = "jev"

    def __init__(self, client: JevClient) -> None:
        self.client = client

    def predict(self, sample: dict[str, Any]) -> CallResult:
        return self.client.predict(sample["state"], sample["questions"])


class MockProvider(Provider):
    """不联网，按样本 expected 加噪声生成假预测，用于跑通全流程。"""

    name = "mock"

    def __init__(self, noise: float = 0.1, seed: int = 42) -> None:
        self.noise = noise
        self._rng = random.Random(seed)
        self._lock = threading.Lock()

    def predict(self, sample: dict[str, Any]) -> CallResult:
        t0 = time.monotonic()
        expected = sample.get("expected") or {}
        with self._lock:
            answers = {
                qname: self._fake(q, expected.get(qname))
                for qname, q in sample["questions"].items()
            }
        latency = time.monotonic() - t0
        est_tokens = len(
            json.dumps(
                {"state": sample["state"], "questions": sample["questions"]},
                ensure_ascii=False,
            )
        ) // 4
        return CallResult(
            answers=answers,
            model="mock-1.0",
            input_tokens=est_tokens,
            output_tokens=0,
            latency_s=latency,
        )

    def _fake(self, q: dict[str, Any], expected: Any) -> dict[str, Any]:
        rng = self._rng
        correct = rng.random() >= self.noise
        qtype = q.get("type")

        if qtype == "noul":
            if isinstance(expected, str):
                exp = expected.strip().lower() in ("true", "1", "yes")
            elif expected is None:
                exp = rng.random() < 0.5
            else:
                exp = bool(expected)
            pred_true = exp if correct else not exp
            p = rng.uniform(0.55, 0.99) if pred_true else rng.uniform(0.01, 0.45)
            return {"type": "noul", "noul": round(p, 4)}

        if qtype == "choice":
            options = list((q.get("criteria") or {}).keys()) or ["true", "false"]
            exp = expected if expected in options else rng.choice(options)
            others = [o for o in options if o != exp]
            winner = exp if correct or not others else rng.choice(others)
            winner_p = rng.uniform(0.55, 0.95)
            probs = self._spread(options, winner, winner_p)
            return {
                "type": "choice",
                "choice": winner,
                "probabilities": probs,
                "confidence": round(winner_p * rng.uniform(0.7, 0.95), 4),
            }

        if qtype == "score":
            levels = [str(x) for x in (q.get("criteria") or ["low", "mid", "high"])]
            n = len(levels)
            idx = self._expected_level(expected, levels, n)
            others = [i for i in range(n) if i != idx]
            winner = idx if correct or not others else rng.choice(others)
            winner_p = rng.uniform(0.55, 0.95)
            keys = [str(i) for i in range(n)]
            probs = self._spread(keys, str(winner), winner_p)
            score = sum(i * probs[str(i)] for i in range(n))
            return {
                "type": "score",
                "score": round(score, 4),
                "legend": {str(i): levels[i] for i in range(n)},
                "probabilities": probs,
                "confidence": round(winner_p * rng.uniform(0.7, 0.95), 4),
            }

        raise ValueError(f"未知问题类型: {qtype!r}")

    def _spread(self, keys: list[str], winner: str, winner_p: float) -> dict[str, float]:
        rng = self._rng
        rest = [k for k in keys if k != winner]
        weights = [rng.random() + 0.01 for _ in rest]
        total = sum(weights)
        probs = {winner: winner_p}
        for k, w in zip(rest, weights):
            probs[k] = (1.0 - winner_p) * w / total
        return {k: round(v, 4) for k, v in probs.items()}

    def _expected_level(self, expected: Any, levels: list[str], n: int) -> int:
        if isinstance(expected, bool):
            return int(expected)
        if isinstance(expected, int):
            return max(0, min(expected, n - 1))
        if isinstance(expected, str):
            s = expected.strip()
            if s.lstrip("-").isdigit():
                return max(0, min(int(s), n - 1))
            for i, desc in enumerate(levels):
                if s == desc or s.lower() == desc.lower():
                    return i
        return self._rng.randrange(n)


class LayaProvider(Provider):
    """本地 Laya 模型（可选依赖）。noul/score 转成 choice 提问后映射回 JEV 答案形态。"""

    name = "laya"

    def __init__(self) -> None:
        try:
            from laya import Router
        except ImportError as e:
            raise RuntimeError(
                "未安装 laya，无法使用 --provider laya。\n"
                "请先运行：pip install laya（会拉取 torch / transformers 等依赖，并下载模型权重），\n"
                "或改用 --provider jev / --provider mock。"
            ) from e
        self._router = Router(preload=True)

    def predict(self, sample: dict[str, Any]) -> CallResult:
        converted = {k: self._convert(q) for k, q in sample["questions"].items()}
        t0 = time.monotonic()
        res = self._router.predict(sample["state"], converted)
        latency = time.monotonic() - t0
        raw = res.get("answers") or {}
        answers = {
            k: self._map_back(q, raw.get(k) or {})
            for k, q in sample["questions"].items()
        }
        routing = res.get("routing") or {}
        return CallResult(
            answers=answers,
            model=f"laya-{routing.get('model', 'local')}",
            input_tokens=0,
            output_tokens=0,
            latency_s=latency,
        )

    def _convert(self, q: dict[str, Any]) -> dict[str, Any]:
        qtype = q.get("type")
        if qtype == "noul":
            criteria = q.get("criteria") or {}
            return {
                "type": "choice",
                "instructions": q.get("instructions", ""),
                "criteria": {"true": criteria.get("true"), "false": criteria.get("false")},
            }
        if qtype == "score":
            levels = [str(x) for x in (q.get("criteria") or [])]
            return {
                "type": "choice",
                "instructions": q.get("instructions", ""),
                "criteria": {str(i): desc for i, desc in enumerate(levels)},
            }
        return q

    def _map_back(self, q: dict[str, Any], ans: dict[str, Any]) -> dict[str, Any]:
        qtype = q.get("type")
        probs = {str(k): float(v) for k, v in (ans.get("probabilities") or {}).items()}
        if qtype == "noul":
            p_true = probs.get("true", 1.0 - probs.get("false", 0.5))
            return {"type": "noul", "noul": round(p_true, 4)}
        if qtype == "score":
            levels = [str(x) for x in (q.get("criteria") or [])]
            score = 0.0
            for k, p in probs.items():
                if k.lstrip("-").isdigit():
                    score += int(k) * p
            return {
                "type": "score",
                "score": round(score, 4),
                "legend": {str(i): levels[i] for i in range(len(levels))},
                "probabilities": probs,
                "confidence": max(probs.values()) if probs else 0.0,
            }
        return ans
