# JEV 调研报告：System One 决策模型与开源对标

**JEV Research Report: TypeSafe's System One Decision Model and Its Open-Source Alternatives**

| | |
|---|---|
| 核实日期 / Verified | 2026-09-21 |
| 数据来源 / Sources | 官方文档、官方评测页、GitHub API（`gh api` 当日快照）、第三方独立评测、中文媒体 |
| 证据分级 / Evidence tags | 【官方】官方发布 · 【第三方】独立测试/媒体 · 【项目方自测】仓库作者自报 · 【未核实】未能找到一手来源 |
| 重要提醒 / Caveat | 本报告所有 star、许可证、fork 数据均为 2026-09-21 的 GitHub API 快照，会分钟级漂移；所有 benchmark 数字**除注明外均为项目方或厂商自报，本报告未做任何实际跑测**。 |

---

## 摘要 / TL;DR

> **EN** — JEV is not a chat model. It is a hosted "System One" decision model from TypeSafe AI (San Francisco, founded 2024, $40M seed led by DCVC, released 2026-09-15). You send a `state` plus typed questions; it returns structured answers with probabilities and never writes free text. Weights are closed; API-only. Official headline claims (193.6× faster / 444.6× cheaper) are contradicted by other numbers on TypeSafe's own pages (40×–200×, 20×–200×, 40×–1000×), and independent tests land between 5×–25× on speed and 8.6×–580× on cost. Open source split into two camps: **interface reproductions** (read option-token logits from a frozen LLM, skip autoregressive decoding) and **genuinely retrained open-weight decision models** (Laya is the standout: Apache-2.0, ModernBERT-class, ~33 ms, post-finetune 0.766 vs JEV's 0.727 on typed-decisions — but it collapses on questions with more than ~20 options).

- **JEV 不是聊天模型，而是"决策模型"**：输入程序状态 + 若干**类型化问题**，一次调用返回带概率的结构化判定，不生成任何自由文本。属于 TypeSafe AI（旧金山，2024 年成立），2026-09-15 发布，种子轮 4000 万美元（DCVC 领投）【第三方+官方新闻稿】。
- **只有三种原语**：`noul`（是非题，返回 0–1 概率）、`choice`（最多 255 个选项的单选）、`score`（2–10 级有序评分）。**没有** ranking / span 类型，也**不支持流式**。
- **定价与规格**：$0.042 / 百万 input token（output 免费）、限速 250k tokens/秒 + 1,200 请求/分钟、单请求 64k 上下文、**输入仅文本**（不支持图像/音频/视频）、权重未开源且不做 per-customer 微调。
- **官方数字自相矛盾**：首页写 193.6× 快 / 444.6× 便宜，发布博文写 40×–200×，非公开 onboarding 页写 20×–200× 与 40×–1,000×。第三方独立实测：速度 **4.8×–25×**，成本 **8.6×–580×**，没有一家复现出 444.6×。
- **效果高度任务依赖**：官方自测四个工作流里，JEV 平均 67.8%（落后 GPT-5.6 Sol 74.1%），其中**发票处理 61.8% 在 9 个模型里排第 8**（仅胜 Haiku 4.5）——这是"JEV 不是通解"最硬的证据，且出自官方自己的评测页。
- **官方主动披露的失败模式**：算术与计数、日期比较、间接推理、大 state 干扰、对抗内容等 9 类（`jaggedness` 页）；并承认**同一个问题与其否定答案的概率之和可以 ≠ 1**（官方示例 0.72 + 0.47 = 1.19）。
- **开源生态分两派**：① **接口复现**——把现成开源模型冻结，只读候选答案 token 的 logits 并做受限 softmax，跳过自回归解码（SemIf 2.5k★、`browser-use/jev-ultrafast` 12.6k★、NanoJev 1.5k★、kev 1.2k★ 等）；② **真正自训并开放权重**——Laya（Apache-2.0，三个 checkpoint，T4 上单问 32.8–39.5 ms）是唯一在公开基准上正面压过 JEV 的开源方案，但它的 base checkpoint 在 zero-shot 下**接近瞎猜**，且 20 个以上选项的场景明显退化。
- **选型结论**：把 JEV 当"免训练的快速决策层"是合理的；但把官方 200×/400× 当作规划前提是有风险的。生产环境至少要实测三件事：**你任务上的准确率、弃权率（实测 30% 弃权即可把 76× 成本优势压到 3.2×）、概率在你数据上是否真的校准**。长期自托管优先考虑 Laya（配合微调与温度拟合）或"小模型 + 严格 JSON schema"，而不是直接套用任何复现项目的宣传数字。

**目录 / Contents**

1. [JEV 是什么](#1-jev-是什么--what-is-jev)
2. [官方主张 vs 独立验证](#2-官方主张-vs-独立验证--official-claims-vs-independent-evidence)
3. [开源生态全景](#3-开源生态全景--the-open-source-landscape)
4. [真正自训并开放权重的决策模型](#4-真正自训并开放权重的决策模型--genuinely-retrained-open-weight-models)
5. [选型建议](#5-选型建议--selection-guide)
6. [风险与局限](#6-风险与局限--risks-and-limitations)
7. [附录：核实方法、未核实清单与参考链接](#7-附录核实方法未核实清单与参考链接--appendix)

---

## 1. JEV 是什么 / What is JEV

> **EN** — JEV is TypeSafe AI's "System One" model: a hosted, text-in/structured-out decision service, not a generative LLM. Its API is a single endpoint (`POST /v1/systemone`) taking `state` + `questions` and returning typed answers. Only three question primitives exist. It cannot write text, cannot explain itself, has no world knowledge beyond the supplied state, and is English-first. Weights are not published and no paper exists.

### 1.1 一句话定义

官方对 System One 的定义是：模型**不写回复、不产代码、不生成推理过程**，只在调用方给定的结构化模式里返回带概率的判定【官方：<https://docs.typesafe.ai/concepts/system-one>】。因此它和"用 LLM 输出 JSON"在**接口形态**上相似，区别在于：

| 维度 | 传统 LLM | JEV（System One） |
|---|---|---|
| 输出 | 自回归生成 token 流 | 一次前向/并行计算，直接给结构化答案 |
| 是否可解释 | 可以生成 reasoning | **不生成任何解释性文本** |
| 世界知识 | 有 | **无**，只了解你传入的 `state` |
| 流式 | 支持 | **不支持**（Pydantic AI 集成文档原话："nothing to stream"）|
| 概率 | 需自取 logits | 原生返回 `probabilities` / `confidence` |
| 权重 | 开源可选 | **闭源**，仅托管 API |

### 1.2 公司与时间线

| 项 | 内容 | 证据 |
|---|---|---|
| 公司 | TypeSafe AI，旧金山（Embarcadero 附近），2024 年成立，全员 in-person 五天 | 【官方】<https://typesafe.ai/team> |
| 创始人 | Diogo Almeida（CEO，前 OpenAI/Google Brain，InstructGPT 论文作者之一）；Erik Gafni（CTO）；Sasha Sheng（COO，前 Meta/FAIR） | 【官方】发布博文 + 媒体 |
| 融资 | 4000 万美元种子轮，DCVC 领投（Business Wire 2026-09-15 公告；原文抓取 403，全文**未核实**） | 【官方新闻稿】`businesswire.com/news/home/20260915525333/en/` |
| 估值 | 报道称约 2 亿美元 | 【第三方，单一来源，**未核实**】 |
| 发布时间 | 官方博文时间戳 **2026-09-15**；部分媒体记 9/14 或 9/16（报道日） | 【官方】<https://typesafe.ai/blog/introducing-system-one-models-and-jev> |
| 当前版本 | `jev-1.13.0`，别名 `jev-latest` / `jev-preview` 均指向它 | 【官方】<https://docs.typesafe.ai/models> |
| 官方附带产物 | `github.com/typesafe-ai/skills`（Agent Skill，MIT，1,259★，**创建于 2026-08-24，早于公测**） | 【GitHub API】 |

### 1.3 API 契约（字段级）

端点：`POST https://api.typesafe.ai/v1/systemone`【官方：<https://docs.typesafe.ai/api>】

请求体三个字段：

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

关键设计：`questions` 是**由你命名的 map**——key 只用于对齐请求与响应，**不会发送给模型**；同一个 `state` 上的所有问题被**并行、独立**评估，官方原话是"Adding questions barely changes the response time"【官方】。

响应体：

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

**三种原语（官方就是全部，没有第四种）**：

| 原语 | 语义 | 返回 | 适用场景（官方举例） |
|---|---|---|---|
| `noul` | 是非题 | 单个 0–1 概率，**没有 `confidence` 字段** | 钓鱼检测、垃圾邮件、越狱检测、流失风险 |
| `choice` | 单选，**最多 255 个选项** | `choice` + `probabilities`（和为 1）+ `confidence` | 意图分类、路由、标签 |
| `score` | 有序评分，**2–10 级** | `score`（**可以是级别之间的值**，如 `1.05`）+ `legend` + `probabilities` + `confidence` | 严重性、质量、紧急度 |

> 常见误解：**JEV 没有 `ranking` 和 `span` 类型**；`boolean` 只是某些渠道（如 Vercel）对 `noul` 的别名。

### 1.4 定价、限速与硬限制【官方：<https://docs.typesafe.ai/models>】

- 价格：**$42 / 十亿 input token = $0.042 / 百万**，**output token 免费**（因为不生成 token）。
- 限速：250,000 tokens/秒、1,200 请求/分钟；官方注明"动态调整、可不另行通知"。
- 上下文：单请求 64k，其中 `state` + 最长单条问题 ≤ 32k。
- 输入模态：**仅文本**（string / JSON object / 文本数组）。不支持图像、音频、视频。
- 语言：英语最佳；官方承认"CJK 等其他语言能用，但效果并不同等"。
- 权重与微调：**闭源**；官方明确"所有账号共用同一套权重，不做 per-customer 微调/LoRA"。
- 价格可持续性：官方自己写了一句罕见的坦白——"**我们无法证明它没有被补贴**"。
- 地区可用性：央广网 2026-09-20 报道"该服务尚未向中国大陆地区开放"【第三方】；但官方文档与服务条款中**未见任何地区/出口管制条款**（本次已 grep 核实），因此这条**以官方口径论仍属未证实**。

### 1.5 官方承认的能力天花板

官方专门有一页 `Jev 1.13 jaggedness`【官方：<https://docs.typesafe.ai/model-jaggedness/jev-1.13>】列出 9 类失败模式，其中几条对工程决策影响很大：

- **字面理解**：不会按常识补全你的意图；
- **算术与计数**：明确不可靠；
- **日期/时间比较**、**多跳间接推理**：弱；
- **大 state 里塞满无关细节**：会被干扰；
- **对抗性内容**、**instructions 与 criteria 互相矛盾**：会被带偏；
- **结构不变量**：不保证满足"总数守恒"这类约束；
- **生成类任务**：直接不支持；
- **概率不是逻辑一致的概率**：同一问题与其否定的概率之和**不必等于 1**（官方示例 0.72 + 0.47 = 1.19）；`score` 的数值校准很弱，**不能**通过插值还原精确数字。

### 1.6 有趣的官方 Demo

- **Doom**：官方博文称以约 **10 queries/秒**、约 **$7/小时** 的成本驱动；输入是**文字化的结构化游戏状态，不是画面**，官方还自嘲"一个非 AI 的 Doom bot 能玩得更好"。
- **Wikiracing**：每一步在数百至数千个链接中做 `choice`；链接数超过 255 时改用"两阶段评分 + 选择"绕开上限。

---

## 2. 官方主张 vs 独立验证 / Official Claims vs Independent Evidence

> **EN** — TypeSafe's marketing numbers vary by page (193.6×/444.6× on the homepage, 40×–200× in the launch post, 20×–200× and 40×–1000× in the gated onboarding page). Eight independent tests published between 09-15 and 09-19 land at 4.8×–25× on latency and 8.6×–580× on cost. Accuracy is highly workflow-dependent: JEV ranks 8th of 9 on the invoice-processing workflow in TypeSafe's *own* eval page. The two most useful independent findings are that a 30% abstain rate collapses the cost advantage from 76× to 3.2×, and that on tasks where the model cannot know the answer it is severely overconfident (ECE 0.107 vs a 0.024 noise floor).

### 2.1 速度与成本：官方自己就有四个版本

| 来源 | 速度倍数 | 成本倍数 | 类型 |
|---|---|---|---|
| TypeSafe 首页 | 193.6× | 444.6× | 【官方】 |
| TypeSafe 发布博文 | 40×–200× | 未公布 | 【官方】 |
| TypeSafe early-access onboarding（需登录） | 20×–200× | **40×–1,000×** | 【官方】 |
| 按官方 evals 表手算 | 约 25×–95× | 76×–440× | 【第三方推算】 |
| Every | 约 25× | 约 580× | 【第三方独立】 |
| Near Here | — | 8.6×（vs Mistral Small 4）/ 58×（vs Gemini Flash-Lite） | 【第三方独立】 |
| gemanor | 4.8×–5.7× 时延 | 45× / 274× | 【第三方独立】 |
| 4esv/jev-eval | 5× | 41×–50× | 【第三方独立】 |
| 硅星人（中文实测） | 0.73–0.75s vs DeepSeek V4 Flash 5.58s | 50 题 $0.002 | 【第三方独立】 |
| Capital & Compute | p50 314 ms / p95 399 ms（复现官方 70–500ms 区间） | $0.0238/千次 | 【第三方独立】 |

**怎么读这张表**：444.6× 是"只与最贵的 Claude Opus 5 那一行比"得到的；官方首页与博文口径差了近一个数量级；第三方实测的中位数落在 **5×–25× 速度、10×–60× 成本**。这不代表 JEV 不快——314 ms p50 的实测确实存在——而是**"200×/400×"不能当作容量规划的输入**。

### 2.2 准确率：官方评测页里最扎眼的一格

官方 evals 页【官方：<https://evals.typesafe.ai/>】四个工作流、9 个模型的对比（本报告直接从该页 HTML 解析，非媒体转述）：

| 工作流 | JEV | 该工作流最佳 | JEV 排名 | JEV 成本排名 |
|---|---|---|---|---|
| Security Incidents | 61.7%（$0.0001, 0.3s） | Opus 5 workflow 66.2% | 第 3 | **最低** |
| **Invoice Processing** | **61.8%**（$0.0011, 0.5s） | Sol workflow 79.1% | **第 8（仅胜 Haiku 4.5）** | 第 2 |
| Customer Service | 76.0%（$0.0001, 0.4s） | Sol workflow 78.3% | 第 4 | **最低** |
| Agent Trace Observability | 71.6%（$0.0003, 0.5s） | Sol workflow 76.6% | 并列第 6 | **最低** |
| **四者平均** | **67.8%** | Sol workflow 74.1% | — | **最低** |

发票处理这一格里，JEV 输给包括最便宜模型 Luna（67.8%）与 DeepSeek V4 Flash（69.8%）在内的 8 个模型。

**第三方准确率对照（节选）**：

| 测试 | 任务 | JEV | 对照 | 结论 |
|---|---|---|---|---|
| LangChain（09-20） | 500 次重复的二元判定，对照人类 oracle | **100%（500/500）** | Terra 99.8% / Luna 96.4% / Claude Sonnet 4.6 80.0% | **JEV 第一，方差最低**；总成本 $0.34 vs Claude $28.17 |
| Arize AI | 18,514 封带真实标签的邮件 | 98.3% | **TF-IDF 分类器 98.4%** | 统计上**持平**（这是唯一有 ground truth 的大型独立测试） |
| gemanor | 1,080 次 Python 规则审查 | 98.0% | Gemini / Fable 5.1 均 100% | 落后 2 点 |
| 4esv | 77 类意图 | 0.78 | Terra 0.85 | 落后 7 点 |
| 硅星人（中文） | 50 条中文客服（4 项全对才计分） | **64–65.2%** | 便宜组第一比它高 1.2 分；强模型组 MiniMax M3 高 10.8 点 | **便宜组第二，强组垫底** |
| RINNECODER | 3D 城市驾驶（自测） | **0/12 完整任务** | — | 522 次转向全部选"直行" |
| NanoJev（项目方） | ViZDoom Basic | 56/128（≈ 未微调 Qwen3-0.6B） | NanoJev 128/128 | 对该游戏任务相对裸 base model 无增益 |

### 2.3 官方主动披露的方法学漏洞

官方 evals 页自己写了这些"nuance"，值得逐条记住：

- 评测在**"我们自己团队的笔记本上、美国西海岸"**跑的；
- 工作流由**内部能力团队**构建，"可能存在偏差"；
- **参考答案不是人工标注，而是 GPT-6 Astra 与 Claude Fable 5.1 输出的平均**——"这会偏向 OpenAI 与 Anthropic 的模型"；
- 宣传里的"**0% 类型错误**"不是实测，官方原话是"Our number is not empirical"；
- side-by-side demo 用的 state 很短，"**会让我们的模型显得更好看**"。

### 2.4 两条最值得记住的独立结论

1. **弃权率（abstain rate）是成本杀手**。第三方在真实队列上实测 **30% 的调用来不及给出可用置信度**，按有效成本公式 `blended = M/(1+aM)`，成本优势从 76× 塌缩到 **3.2×**。成本优势的天花板是 `1/弃权率`，与 JEV 单价多便宜无关。
2. **校准是双面的**。在**可知任务**上 JEV 校准不错（OpenBookQA ECE 0.024 = 噪声底；LangChain 500 次重复判定方差最低）；但在**不可知任务**上严重过度自信（自造合成工单 ECE **0.107 = 噪声底的 4.4 倍**，`score` 子任务的温度参数需重拟合到 **3.40**）。此外官方返回的 `confidence` 字段独立测试下来**从未优于 `max(probabilities)`**。

### 2.5 官方自曝的 9 类失败模式（工程上必须设降级路径）

字面理解 · 算术与计数 · 日期时间比较 · 间接推理 · 大 state 含无关细节 · 对抗内容 · instructions 与 criteria 矛盾 · 结构不变量 · 生成任务。另外两条反直觉但重要：**问题与其否定的概率之和不必为 1**；**`score` 不能靠插值还原精确数值**。

---

## 3. 开源生态全景 / The Open-Source Landscape

> **EN** — Within five days of launch, GitHub accumulated thousands of JEV-related repos. Filtering for projects that actually explain the mechanism leaves ~20–25 real reproductions out of ~4,100 created-after-09-01 repos; the rest are skills, wrappers, awesome-lists and same-day bulk submissions. The dominant technique is identical everywhere: freeze an open LLM, read the logits of candidate answer tokens at a single position, apply a restricted softmax, and skip autoregressive decoding. Notably, the projects that measured their own speedup report **4×–5.2×**, not 200× — because a frozen 4B model still has to prefill the state. Almost none of them claim calibrated probabilities; several explicitly disclaim it.

### 3.1 四个层次（先分清类别，否则数字没有可比性）

| 层次 | 定义 | 代表 | 是否本地推理 | 是否有自训权重 |
|---|---|---|---|---|
| L0 客户端应用 | 自己写 prompt/schema，仍调用云端 JEV API | `browser-use/jev-ultrafast`、`tamaratran/fast-jev-compaction`、`perixtar/jev-e2e`、`typesafe-ai/skills` | ✗ | ✗ |
| L1 接口复现 | 冻结现成开源模型，**只读 option token 的 logits** + 受限 softmax，跳过自回归解码 | `TheoLeeCJ/SemIf`、`r-ms/mini-jev`、`bnsd55/jevmlx`、`featherless-ai/simple-jev`、`ekzhang/openjev-sglang` | ✓ | ✗（权重冻结） |
| L2 复现 + 自训 head/adapter | 在 L1 基础上自己训练打分头或 LoRA | `vinnylarouge/jevlike`、`TianyuCodings/NanoJev`、`jaredpalmer/kev`、`bespokelabsai/nimble`、`wfzyx/von`、`Mapika/decider` | ✓ | ✓（部分/适配器） |
| L3 自研决策模型 | 自己训模型、发权重与数据 | **Laya**（见第 4 章） | ✓ | ✓ |

**这一区分很关键**：L1/L2 的所有"加速倍数"都建立在"**跳过解码**"上，而**state 的 prefill 成本省不掉**。所以它们的实测加速是**个位数倍数**，而不是 200×。

### 3.2 核心项目对照表（star 为 2026-09-21 GitHub API 快照）

| 仓库 | ★ | 许可证 | 底座模型 | 硬件 | HTTP 服务 | 自称校准 |
|---|---:|---|---|---|---|---|
| [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | **12,600** | MIT | 云端 JEV + `inception/mercury-2.5` | 任意 | — | — |
| [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | **5,380** | MIT | 云端 `jev-latest` | 任意 | — | **明确否认** |
| [TheoLeeCJ/SemIf](https://github.com/TheoLeeCJ/SemIf)（原名 OpenJev） | **2,525** | MIT | Qwen3.5-4B / MiniCPM5-2B / Qwen3-0.6B（冻结） | CUDA / Apple MLX / WebGPU | demo | 要求用户自行校准 |
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | **1,522** | MIT | Qwen3-0.6B + 自训 decision heads | CUDA / CPU | ✓ | — |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | **1,217** | **无** | Qwen3.5-9B + LoRA | CUDA | ✓ | — |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | **1,167** | Apache-2.0 | Qwen3.5-0.8B/4B/9B + LoRA | CUDA / Apple Silicon | ✓ | **明确否认** |
| [vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike) | **1,097** | MIT | 从零训 byte-encoder / Qwen2.5-0.5B 冻结 | CPU / MPS / CUDA | — | 不声称 |
| [featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev) | 404 | **无** | Qwen3.5-0.8B / Gemma 4 26B-A4B / Laya | CPU / CUDA | ✓ | **明确否认** |
| [wfzyx/von](https://github.com/wfzyx/von) | 241 | Apache-2.0 | ModernBERT-Large 395M | CPU / CUDA | ✓ | ✓（T=1.1692） |
| [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) | 239 | **无** | Qwen3.6-35B-A3B（SGLang） | B200 级 | ✓ | — |
| [razorback16/openjev](https://github.com/razorback16/openjev) | 220 | Apache-2.0 | DiffusionGemma 26B-A4B | CUDA | — | — |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | 205 | NOASSERTION | ModernBERT-base 151M + 双置信头 | CPU / WebGPU | — | ✓（ECE 1.44%，自测 receipt） |
| [Mapika/decider](https://github.com/Mapika/decider) | 163 | Apache-2.0 | Qwen3.5-2B/0.8B/35B-A3B | CUDA | — | ✓（calibration-aware RL） |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | 47 | MIT | Qwen2.5-7B/3B/1.5B-4bit（MLX） | Apple Silicon / CPU | ✓ | **明确否认** |
| [ikermoel/open-alternative-jev](https://github.com/ikermoel/open-alternative-jev) | 38 | Apache-2.0 | 任意 open-weights | CUDA | — | ✓（MMLU ECE 5.4%→2.1%） |
| [APUS-AI-Lab/fast-browser-use](https://github.com/APUS-AI-Lab/fast-browser-use) | 35 | MIT | Qwen3.5-9B / 35B-A3B | GPU / 无 GPU 的 Mac/PC | ✓ | — |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | 35 | MIT | Qwen3-4B-Instruct-2507（冻结） | CUDA / MPS | ✓ | **明确否认**（"不是校准概率"） |
| [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) | **5,060** | Apache-2.0 | **自研** ModernBERT 系（≈421M） | CPU / CUDA | SDK | ✓（温度拟合后 ECE 0.081） |

**未列入但值得知道**：[`logan-markewich/jeff`](https://github.com/logan-markewich/jeff)（173★，把 GLiNER 用于决策）、`Heman10x-NGU/Verdict-open-jev`（48★）、`deepanwadhwa/OpenDecision`（42★，NLI 路线）、`fstandhartinger/jevbench`（31★，基准工具）、`Micha0827/snapjudge`（7★，MLX）、`NullPo-jp/PocketJev`（0★，Swift/iOS）。

### 3.3 值得逐个看的几个项目

**`TheoLeeCJ/SemIf`（2,525★，MIT）——生态里最有代表性、也最克制的一个**
- 原名 OpenJev，README 首行已改为 `# SemIf (formerly OpenJev)`（APUS 的 README 仍在引用旧名，属过期信息）。
- 两种模式：**direct**（直接读选项 token 的 logits）与 **shared**（state 只 prefill 一次，KV 复用到并行问题）。
- **自测加速只有 5.21×**（1.023s vs 5.332s，RTX 3090），并明确声明"Jev 的数字读自 TypeSafe 公开记录，**我们没有跑真实 Jev endpoint**"；复现的是 102 行的接口范式，而非官方 711 行的完整实现。
- 支持 CUDA / Apple MLX / **WebGPU（浏览器内跑）**，是少数能在纯浏览器演示的方案。

**`r-ms/mini-jev`（35★）——证据链最规范，结论最不利**
- 有 `PREREG.md`（含 v1.1–v1.3 修正），27,900 条带 logits 的运行记录公开在 HuggingFace。
- 结论：**"读字母 logits"与"语法约束生成 JSON"精度相当（Δ −0.22pp）**，加速仅 **4×（短文本）/ 1.4–2.4×（2048 token + 共享前缀）**。
- 明确写"这些是归一化的候选分数，**不是校准概率**"。

**`TianyuCodings/NanoJev`（1,522★）——唯一自训权重+数据全公开，且保留了打脸自己的那一行**
- Qwen3-0.6B + 自训 decision heads；ViZDoom Basic 上 **128/128，JEV 56/128**；但 Maze 任务 **4/10 反输给 JEV 的 7/10**，README 保留该行未删。

**`jaredpalmer/kev`（1,167★，Apache-2.0）——局限性写得最诚实**
- Qwen3.5-0.8B/4B/9B + LoRA（rank 16）；在 typed-decisions 上 JEV 准确率 0.857 vs kev-9B 0.812，但 **Brier 更优（0.211 vs 0.291）**——即 JEV 的**分布质量**更好。
- 自曝：Apple Silicon 上因缺少 DeltaNet 的快速 kernel，**比上一代模型慢 4–7 倍**。

**`APUS-AI-Lab/fast-browser-use`（35★，MIT）——媒体声量与实际影响力严重背离的样本**
- 央广网、科技日报、新浪等报道其为"全球最早一批 / 国内首批 Jev 跨平台开源复现"，但仓库仅 **35★**，远低于同期社区项目；README 也没有独立的 Limitations 章节。
- 技术上是标准的 L1：把页面上可见可交互元素编号成候选动作集，由本地 Qwen3.5-9B 单次前向打分，单任务约 4 次打分；仅 `TYPE_TEXT` 类动作才真正生成 token。

**`bespokelabsai/nimble`（1,217★）——目前唯一敢把 base model 与 JEV 并列的**
- 324 条 held-out 上：**Nimble-9B 90.1%**，其 base（Qwen3.5-9B）66.4%，**JEV 1.13.0 93.2%**——即"微调小模型能追平但没超过"。

**`ikermoel/open-alternative-jev`（38★）——生态里最诚实的一份 benchmark**
- 唯一公开承认自己算错、并保留错误分析（"The correction that made this README honest"）的项目。

**关于 APUS 的 `fast-browser-use` 与 `browser-use/jev-ultrafast` 的区别**：后者（12.6k★）是 **L0 客户端**，仍然调用云端 JEV，只是把 browser-use 的单步交互压缩成"operation + target 两个 head、一次往返"；它代表的是**用量优化**，不是本地替代。

### 3.4 这些复现项目与官方声称的差距，主要来自三个工程事实

1. **Prefill 省不掉**：跳过解码只省生成本身；state 越长，省下的比例越低（mini-jev：短文本 4× → 2048 token 时 1.4–2.4×）。
2. **没有专用硬件/服务栈**：官方是 70–500 ms 的托管服务（独立实测 p50 314 ms 落在区间内），社区是单卡 RTX 3090 / M 系列 Mac。
3. **推理框架不同**：`ekzhang/openjev-sglang` 用 SGLang 的 radix caching 做 prefill-only，是目前最接近"工程化"的路线之一。

### 3.5 生态噪声警告（引用时必须注意）

- GitHub 上 `q=jev` 约 **7,330** 个仓库，其中 9 月以后新建的约 **4,126** 个【GitHub API】；`topic:jev` 与 `topic:system-one` 各至少 55 个；**awesome-jev 类目录至少 18 个**，多数建于 5 天之内。
- 真正解释了机制、能跑的复现约 **20–25 个**；Reddit 上有人从 **287 个仓库里人工筛出 20 个**（该说法**未核实原文**）。
- 最值得引用的一句社区警告来自 `yibie/awesome-jev` 作者本人：**"对同日批量提交的项目要格外警惕——数量不等于质量。"**
- 生态目录站（`jevbest.com` 503 项、`madewithjev.com`）**都明确声明与 TypeSafe 无关**；其 star 快照**系统性偏低 18–39%**（例如 jev-ultrafast 记 9,291，实际 12,585）。引用生态规模时请注明口径，因为三种口径互不一致。

---

## 4. 真正自训并开放权重的决策模型 / Genuinely Retrained Open-Weight Models

> **EN** — Only one project in this ecosystem actually trained a decision model and published the weights: **Laya** (Apache-2.0, 5,060★, three checkpoints on HuggingFace, ~421M ModernBERT-class encoder with decision heads). It beats JEV's published numbers on typed-decisions (0.766 vs 0.727) and is ~7.8× faster, but every Laya accuracy figure is currently self-reported, its base checkpoints are near chance zero-shot, and it degrades badly above ~20 options. The rest of the "retrained" camp are LoRA/head adaptations of frozen models (L2). The 2025-03 RL non-autoregressive lineage is real (arXiv:2503.23303) but the promised weights/dataset cannot be found.

### 4.1 Laya：生态里唯一"自己训 + 开放权重"的决策模型家族

| 项 | 内容 |
|---|---|
| 仓库 | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)，**5,060★ / 454 fork**，Apache-2.0，创建 2026-09-18 |
| 作者 | Nandakishor Mukkunnoth（Convai Innovations，独立研究者；GitHub 上**没有** convaiinnovations 组织，主仓库挂在个人账号下） |
| 权重 | [convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya)（ModernBERT-large + 决策头，**421M**，英文，HF likes 1,204）、[laya-multilingual](https://huggingface.co/convaiinnovations/laya-multilingual)（mmBERT-base，322M，100+ 语言）、[laya-typed-decisions](https://huggingface.co/convaiinnovations/laya-typed-decisions)（微调版） |
| 发行渠道 | PyPI `laya` 0.3.4、[HF Space 在线 demo](https://huggingface.co/spaces/convaiinnovations/laya-demo)、第三方 MLX 移植 [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx)（**1,938★**，M3 Max 上 7.4–13.4 ms/问） |
| 架构 | 双向编码器 + 在 `[MASK]` 位置对各选项打分再 softmax；**一次前向回答全部问题**，答案空间在请求时定义 |
| 训练 | 自述 **RLCD**（以严格适当评分规则作奖励、GRPO 风格策略梯度），附 Kaggle 2×T4 微调 notebook；**训练数据未公开发布**（仅披露 AG News/BoolQ 在训练混合中） |
| 文档 | 无独立论文，技术文档 = 模型卡 + `BENCHMARKS.md` |

**项目方自测基准（T4，对 JEV 官方公布数字）**：

| 指标 | JEV 1.13.0（公开数字） | Laya（routed） | 备注 |
|---|---|---|---|
| typed-decisions（2,000 决策） | 0.727 | **0.766** | 该 checkpoint 在同一 benchmark 的训练 split 上微调过 |
| AG News（4 标签） | 0.910 | **0.950** | 在训练混合中 |
| DAIR Emotion（6 标签） | 0.480 | **0.595** | held-out；JEV 在 **16% 样本上给真实标签零概率** |
| Banking77（>20 选项） | **0.870** | 0.425 | **JEV 反超**，原因是 Laya 选项共享固定 token 预算 |
| ECE（越低越好） | 0.246 | **0.081** | Laya 需先做温度拟合；**出厂原始 ECE 是 0.213，反而比 JEV 差** |
| p50 延迟（单问） | 236–276 ms | **32.8 ms** | 约 7.8× |
| 许可证 | 闭源 API | **Apache-2.0** | — |

**可信度评估（重要）**：JEV 那一侧的数字有独立出处（[AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) 等实测 JEV AG News 0.910 / Banking77 0.870 / DAIR 0.480 / p50 236–256 ms），但 **Laya 侧的全部精度数字目前只有项目方自测，尚未见到高关注度的独立复测**。

**Laya 自己承认的局限（诚实度高于生态平均水平）**：
- **base checkpoint 在 zero-shot 下接近随机**：typed-decisions 上 0.362（多数类基线 0.461、随机 0.318）；**0.766 完全来自微调**——它是"一个适合微调的快速底座"，不是开箱即用的决策引擎。
- **超过 20 个选项就退化**：77 选项时每个标签只剩 3–4 个 token（`head_max_len` 默认 192/256），Banking77 掉到 0.425；官方建议调大预算或做两阶段层级选择。
- **`score` 原语最弱**：SST-5 上 0.372。
- **出厂过自信**，且 `laya-multilingual` **完全没有附带拟合好的温度参数**，用之前必须自己拟合。
- **多语言不能只靠单 checkpoint**：英文 checkpoint 在 51 种语言上 macro 仅 0.227、macro ECE 高达 0.733，**高棉语以 95.2% 置信度给出 0.000 分**；因此才需要"路由到不同 checkpoint"，而切换未预加载的模型会触发 7–10 秒重载。
- **soft 分布质量仍不如 JEV**：typed-decisions 上 argmax 更高（0.766 vs 0.727），但软分布准确率更低（0.471 vs 0.580）。

### 4.2 L2 层：自训 head / LoRA 的方案（不是从零训模型）

| 项目 | 自训了什么 | 对 JEV 的相对位置 |
|---|---|---|
| [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) | Qwen3-0.6B + decision heads，**权重与数据全公开** | ViZDoom 128/128 vs 56/128；Maze 4/10 vs 7/10（自曝落后） |
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | Qwen3.5 三个尺寸 + LoRA rank 16 | 准确率 0.812 vs JEV 0.857，**但 Brier 0.291 不如 JEV 0.211** |
| [bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) | Qwen3.5-9B + LoRA（仅 answer token） | 324 条 held-out：Nimble-9B 90.1%、base 66.4%、**JEV 93.2%** |
| [wfzyx/von](https://github.com/wfzyx/von) | ModernBERT-Large 395M + RLCD 后训练 | 自报 T=1.1692；README 内部两处数字矛盾 |
| [Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) | ModernBERT-base 151M + 双置信头 | 自报 ECE 1.44%（仅项目方 test receipt） |
| [Mapika/decider](https://github.com/Mapika/decider) | 含 calibration-aware RL | 未核实独立复跑 |

这些方案值得参考，但都没有第三方复跑，且底座与任务各不相同，**不能横向比较**。

### 4.3 谱系核实："2025 年 3 月那篇 RL 非自回归决策论文"是真的吗？

- 论文存在：[arXiv:2503.23303 SalesRLAgent](https://arxiv.org/abs/2503.23303)（2025-03-30，与 Laya 同一作者），用 PPO 训练销售对话的转化概率模型、85 ms 推理、非自回归概率估计——**概念谱系属实**，但只是一篇 11KB 短文、领域狭窄。
- 传闻中"当时就开源了权重、数据集与 PyPI 包" **未能核实**：HuggingFace 上找不到对应模型或数据集，PyPI 三个候选名字均 404。（后续的 [arXiv:2510.01237](https://arxiv.org/abs/2510.01237) 是另一个主题——LLM 置信度路由与幻觉缓解。）

### 4.4 传统方案在"严格 schema + 要概率"场景里的实际价值

| 方案 | 概率质量 | 需要的标注量 | 延迟量级 | 适用性 |
|---|---|---|---|---|
| [ModernBERT](https://huggingface.co/answerdotai/ModernBERT-base) + 分类头（Apache-2.0） | 温度缩放后 ECE 约 0.02–0.08（**文献经验值，未独立核实**） | 每个 schema 数百–数千条 | GPU 数 ms–数十 ms | 类别固定、有标注、追求稳定与低成本时的首选 |
| Embedding（如 [mmBERT](https://huggingface.co/jhu-clsp/mmBERT-base)）+ 阈值 | 相似度**不是概率**，需 Platt/isotonic 拟合 | 数十条即可 | CPU 10–50 ms | 中等精度的路由/去重 |
| Zero-shot 判别（如 GLiNER2.5） | 无校准保证 | 0 | GPU 数十 ms | 快速原型，第三方实测精度明显低于 JEV |
| 微调小生成模型输出 JSON | 自述 confidence **无校准保证** | 数百–数千条 | 100 ms–1 s | 需要同一次调用里混合"判断 + 生成"时才有优势 |

**一句话结论**：如果你有标注数据，"微调一个编码器分类器"在延迟、成本、可校准性上通常都优于任何决策模型；决策模型的真正价值在于**免训练的多次判断 + 不生成文本的确定性接口**。

---

## 5. 选型建议 / Selection Guide

> **EN** — Use hosted JEV when you want to validate the "typed decision" pattern quickly and your data may leave your network. Go local (SemIf / kev / jevmlx / simple-jev / von) when offline or data-residency matters, but measure the accuracy gap yourself. Only Laya is a genuine self-hosted *model*, and it must be fine-tuned and temperature-fitted to be useful. If you have labels, a fine-tuned encoder classifier is often the cheapest and best-calibrated option. Always pin the model version, always measure the abstain rate, and never plan capacity on the advertised speedup.

### 5.1 按场景决策

| 你的场景 | 建议 | 理由与注意 |
|---|---|---|
| 想在几小时内验证"类型化决策"是否适合业务 | **直接用云端 JEV**（Playground + API） | 免训练、月成本低；先用你自己的 50–200 条样本测准确率、弃权率、校准 |
| 数据不能出境 / 必须离线 / 内网部署 | **L1/L2 方案**：SemIf、kev、simple-jev、jevmlx、von、NanoJev | 目标是"接口范式"而非官方精度；务必自测**本地 vs 云端的一致率** |
| 有标注数据、要长期自托管且控成本 | **Laya（微调 + 温度拟合）**，或 **微调 ModernBERT 类编码器** | Laya base checkpoint 在 typed-decisions 上接近瞎猜（0.362 vs 随机 0.318），价值全在微调；RAG/分类任务上传统分类器常已足够 |
| 单问题选项超过 20–50 个 | **JEV 仍占优**（Banking77：JEV 0.870 vs Laya 0.425），或改用**两阶段"先粗分再精选"** | Laya 的选项共享固定 token 预算（`head_max_len`），77 个选项时每个标签只剩 3–4 个 token，精度崩掉 |
| 只要"是/否"，量还很大 | **先拿 TF-IDF / 传统分类器做基线** | Arize 用 18,514 封真实标签邮件实测：JEV 98.3% vs TF-IDF 98.4%，**统计上无差异** |
| 中文等非英语场景 | ⚠️ **必须自测** | 官方承认 CJK "能用但不等同"；中文独立实测 64–65.2%，在强模型组垫底 |
| 需要精确数值/算术/日期比较 | ⚠️ **不要让模型做** | 官方 jaggedness 页把它们列为明确失败模式 |
| 要做实时交互（语音、游戏循环） | 可以用，但先量 p95 | 独立实测 p50 314 ms / p95 399 ms；`fast-jev-compaction`、`jev-ultrafast` 是参考用法 |

### 5.2 上线前的 7 条检查清单

1. **建基线**：用你的真实样本跑一次"传统分类器 / 规则 / 现成 LLM"三条基线，别只看 JEV 自己的分数。
2. **量弃权率**：设阈值后统计有多少请求会落到"置信度不足"分支；有效成本 ≈ 单价 / (1 − 弃权率)。
3. **验校准**：在你的数据上算 ECE 与可靠性曲线；必要时按 (问题类型 × 选项数) 分桶重拟温度参数。
4. **给失败模式留降级路径**：算术、日期、间接推理、长 state 干扰这四类别交给它。
5. **锁版本**：官方别名会漂移，生产环境 pin `jev-1.13.0` 这类版本化 ID。
6. **数据合规**：确认 `state` 里是否会带入个人信息；官方是否有零数据保留需自行确认（本报告**未找到**相关信息）。
7. **选开源方案时先看三件事**：许可证（见 6.6）、最近提交时间、README 里有没有 Limitations 章节。

---

## 6. 风险与局限 / Risks and Limitations

> **EN** — The main risks are: (1) official throughput/cost multipliers are not reproducible and vary by a factor of ~10 across the vendor's own pages; (2) abstention silently destroys the cost advantage; (3) calibration is task-dependent and the `confidence` field is worse than `max(probability)`; (4) closed weights with no per-customer fine-tuning means you cannot fix systematic errors except by prompt/schema engineering; (5) the open-source side has a real licensing gap (many repos have no license at all) and routinely mislabels itself as "JEV"; (6) the ecosystem is inflated by same-day bulk submissions — volume is not quality.

### 6.1 供应商与架构锁定

- 权重不公开、无微调接口、无本地部署路径：模型说不行的地方，**只能靠改 state 结构、拆问题、加规则绕**，不能靠训练修。
- 别名 `jev-latest` / `jev-preview` 会指向新版本，线上行为可能在你不知情时改变 → **必须 pin 版本 ID**。
- 官方文档里**没有** KV-cache、批量大小、并发模型等任何底层说明（本次对全部官方文档 grep 过，零命中）；"官方支持 KV-cache 广播"的说法**只出现在第三方复现项目的描述里**，属推断而非事实。

### 6.2 数据合规与地区

- 央广网报道"尚未对中国大陆地区开放"【第三方】；而官方文档与条款中**未见地区限制条款**（已 grep 核实）。落地前请自行与官方确认。
- 该服务是**纯云端**，`state` 必然出网。是否有零数据保留（ZDR）、是否默认用于训练，**本报告未找到可靠信息**。
- 中文/多语言能力非其强项（官方自述 + 独立实测均支持该结论）。

### 6.3 官方数字不可直接用于容量规划

- 同一家公司给出 **4 个互相矛盾的倍数**（193.6×/444.6×、40×–200×、20×–200×、40×–1,000×）。
- 官方 benchmark 的"正确答案"是**两个 LLM 输出的平均**，不是人类标注；官方自己承认这会偏向 OpenAI/Anthropic 的模型。
- 官方自己承认评测在内部笔记本上、由内部团队构建工作流、"0% 类型错误"不是实测、demo 用的 state 偏短。
- 唯一有真实 ground truth 的大型独立测试（Arize，18,514 封邮件）显示与 TF-IDF 打平。

### 6.4 校准可信度是双面的

| 结论 | 证据 |
|---|---|
| 可知任务上不错 | OpenBookQA ECE 0.024（= 噪声底）；LangChain 500 次重复判定 100% 一致、方差最低 |
| 不可知任务上过度自信 | 自造合成工单 ECE 0.107（噪声底的 4.4×）；`score` 子任务需重拟温度 3.40 |
| 返回的 `confidence` 不如 `max(probabilities)` | 独立测试 ECE 0.18 |
| 方向会随原语翻转 | choice/score 过度自信（T≈3.3），boolean 反而欠自信（T≈0.66） |
| 逻辑不一致 | 问题与其否定概率之和可 ≠ 1（官方示例 1.19） |
| 硬失败存在 | DAIR Emotion 上 **16% 样本把零概率给了真实标签**（Laya 项目方报告） |

### 6.5 "弃权率"是最容易被忽略的成本项

- 实测 **30% 弃权** → 成本优势从 76× 掉到 **3.2×**。
- 上限公式：`有效成本倍数 ≤ 1 / 弃权率`，与单价无关。

### 6.6 开源侧的许可证与命名风险

- **无许可证（license = null，采用有法律风险）**：`yibie/awesome-jev`、`featherless-ai/simple-jev`、`ekzhang/openjev-sglang`、`bespokelabsai/nimble`、`SAGAR-TAMANG/sarvam-jev`、`SiliconLabAI/OpenJev` 等。
- **NOASSERTION**（仓库有 LICENSE 文件但 GitHub 无法识别）：`Heman10x-NGU/openJev-verdict-2.0`、`rorshopping/jev-on-a-laptop` 等。
- **重新分发底座模型权重的合规性**：Qwen3.5-4B 本身是 Apache-2.0，因此主流复现项目的再分发**通常没有冲突**；真正明显的缺口是 **NanoJev 的 HuggingFace 权重仓库完全未声明许可证**。不要照搬"复现项目必有许可证问题"的流行说法。
- **命名误导**：把复现项目直接叫 "JEV" 会让人误以为拿到官方模型。正面例子是 `TheoLeeCJ/SemIf` 主动改名并在 README 声明"复现的是接口模式，不是 JEV 未公开的模型与训练，与 TypeSafe 无关"。

### 6.7 生态存在明显注水

- 9 月以后新建的 JEV 相关仓库约 **4,126** 个，真正解释机制的约 **20–25** 个。
- `awesome-jev` 类目录至少 18 个，多数建于 5 天内；目录站的 star 快照**系统性偏低 18–39%**。
- 有仓库 README **内部自相矛盾**（如 `wfzyx/von` 的 T 值与训练集规模各写两版），引用其数字前请交叉核对。
- 引用任何复现项目的 benchmark 前请记住：**本报告没有对任何仓库做实际跑测**，这些数字全部是项目方自报。

### 6.8 路线级质疑

- 有独立分析（Archer，1,029 次黑盒探针）给出**证伪"独立 logits + softmax"**的实验：加入无关选项后 log-odds 从 +0.38 降到 +0.11（10/10 分组一致）——即它可能不是简单的"分类器包装"。
- 但反向证据也存在：对严格 JSON schema 的强模型（Terra）同样能做到"零幻觉"；因此**"不生成文本"本身不构成护城河**，关键是延迟、成本与概率质量这三项的组合。

---

## 7. 附录：核实方法、未核实清单与参考链接 / Appendix

> **EN** — Repo metadata was pulled live with `gh api` on 2026-09-21; official documentation pages, the official eval site, and launch post were fetched and parsed directly (raw captures live in `research/`). Numbers that only exist in secondary reporting are flagged as unverified below. Everything here is reproducible with the commands in 7.4.

### 7.1 本仓库内容

```
README.md                        # 本报告正文
research/jev-official.md         # 官方事实与 API 契约的原始核实记录（含逐条来源）
research/os-reproductions.md     # 开源复现项目逐个核实记录（含 gh api 原始输出）
research/ecosystem-benchmarks.md # 第三方评测、生态目录、风险分析的原始记录
research/laya-github-readme.md   # Laya 官方 README 快照（其 benchmark 与局限）
data/open-source-projects.csv    # 项目元数据表（star/许可证/底座模型等）
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
| 生态规模（7,330 / 4,126 / 503 / 386 / 195 …） | 三种口径互不一致，引用需注明来源 |
| 所有复现项目的加速倍数 | **本报告未对任何仓库做实际跑测** |
| 官方是否有零数据保留、是否默认用于训练 | 未找到信息 |

### 7.4 如何复现本报告的数据

```bash
# 1) 拉取任意仓库的当日元数据
gh api repos/TheoLeeCJ/SemIf \
  --jq '{full_name,stargazers_count,forks_count,open_issues_count,
         license:.license.spdx_id,created_at,pushed_at,description}'

# 2) 按 star 检索 JEV 生态
gh api "search/repositories?q=jev&sort=stars&per_page=50" \
  --jq '.items[]|{full_name,stargazers_count,license:.license.spdx_id,html_url}'

# 3) 读仓库 README
gh api repos/TheoLeeCJ/SemIf/contents/README.md --jq .content | base64 -d

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
- SemIf（原 OpenJev）<https://github.com/TheoLeeCJ/SemIf> · mini-jev <https://github.com/r-ms/mini-jev> · jevlike <https://github.com/vinnylarouge/jevlike> · jevmlx <https://github.com/bnsd55/jevmlx> · NanoJev <https://github.com/TianyuCodings/NanoJev> · kev <https://github.com/jaredpalmer/kev> · nimble <https://github.com/bespokelabsai/nimble> · von <https://github.com/wfzyx/von> · openjev-sglang <https://github.com/ekzhang/openjev-sglang> · simple-jev <https://github.com/featherless-ai/simple-jev> · jev-ultrafast <https://github.com/browser-use/jev-ultrafast> · fast-browser-use <https://github.com/APUS-AI-Lab/fast-browser-use>
- 生态目录：<https://jevbest.com/zh/> · <https://madewithjev.com/github-repos> · <https://github.com/logicrw/awesome-jev-projects> · <https://github.com/yibie/awesome-jev>

**对比图说明**：本报告不提供"谁最快"的单一结论表，因为官方口径互相矛盾、第三方测试任务各不相同、且所有开源项目的数字均未经独立复跑。做选型时请以**你自己数据上的实测**为准。

---

*本报告由 AI 调研代理搜集整理，所有数字均标注了来源类型与核实状态；发现错误请提交 issue 或 PR 修正。*
