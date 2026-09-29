# JEV Research Report: TypeSafe's System One Decision Model and Its Open-Source Alternatives

> **About this document** — This is the English translation of `README.md` v1.1 (2026-09-29). The original Chinese-English bilingual version lives in [README.md](README.md). Evidence tags: [Official] = official sources · [Third-party] = independent tests/media · [Vendor-reported] = self-reported by repo authors · [Unverified] = no primary source found.

| | |
|---|---|
| Verified | 2026-09-21 (v1.0 initial release); star/license/ecosystem data refreshed on **2026-09-29** (v1.1) — see [CHANGELOG.md](CHANGELOG.md) |
| Sources | Official documentation, official eval page, GitHub API (`gh api` same-day snapshots), independent third-party evaluations, Chinese-language media |
| Evidence tags | [Official] officially published · [Third-party] independent tests/media · [Vendor-reported] self-reported by repo authors · [Unverified] no primary source found |
| License | The text of this report is under [CC BY 4.0](LICENSE); citation format in [CITATION.cff](CITATION.cff) |
| Caveat | The report's main conclusions are based on verification as of 2026-09-21; star/license/ecosystem-size figures are 2026-09-29 snapshots and drift minute-by-minute; **all benchmark numbers are, unless noted, self-reported by project authors or the vendor — this report did not run any of them**. |

---

## Quick Reference Card

| Dimension | Conclusion | Evidence |
|---|---|---|
| What it is | A hosted "decision model": `state` + typed questions → structured answers + probabilities; **it does not generate text** | [Official] |
| Three primitives | `noul` (0–1 yes/no) / `choice` (≤255 single-choice) / `score` (2–10 level ordinal rating) | [Official] |
| Price | $0.042 / million input tokens, output free; a 10k-token state ≈ $0.00042/call | [Official] |
| Latency | Official 70–500 ms; independent measurement p50 314 ms / p95 399 ms | [Third-party] |
| Context | 64k per request; `state` + longest single question ≤ 32k; **text input only** | [Official] |
| Speed claims | Official 193.6× (homepage) and 40×–200× (launch post) are **mutually contradictory**; independent measurements 4.8×–25× | [Official/Third-party] |
| Cost claims | Official 444.6× (only against the most expensive model row); independent measurements 8.6×–580×; the Chinese-language test found only ~2.7× | [Official/Third-party] |
| Accuracy | Official average across four workflows 67.8% (≈ Terra / Sonnet 5 tier); binary gating can reach 100% (LangChain, 500 runs against a human oracle) | [Official/Third-party] |
| Notable weaknesses | Invoice processing 61.8% (8th of 9 models), Chinese customer service 64–65%, 0.78 on 77-class intent, arithmetic/date/indirect reasoning | [Official/Third-party] |
| Abstain rate | A measured 30% abstain rate compresses a 76× cost advantage to **3.2×**; the ceiling is `1/abstain rate` | [Third-party] |
| Probability calibration | Good on knowable tasks (ECE 0.024 ≈ noise floor), overconfident on unknowable tasks (ECE 0.107); **do not use the official `confidence` field — use `max(probabilities)`** | [Third-party] |
| Data policy | Does not train on customer requests/responses; **ZDR is Enterprise-only** | [Official 09-29] |
| Current version | `jev-1.13.0` (verified 09-29, no preview build) | [Official] |
| Open-source pick | **Laya** (Apache-2.0, 28.1k★, 33 ms on a T4, post-finetune 0.766 > JEV 0.727; **degrades noticeably above 20 options**) | [Vendor-reported] |
| Scenarios to avoid | High-cardinality classification, Chinese-heavy workloads, numeric-threshold judgments, logically consistent probabilities, >100 Hz control loops | Synthesis |

---

## TL;DR

> JEV is not a chat model. It is a hosted "System One" decision model from TypeSafe AI (San Francisco, founded 2024, $40M seed led by DCVC, released 2026-09-15). You send a `state` plus typed questions; it returns structured answers with probabilities and never writes free text. Weights are closed; API-only. Official headline claims (193.6× faster / 444.6× cheaper) are contradicted by other numbers on TypeSafe's own pages (40×–200×, 20×–200×, 40×–1000×), and independent tests land between 5×–25× on speed and 8.6×–580× on cost. Open source split into two camps: **interface reproductions** (read option-token logits from a frozen LLM, skip autoregressive decoding) and **genuinely retrained open-weight decision models** (Laya is the standout: Apache-2.0, ModernBERT-class, ~33 ms, post-finetune 0.766 vs JEV's 0.727 on typed-decisions — but it collapses on questions with more than ~20 options).

- **JEV is not a chat model — it is a "decision model"**: input a program state plus several **typed questions**, and one call returns structured verdicts with probabilities; it generates no free text whatsoever. It belongs to TypeSafe AI (San Francisco, founded 2024), released 2026-09-15, with a $40M seed round (led by DCVC) [Third-party + official press release].
- **Only three primitives exist**: `noul` (yes/no questions, returns a 0–1 probability), `choice` (single choice among up to 255 options), `score` (2–10 level ordinal rating). There is **no** ranking / span type, and **no streaming**.
- **Pricing and specs**: $0.042 / million input tokens (output free), rate limits of 250k tokens/second + 1,200 requests/minute, 64k context per request, **text-only input** (no image/audio/video), weights not open-sourced and no per-customer fine-tuning.
- **The official numbers contradict themselves**: the homepage says 193.6× faster / 444.6× cheaper, the launch post says 40×–200×, and the non-public onboarding page says 20×–200× and 40×–1,000×. Third-party independent measurements: speed **4.8×–25×**, cost **8.6×–580×** — nobody reproduced 444.6×.
- **Accuracy is highly task-dependent**: across the four workflows in the official self-test, JEV averages 67.8% (behind GPT-5.6 Sol's 74.1%), and **invoice processing at 61.8% ranks 8th of 9 models** (beating only Haiku 4.5) — this is the hardest evidence that "JEV is not a universal solution," and it comes from the official eval page itself.
- **Failure modes officially disclosed by the vendor**: arithmetic and counting, date comparison, indirect reasoning, large-state distraction, adversarial content, and more — 9 categories in total (the `jaggedness` page); it also admits that **the probabilities of a question and its negation need not sum to 1** (official example: 0.72 + 0.47 = 1.19).
- **The open-source ecosystem splits into two camps** (stars are 2026-09-29 snapshots): ① **interface reproductions** — freeze an existing open model, read only the logits of candidate-answer tokens and apply a restricted softmax, skipping autoregressive decoding (`browser-use/jev-ultrafast` 21.3k★, SemIf-OpenJev 4.5k★, kev 7.7k★, NanoJev 2.4k★, etc.); ② **genuinely retrained with open weights** — Laya (Apache-2.0, **28.1k★**, 4.4k HF likes, three checkpoints, 32.8–39.5 ms per question on a T4) has become the **absolute leader** of this direction and the only open-source option that beats JEV head-on on a public benchmark, but its base checkpoint is **near random guessing** zero-shot, and it degrades noticeably beyond 20 options; since 2026-09-23, Together AI has released the open-weight `tev1` (Qwen3.5-4B LoRA fine-tune that outputs a single answer letter) — the **first established company to enter the field**.
- **Selection conclusion**: treating JEV as a "training-free fast decision layer" is reasonable; but treating the official 200×/400× as a planning premise is risky. Before production, measure at least three things yourself: **accuracy on your task, the abstain rate (a measured 30% abstain compresses a 76× cost advantage to 3.2×), and whether the probabilities are actually calibrated on your data**. For long-term self-hosting, prefer Laya (with fine-tuning and temperature fitting) or a "small model + strict JSON schema" approach, rather than taking any reproduction project's advertised numbers at face value.

**Contents**

1. [What is JEV](#1-what-is-jev)
2. [Official Claims vs Independent Evidence](#2-official-claims-vs-independent-evidence)
3. [The Open-Source Landscape](#3-the-open-source-landscape)
4. [Genuinely Retrained Open-Weight Models](#4-genuinely-retrained-open-weight-models)
5. [Selection Guide](#5-selection-guide)
6. [Risks and Limitations](#6-risks-and-limitations)
7. [Appendix: Verification Methodology, Unverified Items, and References](#7-appendix-verification-methodology-unverified-items-and-references)

---

## 1. What is JEV

> JEV is TypeSafe AI's "System One" model: a hosted, text-in/structured-out decision service, not a generative LLM. Its API is a single endpoint (`POST /v1/systemone`) taking `state` + `questions` and returning typed answers. Only three question primitives exist. It cannot write text, cannot explain itself, has no world knowledge beyond the supplied state, and is English-first. Weights are not published and no paper exists.

### 1.1 One-sentence definition

The official definition of System One is: the model **does not write replies, does not produce code, and does not generate reasoning traces** — it only returns verdicts with probabilities inside the structured schema provided by the caller [Official: <https://docs.typesafe.ai/concepts/system-one>]. It is therefore similar to "using an LLM to output JSON" in **interface shape**; the differences are:

| Dimension | Traditional LLM | JEV (System One) |
|---|---|---|
| Output | Autoregressive token stream | One forward/parallel computation, structured answers directly |
| Explainability | Can generate reasoning | **Generates no explanatory text at all** |
| World knowledge | Has it | **None** — only knows the `state` you pass in |
| Streaming | Supported | **Not supported** (verbatim from the Pydantic AI integration docs: "nothing to stream") |
| Probabilities | You must extract logits yourself | Natively returns `probabilities` / `confidence` |
| Weights | Optionally open | **Closed**, hosted API only |

### 1.2 Company and timeline

| Item | Content | Evidence |
|---|---|---|
| Company | TypeSafe AI, San Francisco (near the Embarcadero), founded 2024, fully in-person five days a week | [Official] <https://typesafe.ai/team> |
| Founders | Diogo Almeida (CEO, ex-OpenAI/Google Brain, co-author of the InstructGPT paper); Erik Gafni (CTO); Sasha Sheng (COO, ex-Meta/FAIR) | [Official] launch post + media |
| Funding | $40M seed round led by DCVC (Business Wire announcement 2026-09-15; the original page returned 403 when fetched, full text **unverified**) | [Official press release] `businesswire.com/news/home/20260915525333/en/` |
| Valuation | Reported at roughly $200M | [Third-party, single source, **unverified**] |
| Release date | Official blog post timestamped **2026-09-15**; some media recorded 9/14 or 9/16 (their reporting dates) | [Official] <https://typesafe.ai/blog/introducing-system-one-models-and-jev> |
| Current version | `jev-1.13.0`; both aliases `jev-latest` / `jev-preview` point to it | [Official] <https://docs.typesafe.ai/models> |
| Official companion artifact | `github.com/typesafe-ai/skills` (Agent Skill, MIT, 1,259★, **created 2026-08-24, before the public beta**) | [GitHub API] |

### 1.3 API contract (field level)

Endpoint: `POST https://api.typesafe.ai/v1/systemone` [Official: <https://docs.typesafe.ai/api>]

The request body has three fields:

```jsonc
{
  "state": "……你的程序状态：一段文本、一个 JSON 对象或文本数组……",
  "model": "jev-latest",
  "questions": {
    "risk_level": { "type": "choice", "options": ["low", "medium", "high"] },
    "is_phishing":  { "type": "noul" },
    "quality":      { "type": "score", "levels": ["terrible", "poor", "ok", "good", "great"] }
  }
}
```

Key design: `questions` is a **map whose keys you name** — the keys are only used to align the request with the response and **are not sent to the model**; all questions on the same `state` are evaluated **in parallel and independently**. In the official wording: "Adding questions barely changes the response time" [Official].

Response body:

```jsonc
{
  "model": "jev-1.13.0",
  "answers": {
    "risk_level": { "choice": "high", "probabilities": {"low":0.02,"medium":0.11,"high":0.87}, "confidence": 0.87 },
    "is_phishing": { "noul": 0.994 },
    "quality":     { "score": 3.4, "legend": ["terrible","poor","ok","good","great"],
                     "probabilities": {"terrible":0.01,"poor":0.06,"ok":0.21,"good":0.42,"great":0.30}, "confidence": 0.42 }
  },
  "usage": { "input_tokens": 412, "output_tokens": 0 }
}
```

**The three primitives (these are officially all of them — there is no fourth)**:

| Primitive | Semantics | Returns | Example use cases (official) |
|---|---|---|---|
| `noul` | Yes/no question | A single 0–1 probability, **no `confidence` field** | Phishing detection, spam, jailbreak detection, churn risk |
| `choice` | Single choice, **up to 255 options** | `choice` + `probabilities` (sums to 1) + `confidence` | Intent classification, routing, tagging |
| `score` | Ordinal rating, **2–10 levels** | `score` (**can fall between levels**, e.g. `1.05`) + `legend` + `probabilities` + `confidence` | Severity, quality, urgency |

> Common misconception: **JEV has no `ranking` or `span` type**; `boolean` is merely an alias for `noul` used by some channels (e.g. Vercel).

### 1.4 Pricing, rate limits, and hard limits [Official: <https://docs.typesafe.ai/models>]

- Price: **$42 / billion input tokens = $0.042 / million**, **output tokens are free** (because no tokens are generated).
- Rate limits: 250,000 tokens/second, 1,200 requests/minute; officially noted as "dynamically adjusted, may change without notice."
- Context: 64k per request, of which `state` + the longest single question ≤ 32k.
- Input modality: **text only** (string / JSON object / array of text). No image, audio, or video.
- Language: English is best; the vendor admits "other languages such as CJK work, but the quality is not equivalent."
- Weights and fine-tuning: **closed**; the vendor explicitly states "all accounts share the same set of weights; no per-customer fine-tuning/LoRA."
- Price sustainability: the vendor itself wrote a rare admission — "**we cannot prove that it is not subsidized**."
- Regional availability: CNR (tech.cnr.cn) reported on 2026-09-20 that "the service is not yet available in mainland China" [Third-party]; however, **no region/export-control clause was found** in the official documentation or terms of service (grep-verified for this report), so this item **remains unconfirmed as far as official statements go**.
- Data policy (**verified 2026-09-29**): the official Models page states "**Jev is not trained on customer requests or responses**"; the DPA, privacy policy, and zero data retention (ZDR) are **Enterprise-only** (<https://docs.typesafe.ai/models>).
- Version status (**verified 2026-09-29**): still `jev-1.13.0`; `jev-preview` and `jev-latest` currently point to the same version, with no preview build; rate limits are still declared as "dynamically adjusted, may change without notice."

### 1.5 The capability ceiling the vendor itself acknowledges

The vendor has a dedicated page, `Jev 1.13 jaggedness` [Official: <https://docs.typesafe.ai/model-jaggedness/jev-1.13>], listing 9 categories of failure modes, several of which matter a lot for engineering decisions:

- **Literal interpretation**: it will not fill in your intent with common sense;
- **Arithmetic and counting**: explicitly unreliable;
- **Date/time comparison**, **multi-hop indirect reasoning**: weak;
- **Large states stuffed with irrelevant details**: it gets distracted;
- **Adversarial content**, **instructions contradicting criteria**: it gets led astray;
- **Structural invariants**: it does not guarantee constraints like "totals must be conserved";
- **Generative tasks**: simply not supported;
- **Probabilities are not logically consistent probabilities**: the probabilities of a question and its negation **need not sum to 1** (official example: 0.72 + 0.47 = 1.19); the numeric calibration of `score` is very weak and exact values **cannot** be recovered by interpolation.

### 1.6 Interesting official demos

- **Doom**: the official blog claims it drives the game at about **10 queries/second** for about **$7/hour**; the input is **textual structured game state, not pixels**, and the vendor self-deprecates that "a non-AI Doom bot would play better."
- **Wikiracing**: each step makes a `choice` among hundreds to thousands of links; when the link count exceeds 255, a "two-stage score-then-choose" approach works around the cap.

---

## 2. Official Claims vs Independent Evidence

> TypeSafe's marketing numbers vary by page (193.6×/444.6× on the homepage, 40×–200× in the launch post, 20×–200× and 40×–1000× in the gated onboarding page). Eight independent tests published between 09-15 and 09-19 land at 4.8×–25× on latency and 8.6×–580× on cost. Accuracy is highly workflow-dependent: JEV ranks 8th of 9 on the invoice-processing workflow in TypeSafe's *own* eval page. The two most useful independent findings are that a 30% abstain rate collapses the cost advantage from 76× to 3.2×, and that on tasks where the model cannot know the answer it is severely overconfident (ECE 0.107 vs a 0.024 noise floor).

### 2.1 Speed and cost: the vendor alone has four versions

| Source | Speed multiplier | Cost multiplier | Type |
|---|---|---|---|
| TypeSafe homepage | 193.6× | 444.6× | [Official] |
| TypeSafe launch post | 40×–200× | Not published | [Official] |
| TypeSafe early-access onboarding (login required) | 20×–200× | **40×–1,000×** | [Official] |
| Hand-computed from the official evals table | ~25×–95× | 76×–440× | [Third-party calculation] |
| Every | ~25× | ~580× | [Independent third-party] |
| Near Here | — | 8.6× (vs Mistral Small 4) / 58× (vs Gemini Flash-Lite) | [Independent third-party] |
| gemanor | 4.8×–5.7× latency | 45× / 274× | [Independent third-party] |
| 4esv/jev-eval | 5× | 41×–50× | [Independent third-party] |
| Guixingren (Chinese-language test) | 0.73–0.75 s vs DeepSeek V4 Flash 5.58 s | 50 questions for $0.002 | [Independent third-party] |
| Capital & Compute | p50 314 ms / p95 399 ms (reproduces the official 70–500 ms range) | $0.0238/thousand calls | [Independent third-party] |

**How to read this table**: 444.6× was obtained by "comparing only against the most expensive Claude Opus 5 row"; the official homepage and the launch post differ by nearly an order of magnitude; the median of third-party measurements falls at **5×–25× speed and 10×–60× cost**. This does not mean JEV is not fast — a measured 314 ms p50 genuinely exists — it means **"200×/400×" cannot be used as an input to capacity planning**.

### 2.2 Accuracy: the most glaring cell on the official eval page

The official evals page [Official: <https://evals.typesafe.ai/>] compares four workflows across 9 models (this report parsed the page's HTML directly — not a media retelling):

| Workflow | JEV | Best on that workflow | JEV rank | JEV cost rank |
|---|---|---|---|---|
| Security Incidents | 61.7% ($0.0001, 0.3 s) | Opus 5 workflow 66.2% | 3rd | **Lowest** |
| **Invoice Processing** | **61.8%** ($0.0011, 0.5 s) | Sol workflow 79.1% | **8th (beats only Haiku 4.5)** | 2nd |
| Customer Service | 76.0% ($0.0001, 0.4 s) | Sol workflow 78.3% | 4th | **Lowest** |
| Agent Trace Observability | 71.6% ($0.0003, 0.5 s) | Sol workflow 76.6% | Tied 6th | **Lowest** |
| **Average of the four** | **67.8%** | Sol workflow 74.1% | — | **Lowest** |

On the invoice-processing cell, JEV loses to 8 models, including the cheapest model Luna (67.8%) and DeepSeek V4 Flash (69.8%).

**Third-party accuracy comparisons (excerpt)**:

| Test | Task | JEV | Baseline | Conclusion |
|---|---|---|---|---|
| LangChain (09-20) | 500 repeated binary verdicts against a human oracle | **100% (500/500)** | Terra 99.8% / Luna 96.4% / Claude Sonnet 4.6 80.0% | **JEV first, lowest variance**; total cost $0.34 vs Claude $28.17 |
| Arize AI | 18,514 emails with real labels | 98.3% | **TF-IDF classifier 98.4%** | Statistically a **tie** (the only large independent test with ground truth) |
| gemanor | 1,080 Python rule reviews | 98.0% | Gemini / Fable 5.1 both 100% | 2 points behind |
| 4esv | 77-class intent | 0.78 | Terra 0.85 | 7 points behind |
| Guixingren (Chinese) | 50 Chinese customer-service items (scored only if all 4 parts are correct) | **64–65.2%** | The best in the cheap group beat it by 1.2 points; in the strong-model group MiniMax M3 was 10.8 points higher | **Second in the cheap group, last in the strong group** |
| RINNECODER | 3D city driving (self-test) | **0/12 complete tasks** | — | All 522 steering decisions chose "go straight" |
| NanoJev (project authors) | ViZDoom Basic | 56/128 (≈ un-fine-tuned Qwen3-0.6B) | NanoJev 128/128 | No gain over the bare base model on this game task |

### 2.3 Methodological caveats the vendor discloses itself

The official evals page states these "nuances" itself; each is worth remembering:

- The evals were run **"on our own team's laptops, on the US West Coast"**;
- The workflows were built by the **internal capabilities team** and "may be biased";
- **The reference answers are not human-labeled — they are the average of GPT-6 Astra and Claude Fable 5.1 outputs** — "this biases the results toward OpenAI and Anthropic models";
- The advertised "**0% type errors**" is not a measurement — the official wording is "Our number is not empirical";
- The side-by-side demo uses very short states, which **"makes our model look better."**

### 2.4 The two independent findings most worth remembering

1. **The abstain rate is a cost killer.** A third party measured on a real queue that **30% of calls fail to return a usable confidence in time**; under the effective-cost formula `blended = M/(1+aM)`, the cost advantage collapses from 76× to **3.2×**. The ceiling on the cost advantage is `1/abstain rate`, regardless of how cheap JEV's unit price is.
2. **Calibration is two-sided.** On **knowable tasks** JEV is well calibrated (OpenBookQA ECE 0.024 = noise floor; the lowest variance across LangChain's 500 repeated verdicts); but on **unknowable tasks** it is severely overconfident (a self-built synthetic-ticket set gives ECE **0.107 = 4.4× the noise floor**, and the `score` sub-task's temperature parameter needs refitting to **3.40**). Moreover, the official `confidence` field **never outperformed `max(probabilities)`** in independent testing.

### 2.5 The 9 officially disclosed failure modes (engineering must provide fallback paths)

Literal interpretation · arithmetic and counting · date/time comparison · indirect reasoning · large states with irrelevant details · adversarial content · instructions contradicting criteria · structural invariants · generative tasks. Two more are counterintuitive but important: **the probabilities of a question and its negation need not sum to 1**; and **`score` cannot be interpolated back into exact numeric values**.

---

## 3. The Open-Source Landscape

> Within five days of launch, GitHub accumulated thousands of JEV-related repos. Filtering for projects that actually explain the mechanism leaves ~20–25 real reproductions out of ~4,100 created-after-09-01 repos; the rest are skills, wrappers, awesome-lists and same-day bulk submissions. The dominant technique is identical everywhere: freeze an open LLM, read the logits of candidate answer tokens at a single position, apply a restricted softmax, and skip autoregressive decoding. Notably, the projects that measured their own speedup report **4×–5.2×**, not 200× — because a frozen 4B model still has to prefill the state. Almost none of them claim calibrated probabilities; several explicitly disclaim it.

### 3.1 The four layers (classify first, or the numbers are not comparable)

| Layer | Definition | Representatives | Local inference? | Self-trained weights? |
|---|---|---|---|---|
| L0 Client applications | Write your own prompt/schema; still call the cloud JEV API | `browser-use/jev-ultrafast`, `tamaratran/fast-jev-compaction`, `perixtar/jev-e2e`, `typesafe-ai/skills` | ✗ | ✗ |
| L1 Interface reproductions | Freeze an existing open model, **read only the option-token logits** + restricted softmax, skip autoregressive decoding | `TheoLeeCJ/SemIf-OpenJev`, `r-ms/mini-jev`, `bnsd55/jevmlx`, `featherless-ai/simple-jev`, `ekzhang/openjev-sglang` | ✓ | ✗ (weights frozen) |
| L2 Reproduction + self-trained head/adapter | Train your own scoring head or LoRA on top of L1 | `vinnylarouge/jevlike`, `TianyuCodings/NanoJev`, `jaredpalmer/kev`, `bespokelabsai/nimble`, `wfzyx/von`, `Mapika/decider`, `togethercomputer/tev1` | ✓ | ✓ (partial/adapter) |
| L3 Self-built decision model | Train your own model, publish weights and data | **Laya** (see Chapter 4) | ✓ | ✓ |

**This distinction matters**: every "speedup multiplier" in L1/L2 is built on **"skipping decoding"**, while **the prefill cost of the state cannot be avoided**. So their measured speedups are **single-digit multiples**, not 200×.

### 3.2 Core project comparison table (stars are a 2026-09-29 GitHub API snapshot)

| Repo | ★ | License | Base model | Hardware | HTTP service | Claims calibration |
|---|---:|---|---|---|---|---|
| [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) | **28,058** | Apache-2.0 | **Self-built** ModernBERT family (≈421M) | CPU / CUDA | SDK | ✓ (ECE 0.081 after temperature fitting) |
| [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | 21,264 | MIT | Cloud JEV + `inception/mercury-2.5` | Any | — | — |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | 7,749 | Apache-2.0 | Qwen3.5-0.8B/4B/9B + LoRA | CUDA / Apple Silicon | ✓ | **Explicitly disclaims** |
| [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | 7,167 | MIT | Cloud `jev-latest` | Any | — | **Explicitly disclaims** |
| [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) | 6,604 | Apache-2.0 | MLX port of Laya (not a JEV reproduction) | Apple Silicon | — | — |
| [TheoLeeCJ/SemIf-OpenJev](https://github.com/TheoLeeCJ/SemIf-OpenJev) (originally OpenJev→SemIf, renamed a second time on 09-22) | 4,547 | MIT | Qwen3.5-4B / MiniCPM5-2B / Qwen3-0.6B (frozen) | CUDA / Apple MLX / WebGPU | demo | Requires users to calibrate themselves |
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | 2,419 | MIT | Qwen3-0.6B + self-trained decision heads | CUDA / CPU | ✓ | — |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | 1,897 | **None** | Qwen3.5-9B + LoRA | CUDA | ✓ | — |
| [vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike) | 1,332 | MIT | From-scratch byte-encoder / frozen Qwen2.5-0.5B | CPU / MPS / CUDA | — | No claim |
| [ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya) | 916 | Apache-2.0 | Laya / decider / NLI / GLiClass served locally ("the Ollama of decision models") | CPU / GPU | ✓ | — |
| [Mapika/decider](https://github.com/Mapika/decider) | 887 | Apache-2.0 | Qwen3.5-2B/0.8B/35B-A3B + vision variant | CUDA | — | ✓ (calibration-aware RL) |
| [wfzyx/von](https://github.com/wfzyx/von) | 763 | Apache-2.0 | ModernBERT-Large 395M | CPU / CUDA | ✓ | ✓ (T=1.1692) |
| [featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev) | 567 | **Apache-2.0** (added 09-28; none before) | Qwen3.5-0.8B / Gemma 4 26B-A4B / Laya | CPU / CUDA | ✓ | **Explicitly disclaims** |
| [razorback16/openjev](https://github.com/razorback16/openjev) | 515 | Apache-2.0 | DiffusionGemma 26B-A4B | CUDA | — | — |
| [Liuziyu77/Valen](https://github.com/Liuziyu77/Valen) | 474 | Apache-2.0 | Self-trained multimodal Jev-like training framework (incl. vision) | CUDA | — | — |
| [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) | 332 | **None** | Qwen3.6-35B-A3B (SGLang) | B200-class | ✓ | — |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | 291 | NOASSERTION | ModernBERT-base 151M + dual confidence heads | CPU / WebGPU | — | ✓ (ECE 1.44%, self-tested receipt) |
| [APUS-AI-Lab/fast-browser-use](https://github.com/APUS-AI-Lab/fast-browser-use) | 178 | MIT | Qwen3.5-9B / 35B-A3B | GPU / GPU-less Mac/PC | ✓ | — |
| [togethercomputer/tev1](https://github.com/togethercomputer/tev1) | 165 | MIT | **Qwen3.5-4B LoRA fine-tune (Together AI)** | CUDA | — | — |
| [allebee/jevk5](https://github.com/allebee/jevk5) | 123 | Apache-2.0 | Open-weight alternative | CUDA | — | — |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | 69 | MIT | Qwen2.5-7B/3B/1.5B-4bit (MLX) | Apple Silicon / CPU | ✓ | **Explicitly disclaims** |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | 58 | MIT | Qwen3-4B-Instruct-2507 (frozen) | CUDA / MPS | ✓ | **Explicitly disclaims** ("not calibrated probabilities") |
| [ikermoel/open-alternative-jev](https://github.com/ikermoel/open-alternative-jev) | 57 | Apache-2.0 | Any open-weights model | CUDA | — | ✓ (MMLU ECE 5.4%→2.1%) |

**Not listed but worth knowing**: [`logan-markewich/jeff`](https://github.com/logan-markewich/jeff) (261★, applies GLiNER to decisions), [`fstandhartinger/jevbench`](https://github.com/fstandhartinger/jevbench) (175★, benchmarking tool), `dzhng/jevgrep` (1,574★, a code-search CLI — an application, not a decision model), `Heman10x-NGU/Verdict-open-jev`, `deepanwadhwa/OpenDecision` (57★, NLI route), `Micha0827/snapjudge` (14★, MLX), `NullPo-jp/PocketJev` (2★, Swift/iOS).

### 3.3 Projects worth examining one by one

**`TheoLeeCJ/SemIf-OpenJev` (4,547★, MIT) — the most representative, and the most restrained, project in the ecosystem**
- Originally named OpenJev; the README's first line was once changed to `# SemIf (formerly OpenJev)`, and on **09-22 it was renamed again to `SemIf-OpenJev`** (old links all redirect; APUS's README still references the earliest `TheoLeeCJ/openjev`, which is stale).
- Two modes: **direct** (read the option-token logits directly) and **shared** (prefill the state once, reuse the KV across parallel questions).
- **Its self-measured speedup is only 5.21×** (1.023 s vs 5.332 s, RTX 3090), and it explicitly states "Jev's numbers are read from TypeSafe's public records — **we did not run the real Jev endpoint**"; what it reproduces is the 102-line interface paradigm, not the official 711-line full implementation.
- Supports CUDA / Apple MLX / **WebGPU (runs in the browser)** — one of the few options that can be demoed purely in a browser.

**`r-ms/mini-jev` (58★) — the most rigorous evidence chain, with the most unfavorable conclusion**
- Has a `PREREG.md` (with v1.1–v1.3 amendments); 27,900 run records with logits are public on HuggingFace.
- Conclusion: **"reading letter logits" and "grammar-constrained JSON generation" are comparable in accuracy (Δ −0.22pp)**, and the speedup is only **4× (short text) / 1.4–2.4× (2048 tokens + shared prefix)**.
- Explicitly states: "these are normalized candidate scores, **not calibrated probabilities**."

**`TianyuCodings/NanoJev` (2,419★) — the only one that fully publishes self-trained weights + data, and keeps the row that embarrasses it**
- Qwen3-0.6B + self-trained decision heads; on ViZDoom Basic **128/128 vs JEV's 56/128**; but on the Maze task **4/10, losing to JEV's 7/10** — the README keeps that row undeleted.

**`jaredpalmer/kev` (7,749★, Apache-2.0) — the most honest about its limitations**
- Qwen3.5-0.8B/4B/9B + LoRA (rank 16); on typed-decisions JEV accuracy is 0.857 vs kev-9B's 0.812, but **Brier is better (0.211 vs 0.291)** — i.e., JEV's **distribution quality** is better.
- Self-disclosed: on Apple Silicon, due to the lack of a fast DeltaNet kernel, it is **4–7× slower than the previous-generation model**.

**`APUS-AI-Lab/fast-browser-use` (178★, MIT) — a case where media coverage and actual influence still diverge**
- CNR, Science and Technology Daily, Sina and others reported it as "among the world's earliest / among China's first cross-platform open-source Jev reproductions," but as of 09-29 it has only **178★**, far below community projects of the same period; the README also lacks an independent Limitations section.
- Technically it is a standard L1: it numbers the visible, interactive elements on a page into a candidate action set, scored by a local Qwen3.5-9B in a single forward pass, about 4 scoring passes per task; only `TYPE_TEXT`-type actions actually generate tokens.

**`bespokelabsai/nimble` (1,897★) — currently the only one that dares to place its base model side by side with JEV**
- On 324 held-out items: **Nimble-9B 90.1%**, its base (Qwen3.5-9B) 66.4%, **JEV 1.13.0 93.2%** — i.e., "a fine-tuned small model can catch up but has not surpassed."

**`togethercomputer/tev1` (165★, MIT) — the first established company to enter, but with a different paradigm**
- Together AI's official repo: Qwen3.5-4B fine-tuned with LoRA SFT (37,840 training samples + 4,568 validation), **taking 2–24 options as input and outputting a single answer letter** — it is a "constrained-generation classifier" that **does not output per-option probabilities**, a different paradigm from JEV's "probabilities first."
- Weights are public (`togethercomputer/Tev1-4B-experimental`), with a data recipe and training examples (the official blog calls it "train your own classifier for $17"); self-reported 880/1,000 primary decisions and 300/300 policy-transfer decisions.

**`ikermoel/open-alternative-jev` (57★) — the most honest benchmark in the ecosystem**
- The only project that publicly admitted its own miscalculation and kept the error analysis ("The correction that made this README honest").

**On the difference between APUS's `fast-browser-use` and `browser-use/jev-ultrafast`**: the latter (21.3k★) is an **L0 client** that still calls cloud JEV — it merely compresses browser-use's per-step interaction into "two heads, operation + target, one round trip"; it represents **usage optimization**, not a local replacement.

### 3.4 The gap between these reproductions and the official claims comes mainly from three engineering facts

1. **Prefill cannot be avoided**: skipping decoding only saves generation itself; the longer the state, the smaller the fraction saved (mini-jev: 4× on short text → 1.4–2.4× at 2048 tokens).
2. **No dedicated hardware/serving stack**: the official offering is a hosted service at 70–500 ms (independent measurement p50 314 ms falls inside that range); the community runs single RTX 3090 cards / M-series Macs.
3. **Different inference frameworks**: `ekzhang/openjev-sglang` uses SGLang's radix caching for prefill-only inference — currently one of the most "engineering-grade" routes.

### 3.5 Ecosystem noise warnings (mind these when citing)

- GitHub `q=jev` repos numbered about **7,330** on 09-21, and **reached 14,028 on 09-29 (+91% in 8 days)** [GitHub API]; `topic:jev` and `topic:system-one` each had at least 55 (as of the 09-21 count); **there are now over 20 awesome-jev-style directories** (new since 09-22: `kydlikebtc/awesome-jev` — self-reported 1,207 resources indexed, 582★ — and a Chinese translation `yibie/jev-engineering-zh` at 128★, among others).
- The reproductions that actually explain the mechanism and can run number about **20–25**; someone on Reddit claims to have **manually filtered 20 out of 287 repos** (the original post for this claim is **unverified**).
- The single most quotable community warning comes from the author of `yibie/awesome-jev` himself: **"Be extra wary of projects submitted in bulk on the same day — quantity is not quality."**
- The ecosystem directory sites (`jevbest.com` with 503 entries, `madewithjev.com`, both as of the 09-21 count) **all explicitly state they are unaffiliated with TypeSafe**; their star snapshots are **systematically low** (e.g., jev-ultrafast recorded as 9,291 when the actual count that day was 12,585). When citing ecosystem size, note which counting method is used, because the three methods disagree with each other.

---

## 4. Genuinely Retrained Open-Weight Models

> Laya (Apache-2.0, **28k★**, three checkpoints on HuggingFace, ~421M ModernBERT-class encoder with decision heads) has become the dominant open-weight decision model: it beats JEV's published numbers on typed-decisions (0.766 vs 0.727) and is ~7.8× faster, but every Laya accuracy figure is currently self-reported, its base checkpoints are near chance zero-shot, and it degrades badly above ~20 options. On 2026-09-23 Together AI released **tev1** (Qwen3.5-4B LoRA, returns a single answer letter rather than option probabilities) — the first established company to ship an open-weight JEV-style model. The rest of the "retrained" camp are LoRA/head adaptations of frozen models (L2). The 2025-03 RL non-autoregressive lineage is real (arXiv:2503.23303) but the promised weights/dataset cannot be found.

### 4.1 Laya: the ecosystem's only "self-trained + open-weight" decision-model family (as of 09-29 already the ecosystem's #1 by stars)

| Item | Content |
|---|---|
| Repo | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya), **28,058★ / 2,446 forks** (09-29 snapshot; on 09-21 it was 5,060★ / 454 forks, +454% in 8 days), Apache-2.0, created 2026-09-18 |
| Author | Nandakishor Mukkunnoth (Convai Innovations, independent researcher; there is **no** convaiinnovations organization on GitHub — the main repo lives under a personal account) |
| Weights | [convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya) (ModernBERT-large + decision heads, **421M**, English, HF likes **4,395** — 1,204 on 09-21), [laya-multilingual](https://huggingface.co/convaiinnovations/laya-multilingual) (mmBERT-base, 322M, 100+ languages, 323 likes), [laya-typed-decisions](https://huggingface.co/convaiinnovations/laya-typed-decisions) (fine-tuned variant, 130 likes) |
| Distribution channels | PyPI `laya` 0.3.4, [HF Space online demo](https://huggingface.co/spaces/convaiinnovations/laya-demo), third-party MLX port [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) (**6,604★**, 1,938★ on 09-21; 7.4–13.4 ms/question on an M3 Max), local-serving tool [ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya) (916★, wraps Laya/decider/NLI/GLiClass into a TypeSafe-compatible API) |
| Architecture | Bidirectional encoder + scores each option at the `[MASK]` position, then softmax; **one forward pass answers all questions**; the answer space is defined at request time |
| Training | Self-described **RLCD** (strictly proper scoring rules as reward, GRPO-style policy gradients), with a Kaggle 2×T4 fine-tuning notebook; **training data not publicly released** (only disclosed that AG News/BoolQ are in the training mix) |
| Documentation | No standalone paper; technical docs = model card + `BENCHMARKS.md` |

**The shift in ecosystem position**: on 09-21 Laya was "the only self-built open-weight option"; 8 days later it is the ecosystem's #1 by stars (28k, surpassing the L0 client `jev-ultrafast` at 21.3k), and since 09-23 Together AI has released the open-weight `tev1` (see 3.3 and 4.2) — **"company-grade open-source alternatives" have begun to appear**, and the competitive landscape of this track is changing fast.

**Vendor-reported benchmark (T4, against JEV's officially published numbers)**:

| Metric | JEV 1.13.0 (published numbers) | Laya (routed) | Notes |
|---|---|---|---|
| typed-decisions (2,000 decisions) | 0.727 | **0.766** | This checkpoint was fine-tuned on the training split of the same benchmark |
| AG News (4 labels) | 0.910 | **0.950** | In the training mix |
| DAIR Emotion (6 labels) | 0.480 | **0.595** | Held-out; JEV assigns the true label zero probability on **16% of samples** |
| Banking77 (>20 options) | **0.870** | 0.425 | **JEV pulls ahead**, because Laya's options share a fixed token budget |
| ECE (lower is better) | 0.246 | **0.081** | Laya requires temperature fitting first; **its out-of-the-box raw ECE is 0.213, actually worse than JEV** |
| p50 latency (single question) | 236–276 ms | **32.8 ms** | ~7.8× |
| License | Closed API | **Apache-2.0** | — |

**Credibility assessment (important)**: the numbers on the JEV side have independent provenance ([AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and others measured JEV at AG News 0.910 / Banking77 0.870 / DAIR 0.480 / p50 236–256 ms), but **all of Laya's accuracy figures are currently vendor-reported only; no high-visibility independent retest has been seen yet**.

**Limitations Laya itself acknowledges (more honest than the ecosystem average)**:
- **The base checkpoint is near random zero-shot**: 0.362 on typed-decisions (majority-class baseline 0.461, random 0.318); **0.766 comes entirely from fine-tuning** — it is "a fast base well suited for fine-tuning," not an out-of-the-box decision engine.
- **Degrades beyond 20 options**: at 77 options each label gets only 3–4 tokens (`head_max_len` defaults to 192/256), and Banking77 drops to 0.425; the authors recommend raising the budget or doing two-stage hierarchical selection.
- **The `score` primitive is the weakest**: 0.372 on SST-5.
- **Overconfident out of the box**, and `laya-multilingual` **ships with no fitted temperature parameter at all** — you must fit it yourself before use.
- **Multilingual cannot rely on a single checkpoint**: the English checkpoint scores macro 0.227 across 51 languages with macro ECE as high as 0.733, and **gives Khmer a score of 0.000 at 95.2% confidence** — hence the need to "route to different checkpoints," and switching to a model that is not preloaded triggers a 7–10 second reload.
- **Soft-distribution quality still trails JEV**: on typed-decisions the argmax is higher (0.766 vs 0.727), but the soft-distribution accuracy is lower (0.471 vs 0.580).

### 4.2 The L2 layer: self-trained head / LoRA approaches (not from-scratch models)

| Project | What was self-trained | Position relative to JEV |
|---|---|---|
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | Qwen3-0.6B + decision heads, **weights and data fully public** | ViZDoom 128/128 vs 56/128; Maze 4/10 vs 7/10 (self-disclosed deficit) |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | Qwen3.5 in three sizes + LoRA rank 16 | Accuracy 0.812 vs JEV 0.857, **but Brier 0.291 loses to JEV's 0.211** |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | Qwen3.5-9B + LoRA (answer token only) | 324 held-out items: Nimble-9B 90.1%, base 66.4%, **JEV 93.2%** |
| [wfzyx/von](https://github.com/wfzyx/von) | ModernBERT-Large 395M + RLCD post-training | Self-reported T=1.1692; two internal numbers in the README contradict each other |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | ModernBERT-base 151M + dual confidence heads | Self-reported ECE 1.44% (project-side test receipt only) |
| [Mapika/decider](https://github.com/Mapika/decider) | Includes calibration-aware RL | No verified independent rerun |
| [togethercomputer/tev1](https://github.com/togethercomputer/tev1) | Qwen3.5-4B LoRA SFT (37,840 samples), **official Together AI** | Self-reported 880/1,000 primary decisions, 300/300 policy transfer; **outputs only an answer letter, no option probabilities** — a different paradigm from JEV |
| [allebee/jevk5](https://github.com/allebee/jevk5) | Self-described open-weight alternative (Apache-2.0) | 123★ (09-29); details and benchmarks unverified |

These approaches are worth consulting, but none has a third-party rerun, and their bases and tasks differ — **they cannot be compared side by side**.

### 4.3 Lineage check: is the "March 2025 RL non-autoregressive decision paper" real?

- The paper exists: [arXiv:2503.23303 SalesRLAgent](https://arxiv.org/abs/2503.23303) (2025-03-30, same author as Laya), using PPO to train a conversion-probability model for sales dialogue, 85 ms inference, non-autoregressive probability estimation — **the conceptual lineage is genuine**, but it is only an 11 KB short paper in a narrow domain.
- The rumor that "weights, dataset, and a PyPI package were open-sourced back then" **could not be verified**: no corresponding model or dataset can be found on HuggingFace, and all three candidate PyPI names return 404. (The later [arXiv:2510.01237](https://arxiv.org/abs/2510.01237) is a different topic — LLM confidence routing and hallucination mitigation.)

### 4.4 The practical value of traditional approaches in "strict schema + probabilities required" scenarios

| Approach | Probability quality | Labels needed | Latency scale | Applicability |
|---|---|---|---|---|
| [ModernBERT](https://huggingface.co/answerdotai/ModernBERT-base) + classification head (Apache-2.0) | ECE ~0.02–0.08 after temperature scaling (**literature rule-of-thumb, not independently verified**) | Hundreds–thousands per schema | Single to tens of ms on GPU | First choice when classes are fixed, labels exist, and stability and low cost matter |
| Embeddings (e.g. [mmBERT](https://huggingface.co/jhu-clsp/mmBERT-base)) + threshold | Similarity **is not a probability**; needs Platt/isotonic fitting | Dozens suffice | 10–50 ms on CPU | Medium-precision routing/dedup |
| Zero-shot classification (e.g. GLiNER2.5) | No calibration guarantee | 0 | Tens of ms on GPU | Rapid prototyping; third-party measurements show accuracy clearly below JEV |
| Fine-tuned small generative model outputting JSON | Self-reported confidence with **no calibration guarantee** | Hundreds–thousands | 100 ms–1 s | Only advantageous when a single call must mix "judgment + generation" |

**One-line conclusion**: if you have labeled data, "fine-tune an encoder classifier" usually beats any decision model on latency, cost, and calibratability; the real value of decision models is **training-free repeated judgments + a deterministic interface that does not generate text**.

---

## 5. Selection Guide

> Use hosted JEV when you want to validate the "typed decision" pattern quickly and your data may leave your network. Go local (SemIf / kev / jevmlx / simple-jev / von) when offline or data-residency matters, but measure the accuracy gap yourself. Only Laya is a genuine self-hosted *model*, and it must be fine-tuned and temperature-fitted to be useful. If you have labels, a fine-tuned encoder classifier is often the cheapest and best-calibrated option. Always pin the model version, always measure the abstain rate, and never plan capacity on the advertised speedup.

### 5.1 Decide by scenario

| Your scenario | Recommendation | Rationale and caveats |
|---|---|---|
| Want to validate within hours whether "typed decisions" fit your business | **Use cloud JEV directly** (Playground + API) | Training-free, low monthly cost; first measure accuracy, abstain rate, and calibration on 50–200 of your own samples |
| Data cannot leave the country / must be offline / intranet deployment | **L1/L2 options**: SemIf, kev, simple-jev, jevmlx, von, NanoJev | The goal is the "interface paradigm," not official accuracy; be sure to measure the **local-vs-cloud agreement rate** yourself |
| Have labeled data, want long-term self-hosting with cost control | **Laya (fine-tune + temperature fitting)**, or a **fine-tuned ModernBERT-class encoder** | Laya's base checkpoint is near random guessing on typed-decisions (0.362 vs random 0.318) — all its value lies in fine-tuning; for RAG/classification tasks a traditional classifier is often already sufficient |
| More than 20–50 options per question | **JEV still has the edge** (Banking77: JEV 0.870 vs Laya 0.425), or switch to a **two-stage "coarse-then-fine" selection** | Laya's options share a fixed token budget (`head_max_len`); at 77 options each label gets only 3–4 tokens and accuracy collapses |
| Only need "yes/no", at large volume | **Start with a TF-IDF / traditional-classifier baseline** | Arize measured 18,514 real-labeled emails: JEV 98.3% vs TF-IDF 98.4% — **no statistical difference** |
| Chinese or other non-English scenarios | ⚠️ **You must test it yourself** | The vendor admits CJK "works but is not equivalent"; independent Chinese-language measurement: 64–65.2%, last in the strong-model group |
| Need exact numbers / arithmetic / date comparison | ⚠️ **Do not let the model do it** | The official jaggedness page lists these as explicit failure modes |
| Real-time interaction (voice, game loops) | Usable, but measure p95 first | Independent measurement p50 314 ms / p95 399 ms; `fast-jev-compaction` and `jev-ultrafast` are reference usages |

### 5.2 Pre-launch checklist: 7 items

1. **Build baselines**: run three baselines on your real samples — "traditional classifier / rules / off-the-shelf LLM" — and don't look only at JEV's own scores.
2. **Measure the abstain rate**: after setting a threshold, count how many requests fall into the "insufficient confidence" branch; effective cost ≈ unit price / (1 − abstain rate).
3. **Verify calibration**: compute ECE and reliability curves on your data; if necessary, refit temperature parameters bucketed by (question type × option count).
4. **Leave fallback paths for the failure modes**: do not hand it arithmetic, dates, indirect reasoning, or long-state distraction.
5. **Pin the version**: official aliases drift; pin a versioned ID like `jev-1.13.0` in production.
6. **Data compliance**: confirm whether `state` carries personal information; the vendor verified on 09-29 that it **does not train on customer requests/responses**, but zero data retention (ZDR) is **Enterprise-only** — non-Enterprise users must evaluate this themselves.
7. **When choosing an open-source option, check three things first**: the license (see 6.6), the recency of the last commit, and whether the README has a Limitations section.

---

## 6. Risks and Limitations

> The main risks are: (1) official throughput/cost multipliers are not reproducible and vary by a factor of ~10 across the vendor's own pages; (2) abstention silently destroys the cost advantage; (3) calibration is task-dependent and the `confidence` field is worse than `max(probability)`; (4) closed weights with no per-customer fine-tuning means you cannot fix systematic errors except by prompt/schema engineering; (5) the open-source side has a real licensing gap (many repos have no license at all) and routinely mislabels itself as "JEV"; (6) the ecosystem is inflated by same-day bulk submissions — volume is not quality.

### 6.1 Vendor and architecture lock-in

- Weights are not public, there is no fine-tuning interface, and no local deployment path: where the model says no, **you can only work around it by restructuring the state, splitting questions, or adding rules — you cannot fix it by training**.
- The aliases `jev-latest` / `jev-preview` will point to new versions; production behavior can change without your knowledge → **you must pin a version ID**.
- The official documentation contains **no** low-level explanation of KV-cache, batch size, or the concurrency model (all official docs were grepped for this report — zero hits); the claim that "the official service supports KV-cache broadcast" **appears only in the descriptions of third-party reproduction projects** and is inference, not fact.

### 6.2 Data compliance and region

- CNR reported that the service is "not yet available in mainland China" [Third-party]; yet **no region-restriction clause was found** in the official documentation or terms (grep-verified). Confirm with the vendor before deployment.
- The service is **purely cloud-based**, so `state` necessarily leaves your network. The official Models page of 2026-09-29 states: "**Jev is not trained on customer requests or responses**"; the DPA, privacy policy, and **zero data retention (ZDR) are offered only for Enterprise** (<https://docs.typesafe.ai/models>) — the data-retention policy for non-Enterprise tiers still needs to be confirmed with the vendor.
- Chinese/multilingual capability is not its strength (supported by both the vendor's own statements and independent measurements).

### 6.3 Official numbers cannot be used directly for capacity planning

- The same company gives **4 mutually contradictory multipliers** (193.6×/444.6×, 40×–200×, 20×–200×, 40×–1,000×).
- The "correct answers" in the official benchmark are **the average of two LLMs' outputs**, not human labels; the vendor itself admits this biases results toward OpenAI/Anthropic models.
- The vendor itself admits the evals ran on internal laptops, the workflows were built by the internal team, "0% type errors" is not a measurement, and the demo states are on the short side.
- The only large independent test with real ground truth (Arize, 18,514 emails) shows a tie with TF-IDF.

### 6.4 Calibration trustworthiness is two-sided

| Conclusion | Evidence |
|---|---|
| Good on knowable tasks | OpenBookQA ECE 0.024 (= noise floor); 100% consistency across LangChain's 500 repeated verdicts, lowest variance |
| Overconfident on unknowable tasks | Self-built synthetic tickets ECE 0.107 (4.4× the noise floor); the `score` sub-task needs temperature refit to 3.40 |
| The returned `confidence` is worse than `max(probabilities)` | Independent test ECE 0.18 |
| Direction flips with the primitive | choice/score overconfident (T≈3.3), boolean underconfident instead (T≈0.66) |
| Logically inconsistent | The probabilities of a question and its negation can sum to ≠ 1 (official example 1.19) |
| Hard failures exist | On DAIR Emotion, **16% of samples assign zero probability to the true label** (reported by the Laya authors) |

### 6.5 The "abstain rate" is the most easily overlooked cost item

- A measured **30% abstain rate** → the cost advantage drops from 76× to **3.2×**.
- Ceiling formula: `effective cost multiplier ≤ 1 / abstain rate`, independent of unit price.

### 6.6 License and naming risks on the open-source side

- **No license (license = null, adoption carries legal risk, verified 09-29)**: `yibie/awesome-jev` (now up to **1,950★**), `bespokelabsai/nimble` (**1,897★**), `ekzhang/openjev-sglang`, `SAGAR-TAMANG/sarvam-jev`, `SiliconLabAI/OpenJev`, etc. **Good news**: `featherless-ai/simple-jev` added Apache-2.0 on 09-28.
- **NOASSERTION** (the repo has a LICENSE file that GitHub cannot identify): `Heman10x-NGU/openJev-verdict-2.0`, `rorshopping/jev-on-a-laptop`, `kydlikebtc/awesome-jev`, `yibie/jev-engineering-zh`, etc.
- **Compliance of redistributing base-model weights**: Qwen3.5-4B is itself Apache-2.0, so redistribution by mainstream reproduction projects **is generally not in conflict**; the one clearly visible gap is that **NanoJev's HuggingFace weights repo declares no license at all**. Do not parrot the popular claim that "reproduction projects necessarily have license problems."
- **Misleading naming**: calling a reproduction project "JEV" outright can make people think they are getting the official model. A positive example is `TheoLeeCJ/SemIf-OpenJev`, which proactively renamed itself and states in its README that "what is reproduced is the interface pattern, not JEV's unpublished model and training; unaffiliated with TypeSafe."

### 6.7 The ecosystem shows obvious inflation

- GitHub `q=jev` repos: about **7,330** on 09-21 → about **14,028** on 09-29 (+91% in 8 days); those that actually explain the mechanism still number about **20–25**.
- There are now over **20** `awesome-jev`-style directories, most created in the first week after launch; the directory sites' star snapshots are **systematically low**.
- Some repo READMEs are **internally self-contradictory** (e.g., `wfzyx/von` gives two versions each of its T value and training-set size); cross-check before citing their numbers.
- Before citing any reproduction project's benchmark, remember: **this report did not run any of these repos** — all these numbers are vendor-reported.

### 6.8 Route-level doubts

- One independent analysis (Archer, 1,029 black-box probes) presents an experiment **falsifying "independent logits + softmax"**: after adding irrelevant options, log-odds dropped from +0.38 to +0.11 (consistent across 10/10 groups) — i.e., it may not be a simple "classifier wrapper."
- But counter-evidence exists too: strong models on strict JSON schema (Terra) can likewise achieve "zero hallucination"; therefore **"not generating text" is not in itself a moat** — what matters is the combination of latency, cost, and probability quality.

---

## 7. Appendix: Verification Methodology, Unverified Items, and References

> Repo metadata was pulled live with `gh api` on 2026-09-21 and refreshed on 2026-09-29; official documentation pages, the official eval site, and launch post were fetched and parsed directly (raw captures live in `research/`). Numbers that only exist in secondary reporting are flagged as unverified below. Everything here is reproducible with the commands in 7.4.

### 7.1 Contents of this repository

```
README.md                        # 本报告正文（v1.1）
LICENSE                          # CC BY 4.0（报告文本许可）
CITATION.cff                     # 引用格式
CHANGELOG.md                     # 版本更新记录
research/jev-official.md         # 官方事实与 API 契约的原始核实记录（含逐条来源）
research/os-reproductions.md     # 开源复现项目逐个核实记录（含 gh api 原始输出）
research/ecosystem-benchmarks.md # 第三方评测、生态目录、风险分析的原始记录
research/os-decision-models.md   # Laya 与自训开放权重模型的核实记录
research/laya-github-readme.md   # Laya 官方 README 快照（其 benchmark 与局限）
data/open-source-projects.csv    # 项目元数据表（star/许可证/底座模型等，09-29 快照，38 行）
```

(Translation of the file manifest: `README.md` = this report's main text (v1.1); `LICENSE` = CC BY 4.0 (report text license); `CITATION.cff` = citation format; `CHANGELOG.md` = version history; `research/jev-official.md` = raw verification record of official facts and the API contract (with per-item sources); `research/os-reproductions.md` = per-project verification record of open-source reproductions (with raw `gh api` output); `research/ecosystem-benchmarks.md` = raw record of third-party evals, ecosystem directories, and risk analyses; `research/os-decision-models.md` = verification record for Laya and self-trained open-weight models; `research/laya-github-readme.md` = snapshot of Laya's official README (its benchmarks and limitations); `data/open-source-projects.csv` = project metadata table (stars/license/base model, etc., 09-29 snapshot, 38 rows).)

### 7.2 Evidence-tag definitions

| Tag | Meaning |
|---|---|
| [Official] | From official sites such as typesafe.ai / docs.typesafe.ai / evals.typesafe.ai, fetched directly for this report |
| [Third-party] | Published by independent testers, media, or analysts; not rerun for this report |
| [Vendor-reported] | Benchmarks published by an open-source repo's own authors, with no third-party rerun |
| [Unverified] | Only secondary retellings exist, sources contradict each other, or the original page is unreachable |

### 7.3 Explicitly unverified / doubtful items

| Item | Status |
|---|---|
| Full text of the Business Wire funding press release, The Register original | Fetch failed (403 / unreachable); cited only via republications |
| TypeSafe's ~$200M valuation | Single third-party source |
| Official parameter count, architecture, training data, KV-cache and batching mechanisms | Not officially published; **any claim of "official KV-cache broadcast" is third-party inference** |
| The multiplier figures across official pages (193.6×/444.6×/40×–200×/40×–1,000×) | The vendor contradicts itself; its methodology cannot be reproduced |
| "Cleared 140k waitlist in 36 hours", "trained on 100% synthetic data" | Secondary retellings / explicitly labeled as rumor |
| `wfzyx/von`'s T value, training-set size, and cited arXiv entry | Internally contradictory / the arXiv entry's **existence is unverified** |
| `Heman10x-NGU/openJev-verdict-2.0`'s ECE 1.44%, and all of NanoJev/kev/nimble's benchmarks | Vendor-reported, no third-party rerun seen |
| APUS "among the world's earliest / among China's first" | Media + project-author claims; cannot be independently verified |
| Ecosystem size (7,330→**14,028** / 503 / 386 / 195 …) | Three counting methods disagree; note the source when citing |
| All reproduction projects' speedup multipliers | **This report did not run any of these repos** |
| ~~Whether the vendor has zero data retention, whether data is used for training by default~~ | **Verified on the official Models page on 2026-09-29**: does not train on customer requests/responses; ZDR is Enterprise-only |
| Benchmarks and details of `togethercomputer/tev1`, `allebee/jevk5`, `Liuziyu77/Valen` | Appeared after 09-23; **only metadata and READMEs were collected — not run** |

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

### 7.5 Key references

**Official**
- Website <https://typesafe.ai/> · Launch post <https://typesafe.ai/blog/introducing-system-one-models-and-jev> · Team <https://typesafe.ai/team>
- Docs: <https://docs.typesafe.ai/api> · `/models` · `/primitives` · `/concepts/system-one` · Failure modes <https://docs.typesafe.ai/model-jaggedness/jev-1.13>
- Evals page <https://evals.typesafe.ai/> · Agent Skill <https://github.com/typesafe-ai/skills>

**Independent third-party evaluations**
- LangChain <https://www.langchain.com/blog/building-a-harness-with-jev> · Arize <https://arize.com/blog/typesafe-jev-llm-judge/> · Capital & Compute <https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/> · bigbangindex <https://bigbangindex.com/blog/typesafe-jev-cost-latency-analysis>
- Chinese-language: CNR (央广网) <https://tech.cnr.cn/techph/20260920/t20260920_527819594.shtml> · QbitAI (量子位) <https://www.qbitai.com/2026/09/492939.html>

**Open-source projects**
- Laya <https://github.com/NandhaKishorM/laya> (weights <https://huggingface.co/convaiinnovations/laya>, MLX port `mizorewww/laya-mlx`)
- SemIf-OpenJev (formerly OpenJev) <https://github.com/TheoLeeCJ/SemIf-OpenJev> · mini-jev <https://github.com/r-ms/mini-jev> · jevlike <https://github.com/vinnylarouge/jevlike> · jevmlx <https://github.com/bnsd55/jevmlx> · NanoJev <https://github.com/TianyuCodings/NanoJev> · kev <https://github.com/jaredpalmer/kev> · nimble <https://github.com/bespokelabsai/nimble> · von <https://github.com/wfzyx/von> · openjev-sglang <https://github.com/ekzhang/openjev-sglang> · simple-jev <https://github.com/featherless-ai/simple-jev> · jev-ultrafast <https://github.com/browser-use/jev-ultrafast> · fast-browser-use <https://github.com/APUS-AI-Lab/fast-browser-use> · tev1 (Together AI) <https://github.com/togethercomputer/tev1> · ollaya <https://github.com/ollaya-dev/ollaya> · Valen <https://github.com/Liuziyu77/Valen>
- Ecosystem directories: <https://jevbest.com/zh/> · <https://madewithjev.com/github-repos> · <https://github.com/logicrw/awesome-jev-projects> · <https://github.com/yibie/awesome-jev>

**Note on comparison tables**: this report does not provide a single "who is fastest" conclusion table, because the official figures contradict each other, the third-party tests all use different tasks, and none of the open-source projects' numbers has been independently rerun. When making a selection, rely on **measurements on your own data**.

---

*This report was compiled by an AI research agent; every number is annotated with its source type and verification status. If you find an error, please open an issue or a PR to correct it.*
