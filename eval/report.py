from __future__ import annotations

import json
from typing import Any


def _pct(x: float | None) -> str:
    return "N/A" if x is None else f"{x * 100:.1f}%"


def _num(x: float | None, nd: int = 4) -> str:
    return "N/A" if x is None else f"{x:.{nd}f}"


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["meta"]
    s = report["summary"]
    lines: list[str] = []
    add = lines.append

    add("# JEV 评估报告")
    add("")
    add(f"- 日期：{meta['date']}")
    add(f"- provider：`{meta['provider']}`（model：`{meta['model']}`）")
    add(f"- 样本文件：`{meta['samples_file']}`（{meta['n_samples']} 条样本 × 每样本重复 {meta['repeat']} 次 = {s['n_calls']} 次调用）")
    add(f"- 置信阈值：{meta['threshold']}（低于此值视为弃权，转人工）")
    if meta["provider"] == "mock":
        add(f"- mock 噪声：{meta['mock_noise']}，随机种子：{meta['seed']}")
    add("")

    add("## 核心分流指标")
    add("")
    add("| 指标 | 值 | 含义 |")
    add("|---|---|---|")
    add(f"| 总体准确率 | {_pct(s['accuracy'])} | 全部「样本×重复×问题」记录上的准确率 |")
    add(f"| 弃权率 | {_pct(s['abstain_rate'])} | 置信分 < 阈值、需转人工的比例 |")
    add(f"| 自动处理率 | {_pct(s['auto_rate'])} | 1 − 弃权率 |")
    add(f"| 自动处理区间准确率 | {_pct(s['auto_accuracy'])} | 自动处理子集上的准确率 |")
    add("")

    add("## 各问题准确率")
    add("")
    add("| 问题 | 类型 | 样本数 | 准确率 | 弃权率 |")
    add("|---|---|---|---|---|")
    for qname, slot in s["per_question"].items():
        add(
            f"| {qname} | {slot['type']} | {slot['n']} "
            f"| {_pct(slot['accuracy'])} | {_pct(slot['abstain_rate'])} |"
        )
    add("")

    add("## 校准与稳定性")
    add("")
    add(f"- ECE（10 bins，按置信分）：{_num(s['ece'])}（越低越好）")
    add(f"- 抖动（flip rate）：{_pct(s['flip_rate'])}（重复 {meta['repeat']} 次中与多数派预测不一致的比例）")
    add("")

    add("## 串联成功率")
    add("")
    add(f"- 实测串联成功率（单样本全部问题全对）：{_pct(s['chained_success'])}")
    add("")
    add("理论对照：若单项准确率为 p，串联 n 项的期望成功率为 p^n：")
    add("")
    add("| 串联项数 n | p^n |")
    add("|---|---|")
    for row in s["chained_theory"]:
        add(f"| {row['n']} | {_num(row['p_pow_n'])} |")
    add("")

    add("## 成本与延迟")
    add("")
    add(f"- 总 input tokens：{s['total_input_tokens']}，总 output tokens：{s['total_output_tokens']}")
    add(f"- 估算成本：${s['cost_usd']:.6f}（按 $0.042 / 百万 input token，output 免费）")
    add(f"- 延迟 p50：{s['latency_p50_s'] * 1000:.0f} ms，p95：{s['latency_p95_s'] * 1000:.0f} ms")
    add("")

    add("## 说明与备注")
    add("")
    add("- 置信分口径：noul 取 `max(p, 1-p)`；choice 取 `max(probabilities.values())`；score 取 argmax 级别的概率。"
        "**刻意不使用官方响应里的 `confidence` 字段**——本仓库调研发现它在所有对照中从未优于 `max(probabilities)`（见 research/ 目录）。")
    if meta["provider"] == "mock":
        add("- **本次为 mock 运行**：预测由样本 expected 加噪声生成，不代表任何真实模型能力，仅用于验证流程。")
    if meta["provider"] == "laya":
        add("- Laya 为本地模型，成本按 0 计；其零样本能力有限（基座 checkpoint 接近随机），微调后才有参考意义。")
    add("- JEV 实际表现受地区可用性与限速（429 退避）影响；正式对比请 pin 版本化 model ID 而非 `jev-latest`。")
    add("")
    return "\n".join(lines)


def write_reports(report: dict[str, Any], out_dir: str) -> tuple[str, str]:
    import os

    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "report.json")
    md_path = os.path.join(out_dir, "report.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(report))
    return json_path, md_path
