<div align="center">

# JEV Research Report

**TypeSafe's System One Decision Model and Its Open-Source Alternatives**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.3-blue)](CHANGELOG.md)
[![Data Snapshot](https://img.shields.io/badge/data%20snapshot-2026--09--29-orange)](CHANGELOG.md)
[![GitHub Stars](https://img.shields.io/github/stars/Chorylee7/JEV?style=social)](https://github.com/Chorylee7/JEV/stargazers)

[⚡ Quick Reference Card](#quick-ref) · [📋 TL;DR](#tldr) · [🇨🇳 中文版 / Chinese version](README.md) · [🧪 Eval Harness](eval/) · [📜 Changelog](CHANGELOG.md)

</div>

> **About this document**: this is the English version of [README.md](README.md) v1.3 (2026-09-30). **How to read**: conclusions first — if you only want the answers, the "Quick Reference Card" below is enough. Every number carries an evidence tag: **[Official]** officially published · **[Third-party]** independent tests/media · **[Vendor-reported]** self-reported by the repo author · **[Unverified]** no primary source.
> **Basis of figures**: conclusions are based on verification as of 2026-09-21; star/license/ecosystem-size figures are 2026-09-29 snapshots (changes in [CHANGELOG](CHANGELOG.md)); **all benchmark numbers are, unless noted, self-reported by project authors or the vendor — this report ran no actual tests**.

## ⚡ Quick Reference Card <a id="quick-ref"></a>

| Dimension | Conclusion | Evidence |
|---|---|---|
| What it is | A hosted "decision model": `state` + typed questions → structured answers + probabilities; **it does not generate text** | [Official] |
| Three primitives | `noul` (0–1 yes/no) / `choice` (≤255 single-choice) / `score` (2–10 level ordinal rating) | [Official] |
| Price | $0.042 / million input tokens, output free; a 10k-token state ≈ $0.00042/call | [Official] |
| Latency | Official 70–500ms; independent measurement p50 314ms / p95 399ms | [Third-party] |
| Context | 64k per request; `state` + longest single question ≤ 32k; **text input only** | [Official] |
| Speed claims | Official 193.6× (homepage) and 40×–200× (launch post) are **mutually contradictory**; independent measurements 4.8×–25× | [Official/Third-party] |
| Cost claims | Official 444.6× (only against the most expensive model row); independent measurements 8.6×–580×; the Chinese-language test found only ~2.7× | [Official/Third-party] |
| Accuracy | Official average across four workflows 67.8% (≈ Terra / Sonnet 5 tier); binary gating can reach 100% (LangChain, 500 runs against a human oracle) | [Official/Third-party] |
| Notable weaknesses | Invoice processing 61.8% (8th of 9 models), Chinese customer service 64–65%, 0.78 on 77-class intent, arithmetic/date/indirect reasoning | [Official/Third-party] |
| Abstain rate | A measured 30% abstain rate compresses a 76× cost advantage to **3.2×**; the ceiling is `1/abstain rate` | [Third-party] |
| Probability calibration | Good on knowable tasks (ECE 0.024 ≈ noise floor), overconfident on unknowable tasks (ECE 0.107); **do not use the official `confidence` field — use `max(probabilities)`** | [Third-party] |
| Data policy | Does not train on customer requests/responses; **ZDR is Enterprise-only** | [Official 09-29] |
| Current version | `jev-1.13.0` (verified 09-29, no preview builds) | [Official] |
| Open-source pick | **Laya** (Apache-2.0, 28.1k★, 33ms on a T4, post-finetune 0.766 > JEV 0.727; **degrades noticeably beyond 20 options**) | [Vendor-reported] |
| Scenarios to avoid | High-cardinality classification, Chinese-heavy workloads, numeric-threshold judgments, logically consistent probabilities, >100Hz control loops | Synthesis |

## 📋 This report answers four questions <a id="tldr"></a>

1. **What is JEV?** A hosted decision model that only makes judgments and writes no text → [§1](#s1-what-is-jev)
2. **Are the official "200× faster, 400× cheaper" claims credible?** The vendor's own numbers contradict each other; independent measurements land at 5–25× speed and 9–580× cost → [§2](#s2-claims-vs-evidence)
3. **What open-source alternatives exist?** About 20+ interface reproductions; the genuinely self-trained open-weight ones are Laya (28k★) and the just-entered Together AI `tev1` → [§3](#s3-landscape) · [§4](#s4-open-weight-models)
4. **Should I use it, and how?** Scenario-based decision table + a 7-item go-live checklist + an 8-item risk checklist → [§5](#s5-selection-guide) · [§6](#s6-risks)

<details>
<summary>📑 Full table of contents (click to expand)</summary>

1. [What is JEV](#s1-what-is-jev)
2. [Measured performance: official claims vs independent verification](#s2-claims-vs-evidence)
3. [The open-source landscape](#s3-landscape)
4. [Genuinely retrained open-weight decision models](#s4-open-weight-models)
5. [Selection guide](#s5-selection-guide)
6. [Risk checklist](#s6-risks)
7. [Appendix: verification methods, unverified list, and references](#s7-appendix)

</details>

---

## 🤖 1. What is JEV <a id="s1-what-is-jev"></a>

> *EN — JEV is TypeSafe AI's hosted "System One" decision model: typed questions in, structured answers with probabilities out, never free text.*

**In one sentence**: JEV is a "System One" decision model released by TypeSafe AI (San Francisco, founded 2024; founder Diogo Almeida is one of the authors of the InstructGPT paper; $40M seed round led by DCVC) on **2026-09-15** — **it only makes judgments and writes no text**: you pass in program state (`state`) and several typed questions, and one call returns structured answers with probabilities. Weights are closed-source; cloud API only.

### 1.1 Three primitives = its entire capability boundary

| Primitive | Semantics | Returns | Example |
|---|---|---|---|
| `noul` | yes/no | a single 0–1 probability (**no confidence field**) | "Is this message urgent?" |
| `choice` | single choice (**≤255 options**) | the option + `probabilities` (sum to 1) + `confidence` | "Which team should this route to?" |
| `score` | ordinal rating (**2–10 levels**) | a value (can fall between levels, e.g. 1.05) + distribution + `confidence` | "How angry is the customer, 1–5?" |

Note: **no ranking or span types**; `boolean` is just an alias some channels (e.g. Vercel) use for `noul`.

### 1.2 What one call looks like

Endpoint `POST https://api.typesafe.ai/v1/systemone`; all questions in one request are **evaluated in parallel** against the same `state` (official: "adding questions barely increases response time"):

```jsonc
// 请求（节选）
{
  "state": "Help! My payouts have been failing for 3 days.",
  "model": "jev-latest",
  "questions": {
    "route":  { "type": "choice", "instructions": "Which team should handle this?",
                "criteria": {"billing": "Payments, invoicing, refunds", "technical": "Bugs, outages"} },
    "urgent": { "type": "noul", "instructions": "Does this convey urgency?" }
  }
}
// 响应（节选）
{ "model": "jev-1.13.0",
  "answers": {
    "route":  { "choice": "technical", "probabilities": {"billing": 0.12, "technical": 0.88}, "confidence": 0.81 },
    "urgent": { "noul": 0.95 }
  },
  "usage": { "input_tokens": 318, "output_tokens": 34 } }
```

You name the keys of `questions`; answers come back under the same keys, and **the keys are not sent to the model**; `instructions` / `criteria` accept structured JSON. SDKs: Python `typesafe-sdk`, TS `@typesafe-ai/sdk`; the official Agent Skill is at [typesafe-ai/skills](https://github.com/typesafe-ai/skills) (MIT, 2,392★).

### 1.3 Specs, pricing, and hard limits

| Item | Value | Evidence |
|---|---|---|
| Price | $0.042 / million input tokens (**output free**); the vendor itself admits it "cannot prove it isn't subsidized" | [Official] |
| Latency | Official 70–500ms; independent measurement p50 314ms / p95 399ms | [Official/Third-party] |
| Rate limits | 250k tokens/second + 1,200 requests/minute, **stated to be dynamically adjusted and may change without notice** | [Official] |
| Context | 64k per request; `state` + longest single question ≤ 32k | [Official] |
| Input modality | **Text only** (no image/audio/video; the vendor notes "yet"); **no streaming** | [Official] |
| Language | Best in English; CJK "works but is not on equal footing" | [Official] |
| Weights/fine-tuning | Closed; all accounts share the same weights; no per-customer fine-tuning | [Official] |
| Version | `jev-1.13.0` (verified 09-29, no preview builds); pin a version ID in production | [Official] |
| Data policy | Does not train on customer requests/responses; **ZDR is Enterprise-only** | [Official 09-29] |
| Region | CNR reports it is "not available in mainland China"; the official terms **contain no explicit regional restriction** — judged on the official record, unconfirmed | [Third-party] |

### 1.4 Weaknesses the vendor itself admits (the jaggedness page)

The vendor devotes a standalone page to 9 categories of failure modes [Official]: **literal interpretation · arithmetic and counting · date comparison · indirect reasoning · large-state distraction · adversarial content · contradictions between instructions and criteria · structural invariants · generative tasks**. Two further counterintuitive points: **the probabilities of a question and its negation can sum to ≠ 1** (official example: 0.72 + 0.47 = 1.19); `score` is weakly calibrated numerically and cannot be interpolated back to exact numbers.

### 1.5 Two fun official demos

- **Doom**: fed a textual, structured game state (**it never sees the screen**), about 10 queries/second, $7/hour; the vendor self-deprecatingly notes that "a non-AI Doom bot plays better."
- **Wikiracing**: each step is a `choice` among hundreds to thousands of links; when there are more than 255 options it uses a "two-stage score-then-select" approach.

---

## 📊 2. Measured performance: official claims vs independent verification <a id="s2-claims-vs-evidence"></a>

> *EN — The vendor's headline multipliers contradict each other across its own pages; independent tests land at 4.8×–25× speed and 8.6×–580× cost; accuracy is highly task-dependent.*

### 2.1 Speed and cost: the vendor itself has four versions

| Source | Speed multiplier | Cost multiplier | Type |
|---|---|---|---|
| TypeSafe homepage | 193.6× | 444.6× | [Official] |
| TypeSafe launch post | 40×–200× | not published | [Official] |
| TypeSafe onboarding (login required) | 20×–200× | 40×–1,000× | [Official] |
| Hand-computed from the official evals table | ~25×–95× | 76×–440× | [Third-party derived] |
| **Independent measurements, combined** (Every / Near Here / gemanor / 4esv / Guixingren (Chinese-language outlet) / Capital & Compute) | **4.8×–25×** (p50 314ms falls within the official 70–500ms range) | **8.6×–580×** | [Third-party] |

**How to read it**: 444.6× comes from "comparing only against the most expensive Opus 5 row"; third-party measured medians land at **5×–25× speed, 10×–60× cost**. "Fast" is real, but "200×/400×" cannot be used for capacity planning.

### 2.2 Accuracy: the task decides everything

The official evals page's four workflows (this report parsed them directly from the page HTML, not via media relay):

| Workflow | JEV | Best on that workflow | JEV rank (of 9 models) |
|---|---|---|---|
| Security Incidents | 61.7% | Opus 5 workflow 66.2% | 3rd |
| **Invoice Processing** | **61.8%** | Sol workflow 79.1% | **8th (beats only Haiku 4.5)** |
| Customer Service | 76.0% | Sol workflow 78.3% | 4th |
| Agent Trace Observability | 71.6% | Sol workflow 76.6% | tied for 6th |
| **Average** | **67.8%** | Sol workflow 74.1% | — |

Third-party independent tests (excerpt; full version in [research/ecosystem-benchmarks.md](research/ecosystem-benchmarks.md) Table B):

| Test | Task | JEV | Comparison | Conclusion |
|---|---|---|---|---|
| LangChain (09-20) | 500 repeated binary judgments against a human oracle | **100%** | Terra 99.8% / Sonnet 4.6 80.0% | **First place, lowest variance**; total cost $0.34 vs Claude $28.17 |
| Arize | 18,514 real labeled emails | 98.3% | **TF-IDF 98.4%** | statistical tie |
| gemanor | 1,080 rule reviews | 98.0% | Gemini / Fable 100% | 2 points behind |
| 4esv | 77-class intent | 0.78 | Terra 0.85 | 7 points behind |
| Guixingren (Chinese-language outlet) | 50 Chinese customer-service items (scored only if all four parts are correct) | **64–65.2%** | MiniMax M3 10.8 points higher | **bottom** of the strong-model group |
| NanoJev (vendor) | ViZDoom Basic | 56/128 ≈ bare Qwen3-0.6B | NanoJev 128/128 | no gain on this task |

**Methodology warning**: the "correct answers" in the official evals are **the average of two LLM outputs** (not human labels; the vendor itself admits this biases toward OpenAI/Anthropic models); the vendor also admits the evals ran on an internal laptop, the workflows were built by internal teams, "0% type errors" was not actually measured, and the demo states are on the short side.

### 2.3 Two hidden variables that decide success or failure

**① Abstain rate — the cost killer.** With a measured 30% abstain rate, the cost advantage collapses from 76× to **3.2×**; the ceiling is `1/abstain rate`, independent of unit price. The abstain rate is of your own making: a thin state abstains 57.8% of the time; after adding 3 fields to the state, it fell from **65% to 40%** at a 0.5 threshold.

**② Calibration is two-sided.** Very good on knowable tasks (OpenBookQA ECE 0.024 ≈ noise floor; LangChain's 500 repeats had the lowest variance); overconfident on unknowable tasks (synthetic-ticket ECE **0.107** = 4.4× the noise floor; the `score` subtask needs a refit temperature of **3.40**); the official `confidence` field **never beat `max(probabilities)`** — use the latter directly with your own thresholds.

---

## 🌐 3. The open-source landscape <a id="s3-landscape"></a>

> *EN — Only ~20–25 repos actually implement the mechanism (out of 14k+ and counting); the dominant trick is "freeze an open LLM, read option-token logits, restricted softmax, skip decoding" — self-measured speedups are 4–5×, not 200×. Almost none claim calibrated probabilities; several explicitly disclaim it.*

### 3.1 Distinguish four layers first (otherwise the numbers are not comparable)

| Layer | Definition | Representatives | Local inference | Self-trained weights |
|---|---|---|---|---|
| L0 client application | writes its own prompts/schemas; still calls the cloud JEV API | `browser-use/jev-ultrafast`, `tamaratran/fast-jev-compaction`, `typesafe-ai/skills` | ✗ | ✗ |
| L1 interface reproduction | freezes an open model, **reads only the option-token logits** + restricted softmax, skips autoregressive decoding | `TheoLeeCJ/SemIf-OpenJev`, `r-ms/mini-jev`, `bnsd55/jevmlx`, `featherless-ai/simple-jev`, `ekzhang/openjev-sglang` | ✓ | ✗ (frozen) |
| L2 reproduction + self-trained head/adapter | trains its own scoring head or LoRA on top of L1 | `vinnylarouge/jevlike`, `TianyuCodings/NanoJev`, `jaredpalmer/kev`, `bespokelabsai/nimble`, `wfzyx/von`, `Mapika/decider`, `togethercomputer/tev1` | ✓ | ✓ (partial/adapter) |
| L3 self-developed decision model | trains its own model; releases weights and data | **Laya** (see §4) | ✓ | ✓ |

**Key point**: the "speedup multiples" of L1/L2 are all built on **skipping decoding**, while **prefill of the `state` cannot be skipped** — so their measured speedups are single-digit multiples, not 200×.

### 3.2 Core project comparison (stars are 2026-09-29 GitHub API snapshots)

| Repo | ★ | License | Base model | Hardware | HTTP service | Claims calibration |
|---|---:|---|---|---|---|---|
| [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) | **28,058** | Apache-2.0 | **Self-developed** ModernBERT-class (≈421M) | CPU / CUDA | SDK | ✓ (ECE 0.081 after temperature fitting) |
| [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | 21,264 | MIT | Cloud JEV + `inception/mercury-2.5` | any | — | — |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | 7,749 | Apache-2.0 | Qwen3.5-0.8B/4B/9B + LoRA | CUDA / Apple Silicon | ✓ | **explicitly disclaims** |
| [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | 7,167 | MIT | Cloud `jev-latest` | any | — | **explicitly disclaims** |
| [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) | 6,604 | Apache-2.0 | MLX port of Laya (not a JEV reproduction) | Apple Silicon | — | — |
| [TheoLeeCJ/SemIf-OpenJev](https://github.com/TheoLeeCJ/SemIf-OpenJev) (originally OpenJev→SemIf, renamed a second time on 09-22) | 4,547 | MIT | Qwen3.5-4B / MiniCPM5-2B / Qwen3-0.6B (frozen) | CUDA / Apple MLX / WebGPU | demo | requires users to calibrate themselves |
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | 2,419 | MIT | Qwen3-0.6B + self-trained decision heads | CUDA / CPU | ✓ | — |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | 1,897 | **none** | Qwen3.5-9B + LoRA | CUDA | ✓ | — |
| [vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike) | 1,332 | MIT | Byte-encoder trained from scratch / frozen Qwen2.5-0.5B | CPU / MPS / CUDA | — | no claim |
| [ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya) | 916 | Apache-2.0 | Serves Laya / decider / NLI / GLiClass locally ("the Ollama of decision models") | CPU / GPU | ✓ | — |
| [Mapika/decider](https://github.com/Mapika/decider) | 887 | Apache-2.0 | Qwen3.5-2B/0.8B/35B-A3B + vision variant | CUDA | — | ✓ (calibration-aware RL) |
| [wfzyx/von](https://github.com/wfzyx/von) | 763 | Apache-2.0 | ModernBERT-Large 395M | CPU / CUDA | ✓ | ✓ (T=1.1692) |
| [featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev) | 567 | **Apache-2.0** (license added 09-28; previously none) | Qwen3.5-0.8B / Gemma 4 26B-A4B / Laya | CPU / CUDA | ✓ | **explicitly disclaims** |
| [razorback16/openjev](https://github.com/razorback16/openjev) | 515 | Apache-2.0 | DiffusionGemma 26B-A4B | CUDA | — | — |
| [Liuziyu77/Valen](https://github.com/Liuziyu77/Valen) | 474 | Apache-2.0 | self-trained multimodal Jev-like training framework (incl. vision) | CUDA | — | — |
| [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) | 332 | **none** | Qwen3.6-35B-A3B (SGLang) | B200-class | ✓ | — |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | 291 | NOASSERTION | ModernBERT-base 151M + dual confidence heads | CPU / WebGPU | — | ✓ (ECE 1.44%, self-test receipt) |
| [APUS-AI-Lab/fast-browser-use](https://github.com/APUS-AI-Lab/fast-browser-use) | 178 | MIT | Qwen3.5-9B / 35B-A3B | GPU / GPU-less Mac/PC | ✓ | — |
| [togethercomputer/tev1](https://github.com/togethercomputer/tev1) | 165 | MIT | **Qwen3.5-4B LoRA fine-tune (Together AI)** | CUDA | — | — |
| [allebee/jevk5](https://github.com/allebee/jevk5) | 123 | Apache-2.0 | open-weight alternative | CUDA | — | — |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | 69 | MIT | Qwen2.5-7B/3B/1.5B-4bit (MLX) | Apple Silicon / CPU | ✓ | **explicitly disclaims** |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | 58 | MIT | Qwen3-4B-Instruct-2507 (frozen) | CUDA / MPS | ✓ | **explicitly disclaims** ("not calibrated probabilities") |
| [ikermoel/open-alternative-jev](https://github.com/ikermoel/open-alternative-jev) | 57 | Apache-2.0 | any open-weights model | CUDA | — | ✓ (MMLU ECE 5.4%→2.1%) |

**Not listed but worth knowing**: [`logan-markewich/jeff`](https://github.com/logan-markewich/jeff) (261★, applies GLiNER to decisions), [`fstandhartinger/jevbench`](https://github.com/fstandhartinger/jevbench) (175★, benchmarking tool), `dzhng/jevgrep` (1,574★, a code-retrieval CLI — an application, not a decision model), `Heman10x-NGU/Verdict-open-jev`, `deepanwadhwa/OpenDecision` (57★, NLI approach), `Micha0827/snapjudge` (14★, MLX), `NullPo-jp/PocketJev` (2★, Swift/iOS).

### 3.3 Quick takes on key projects

- **SemIf-OpenJev** (4,547★): the most representative and the most restrained project in the ecosystem. Two modes, direct/shared (state prefilled only once, KV reused across parallel questions); **self-measured speedup is only 5.21×** (RTX 3090); explicitly states it "never ran against the real Jev endpoint"; supports **running in-browser via WebGPU**.
- **mini-jev** (58★): the most rigorous evidence chain (pre-registration document + 27,900 HF records with logits). Its conclusion is the most unfavorable: **reading letter logits matches grammar-constrained generation in accuracy (Δ −0.22pp)**, with only a 4× speedup (short texts); it explicitly writes "not calibrated probabilities."
- **NanoJev** (2,419★): the only one with self-trained weights + fully public data; ViZDoom 128/128 vs JEV 56/128, but on Maze it lost 4/10 to JEV's 7/10 (the README keeps that line, undeleted).
- **kev** (7,749★): the most honest about limitations; Brier 0.291 vs JEV 0.211 (**JEV's distribution quality is better**); admits it is 4–7× slower than the previous generation on Apple Silicon.
- **tev1** (165★, **official Together AI**): the first established company to enter the field. Qwen3.5-4B LoRA SFT (37,840 training samples), **takes 2–24 options as input, outputs a single answer letter, gives no probabilities** — it is a constrained-generation classifier, a different paradigm from JEV; weights are public; the official blog says "train your own classifier for $17."
- **fast-browser-use** (178★, APUS): CNR, Science and Technology Daily and others call it "among the earliest reproductions worldwide," but its stars are far below community projects of the same period, and the README has no standalone Limitations section; technically it is a standard L1 (DOM element numbering + local Qwen3.5-9B scoring, about 4 calls per task).
- **nimble** (1,897★): the only one that dares to put its base model next to JEV — 324 held-out items: Nimble-9B 90.1% vs base 66.4% vs **JEV 93.2%** (fine-tuning catches up but does not surpass).
- **open-alternative-jev** (57★): the most honest benchmark — publicly admits it miscalculated and keeps the error analysis.
- **jev-ultrafast** (21.3k★, official browser-use): note that it is an **L0 cloud client** (compressing single-step interaction into one round trip); it represents usage optimization, **not a local replacement**.

### 3.4 Why reproduction projects only reach single-digit multiples

1. **Prefill cannot be skipped**: skipping decoding only saves generation itself; the longer the state, the less you save (mini-jev: 4× on short texts → 1.4–2.4× at 2048 tokens).
2. **No dedicated hardware/serving stack**: the official product is a 70–500ms hosted service; the community runs single RTX 3090 cards / M-series Macs.
3. **Different inference frameworks**: `ekzhang/openjev-sglang` uses SGLang's radix caching for prefill-only, one of the closest routes to an "engineering-grade" approach.

### 3.5 Ecosystem noise warning

- GitHub `q=jev` repos: ~**7,330** on 09-21 → ~**14,028** on 09-29 (+91% in 8 days) [GitHub API]; awesome-style directories already exceed **20**, most created in the first week after release.
- Reproductions that actually explain the mechanism and can run: about **20–25**; the warning from the author of `yibie/awesome-jev` is worth quoting: **"Be extra wary of projects submitted in batches on the same day — quantity is not quality."**
- The ecosystem directory sites (jevbest.com, madewithjev.com, as of 09-21) **both state they are unaffiliated with TypeSafe**; their star snapshots are systematically low; cite the basis when quoting ecosystem size.

---

## 🏗️ 4. Genuinely retrained open-weight decision models <a id="s4-open-weight-models"></a>

> *EN — Laya (Apache-2.0, 28k★, ~421M ModernBERT-class encoder + decision heads) is the dominant open-weight decision model: it beats JEV's published typed-decisions score (0.766 vs 0.727) and is ~7.8× faster — but all accuracy figures are self-reported, base checkpoints are near chance zero-shot, and it degrades badly above ~20 options. On 09-23 Together AI shipped tev1 (Qwen3.5-4B LoRA, returns a single answer letter, no option probabilities).*

### 4.1 Laya at a glance (already the ecosystem's #1 by stars as of 09-29)

| Item | Content |
|---|---|
| Repo | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya), **28,058★ / 2,446 forks** (09-29 snapshot; 5,060★ on 09-21, +454% in 8 days), Apache-2.0 |
| Author | Nandakishor Mukkunnoth (Convai Innovations, independent researcher; the main repo sits under his personal account) |
| Weights | HF [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya) (ModernBERT-large + decision heads, 421M, 4,395 likes), [`laya-multilingual`](https://huggingface.co/convaiinnovations/laya-multilingual) (mmBERT-base, 322M, 100+ languages), [`laya-typed-decisions`](https://huggingface.co/convaiinnovations/laya-typed-decisions) (fine-tuned version) |
| Channels | PyPI `laya` 0.3.4; [HF Space demo](https://huggingface.co/spaces/convaiinnovations/laya-demo); MLX port [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) (6,604★, M3 Max 7.4–13.4 ms/question); local serving [ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya) (916★, TypeSafe-compatible API) |
| Architecture | Bidirectional encoder + scoring each option at the `[MASK]` position, then softmax; **answers all questions in a single forward pass**; the answer space is defined at request time |
| Training | Self-described RLCD (strictly proper scoring-rule rewards, GRPO-style policy gradient), with a Kaggle 2×T4 fine-tuning notebook attached; **training data not public** (only AG News/BoolQ disclosed as part of the training mix) |
| Documentation | No standalone paper; technical documentation = model card + `BENCHMARKS.md` |

**Vendor-reported benchmarks (T4, against JEV's officially published numbers)**:

| Metric | JEV 1.13.0 (public numbers) | Laya (routed) | Notes |
|---|---|---|---|
| typed-decisions (2,000 decisions) | 0.727 | **0.766** | this checkpoint was fine-tuned on the training split of the same benchmark |
| AG News (4 labels) | 0.910 | **0.950** | in the training mix |
| DAIR Emotion (6 labels) | 0.480 | **0.595** | held-out; **JEV assigns zero probability to the true label on 16% of samples** |
| Banking77 (>20 options) | **0.870** | 0.425 | **JEV pulls ahead**: Laya's options share a fixed token budget |
| ECE (lower is better) | 0.246 | **0.081** | Laya needs temperature fitting first; **its out-of-the-box raw ECE 0.213 is actually worse than JEV's** |
| p50 latency (single question) | 236–276 ms | **32.8 ms** | ~7.8× |
| License | closed-source API | **Apache-2.0** | — |

**Credibility assessment**: the JEV-side numbers have independent provenance ([AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and others measured JEV at AG News 0.910 / Banking77 0.870 / p50 236–256ms); **all Laya-side accuracy numbers are currently vendor-reported only**, and no high-visibility independent retest has been seen yet.

**Limitations Laya itself admits (more honest than the ecosystem average)**:

- **The base checkpoint is near-random zero-shot**: 0.362 on typed-decisions (majority-class baseline 0.461); **0.766 comes entirely from fine-tuning** — it is "a fast base well suited to fine-tuning," not an out-of-the-box decision engine.
- **Degrades beyond 20 options**: at 77 options each label gets only 3–4 tokens (`head_max_len` defaults to 192/256), and Banking77 drops to 0.425; the fix is a larger budget or two-stage hierarchical selection.
- **`score` is the weakest** (SST-5 0.372); **overconfident out of the box**, and `laya-multilingual` ships with no fitted temperature at all.
- **Multilingual cannot rely on a single checkpoint**: the English checkpoint reaches only macro 0.227 across 51 languages with macro ECE 0.733, **and gives Khmer a score of 0.000 at 95.2% confidence**; switching to a model that is not preloaded triggers a 7–10s reload.
- **Soft-distribution quality still trails JEV** (0.471 vs 0.580).

### 4.2 Other self-trained / adapted approaches (L2 layer; none have seen third-party reruns)

| Project | What was self-trained | Position vs JEV |
|---|---|---|
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | Qwen3-0.6B + decision heads, **weights and data fully public** | ViZDoom 128/128 vs 56/128; Maze 4/10 vs 7/10 (self-admitted lag) |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | Qwen3.5 in three sizes + LoRA rank 16 | accuracy 0.812 vs JEV 0.857, **but Brier 0.291 vs JEV 0.211** |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | Qwen3.5-9B + LoRA (answer token only) | 324 held-out items: Nimble-9B 90.1%, base 66.4%, **JEV 93.2%** |
| [wfzyx/von](https://github.com/wfzyx/von) | ModernBERT-Large 395M + RLCD post-training | self-reported T=1.1692; two internally contradictory numbers in the README |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | ModernBERT-base 151M + dual confidence heads | self-reported ECE 1.44% (vendor test receipt only) |
| [Mapika/decider](https://github.com/Mapika/decider) | includes calibration-aware RL | no independent rerun verified |
| [togethercomputer/tev1](https://github.com/togethercomputer/tev1) | Qwen3.5-4B LoRA SFT (37,840 samples), **official Together AI** | self-reported 880/1,000 primary decisions, 300/300 policy transfer; **outputs only the answer letter, no probabilities** |
| [allebee/jevk5](https://github.com/allebee/jevk5) | claims to be an open-weight alternative (Apache-2.0) | 123★ (09-29); details and benchmarks unverified |

### 4.3 Lineage check: is "that RL paper from March 2025" real?

- The paper exists: [arXiv:2503.23303 SalesRLAgent](https://arxiv.org/abs/2503.23303) (2025-03-30, same author as Laya), a PPO-trained model for sales-conversation conversion probability with 85ms inference — **the conceptual lineage checks out**, but it is only an 11KB short paper in a narrow domain.
- The rumored "weights, dataset, and PyPI package were open-sourced back then" **could not be verified**: no corresponding model or dataset can be found on HF, and all candidate PyPI names return 404.

### 4.4 The practical value of traditional approaches in "strict schema + probabilities required" scenarios

| Approach | Probability quality | Labels needed | Latency scale | Fit |
|---|---|---|---|---|
| [ModernBERT](https://huggingface.co/answerdotai/ModernBERT-base) + classification head (Apache-2.0) | ECE ~0.02–0.08 after temperature scaling (**literature values, not independently verified**) | hundreds to thousands per schema | GPU: a few ms to tens of ms | first choice when classes are fixed and labels exist |
| Embedding (e.g. [mmBERT](https://huggingface.co/jhu-clsp/mmBERT-base)) + threshold | similarity **is not a probability**; needs Platt/isotonic fitting | a few dozen suffice | CPU 10–50 ms | medium-precision routing/dedup |
| Zero-shot discriminators (e.g. GLiNER2.5) | no calibration guarantee | 0 | GPU tens of ms | quick prototypes; third-party tests show accuracy clearly below JEV |
| Fine-tuned small generative model outputting JSON | self-reported confidence has **no calibration guarantee** | hundreds to thousands | 100 ms–1 s | only wins when one call must mix "judgment + generation" |

**In one sentence**: when labeled data exists, "fine-tune an encoder classifier" usually beats any decision model on latency, cost, and calibratability; the real value of decision models lies in **training-free repeated judgments + a deterministic interface that generates no text**.

---

## 🧭 5. Selection guide <a id="s5-selection-guide"></a>

> *EN — Use hosted JEV to validate the "typed decision" pattern quickly; go local (L1/L2) when offline or data-residency matters; only Laya is a genuine self-hosted model and must be fine-tuned and temperature-fitted; with labels, a fine-tuned encoder classifier is often cheapest and best-calibrated. Always pin the model version and measure the abstain rate.*

### 5.1 Decisions by scenario

| Your scenario | Recommendation | Rationale and caveats |
|---|---|---|
| Validate whether "typed decisions" fit your business within hours | **Use hosted JEV directly** (Playground + API) | no training needed; first measure accuracy, abstain rate, and calibration on your own 50–200 samples |
| Data cannot leave the country / must be offline / intranet | **L1/L2 options**: SemIf-OpenJev, kev, simple-jev, jevmlx, von, NanoJev | the goal is the "interface paradigm," not official accuracy; be sure to measure **local-vs-cloud agreement** yourself |
| Have labeled data; self-host long-term to control costs | **Laya (fine-tuned + temperature-fitted)**, or **fine-tune a ModernBERT-class encoder** | Laya's base checkpoint is near random guessing (0.362 vs random 0.318); all its value is in fine-tuning |
| A single question with more than 20–50 options | **JEV still leads** (Banking77: 0.870 vs Laya 0.425), or **two-stage "coarse-then-fine" selection** | Laya's options share a fixed token budget; at 77 options each label has only 3–4 tokens |
| Only need yes/no, at large volume | **Baseline with TF-IDF / traditional classifiers first** | Arize measured: JEV 98.3% vs TF-IDF 98.4% — **no statistically significant difference** |
| Chinese and other non-English scenarios | ⚠️ **Must test yourself** | the vendor admits CJK "works but is not equivalent"; independent Chinese-language tests: 64–65.2%, bottom of the strong-model group |
| Need exact numbers / arithmetic / date comparisons | ⚠️ **Do not let the model do it** | the official jaggedness page explicitly lists these as failure modes |
| Real-time interaction (voice, game loops) | usable; measure p95 first | independent measurements p50 314ms / p95 399ms; see the usage patterns of `jev-ultrafast` and `fast-jev-compaction` |

### 5.2 A 7-item checklist before going live

1. **Build baselines**: run three baselines on real samples — "traditional classifier / rules / an off-the-shelf LLM"; don't just look at JEV's own scores.
2. **Measure the abstain rate**: after setting a threshold, count the share that falls into the "insufficient confidence" branch; effective cost ≈ unit price / (1 − abstain rate).
3. **Verify calibration**: compute ECE and reliability curves on your own data; if needed, refit the temperature per bucket of (question type × option count).
4. **Leave fallback paths for failure modes**: do not hand it arithmetic, dates, indirect reasoning, or long-state distraction.
5. **Pin versions**: official aliases drift; pin a versioned ID like `jev-1.13.0` in production.
6. **Data compliance**: confirm whether `state` carries personal information; the vendor is verified not to train on customer data (09-29), but **ZDR is Enterprise-only**.
7. **Check three things first when choosing an open-source option**: the license (see §6 Risk 6), the last commit time, and whether the README has a Limitations section.

---

## ⚠️ 6. Risk checklist <a id="s6-risks"></a>

> *EN — Eight risks, one line each: vendor lock-in, data compliance, irreproducible official numbers, two-sided calibration, abstain-rate cost collapse, open-source licensing gaps, ecosystem inflation, and the "is it just a classifier wrapper" question.*

| # | Risk | In one line | Mitigation |
|---|---|---|---|
| 1 | **Vendor lock-in** | closed-source, no fine-tuning, aliases drift; if the model underperforms, you can only work around it by changing schemas / splitting questions / adding rules | pin versioned IDs; write judgment criteria into `criteria`; keep a local fallback |
| 2 | **Data compliance** | cloud-only, `state` must leave your network; the vendor does not train on customer data (verified 09-29) but **ZDR is Enterprise-only**; mainland-China availability reports are inconsistent with the official terms | confirm DPA/ZDR first for sensitive scenarios; consider local options |
| 3 | **Official numbers not reproducible** | the same company publishes 4 mutually contradictory multiplier bases; reference answers are not human-labeled; the KV-cache mechanism is **purely third-party inference** (zero mention in official docs) | use third-party measurements (5–25×) for capacity planning, not the official homepage |
| 4 | **Two-sided calibration** | overconfident on unknowable tasks (ECE 0.107 = 4.4× the noise floor); the official `confidence` field is worse than `max(probabilities)`; a question and its negation can have probabilities summing to ≠ 1 | compute ECE on your own data; set thresholds with `max(probabilities)` |
| 5 | **Abstain rate eats the cost advantage** | measured 30% abstain → 76× cost advantage becomes 3.2×; ceiling = `1/abstain rate` | measure the abstain rate before launch; give the state enough (adding 3 fields cut abstain by −25pp in tests) |
| 6 | **Open-source licensing gaps** | no license (adoption carries legal risk): `yibie/awesome-jev` (1,950★), `bespokelabsai/nimble` (1,897★), `ekzhang/openjev-sglang`, etc.; NanoJev's HF weights declare no license | check the license field before adopting (`featherless-ai/simple-jev` added Apache-2.0 on 09-28) |
| 7 | **Ecosystem inflation** | repos doubled to 14,028 in 8 days; only ~20–25 actually run; directory sites' star counts are systematically low | trust `gh api`, not directory sites; beware same-day batch submissions |
| 8 | **Route-level skepticism** | "generating no text" is not a moat (strong models with strict JSON schemas likewise have zero hallucination); but black-box probes show it is **not** simply an "independent logits + softmax" wrapper | evaluate value by the **latency × cost × probability quality** combination, not any single point |

---

## 📎 7. Appendix: verification methods, unverified list, and references <a id="s7-appendix"></a>

> *EN — Repo metadata pulled live with `gh api` on 2026-09-21 and refreshed 2026-09-29; official docs/eval pages fetched and parsed directly (raw notes in `research/`). Reproducible with the commands in 7.4.*

### 7.1 Contents of this repository

```
README.md                        # 本报告正文（v1.3）
REPORT-EN.md                     # 全英文版报告
LICENSE                          # CC BY 4.0（报告文本许可）
CITATION.cff                     # 引用格式
CHANGELOG.md                     # 版本更新记录
eval/                            # 评估脚手架：在你自己的样本上实测 JEV/Laya（准确率/弃权率/ECE/抖动）
research/jev-official.md         # 官方事实与 API 契约的原始核实记录（含逐条来源）
research/os-reproductions.md     # 开源复现项目逐个核实记录（含 gh api 原始输出）
research/ecosystem-benchmarks.md # 第三方评测、生态目录、风险分析的原始记录
research/os-decision-models.md   # Laya 与自训开放权重模型的核实记录
research/laya-github-readme.md   # Laya 官方 README 快照（其 benchmark 与局限）
data/open-source-projects.csv    # 项目元数据表（star/许可证/底座模型等，09-29 快照，38 行）
```

### 7.2 Evidence-tag legend

| Tag | Meaning |
|---|---|
| [Official] | from typesafe.ai / docs.typesafe.ai / evals.typesafe.ai and other official sites; fetched directly for this report |
| [Third-party] | published by independent testers, media, or analysts; not rerun for this report |
| [Vendor-reported] | benchmarks published by an open-source repo's own author, with no third-party rerun |
| [Unverified] | only secondhand relays, or mutually contradictory sources, or the original page is unreachable |

### 7.3 Explicitly unverified / questionable items

| Item | Status |
|---|---|
| Full text of the Business Wire funding press release; The Register's original article | fetch failed (403 / unreachable); quoted only via republication |
| TypeSafe's ~$200M valuation | single third-party source |
| Official parameter count, architecture, training data, KV-cache and batching mechanism | not disclosed by the vendor; **any claim of "official KV-cache broadcasting" is third-party inference** |
| The multiplier bases across official pages (193.6×/444.6×/40×–200×/40×–1,000×) | the vendor contradicts itself; the methodology cannot be reproduced |
| "Cleared a 140k waitlist in 36 hours," "trained on 100% synthetic data" | secondhand relays / explicitly marked as rumor |
| `wfzyx/von`'s T value, training-set size, cited arXiv entry | internally contradictory within the repo / the arXiv entry's **existence not verified** |
| `Heman10x-NGU/openJev-verdict-2.0`'s ECE 1.44%; all NanoJev/kev/nimble benchmarks | vendor-reported; no third-party rerun seen |
| APUS "among the earliest worldwide / first in China" | media + vendor framing; cannot be independently verified |
| Ecosystem size (7,330→**14,028** / 503 / 386 / 195 …) | the three counts are inconsistent; cite the source when quoting |
| Speedup multiples of all reproduction projects | **this report ran no actual tests on any repo** |
| ~~Whether the vendor has zero data retention, whether it trains by default~~ | **Verified on the official Models page on 2026-09-29**: does not train on customer requests/responses; ZDR is Enterprise-only |
| `togethercomputer/tev1`, `allebee/jevk5`, `Liuziyu77/Valen` benchmarks and details | appeared after 09-23; **metadata and README only, no tests run** |

### 7.4 How to reproduce this report's data

```bash
# 1) 拉取任意仓库的当日元数据
gh api repos/TheoLeeCJ/SemIf-OpenJev \
  --jq '{full_name,stargazers_count,forks_count,open_issues_count,
         license:.license.spdx_id,created_at,pushed_at,description}'

# 2) 按 star 检索 JEV 生态
gh api "search/repositories?q=jev&sort=stars&per_page=50" \
  --jq '.items[]|{full_name,stargazers_count,license:.license.spdx_id,html_url}'

# 3) 读仓库 README
gh api repos/TheoLeeCJ/SemIf-OpenJev/contents/README.md --jq .content | base64 -d

# 4) 官方文档与评测页
curl -s https://docs.typesafe.ai/models
curl -s https://evals.typesafe.ai/ | sed 's/<[^>]*>/ /g'
```

### 7.5 Main reference links

**Official**
- Homepage <https://typesafe.ai/> · Launch post <https://typesafe.ai/blog/introducing-system-one-models-and-jev> · Team <https://typesafe.ai/team>
- Docs: <https://docs.typesafe.ai/api> · `/models` · `/primitives` · `/concepts/system-one` · Failure modes <https://docs.typesafe.ai/model-jaggedness/jev-1.13>
- Evals page <https://evals.typesafe.ai/> · Agent Skill <https://github.com/typesafe-ai/skills>

**Third-party independent evaluations**
- LangChain <https://www.langchain.com/blog/building-a-harness-with-jev> · Arize <https://arize.com/blog/typesafe-jev-llm-judge/> · Capital & Compute <https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/> · bigbangindex <https://bigbangindex.com/blog/typesafe-jev-cost-latency-analysis>
- Chinese-language: CNR <https://tech.cnr.cn/techph/20260920/t20260920_527819594.shtml> · QbitAI <https://www.qbitai.com/2026/09/492939.html>

**Open-source projects**
- Laya <https://github.com/NandhaKishorM/laya> (weights <https://huggingface.co/convaiinnovations/laya>, MLX port `mizorewww/laya-mlx`)
- SemIf-OpenJev (formerly OpenJev) <https://github.com/TheoLeeCJ/SemIf-OpenJev> · mini-jev <https://github.com/r-ms/mini-jev> · jevlike <https://github.com/vinnylarouge/jevlike> · jevmlx <https://github.com/bnsd55/jevmlx> · NanoJev <https://github.com/TianyuCodings/NanoJev> · kev <https://github.com/jaredpalmer/kev> · nimble <https://github.com/bespokelabsai/nimble> · von <https://github.com/wfzyx/von> · openjev-sglang <https://github.com/ekzhang/openjev-sglang> · simple-jev <https://github.com/featherless-ai/simple-jev> · jev-ultrafast <https://github.com/browser-use/jev-ultrafast> · fast-browser-use <https://github.com/APUS-AI-Lab/fast-browser-use> · tev1 (Together AI) <https://github.com/togethercomputer/tev1> · ollaya <https://github.com/ollaya-dev/ollaya> · Valen <https://github.com/Liuziyu77/Valen>
- Ecosystem directories: <https://jevbest.com/zh/> · <https://madewithjev.com/github-repos> · <https://github.com/logicrw/awesome-jev-projects> · <https://github.com/yibie/awesome-jev>

**Note on comparison charts**: this report deliberately provides no single "who is fastest" conclusion table, because the vendor's own bases contradict each other, third-party tests each use different tasks, and no open-source project's numbers have been independently rerun. For selection decisions, rely on **measurements on your own data**.

<div align="center">

<sub>This report was researched and compiled by an AI research agent; every number is tagged with its source type and verification status · Text under [CC BY 4.0](LICENSE) · Citation format in [CITATION.cff](CITATION.cff)</sub>

<sub>Found an error? [Issues](https://github.com/Chorylee7/JEV/issues) and PRs are welcome</sub>

</div>
