# JEV 官方事实与架构 — 原始资料汇编

> 调研日期：2026-09-21（北京时间）
> 负责范围：任务 1「JEV 官方事实与架构」
> 规则：**严格区分「官方/项目方宣称」与「第三方独立验证」**；查不到的写「未核实」，不编造。

---

## 0. 快速结论表（每条附来源）

| 项目 | 结论 | 来源类型 | 来源 |
|---|---|---|---|
| 公司 | TypeSafe AI，旧金山，2024 年成立（一说"两年隐蔽期/2024 创立"） | 官方+媒体 | https://typesafe.ai/team ; https://techstartups.com/2026/09/15/venture-capital-startup-funding-roundup-september-15-2026-alumni-ventures-lightscape-partners-kleiner-perkins-khosla-ventures-sequoia-capital-more/ |
| 创始人 | Diogo Almeida（CEO）；联合创始人 Erik Gafni（CTO，前 Ravel/Invitae/Freenome）、Sasha Sheng（COO，前 Meta/FAIR） | 媒体+官方 | https://www.tao.media/typesafe-ai-launches-jev-a-system-one-model-built-for-software-decisions/ ; https://www.startuphub.ai/ai-news/artificial-intelligence/2026/typesafe-jev-model-kills-chat |
| 融资 | **4000 万美元种子轮，DCVC 领投**（Business Wire 公告） | 官方新闻稿 | https://www.businesswire.com/news/home/20260915525333/en/ ；Yahoo Finance 转载 https://finance.yahoo.com/technology/ai/articles/typesafe-ai-emerges-stealth-40m-190000776.html |
| 估值 | 报道称约 **2 亿美元**（Forbes 口径） | 第三方媒体（单一来源，未核实） | https://hellomarvisaitoday.com/articles/78198eff-1eea-419e-93d9-7ef42bd050a6 ; https://www.aimiracle.ai/ai-news/jev-ai-model/ |
| 发布时间 | **官方博文标注 2026-09-15**（美东时间下午 3:00 发布融资公告）；部分媒体记 9/14 或 9/16 | 官方博文时间戳 | https://typesafe.ai/blog/introducing-system-one-models-and-jev |
| 模型版本 | `jev-1.13.0`，别名 `jev-latest` 与 `jev-preview` 当前均指向它 | 官方文档 | https://docs.typesafe.ai/models |
| API 端点 | `POST https://api.typesafe.ai/v1/systemone` | 官方文档 | https://docs.typesafe.ai/api |
| 三种原语 | Choice / Score / Noul（无 ranking、无 span、无 boolean 类型） | 官方文档 | https://docs.typesafe.ai/primitives |
| 定价 | $0.042 / 百万 input token（=$42/十亿），**output token 免费** | 官方文档 | https://docs.typesafe.ai/models |
| 速率限制 | 250,000 tokens/秒 与 1,200 请求/分钟（**官方称动态调整，不另行通知**） | 官方文档 | https://docs.typesafe.ai/models |
| 上下文 | 单请求 64k token；其中 `state` + 最长单条问题 ≤ 32k | 官方文档 | https://docs.typesafe.ai/models |
| 输入模态 | **仅文本**（string / JSON object / array of text）。不支持图像、音频、视频 | 官方文档 | https://docs.typesafe.ai/concepts/system-one |
| 权重 | **未开源**。仅托管 API。官方明确「所有账号同一套权重，不做 per-account 微调/LoRA」 | 官方文档 | https://docs.typesafe.ai/models |
| 流式 | **不支持流式**（非自回归，无 token 流） | 官方（隐含）+ 第三方集成文档 | https://pydantic.dev/docs/ai/models/typesafe/ |
| 中国大陆 | **未对中国大陆开放**（第三方报道；官方条款/文档未见明文地区清单） | 第三方（央广网） | https://www.cnr.cn/tech/techph/20260920/t20260920_527819594.shtml |
| Doom demo | 有。结构化文本游戏状态输入，~10 queries/秒，约 $7/小时 | 官方博文 | https://typesafe.ai/blog/introducing-system-one-models-and-jev |
| 官方基准 | Jev 67.8% / $0.0004 / 0.4s（四工作流均值），对比 GPT-5.6 Sol 74.1% | 官方（自测） | https://evals.typesafe.ai/ |
| 首页宣称 | 193.6x faster / 444.6x cheaper；另说 238x lower input price than Claude Fable 5.1 | 官方（自测） | https://typesafe.ai/ |

---

## 1. 公司与创始人

### 1.1 官方 team 页原文
> "We're a close-knit, flat team from OpenAI, Google Brain, Meta/FAIR, Stripe, Airbnb, Plaid, Docker, and more. We're backed by top-tier investors who share our vision for building the foundation of truly transformative AI.
> Our team works in-person five days a week in our San Francisco office near the Embarcadero station."

来源：https://typesafe.ai/team

### 1.2 创始人
- **Diogo Almeida**（CEO）：前 OpenAI 研究员、前 Google Brain。InstructGPT（2022）论文共同作者，参与 RLHF 与早期 ChatGPT 相关研究；亦被列为 GPT-4 / ChatGPT 论文共同作者（此点见四weekmba 与多家转述，属"媒体口径"）。
  - 官方博文自述：「At OpenAI, I helped build the methods that made language models useful at following instructions and talking with people. That work ended up as the research behind ChatGPT.」
    来源：https://typesafe.ai/blog/introducing-system-one-models-and-jev
  - 另有 2026-07-31 上传的 AI Engineer 演讲，称其团队「basically invented post-training」。来源：https://fourweekmba.com/ai-typesafe-ai-almeida-chatgpt-era-structural-read/
- **Erik Gafni**（CTO）：前 Ravel / Invitae / Freenome（基因组学）。来源：https://www.startuphub.ai/ai-news/artificial-intelligence/2026/typesafe-jev-model-kills-chat
- **Sasha Sheng**（COO）：前 Meta / FAIR 研究工程师。同上。
- 公司 **2024 年创立**，至发布时约两年隐蔽期。来源：https://techstartups.com/2026/09/16/startup-funding-news-today-september-16-2026-anew-labs-caddi-space-epoch-typesafe-ai-more/

### 1.3 融资
- **官方新闻稿**：*TypeSafe AI Emerges From Stealth With $40M in Funding With New Model for Composable AI*，Business Wire，URL token `20260915525333`（对应 2026-09-15）。
  - 原文链接：https://www.businesswire.com/news/home/20260915525333/en/ （直接抓取返回 **403 Forbidden**，未能读取全文）
  - 转载：https://finance.yahoo.com/technology/ai/articles/typesafe-ai-emerges-stealth-40m-190000776.html
  - 「TypeSafe has raised approximately $40 million in funding led by DCVC. Early access to its first frontier model, Jev, is waitlisted at typesafe.」
- **DCVC 领投**，金额约 4,000 万美元。多方一致（TechStartups、FinSMEs、Seedtable、tao.media、Finsmes）。Seedtable 记录：https://seedtable.com/companies/typesafe-ai/funding-rounds/seed-2026-09
- **估值**：报道称约 **2 亿美元**（AIToday 明确写 "valuing it at a reported $200 million"；ai miracle 称 Forbes 报道约 $200M）。
  - https://hellomarvisaitoday.com/articles/78198eff-1eea-419e-93d9-7ef42bd050a6
  - **注意**：该估值未在官方新闻稿（我未能读到原文）中确认，属**第三方报道，未核实**。
- 融资公告时间：TechStartups 记录为美东时间 **9 月 15 日 15:00 ET**。
  https://techstartups.com/2026/09/16/startup-funding-news-today-september-16-2026-anew-labs-caddi-space-epoch-typesafe-ai-more/

---

## 2. 发布时间：口径差异梳理

| 日期 | 出处 | 说明 |
|---|---|---|
| **2026-09-15** | 官方博文页头 `Sep 15, 2026`；Business Wire token `20260915525333`；TechStartups 记 15:00 ET | **最可信，官方时间戳** |
| 2026-09-14 | remio.ai、jdon.com、Threads 帖 | 少数二手来源，疑为时区/笔误 |
| 2026-09-16 | IT之家「昨日（9月16日）发布」；Techmeme 条目 `260916/p1`；The Register 文章 URL 含 `/2026/09/16/` | 媒体报道日/新闻聚合日，非发布日 |

- 官方博文：https://typesafe.ai/blog/introducing-system-one-models-and-jev （页头日期 Sep 15, 2026，作者 Diogo Almeida, founder, TypeSafe）
- Techmeme：https://www.techmeme.com/260916/p1
- The Register URL（未能抓取正文）：https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711
  - 抓取失败（JS 渲染 + 网络错误）。**正文原文未核实，仅通过多方转述引用。**

**结论**：发布日 = **2026-09-15**（官方博文 + Business Wire）。9/14 与 9/16 的说法是二手来源差异。

---

## 3. 名称由来（官方博文 FAQ + 正文）

- **System One Models**：借 Daniel Kahneman《思考，快与慢》中 System 1（快、直觉）vs System 2（慢、审慎）的区分。官方同时承认：「"System 1 thinking" has also implied error-prone. For reasons we will get into in the future, we believe System One Models can be made more reliable than its alternatives.」
- **Jev**：取名自经济学家 **William Stanley Jevons**（杰文斯悖论）。官方原文：「We expect machine intelligence to follow a similar path to coal, after steam-engine efficiency led to an increase in demand. Every order of magnitude drop in the cost of intelligence unlocks orders of magnitude more use cases.」
- 官方标语：「We're building prod, not God.」（引自 Every 报道转述）
- 来源：https://typesafe.ai/blog/introducing-system-one-models-and-jev

---

## 4. 官方 API 形态（原文级）

### 4.1 端点
```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```
来源：https://docs.typesafe.ai/api

> **注意**：**不是** chat completions 形态。官方无 `/v1/chat/completions`。

### 4.2 请求体（官方字段级文档，原文）

| 字段 | 类型 | 必填 | 官方说明 |
|---|---|---|---|
| `state` | string \| object \| array | 是 | 被评估的内容。纯文本用 string；结构化数据（chat logs、records、应用当前状态）用 object/array |
| `model` | string | 是 | 处理请求的模型。用 `"jev-latest"` |
| `questions` | map<string, Question> | 是 | 类型化问题的映射。**key 由你自己取，答案以同样的 key 返回。key 不会发送给底层模型，不参与推理** |

示例请求：
```json
{
  "state": "Help! My payouts have been failing for 3 days.",
  "model": "jev-latest",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "Does this convey urgency?"
    }
  }
}
```

### 4.3 三种问题类型（官方 = 全部类型，无第四种）

#### (a) Noul — 是/否
```json
{
  "type": "noul",
  "instructions": "Does this convey urgency?",
  "criteria": {
    "true": "Explicitly time-sensitive",
    "false": "No urgency expressed"
  }
}
```
- `type`: `"noul"`（必填）
- `instructions`: string \| object \| array（必填）
- `criteria`: object，可选，含 `true` / `false` 字段描述

#### (b) Choice — 从一组选项中选一个
```json
{
  "type": "choice",
  "instructions": "Which team should handle this?",
  "criteria": {
    "billing": "Payments, invoicing, refunds",
    "technical": "Bugs, outages, integrations",
    "sales": "Pricing, upgrades, new accounts"
  }
}
```
- `criteria`: map<string, string | object | array | null>（必填），**最多 255 个选项**
- 可用 `null` 表示某选项无需额外说明

#### (c) Score — 在你的评分表上打分
```json
{
  "type": "score",
  "instructions": "How frustrated is the customer?",
  "criteria": ["Calm", "Frustrated", "Very angry"]
}
```
- `criteria`: array<string | object | array>（必填），有序数组，**至少 2 级，API 最多接受 10 级**

#### `instructions` 支持结构化对象
```json
"instructions": {
  "potential_duplicate": {
    "name": "John Smith",
    "location": "Oakland, California",
    "last_employer": "Google"
  },
  "question": "Is the resume for the same person as `potential_duplicate`?"
}
```
（用反引号引用数据字段名，与 state 嵌套值引用方式一致）

来源：https://docs.typesafe.ai/api ; https://docs.typesafe.ai/primitives

### 4.4 响应体（官方字段级文档，原文）

| 字段 | 类型 | 说明 |
|---|---|---|
| `model` | string | 实际执行评估的模型（版本化 ID，如 `jev-1.13.0`） |
| `answers` | map<string, Answer> | 每个问题一个答案，key 与请求一致 |
| `usage` | object | `input_tokens` (int)、`output_tokens` (int) |

#### Noul 答案
```json
{
  "model": "jev-1.13.0",
  "answers": {
    "is_urgent": { "type": "noul", "noul": 0.95 }
  },
  "usage": { "input_tokens": 307, "output_tokens": 20 }
}
```
- `noul`: number，0（否）到 1（是）
- **Noul 答案没有 `confidence` 字段**（官方 Confidence 页明确："Noul answers don't carry one."）

#### Choice 答案
```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "billing",
      "probabilities": { "billing": 0.88, "technical": 0.12, "sales": 0.0 },
      "confidence": 0.81
    }
  },
  "usage": { "input_tokens": 318, "output_tokens": 34 }
}
```
- `choice`: string，最高概率选项
- `probabilities`: map<string, number>，浮点和为 1
- `confidence`: number，由概率分布导出

#### Score 答案
```json
{
  "model": "jev-1.13.0",
  "answers": {
    "frustration": {
      "type": "score",
      "score": 1.05,
      "legend": { "0": "Calm", "1": "Frustrated", "2": "Very angry" },
      "probabilities": { "0": 0.0, "1": 0.95, "2": 0.05 },
      "confidence": 0.92
    }
  },
  "usage": { "input_tokens": 304, "output_tokens": 18 }
}
```
- `score`: number，概率加权值，可落在级别之间（如 1.05）
- `legend`: map<string, string>，级别编号 → 描述
- `probabilities`: 每个级别（字符串 key）→ 概率

### 4.5 完整可运行 cURL（官方 Quick start 原文）
```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
  {
    "state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
    "model": "jev-latest",
    "questions": {
      "urgency": {
        "type": "noul",
        "instructions": "Does this message express urgency?"
      }
    }
  }
EOF
```

三原语混合的官方示例请求/响应（`urgency` / `department` / `frustration` 一次调用）见 https://docs.typesafe.ai/introduction/quickstart

### 4.6 Python SDK（官方原文）
```bash
pip install typesafe-sdk     # 需要 Python >= 3.10
# 或
uv add typesafe-sdk
```
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()   # 从环境变量读 TYPESAFE_API_KEY，默认调用 jev-latest

ticket = "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."

response = client.system_one(
    state=ticket,
    questions={
        "department": Choice(
            instructions="Which team should handle this",
            criteria={
                "billing": "Payment or subscription issues",
                "technical": "Bugs or integration problems",
                "sales": "Pricing or account questions",
            },
        ),
        "frustration": Score(
            instructions="How frustrated the customer appears",
            criteria=[
                "Calm, just stating facts",
                "Frustrated but civil",
                "Very angry, strong language",
            ],
        ),
        "is_urgent": Noul(
            instructions="The message conveys urgency or time-sensitivity",
        ),
    },
)

print(response.answers["department"].choice)
print(response.answers["frustration"].score)
print(response.answers["is_urgent"].noul)
```
- TypeScript SDK：`@typesafe-ai/sdk`
- 另有 Agent Skill：`claude plugin marketplace add typesafe-ai/skills` + `claude plugin install typesafe@typesafe-ai`，或 `npx skills add typesafe-ai/skills --skill typesafe-ai`
- SDK 仓库：https://github.com/typesafe-ai/skills （MIT，1,259 stars，创建 2026-08-24，最后推送 2026-09-12，59 forks，4 open issues — 数据来自 `gh api`，查询时间 2026-09-21）

### 4.7 模型列表接口
```bash
curl https://api.typesafe.ai/v1/models \
  -H "Authorization: Bearer $TYPESAFE_API_KEY"
```
返回数组，每项含 `model`（ID/别名）、描述、`release date`。**目前只列出别名**；版本化 ID（如 `jev-1.13.0`）即使不在列表里也被 `model` 字段接受。

---

## 5. 机制：并行、批量、KV-cache

### 5.1 官方明确支持的
- **请求内并行**：「All three question types can be mixed in a single API call. Every question is evaluated in parallel and in isolation against the same `state` in one go. **Adding questions barely changes the response time.** Each question is evaluated independently, so adding more questions does not create context-rot.」
  来源：https://docs.typesafe.ai/introduction
- **一次 ingest，多次评估**：「Jev ingests the `state` once and evaluates every question against it in parallel.」
  来源：https://docs.typesafe.ai/models
- **推测式扇出（Speculative fan-out）**：官方模式页，建议一次发送大量（含"投机性"）问题，由代码决定哪些结果重要。
  来源：https://docs.typesafe.ai/patterns/fan-out
- **并行采样器（parallel sampler）**：官方博文称「新模型架构 + parallel sampler for maximum efficiency」；「Parallel. Generates all outputs in a single query. Incredibly efficient and hardware-aware.」

### 5.2 未在官方文档中明确的
- **KV-cache 复用**：我在官方文档全文（llms.txt 所有 `.md` 页面）grep `kv.cache|kv cache|prompt cach|stream|concurren|batch size` — **零命中**。官方文档**没有** KV-cache 复用、跨请求缓存、显式批处理（batch endpoint）的说明。
  - **对 KV-cache 的描述来自中国厂商 APUS 的复现说明**（第三方）：「APUS 复现了单 Token Logits 快速决策，跳过自回归解码的过程，实现了 Jev **KV-Cache 广播与并发批量评估**的工作机制」。来源：https://www.cnr.cn/tech/techph/20260920/t20260920_527819594.shtml
  - → **KV-cache 广播 / 并发批量评估为第三方推断，非官方文档确认。**
- **流式**：官方文档无 streaming 说明。Pydantic AI 的 TypeSafe 集成文档解释：「Jev answers in one piece, so there is nothing to stream, and nothing that stops working: `run_stream`, an `event_stream_handler`, and the AG-UI and Vercel AI adapters get the whole answer as a single event. There are no partial results and no earlier first token — it is compatibility, not streaming.」
  来源：https://pydantic.dev/docs/ai/models/typesafe/
- **客户端并发**：`jevaiguide.com` 独立测试记录「The whole run of 483 decisions finished in 20.2 seconds at a concurrency of 8」（第三方自建并发）。来源：https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/

### 5.3 官方「原子问题」设计原则（影响架构）
> "Think of each question as a gut-check determination: the kind of judgment a highly knowledgeable person could make in a few seconds given the right context."
> "If the question you want to ask would require extended reasoning or weighs multiple independent factors, decompose it. Ask each factor as a separate question, then combine the results with logic in your code."
> 示例：不要问"给这份创业 pitch 打分"，而要分别问市场规模、技术可行性、差异化，再用你自己的公式组合。

来源：https://docs.typesafe.ai/introduction ; https://docs.typesafe.ai/primitives

---

## 6. 定价、速率限制、上下文

### 6.1 官方 Models 页原文表格（`jev-1.13`）

| 项目 | 值 |
|---|---|
| Model ID | `jev-1.13.0` |
| 定价 | **$42 / Btok**（十亿 token）；**$0.042 / Mtok**（百万 token） |
| 速率限制 | **250,000 tokens 每秒 / 1,200 请求每分钟** |
| 上下文长度 | **64k tokens / 请求**；其中 `state` + 最长单条问题 **32k** |
| 输入 | **仅文本**。String、JSON object，或文本数组。**无图像/音频/视频输入** |

- 计费方式：**按 input token 计费，output token 免费**
- 速率限制官方原文：「**Rate limits are adjusting dynamically.** We are serving a very large volume of demand, and the limits above can change without notice while we do, as upcoming large GPU deals land and we let in more users. Once things settle down more, we'll be able to offer more stable limits. Higher limits are available on custom and enterprise plans. Contact sales@typesafe.ai.」
- 超限返回 `429 Too Many Requests`；SDK 默认带 backoff 重试并遵守 `retry-after` 头。
- 别名：`jev-latest` → `jev-1.13.0`（"most recent stable, official release"）；`jev-preview` → `jev-1.13.0`（当前与 latest 相同，无 preview 构建）。
- 官方建议：**调好阈值后应 pin 版本化 ID，而不是用别名**（别名会随版本移动）。响应里的 `model` 字段会报告实际回答的版本化 ID。

来源：https://docs.typesafe.ai/models

### 6.2 官方定价对比口径
- 首页：「**$42 Per Billion input tokens. 238x Lower input price than Claude Fable 5.1**」
- 博文表格：「Input tokens: from $0.20 to $10 / MTok」对比 LLM；「Output tokens: ~5x more expensive than input tokens」（针对 LLM）
- 博文：「Input tokens: $0.042 / MTok ($42 per billion tokens). Output tokens: FREE (too cheap to meter).」

### 6.3 关于价格可持续性（官方自认无法证明）
> "**Cost per call:** We make our pricing transparent. **We can't prove it isn't subsidized**; we'll need the long-term to prove the sustainability of our pricing (which we expect to go down, not up)."
来源：https://typesafe.ai/blog/introducing-system-one-models-and-jev

---

## 7. 官方基准 / 性能数据：口径与细节

### 7.1 首页数字（官方）
- 展示框：「**193.6x Faster, 444.6x Cheaper.*** / *based on workflows for System One tasks (proof)」
- 具体一例：TypeSafe AI **Cost $0.000081, Completed in 0.114s**；LLMs **Cost $0.013880, Completed in 8.566s**
- 官网另有 `[b.64]` base64 段（疑似彩蛋/混淆内容），未解读。
来源：https://typesafe.ai/

### 7.2 博文口径（官方）
| 维度 | Existing LLMs | System One + Jev |
|---|---|---|
| 训练/优化 | RLHF / RLVR | **RLCD**（Reinforcement Learning for Calibrated Decisions） |
| 输入 | 非结构化数据（文本），强调**顺序消息** | 非结构化数据，强调**结构化程序状态** |
| 输出 | **字符串/生成文本**，需 parse + validate | **类型安全结构化值**，永不产生类型错误 |
| 采样 | **顺序**，一次一个 token | **并行**，单次查询生成全部输出 |
| 成本 | 输入 $0.20–$10 / MTok；输出约为输入 5 倍 | 输入 $0.042 / MTok；输出 **FREE** |
| 速度 | 端到端 **3–329 秒** | 端到端 **70ms–500ms**；**对同等智能水平的 System One 型查询快 40x–200x** |
| 置信度 | 过度自信、不一致 | 每个输出都带 confidence；校准：更高置信度 = 更高准确率 |

### 7.3 官方对自身声明的 "Nuance"（**极其重要，官方主动披露的局限**）

**关于速度/成本：**
> "**Speed per call:** We truly are that fast, though **our published evals are generally run from our laptops on the West Coast** (this is where our service is currently based)."

**关于工作流评测（193.6x / 444.6x 的来源）：**
> "This is where the claims of 193.6x faster, 444.6x cheaper on our home page comes from, and **we expect that these are on the higher end of real world gains.**"
> "These content of these workflows were **not deliberately chosen nor constructed to make our model look good**, and are not in our training distribution. However, **they were made by individuals on our model capabilities team, so some bias could exist.**"
> "We use the **average of GPT-6 Astra and Fable 5.1 as the reference answer, which biases answers towards OpenAI and Anthropic's models.** We likely underestimate the relative performance of our model and DeepSeek's models."
> "The LLMs use our **System One LLM wrapper**, which constrains LLMs to output structured decisions compatible with our API. We have found this to be the most accurate way to get decisions from LLMs, but **this tends to be slower and more expensive than giving decisions without probabilities.**"

**关于 "0% 幻觉 / 0% 类型错误"：**
> "**Our number is not empirical.** Schema matching is guaranteed, thus we can confidently add 0% into the plots."
> "The numbers for LLMs are from **OpenRouter** i.e., there almost certainly is bias here: more complex queries might be routed to better models."

**关于 side-by-side demo：**
> "The `state` is also a short, dense, and detailed paragraph, to emphasize the difference in sampling methodology. **The relatively shorter input paints our model in an advantageous light.**"
> "for the recorded run, the only disagreement with **GPT-5.6 Terra** is on 'Churn likelihood level'. The actual answer seems genuinely ambiguous to us."
> "We used **GPT-5.6 Terra** with default reasoning for this example, because we've found it to be the most comparable at intelligence to Jev on average."

来源：https://typesafe.ai/blog/introducing-system-one-models-and-jev

### 7.4 官方评测方法论（工作流评测）
> "We made a new type of evaluation to measure how well AI works within code. We don't optimize for a ground truth classification or allow the harness and model to change (potentially allowing for overfitting via harness engineering). Instead, **we assume there is a correct compute graph (a "workflow" represented in code) and use the predictions of the largest, smartest, and most expensive external models as reference probabilities.**
> Rephrased: every model gets the same workflow. We test how they compare to **the average of the smartest models (in this case, Astra and Fable).**"

### 7.5 官方 evals 站点实测数据（`evals.typesafe.ai`，2026-09-21 抓取）

四个工作流：Security Incidents（安全事件处置）、Agent Trace Observability（Agent 轨迹审查）、Invoice Processing（发票处理）、Customer Service（客服路由）。
参考标签：**GPT-6 Astra 与 Claude Fable 5.1 在 high thinking 下的答案的平均**。所有模型使用 provider 默认 reasoning 设置。

**总览（四工作流等权平均，`index.html`）：**

| 模型 | 配置 | 准确率 | 每例成本 | 每例耗时 |
|---|---|---|---|---|
| GPT-5.6 Sol | workflow | **74.1%** | $0.0836 | 23.3 s |
| Claude Opus 5 | workflow | 73.1% | $0.1761 | 37.8 s |
| **Jev** | **workflow** | **67.8%** | **$0.0004** | **0.4 s** |
| GPT-5.6 Terra | workflow | 67.9% | $0.0304 | 10.1 s |
| Sonnet 5 | workflow | 67.8% | $0.1174 | 78.1 s |
| GPT-5.6 Luna | workflow | 66.8% | $0.0033 | 12.9 s |
| DS v4 pro | workflow | 65.5% | $0.0413 | 86.5 s |
| DS v4 flash | workflow | 64.4% | $0.0059 | 51.9 s |
| Haiku 4.5 | workflow | 53.6% | $0.0195 | 12.5 s |

prompt 模式（同一策略写成一段 prompt）全部显著更差，如 Haiku 4.5 prompt 仅 18.1%、Opus 5 prompt 64.8%、Sonnet 5 prompt 60.4%。

**单工作流 Jev 表现（逐页抓取）：**

| 工作流 | Jev 准确率 | Jev 成本 | Jev 耗时 | 该工作流最强 workflow LLM |
|---|---|---|---|---|
| Security Incidents | 61.7% | $0.0001 | 0.3 s | Opus 5 66.2% / Sol 62.5% |
| Agent Trace Observability | 71.6% | $0.0003 | 0.5 s | Sol 76.6% / Luna 76.1% / Opus 75.2% |
| Invoice Processing | 61.8% | $0.0011 | 0.5 s | Sol 79.1% / Opus 78.4% / Terra 74.7% |
| Customer Service | 76.0% | $0.0001 | 0.4 s | Sol 78.3% / DS v4 flash 76.8% / Opus 72.4% |

→ **Jev 在 4 个工作流里有 2 个（Invoice、Agent Trace）明显落后最强 LLM（差 7–17 个百分点）**，且官方自己的图注写着 "frontier: nothing is both cheaper and more accurate"。

**评测页的"工作流"设计说明（官方原文要点）：**
> "To automate a task, we decompose the decisions into programmatic rules and intelligent judgments. Rather than ask a model to solve the entire problem in one shot (like the prompt examples in the plot), we ask independent narrow questions and defer to code where possible. We use three types: Noul, yes or no; Choice, one option among several; Score, a level on a scale. The results are then used programmatically to produce the output actions. **Averaged across the four example tasks, every model is more accurate, cheaper and faster in the workflow than it is with the same policy as a prompt.**"

来源：https://evals.typesafe.ai/ ; https://evals.typesafe.ai/security_incidents.html ; https://evals.typesafe.ai/agent_trace_observability.html ; https://evals.typesafe.ai/invoice_processing.html ; https://evals.typesafe.ai/customer_service.html

### 7.6 第三方对官方数字的质疑

**(a) 数字口径互相矛盾（Capital & Compute 汇总）**

| 出现位置 | 快多少 | 便宜多少 |
|---|---|---|
| typesafe.ai 首页 | 193.6x | 444.6x |
| 博文 Evidence 节 | 40x–200x | 未公布范围 |
| 早期访问 onboarding 页（不公开） | 20x–200x | 40x–1,000x |
| Capital & Compute 按官方 eval 表反算 | 约 25x–95x | 76x–440x |

来源：https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/

**(b) 444.6x 的算术来源**：按官方 eval 表，Jev $0.0004 vs Opus 5 $0.1761 → 约 440x；vs Terra $0.0304 → 约 76x。**"444.6x 是最贵那一档模型的行，不是全场平均"。** 同上来源。

**(c) 五家第三方实测成本倍数（互相不一致，且都不等于 444.6x）**

| 谁跑的 | 任务/规模 | 对比对象 | 实测 |
|---|---|---|---|
| Mike Taylor, Every | 37 篇文档 777 个判断（累计 1,709） | Claude Fable 5.1 | 约 25x 快、约 580x 便宜；植入缺陷 7 个中抓到 6 个（Fable 7/7） |
| Near Here | 活动列表审核，50 例 | Mistral Small 4 / Gemini 3.5 Flash-Lite | 便宜 8.6x / 58x；Jev 48/50 正确 vs 42 / 43 |
| gemanor benchmark | Python 代码审查，1,080 次调用 | Gemini 3.8-Flash / Claude Fable 5.1 | 便宜 45x / 274x；正确率 98.0% vs 两者 100% |
| Paddy Alton, paddo.dev | 9,081 真实产品匹配裁决 | 无 | 全队列 $0.32；**30% 弃权（abstain）** |
| Laurie Voss, Arize AI | 垃圾邮件分类，18,514 封 | 训练好的 TF-IDF 分类器 | **98.3% vs 98.4%（真实标签，统计上无显著差异）** |

来源：https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/ ；原始：
- Every: https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds
- Near Here: https://nearhere.events/blog/typesafe-jev-mistral-gemini-event-validation
- gemanor: https://github.com/gemanor/jev-code-review-benchmark
- paddo.dev: https://paddo.dev/blog/thirty-cent-judge
- Arize: https://arize.com/blog/typesafe-jev-llm-judge/

**(d) 关键结构性问题：参考标签是 LLM 生成的，没有人类 ground truth**
> "The reference labels are LLM-generated. TypeSafe's evals page states the labels come from 'an average of the responses of GPT-6 Astra and Claude Fable 5.1, both at high thinking.' **There is no human ground truth anywhere.** So '67.8% accuracy' means *67.8% agreement with a two-frontier-model consensus.*"
来源：https://bigbangindex.com/blog/typesafe-jev-cost-latency-analysis

**(e) "弃权率"（abstain rate）对成本优势的侵蚀（第三方算术）**
- 公式：`Blended multiple = M / (1 + a × M)`，a = 弃权率；当 M 很大时收敛到 `1/a`。
- 30% 弃权率 → 天花板 3.33x，无论 Jev 单例便宜 76x 还是 580x。
- Capital & Compute 自测（483 条真实 Search Console 查询）：p50 = 314ms，p95 = 399ms（**落在官方 70–500ms 区间**）；$0.0115 / 483 例 = **$0.0238/1,000**；但**二元决策上 57.8% 的答案 confidence < 0.5**，据公式 blended multiple 仅 **1.3x**。
- 后续实验：把 state 从"仅查询词"换成"查询词 + 排名页面 + 位置 + 曝光量"，mean confidence 从 0.412 → 0.505，0.5 门槛下弃权率从 65.0% → 40.0%，0.8 门槛下不变（95.8%）。→ **Jev 的 confidence 是 state 信息量的函数。**
来源：https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/

**(f) Arize AI（第三方）对 "can't hallucinate" 的直接质疑**
> "TypeSafe also claims Jev 'can't hallucinate', but **that really feels like an over-reach.** Jev can't return an answer outside the schema you gave it. **Within that schema, it could still be giving the wrong answer**, although its probability score should give you a clue if it's not confident."
> "Of course, we know better than to take a vendor's word for these things, **so Arize will be running our own benchmarks just as soon as we can.**"
来源：https://arize.com/blog/typesafe-jev-llm-judge/

**(g) The Register 的质疑方向（未能抓取原文，通过多方转述）**
- 「structured answers can still be wrong」/「comparing hallucination rates with chat models...」
- 转述来源：https://universaldigitalassistant.com/launches/typesafe-ai-jev/ ；https://news.guthlabs.ai/story/typesafe-ai-jev-system-one-model
- **⚠️ 原文未核实**（theregister.com 抓取失败：JS 渲染 + 网络错误）。

**(h) Hacker News 社区的批评（二手转述）**
- 最高票批评不是"技术造假"，而是**「frontier model」这个标签的框架问题**：Jev 不能写代码、不能对话、不能生成句子，把它和前沿 LLM 并称"frontier model"是过度包装。
- 来源：https://explainx.ai/blog/typesafe-ai-jev-system-one-models-launch-2026 ；原 HN 条目据 zenn 转述为 item 49717558，含 CEO 本人回复，471 条评论。
- **HN 原帖未直接核实。**

**(i) 官方未公开的东西**
- **架构未公开**：博文只说"new model architecture"、"parallel sampler"、"RLCD"，**没有论文、没有参数量、没有权重**。
- **权重未开源**：官方文档明确「Jev is not fine-tuned or LoRA-adapted with customer data. It is trained with RLCD ... **the same weights serve every account**」，且无下载路径。
- 第三方总结：「Jev is a hosted, closed-weight API in early access. There is nothing to download, and TypeSafe has published no self-host or open-weight path.」
  来源：https://www.modemguides.com/blogs/ai-news/jev-typesafe-reality-check-run-locally

---

## 8. 官方限制清单

### 8.1 官方 System One 概念页原文（硬限制）
> "**System One models do not write replies, produce code, or generate explanations of their reasoning.**"
> "**Jev currently accepts text input only.** It evaluates strings, JSON objects, and arrays of text. **Images, audio, and video are not supported (yet).**"
> "Calibration is measured across groups of predictions; **it does not guarantee that an individual answer is correct.**"
来源：https://docs.typesafe.ai/concepts/system-one

### 8.2 语言支持（官方 Models 页）
> "English is the **primary training language and where accuracy is currently best.** Other languages, **including CJK scripts, are handled but not equally well**; test on your own content before relying on Jev for a non-English workload, and pay close attention to Confidence when routing."

### 8.3 数据与隐私（官方）
- 「Jev is **not trained on customer requests or responses**.」
- 企业客户可申请 **zero data retention (ZDR)**，联系 privacy@typesafe.ai。
- 法律文档：DPA https://typesafe.ai/legal/data-processing ；MCA https://typesafe.ai/legal/mca ；Privacy https://typesafe.ai/legal/privacy-policy
来源：https://docs.typesafe.ai/models ; https://docs.typesafe.ai/legal

### 8.4 官方「Jev 1.13 jaggedness」（**官方自曝的 9 大失败模式**，Last reviewed 2026-09-17）

| # | 失败模式 | 官方建议 |
|---|---|---|
| 1 | **字面理解**（Literal reading） | 在 instructions 写精确条件；边界情况放进 criteria |
| 2 | **数学与数字** | 算术留在代码里 |
| 3 | **日期时间比较** | 抽取组件；在代码里比较 |
| 4 | **间接推理**（Indirection） | 减少跳数；直接指向 state 中相关部分 |
| 5 | **超大 state 含无关细节** | 先过滤；只发问题需要的内容 |
| 6 | **对抗性内容** | 写精确 prompt，上线前测边界用例 |
| 7 | **instructions 与 criteria 自相矛盾** | 对齐两者 |
| 8 | **常识/结构不变量** | 每个决策只问一次；不变量在代码里强制 |
| 9 | **生成** | 用生成模型 |

补充原文细节：
- 「`jev-1.13` **answers the question you wrote, not the one you meant.** Scoping words, negations, and implied conditions are read at face value.」
- 「`jev-1.13` **does not count reliably.** ... The model recognizes the shape of an answer rather than tallying, and the error grows with the size of the thing being counted.」
- 「questions about colors using hex values will underperform compared to those using the English names. Given RGB triples or hex values it cannot reliably judge whether two values are near each other.」
- 「`jev-1.13` reads dates as text, not as ordered quantities.」
- 「`jev-1.13`'s score levels are **weak in numerical calibration**. It will not be able to help you reconstruct the exact number by interpolating between the nearest two levels.」
- 官方还提醒：**一个问题与它的否定不必然加起来等于 1**。第三方引用的官方实例：同一张工单，「客户是否要求退款」= 0.72，「客户是否要求除退款以外的东西」= 0.47，**和为 1.19**。
  来源：https://docs.typesafe.ai/model-jaggedness/jev-1.13 ；转述：https://fdeinterviews.com/blog/what-is-jev-typesafe-ai-system-one-model

### 8.5 早期访问 onboarding 页中的额外限制（**第三方转述的未公开页面内容，非我直接核实**）
Capital & Compute 称在登录后的 onboarding 页（"Welcome inside TypeSafe: Meet Jev"，需鉴权）看到官方更直白的表述：
- **推理深度**：Jev 在涉及高推理的 System 2 任务上弱于大型推理模型，官方举例**数学推理与国际象棋**。
- **领域知识**：Jev 没有小众领域的深度知识，解决办法是把缺失上下文塞进 state，而不是指望模型知道。
- **"frontier-level intelligence for System 1 tasks" 是最难辩护的宣称**，官方称业内尚无好的证明方法，请用户自行实验判断。
- 「它可以直接为其模型盈利地提供服务」；但博文公开层面只说无法证明没有补贴。
- **⚠️ 该页需鉴权，我未能独立访问，属二手转述。**

来源：https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/

### 8.6 中国大陆可用性
- **央广网（中国官方媒体）2026-09-20 报道原文**：「据 TypeSafe 官方公布，该模型在分类决策任务上比前沿大模型最快提速近 200 倍，成本最低降至约四百分之一。**目前，该服务尚未向中国大陆地区开放。**」
  来源：https://www.cnr.cn/tech/techph/20260920/t20260920_527819594.shtml
- **我未在官方文档或服务条款中找到明文地区清单。** 我 grep 了 `typesafe.ai/legal/terms` 全文的 `region / country / export / embargo / sanction / China / geograph` 关键词——**只命中"License Restrictions"等无关条款，无地区限制条款**。
  - → **「未对中国大陆开放」为第三方（央广网）陈述，非官方文档明文。属于事实层面的观察（service 未开放），但官方未发布地区清单。**

### 8.7 可用渠道（第三方整理，官方文档只覆盖第一条）

| 渠道 | 模型名 | 前置条件 | 备注 |
|---|---|---|---|
| TypeSafe 官方 API | `jev-1.13.0`（或 `jev-latest`） | 从 waitlist 被批准 | 官方唯一文档化的渠道 |
| OpenRouter | `typesafe/jev-1.13` | 预付额度 | 2026-09-18 上线；走**独立 alpha 端点** `POST https://openrouter.ai/api/alpha/decisions`，**不是** chat completions |
| Vercel AI Gateway | `typesafe-ai/jev` | Vercel 团队绑卡 | 2026-09-16 同日上线；促销期免费至 2026-09-25 |
| Cloudflare Workers AI | `typesafe/jev` | Cloudflare 账号 | 2026-09-19 加入目录，32,000 token 上下文 |
| Netlify AI Gateway | — | Netlify 项目 | 2026-09-18 changelog；装 `@typesafe-ai/sdk` 即可，无需自建 API key |
| Requesty | `typesafe/jev-1.13.0` | — | 2026-09-19 |

- 渠道差异坑：**是/否类型在 Vercel 上叫 `boolean`，其他地方叫 `noul`**。
来源：https://jevaiguide.com/ ; https://jevaiguide.com/channels/ ; https://vercel.com/kb/guide/typesafe-jev-and-ai-sdk ; https://www.netlify.com/changelog/typesafe-jev-ai-gateway/ ; https://developers.cloudflare.com/ai/models/typesafe/jev/

### 8.8 官方 Agent Skill
- 官方发布 Claude Code 插件式 skill：`claude plugin marketplace add typesafe-ai/skills` → `claude plugin install typesafe@typesafe-ai`
- 或 `npx skills add typesafe-ai/skills --skill typesafe-ai`
- 仓库（MIT，1,259 stars，2026-09-21 `gh api` 查询）：https://github.com/typesafe-ai/skills
- 另有官方「LLM→System One」适配器：https://github.com/typesafe-ai/system-one-adapter-python （MIT，206 stars，"Drop-in TypeSafeClient replacement backed by LLM APIs"）

---

## 9. 官方 Fun Demos

### 9.1 Doom（官方博文原文）
> "We love how this doomo doomonstrates real-time intelligence and what can be doone with code + AI. The engineer behind it was worried about making **10 queries a second (which ends up costing ~$7/hour)**, but the rest of us agreed that was lower than expected! This is so fun we intend to not only release an in-depth walkthrough, but also host some events to hack on this."
> **Nuance:**
> - "The demo is on **structured state as a data structure with text, not on images (yet…)**"
> - "**A non-AI doom bot could play better**, but we wanted a bot that was reactive to different representations of game state, and most importantly… following instructions was cool as heck!"

第三方补充描述（chatmaxima，**非官方**）：「It does not look at the screen. On every tile the character reaches, the application sends Jev the nearby game state as structured text. Jev returns a direction, a strategy, a danger score, and flags such as 'trapped' or 'committed'.」
来源：https://chatmaxima.com/blog/typesafe-jev-system-one-model/

### 9.2 Wikiracing（官方博文原文）
> "The objective of the game is to start on one Wikipedia page and reach a specific other Wikipedia page using only links you come across while traversing. **Each step can mean choosing between hundreds to thousands of links!** It's a great playground for demonstrating not just intelligence-per-second, but also the compounding benefits of not hallucinating with high-cardinality choices."
> **Nuance:**
> - "Our speedups here tend to be **a lot less** than in previous demos. That's because this is **against the non-reasoning modes of the models** (except Astra which was set to the lowest reasoning setting). ... This was to make the demo more bearable to watch. **The LLMs look much worse at this task than with reasoning enabled.**"
> - "**Jev supports a cardinality up to 255.** For the higher cardinality choices, we do a **2 stage-system of scoring independently then making an explicit choice**, hence the occassional slowdown."

来源：https://typesafe.ai/blog/introducing-system-one-models-and-jev

### 9.3 其他官方 demo
- Smart home assistant demo：https://docs.typesafe.ai/demos/smart-home
- Demos 索引：https://docs.typesafe.ai/demos

---

## 10. 官方文档地图（供后续检索）

完整索引（可喂给 agent）：https://docs.typesafe.ai/llms.txt

关键页面：
| 内容 | 官方地址 |
|---|---|
| 简介/原语总览 | https://docs.typesafe.ai/introduction |
| Quick start | https://docs.typesafe.ai/introduction/quickstart |
| System One 概念 | https://docs.typesafe.ai/concepts/system-one |
| State 说明 | https://docs.typesafe.ai/concepts/state |
| 如何构建 | https://docs.typesafe.ai/concepts/how-to-build-with-system-one |
| 用例地图 | https://docs.typesafe.ai/concepts/use-case-map |
| 原语（Choice/Score/Noul） | https://docs.typesafe.ai/primitives |
| 置信度 | https://docs.typesafe.ai/confidence |
| 模式（扇出/置信路由/复合打分/意图路由） | https://docs.typesafe.ai/patterns |
| HTTP API 参考 | https://docs.typesafe.ai/api |
| 模型/定价/限速 | https://docs.typesafe.ai/models |
| Jev 1.13 缺陷清单 | https://docs.typesafe.ai/model-jaggedness/jev-1.13 |
| 法律 | https://docs.typesafe.ai/legal |
| 状态页 | https://status.typesafe.ai |
| 控制台/Playground | https://console.typesafe.ai |
| 工作流评测 | https://evals.typesafe.ai |
| 官方博文 | https://typesafe.ai/blog/introducing-system-one-models-and-jev |
| 官网其他博文 | antitbenchmaxxing / bitterest-lesson / ai-too-good-to-be-true-too-bad-to-be-useful-typesafe-ai / diogo-almeida---founders-you-should-know |

---

## 11. LangChain 博客要点（`https://www.langchain.com/blog/building-a-harness-with-jev`）

**性质：第三方集成方，但大量转述官方口径与官方数字。**

- 官方数字引用：「The company reports up to **200x faster inference and 400x lower cost** than comparable LLMs on classification tasks.」→ **这里是"200x/400x"这一广泛流传口径的直接来源。**
- 三种问题类型总结（Choice / Score / Noul）与本文档一致。
- 并行特性引用：「System One models evaluate every question in a request in parallel. **Adding questions barely changes the response time** and costs only the tokens for the extra questions, which are cheap.」
- 请求示例：
```json
{
  "model": "jev-latest",
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and it keeps failing. I'm losing sales. Please help ASAP.",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```
  响应片段：`{ "is_urgent": { "type": "noul", "noul": 0.999 } }`
- LangChain 集成类：`TypeSafeClassifier`（包 `langchain-typesafe`，环境变量 `TYPESAFE_API_KEY`）
```python
from langchain_typesafe import Noul, TypeSafeClassifier

classifier = TypeSafeClassifier()

response = classifier.invoke({
    "state": (
        "The deploy failed twice and customers are seeing 500s. "
        "Can someone look now?"
    ),
    "questions": {
        "urgent": Noul(
            instructions="Does this need attention right now?"
        ),
    },
})

urgency = response.nouls["urgent"].noul
```
  state 可以是文本、结构化数据，或 LangChain messages。
- 两个官方合作模式：`ModelRouterMiddleware`（模型路由）与 `AutoModeMiddleware`（工具调用前风险拦截，`AutoModeMiddleware(tools=["bash"])`）。
- 提到的社区项目：Browserbase 的 Kyle Jeong（浏览器 agent）、Jarrod Watts（实盘交易 agent）、Ryan Vogel（邮件分流）。
- **注意**：博客内容里出现的 GPT-5.6 Luna / Sol、`openai:gpt-5.6-luna` 等型号名，与本报告其他第三方资料一致，但我未独立核实这些型号名。作者署名（Capital & Compute 引用为 Sydney Runkle 与 Hunter Lovell，2026-09-17）**未在我抓取的页面中出现**，属未核实。

---

## 12. Eigent 中文博客要点（`https://www.eigent.ai/zh-CN/blog/typesafe-ai-jev-system-one-models`）

**性质：第三方中文解读，非官方。要点提炼：**
- 发布时间 2026-09-15。
- 融资：**DCVC 领投 4000 万美元**。
- 命名致敬 William Stanley Jevons。
- 三种原语：Choice（**最多 255 个选项**，可加显式 `other`）、Score（**2–10 级**，返回值可落在级别之间，如 `1.4`）、Noul（0–1 单一概率）。
- 对比表（第三方制作，非官方）：

| | Jev（System One） | 前沿 LLM |
|---|---|---|
| 输出 | 类型化决策 + 概率 | 生成文本（字符串） |
| 采样 | 并行，单次处理 | 顺序，逐 token |
| 延迟 | 70–500 ms（**自报**） | 秒级 |
| 结构化输出错误 | 从根本上 0% | 非零 |
| 置信度 | 每次回答均校准 | 通常过度自信 |

- 中文博客对官方口径的复述：**输入 $0.042/百万 token，输出免费**；延迟 70–500ms；首页宣称「快 193.6 倍、便宜 444.6 倍」。
- **该中文博客明确写出的警示（与官方 nuance 一致）**：
  - 「请将这些数据视为**厂商声明，而非独立验证结果**。」
  - 「评测在其团队**自己的笔记本电脑上于美国西海岸运行**；**无法证明定价未经补贴**；其工作流虽未纳入训练集，但由**其内部团队构建**。」
  - 「该基准测试**以 GPT-6 Astra 和 Fable 5.1 的平均值作为'正确'参考**，这本身就引入了对这两个模型的偏向。」
  - 「**目前，它仍处于早期访问阶段，仅支持文本，所有性能数据均为自报**——前景可期，但尚待验证。」
- 三大局限：**无世界知识**（只了解传入的 state）、**校准是群体属性**（不保证单次正确）、**无生成能力**（对话/代码/推理解释均不在范围内）。

---

## 13. 社区/开源复现（背景参考，供任务 2 交叉核对）

**用 `gh api search/repositories` 查询（2026-09-21）：**

| 仓库 | Stars | 许可证 | 说明 | 创建日 |
|---|---|---|---|---|
| browser-use/jev-ultrafast | 12,588 | MIT | "i. am. speed." | 2026-09-16 |
| NandhaKishorM/laya | 5,033 | **Apache-2.0** | ConvAI Innovations 的 421M 开源 System One | 2026-09-18 |
| TheoLeeCJ/SemIf（前 OpenJev） | 2,523 | MIT | "Semantic ifs from open models, on a 3090 at home" | 2026-09-16 |
| jaredpalmer/kev | 1,163 | Apache-2.0 | 可自行训练的 Qwen3.5 系决策模型 | 2026-09-17 |
| typesafe-ai/skills（**官方**） | 1,259 | MIT | 官方 Agent Skill | 2026-08-24 |
| Anil-matcha/awesome-jev-by-typesafe | 719 | MIT | 精选列表 | 2023-05-17（旧仓库改名） |
| yibie/awesome-jev | 673 | 无 | 精选列表 | 2026-09-17 |
| v-modal/awesome-jev-tools | 566 | 无 | 精选列表 | 2026-09-19 |
| thruwire/foreman | 441 | MIT | 软件工厂工头 | — |
| devagrawal09/jev-review | 420 | MIT | 代码审查工作流 | — |
| wfzyx/von | 241~242 | Apache-2.0 | "Sub-15ms, non-autoregressive, local drop-in alternative" | 2026-09-18 |
| razorback16/openjev | 220 | Apache-2.0 | 基于 DiffusionGemma | 2026-09-18 |
| typesafe-ai/system-one-adapter-python（**官方**） | 206 | MIT | LLM API 支撑的 TypeSafeClient 替代 | 2026-08-08 |
| Heman10x-NGU/openJev-verdict-2.0 | 205 | NOASSERTION | 151M，宣称 77.10% acc / 0.0636 Brier / 0.0144 ECE | 2026-09-19 |
| logan-markewich/jeff | 173 | MIT | 基于 GliFormer 的自托管替代 | 2026-09-19 |
| ikermoel/open-alternative-jev | 38 | Apache-2.0 | Qwen3.5-4B 方案 | 2026-09-18 |

**Laya 相关第三方评测（要点，供任务 2 用）：**
- Laya：Convai Innovations，421M（ModernBERT-large 主干 + 从零训练的 decision head），Apache-2.0，三个 checkpoint（`laya` 英语 512 上下文、`laya-multilingual` mmBERT-base 322M 1024、`laya-typed-decisions` 421M 1024）。
- 作者自报速度：T4 上 英语单问题 39.5 ms，多语言 32.8 ms，批量多语言 7.2 ms/问题。
- **Laya 模型卡自述：zero-shot typed-decisions 准确率仅 0.362（接近随机）；0.766 需要在该 benchmark 自己的训练 split 上微调。**
- 其作者 Nandakishor Mukkunnoth 发过 priority claim（HN 1,231 点）：他 2025 年 3 月就发布了非自回归 RL 决策模型（arXiv 2503.23303）Apache-2.0 权重，认为 Jev 是同一想法在 2026 年 9 月以无权重、计量 API 的形式推出。
- 来源：https://aiweekly.co/alerts/convai-ships-laya-a-421m-modernbert-decision-model-apache-20 ；https://fdeinterviews.com/blog/what-is-jev-typesafe-ai-system-one-model ；https://mindpattern.ai/e/modernbert

**APUS（中国）复现（供任务 3 参考）：**
- 央广网 2026-09-20：APUS AI 实验室 9 月 19 日公布「全球最早一批针对 Jev 的独立开源复现成果」，包装为 Agent Skill **`fast-browser-use`**，MIT 协议，支持本地离线执行（macOS/Linux/Windows，有/无 GPU 皆可）。
- 复现内容（**项目方说法**）：「复现了单 Token Logits 快速决策，跳过自回归解码的过程，实现了 Jev **KV-Cache 广播与并发批量评估**的工作机制」。
- 实测（**项目方说法**）：Apple M2 Pro 笔记本上，本地运行 Qwen3.5-9B，真实维基百科检索任务中位耗时约 **18 秒**，表单填报/站内导航约 **3 秒**，单任务模型打分仅 **4 次**，全程零云端调用、零 API 费用。
- 来源：https://www.cnr.cn/tech/techph/20260920/t20260920_527819594.shtml （另见搜狐转载 https://m.sohu.com/a/1078660919_362042/）

---

## 14. 明确未能核实 / 存疑项清单

| # | 项目 | 状态 |
|---|---|---|
| 1 | The Register 2026-09-16 原文（*TypeSafe AI debuts model for machines that plays Doom*） | ❌ 抓取失败（JS 渲染 + 网络错误）。仅通过多方转述引用其论点（"cannot hallucinate" 被质疑、$40M、Doom demo、0.114s vs 8.566s、Claude Fable 5.1 单价对比）。 |
| 2 | Business Wire 官方新闻稿全文 | ❌ 403 Forbidden。仅有转载摘要。 |
| 3 | 估值 ~$200M | ⚠️ 第三方报道（AIToday 称 "reported $200 million"，ai miracle 称 Forbes 报道）。**未在官方渠道核实。** |
| 4 | "未对中国大陆开放" | ⚠️ 央广网陈述。我未在官方条款/文档中找到地区清单。 |
| 5 | 官网 `[b.64]` base64 段落、FAQ 折叠内容（7 条问答的答案） | ❌ FAQ 答案由 JS 动态加载，HTML 里只有问题文本，未取得答案正文。 |
| 6 | KV-cache 复用 | ❌ 官方文档零提及。仅 APUS 第三方复现称其存在。 |
| 7 | 显式 batch endpoint / 跨请求缓存 | ❌ 官方文档无。 |
| 8 | 官方是否支持 streaming | ⚠️ 官方文档无明文"不支持"。Pydantic AI 集成文档明确「nothing to stream」。 |
| 9 | 参数量、架构细节、训练数据来源 | ❌ 官方未公开（博文 FAQ 有 "Where does our training data come from?" 一问，但答案未能取得）。 |
| 10 | "waitlist 36 小时清掉 ~140,000 报名" | ⚠️ explainx.ai 引述 TypeSafe 自述，**未核实**。 |
| 11 | LangChain 博客署名与日期 | ⚠️ Capital & Compute 引用为 Sydney Runkle 与 Hunter Lovell、2026-09-17；我抓取的页面正文中未见署名。 |
| 12 | 早期访问 onboarding 页（"Welcome inside TypeSafe: Meet Jev"）内容 | ⚠️ 需鉴权，无法独立访问。Capital & Compute 转述，可信度中等。 |
| 13 | Hacker News 原帖（item 49717558）内容 | ❌ 未直接核实；通过 explainx.ai / zenn 转述。 |
| 14 | `jevaiguide.com`、`jevmodel.org` 等第三方站点的独立性 | ⚠️ 均自称"独立、非官方关联"，但无法验证其实际独立性。已将其中内容在本文档中标注为第三方。 |

---

## 15. 引用链接全集

**官方**
- 官网 https://typesafe.ai/
- 官方博文 https://typesafe.ai/blog/introducing-system-one-models-and-jev
- 官方团队页 https://typesafe.ai/team
- 官方宣言 https://typesafe.ai/manifesto
- 官方文档 https://docs.typesafe.ai/ （索引 https://docs.typesafe.ai/llms.txt）
- 官方评测 https://evals.typesafe.ai/
- 官方 Skill 仓库 https://github.com/typesafe-ai/skills
- 官方 LLM 适配器 https://github.com/typesafe-ai/system-one-adapter-python
- 官方 SDK：`typesafe-sdk`（Python）、`@typesafe-ai/sdk`（TS）
- 商业新闻稿（403）https://www.businesswire.com/news/home/20260915525333/en/

**第三方 — 独立评测/质疑**
- Every（Mike Taylor）https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds
- Arize AI（Laurie Voss）https://arize.com/blog/typesafe-jev-llm-judge/
- Capital & Compute https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/
- paddo.dev https://paddo.dev/blog/thirty-cent-judge
- Near Here https://nearhere.events/blog/typesafe-jev-mistral-gemini-event-validation
- gemanor https://github.com/gemanor/jev-code-review-benchmark
- FDEInterviews https://fdeinterviews.com/blog/what-is-jev-typesafe-ai-system-one-model
- DataCamp https://www.datacamp.com/blog/system-one-models-jev
- The Decoder / The Register（转述）https://universaldigitalassistant.com/launches/typesafe-ai-jev/ ；https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711

**第三方 — 集成方**
- LangChain https://www.langchain.com/blog/building-a-harness-with-jev
- Pydantic AI https://pydantic.dev/docs/ai/models/typesafe/
- Vercel https://vercel.com/kb/guide/typesafe-jev-and-ai-sdk
- Netlify https://www.netlify.com/changelog/typesafe-jev-ai-gateway/

**第三方 — 中文**
- 央广网（中国官方媒体，APUS 复现 + 大陆未开放）https://www.cnr.cn/tech/techph/20260920/t20260920_527819594.shtml
- Eigent https://www.eigent.ai/zh-CN/blog/typesafe-ai-jev-system-one-models
- IT之家 https://www.ithome.com/1/003/584.htm
- 博客园 https://www.cnblogs.com/sing1ee/p/23040079
- AI工具集 https://ai-bot.cn/jev/
- AIHub https://www.aihub.cn/ai-model/typesafe-jev/

**第三方 — 手册/百科类（独立声明，未验证）**
- https://jevaiguide.com/ （自称独立手册，含渠道对比与错误码）
- https://jevmodel.org
- https://jevpatterns.com
- https://jev-agent.com
- https://jevai.wiki
- https://systemonemodels.org/models/jev/
- https://madewithjev.com/what-is-jev

---

*文件生成于 2026-09-21。所有数字均标注来源；标注为「官方」的是 TypeSafe 自有材料（公司自测/自述），标注为「第三方」的是外部材料。*
