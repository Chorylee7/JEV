#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime
import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jev_client import JevApiError, JevClient
from metrics import compute_metrics, judge
from providers import JevProvider, LayaProvider, MockProvider, Provider
from report import write_reports

VALID_TYPES = ("noul", "choice", "score")


def load_samples(path: str) -> list[dict[str, Any]]:
    samples = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"样本文件第 {lineno} 行不是合法 JSON：{e}")
            for field in ("id", "state", "questions"):
                if field not in s:
                    raise SystemExit(f"样本文件第 {lineno} 行缺少必填字段 `{field}`")
            for qname, q in s["questions"].items():
                if q.get("type") not in VALID_TYPES:
                    raise SystemExit(
                        f"样本 {s['id']} 的问题 `{qname}` 类型无效：{q.get('type')!r}"
                        f"（仅支持 {VALID_TYPES}）"
                    )
            samples.append(s)
    if not samples:
        raise SystemExit(f"样本文件为空：{path}")
    return samples


def make_provider(args: argparse.Namespace) -> Provider:
    if args.provider == "mock":
        return MockProvider(noise=args.mock_noise, seed=args.seed)
    if args.provider == "laya":
        try:
            return LayaProvider()
        except RuntimeError as e:
            raise SystemExit(str(e))
    api_key = os.environ.get("TYPESAFE_API_KEY") or os.environ.get("TYPESAPE_API_KEY")
    if not api_key:
        raise SystemExit(
            "未找到 JEV API key。\n"
            "请设置环境变量 TYPESAFE_API_KEY（官方名称；也兼容 TYPESAPE_API_KEY），例如：\n"
            "  export TYPESAFE_API_KEY=sk-...\n"
            "暂时没有 key 可先用内置假模型跑通全流程：--provider mock"
        )
    return JevProvider(JevClient(api_key=api_key, model=args.model))


def run_one(provider: Provider, sample: dict[str, Any], repeat_idx: int):
    call = provider.predict(sample)
    records = []
    expected = sample.get("expected") or {}
    for qname, q in sample["questions"].items():
        answer = call.answers.get(qname)
        if answer is None:
            raise JevApiError(f"样本 {sample['id']} 的响应中缺少问题 `{qname}` 的答案")
        pred, conf, correct = judge(q, answer, expected.get(qname))
        records.append(
            {
                "sample_id": sample["id"],
                "repeat": repeat_idx,
                "question": qname,
                "qtype": q["type"],
                "prediction": pred,
                "confidence": round(conf, 4),
                "correct": correct,
                "raw_answer": answer,
            }
        )
    return records, call


def main() -> None:
    ap = argparse.ArgumentParser(
        description="在用户样本上评估 TypeSafe JEV（或本地 Laya / mock）的类型化决策表现"
    )
    ap.add_argument("--samples", required=True, help="JSONL 样本文件路径")
    ap.add_argument("--provider", choices=["jev", "laya", "mock"], default="mock")
    ap.add_argument("--threshold", type=float, default=0.6, help="弃权置信阈值，默认 0.6")
    ap.add_argument("--repeat", type=int, default=3, help="每样本重复次数（测抖动），默认 3")
    ap.add_argument("--concurrency", type=int, default=8, help="并发请求数，默认 8")
    ap.add_argument("--out", required=True, help="报告输出目录")
    ap.add_argument("--model", default="jev-latest", help="JEV 模型 ID，默认 jev-latest")
    ap.add_argument("--mock-noise", type=float, default=0.1, help="mock 错误率，默认 0.1")
    ap.add_argument("--seed", type=int, default=42, help="mock 随机种子，默认 42")
    args = ap.parse_args()

    samples = load_samples(args.samples)
    provider = make_provider(args)

    tasks = [(s, r) for s in samples for r in range(args.repeat)]
    records: list[dict[str, Any]] = []
    calls = []
    errors = []
    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(run_one, provider, s, r): (s["id"], r) for s, r in tasks}
        for fut in cf.as_completed(futs):
            sid, r = futs[fut]
            try:
                recs, call = fut.result()
            except Exception as e:
                errors.append(f"样本 {sid} 第 {r + 1} 次重复失败：{e}")
                continue
            records.extend(recs)
            calls.append(call)

    if errors:
        print("部分调用失败：", file=sys.stderr)
        for e in errors[:10]:
            print(f"  - {e}", file=sys.stderr)
        if len(errors) > 10:
            print(f"  … 共 {len(errors)} 个失败", file=sys.stderr)
    if not records:
        raise SystemExit("所有调用均失败，无法生成报告。")

    summary = compute_metrics(records, calls, args.threshold)
    report = {
        "meta": {
            "date": datetime.date.today().isoformat(),
            "provider": args.provider,
            "model": calls[0].model if calls else args.model,
            "samples_file": args.samples,
            "n_samples": len(samples),
            "repeat": args.repeat,
            "threshold": args.threshold,
            "concurrency": args.concurrency,
            "mock_noise": args.mock_noise,
            "seed": args.seed,
        },
        "summary": summary,
        "errors": errors,
        "records": records,
    }
    json_path, md_path = write_reports(report, args.out)

    def pct(x):
        return "N/A" if x is None else f"{x * 100:.1f}%"

    print(f"完成：{summary['n_calls']} 次调用，{summary['n_records']} 条判定记录")
    print(f"  总体准确率        {pct(summary['accuracy'])}")
    print(f"  弃权率            {pct(summary['abstain_rate'])}（阈值 {args.threshold}）")
    print(f"  自动处理率        {pct(summary['auto_rate'])}")
    print(f"  自动处理区间准确率 {pct(summary['auto_accuracy'])}")
    print(f"  ECE               {summary['ece'] if summary['ece'] is None else round(summary['ece'], 4)}")
    print(f"  抖动 flip rate    {pct(summary['flip_rate'])}")
    print(f"  串联成功率        {pct(summary['chained_success'])}")
    print(f"  成本              ${summary['cost_usd']:.6f}，延迟 p50 {summary['latency_p50_s'] * 1000:.0f} ms / p95 {summary['latency_p95_s'] * 1000:.0f} ms")
    print(f"报告：{md_path}")
    print(f"     {json_path}")


if __name__ == "__main__":
    main()
