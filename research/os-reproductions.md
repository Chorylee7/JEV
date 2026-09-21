# JEV 开源复现项目·原始资料汇编

> 数据采集时间：**2026-09-21T04:15Z（UTC）／ 2026-09-21 12:15 CST**
> 采集工具：`gh api`（gh CLI 已登录账号 `Chorylee7`，token scopes: `gist, read:org, repo`）+ WebSearch
> 所有 star/fork/license/created_at/pushed_at 均为上述时刻 GitHub API 返回值，**未经二次推测**。
> 「未核实」= 本次采集未取得该字段的权威来源。

---

## 0. 背景事实核对（用于交叉验证开源项目的主张）

| 事实 | 内容 | 来源 | 核实状态 |
|---|---|---|---|
| 发布方 | TypeSafe AI，创始人 Diogo Almeida（前 OpenAI 研究员、InstructGPT/ChatGPT/RLHF 论文作者之一，曾在 Google Brain） | https://explainx.ai/blog/typesafe-ai-jev-system-one-models-launch-2026 | 第三方报道 |
| 发布日 | 2026-09-15（有来源写「early access on 2026-09-14」，另一处写「as of 15 September 2026」） | https://www.ayautomate.com/blog/jev-typesafe-system-one-model ; https://www.remio.ai/post/typesafe-jev-ai-model-challenges-the-llm-first-software-stack ; https://aiprofitboardroom.com/blog/jev-ai/ | **日期存在 9/14 与 9/15 两种说法**，未完全对齐 |
| 融资 | 出 stealth 同时公布 $40M seed | https://www.ayautomate.com/blog/jev-typesafe-system-one-model | 第三方报道 |
| 定价 | input $0.042/1M tokens，output 免费 | 官方：https://docs.typesafe.ai/models （被多个仓库 README 直接引用） | 官方 |
| 官方性能声明 | 分类/决策任务最快快约 200×、成本最低约 1/400 | 央广网/新华网转述"TypeSafe 官方公布" | **官方单方面宣称**，本次未看到可复现的官方 benchmark 表 |
| 接口 | `POST https://api.typesafe.ai/v1/systemone`；model 名 `jev-latest` / `jev-1.13` | 多个复现仓库 README 与实际代码 | 多源一致 |
| 三个原语 | Choice（多选归一化分布）、Noul（布尔后验概率）、Score（有序量表期望值） | https://docs.typesafe.ai/primitives/choice ；多仓库一致 | 多源一致 |
| 官方 benchmark 页 | https://evals.typesafe.ai/ | SemIf README 引用 | 官方 |
| 权重 | **未开源，仅云端 API**（waitlist-gated 早期访问） | https://aiprofitboardroom.com/blog/jev-ai/ | 与"仅 API"背景一致 |
| 是否"从不幻觉" | 有媒体标题写 "Never Hallucinates" | https://explainx.ai/blog/typesafe-ai-jev-system-one-models-launch-2026 | **媒体表述，非官方承诺** |

**重要交叉事实：** APUS（麒麟合盛）开源复现被中国官媒报道：
- 央广网 https://tech.cnr.cn/techph/20260920/t20260920_527819594.shtml （2026-09-20）
- 新华网 http://www.news.cn/tech/20260921/8f1c9bd6a9254e629383f1ac51e0d27d/c.html （2026-09-21）
- 量子位 https://www.qbitai.com/2026/09/492939.html （2026-09-20 16:30）
- MENAFN / Arabian Post https://menafn.com/1111681502/Typesafe-Unveils-Decision-Focused-AI-Model-Jev-Arabian-Post

**注意：** 媒体稿称 APUS 项目为「全球最早一批 / 国内首批」独立开源复现，且称「全部代码以 MIT 协议开放」。**这是媒体+项目方宣称**；实际仓库 star 数（35）远低于同期社区项目如 `browser-use/jev-ultrafast`（12,586）与 `TheoLeeCJ/SemIf`（2,524）。「最早」这一说法本次无法独立核实。

---

## 1. 检索方法（可复现）

```bash
# 按 star 排序全量检索
gh api "search/repositories?q=jev&sort=stars&per_page=50" \
  --jq '.items[]|{full_name,stargazers_count,forks_count,license:.license.spdx_id,description,created_at,pushed_at,html_url}'

# 精确名检索
gh api "search/repositories?q=openjev+OR+semif+in:name&sort=stars&per_page=50"
gh api "search/repositories?q=mini-jev+OR+minijev&sort=stars&per_page=20"
gh api "search/repositories?q=jev-e2e&sort=stars&per_page=20"
gh api "search/repositories?q=jev+mlx&sort=stars&per_page=20"
gh api "search/repositories?q=%22fast+browser+use%22+jev&per_page=20"

# topic 检索
gh api "search/repositories?q=topic:jev&sort=stars&per_page=60"
gh api "search/repositories?q=topic:system-one&sort=stars&per_page=50"

# 范式关键词检索
gh api "search/repositories?q=%22non-autoregressive%22+decision+model&sort=stars&per_page=30"
gh api "search/repositories?q=%22forward+pass%22+logits+jev&sort=stars&per_page=30"
gh api "search/repositories?q=%22typed+decisions%22&sort=stars&per_page=30"
gh api "search/repositories?q=jev+reproduction+OR+reproduce&sort=stars&per_page=25"
gh api "search/repositories?q=%22system+one%22+decision+model+open+source&sort=stars&per_page=30"

# 单仓详情
gh api repos/OWNER/REPO --jq '{full_name,stargazers_count,forks_count,open_issues_count,
  subscribers_count,license:.license.spdx_id,created_at,pushed_at,updated_at,size,language,topics,homepage,description,archived,default_branch}'

# README
gh api repos/OWNER/REPO/contents/README.md --jq .content | base64 -d
```

**检索缺口（本次未覆盖）：** GitHub 上存在**数百个**同日批量提交的 `awesome-jev` 类目录仓库（至少 18 个独立作者）。本文件只收录**实际做复现/推理引擎**的项目，目录类仓库单列于 §5。

---

## 2. 任务点名项目（逐一核实）

### 2.1 `TheoLeeCJ/SemIf`（原名 OpenJev）★ 主要项目

| 字段 | 值 |
|---|---|
| 仓库全名 | `TheoLeeCJ/SemIf` |
| URL | https://github.com/TheoLeeCJ/SemIf |
| Stars | **2,524** |
| Forks | 158 |
| Open issues | 13 |
| Watchers | 10 |
| License | **MIT**（代码） |
| 创建 | 2026-09-16T03:51:21Z |
| 最近推送 | 2026-09-19T04:46:36Z |
| 语言 | Python |
| 主页 | **openjev.com** |
| 默认分支 | `master` |
| topics | （空） |
| archived | false |

**改名事实（README 第1行，原文）：** `# SemIf (formerly OpenJev)`
> "**Independent research project.** SemIf was formerly called OpenJev. It is not affiliated with or endorsed by TypeSafe."

**底座模型：** 主基线 `Qwen/Qwen3.5-4B`（BF16），revision 固定为
`851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`。
浏览器 demo 模型梯度：Qwen3-0.6B (Q8_0, 639 MB) / MiniCPM5-2B (Q4_K_M, 1.56 GB) / Qwen3.5-4B (Q4_K_M, 3.01 GB)。
另对比 `Qwen/Qwen3-Reranker-4B`。

**核心做法（README 原文）：**
- `--mode direct`：**单次前向读取 declared option logits**（"one forward pass reads declared option logits; no answer token is sampled"）。
- `--mode shared`：**同一 state 只 prefill 一次，criteria 并行评估**（"prefill it once and evaluate the criteria in parallel"）——即 KV-cache 广播/前缀复用。
- 三种执行路径：Fresh direct scoring / Serial prefix reuse / Parallel suffixes / Native reranker。
- **跳过自回归解码：** 输出 token 数 = 0。

**硬件：** CUDA（RTX 3090，24GB 可装 4B BF16）；Apple Silicon 有原生 MLX backend（`pip install -e '.[test,mlx]'` + `--backend mlx`）；另有 **WebGPU 浏览器 demo**（`webgpu-demo/index.html`，无需 API key）。

**HTTP server：** README 未描述 HTTP server；提供 CLI（`semif-score`）+ 本地 HTML demo。**未核实 HTTP server。**

**是否声称校准：** **谨慎**。README 原文：
> "Returned probabilities are conditional on the supplied options. **Calibrate and validate them on the workload where they will make decisions.**"

即项目方**不声称开箱校准**，要求用户自行校准。未给出 ECE 数字。

**自测数据（项目方自报）——**

速度（同一 frozen Qwen3.5-4B、同一 state、21 条二元 criteria、单张 RTX 3090、3 次中位数）：

| Output path | Time | Output tokens | Result |
|---|---:|---:|---|
| Direct typed logits, median of 3 | **1.023 s** | **0** | 21 probability pairs |
| Autoregressive JSON array, median of 3 | 5.332 s | 111 | Valid ordered 21-value array |

→ 加速 **5.21×**（非 200×）。作者自注：「Their choices agreed with direct argmax on 18/21 criteria, so this is a **systems comparison** rather than a claim that the two readouts are semantically equivalent.」

state 复用（37 states × 21 criteria = 777 decisions）：

| Execution path | Decisions/s | 777 decisions |
|---|---:|---:|
| Fresh direct scoring | 2.33 | 333.1 s |
| Serial prefix reuse | 10.75 | 72.3 s |
| Parallel suffixes | **20.03** | **38.8 s** |
| Native reranker | 1.86 | 417.3 s |

**质量（balanced accuracy，项目方自报）：**

| System | Authored balanced acc | Perturbation balanced acc | TypeSafe subset agreement |
|---|---:|---:|---:|
| Qwen3-0.6B | 0.440 | 0.528 | 0.407 |
| MiniCPM5-2B | 0.686 | 0.693 | 0.637 |
| **Qwen3.5-4B** | **0.813** | **0.766** | 0.845 |
| Published Jev | — | — | **0.883** |

> 原文边界声明："The Jev number is read from TypeSafe's published records; **we did not run a live Jev endpoint**. The comparison covers the 102 rows that could be aligned from public artifacts, not TypeSafe's reported 711-row aggregate."

其他：WANLI balanced acc 0.637（256 行）；36 条 judgment grid accuracy 0.806。

**README 承认的局限：**
- "The fast reuse paths are experimental: BF16 execution **changed 5–6 of 777 argmaxes** relative to fresh scoring."
- 概率是"conditional on the supplied options"，必须自行校准。
- 复现的是**接口范式**："This project reproduces that **interface pattern** with open models; it does **not** reproduce Jev's undisclosed model or training."
- 未跑真实 Jev endpoint，Jev 数字是从官方公开记录读的。
- 模型权重与第三方源码不在仓库内。

**第三方验证状态：** 项目自称有 preregistered 实验、committed row-level outputs、checksums。**未做第三方独立复现验证。**

---

### 2.2 `r-ms/mini-jev`

| 字段 | 值 |
|---|---|
| URL | https://github.com/r-ms/mini-jev |
| Stars | **35** |
| Forks | 3 |
| Open issues | 1 |
| License | **MIT** |
| 创建 | 2026-09-17T19:41:13Z |
| 最近推送 | 2026-09-18T12:05:38Z |
| 语言 | Python |
| 主页 | null |

**底座模型：** `Qwen/Qwen3-4B-Instruct-2507`（bf16, greedy），revision pinned。约束生成用 `xgrammar`。任务数据集 CLINC150。
**核心做法：** 把每个 closed-choice field 变成字母化的多选题，**一次前向读取 option letter 的 logits**（"read the model's scores for the option letters at the answer position. No token is generated"）。字符串/数字仍然生成。**共享 KV cache（shared-prefix）**跨问题复用。
**硬件：** Apple Silicon (MPS) 或 NVIDIA CUDA；4B 模型约 8.5 GB 内存，约 9 GB 磁盘。
**HTTP server：** 有本地 demo server（`demo/server.py`，`http://127.0.0.1:8765/`），是教学 bench，非生产 API。
**是否声称校准：** **明确否认校准**。README 原文：
> "the shares are ***normalized candidate scores*, not calibrated probabilities**; use the gap for abstention, **do not read the percentage as P(correct)**"
且 `DEFERRED.md` 列出「what was deliberately not done (**second model, calibration**)」。

**项目方自报结果（preregistered，PREREG.md + amendments v1.1–v1.3）：**

| 问题 | 结论 | 证据 |
|---|---|---|
| 读字母 vs 语法约束生成 JSON 是否掉精度？ | **不掉**。intent field，6750 配对观测/450 文本：JSON 0.909，letters 0.907，Δ −0.22 pp，95% CI [−1.44, +1.04]。k=2..16 每个都覆盖 0 | run b2 |
| 机制真的是"读答案"吗？ | 是。13,600/13,600 问题中最高概率 next token 就是 option letter；candidate mass min 0.99999624；position prior flat | run b2 |
| 更快吗？ | 短文本（32 tokens）**4× 更快**（0.24× 时间）。2048-token 长文本配 shared-prefix cache：**1.4× / 1.8× / 2.4× 更快**（1/2/3 fields）。naive 每字段重读文本反而**更慢**（1.10–1.16×） | runs b2/b3 |
| 字母 vs 写选项全名？ | 字母好：intent +10.0 pp [+8.3, +11.7]；domain +13.2 pp；单 token 布尔 +1.2 pp（CI 覆盖 0） | run b1 |
| 哪里会输？ | Out-of-scope 文本：JSON 选"none of the above" 47/50，letters 只有 41/50。**依赖字段**：后续布尔若写在同一 JSON 里会 +5 pp | run b2 |
| 让模型自己写概率（TypeSafe adapter 形状）？ | **不行**。intent 只有 0.346（vs letters 0.896），62% 的"choice"都是第一个选项 | run b3 |
| shared KV cache 会改答案吗？ | 精度相同（0.8484 vs 0.8483）；13,500 中 59 个答案翻转，全在接近平局处。两台不同 RTX 4090 上跑同样代码逐位相同（607/607） | run b2 |

**README 承认的局限（原文）：**
> "One model (Qwen3-4B-Instruct), one dataset (CLINC150, English, short utterances). Bench times are one request at a time on one GPU. The letter shares are a ranking with a confidence gap, not calibrated probabilities."

另：>26 options 的 enum、Score 原语、extraction-as-choice 均**明确标注为未测量**。

**数据集：** 运行记录在 HF `Mikhail/mini-jev-runs`（27,900 decisions，含完整 candidate logits、normalized scores、confidence gaps、provenance hashes）。

---

### 2.3 `vinnylarouge/jevlike`

| 字段 | 值 |
|---|---|
| URL | https://github.com/vinnylarouge/jevlike |
| Stars | **1,097** |
| Forks | 97 |
| Open issues | 5 |
| License | **MIT** |
| 创建 | 2026-09-16T10:26:01Z |
| 最近推送 | 2026-09-16T18:12:53Z |
| 语言 | Python |
| description | **null（无描述）** |

**底座模型：** **从零训练的 byte-level encoder**（默认，learns byte embeddings from scratch）；可选 Hugging Face frozen encoder 路径 —— README 示例用 `Qwen/Qwen2.5-0.5B`，`--rank 256` 只训 scorer head。**这是一个"从零训练 starter model"，不是对现成 LLM 的推理包装。**

**核心做法：** 每个 option 变成一个 query vector → 对 context token 做 attention → 每个 option 得到一个 context vector → shared dot product 出分数 → **softmax across options**。一次前向出每个 option 一个概率。
- 发布 checkpoint：`examples/checkpoints/joint-imitation.pt`（Doom 7 键 + 象棋 5 键的 joint checkpoint）、更强的 chess-only checkpoint、一个 shared 12-option checkpoint。
- 视觉版本：`jevlike.vision` 可从 image patches 评分 controller buttons。

**硬件：** CPU、Apple MPS、CUDA（`--device`）。
**HTTP server：** 无。提供 CLI：`jevlike-train` / `jevlike-eval` / `jevlike-predict` / `jevlike-data`。
**是否声称校准：** **是，声称测量 ECE** —— "Expected calibration error compares confidence with observed accuracy." 另打印 shuffled-context control。**但这是工具能力描述，未给出具体 ECE 数值。**

**项目方自报数字（README 原文）：**
- 合成菜单上 one-pass scorer 约 **98%** accuracy。
- Target-disjoint Wikispeedia next-click：frozen Qwen2.5-0.5B encoder + scorer = **26%**（shuffled 与 random-encoder 对照约 8%）；40,000 clicks 从零训练的小模型 = **29%**。
- 「八选项时，one pass 比被迫写 400 tokens 的小 decoder **快约 100 倍**」。
- Doom joint checkpoint：10 局平均 **0.60 kills**，reward **−97.50**。
- Chess-only checkpoint：对 random mover **4 胜 46 平 0 负**（50 局）；**对 Stockfish level 0：0 胜 2 平 48 负**。

**README 承认的局限（原文，全列）：**
- "This is a research starter, **not a copy of Jev**."
- "Accuracy depends on data quality, split quality and the encoder."
- "The byte encoder is cheap but **weak on language meaning**."
- "The pretrained path may download a large model and needs more memory."
- "One-pass scoring **requires the complete option list** before prediction."
- "The speed comparison used a **small local decoder** rather than a large commercial model."
- "**We did not show equal quality with Jev** or reproduce TypeSafe's private training method."
- Doom/chess 录像是「selected for activity」，明确声明**不是典型玩法或能力声明**。

---

### 2.4 JEV MLX engine / mlx 系列

本次共发现 **5 个** MLX 相关仓库（含 1 个 Laya 而非 JEV 的）：

#### 2.4.1 `bnsd55/jevmlx` —— 最完整的 MLX 实现

| 字段 | 值 |
|---|---|
| URL | https://github.com/bnsd55/jevmlx |
| Stars | **47** |
| Forks | 8 |
| Open issues | 7 |
| License | **MIT** |
| 创建 | 2026-09-17T10:20:12Z |
| 最近推送 | 2026-09-21T03:13:55Z（**活跃**） |
| 语言 | Python |
| topics | `apple-silicon`, `jev`, `local-llm`, `local-models`, `mlx` |
| homepage | https://github.com/bnsd55/jevmlx#readme |

**底座模型别名（README 表格原文）：**

| Alias | Resolves to | Use |
|---|---|---|
| `quality` | `mlx-community/Qwen2.5-7B-Instruct-4bit` | **default** — best accuracy |
| `fast` | `mlx-community/Qwen2.5-3B-Instruct-4bit` | lower latency |
| `test` | `mlx-community/Qwen2.5-1.5B-Instruct-4bit` | tests only (too small for production) |

下载量：~2 GB (`fast`) / ~4.5 GB (`quality`)。也支持任意 HF Hub id，例如 `mlx-community/Llama-3.2-3B-Instruct-4bit`。

**核心做法：**
- schema 里的每个 field（bool / enum / multi-select）的**所有允许选项在一次 prefill 中全部从 logits 评分**，不生成文本；JSON 由程序从 winner 拼装（"valid by construction"）。
- **KV cache 共享**："The model prefills once and the KV cache is shared."
- 每个 field 一行 scoring row（multi-token option 用额外 trie rows）；每 field 一个 **restricted softmax**；temperature 最后统一施加；ties 确定性解析。
- 两个 scorer：`labels`（默认，7B 上实测更好）与 `slots`（单 token letter codes，长选项列表更便宜）。
- 有 **codebook search**，按 tokenizer 编译 schema，挑 tokenize 最干净的 neutral alias codes。
- context 用 per-context nonce 围栏，防止内部行伪造闭合围栏。
- chunk 大小按实测 active-memory budget 决定；Metal OOM 时 halve chunk 并重试。
- 支持 `constraints`（implies / excludes / requires_parent）+ `prior_correction` + `calibration=<path>`。

**硬件：** Apple Silicon M1+，Python 3.12+。单 Metal GPU、单 serial worker。**也支持 `--backend openai`** 走任何返回 logprobs 的 OpenAI 兼容 server（Ollama / vLLM），但「one request per field (slower than one pass)」且只能看到 top-k logprobs。

**HTTP server：** **有**（`jevmlx serve --model fast --port 8000`）。

| Method | Path | 说明 |
|---|---|---|
| POST | `/decide` | `{"schema","context","temperature"}` → per-field result |
| POST | `/v1/systemone` | TypeSafe 形状：`{"state","questions"}` → `{model, answers, usage}` |
| GET | `/v1/models` | |
| GET | `/health` | 带 `queue_depth`, `queue_capacity`, `worker_alive` |
| GET | `/ready` | 503 直到 load + warm-up 完成 |

背压：队列满 → **429 + Retry-After**（`--queue-size` 默认 16）；超 `--max-rows`(2048) 或 `--max-prompt-tokens`(8192) → **413**（在任何模型工作前）。每个响应带 `queue_depth` 与 `queue_wait_ms`。

**是否声称校准：** **有校准工具，但未声称默认校准。** 
- `abstain_below_margin=X` 用 `probability_margin`（top1 − top2）做弃权门；README 强调「**Fit the threshold on labeled examples — not by feel**」。
- 有 `calibrate` CLI：在 labeled JSONL 上拟合 temperature + multi calibrator。
- `FieldResult` 带 `legal_mass`（允许 continuation 的概率质量，低 = 泄漏信号）。
- `ordered=True` 的 enum 额外给 `argmax_level`、`expected_index` (Σ pᵢ·i)、`expected_score_normalized`。
- **未发布 ECE 数字。**

**README 承认的局限：**
- "Not affiliated with TypeSafe AI."
- restricted softmax 无法说"以上都不是"，除非显式给 `other`/`escalate` 选项或 `allow_none_of_above=True`。
- OpenAI-compatible backend 路径：「only the server's top-k logprobs are visible — options missing from that list get a **floor probability** and `truncated: true`」。
- **Leaderboard 表格：** 官方 TypeSafe 准确率是**引用**的（"cited, retrieved 2026-09-17"），本地行空白 —— `<!-- leaderboard:start --> ... No local results yet — contribute one with jevmlx bench. <!-- leaderboard:end -->`。表格脚注：*"Official accuracies are on TypeSafe's full private eval; ours are on the 20 public example cases, so the numbers are indicative, **not the same test**."*

引用的官方数字（**引用，非本项目测量**）：

| Model | Source | Accuracy | Time/case | Cost/case |
|---|---|---:|---:|---:|
| Jev | official (cited) | 67.8% | 0.4s | $0.0004 |
| GPT-5.6 Terra | official (cited) | 67.9% | 10.1s | $0.0304 |
| Claude Sonnet 5 | official (cited) | 67.8% | 78.1s | $0.1174 |
| Claude Opus 5 | official (cited) | 73.1% | 37.8s | $0.1761 |
| GPT-5.6 Sol | official (cited) | 74.1% | 23.3s | $0.0836 |
| Claude Haiku 4.5 | official (cited) | 53.6% | 12.5s | $0.0195 |

附带：bundled presets `fintech_fraud`(28 fields) / `support_triage`(30) / `code_security`(28) / `high_cardinality_255`(4, 255-choice) / `content_moderation`(20) / `inbound_email`(19)。有 TypeScript client `@jevmlx/client`（在 `js/`，未发 npm）。

#### 2.4.2 `CoderInPajamas/JEV-MLX`

| 字段 | 值 |
|---|---|
| URL | https://github.com/CoderInPajamas/JEV-MLX |
| Stars | **2** |
| Forks | 0 |
| License | **MIT** |
| 创建 | 2026-09-20T13:09:46Z |
| 最近推送 | 2026-09-20T16:13:19Z |
| 语言 | Python |
| topics | `action-selection`, `apple-silicon`, `jev`, `local-inference`, `mlx`, `mlx-lm`, `semantic-routing` |

- 项目内部名 JEV MLX；**发行包/CLI 名 `jev-mlx`，Python import 为 `jev_mlx`**。README 明确：**"Version 0.1 is experimental and has not been published to PyPI."**
- 前身名为 **MLXJ**（录屏文件名保留旧名）。
- **底座模型：** 用户自带本地 MLX-LM checkpoint。README 实测用了三个：`Qwen3.5-9B-OptiQ-4bit`、`Gemma 4 26B-A4B MoE`、`GLM-4.7-Flash-4bit`。
- **核心做法：** state + 一句话 utterance + 动态 allowed choices → 选一个稳定 business ID。**prefix reuse**（"Reuse stable context while evaluating every new utterance. **Never cache final answers.**"）。有显式 `no_match` / `abstain` 结果。有 state version 保护（state 变更后拒绝 stale decision，执行授权只消费一次）。
- **硬件：** Apple Silicon，native ARM Python 3.11+。
- **HTTP server：** 有（localhost HTTP service），另提供 Python API + CLI（`jev-mlx decide --request examples/decision.json`）。
- **是否声称校准：** **明确否认**。README 原文：
  > "Candidate scores rank choices and are **not calibrated probabilities of correctness**. State guards do not establish semantic correctness."
- **自测数据（Apple M2 Max / 64 GiB / 36 个虚构英文 case，6 个域）：**

| Local checkpoint | Exact decisions / 36 | Wrong actions / 30 | Same-page p50 / p95 |
|---|---:|---:|---:|
| Qwen3.5-9B-OptiQ-4bit | 30 / 36 (**83.3%**) | 1 / 30 | 194.8 / 407.5 ms |
| Gemma 4 26B-A4B MoE | 31 / 36 (**86.1%**) | 1 / 30 | 168.9 / 556.5 ms |
| GLM-4.7-Flash-4bit | 21 / 36 (**58.3%**) | 8 / 30 | 170.6 / 330.5 ms |

- **承认的局限：** "**These results do not establish reliable unattended actions, arbitrary-model compatibility, or fixed 100 ms performance.**"；timings 需要 weights 已加载 + 可复用 page prefix，不代表 startup 或任意新页面；Gemma 选错 queue item，Qwen 选错最长续航产品；GLM action error 更多；「**earlier small sample's zero-error observation did not carry over to new cases**」。
- Blocks 游戏 demo：Qwen3.5-9B，20 步放置、清 4 行、400 分；decision **p50/p95 = 5.78 / 11.57 秒**；第一次尝试模型**拒绝放置**；两次尝试都保留在报告里，明确「**not a held-out game benchmark or a speed claim**」。

#### 2.4.3 `day253/microjev`

| 字段 | 值 |
|---|---|
| URL | https://github.com/day253/microjev |
| Stars | **1** |
| Forks | 0 |
| License | **MIT** |
| 创建 | 2026-09-20T15:35:49Z |
| 最近推送 | 2026-09-20T18:49:34Z |
| 语言 | Python |

- **底座模型：** **GPT-2 124M**（`openai-community/gpt2`，revision `607a30d783dfa663caf39e06633721c8d4cfcd7e`）+ MLX 训练的结构化决策头，直接输出 **Choice / Noul / Score**。另有**零依赖纯 Python 教学实现**（不是 GPT-2 124M）。
- **硬件：** Apple Silicon（M4 Pro / macOS 26.6.2 / Python 3.13 验证）。含全量微调、只训决策头、模型保存/离线加载、概率校准、本机速度基准。
- **核心做法：** 新增「动态候选打分器」（`docs/candidate.md`）：运行时输入状态/问题/候选描述，由同一个 GPT-2 标量打分头输出分布。通过候选换序、问题 ID 改名、混合候选数量测试。
- **HTTP server：** 未见描述。
- **是否声称校准：** 是，README 称「独立校准」。
- **自测数据（2,210 条独立测试影评）：** 标准正面命题准确率 **87.19%**；正面/负面改写 **86.83% / 83.08%**；否定命题 **86.43%**；标准三分类 **71.54%**（「仍弱于固定头基线」）。
- **承认的局限：** 「这里验证的是**英文情感决策，不能外推到通用指令能力**」；「**没有使用 Jev 权重，不是 Jev 内部架构或 RLCD 的复现**」；权重不含在 Git 仓库内。

#### 2.4.4 `NullPo-jp/PocketJev`

| 字段 | 值 |
|---|---|
| URL | https://github.com/NullPo-jp/PocketJev |
| Stars | **0** |
| Forks | 0 |
| License | **MIT** |
| 创建 | 2026-09-17T11:14:40Z |
| 最近推送 | 2026-09-17T13:18:49Z |
| 语言 | **Swift** |
| topics | `ios`, `mlx`, `on-device-ai`, `qwen3-vl`, `swift`, `swiftui`, `vision-language-model` |

- **底座模型：** Qwen3-VL，**直接读 option logits**。
- **平台：** on-device iPhone 视觉决策工具（MLX + Swift/SwiftUI）。**这是本次发现的唯一 iOS 原生实现。**
- 未取 README（本次仅取元数据）。

#### 2.4.5 `Micha0827/snapjudge`（同属 MLX 系）

| 字段 | 值 |
|---|---|
| URL | https://github.com/Micha0827/snapjudge |
| Stars | **7** |
| Forks | 0 |
| License | **MIT** |
| 创建 | 2026-09-18T18:29:43Z |
| 最近推送 | 2026-09-19T18:29:19Z |
| topics | `apple-silicon`, `mlx`, `fastapi`, `logits`, `qwen`, `zero-shot-classification` 等 |

- 描述原文：「Typed decisions (choice / score / yes-no) from local Qwen models on Apple Silicon. **Probabilities come straight from the logits, no text generation.** **TypeSafe-compatible HTTP API**, runs on MLX.」
- **有 TypeSafe 兼容 HTTP API**（FastAPI）。

#### 2.4.6 顺带发现（**不是 JEV 复现，是 Laya 系**）

| 仓库 | Stars | License | 说明 |
|---|---:|---|---|
| `mizorewww/laya-mlx` | **1,931** | Apache-2.0 | Native MLX runtime for **Laya** typed decision models — 7–14 ms short decisions on M3 Max。created 2026-09-19，pushed 2026-09-19。topics 含 `system-one`, `typed-decisions` |
| `mizorewww/laya-coreml` | 453 | Apache-2.0 | Local **Laya** typed decisions on Apple Core ML and Neural Engine，~5 ms short decisions on M3 Max |
| `aovestdipaperino/laya-rust` | 2 | Apache-2.0 | Pure-Rust inference for Laya（ModernBERT-large + RL decision head），on candle |
| `lkarlslund/laya.cpp` | 12 | MIT | RTX-optimized C++ inference for Laya typed decisions |
| `r33drichards/laya-vision` | 11 | Apache-2.0 | Image inputs for Laya：calibrated, non-generative typed decisions over images + text（SmolVLM-256M backbone） |

**注意：** `mizorewww/laya-mlx` 的 star 数（1,931）**高于所有 JEV MLX 系仓库**，但它复现的是 **Laya**（`convaiinnovations/laya`，421M ModernBERT-Large marker 模型），不是 JEV。JEV 研究中被多次作为对照基线引用。**二者不应混淆。**

---

### 2.5 `APUS-AI-Lab/fast-browser-use`（APUS 麒麟合盛 AI 实验室）

| 字段 | 值 |
|---|---|
| 仓库全名 | `APUS-AI-Lab/fast-browser-use` |
| URL | https://github.com/APUS-AI-Lab/fast-browser-use |
| Stars | **35** |
| Forks | 1 |
| Open issues | 0 |
| Watchers | 1 |
| License | **MIT** |
| 创建 | 2026-09-19T10:17:17Z |
| 最近推送 | 2026-09-21T02:48:29Z |
| 语言 | Python |
| 主页 | null |
| 仓库体积 | 16,533 KB |
| description | "A fast browser-use skill powered by local LLMs via single-token reflexes. Fast, local-first, zero hallucinations." |

**底座模型：** `Qwen3.5-9B`（BF16 或 MLX 4-bit）与 `Qwen3.5-35B-A3B`（MoE，BF16 或 MLX 4-bit）。**全部本地权重，零云端 API。**

**核心做法（README 原文摘要）：**
1. **DOM 候选化：** 轻量 in-page scanner 只提取当前可见、可交互元素，格式化成离散候选 tuple，例如
   ```python
   ("CLICK", "btn_search")
   ("SELECT", "opt_timezone_sg")
   ("TYPE_TEXT", "input_query")
   ("DONE", "task_completed")
   ```
2. **单 token logits 评分：** 每个合法候选动态映射到词表里一个唯一单 token（`A`, `B`, `C`...），**一次前向**取 next-token logits，做归一化 softmax：
   $$P(c_i \mid \text{Context}) = \frac{\exp(z_i / T)}{\sum_{j=1}^K \exp(z_j / T)}$$
   README 表述：「reduces scoring from an O(tokens × layers) autoregressive decoding loop to an **O(1)** logits projection」
3. **动作/生成解耦：** 结构性动作走离散 logits 评分；**只有选中 `TYPE_TEXT` 时才调用生成式推理**写字段内容。
4. **KV-Cache Broadcasting & Batched Evaluation（原文标题）：**「By prefilling the common page context once and **broadcasting the base KV-Cache across candidate dimensions**, evaluating multiple fields or candidate options is parallelized into a single batch forward pass without cascading autoregressive error.」
5. **联合 Action + DONE 评分：**「Candidate actions and completion (`DONE`) are scored within the same forward pass, **slashing per-task inference passes from 14 to 4**.」

**硬件支持（README 表格原文）：**

| 平台 | Backend | 模型 | 最低内存 | 峰值 | 推荐硬件 |
|---|---|---|---|---|---|
| Apple Silicon M1–M5 | **MLX** (`FBU_BACKEND=mlx`) | Qwen3.5-9B MLX 4-bit | **16 GB** | ~6.5–7.5 GB | 16 GB+ 统一内存 |
| Apple Silicon M1–M5 | MLX | Qwen3.5-35B-A3B MLX 4-bit | **32 GB** | ~20.3–21.1 GB | 36/48/64 GB+ |
| NVIDIA GPU (Linux/Win) | PyTorch CUDA | Qwen3.5-9B BF16 | **24 GB VRAM** | ~20–22 GB | RTX 3090/4090/6000 Ada/A10/A5000 |
| NVIDIA GPU (Linux/Win) | PyTorch CUDA | Qwen3.5-35B-A3B BF16 | **80 GB VRAM** | ~75–80 GB | RTX PRO 6000 Blackwell (96GB) / A100 / H100 |
| x86 / ARM CPU | PyTorch CPU | Qwen3.5-9B FP32/BF16 | **32 GB RAM** | ~20–24 GB RAM | 多核工作站 |

环境变量：`FBU_BACKEND`(auto/mlx/torch)、`FBU_DEVICE`(auto/cpu/cuda/cuda:N)、`FBU_DTYPE`、`FBU_MODEL`。

**HTTP server：** README 未见 HTTP server 描述；提供 **CLI**（`fbu run/record/download/install-browser`）、**Python API**（`from fast_browser_use import Agent`）、以及 **Agent Skill** 打包（`npx skills add APUS-AI-Lab/fast-browser-use --skill fast-browser-use -a claude-code -a codex -g -y`）。

**是否声称校准：** **未声称。** README 未出现 calibration / ECE / 校准相关主张。它声称的是「**Zero Hallucination**」（因为动作从可见 DOM 派生，语法 100% 合法）。

**项目方自报 Benchmark（硬件：NVIDIA RTX PRO 6000 Blackwell Workstation 96 GB VRAM, Linux x86_64；PyTorch 2.14.0 CUDA 13.0 + flash-linear-attention + causal-conv1d；100% 本地推理）：**

Wikipedia 端到端实时导航（"Find and open the Wikipedia article about Python (programming language) starting from Main_Page, strictly verifying final URL and title."）：

| Run | Qwen3.5-9B 用时 | Qwen3.5-35B-A3B 用时 |
|---|---:|---:|
| Trial 1 | 4.055 s | 8.221 s |
| Trial 2 | 3.935 s | 4.933 s |
| Trial 3 | 4.067 s | 4.944 s |
| **Median** | **4.055 s** | **4.944 s** |

（原文：*Task completed in 4 discrete single-token scoring steps.*）

多场景套件：

| 场景 | 9B | 35B-A3B | 独立验证方式 |
|---|---:|---:|---|
| Wikipedia Navigation | **4.055 s** | **4.944 s** | 最终 canonical URL + 标题严格匹配 |
| Workspace Settings Form | **2.488 s** | **3.360 s** | 保存确认通知精确匹配 |
| Local Reading Room Navigation | **0.808 s** | **1.049 s** | 目标文章 URL + 标题精确匹配 |
| Python.org Navigation | **1.789 s** | **2.120 s** | 目标 `/about/` URL 精确匹配 |
| Example.com → IANA Info | **1.263 s** | **1.535 s** | 目的域精确匹配 |

**Harness（护栏）设计（README 自述）：**
- Bounded Settling Window：强制 150 ms 静默窗口（新文档 ≥500 ms，输入后 ≥300 ms）。
- Pre-Execution Physical Guards：可见性/遮挡检查、DOM freshness、read-only 保护。
- Write-Once Trace & No Mutation Retries：动作派发前不可变记录；派发过的 mutation **从不盲目重试**。
- Independent Outcome Verification：模型 `DONE` 视为「**subjective hypothesis**」，必须用外部断言（`--expect-url` / `--expect-title` / `--expect-text`）验证。

**README 承认/隐含的局限：**
- README **未见独立的 "Limitations" 章节**（这是一个缺口；相比之下 mini-jev / jevlike / kev 都有）。防护性表述散落在 harness 章节（如 DONE 只是 hypothesis）。
- 明确指出是对 Jev **范式**的「reverse engineering」，**不是**复现 TypeSafe 的权重或训练：「Jev is provided as a cloud API service **without publicly available model weights or internal implementation details**.」
- 溯源与致谢原文：「Inspired by [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast). Upstream MIT attribution and notices are preserved in [NOTICE](NOTICE). This project also draws inspiration and ideas from [openjev](https://github.com/TheoLeeCJ/openjev) and [Qwen-2.5-1B-RLCD](https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD).」
  → 注意 APUS 引用的是 **`TheoLeeCJ/openjev`**（SemIf 的旧名），即确认了改名事实。
- 有简体中文 README：`README.zh-CN.md`。

**第三方（媒体）验证状态：** 央广网、新华网、量子位、新浪、Sohu 均报道，**但报道内容为项目方供给的新闻稿口径**，未看到媒体独立复跑 benchmark。

---

### 2.6 `tamaratran/fast-jev-compaction`

| 字段 | 值 |
|---|---|
| URL | https://github.com/tamaratran/fast-jev-compaction |
| Stars | **5,376** |
| Forks | 295 |
| Open issues | **59** |
| Watchers | 12 |
| License | **MIT** |
| 创建 | 2026-09-17T05:57:20Z |
| 最近推送 | 2026-09-18T04:45:31Z |
| 语言 | TypeScript |
| 主页 | `""`（空串） |
| 体积 | 245 KB |

**性质：** **不是模型复现，是 Jev 的客户端应用。** Claude Code 的 context compaction 插件 + npm library。
**底座模型：** 无自有模型，调用 TypeSafe 云端 API（`baseUrl` 默认 `https://api.typesafe.ai/v1/systemone`，`model` 默认 `jev-latest`）。
**核心做法：**
- 不使用摘要。对每个非 pinned 的 `tool_use`/`tool_result` 发**两个 `noul` 问题**：call 是否该留、result 是否该逐字保留。
- 阈值：`keepThreshold` 默认 0.5；`keepResult ≥ threshold` → 全留；否则 `keepCall ≥ threshold` → 留 call、result 截断；否则整个删除。
- 状态拟合分阶段：tool inputs 截到 1000 → 200 → 60 字符；长文本 abridge 成 head+tail；旧消息折叠；仍不 fit 则 **throw**。
- 请求拆分：`maxRequestTokens` 默认 30,000（在 Jev 32k 请求上限下）；**同一完整 state 随每个请求重发**，请求并发、答案合并。
- token 估算**不用 tokenizer**：「a word per six letters, half a token per digit, ~one per other symbol」，标定到略高于 Jev 报告值。

**硬件：** N/A（云端 API）。
**HTTP server：** 无。
**是否声称校准：** README 明确**限定**：
> "**Calibration is at the request level**; **a probability is not a proof that a result is safe to delete.** The assistant can always re-run the tool."

**README 承认的局限（原文 Limitations 全文）：**
- "Only tool calls and results are candidates; text messages are never removed or shortened in the output (they are only abridged in the state Jev sees)."
- "Token sizes are **estimates from character counts, not a tokenizer**."
- "Calibration is at the request level; a probability is not a proof that a result is safe to delete."
- "The full state is repeated with every request, so a history near the state ceiling **costs one request per handful of questions**."

**其他：** Jev 失败/畸形答案/缺 key/无法 fit → **throw**，由调用方（或 Claude Code hook）决定 fallback。Claude Code function hooks 是**早期访问功能**（需 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`，Claude Code **2.1.274+**）。演示 app `demo/JevDemo` 是「scripted, **dramatized**」版本，「**It never calls the API**」。单测用 fake Jev，从不接触 TypeSafe。

---

### 2.7 `perixtar/jev-e2e`

| 字段 | 值 |
|---|---|
| URL | https://github.com/perixtar/jev-e2e |
| Stars | **3** |
| Forks | 0 |
| Open issues | 1 |
| License | **MIT** |
| 创建 | 2026-09-18T19:04:41Z |
| 最近推送 | 2026-09-19T10:34:32Z |
| 语言 | TypeScript |
| topics | `browser-automation`, `end-to-end-testing`, `jev`, `openrouter`, `playwright`, `typescript` |
| 体积 | 10,121 KB |

**性质：** Jev 应用（自然语言 Web E2E 测试），非模型复现。
**模型接入：** **经 OpenRouter**，默认 `typesafe/jev-1.13` 做 control selection，可选 `openai/gpt-4.1-mini` 解释 prose。**「Direct TypeSafe transport is not implemented.」** 用 `POST /api/alpha/decisions`。
**核心做法：** 可选 prose planner → 语义步骤 + 显式期望；Jev 从观测到的 controls/navigation 中选；Playwright 独立执行动作并检查期望；结果为 **PASS / FAIL / BLOCKED**。缺失证据或不支持的需求 → BLOCKED。保存的 flow 可**零模型调用重放**；目标失效时由 Jev 修复。
**硬件：** Node.js 22+，本地 Chromium（alpha）。
**HTTP server：** 有**本地 workbench**（`npm run ui`，默认 http://127.0.0.1:4007）。
**是否声称校准：** 未涉及。
**自报 eBay 实测（2026-09-18，经 OpenRouter，每模型 3 次尝试、轮换顺序、全新访客上下文、无重试/无替换模型/无丢弃失败）：**

| Model | Completed-case median | API cost / completed case (median) | PASS / attempts | Correct UI choices |
|---|---:|---:|---:|---:|
| **Jev 1.13** | 47.46 s | **$0.006678** | 1/3 | 30/31 |
| GPT-5.6 Luna | 61.99 s | $0.027704 | 2/3 | 32/32 |
| Claude Sonnet 5 | 78.62 s | $0.406216 | 1/3 | 19/19 |

**项目方自己的诚实边界（原文）：** "**Completed-case sample sizes are 1 / 2 / 1; these small, unequal samples do not establish a general accuracy ranking.**"；"Three attempts were blocked by eBay availability, and one by a detached-frame bug in the benchmark observer. The verifier stopped the incorrect choice before executing it."；"**It does not measure natural-language planning or the unmodified CLI's reliability on eBay.**"

**承认的局限：** alpha（CLI + workbench，仅 Chromium）；npm release 尚未发布；**不支持** native desktop/mobile apps、CAPTCHA、canvas、复杂 frames、支付流程、主观视觉判断；hosted infra 属后续阶段；**raw trace recording is not implemented**；可见应用文本会发给 OpenRouter，报告里可能残留无关页面内容。

---

### 2.8 `logicrw/awesome-jev-projects`

| 字段 | 值 |
|---|---|
| URL | https://github.com/logicrw/awesome-jev-projects |
| Stars | **240** |
| Forks | 20 |
| Open issues | 0 |
| License | **MIT** |
| 创建 | 2026-09-18T06:41:50Z |
| 最近推送 | 2026-09-21T02:26:03Z |
| 语言 | JavaScript |
| 主页 | https://logicrw.github.io/awesome-jev-projects/ |
| 体积 | 21,215 KB |
| topics | `ai-agents`, `awesome`, `awesome-list`, `decision-model`, `developer-tools`, `jev`, `jev-model`, `system-one`, `typesafe-ai` |

**性质：** 目录/雷达仓库（"source-backed open-source ecosystem radar, plain-language project discovery, and **automatic GitHub sync**"）。**不含模型代码。**
**规模：** README 220,176 bytes。可提取出 **60+ 个唯一 GitHub 仓库引用**（脚本 `grep -oE 'github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+' | sort -u`）。抽样：`AbdelStark/jev-benchmarks`, `AboveColin/HA-Jev`, `BerriAI/litellm`, `ComposioHQ/composio`, `0xNatoshi/jev-codex-router`, `GhalebDweikat/winnow`, `Kiln-AI/jev_jsonschema`, `Bodila51/grok-bot-jev` 等。
**局限：** 是**自动同步**的索引，非人工审核；用于发现线索，不作为质量或存在性证据。

---

### 2.9 `yibie/awesome-jev`

| 字段 | 值 |
|---|---|
| URL | https://github.com/yibie/awesome-jev |
| Stars | **673** |
| Forks | 98 |
| Open issues | 3 |
| License | **null（无许可证）** |
| 创建 | 2026-09-17T14:23:21Z |
| 最近推送 | 2026-09-21T01:52:38Z |
| 语言 | Python |
| topics | `awesome`, `awesome-list`, `jev`, `llm` |
| 主页 | `""`（空串） |

**性质：** 目录仓库，由 `scripts/build-readme.py` 从 category 文件聚合生成 README。
**收录规模（README 自报，按 category）：**

| Category | Entries |
|---|---:|
| Classification & Routing | 24 |
| Verification & Guardrails | 22 |
| Scoring & Ranking | 20 |
| Agent Decisions | 31 |
| Data Labeling & Curation | 5 |
| Evaluation & Benchmarking | 16 |
| Calibration & Research | 22 |
| Infra / SDKs / Integrations | 43 |
| Game & Simulation | 10 |
| Finance & Trading | 4 |
| Compliance & Legal | 1 |
| Content Moderation | 4 |
| Related Practices / Discussions | 54 |
| Scientific Pipelines | 0（"still being seeded"） |

**这个仓库对本报告最有价值的地方 —— 它是唯一明确写出「批量提交不可信」警告的来源。README 原文：**

> [!WARNING]
> **A listing is not an endorsement.** This project applies *inclusion* rules only... It does **not** review code quality, security, maturity, or whether a project runs at all.
>
> **Treat same-day bulk submissions with particular care.** Several repositories published together by one author, sharing a scaffold and a thin commit history, can satisfy every inclusion rule and still be unproven. **Volume is not evidence of quality.**

**其列出的自查清单（原文）：**

| Check | Why it matters |
|---|---|
| Does the code actually call the Jev API? | "An entry can read well on a README alone." |
| Is there a runnable check? | "**No check means no evidence that it works.**" |
| Do the numbers have a source? | "We strip claims we cannot verify, but the project page itself may still carry them." |
| How much of the repository is code? | "**Some projects are mostly prompt documents.**" |
| Is there a license? | "A few entries have none, which limits reuse and redistribution." |

**许可证缺口：** `yibie/awesome-jev` 本身 **license = null**。

---

## 3. 本次新发现的重要复现项目（非任务点名，但 star/完整度靠前）

> 排序按 star 降序。**全部为 gh api 于 2026-09-21T04:15Z 的返回值。**

### 3.1 `browser-use/jev-ultrafast`（12,586★，全生态最高）

| 字段 | 值 |
|---|---|
| URL | https://github.com/browser-use/jev-ultrafast |
| Stars | **12,586** |
| Forks | 783 |
| Open issues | 87 |
| Watchers | 31 |
| License | **MIT** |
| 创建 | 2026-09-16T21:30:12Z |
| 最近推送 | 2026-09-18T16:28:35Z |
| 语言 | Python |
| description | **"i. am. speed."** |
| 主页 | https://browser-use.com |

**性质：** Jev **的客户端应用**（不是模型复现）——Browser Use 官方项目，调 TypeSafe API。
**核心做法（README 原文）：** 动态、带索引的 action space。一次 observation 产出 element table；**operation head + target head 共享同一状态，在一次 TypeSafe 请求里同时返回**（"Two decisions, **one network round trip**"）。target questions 是 speculative 的——只有 operation 是 CLICK 时 `click_target` 才执行。operations：`CLICK`, `TYPE_TEXT`, `SELECT`, `SCROLL_UP`, `SCROLL_DOWN`, `WAIT`, `DONE`, `BLOCKED`。**只有 `TYPE_TEXT` 才调用小 LLM 生成文本**（示例配置用 OpenRouter 的 `inception/mercury-2.5`，reasoning disabled）。
**硬件：** 本地 Chrome + Browser Harness（`uv run browser-harness --doctor`）；需要 `TYPESAFE_API_KEY` + `TEXT_MODEL_API_KEY`。
**HTTP server：** 有本地 inspector（http://127.0.0.1:8766）。
**是否声称校准：** 有 operation/target probabilities 展示，但**未声称 calibrated**。

**自报数字：**
- **Zürich → London on Google Flights in 7.1 秒**（实际测得 video 为 **7,073 ms**），含真实文本生成与加载等待，1× 播放。
- 六次交替运行（相同模型与设置），两版本都 **3/3** 通过；**median task time 9.450 s → 7.092 s（25% 下降）**；**median browser protocol calls 1,092 → 101**。
- 同一 policy：Wikipedia 文章 **2.798 s**；本地酒店搜索/筛选 **1.896 s**。

**承认的局限（原文）：**
> "This is **three repeats of one task on one browser profile, not a general reliability benchmark**."
> "A `DONE` choice **still requires independent outcome verification**."
> "The DOM reader handles common HTML and ARIA controls, **not the full accessible-name specification**. **Shadow roots, frames, canvas, uploads, pop-up tabs, nested scrolling, and arbitrary keyboard widgets remain outside this MVP.** Owned tabs share the existing Chrome profile."

**第三方：** 被 APUS README 明确致敬并作为灵感来源。

---

### 3.2 `TianyuCodings/NanoJev`（1,520★）

| 字段 | 值 |
|---|---|
| URL | https://github.com/TianyuCodings/NanoJev |
| Stars | **1,520** |
| Forks | 180 |
| Open issues | 6 |
| License | **MIT** |
| 创建 | 2026-09-17T16:08:30Z |
| 最近推送 | 2026-09-20T11:13:01Z |
| 语言 | Python |
| 体积 | 64,035 KB（**最大的复现仓库之一**） |

**底座模型：** **Qwen3-0.6B** + decision heads，**单一 checkpoint 跨四个游戏任务复用**。
**权重量化：** HF `C-Tianyu/NanoJev`，release tag `unified-games-v1`（= 训练 run `hard_lr1e5` 的 step-400 checkpoint）；数据集 HF `C-Tianyu/NanoJev-Data`。**模型与数据集公开，无需登录即可下载。**
**核心做法（README 原文）：**
- **Parallel decisions**：batch 独立 states/questions/candidate paths 进一次 backbone 前向。
- **Dynamic candidates**：Choice 对 2–255 个候选返回分布（shared scoring head）。
- **Boolean** 用 sigmoid；**Score** 返回 2–10 个有序 level 的概率分布与期望值。
- Choice 用 **set attention + softmax**。
- 「direct probabilities: rank, select or sample actions **without generating answer tokens**」。
**硬件：** README quick start 用 CUDA（`scripts/serve_decisions.py`，带 `--disable-native-triton`）。
**HTTP server：** **有** —— `POST http://127.0.0.1:8765/api/evaluate`，服务加载模型一次。
**是否声称校准：** 训练数据有独立 **calibration split**；但**未给出 ECE 数字**。

**自报结果（held-out gameplay，274-case 完整 test set，同一 observation interface / candidate actions / seeded epsilon-greedy controller）：**

| Model | Maze | Snake | Basic | Predict Position |
|---|---:|---:|---:|---:|
| **NanoJev** | 4/10 | 8/8 | **128/128** | **27/128** |
| Jev | 7/10 | 8/8 | 56/128 | 11/128 |
| Untuned Qwen3-0.6B | 2/10 | 0/8 | 56/128 | 11/128 |

> 注意：**在 Maze 上 NanoJev（4/10）反而输给 Jev（7/10）**，README 保留了这一行。
> Test + OOD 共 **548 cases per model**；「Every evaluated trajectory passes **independent simulator replay**」。

其他：数据集 **18,760 decision questions per target variant**（含 16,333 ViZDoom questions）；Predict Position 含 **896 expert episodes / 17,498 recorded decisions**。混合训练权重 Maze/Snake/Basic/PredictPosition = **1/3, 1/3, 1/6, 1/6**。
**Roadmap 未完成项（即当前局限）：** RLCD post-training 未做；shared-prefix inference 未做；更大 candidate batch 未做；结构化输入支持未做。

---

### 3.3 `jaredpalmer/kev`（1,162★）

| 字段 | 值 |
|---|---|
| URL | https://github.com/jaredpalmer/kev |
| Stars | **1,162** |
| Forks | 70 |
| Open issues | 4 |
| License | **Apache-2.0** |
| 创建 | 2026-09-17T20:49:39Z |
| 最近推送 | 2026-09-21T02:49:06Z（活跃） |
| 语言 | Python |
| topics | `decision-model`, `jev`, `qwen3` |
| 体积 | 23,311 KB |

**底座模型：** **Qwen3.5** 家族的 0.8B / 4B / 9B（HF collection `jaredpalmer/kev`）；上一代是 Qwen3（`jaredpalmer/kev-4b@qwen3`、Kev-0.6B、Kev-8B）。
**训练依据：** README 明确指向 **https://archerhume.com/posts/jevs-architecture-unmasked** 描述的架构。
**核心做法：** 「Questions **share the input text but can't read each other**」（问题隔离）。同时支持 `noul` / `choice` / `score` 在同一请求里。训练：`decision-v7` 数据集（10,000 例来自十个公开数据集 + 896 生成的 policy 例 + 1,680 例来自 60 个生成规则结构），2 epochs，**LoRA rank 16 + cross-entropy**；lr = 1e-4 (0.8B) / 5e-5 (4B, 9B)。Qwen3.5 基座 adapter 覆盖 DeltaNet projections。
**API 兼容：** 「The API matches TypeSafe's System One, so you can **point their Python SDK at your local server**」。
**硬件：** CUDA（H100 + flash-linear-attention 时五问请求「tens of milliseconds」）与 Apple Silicon。
**HTTP server：** **有** —— `python -m kev.serve --run jaredpalmer/kev-4b --port 8009`，端点 `POST /v1/systemone`。
**是否声称校准：** **明确否认**（见局限第 1 条）。

**Apple Silicon 服务性能（bf16 on M5，五问 × 三选项，~230-token state）：**

| Model | Time | 上一代同请求 |
|---|---:|---:|
| Kev-0.8B | 329 ms | Kev-0.6B (Qwen3): 123 ms |
| Kev-4B | 779 ms | Kev-4B (Qwen3): 174 ms |
| Kev-9B | ≈ 2 s | Kev-8B (Qwen3): ≈ 300 ms |

> 原文：*"**On Apple Silicon there are no fast kernels for the DeltaNet layers**, so PyTorch runs reference code... If you serve on a Mac and need low latency, **use the Qwen3 models for now**. An MLX backend for the Qwen3.5 models is the next planned change."*
> 前缀缓存优化：重复 772-token state，Kev-4B (Qwen3) **242 ms 而非 861 ms**。

**README 承认的局限（原文全列）：**
- "**Probabilities aren't well calibrated on new sources.** On the new-source development set, **Kev-4B assigns at least 0.9 probability to a wrong answer on 8.2% of questions** (Kev-9B: 7.5%). Test it on your own data before choosing a probability threshold."
- "**Fine-tuning can make the base model worse** at individual tasks. Date arithmetic is the clearest case: the untrained Qwen3.5-9B base gets 0.82 on the `deadline` policy questions and Kev-9B gets 0.72, because **training erodes the skill**."
- "Knowledge questions (**MMLU 0.74 vs Jev 0.90**) are the other large gap."
- "The current models are **slow on Apple Silicon**."
- "**Changing option order can change an answer.** Question isolation doesn't prevent this."
- "Training uses at most 384 state tokens and 1,024 tokens for the state plus one question. Serving allows 8,192 tokens... **longer context wasn't covered by training**."
- "The server handles **one request at a time**... doesn't batch requests from different callers."

**额外的诚实性证据：** bf16 vs fp32 在 24 条 new-source 记录上概率差至多 0.017，「**That is a small check, not a guarantee for every input**」。有 web playground（可测 option order 影响、packed vs separate、问题隔离、fake delimiter tokens）和象棋 demo。

---

### 3.4 `wfzyx/von`（241★）

| 字段 | 值 |
|---|---|
| URL | https://github.com/wfzyx/von |
| Stars | **241** |
| Forks | 22 |
| Open issues | 2 |
| License | **Apache-2.0** |
| 创建 | 2026-09-18T05:03:47Z |
| 最近推送 | 2026-09-21T02:03:12Z |
| 语言 | Python |
| 默认分支 | **master** |
| topics | `decision-model`, `jev`, `machine-learning`, `python`, `rlcd`, `system-one`, `typesafe` |

**底座模型：** **ModernBERT-Large（395M params，1.5 GB）** + decision head。权重 HF `wfzyx/von-1.0`。
**核心做法：** 非自回归、并行；「Operates entirely **in-process or via an HTTP server**」；「evaluates arbitrary discrete and continuous criteria directly over input state in **a single forward pass without autoregressive text generation**」。
**三原语实现：**
- Choice：$P(c_k|S,Q) = \exp(z_k/T) / \sum_j \exp(z_j/T)$，$T = 1.1692$，Confidence = $P(c_{(1)}) - P(c_{(2)})$
- Noul：$P(y=1|S,Q) \in [0,1]$，用**双正负 criteria framing** 抵消词法否定偏差
- Score：$\mathbb{E}[L|S,Q] = \sum_l l \cdot P(l|S,Q)$

**训练/校准方法（RLCD）：**
- 复合损失 $\mathcal{L}_{\text{RLCD}} = \mathcal{L}_{\text{CE}} + \lambda \mathcal{L}_{\text{Brier}}$，$\lambda = 0.5$
- 训练集：**250,000 class-balanced examples**，来自 ANLI (Rounds 1–3) / WANLI / MultiNLI & SNLI（README 另有一处写 "~290,000-example balanced multi-domain corpus" —— **仓库内两个数字不一致**）
- 温度标定：bounded NLL 最小化，收敛于 **T = 1.1692**；README 称「yielding **near-ideal expected calibration error (ECE)**」但**未给出 ECE 数字**
- 同一 README 的 Choice 公式处又写 **T = 1.1692**，但 Overview 处写 $T = 1.0367$ —— **仓库内 temperature 数字自相矛盾**

**硬件：** NVIDIA CUDA、AMD ROCm (Linux)、Apple Silicon MPS、多线程 CPU。
**HTTP server：** **有** —— `von serve --host 0.0.0.0 --port 8000`，**声称完全兼容 TypeSafe `/v1/systemone` 规范**。有 Python SDK (`von-sdk`) 与 TypeScript SDK (`von-sdk` on npm/bun)。

**自报 benchmark：**

| Model / Architecture | Size | v2 Macro Acc (49 tasks) | Choice Macro (20 tasks) | ViZDoom Kills (Defend Center) | GPU Latency | Hosting |
|---|---:|---:|---:|---:|---:|---|
| **TypeSafe Jev** (`typesafe/jev-1.13`) | Proprietary MoE | **96.6%** | **96.8%** | 5.62 kills | ~115 ms (API) | Cloud Only ($0.042/1M tokens) |
| **Von OptionMarker (Current)** | **395M (1.5 GB)** | **71.5%** | **83.4%** | **9.38 kills** | **~18 ms** | Local / Free (Apache 2.0) |
| GLiNER2 (`fastino/gliner2-large-v1`) | ~300M | 68.4% | 76.2% | N/A | ~93 ms | Local / Free |
| Finetuned Qwen3.5 (4B Causal) | 4B | ~63.5% | 71.0% | 3.62 kills | ~144 ms | Local / Open |
| Laya (`convaiinnovations/laya`) | 421M | 58.3% | 66.8% | 1.25 kills | ~16 ms | Local / Free |

> **重要：** Von 在 v2 macro accuracy 上（71.5%）**大幅落后** Jev（96.6%），README 自己列出了这一行；只在 ViZDoom kills 上超过（9.38 vs 5.62）。

**承认的局限（README 的 Domain Generalization 章节，原文要点）：**
- 「Unlike generative LLMs that synthesize paragraphs, Von is an **in-context semantic verifier**.」
- 「**Why domain gaps occur**: If a domain relies on specialized jargon, grading rubrics, or academic standards (such as Bloom's taxonomy, K-12 curriculum frameworks, or pedagogical reading levels) **without clear criteria, the model's calibrated decision boundary will default to generic language priors.**」
- 修复建议：给**描述性 criteria** 而非裸标签（README 给了具体反例/正例）。
- 引用文献 `RLCD` 的 arXiv 编号为 `arXiv:2503.23303`，标题 "Reinforcement Learning with Calibration Distribution"，作者 `DeepMostInnovations` —— 本次**未核实该 arXiv 条目是否真实存在**。

---

### 3.5 `ekzhang/openjev-sglang`（239★）

| 字段 | 值 |
|---|---|
| URL | https://github.com/ekzhang/openjev-sglang |
| Stars | **239** |
| Forks | 27 |
| Open issues | 3 |
| License | **null（无许可证）** |
| 创建 | 2026-09-17T18:11:49Z |
| 最近推送 | 2026-09-18T15:46:43Z |
| 语言 | Python |
| topics | `jev`, `llm`, `structured-generation`, `systemone` |
| 主页 | https://ekzhang--openjev-sglang-openjev.us-west.modal.direct |

**底座模型：** **Qwen3.6-35B-A3B on SGLang**。
**核心做法：** 实现 TypeSafe/Jev HTTP API 的 server。每个 container 一张 **B200**，跑 SGLang **0.5.19 的 Rust frontend**，开 **radix caching** 与 **breakable prefill CUDA graphs**。独立 Python API 进程用 FastAPI + uvloop + Rust-backed HF tokenizer + pooled async HTTP 连接。描述里写 "prefill-only"。
**硬件：** Modal 上的 B200（`compute_region=["us-west","us-central","us"]`，无显式 container 上限，5 分钟空闲后 scale to zero）。
**HTTP server：** **有** —— `https://...us-west.modal.direct`，`POST /v1/systemone`；有 `openjev smoke <URL>` 冒烟测试（覆盖三种 answer 类型、64-answer question、基础语义 sanity、拒绝 65 answers，报告 startup wait / inference latency / cache usage）。
**是否声称校准：** 未涉及。
**已实现 / 已知坑（README 原文技术细节）：**
- 规避 SGLang bug #34719（mixed-logprob batch crash）：cache warmup 也请求一个未使用的 token probability，使 warmup 与 scoring 请求 batch 兼容，**无需给 SGLang 打补丁**。
- Scaled-to-zero 时 Server 返回 **503**；smoke 命令会重试启动响应。
- 若 SGLang 异常退出，API 也退出；Modal launcher 监视 API 并退出 container，**避免留下 HTTP 活着但推理后端已死的进程**。
- 模型权重持久化在 Modal Volume `openjev-huggingface`，与 SGLang tuning cache、Triton compilation cache 一起；**CUDA graph capture 每次启动仍会跑**。
- **无 LICENSE 文件**（license = null）—— 这是采用风险点。

---

### 3.6 `featherless-ai/simple-jev`（404★）

| 字段 | 值 |
|---|---|
| URL | https://github.com/featherless-ai/simple-jev |
| Stars | **404** |
| Forks | 42 |
| Open issues | 2 |
| License | **null（无许可证）** |
| 创建 | 2026-09-18T09:52:15Z |
| 最近推送 | 2026-09-20T08:18:21Z |
| 语言 | Python |
| description | "Turn any open model into a classifier/jev endpoint" |

**底座模型（可选多后端）：**
- `Qwen/Qwen3.5-0.8B`（CPU 示例，float32）
- `google/gemma-4-26B-A4B-it`（CUDA bf16 示例）
- `convaiinnovations/laya`（`--backend laya`，`--subfolder typed-decisions`，native encoder backend）

**核心做法（README 原文）：** 「Simple Jev **reads the model's next-token logits for each question** and builds a JSON response containing choices, rubric scores, or truth/support judgments. **The model does not generate a JSON completion: the server constructs the response from the scores.**」
实现要点：
1. 共享 prompt builder 生成一致的分类器指令 + 每问一个 scoring branch
2. HF server 按模型原生 chat format 渲染
3. **「It evaluates the exact common token prefix once and reuses that prefix's KV cache across batches of question suffixes.」**
4. 读 allowed answer labels 的 next-token logits，共享 scoring 代码归一化并构造 JSON

**硬件：** CPU（0.8B）、NVIDIA CUDA/ROCm（26B MoE）。
**HTTP server：** **有** —— 监听 `http://127.0.0.1:8000`，`POST /v1/classifier`（**`/v1/systemone` 是 `/v1/classifier` 的 alias**），`GET /health`，`/docs` 交互式 API 文档。有**公开 demo API**（`https://simple-jev-demo-api.featherless.ai/v1/`，无需登录/API key，**2k token 上下文上限，限速 2 RPS**）。
**是否声称校准：** **明确否认**，原文：
> "Choice and score confidence is **the largest probability among their allowed labels**. **These distributions, and the Noul value, are not calibrated probabilities of correctness.**"
另：「A valid response structure **does not guarantee a correct decision**.」
**承认的局限：** 「**It does not reproduce TypeSafe's model architecture or training, or establish equivalent accuracy, calibration, or speed.**」；「**Cache reuse currently lasts only for a single request.**」；README 自标 "**a launch example, not a verified full-size Gemma benchmark**"；Laya backend 的 2× RoPE 插值是实验性的，「**does not establish accuracy or calibration beyond the checkpoint's training length**」。

---

### 3.7 `razorback16/openjev`（220★）

| 字段 | 值 |
|---|---|
| URL | https://github.com/razorback16/openjev |
| Stars | **220** |
| Forks | 20 |
| Open issues | 2 |
| License | **Apache-2.0** |
| 创建 | 2026-09-18T09:15:33Z |
| 最近推送 | 2026-09-20T22:21:28Z |
| 语言 | Python |
| 主页 | **https://codiv.ai** |

**底座模型：** **DiffusionGemma 26B-A4B**（`nvidia/diffusiongemma-26B-A4B-it-NVFP4`，Apache-2.0）。
**核心做法：** 两种跑法 —— vLLM on NVIDIA GPU，或 Apple Silicon 上 in-process MLX。「It reads the answers straight off the model's probabilities. It generates no text and parses nothing, **so an answer cannot go off-schema.**」**Questions can also ask about images**（多模态）。
**API 兼容：** 「It runs the same wire API as TypeSafe's Jev, so **their SDKs work against it unchanged.**」
**HTTP server：** **有**，且**有托管免费实例**：Codiv `https://api.codiv.ai/v1/systemone`（注册送 100M input tokens，无需信用卡）。vLLM backend 还额外在 OpenAI 兼容的 `/v1/chat/completions` 上提供文本生成，**不额外占 GPU 内存**。
**是否声称校准：** 声称 "calibrated"（描述语），**但未给出 ECE 数字**。
**声明：** "OpenJev is an independent project. It is **not affiliated with or endorsed by TypeSafe AI**."

---

### 3.8 `ikermoel/open-alternative-jev`（38★）—— 诚实性最好的 benchmark 之一

| 字段 | 值 |
|---|---|
| URL | https://github.com/ikermoel/open-alternative-jev |
| Stars | **38** |
| Forks | 8 |
| Open issues | 2 |
| License | **Apache-2.0** |
| 创建 | 2026-09-18T05:20:56Z |
| 最近推送 | 2026-09-21T03:37:00Z |
| 语言 | Python |
| 主页 | https://huggingface.co/spaces/IkerMoel/open-alternative-jev |
| topics | `calibration`, `jev`, `logprobs`, `open-jev`, `system-one`, `typed-decisions`, `vllm`, `transformers` 等 18 个 |
| 包名 | pip `open-alternative-jev`，import `so1` |

**底座模型：** **任何 open-weights LLM**。benchmark 用 `Qwen/Qwen3.6-27B`（bitsandbytes 8-bit，H200 MIG 35GB slice，HF Transformers）；library 对比用 `Qwen3.5-4B`（BF16）。
**核心做法：** 「no text is generated: the model reads the state once and every question is answered from the next-token distribution at its own position, restricted to the options you give.」**Packing**：共享 state 只写一次，多问题打包进一个序列。
**后端：** HF Transformers + **vLLM**（vLLM 用 prefix cache + `allowed_token_ids` / `prompt_logprobs`）。
**HTTP server：** **明确没有** —— 原文：「This replaces the library, **not the endpoint**: it is a Python package you call in-process, and **there is no HTTP server or drop-in API for the official Jev SDK**.」
**是否声称校准：** **是，给出了可复现的 ECE 数字。**

**自报结果：**

RACE-H，250 passages × 4 questions (n = 1000)，Qwen3.6-27B：

| Mode | Accuracy | Questions/s | Tokens processed |
|---|---:|---:|---:|
| A: one question per forward | 92.6 % | 1.66 | 468,583 |
| B: batch of 4 (padding) | 92.8 % | 2.00 | 481,924 |
| **Open Alternative to Jev** (packed) | **92.9 %** | **4.55** | **186,898** |

MMLU，1200 questions，无 shared state：

| Mode | Accuracy | Questions/s |
|---|---:|---:|
| A | 84.2 % | 3.10 |
| B（batch 3） | 83.8 % | 3.88 |
| packed 3 | 84.0 % | 5.44 |
| packed 6 | 84.9 % | 6.21 |
| packed 12 | 84.2 % | 6.71 |

**校准（ECE）：** 温度缩放单一标量（一半拟合、一半评估）：**MMLU 5.4% → 2.1%**；**RACE-H 2.8% → 1.1%**。Raw confidence 约高 5 个点（mean confidence 0.90 vs accuracy 0.84 on MMLU）。RACE-H packed 本来就接近校准（T = 1.0–1.1），scaling 无帮助。

**四个 "correction/honesty" 明文（这是本报告最有价值的可靠性证据之一）：**
1. **自我纠错：** 「**The correction that made this README honest.** Our first pilot reported "1.4x faster than batching" on MMLU. Regressing forward time on token counts showed that B and C cost **exactly the same per token (0.96 vs 0.97 ms)** and that **the whole difference was padding waste in the batch**. We kept the pilot and the analysis...」
2. **干扰效应：** 「Later questions in a packed sequence can attend to earlier questions and to the placeholders between them.」对照噪声底：同 prompt 单独跑、右 padding 到固定长度也会改变 **2.7%** 答案（纯 kernel numerics）；**packing 改变 6–9%**。改变是对称的，聚合精度不掉，但**单条决策会因"伴随哪些问题、什么顺序"而不同**（轮转顺序改变 8% MMLU 答案、2.4% RACE-H 答案）。建议需要答案级稳定就用 `mode="separate"`。
3. **packing 对小模型是负收益：** 「On the 4B model, **packing costs 2.8 points** (11 of 400 answers), where the 27B lost nothing. **Interference grows as the model shrinks.**」
4. **vLLM 上 separate 最快：** 「Prefix caching already computes the shared passage once, and **constrained one-token generation is cheaper than extracting top-k `prompt_logprobs` at every position.`** Packing's throughput advantage is **a property of engines without a prefix cache, such as plain Transformers.**」

两后端一致性：separate 模式下 vLLM 与 Transformers **99.8%** 选同一答案，概率平均绝对差 **0.003**。

**硬件：** CUDA GPU（H200 MIG / 单 H200）；CPU 可跑小模型（测试套件用 Qwen2.5-0.5B 在笔记本上跑）。有 HF Space 在线 demo（Qwen3.5-4B，免安装）。

**Live demo 模型：** HF Space `IkerMoel/open-alternative-jev`。

---

### 3.9 `Heman10x-NGU/openJev-verdict-2.0`（205★）与 `Heman10x-NGU/Verdict-open-jev`（48★）

#### openJev-verdict-2.0

| 字段 | 值 |
|---|---|
| URL | https://github.com/Heman10x-NGU/openJev-verdict-2.0 |
| Stars | **205** |
| Forks | 28 |
| License | **NOASSERTION**（GitHub 无法识别；README badge 写 Apache 2.0） |
| 创建 | 2026-09-19T12:14:46Z |
| 最近推送 | 2026-09-20T14:54:40Z |
| 语言 | Python |
| 主页 | https://heman10x-ngu.github.io/openJev-verdict-2.0/ |
| topics（20 个） | `calibration`, `brier-score`, `modernbert`, `non-autoregressive`, `onnx`, `webgpu`, `rlcd`, `selective-prediction`, `uncertainty-quantification`, `system-one`, `typed-decisions`, `typesafe-ai`, `jev` 等 |

**两个模型（README 明确区分）：**
1. **Verdict**（151M，在 **JevBench** 上评测）——基于 ModernBERT-base + GLiClass。公开 checkpoint `heman10x/rlcd-modernbert-151m`（已更新到 v1.4）。
2. **Verdict 2.0** —— 专为 typed software workflows 的架构，在 **`LocalLLaMA/typed-decisions`** 上评测。权重以 **Git LFS pointer 形式**存在于 `artifacts/verdict2-base/model.pt`。数字由 `verdict2/evaluate.py` 对其 audited test receipt（`reports/verdict2_base_test.json`）产生。

**核心做法：** 非自回归 single pass + **dual-channel calibration**（专用 confidence head）。有 **in-browser WebGPU engine**（零云端边缘就绪）。ONNX 导出。

**自报结果（2,000 held-out enterprise decisions）：**
- **77.10% accuracy**（称 ahead of Laya's **76.60%** 与 Jev's **72.70%**）
- **Brier 0.0636**（称 best overall）
- **ECE 1.44%**（dedicated confidence head）
- 「2.8x fewer parameters, fine-tuned in **8.8 hours on a budget consumer laptop GPU**」
- 延迟 **~20–25 ms / decision**

**v1.4 inference engine 修复（说明是推理修复不是重训，"weights are byte-identical to the published checkpoint"）——**

| Metric / slice | Before (v1.0) | After (v1.4) | Change |
|---|---:|---:|---|
| Easy tier accuracy (48 tasks) | 85.4% | 87.5% | +2.1% |
| Standard tier accuracy (72 tasks) | 62.5% | 69.4% | +6.9% |
| Hard tier accuracy (111 tasks) | 36.9% | 36.9% | 0.0% |
| Hard-tier ECE | 0.298 | 0.118 | **−0.180 (−60.4%)** |
| Probability fidelity | 62.8 | 72.8 | +10.0 pts |

三个修复：(1) calibrator 自动加载 + 移除 5-option scope 限制；(2) **NLI sentence templating**（candidate labels 用 `It is {description}` hypothesis framing）；(3) **context budget 从 1024 砍到 512 tokens**（因为权重是在 <71 token 的 state 上训练的）。
**这三点本身就是对该项目早期版本缺陷的公开承认。**

**注意：** repository 里同时存在 `Heman10x-NGU/Verdict-open-jev`（48★，Apache-2.0 badge 但 license NOASSERTION，创建 2026-09-17T18:01:41Z，pushed 2026-09-20T14:54:34Z）—— 描述为 "Non-autoregressive decision engine on ModernBERT (151M) with calibrated uncertainty (RLCD), TypeSafe AI Jev benchmark audit, and in-browser WebGPU playground"。**两个仓库关系：同一作者的同源项目（v1 与 2.0），不是独立复现。**

**`openJev-verdict-2.0` 的 benchmark 数字（77.10% / 0.0636 Brier / 0.0144 ECE）目前只在项目方自己的 test receipt 上，本次未找到第三方独立复跑。**

---

### 3.10 其他值得记录的发现

| 仓库 | Stars | License | 底座模型 | 核心做法 / 备注 | created |
|---|---:|---|---|---|---|
| `Mapika/decider` | **163** | Apache-2.0 | `Qwen/Qwen3.5-2B-Base`（v10）+ `Qwen/Qwen3.5-35B-A3B-Base`（v1）+ `Qwen3.5-0.8B-Base` + vision 版 | 一前向出每问分布，**无解码、无解析**；最多 255 options、32k tokens。v10 加了 384 步 calibration-aware RL。live browser 93%（v8 83%）；belief 0.22 nats 高于 exact laws（v8 0.47）；JevBench hard **0.676**；Bespoke macro 0.774。HF 权重 `Mapika/decider-2b` 等 | 2026-09-16T07:15:09Z |
| `bespokelabsai/nimble` | **1,215** | **null** | `Qwen/Qwen3.5-9B` + LoRA（只训 answer tokens） | "Data, Model, Recipe for an open Jev"。**「we did not distill from Jev」**。324 held-out：Nimble-9B 匹配 reference labels **90.1%** vs base model **66.4%** vs **Jev 1.13.0 93.2%**。serving「reads the prompt once and then scores one answer token per question」。HF `bespokelabs/Bespoke-Nimble-9B`。「built in one day, expect rough edges」 | 2026-09-18T09:07:48Z |
| `intikhab49/open-jev-typed-decision-engine` | 24 | Apache-2.0 | 150M encoder（ModernBERT / ONNX） | 「**0.697 vs Jev's 0.727, 2.5× better calibrated, 4× faster, $0**」；Colab 免费 T4 **<30 分钟**训完。**重要的方法论文本：**「TypeSafe does not publish Jev's parameter count... **Any size comparison you see, including here, is inference from price and latency rather than a disclosed figure.**」 | 2026-09-19T14:26:31Z |
| `fstandhartinger/jevbench` | 31 | MIT | N/A（benchmark） | **JevBench v1.2.3**，Benchmark Heaven 自建 benchmark，非 TypeSafe 关联。**JevBench Score = Intelligence / Calibration / Speed / Cost 各 25%，几何平均**。校准项：hard tier ECE + 对 exact gold distribution 的 fidelity（**label-only 系统记 0 分**）。Cost 列口径是 **$ / 1,000 decisions，不是 per 1,000 tokens**；Jev 1.13.0 平均每 decision 读 **950 input tokens**，@$0.042/1M → **$0.0399 / 1,000 decisions**。534 个 v1.2 decisions。已承认组合实验（confidence cascades / committees / best-of-n）**都没改变排名** | 2026-09-19T07:07:36Z |
| `rorshopping/jev-on-a-laptop` | 22 | NOASSERTION | `harshatheg/Qwen-2.5-1B-RLCD`（clone，not vendored）+ Qwen2.5-1.5B-Instruct-4bit | **最清晰的 KV-cache 广播示意图**：context+schema → prefill 一次 → KV cache → **broadcast ×N fields** → 一次 batched forward → slice logits → softmax。主张「**a 1.5B model that cannot reliably write 28-field JSON can still make 28 schema-valid decisions in ~0.4 s**」。16 GB M5 MacBook Air 上测三种尺寸。**「documented what's real vs. marketing」**。另有 `rorshopping/parallel-decisions`（有 `GPU_SETUP.md`） | 2026-09-16T09:21:53Z |
| `sarvam-jev` (`SAGAR-TAMANG`) | 38 | **null** | sarvam-1（Indic LLM） | 「Generation-free typed decisions on Indic LLMs. An open Jev-style inference engine on sarvam-1: **constrained logit readout instead of autoregressive JSON**。Runs **client-side in the browser**.」 | 2026-09-18T06:42:31Z |
| `siliconkernel/vllm-jev-decison` | 8 | MIT | vLLM 后端任意模型 | 「Classification-only typed decisions for vLLM: finite-schema candidate scoring, probabilities, and abstention. **No generative fallback.**」 | 2026-09-18T01:20:58Z |
| `0xBakeer/arbiter` | 14 | MIT | Laya 或自带模型 | 「Serve typed-decision (System 1) models — Laya or your own — on NVIDIA GPUs or Apple Silicon, with a **Jev-compatible API** and coding-agent integrations」 | 2026-09-20T04:45:28Z |
| `deepanwadhwa/OpenDecision` | 42 | Apache-2.0 | NLI 模型 | 「OpenDecision is an open-source semantic decision engine like typesafe's jev.」topics: `nli`, `systemone`, `typesafe-ai` | 2026-09-17T21:28:58Z |
| `akash-kamat/system-one-gemma` | 3 | **null** | **Gemma 3 270M** + scoring head | 「calibrated decisions in a single forward pass. No text generation.」**体积最小的复现之一（270M）** | 2026-09-17T14:15:31Z |
| `abhishek085/open-spark-jev` | 7 | Apache-2.0 | Qwen3 | 「inspired by TypeSafe's Jev and System One - built on Qwen3 for **NVIDIA DGX Spark**」 | 2026-09-20T19:39:22Z |
| `capitaharlock/jev-clone` | 0 | Apache-2.0 | — | 「local System One decision model ... dynamic options, **shared-state inference and zero autoregressive decoding**. Runs on **Apple Silicon and CUDA**.」**仓库语言为 null（本次未核实是否真有代码）** | 2026-09-19T17:47:44Z |

---

## 4. 专项对比：核心做法归类

| 仓库 | 单次前向读 option token logits | 受限 softmax | KV-cache 广播 / prefix reuse | 跳过自回归解码 | 动态候选（运行时定义选项） | 有 head 训练 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `TheoLeeCJ/SemIf` | ✓ | ✓（direct mode） | ✓（shared mode，prefill once → parallel） | ✓ | ✓（criteria+options 随请求到达） | ✗（frozen 模型） |
| `r-ms/mini-jev` | ✓（读 letter logits） | ✓ | ✓（shared prefix；KV cache 复用） | ✓（closed-choice 字段）；字符串/数字仍生成 | ✓（schema 随请求） | ✗（frozen） |
| `vinnylarouge/jevlike` | ✗（自有 option-attention head） | ✓（softmax across options） | ✗ | ✓ | ✓（每行 option 数可不同，≥2） | ✓（从零训 scorer head） |
| `bnsd55/jevmlx` | ✓ | ✓（restricted softmax/field） | ✓（"model prefills once and the KV cache is shared"） | ✓ | ✓（schema 编译） | ✗ |
| `CoderInPajamas/JEV-MLX` | ✓（读 candidate scores/logits） | 有 margin | ✓（prefix reuse） | ✓ | ✓（dynamic choices） | ✗ |
| `day253/microjev` | ✓（GPT-2 标量打分头） | 有 | 未核实 | ✓ | ✓（动态候选打分器） | ✓（MLX 训决策头） |
| `APUS fast-browser-use` | ✓（单 token 映射 A/B/C...） | ✓（normalized softmax over candidate logits） | ✓（"KV-Cache Broadcasting & Batched Evaluation"） | ✓（仅 TYPE_TEXT 才生成） | ✓（从可见 DOM 动态生成候选） | ✗ |
| `browser-use/jev-ultrafast` | 云端 API（TypeSafe） | — | — | — | ✓（operation/target 动态 heads） | ✗ |
| `tamaratran/fast-jev-compaction` | 云端 API | — | — | — | 问题动态生成 | ✗ |
| `perixtar/jev-e2e` | 云端 API（经 OpenRouter） | — | — | — | 从观测 controls 选 | ✗ |
| `TianyuCodings/NanoJev` | ✓ | ✓（Choice set attention + softmax） | 未做（roadmap） | ✓ | ✓（2–255 动态候选） | ✓（Qwen3-0.6B + decision heads） |
| `jaredpalmer/kev` | ✓（读 answer tokens 的 logits） | ✓ | ✓（state prefix cache） | ✓ | ✓ | ✓（LoRA rank 16） |
| `wfzyx/von` | ✓ | ✓（T=1.1692，restricted） | 未核实 | ✓（非自回归 ModernBERT） | ✓ | ✓（RLCD 后训练） |
| `ekzhang/openjev-sglang` | ✓（prefill-only） | ✓ | ✓（radix caching） | ✓ | ✓ | ✗ |
| `featherless-ai/simple-jev` | ✓（next-token logits per question） | ✓ | ✓（"evaluates the exact common token prefix once and reuses that prefix's KV cache"） | ✓ | ✓ | ✗ |
| `razorback16/openjev` | ✓（读概率） | ✓ | 未核实 | ✓（DiffusionGemma） | ✓ | ✗ |
| `ikermoel/open-alternative-jev` | ✓（next-token distribution at its own position, restricted to options） | ✓ | ✓（packing：state 写一次） | ✓ | ✓ | ✗（用现成 LLM） |
| `Heman10x openJev-verdict-2.0` | ✓ | ✓ | 未核实 | ✓ | ✓ | ✓（ModernBERT + dual confidence head） |
| `Mapika/decider` | ✓ | ✓ | 未核实 | ✓ | ✓（≤255 options） | ✓（含 calibration-aware RL） |
| `bespokelabsai/nimble` | ✓（"scores one answer token per question"） | ✓ | ✓（"reads the prompt once"） | ✓ | ✓ | ✓（LoRA on answer tokens only） |
| `rorshopping/jev-on-a-laptop` | ✓ | ✓ | ✓（**图示最清楚**：broadcast ×N fields） | ✓ | ✓ | ✗ |

---

## 5. 硬性对照表（全部字段来自 gh api）

**⚠️ Star 数会分钟级漂移。** 下表 Stars 列同时给出两个时点：
- `T1` = 2026-09-21T04:15Z（本文件主体采集时刻）
- `T2` = 2026-09-21T04:2xZ（收尾复核时刻）

两者相差 0–5 星属正常增长。**引用时请注明时点。**

### 5.1 任务点名项目

| 仓库全名 | URL | Stars T1 | Stars T2 | Forks | Issues | License | Created | Pushed | 语言 |
|---|---|---:|---:|---:|---:|---|---|---|---|
| `TheoLeeCJ/SemIf` | https://github.com/TheoLeeCJ/SemIf | 2,524 | **2,525** | 158 | 13 | MIT | 2026-09-16T03:51:21Z | 2026-09-19T04:46:36Z | Python |
| `r-ms/mini-jev` | https://github.com/r-ms/mini-jev | 35 | 35 | 3 | 1 | MIT | 2026-09-17T19:41:13Z | 2026-09-18T12:05:38Z | Python |
| `vinnylarouge/jevlike` | https://github.com/vinnylarouge/jevlike | 1,097 | 1,097 | 97 | 5 | MIT | 2026-09-16T10:26:01Z | 2026-09-16T18:12:53Z | Python |
| `bnsd55/jevmlx` | https://github.com/bnsd55/jevmlx | 47 | 47 | 8 | 7 | MIT | 2026-09-17T10:20:12Z | 2026-09-21T03:13:55Z | Python |
| `CoderInPajamas/JEV-MLX` | https://github.com/CoderInPajamas/JEV-MLX | 2 | 2 | 0 | 0 | MIT | 2026-09-20T13:09:46Z | 2026-09-20T16:13:19Z | Python |
| `day253/microjev` | https://github.com/day253/microjev | 1 | 1 | 0 | 0 | MIT | 2026-09-20T15:35:49Z | 2026-09-20T18:49:34Z | Python |
| `NullPo-jp/PocketJev` | https://github.com/NullPo-jp/PocketJev | 0 | 0 | 0 | 0 | MIT | 2026-09-17T11:14:40Z | 2026-09-17T13:18:49Z | Swift |
| `APUS-AI-Lab/fast-browser-use` | https://github.com/APUS-AI-Lab/fast-browser-use | 35 | 35 | 1 | 0 | MIT | 2026-09-19T10:17:17Z | 2026-09-21T02:48:29Z | Python |
| `tamaratran/fast-jev-compaction` | https://github.com/tamaratran/fast-jev-compaction | 5,376 | **5,380** | 295 | **59** | MIT | 2026-09-17T05:57:20Z | 2026-09-18T04:45:31Z | TypeScript |
| `perixtar/jev-e2e` | https://github.com/perixtar/jev-e2e | 3 | 3 | 0 | 1 | MIT | 2026-09-18T19:04:41Z | 2026-09-19T10:34:32Z | TypeScript |
| `logicrw/awesome-jev-projects` | https://github.com/logicrw/awesome-jev-projects | 240 | 240 | 20 | 0 | MIT | 2026-09-18T06:41:50Z | 2026-09-21T02:26:03Z | JavaScript |
| `yibie/awesome-jev` | https://github.com/yibie/awesome-jev | 673 | **674** | 98→**99** | 3 | **null** | 2026-09-17T14:23:21Z | 2026-09-21T01:52:38Z | Python |
| `browser-use/jev-ultrafast` | https://github.com/browser-use/jev-ultrafast | 12,586 | **12,593** | 783 | **87** | MIT | 2026-09-16T21:30:12Z | 2026-09-18T16:28:35Z | Python |

### 5.2 高星 / 高完整度新发现

| 仓库全名 | Stars | Forks | License | Created | Pushed | 底座模型 |
|---|---:|---:|---|---|---|---|
| `browser-use/jev-ultrafast` | 12,586 | 783 | MIT | 09-16 | 09-18 | TypeSafe Jev（云端）+ `inception/mercury-2.5` |
| `tamaratran/fast-jev-compaction` | 5,376 | 295 | MIT | 09-17 | 09-18 | TypeSafe `jev-latest` |
| `TheoLeeCJ/SemIf` | 2,524 | 158 | MIT | 09-16 | 09-19 | Qwen3.5-4B / MiniCPM5-2B / Qwen3-0.6B |
| `mizorewww/laya-mlx`（**Laya 非 JEV**） | 1,931 | 98 | Apache-2.0 | 09-19 | 09-19 | Laya（ModernBERT） |
| `TianyuCodings/NanoJev` | 1,520 | 180 | MIT | 09-17 | 09-20 | Qwen3-0.6B + decision heads |
| `bespokelabsai/nimble` | 1,215 | 85 | **null** | 09-18 | 09-20 | Qwen3.5-9B + LoRA |
| `jaredpalmer/kev` | 1,162 | 70 | Apache-2.0 | 09-17 | 09-21 | Qwen3.5-0.8B/4B/9B |
| `vinnylarouge/jevlike` | 1,097 | 97 | MIT | 09-16 | 09-16 | byte-encoder from scratch / Qwen2.5-0.5B frozen |
| `featherless-ai/simple-jev` | 404 | 42 | **null** | 09-18 | 09-20 | Qwen3.5-0.8B / Gemma 4 26B-A4B / Laya |
| `wfzyx/von` | 241 | 22 | Apache-2.0 | 09-18 | 09-21 | ModernBERT-Large 395M |
| `ekzhang/openjev-sglang` | 239 | 27 | **null** | 09-17 | 09-18 | Qwen3.6-35B-A3B (SGLang/B200) |
| `razorback16/openjev` | 220 | 20 | Apache-2.0 | 09-18 | 09-20 | DiffusionGemma 26B-A4B |
| `Heman10x-NGU/openJev-verdict-2.0` | 205 | 28 | NOASSERTION | 09-19 | 09-20 | ModernBERT-base 151M |
| `logan-markewich/jeff` | 173 | 11 | MIT | 09-19 | 09-20 | GliFormer（GLiNER） |
| `Mapika/decider` | 163 | 5 | Apache-2.0 | 09-16 | 09-20 | Qwen3.5-2B/35B-A3B/0.8B |
| `Heman10x-NGU/Verdict-open-jev` | 48 | 6 | NOASSERTION | 09-17 | 09-20 | ModernBERT 151M |
| `deepanwadhwa/OpenDecision` | 42 | 3 | Apache-2.0 | 09-17 | 09-20 | NLI |
| `ikermoel/open-alternative-jev` | 38 | 8 | Apache-2.0 | 09-18 | 09-21 | 任意 open-weights（测 Qwen3.6-27B / 3.5-4B） |
| `SAGAR-TAMANG/sarvam-jev` | 38 | 6 | **null** | 09-18 | 09-18 | sarvam-1 |
| `bnsd55/jevmlx` | 47 | 8 | MIT | 09-17 | 09-21 | Qwen2.5-7B/3B/1.5B-Instruct-4bit (MLX) |
| `r-ms/mini-jev` | 35 | 3 | MIT | 09-17 | 09-18 | Qwen3-4B-Instruct-2507 |
| `APUS-AI-Lab/fast-browser-use` | 35 | 1 | MIT | 09-19 | 09-21 | Qwen3.5-9B / 35B-A3B |
| `fstandhartinger/jevbench` | 31 | 1 | MIT | 09-19 | 09-21 | N/A（benchmark） |
| `SiliconLabAI/OpenJev` | 28 | 4 | **null** | 09-20 | 09-20 | 未核实 |
| `intikhab49/open-jev-typed-decision-engine` | 24 | 1 | Apache-2.0 | 09-19 | 09-19 | 150M encoder |
| `rorshopping/jev-on-a-laptop` | 22 | 1 | NOASSERTION | 09-16 | 09-17 | Qwen-2.5-1B-RLCD / Qwen2.5-1.5B-4bit |
| `zhihz/openjev` | 24 | 2 | NOASSERTION | 09-16 | 09-16 | 未核实 |
| `IamBusy/OpenJev-Vision` | 22 | 3 | Apache-2.0 | 09-19 | 09-19 | 视觉版 |
| `0xBakeer/arbiter` | 14 | 2 | MIT | 09-20 | 09-20 | Laya 或自带 |
| `siliconkernel/vllm-jev-decison` | 8 | 0 | MIT | 09-18 | 09-18 | vLLM |
| `Micha0827/snapjudge` | 7 | 0 | MIT | 09-18 | 09-19 | Qwen + MLX |
| `abhishek085/open-spark-jev` | 7 | 2 | Apache-2.0 | 09-20 | 09-21 | Qwen3 / DGX Spark |
| `akash-kamat/system-one-gemma` | 3 | 0 | **null** | 09-17 | 09-18 | Gemma 3 270M |
| `perixtar/jev-e2e` | 3 | 0 | MIT | 09-18 | 09-19 | `typesafe/jev-1.13`（OpenRouter） |
| `CoderInPajamas/JEV-MLX` | 2 | 0 | MIT | 09-20 | 09-20 | Qwen3.5-9B / Gemma 4 26B-A4B / GLM-4.7-Flash |
| `day253/microjev` | 1 | 0 | MIT | 09-20 | 09-20 | GPT-2 124M (MLX) |
| `NullPo-jp/PocketJev` | 0 | 0 | MIT | 09-17 | 09-17 | Qwen3-VL (MLX, Swift/iOS) |
| `capitaharlock/jev-clone` | 0 | 0 | Apache-2.0 | 09-19 | 09-19 | 未核实（语言 null） |

### 5.3 许可证缺口（license = null，采用有风险）

`yibie/awesome-jev`、`featherless-ai/simple-jev`、`ekzhang/openjev-sglang`、`bespokelabsai/nimble`、`SAGAR-TAMANG/sarvam-jev`、`akash-kamat/system-one-gemma`、`SiliconLabAI/OpenJev`、`v-modal/awesome-jev-tools`、`dabit3/jev-experiments`、`Sac-Y/Jev-cu`、`fhshaik/typesafe-mario`、`rmalde/minecraft-agent`（后两者为应用非复现）

**NOASSERTION（GitHub 无法识别，但仓库内有许可证文件）：** `Heman10x-NGU/openJev-verdict-2.0`、`Heman10x-NGU/Verdict-open-jev`、`rorshopping/jev-on-a-laptop`、`reticlehq/reticle`、`milind-soni/tiptour-macos`。

### 5.4 任务点名「不存在的项目」核查

| 任务提到的名字 | 核查结果 |
|---|---|
| **mini-jev** | ✓ 多个同名仓库。最相关的 `r-ms/mini-jev`（35★，MIT）。另有 `deep-diver/mini-jev`(3★, 无 license)、`samat2003/mini-Jev`(3★, Apache-2.0)、`UpHash-Network/mini-jev`(0★)、`luckberonne/mini-jev`(0★)、`Haslab-dev/pandu-jev`(0★) |
| **jevlike** | ✓ 唯一：`vinnylarouge/jevlike`（1,097★） |
| **JEV MLX engine / mlx 系列** | ✓ 找到 5 个 JEV 相关 + 5 个 Laya 相关（见 §2.4）。**没有名为 "JEV MLX engine" 的仓库**；最接近的是 `bnsd55/jevmlx` 与 `CoderInPajamas/JEV-MLX`（包名 `jev-mlx`） |
| **fast-browser-use（APUS 麒麟合盛 AI 实验室）** | ✓ `APUS-AI-Lab/fast-browser-use`（35★）。**注意同名干扰：** `rknoche6/fast-browser-use`（3★，Rust DOM，与 JEV 无关）、`NachaFromMars/fast-browser-use`（1★，CDP 自动化，与 JEV 无关）、`gauravdhiman/browser-use-fastapi-docker-server`（37★，2025 年项目，与 JEV 无关） |
| **fast-jev-compaction** | ✓ 唯一：`tamaratran/fast-jev-compaction`（5,376★） |
| **jev-e2e（perixtar）** | ✓ 确认：`perixtar/jev-e2e`（3★，MIT）。同名相关：`dingw530/playwright-jev`（0★，Jev + playwright-cli） |
| **logicrw/awesome-jev-projects** | ✓ 确认（240★，MIT） |
| **yibie/awesome-jev** | ✓ 确认（673★，**无 license**） |
| **SemIf（原名 OpenJev，作者 TheoLeeCJ）** | ✓ 确认改名事实。**注意：** APUS README 仍引用旧名 `TheoLeeCJ/openjev` |

---

## 6. 生态规模快照（2026-09-21T04:15Z）

- `gh api "search/repositories?q=jev&sort=stars&per_page=50"` 前 50 名中，**约 40 个**是 JEV 相关（其余是同名干扰：`jevajs/Jeva`、`GoldenGnu/jeveassets`、`killop/anything_about_game` 等）。
- `q=topic:jev` 返回**至少 55 个**仓库。
- `q=topic:system-one` 返回**至少 55 个**仓库，其中约 40 个提到 Jev/TypeSafe。
- `awesome-jev` 类目录仓库至少 **18 个**（`yibie`、`logicrw`、`cobanov`、`AnotiaWang`、`fatwang2`、`AbdelStark/awesome-typesafe`、`valentynkit`、`hellogumbo`、`kraayenjon`、`AppitStudio`、`v-modal`、`Anil-matcha/awesome-jev-by-typesafe`、`OmniJev/awesome-jev-gallery`、`walidboulanouar/awesome-jev-use-cases`、`anandi1989/awesome-jev-usecases`、`majiayu000/awesome-jev`、`daftAI2026/awesome-jev`、`wh000wh000/awesome-jev-live`、`ckaraca/awesome-jev`、`yzfly/awesome-jev-zh`、`everyinfra/jev-radar`）。
- **真正训练/推理模型的复现仓库约 20–25 个**；**应用/插件/目录类占绝大多数**。

---

## 7. 未核实 / 需谨慎的清单

| 事项 | 状态 |
|---|---|
| TypeSafe 官方 "最快 200×、成本 1/400" | **官方单方面宣称**；本次未找到可复现的官方 benchmark 方法说明 |
| TypeSafe 官方星标/准确率（如 Jev 67.8%、96.6% macro） | 均为**第三方仓库引用官方页面**，非独立测量 |
| `TheoLeeCJ/SemIf` 中 "Published Jev 0.883" | 项目自述「read from TypeSafe's published records; **we did not run a live Jev endpoint**」 |
| `Heman10x-NGU/openJev-verdict-2.0` 的 77.10% / 0.0636 Brier / 0.0144 ECE | 项目方自己的 audited test receipt，**未见第三方独立复跑** |
| `wfzyx/von` 的 T 值 | **仓库内自相矛盾**：Overview 写 T=1.0367，Choice 章节写 T=1.1692 |
| `wfzyx/von` 的训练集规模 | **仓库内自相矛盾**：250,000 与 ~290,000 两处 |
| `wfzyx/von` 引用的 `arXiv:2503.23303` (DeepMostInnovations, RLCD) | **未核实该 arXiv 条目存在** |
| `capitaharlock/jev-clone` | 语言字段为 null，**未核实是否真有可运行代码** |
| `SiliconLabAI/OpenJev` / `zhihz/openjev` / `xingwudao/OpenJev` / `GPT-AGI/OpenJev` | 仅取元数据，**未读 README** |
| 所有「200×/400×」类速度成本声明的独立验证 | **本次未对任何仓库做实际跑测**；所有 benchmark 数字均为项目方自报 |
| APUS「全球最早一批 / 国内首批」 | 媒体+项目方口径，**无法独立核实** |
| Jev 发布日 9/14 vs 9/15 | **两个日期并存**，未对齐 |
| `mizorewww/laya-mlx` 与 JEV 的关系 | 它是 **Laya** 复现（1,931★），常被 JEV 生态引用为对照基线；**不是 JEV 复现** |
| 各仓库是否存在「单作者批量提交、共享 scaffold」现象 | `yibie/awesome-jev` 明确警告该现象存在；**本报告未逐仓核查 commit 历史** |

---

## 8. 参考链接汇总

**官方**
- 博客：https://typesafe.ai/blog/introducing-system-one-models-and-jev
- 文档：https://docs.typesafe.ai/introduction · https://docs.typesafe.ai/api · https://docs.typesafe.ai/primitives/choice · https://docs.typesafe.ai/models · https://docs.typesafe.ai/patterns/fan-out · https://docs.typesafe.ai/agent-skill
- 评测页：https://evals.typesafe.ai/

**媒体报道**
- https://explainx.ai/blog/typesafe-ai-jev-system-one-models-launch-2026（2026-09-20）
- https://fourweekmba.com/ai-typesafe-ai-almeida-chatgpt-era-structural-read/（2026-09-20）
- https://aiprofitboardroom.com/blog/jev-ai/（2026-09-19）
- https://menafn.com/1111681502/Typesafe-Unveils-Decision-Focused-AI-Model-Jev-Arabian-Post（2026-09-19）
- https://www.ayautomate.com/blog/jev-typesafe-system-one-model（2026-09-19）
- https://www.remio.ai/post/typesafe-jev-ai-model-challenges-the-llm-first-software-stack（2026-09-19）
- https://www.testmuai.com/blog/what-is-jev/
- https://www.oguzhan.co/typesafe-jev-system-one-decision-model/（2026-09-20）
- 中文：https://tech.cnr.cn/techph/20260920/t20260920_527819594.shtml · http://www.news.cn/tech/20260921/8f1c9bd6a9254e629383f1ac51e0d27d/c.html · https://www.qbitai.com/2026/09/492939.html · https://news.sina.cn/ai/2026-09-20/detail-inisnhav1546465.d.html · https://m.sohu.com/a/1078660919_362042/

**生态目录 / 聚合**
- https://madewithjev.com/categories/agents-and-browsers
- https://benchmarkheaven.com/jev-models
- https://archerhume.com/posts/jevs-architecture-unmasked（被 `jaredpalmer/kev` 引用为架构依据）
- https://morethanamachine.com/posts/jev-style-decisions-dgx-spark/（被 `wfzyx/von` 引用为 ViZDoom 协议来源）

**底座模型**
- https://huggingface.co/Qwen/Qwen3.5-4B · /Qwen3.5-0.8B · /Qwen3.5-9B · /Qwen3.5-35B-A3B · /Qwen3.5-2B-Base · /Qwen3-4B-Instruct-2507 · /Qwen3-0.6B · /Qwen3-VL
- https://huggingface.co/openbmb/MiniCPM5-2B
- https://huggingface.co/mlx-community/Qwen2.5-7B-Instruct-4bit · /Qwen2.5-3B-Instruct-4bit · /Qwen2.5-1.5B-Instruct-4bit
- https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD
- https://huggingface.co/nvidia/diffusiongemma-26B-A4B-it-NVFP4
- https://huggingface.co/fastino/gliner2-large-v1
- https://huggingface.co/convaiinnovations/laya
- https://huggingface.co/google/gemma-4-26B-A4B-it
- https://huggingface.co/C-Tianyu/NanoJev · https://huggingface.co/datasets/C-Tianyu/NanoJev-Data
- https://huggingface.co/bespokelabs/Bespoke-Nimble-9B
- https://huggingface.co/Mapika/decider-2b · /decider-35b-a3b · /decider-0.8b · /decider-2b-vision
- https://huggingface.co/wfzyx/von-1.0
- https://huggingface.co/heman10x/rlcd-modernbert-151m
- https://huggingface.co/datasets/Mikhail/mini-jev-runs
- https://huggingface.co/datasets/LocalLLaMA/typed-decisions
- https://huggingface.co/datasets/alisawuffles/WANLI · /clinc/clinc_oos
