from __future__ import annotations

from collections import Counter
from typing import Any

from jev_client import PRICE_PER_INPUT_TOKEN_USD, CallResult


def normalize_expected(q: dict[str, Any], expected: Any) -> Any:
    qtype = q.get("type")
    if expected is None:
        return None
    if qtype == "noul":
        if isinstance(expected, str):
            s = expected.strip().lower()
            if s in ("true", "1", "yes"):
                return True
            if s in ("false", "0", "no"):
                return False
            return None
        return bool(expected)
    if qtype == "choice":
        return str(expected)
    if qtype == "score":
        levels = [str(x) for x in (q.get("criteria") or [])]
        if isinstance(expected, bool):
            return int(expected)
        if isinstance(expected, int):
            return expected
        if isinstance(expected, float):
            return int(expected)
        if isinstance(expected, str):
            s = expected.strip()
            if s.lstrip("-").isdigit():
                return int(s)
            for i, desc in enumerate(levels):
                if s == desc or s.lower() == desc.lower():
                    return i
        return None
    return expected


def judge(q: dict[str, Any], answer: dict[str, Any], expected: Any) -> tuple[Any, float, bool | None]:
    """返回 (预测值, 置信分, 是否正确)。置信分不使用官方 confidence 字段。"""
    qtype = q.get("type")
    exp = normalize_expected(q, expected)

    if qtype == "noul":
        p = float(answer.get("noul", 0.5))
        pred = p >= 0.5
        conf = max(p, 1.0 - p)
    elif qtype == "choice":
        probs = {k: float(v) for k, v in (answer.get("probabilities") or {}).items()}
        pred = str(answer.get("choice", ""))
        conf = max(probs.values()) if probs else 1.0
    elif qtype == "score":
        probs = {k: float(v) for k, v in (answer.get("probabilities") or {}).items()}
        if probs:
            best = max(probs, key=lambda k: probs[k])
            pred = int(best) if str(best).lstrip("-").isdigit() else best
            conf = probs[best]
        else:
            pred = int(round(float(answer.get("score", 0.0))))
            conf = 1.0
    else:
        raise ValueError(f"未知问题类型: {qtype!r}")

    correct = (pred == exp) if exp is not None else None
    return pred, conf, correct


def percentile(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def ece(records: list[dict[str, Any]], bins: int = 10) -> float | None:
    pts = [
        (r["confidence"], r["correct"])
        for r in records
        if r["correct"] is not None and r["confidence"] is not None
    ]
    if not pts:
        return None
    total = len(pts)
    value = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(c, ok) for c, ok in pts if lo <= c < hi or (b == bins - 1 and c >= hi)]
        if not sel:
            continue
        acc = sum(1 for _, ok in sel if ok) / len(sel)
        conf = sum(c for c, _ in sel) / len(sel)
        value += len(sel) / total * abs(acc - conf)
    return value


def compute_metrics(
    records: list[dict[str, Any]],
    calls: list[CallResult],
    threshold: float,
) -> dict[str, Any]:
    scored = [r for r in records if r["correct"] is not None]
    n = len(scored)
    accuracy = sum(1 for r in scored if r["correct"]) / n if n else None

    abstained = [r for r in records if r["confidence"] is not None and r["confidence"] < threshold]
    abstain_rate = len(abstained) / len(records) if records else None
    auto = [
        r for r in scored
        if r["confidence"] is not None and r["confidence"] >= threshold
    ]
    auto_rate = 1.0 - abstain_rate if abstain_rate is not None else None
    auto_accuracy = sum(1 for r in auto if r["correct"]) / len(auto) if auto else None

    per_question: dict[str, dict[str, Any]] = {}
    for r in records:
        qname = r["question"]
        slot = per_question.setdefault(
            qname, {"type": r["qtype"], "n": 0, "correct": 0, "abstained": 0}
        )
        slot["n"] += 1
        if r["correct"]:
            slot["correct"] += 1
        if r["confidence"] is not None and r["confidence"] < threshold:
            slot["abstained"] += 1
    for slot in per_question.values():
        slot["accuracy"] = slot["correct"] / slot["n"] if slot["n"] else None
        slot["abstain_rate"] = slot["abstained"] / slot["n"] if slot["n"] else None

    groups: dict[tuple[str, str], list[Any]] = {}
    for r in records:
        groups.setdefault((r["sample_id"], r["question"]), []).append(r["prediction"])
    flips = []
    for preds in groups.values():
        if len(preds) <= 1:
            flips.append(0.0)
            continue
        majority_count = Counter(preds).most_common(1)[0][1]
        flips.append(1.0 - majority_count / len(preds))
    flip_rate = sum(flips) / len(flips) if flips else None

    chains: dict[tuple[str, int], list[bool]] = {}
    for r in scored:
        chains.setdefault((r["sample_id"], r["repeat"]), []).append(bool(r["correct"]))
    chained = (
        sum(1 for oks in chains.values() if all(oks)) / len(chains) if chains else None
    )

    max_q = max((len(v) for v in chains.values()), default=0)
    theory = []
    if accuracy is not None:
        for k in range(1, max(max_q, 1) + 1):
            theory.append({"n": k, "p_pow_n": round(accuracy**k, 4)})

    latencies = [c.latency_s for c in calls]
    total_in = sum(c.input_tokens for c in calls)
    total_out = sum(c.output_tokens for c in calls)

    return {
        "n_records": len(records),
        "n_calls": len(calls),
        "accuracy": accuracy,
        "abstain_rate": abstain_rate,
        "auto_rate": auto_rate,
        "auto_accuracy": auto_accuracy,
        "ece": ece(records),
        "flip_rate": flip_rate,
        "chained_success": chained,
        "chained_theory": theory,
        "per_question": per_question,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "cost_usd": total_in * PRICE_PER_INPUT_TOKEN_USD,
        "latency_p50_s": percentile(latencies, 0.5),
        "latency_p95_s": percentile(latencies, 0.95),
    }
