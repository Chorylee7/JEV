# JEV 评估脚手架（eval/）

在你自己的样本上评估 **TypeSafe JEV**（以及可选的本地 Laya）在"类型化决策 / 分流"场景的真实表现。核心指标面向分流场景设计：**弃权率 / 自动处理率 / 自动处理区间准确率**、校准（ECE）、抖动（flip rate）、串联成功率、成本与延迟。

## 环境要求

- Python 3.10+
- **核心功能零依赖**：只用标准库（`urllib` + `concurrent.futures`），不需要 `pip install` 任何东西即可跑 `jev` 与 `mock`
- 可选：`pip install laya`（见 `requirements.txt`），用于 `--provider laya` 本地模型对照

## 环境变量

| 变量 | 说明 |
|---|---|
| `TYPESAFE_API_KEY` | JEV API key（**官方名称**）。`--provider jev` 时必填 |
| `TYPESAPE_API_KEY` | 兼容别名（常见的拼写变体），优先级低于上面那个 |

没有 key 时直接用 `--provider mock` 跑通全流程。

## 样本格式（JSONL，每行一个样本）

```json
{"id":"t-001","state":"...文本或对象...","questions":{"urgency":{"type":"noul","instructions":"..."},"route":{"type":"choice","instructions":"...","criteria":{"billing":"...","technical":"..."}}},"expected":{"urgency":true,"route":"billing"}}
```

- `state`：字符串 / 对象 / 数组，原样发给 API
- `questions`：key 自取，三种类型与官方 API 一致：
  - `noul`：`criteria` 可选（`{"true":"...","false":"..."}`）
  - `choice`：`criteria` 必填（选项 key → 描述，描述可为 `null`）
  - `score`：`criteria` 为有序级别描述数组（2–10 级）
- `expected` 取值约定：
  - noul → `true/false`（兼容 `0/1`、`"true"/"false"`）
  - choice → 选项 key 字符串
  - score → 级别序号（int 或数字字符串）**或**级别描述字符串（与 criteria 中某一项精确/忽略大小写匹配）

参考 `samples.example.jsonl`（5 条电商客服假样本，覆盖三种类型）。

## 用法

```bash
# 无 key 先跑通流程（内置假模型）
python3 eval/run_eval.py --samples eval/samples.example.jsonl --provider mock --repeat 3 --out reports/smoke

# 真实 JEV
export TYPESAFE_API_KEY=sk-...
python3 eval/run_eval.py --samples eval/samples.example.jsonl --provider jev \
  --threshold 0.6 --repeat 3 --concurrency 8 --out reports/run1

# 本地 Laya（需 pip install laya）
python3 eval/run_eval.py --samples eval/samples.example.jsonl --provider laya --out reports/laya1
```

## CLI 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--samples` | （必填） | JSONL 样本文件路径 |
| `--provider` | `mock` | `jev` / `laya` / `mock` |
| `--threshold` | `0.6` | 弃权置信阈值：置信分低于此值视为弃权（转人工） |
| `--repeat` | `3` | 每样本重复次数，用于统计抖动 |
| `--concurrency` | `8` | 并发请求数（官方限速 1200 req/min、250k tok/s，429 会自动按 `retry-after` 退避重试） |
| `--out` | （必填） | 报告输出目录 |
| `--model` | `jev-latest` | JEV 模型 ID；正式对比建议 pin 版本化 ID（如 `jev-1.13.0`），别名会随版本移动 |
| `--mock-noise` | `0.1` | mock 预测错误率 |
| `--seed` | `42` | mock 随机种子（固定后可复现） |

## 输出文件

`--out` 目录下生成两个文件：

- `report.md`：人类可读报告，含核心分流指标、各问题准确率、校准与抖动、串联成功率及理论对照、成本与延迟
- `report.json`：同一份数据的机器可读版，附全部逐条判定记录（`records`，含 raw_answer），可自行二次分析

## 指标定义

判定函数（对每条「样本 × 重复 × 问题」记录）：

- noul → 预测 `true` 当且仅当 `answer.noul >= 0.5`；置信分 = `max(p, 1-p)`
- choice → 预测 `answer.choice`；置信分 = `max(probabilities.values())`
- score → 预测 `argmax(probabilities)` 对应级别；置信分 = 该级别的概率

> **注意：刻意不使用官方响应里的 `confidence` 字段。** 本仓库调研（`research/` 目录）发现该字段由概率分布导出，在所有对照中从未优于 `max(probabilities)`，因此统一用 max(prob) 口径，三种问题类型一致可比。noul 答案官方本就不带 confidence 字段。

汇总指标：

| 指标 | 定义 |
|---|---|
| 总体准确率 | 全部记录上预测 == expected 的比例 |
| **弃权率** | 置信分 < `--threshold` 的记录比例（分流中需转人工的部分） |
| **自动处理率** | 1 − 弃权率 |
| **自动处理区间准确率** | 仅自动处理子集上的准确率（分流场景最关键的指标） |
| ECE | 10 个等宽置信 bin 上的期望校准误差，越低越好 |
| 抖动 flip rate | 同一「样本 × 问题」重复 N 次中，与多数派预测不一致的比例 |
| 串联成功率 | 单样本所有问题全对记 1 的均值；报告附「单项准确率 p、串联 n 项 → p^n」理论对照表 |
| 成本 | Σ input_tokens × $0.042 / 1e6（output 免费）；mock/laya 不产生真实费用 |
| 延迟 | 每次 API 调用的 p50 / p95 |

## Provider 说明

- `jev`：直连 `POST https://api.typesafe.ai/v1/systemone`，429/5xx 自动退避重试（遵守 `retry-after`），记录每次调用的延迟与 usage
- `laya`（可选）：本地模型，`pip install laya` 后可用。按官方 README 的 `Router(preload=True).predict(state, questions)` 调用；noul 转成 true/false 两选项 choice、score 转成级别选项 choice 后映射回 JEV 答案形态，choice 直传。import 失败会给出中文提示并退出
- `mock`：不联网，按样本 `expected` 加 `--mock-noise` 错误率生成形态完整的假预测（含概率分布），保证无 API key 也能验证全流程与报告格式

## 已知局限

- **mock 不是真模型**：它的"准确率"约等于 `1 - mock-noise`，只用于验证流程，不代表任何模型能力
- **JEV 实际表现受地区可用性与限速影响**：官方称限速动态调整；超限会触发 429 退避，拉长总耗时（据第三方报道服务未对中国大陆开放，官方文档无地区清单）
- JEV 官方自述英语表现最好，CJK"能处理但不同样好"——中文样本请自行调阈值并关注弃权率
- 串联理论对照 `p^n` 假设各问题独立，实测串联成功率可能高于或低于该值
- Laya 基座 checkpoint 零样本能力有限（其模型卡自述 zero-shot 接近随机），微调后数字才有参考意义
- 样本量小时各指标波动大，建议至少几十条样本再下结论
