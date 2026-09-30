<div align="center">

# JEV 调研报告

**TypeSafe System One 决策模型与开源对标**

**JEV Research Report: What JEV really is — and the open-source alternatives**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.3-blue)](CHANGELOG.md)
[![Data Snapshot](https://img.shields.io/badge/data%20snapshot-2026--09--29-orange)](CHANGELOG.md)
[![GitHub Stars](https://img.shields.io/github/stars/Chorylee7/JEV?style=social)](https://github.com/Chorylee7/JEV/stargazers)

[⚡ 快速参考卡](#quick-ref) · [📋 导读](#tldr) · [🌐 English Report](REPORT-EN.md) · [🧪 评估脚手架](eval/) · [📜 更新日志](CHANGELOG.md)

</div>

> **怎么读**：结论先行——只想知道答案，看下面的「快速参考卡」就够。每个数字都带证据等级：**【官方】**官方发布 · **【第三方】**独立测试/媒体 · **【项目方自测】**仓库作者自报 · **【未核实】**无一手来源。全英文版见 [REPORT-EN.md](REPORT-EN.md)。
> **口径**：结论基于 2026-09-21 的核实；star/许可证/生态规模为 2026-09-29 快照（变更见 [CHANGELOG](CHANGELOG.md)）；**所有 benchmark 数字除注明外均为项目方或厂商自报，本报告未做任何实际跑测**。

## ⚡ 快速参考卡 / Quick Reference Card <a id="quick-ref"></a>

| 维度 | 结论 | 证据 |
|---|---|---|
| 它是什么 | 托管"决策模型"：`state` + 类型化问题 → 结构化答案 + 概率；**不生成文本** | 【官方】 |
| 三种原语 | `noul`（0–1 是非）/ `choice`（≤255 单选）/ `score`（2–10 级有序评分） | 【官方】 |
| 价格 | $0.042 / 百万 input token，输出免费；10k token state ≈ $0.00042/次 | 【官方】 |
| 延迟 | 官方 70–500ms；独立实测 p50 314ms / p95 399ms | 【第三方】 |
| 上下文 | 请求 64k；`state` + 最长单问 ≤ 32k；**仅文本输入** | 【官方】 |
| 速度宣称 | 官方 193.6×（首页）与 40×–200×（博文）**自相矛盾**；独立实测 4.8×–25× | 【官方/第三方】 |
| 成本宣称 | 官方 444.6×（只对最贵模型那一行）；独立实测 8.6×–580×；中文实测仅约 2.7× | 【官方/第三方】 |
| 准确率 | 官方四工作流平均 67.8%（≈ Terra / Sonnet 5 档）；二元门禁可达 100%（LangChain 500 次对照人类 oracle） | 【官方/第三方】 |
| 明显短板 | 发票类 61.8%（9 模型第 8）、中文客服 64–65%、77 类意图 0.78、算术/日期/间接推理 | 【官方/第三方】 |
| 弃权率 | 实测 30% 弃权把 76× 成本优势压到 **3.2×**；天花板 = `1/弃权率` | 【第三方】 |
| 概率校准 | 可知任务好（ECE 0.024 ≈ 噪声底），不可知任务过度自信（ECE 0.107）；**别用官方 `confidence` 字段，用 `max(probabilities)`** | 【第三方】 |
| 数据政策 | 不训练客户请求/响应；**ZDR 仅企业版** | 【官方 09-29】 |
| 当前版本 | `jev-1.13.0`（09-29 核实，无 preview 构建） | 【官方】 |
| 开源首选 | **Laya**（Apache-2.0，28.1k★，T4 上 33ms，微调后 0.766 > JEV 0.727；**>20 个选项明显退化**） | 【项目方自测】 |
| 别用的场景 | 高基数分类、中文重负载、数值阈值判断、要求逻辑一致的概率、>100Hz 控制回路 | 综合 |

## 📋 这份报告回答四个问题 <a id="tldr"></a>

1. **JEV 是什么？** 一个只做判断、不写文字的托管决策模型 → [§1](#s1-what-is-jev)
2. **官方宣称的"快 200×、省 400×"可信吗？** 官方口径自相矛盾；独立实测 5–25× 速度、9–580× 成本 → [§2](#s2-claims-vs-evidence)
3. **有哪些开源替代？** 接口复现约 20+ 个；真正自研开放权重的是 Laya（28k★）和刚下场的 Together AI `tev1` → [§3](#s3-landscape) · [§4](#s4-open-weight-models)
4. **我该不该用、怎么用？** 按场景决策表 + 7 条上线检查清单 + 8 条风险清单 → [§5](#s5-selection-guide) · [§6](#s6-risks)

<details>
<summary>📑 完整目录（点击展开）</summary>

1. [JEV 是什么](#s1-what-is-jev)
2. [实测表现：官方宣称 vs 独立验证](#s2-claims-vs-evidence)
3. [开源生态全景](#s3-landscape)
4. [真正自训并开放权重的决策模型](#s4-open-weight-models)
5. [选型建议](#s5-selection-guide)
6. [风险清单](#s6-risks)
7. [附录：核实方法、未核实清单与参考链接](#s7-appendix)

</details>

---

## 🤖 1. JEV 是什么 / What is JEV <a id="s1-what-is-jev"></a>

> *EN — JEV is TypeSafe AI's hosted "System One" decision model: typed questions in, structured answers with probabilities out, never free text.*

**一句话**：JEV 是 TypeSafe AI（旧金山，2024 年成立；创始人 Diogo Almeida 为 InstructGPT 论文作者之一；4000 万美元种子轮、DCVC 领投）于 **2026-09-15** 发布的 "System One" 决策模型——**它只做判断，不写任何文字**：你传入程序状态（`state`）和若干类型化问题，它一次调用返回带概率的结构化答案。权重闭源、仅云端 API。

### 1.1 三种原语 = 它的全部能力边界

| 原语 | 语义 | 返回 | 例子 |
|---|---|---|---|
| `noul` | 是/否 | 单个 0–1 概率（**无 confidence 字段**） | "这条消息是否紧急？" |
| `choice` | 单选（**≤255 个选项**） | 选项 + `probabilities`（和为 1）+ `confidence` | "该路由到哪个团队？" |
| `score` | 有序评分（**2–10 级**） | 分值（可落在级别之间，如 1.05）+ 分布 + `confidence` | "客户愤怒程度 1–5？" |

注意：**没有 ranking、span 类型**；`boolean` 只是部分渠道（如 Vercel）对 `noul` 的别名。

### 1.2 一次调用长什么样

端点 `POST https://api.typesafe.ai/v1/systemone`；一个请求里的所有问题对同一 `state` **并行评估**（官方："加问题几乎不增加响应时间"）：

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

`questions` 的 key 由你命名、答案按同 key 返回、**key 不发给模型**；`instructions` / `criteria` 接受结构化 JSON。SDK：Python `typesafe-sdk`、TS `@typesafe-ai/sdk`；官方 Agent Skill 见 [typesafe-ai/skills](https://github.com/typesafe-ai/skills)（MIT，2,392★）。

### 1.3 规格、价格与硬限制

| 项 | 值 | 证据 |
|---|---|---|
| 价格 | $0.042 / 百万 input token（**output 免费**）；官方自认"无法证明它没有被补贴" | 【官方】 |
| 延迟 | 官方 70–500ms；独立实测 p50 314ms / p95 399ms | 【官方/第三方】 |
| 限速 | 250k tokens/秒 + 1,200 请求/分钟，**声明动态调整、可不另行通知** | 【官方】 |
| 上下文 | 请求 64k；`state` + 最长单问 ≤ 32k | 【官方】 |
| 输入模态 | **仅文本**（图像/音频/视频不支持，官方注明 "yet"）；**不支持流式** | 【官方】 |
| 语言 | 英语最佳，CJK "能用但不同等" | 【官方】 |
| 权重/微调 | 闭源；所有账号同一套权重，无 per-customer 微调 | 【官方】 |
| 版本 | `jev-1.13.0`（09-29 核实，无 preview 构建）；生产环境应 pin 版本 ID | 【官方】 |
| 数据政策 | 不训练客户请求/响应；**ZDR 仅企业版** | 【官方 09-29】 |
| 地区 | 央广网称"未对中国大陆开放"；官方条款**无地区限制明文**，以官方口径论未证实 | 【第三方】 |

### 1.4 官方自己承认的短板（jaggedness 页）

官方单列一页列出 9 类失败模式【官方】：**字面理解 · 算术与计数 · 日期比较 · 间接推理 · 大 state 干扰 · 对抗内容 · instructions 与 criteria 矛盾 · 结构不变量 · 生成任务**。另有两个反直觉点：**问题与其否定的概率之和可以 ≠ 1**（官方示例 0.72 + 0.47 = 1.19）；`score` 数值校准弱，不能插值还原精确数字。

### 1.5 两个好玩的官方 demo

- **Doom**：喂文字化的结构化游戏状态（**不看画面**），约 10 queries/秒、$7/小时；官方自嘲"非 AI 的 Doom bot 玩得更好"。
- **Wikiracing**：每步在数百至数千个链接中做 `choice`；超过 255 个选项时走"两阶段评分 + 选择"。

---

## 📊 2. 实测表现：官方宣称 vs 独立验证 <a id="s2-claims-vs-evidence"></a>

> *EN — The vendor's headline multipliers contradict each other across its own pages; independent tests land at 4.8×–25× speed and 8.6×–580× cost; accuracy is highly task-dependent.*

### 2.1 速度与成本：官方自己就有四个版本

| 来源 | 速度倍数 | 成本倍数 | 类型 |
|---|---|---|---|
| TypeSafe 首页 | 193.6× | 444.6× | 【官方】 |
| TypeSafe 发布博文 | 40×–200× | 未公布 | 【官方】 |
| TypeSafe onboarding（需登录） | 20×–200× | 40×–1,000× | 【官方】 |
| 官方 evals 表手算 | 约 25×–95× | 76×–440× | 【第三方推算】 |
| **独立实测汇总**（Every / Near Here / gemanor / 4esv / 硅星人 / Capital & Compute） | **4.8×–25×**（p50 314ms 落在官方 70–500ms 区间） | **8.6×–580×** | 【第三方】 |

**读法**：444.6× 是"只跟最贵的 Opus 5 那一行比"得到的；第三方实测中位数落在 **5×–25× 速度、10×–60× 成本**。"快"是真的，但"200×/400×"不能用于容量规划。

### 2.2 准确率：任务决定一切

官方 evals 页四工作流（本报告直接从页面 HTML 解析，非媒体转述）：

| 工作流 | JEV | 该工作流最佳 | JEV 排名（共 9 个模型） |
|---|---|---|---|
| Security Incidents | 61.7% | Opus 5 workflow 66.2% | 第 3 |
| **Invoice Processing** | **61.8%** | Sol workflow 79.1% | **第 8（仅胜 Haiku 4.5）** |
| Customer Service | 76.0% | Sol workflow 78.3% | 第 4 |
| Agent Trace Observability | 71.6% | Sol workflow 76.6% | 并列第 6 |
| **平均** | **67.8%** | Sol workflow 74.1% | — |

第三方独立测试（节选；完整版见 [research/ecosystem-benchmarks.md](research/ecosystem-benchmarks.md) 表 B）：

| 测试 | 任务 | JEV | 对照 | 结论 |
|---|---|---|---|---|
| LangChain（09-20） | 500 次重复二元判定，对人类 oracle | **100%** | Terra 99.8% / Sonnet 4.6 80.0% | **第一，方差最低**；总成本 $0.34 vs Claude $28.17 |
| Arize | 18,514 封真实标签邮件 | 98.3% | **TF-IDF 98.4%** | 统计打平 |
| gemanor | 1,080 次规则审查 | 98.0% | Gemini / Fable 100% | 落后 2 点 |
| 4esv | 77 类意图 | 0.78 | Terra 0.85 | 落后 7 点 |
| 硅星人（中文） | 50 条中文客服（四项全对才计分） | **64–65.2%** | MiniMax M3 高 10.8 点 | 强模型组**垫底** |
| NanoJev（项目方） | ViZDoom Basic | 56/128 ≈ 裸 Qwen3-0.6B | NanoJev 128/128 | 该任务上无增益 |

**方法学警告**：官方评测的"正确答案"是**两个 LLM 输出的平均**（非人工标注，官方自承这会偏向 OpenAI/Anthropic 的模型）；官方还自承评测跑在内部笔记本上、工作流由内部团队构建、"0% 类型错误"非实测、demo 的 state 偏短。

### 2.3 两个决定成败的隐藏变量

**① 弃权率（abstain rate）——成本杀手。** 实测 30% 弃权时，成本优势从 76× 塌到 **3.2×**；天花板 = `1/弃权率`，与单价无关。弃权率是你自己造成的：薄 state 弃权 57.8%，state 加 3 个字段后 0.5 阈值下从 **65% 降到 40%**。

**② 校准是双面的。** 可知任务上很好（OpenBookQA ECE 0.024 ≈ 噪声底；LangChain 500 次重复方差最低）；不可知任务上过度自信（自造工单 ECE **0.107** = 噪声底 4.4 倍，`score` 子任务需重拟温度 **3.40**）；官方 `confidence` 字段**从未优于 `max(probabilities)`**——建议直接用后者自定阈值。

---

## 🌐 3. 开源生态全景 / The Open-Source Landscape <a id="s3-landscape"></a>

> *EN — Only ~20–25 repos actually implement the mechanism (out of 14k+ and counting); the dominant trick is "freeze an open LLM, read option-token logits, restricted softmax, skip decoding" — self-measured speedups are 4–5×, not 200×. Almost none claim calibrated probabilities; several explicitly disclaim it.*

### 3.1 先分清四个层次（否则数字没有可比性）

| 层次 | 定义 | 代表 | 本地推理 | 自训权重 |
|---|---|---|---|---|
| L0 客户端应用 | 自己写 prompt/schema，仍调用云端 JEV API | `browser-use/jev-ultrafast`、`tamaratran/fast-jev-compaction`、`typesafe-ai/skills` | ✗ | ✗ |
| L1 接口复现 | 冻结开源模型，**只读 option token 的 logits** + 受限 softmax，跳过自回归解码 | `TheoLeeCJ/SemIf-OpenJev`、`r-ms/mini-jev`、`bnsd55/jevmlx`、`featherless-ai/simple-jev`、`ekzhang/openjev-sglang` | ✓ | ✗（冻结） |
| L2 复现 + 自训 head/adapter | 在 L1 基础上自己训练打分头或 LoRA | `vinnylarouge/jevlike`、`TianyuCodings/NanoJev`、`jaredpalmer/kev`、`bespokelabsai/nimble`、`wfzyx/von`、`Mapika/decider`、`togethercomputer/tev1` | ✓ | ✓（部分/适配器） |
| L3 自研决策模型 | 自己训模型、发权重与数据 | **Laya**（见 §4） | ✓ | ✓ |

**关键**：L1/L2 的"加速倍数"都建立在**跳过解码**上，而 **state 的 prefill 省不掉**——所以它们的实测加速是个位数倍数，不是 200×。

### 3.2 核心项目对照表（star 为 2026-09-29 GitHub API 快照）

| 仓库 | ★ | 许可证 | 底座模型 | 硬件 | HTTP 服务 | 自称校准 |
|---|---:|---|---|---|---|---|
| [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) | **28,058** | Apache-2.0 | **自研** ModernBERT 系（≈421M） | CPU / CUDA | SDK | ✓（温度拟合后 ECE 0.081） |
| [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | 21,264 | MIT | 云端 JEV + `inception/mercury-2.5` | 任意 | — | — |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | 7,749 | Apache-2.0 | Qwen3.5-0.8B/4B/9B + LoRA | CUDA / Apple Silicon | ✓ | **明确否认** |
| [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | 7,167 | MIT | 云端 `jev-latest` | 任意 | — | **明确否认** |
| [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) | 6,604 | Apache-2.0 | Laya 的 MLX 移植（非 JEV 复现） | Apple Silicon | — | — |
| [TheoLeeCJ/SemIf-OpenJev](https://github.com/TheoLeeCJ/SemIf-OpenJev)（原名 OpenJev→SemIf，09-22 二次更名） | 4,547 | MIT | Qwen3.5-4B / MiniCPM5-2B / Qwen3-0.6B（冻结） | CUDA / Apple MLX / WebGPU | demo | 要求用户自行校准 |
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | 2,419 | MIT | Qwen3-0.6B + 自训 decision heads | CUDA / CPU | ✓ | — |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | 1,897 | **无** | Qwen3.5-9B + LoRA | CUDA | ✓ | — |
| [vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike) | 1,332 | MIT | 从零训 byte-encoder / Qwen2.5-0.5B 冻结 | CPU / MPS / CUDA | — | 不声称 |
| [ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya) | 916 | Apache-2.0 | Laya / decider / NLI / GLiClass 本地服务化（"决策模型的 Ollama"） | CPU / GPU | ✓ | — |
| [Mapika/decider](https://github.com/Mapika/decider) | 887 | Apache-2.0 | Qwen3.5-2B/0.8B/35B-A3B + vision 版 | CUDA | — | ✓（calibration-aware RL） |
| [wfzyx/von](https://github.com/wfzyx/von) | 763 | Apache-2.0 | ModernBERT-Large 395M | CPU / CUDA | ✓ | ✓（T=1.1692） |
| [featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev) | 567 | **Apache-2.0**（09-28 补证，此前无） | Qwen3.5-0.8B / Gemma 4 26B-A4B / Laya | CPU / CUDA | ✓ | **明确否认** |
| [razorback16/openjev](https://github.com/razorback16/openjev) | 515 | Apache-2.0 | DiffusionGemma 26B-A4B | CUDA | — | — |
| [Liuziyu77/Valen](https://github.com/Liuziyu77/Valen) | 474 | Apache-2.0 | 自训多模态 Jev-like 训练框架（含 vision） | CUDA | — | — |
| [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) | 332 | **无** | Qwen3.6-35B-A3B（SGLang） | B200 级 | ✓ | — |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | 291 | NOASSERTION | ModernBERT-base 151M + 双置信头 | CPU / WebGPU | — | ✓（ECE 1.44%，自测 receipt） |
| [APUS-AI-Lab/fast-browser-use](https://github.com/APUS-AI-Lab/fast-browser-use) | 178 | MIT | Qwen3.5-9B / 35B-A3B | GPU / 无 GPU 的 Mac/PC | ✓ | — |
| [togethercomputer/tev1](https://github.com/togethercomputer/tev1) | 165 | MIT | **Qwen3.5-4B LoRA 微调（Together AI）** | CUDA | — | — |
| [allebee/jevk5](https://github.com/allebee/jevk5) | 123 | Apache-2.0 | open-weight 替代 | CUDA | — | — |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | 69 | MIT | Qwen2.5-7B/3B/1.5B-4bit（MLX） | Apple Silicon / CPU | ✓ | **明确否认** |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | 58 | MIT | Qwen3-4B-Instruct-2507（冻结） | CUDA / MPS | ✓ | **明确否认**（"不是校准概率"） |
| [ikermoel/open-alternative-jev](https://github.com/ikermoel/open-alternative-jev) | 57 | Apache-2.0 | 任意 open-weights | CUDA | — | ✓（MMLU ECE 5.4%→2.1%） |

**未列入但值得知道**：[`logan-markewich/jeff`](https://github.com/logan-markewich/jeff)（261★，把 GLiNER 用于决策）、[`fstandhartinger/jevbench`](https://github.com/fstandhartinger/jevbench)（175★，基准工具）、`dzhng/jevgrep`（1,574★，代码检索 CLI，属应用而非决策模型）、`Heman10x-NGU/Verdict-open-jev`、`deepanwadhwa/OpenDecision`（57★，NLI 路线）、`Micha0827/snapjudge`（14★，MLX）、`NullPo-jp/PocketJev`（2★，Swift/iOS）。

### 3.3 重点项目快评

- **SemIf-OpenJev**（4,547★）：生态里最有代表性也最克制。direct/shared 两模式（state 只 prefill 一次、KV 复用到并行问题）；**自测加速只有 5.21×**（RTX 3090），明确声明"没跑过真实 Jev endpoint"；支持 **WebGPU 浏览器内跑**。
- **mini-jev**（58★）：证据链最规范（预注册文档 + 27,900 条带 logits 的 HF 记录）。结论最不利：**读 letter logits 与语法约束生成精度相当（Δ −0.22pp）**，加速仅 4×（短文本）；明确写"不是校准概率"。
- **NanoJev**（2,419★）：唯一自训权重 + 数据全公开；ViZDoom 128/128 vs JEV 56/128，但 Maze 4/10 反输 JEV 7/10（README 保留该行未删）。
- **kev**（7,749★）：局限性写得最诚实；Brier 0.291 不如 JEV 0.211（**JEV 的分布质量更好**）；自曝 Apple Silicon 上比上一代慢 4–7 倍。
- **tev1**（165★，**Together AI 官方**）：首家正规公司下场。Qwen3.5-4B LoRA SFT（37,840 条训练样本），**输入 2–24 个选项、输出单个答案字母、不给概率**——是约束生成式分类器，范式与 JEV 不同；权重公开，官方博客称"$17 训出自己的分类器"。
- **fast-browser-use**（178★，APUS）：央广网/科技日报等称"全球最早一批复现"，但 star 远低于同期社区项目，README 无独立 Limitations 章节；技术上是标准 L1（DOM 元素编号 + 本地 Qwen3.5-9B 打分，单任务约 4 次）。
- **nimble**（1,897★）：唯一敢把 base model 与 JEV 并列——324 条 held-out：Nimble-9B 90.1% vs base 66.4% vs **JEV 93.2%**（微调能追平但没超过）。
- **open-alternative-jev**（57★）：最诚实的 benchmark——公开承认自己算错并保留错误分析。
- **jev-ultrafast**（21.3k★，browser-use 官方）：注意它是 **L0 云端客户端**（把单步交互压缩成一次往返），代表用量优化，**不是本地替代**。

### 3.4 为什么复现项目只有个位数倍数

1. **Prefill 省不掉**：跳过解码只省生成本身；state 越长省得越少（mini-jev：短文本 4× → 2048 token 时 1.4–2.4×）。
2. **没有专用硬件/服务栈**：官方是 70–500ms 托管服务，社区是单卡 RTX 3090 / M 系列 Mac。
3. **推理框架不同**：`ekzhang/openjev-sglang` 用 SGLang 的 radix caching 做 prefill-only，是最接近"工程化"的路线之一。

### 3.5 生态噪声警告

- GitHub `q=jev` 仓库 09-21 约 **7,330** → 09-29 约 **14,028**（8 天 +91%）【GitHub API】；awesome 类目录已超 **20** 个，多数建于发布首周。
- 真正解释机制、能跑的复现约 **20–25 个**；`yibie/awesome-jev` 作者的警告值得引用：**"对同日批量提交的项目要格外警惕——数量不等于质量。"**
- 生态目录站（jevbest.com、madewithjev.com，09-21 口径）**均声明与 TypeSafe 无关**，star 快照系统性偏低；引用生态规模请注明口径。

---

## 🏗️ 4. 真正自训并开放权重的决策模型 / Genuinely Retrained Open-Weight Models <a id="s4-open-weight-models"></a>

> *EN — Laya (Apache-2.0, 28k★, ~421M ModernBERT-class encoder + decision heads) is the dominant open-weight decision model: it beats JEV's published typed-decisions score (0.766 vs 0.727) and is ~7.8× faster — but all accuracy figures are self-reported, base checkpoints are near chance zero-shot, and it degrades badly above ~20 options. On 09-23 Together AI shipped tev1 (Qwen3.5-4B LoRA, returns a single answer letter, no option probabilities).*

### 4.1 Laya 速览（截至 09-29 已是生态 star 第一）

| 项 | 内容 |
|---|---|
| 仓库 | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)，**28,058★ / 2,446 fork**（09-29 快照；09-21 时 5,060★，8 天 +454%），Apache-2.0 |
| 作者 | Nandakishor Mukkunnoth（Convai Innovations，独立研究者，主仓库挂个人账号） |
| 权重 | HF [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya)（ModernBERT-large + 决策头，421M，likes 4,395）、[`laya-multilingual`](https://huggingface.co/convaiinnovations/laya-multilingual)（mmBERT-base，322M，100+ 语言）、[`laya-typed-decisions`](https://huggingface.co/convaiinnovations/laya-typed-decisions)（微调版） |
| 渠道 | PyPI `laya` 0.3.4；[HF Space demo](https://huggingface.co/spaces/convaiinnovations/laya-demo)；MLX 移植 [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx)（6,604★，M3 Max 7.4–13.4 ms/问）；本地服务化 [ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya)（916★，TypeSafe 兼容 API） |
| 架构 | 双向编码器 + `[MASK]` 位置对各选项打分再 softmax；**一次前向回答全部问题**，答案空间请求时定义 |
| 训练 | 自述 RLCD（严格适当评分规则奖励、GRPO 风格策略梯度），附 Kaggle 2×T4 微调 notebook；**训练数据未公开**（仅披露 AG News/BoolQ 在训练混合中） |
| 文档 | 无独立论文；技术文档 = 模型卡 + `BENCHMARKS.md` |

**项目方自测基准（T4，对 JEV 官方公布数字）**：

| 指标 | JEV 1.13.0（公开数字） | Laya（routed） | 备注 |
|---|---|---|---|
| typed-decisions（2,000 决策） | 0.727 | **0.766** | 该 checkpoint 在同一 benchmark 的训练 split 上微调过 |
| AG News（4 标签） | 0.910 | **0.950** | 在训练混合中 |
| DAIR Emotion（6 标签） | 0.480 | **0.595** | held-out；JEV 在 **16% 样本上给真实标签零概率** |
| Banking77（>20 选项） | **0.870** | 0.425 | **JEV 反超**：Laya 选项共享固定 token 预算 |
| ECE（越低越好） | 0.246 | **0.081** | Laya 需先温度拟合；**出厂原始 ECE 0.213 反而比 JEV 差** |
| p50 延迟（单问） | 236–276 ms | **32.8 ms** | 约 7.8× |
| 许可证 | 闭源 API | **Apache-2.0** | — |

**可信度评估**：JEV 一侧的数字有独立出处（[AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) 等实测 JEV AG News 0.910 / Banking77 0.870 / p50 236–256ms）；**Laya 一侧的全部精度数字目前只有项目方自测**，尚未见到高关注度的独立复测。

**Laya 自己承认的局限（诚实度高于生态平均）**：

- **base checkpoint zero-shot 接近随机**：typed-decisions 上 0.362（多数类基线 0.461）；**0.766 完全来自微调**——它是"适合微调的快速底座"，不是开箱即用的决策引擎。
- **>20 个选项退化**：77 选项时每个标签只剩 3–4 个 token（`head_max_len` 默认 192/256），Banking77 掉到 0.425；需调大预算或做两阶段层级选择。
- **`score` 最弱**（SST-5 0.372）；**出厂过自信**，且 `laya-multilingual` 完全没附带拟合好的温度参数。
- **多语言不能只靠单 checkpoint**：英文 checkpoint 在 51 种语言上 macro 仅 0.227、macro ECE 0.733，**高棉语以 95.2% 置信度给出 0.000 分**；切换未预加载模型会触发 7–10s 重载。
- **soft 分布质量仍不如 JEV**（0.471 vs 0.580）。

### 4.2 其他自训 / 适配方案（L2 层，均未见第三方复跑）

| 项目 | 自训了什么 | 对 JEV 的相对位置 |
|---|---|---|
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | Qwen3-0.6B + decision heads，**权重与数据全公开** | ViZDoom 128/128 vs 56/128；Maze 4/10 vs 7/10（自曝落后） |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | Qwen3.5 三个尺寸 + LoRA rank 16 | 准确率 0.812 vs JEV 0.857，**但 Brier 0.291 不如 JEV 0.211** |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | Qwen3.5-9B + LoRA（仅 answer token） | 324 条 held-out：Nimble-9B 90.1%、base 66.4%、**JEV 93.2%** |
| [wfzyx/von](https://github.com/wfzyx/von) | ModernBERT-Large 395M + RLCD 后训练 | 自报 T=1.1692；README 内部两处数字矛盾 |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | ModernBERT-base 151M + 双置信头 | 自报 ECE 1.44%（仅项目方 test receipt） |
| [Mapika/decider](https://github.com/Mapika/decider) | 含 calibration-aware RL | 未核实独立复跑 |
| [togethercomputer/tev1](https://github.com/togethercomputer/tev1) | Qwen3.5-4B LoRA SFT（37,840 样本），**Together AI 官方** | 自报 880/1,000 主决策、300/300 策略迁移；**只输出答案字母、不给概率** |
| [allebee/jevk5](https://github.com/allebee/jevk5) | 自称 open-weight 替代（Apache-2.0） | 123★（09-29）；细节与 benchmark 未核实 |

### 4.3 谱系核实："2025 年 3 月那篇 RL 论文"是真的吗？

- 论文存在：[arXiv:2503.23303 SalesRLAgent](https://arxiv.org/abs/2503.23303)（2025-03-30，与 Laya 同一作者），PPO 训练销售对话转化概率模型、85ms 推理——**概念谱系属实**，但只是 11KB 短文、领域狭窄。
- 传闻中"当时就开源了权重、数据集与 PyPI 包"**未能核实**：HF 上找不到对应模型或数据集，PyPI 候选名均 404。

### 4.4 传统方案在"严格 schema + 要概率"场景里的实际价值

| 方案 | 概率质量 | 需要的标注量 | 延迟量级 | 适用性 |
|---|---|---|---|---|
| [ModernBERT](https://huggingface.co/answerdotai/ModernBERT-base) + 分类头（Apache-2.0） | 温度缩放后 ECE 约 0.02–0.08（**文献经验值，未独立核实**） | 每个 schema 数百–数千条 | GPU 数 ms–数十 ms | 类别固定、有标注时的首选 |
| Embedding（如 [mmBERT](https://huggingface.co/jhu-clsp/mmBERT-base)）+ 阈值 | 相似度**不是概率**，需 Platt/isotonic 拟合 | 数十条即可 | CPU 10–50 ms | 中等精度的路由/去重 |
| Zero-shot 判别（如 GLiNER2.5） | 无校准保证 | 0 | GPU 数十 ms | 快速原型，第三方实测精度明显低于 JEV |
| 微调小生成模型输出 JSON | 自述 confidence **无校准保证** | 数百–数千条 | 100 ms–1 s | 同一次调用要混合"判断 + 生成"时才有优势 |

**一句话**：有标注数据时，"微调一个编码器分类器"在延迟、成本、可校准性上通常优于任何决策模型；决策模型的真正价值在于**免训练的多次判断 + 不生成文本的确定性接口**。

---

## 🧭 5. 选型建议 / Selection Guide <a id="s5-selection-guide"></a>

> *EN — Use hosted JEV to validate the "typed decision" pattern quickly; go local (L1/L2) when offline or data-residency matters; only Laya is a genuine self-hosted model and must be fine-tuned and temperature-fitted; with labels, a fine-tuned encoder classifier is often cheapest and best-calibrated. Always pin the model version and measure the abstain rate.*

### 5.1 按场景决策

| 你的场景 | 建议 | 理由与注意 |
|---|---|---|
| 几小时内验证"类型化决策"是否适合业务 | **直接用云端 JEV**（Playground + API） | 免训练；先用自己的 50–200 条样本测准确率、弃权率、校准 |
| 数据不能出境 / 必须离线 / 内网 | **L1/L2 方案**：SemIf-OpenJev、kev、simple-jev、jevmlx、von、NanoJev | 目标是"接口范式"而非官方精度；务必自测**本地 vs 云端的一致率** |
| 有标注数据、长期自托管控成本 | **Laya（微调 + 温度拟合）**，或**微调 ModernBERT 类编码器** | Laya base checkpoint 接近瞎猜（0.362 vs 随机 0.318），价值全在微调 |
| 单问题选项超过 20–50 个 | **JEV 仍占优**（Banking77：0.870 vs Laya 0.425），或**两阶段"先粗分再精选"** | Laya 选项共享固定 token 预算，77 选项时每标签只剩 3–4 个 token |
| 只要"是/否"，量很大 | **先拿 TF-IDF / 传统分类器做基线** | Arize 实测：JEV 98.3% vs TF-IDF 98.4%，**统计上无差异** |
| 中文等非英语场景 | ⚠️ **必须自测** | 官方承认 CJK "能用但不等同"；中文独立实测 64–65.2%，强模型组垫底 |
| 需要精确数值/算术/日期比较 | ⚠️ **不要让模型做** | 官方 jaggedness 页明确列为失败模式 |
| 实时交互（语音、游戏循环） | 可以用，先量 p95 | 独立实测 p50 314ms / p95 399ms；参考 `jev-ultrafast`、`fast-jev-compaction` 用法 |

### 5.2 上线前的 7 条检查清单

1. **建基线**：用真实样本跑"传统分类器 / 规则 / 现成 LLM"三条基线，别只看 JEV 自己的分数。
2. **量弃权率**：设阈值后统计"置信度不足"分支占比；有效成本 ≈ 单价 / (1 − 弃权率)。
3. **验校准**：在自己的数据上算 ECE 与可靠性曲线；必要时按 (问题类型 × 选项数) 分桶重拟温度参数。
4. **给失败模式留降级路径**：算术、日期、间接推理、长 state 干扰这四类别交给它。
5. **锁版本**：官方别名会漂移，生产环境 pin `jev-1.13.0` 这类版本化 ID。
6. **数据合规**：确认 `state` 是否带入个人信息；官方已核实不训练客户数据（09-29），但 **ZDR 仅企业版**。
7. **选开源方案先看三件事**：许可证（见 §6 风险 6）、最近提交时间、README 里有没有 Limitations 章节。

---

## ⚠️ 6. 风险清单 / Risk Checklist <a id="s6-risks"></a>

> *EN — Eight risks, one line each: vendor lock-in, data compliance, irreproducible official numbers, two-sided calibration, abstain-rate cost collapse, open-source licensing gaps, ecosystem inflation, and the "is it just a classifier wrapper" question.*

| # | 风险 | 一句话 | 应对 |
|---|---|---|---|
| 1 | **供应商锁定** | 闭源、无微调、别名会漂移；模型不行只能靠改 schema/拆问题/加规则绕 | pin 版本化 ID；判据写进 criteria；保留本地降级方案 |
| 2 | **数据合规** | 纯云端、`state` 必出网；官方不训练客户数据（09-29 核实）但 **ZDR 仅企业版**；大陆可用性报道与官方条款不一致 | 敏感场景先确认 DPA/ZDR；考虑本地方案 |
| 3 | **官方数字不可复现** | 同一家公司 4 个互相矛盾的倍数口径；参考答案非人工标注；KV-cache 机制**纯属第三方推断**（官方文档零提及） | 容量规划用第三方实测（5–25×），不用官方首页 |
| 4 | **校准双面** | 不可知任务上过度自信（ECE 0.107 = 噪声底 4.4 倍）；官方 `confidence` 字段不如 `max(probabilities)`；问题与其否定概率之和可 ≠ 1 | 用自己的数据算 ECE；阈值用 `max(probabilities)` |
| 5 | **弃权率吃掉成本** | 实测 30% 弃权 → 76× 成本优势变 3.2×；天花板 = `1/弃权率` | 上线前先测弃权率；state 给足（实测加 3 个字段弃权率 −25pp） |
| 6 | **开源许可证缺口** | 无 license（采用有法律风险）：`yibie/awesome-jev`（1,950★）、`bespokelabsai/nimble`（1,897★）、`ekzhang/openjev-sglang` 等；NanoJev 的 HF 权重未声明许可证 | 采用前查 license 字段（`featherless-ai/simple-jev` 已于 09-28 补 Apache-2.0） |
| 7 | **生态注水** | 仓库 8 天翻倍至 14,028；真正能跑的约 20–25 个；目录站 star 系统性偏低 | 信 `gh api` 不信目录站；警惕同日批量提交 |
| 8 | **路线级质疑** | "不生成文本"不构成护城河（严格 JSON schema 的强模型同样零幻觉）；但也有黑盒探针显示它**不是**简单的"独立 logits + softmax"包装 | 评估价值看 **延迟 × 成本 × 概率质量** 三项组合，不看单点 |

---

## 📎 7. 附录：核实方法、未核实清单与参考链接 / Appendix <a id="s7-appendix"></a>

> *EN — Repo metadata pulled live with `gh api` on 2026-09-21 and refreshed 2026-09-29; official docs/eval pages fetched and parsed directly (raw notes in `research/`). Reproducible with the commands in 7.4.*

### 7.1 本仓库内容

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

### 7.2 证据分级说明

| 标记 | 含义 |
|---|---|
| 【官方】 | 来自 typesafe.ai / docs.typesafe.ai / evals.typesafe.ai 等官方站点，本次直接抓取 |
| 【第三方】 | 独立测试者、媒体、分析者发布，本次未复跑 |
| 【项目方自测】 | 某个开源仓库作者自己公布的 benchmark，无第三方复跑 |
| 【未核实】 | 只有二手转述、或来源互相矛盾、或原页不可达 |

### 7.3 明确未核实 / 存疑清单

| 事项 | 状态 |
|---|---|
| Business Wire 融资新闻稿全文、The Register 原文 | 抓取失败（403 / 不可达），仅通过转载引用 |
| TypeSafe 约 2 亿美元估值 | 单一第三方来源 |
| 官方参数量、架构、训练数据、KV-cache 与批处理机制 | 官方未公开，**任何"官方 KV-cache 广播"的说法均为第三方推断** |
| 各官方页面的倍数口径（193.6×/444.6×/40×–200×/40×–1,000×） | 官方自己互相矛盾，无法复现其方法学 |
| "36 小时清掉 14 万 waitlist"、"100% 合成数据训练" | 二手转述 / 明确标注为 rumor |
| `wfzyx/von` 的 T 值、训练集规模、引用的 arXiv 条目 | 仓库内自相矛盾 / arXiv 条目**未核实存在** |
| `Heman10x-NGU/openJev-verdict-2.0` 的 ECE 1.44%、NanoJev/kev/nimble 的全部 benchmark | 项目方自测，未见第三方复跑 |
| APUS"全球最早一批 / 国内首批" | 媒体 + 项目方口径，无法独立核实 |
| 生态规模（7,330→**14,028** / 503 / 386 / 195 …） | 三种口径互不一致，引用需注明来源 |
| 所有复现项目的加速倍数 | **本报告未对任何仓库做实际跑测** |
| ~~官方是否有零数据保留、是否默认用于训练~~ | **已于 2026-09-29 在官方 Models 页核实**：不训练客户请求/响应；ZDR 仅企业版 |
| `togethercomputer/tev1`、`allebee/jevk5`、`Liuziyu77/Valen` 的 benchmark 与细节 | 09-23 后新出现，**仅取元数据与 README，未做跑测** |

### 7.4 如何复现本报告的数据

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

### 7.5 主要参考链接

**官方**
- 官网 <https://typesafe.ai/> · 发布博文 <https://typesafe.ai/blog/introducing-system-one-models-and-jev> · 团队 <https://typesafe.ai/team>
- 文档：<https://docs.typesafe.ai/api> · `/models` · `/primitives` · `/concepts/system-one` · 失败模式 <https://docs.typesafe.ai/model-jaggedness/jev-1.13>
- 评测页 <https://evals.typesafe.ai/> · Agent Skill <https://github.com/typesafe-ai/skills>

**第三方独立评测**
- LangChain <https://www.langchain.com/blog/building-a-harness-with-jev> · Arize <https://arize.com/blog/typesafe-jev-llm-judge/> · Capital & Compute <https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/> · bigbangindex <https://bigbangindex.com/blog/typesafe-jev-cost-latency-analysis>
- 中文：央广网 <https://tech.cnr.cn/techph/20260920/t20260920_527819594.shtml> · 量子位 <https://www.qbitai.com/2026/09/492939.html>

**开源项目**
- Laya <https://github.com/NandhaKishorM/laya>（权重 <https://huggingface.co/convaiinnovations/laya>，MLX 移植 `mizorewww/laya-mlx`）
- SemIf-OpenJev（原 OpenJev）<https://github.com/TheoLeeCJ/SemIf-OpenJev> · mini-jev <https://github.com/r-ms/mini-jev> · jevlike <https://github.com/vinnylarouge/jevlike> · jevmlx <https://github.com/bnsd55/jevmlx> · NanoJev <https://github.com/TianyuCodings/NanoJev> · kev <https://github.com/jaredpalmer/kev> · nimble <https://github.com/bespokelabsai/nimble> · von <https://github.com/wfzyx/von> · openjev-sglang <https://github.com/ekzhang/openjev-sglang> · simple-jev <https://github.com/featherless-ai/simple-jev> · jev-ultrafast <https://github.com/browser-use/jev-ultrafast> · fast-browser-use <https://github.com/APUS-AI-Lab/fast-browser-use> · tev1（Together AI）<https://github.com/togethercomputer/tev1> · ollaya <https://github.com/ollaya-dev/ollaya> · Valen <https://github.com/Liuziyu77/Valen>
- 生态目录：<https://jevbest.com/zh/> · <https://madewithjev.com/github-repos> · <https://github.com/logicrw/awesome-jev-projects> · <https://github.com/yibie/awesome-jev>

**对比图说明**：本报告不提供"谁最快"的单一结论表，因为官方口径互相矛盾、第三方测试任务各不相同、且所有开源项目的数字均未经独立复跑。做选型时请以**你自己数据上的实测**为准。

<div align="center">

<sub>本报告由 AI 调研代理搜集整理，所有数字均标注了来源类型与核实状态 · 文本采用 [CC BY 4.0](LICENSE) 许可 · 引用格式见 [CITATION.cff](CITATION.cff)</sub>

<sub>发现错误欢迎提 [Issue](https://github.com/Chorylee7/JEV/issues) 或 PR 修正</sub>

</div>
