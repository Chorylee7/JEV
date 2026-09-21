# 任务 4｜基准、生态与批判视角（原始资料）

采集日期：2026-09-21（UTC+8）
采集方式：`gh api`（账号 Chorylee7，token 有 repo 权限）＋ FetchURL / WebSearch
核心原则：**严格区分「TypeSafe 官方宣称」「开源复现项目方自测」「第三方独立测试」**；查不到的一律标注「未核实」。

---

## 0. 核实方法与本文件的可信度声明

| 类别 | 定义 | 本文件中的标记 |
|---|---|---|
| 官方宣称 | TypeSafe 自家博客／文档／evals 站点／early access 页面 | 【官方】 |
| 项目方自测 | 开源复现项目自己跑的 benchmark，无第三方复现 | 【项目方自测】 |
| 第三方独立 | 无披露关联的独立个人/机构自行设计任务、自行选对照组、自行定答案 | 【第三方独立】 |
| 我方核实 | 本次用 `gh api` / HTTP 直查得到的一手数据 | 【本次核实】 |
| 未核实 | 无法确认 | 【未核实】 |

**重要方法论警告（贯穿本文件）**：Jev 的官方 benchmark 准确率不是对照人工标注的 ground truth，而是**对照「GPT-6 Astra 与 Claude Fable 5.1 输出的平均值」**。这一点被多家媒体与独立研究者反复指出。

---

## 1. 版本、价格、上下文基线（用于对比表锚点）

### 1.1 官方公布的模型与定价【官方】

| 项目 | 值 | 来源 |
|---|---|---|
| 模型 ID | `jev-1.13.0`（通过 `jev-latest` 别名到达） | docs.typesafe.ai/models（经 Capital & Compute 引用） |
| 端点 | `POST https://api.typesafe.ai/v1/systemone` | apidog 文章、官方文档 |
| 输入价格 | **$0.042 / 百万 input token**（= $42 / 十亿） | typesafe.ai 首页 + docs |
| 输出价格 | **$0（免费）**，官方原话 "too cheap to meter" | 官方发布博客 |
| 上下文 | 整请求 64k token；`state` + 单条最长 question 合计上限 32k | docs.typesafe.ai/models |
| 速率限制 | 250,000 token/s，1,200 请求/分钟（官方注明早期访问期间会变动） | docs.typesafe.ai/models |
| 端到端延迟 | 70ms–500ms | 官方发布博客 |
| 三个原语 | `Choice`（最多 255 选项）、`Score`（有序量表）、`Noul`（0–1 布尔概率） | docs.typesafe.ai |
| 训练方法 | RLCD（Reinforcement Learning for Calibrated Decisions），配方未公开 | 官方博客 |
| 权重开源 | **否**，闭源、纯云端 API，无自托管方案 | 官方；cndba.cn 中文分析亦确认「无公开模型权重、无训练代码、无完整架构论文」 |

### 1.2 官方宣称的倍数，以及同一家公司在不同页面上给出**互相矛盾**的区间【关键发现】

Capital & Compute 把 TypeSafe 自己三个不同页面的数字并列，发现互不一致：

| 出处 | 更快 | 更便宜 |
|---|---|---|
| typesafe.ai 首页 | 193.6x | 444.6x |
| 发布博客 Evidence 段 | 40x–200x | 未公布区间 |
| **Early-access 登录后 onboarding 页（非公开）** | **20x–200x** | **40x–1,000x** |
| 该站按官方 evals 表格手算 | 约 25x–95x | 76x–440x |

来源：https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/

**要点**：
- onboarding 页的**速度下限 20x 是公开博客下限 40x 的一半**。
- 只有非公开页面公布了成本区间，且宽到 40x–1,000x（25 倍跨度）。
- 444.6x 的来源被同一分析追出：**就是 Claude Opus 5 那一行单独算出来的**（Jev $0.0004/case vs Opus 5 $0.1761/case ≈ 440x），不是跨模型平均。相对 GPT-5.6 Terra 是约 76x。
- 官方自己注明这些数字「处于真实收益的高端」。

### 1.3 官方 evals 一手数据【官方，本次直接从 evals.typesafe.ai HTML 抓取，非二手转述】

> ✅ 这一节的数字是我从 `evals.typesafe.ai` 各页面 HTML 中直接解析出来的，**不是媒体转述**。来源：https://evals.typesafe.ai/

**关键方法学原文（官方自己写的，可整句引用）**：

> "For this eval, the reference labels are generated via **an average of the responses of GPT-6 Astra and Claude Fable 5.1**, both at high thinking, answering every question in the harness. All other models are evaluated using **the provider's default reasoning settings**."

> 解读：**参考答案不是人工标注，是两个模型的平均回答**。这直接支持了 juejin、Arize、explainx 三方的批评。

**官方图表把每个模型跑两种模式**，这个区分在二手报道里几乎全被忽略：
- `· workflow ·` = 用 TypeSafe 自己的 structured-decision wrapper（官方称这是最准的抽取方式，但更慢更贵）
- `· prompt ·` = 自由 prompt

#### 表 1.3a：四个工作流的平均值（evals 首页）

| 模型 | 模式 | 准确率 | 成本/case | 时延/case |
|---|---|---|---|---|
| **Jev** | **workflow** | **67.8%** | **$0.0004** | **0.4 s** |
| GPT-5.6 Terra | workflow | **67.9%** | $0.0304 | 10.1 s |
| GPT-5.6 Terra | prompt | 61.6% | $0.0750 | 25.1 s |
| GPT-5.6 Sol | workflow | **74.1%** | $0.0836 | 23.3 s |
| GPT-5.6 Sol | prompt | 63.4% | $0.2005 | 48.6 s |
| GPT-5.6 Luna | workflow | 66.8% | $0.0033 | 12.9 s |
| GPT-5.6 Luna | prompt | 51.9% | $0.0079 | 27.3 s |
| Claude Opus 5 | workflow | **73.1%** | $0.1761 | 37.8 s |
| Claude Opus 5 | prompt | 64.8% | $0.3417 | 70.5 s |
| Claude Sonnet 5 | workflow | 67.8% | $0.1174 | 78.1 s |
| Claude Sonnet 5 | prompt | 60.4% | $0.2251 | 149.2 s |
| Claude Haiku 4.5 | workflow | 53.6% | $0.0195 | 12.5 s |
| Claude Haiku 4.5 | prompt | 18.1% | $0.0363 | 21.2 s |
| DeepSeek V4 Flash | workflow | 64.4% | $0.0059 | 51.9 s |
| DeepSeek V4 Flash | prompt | 59.3% | $0.0132 | 120.1 s |
| DeepSeek V4 Pro | workflow | 65.5% | $0.0413 | 86.5 s |
| DeepSeek V4 Pro | prompt | 59.7% | $0.0907 | 192.1 s |

> **关键读法**：Jev 的 67.8% 与 Terra workflow 的 67.9% 打成平手，与 Sonnet 5 workflow 的 67.8% **完全同分**；落后 Sol workflow 6.3 点、Opus 5 workflow 5.3 点。Jev 比 Luna workflow（66.8%）、DS V4 Pro workflow（65.5%）、DS V4 Flash workflow（64.4%）、Haiku 4.5 workflow（53.6%）都高。**但 Jev 的成本 $0.0004 比 Luna 的 $0.0033 还低 8 倍。**

#### 表 1.3b：逐工作流——**Jev 的表现高度任务依赖，且有一个工作流几乎垫底**

**① Security Incidents（安全事件处置）**

| 模型 | 模式 | 准确率 | 成本/case | 时延 |
|---|---|---|---|---|
| Claude Opus 5 | workflow | **66.2%** | $0.0574 | 15.1 s |
| GPT-5.6 Sol | workflow | **62.5%** | $0.0295 | 8.5 s |
| **Jev** | **workflow** | **61.7%** | **$0.0001** | **0.3 s** |
| Claude Sonnet 5 | workflow | 60.8% | $0.0271 | 18.9 s |
| Claude Haiku 4.5 | workflow | 58.8% | $0.0047 | 3.4 s |
| GPT-5.6 Luna | workflow | 52.1% | $0.0013 | 7.0 s |
| GPT-5.6 Terra | workflow | 51.2% | $0.0119 | 5.7 s |
| DeepSeek V4 Pro | workflow | 41.7% | $0.0234 | 60.0 s |
| DeepSeek V4 Flash | workflow | 37.9% | $0.0032 | 37.4 s |
| Claude Haiku 4.5 | prompt | **17.1%** | $0.0068 | 4.6 s |

> Jev 在这个工作流上是**第一名之下**，仅次于 Opus 5 和 Sol。**成本 $0.0001/case 是全场最低**（比 Luna 的 $0.0013 还低 13 倍）。

**② Invoice Processing（发票处理）—— Jev 几乎垫底**

| 模型 | 模式 | 准确率 | 成本/case | 时延 |
|---|---|---|---|---|
| GPT-5.6 Sol | workflow | **79.1%** | $0.2152 | 34.3 s |
| Claude Opus 5 | workflow | 78.4% | $0.4856 | 92.1 s |
| GPT-5.6 Terra | workflow | 74.7% | $0.0778 | 17.3 s |
| Claude Sonnet 5 | workflow | 72.9% | $0.3616 | 241.3 s |
| DeepSeek V4 Pro | workflow | 72.7% | $0.0830 | 137.4 s |
| DeepSeek V4 Flash | workflow | 69.8% | $0.0133 | 84.1 s |
| GPT-5.6 Luna | workflow | 67.8% | $0.0081 | 21.4 s |
| **Jev** | **workflow** | **61.8%** | **$0.0011** | **0.5 s** |
| Claude Haiku 4.5 | workflow | 42.9% | $0.0558 | 30.8 s |
| Claude Haiku 4.5 | prompt | **6.0%** | $0.0763 | 63.4 s |

> ⚠️ **在发票处理上，Jev（61.8%）只赢过 Haiku 4.5，输给全部其他 8 个模型的 workflow 模式**，包括最便宜的 Luna（67.8%）和 DeepSeek V4 Flash（69.8%）。**这是报告「风险与局限」章节必须引用的一格。**

**③ Customer Service（客服路由）—— Jev 表现最好**

| 模型 | 模式 | 准确率 | 成本/case | 时延 |
|---|---|---|---|---|
| GPT-5.6 Sol | workflow | **78.3%** | $0.0323 | 10.1 s |
| DeepSeek V4 Flash | workflow | 76.8% | $0.0029 | 34.6 s |
| DeepSeek V4 Pro | workflow | 76.1% | $0.0232 | 58.6 s |
| **Jev** | **workflow** | **76.0%** | **$0.0001** | **0.4 s** |
| GPT-5.6 Terra | workflow | 72.7% | $0.0111 | 6.0 s |
| Claude Opus 5 | workflow | 72.4% | $0.0579 | 16.6 s |
| GPT-5.6 Luna | workflow | 71.4% | $0.0013 | 8.8 s |
| Claude Sonnet 5 | workflow | 69.3% | $0.0264 | 14.3 s |
| Claude Haiku 4.5 | workflow | 55.4% | $0.0074 | 8.8 s |

> Jev 76.0% 排第四，**击败 Opus 5、Terra、Sonnet 5、Luna**，且成本最低。

**④ Agent Trace Observability（Agent 轨迹可观测性）**

| 模型 | 模式 | 准确率 | 成本/case | 时延 |
|---|---|---|---|---|
| GPT-5.6 Sol | workflow | **76.6%** | $0.0575 | 40.3 s |
| GPT-5.6 Luna | workflow | 76.1% | $0.0025 | 14.5 s |
| Claude Opus 5 | workflow | 75.2% | $0.1033 | 27.4 s |
| DeepSeek V4 Flash | workflow | 73.0% | $0.0043 | 51.7 s |
| GPT-5.6 Terra | workflow | 73.0% | $0.0209 | 11.4 s |
| DeepSeek V4 Pro | workflow | 71.6% | $0.0357 | 90.1 s |
| **Jev** | **workflow** | **71.6%** | **$0.0003** | **0.5 s** |
| Claude Sonnet 5 | workflow | 68.0% | $0.0545 | 38.0 s |
| Claude Haiku 4.5 | workflow | 57.2% | $0.0100 | 7.1 s |

> Jev 71.6% 并列第六，击败 Sonnet 5 和 Haiku 4.5，成本仍最低。

**官方 evals 的四条自我披露局限（官方写在发布博客里，可引用）**
1. 准确率 = 与「GPT-6 Astra 与 Claude Fable 5.1 平均回答」的一致度，把 OpenAI / Anthropic 的「文风」烧进了答案键。
2. 四个工作流由 **TypeSafe 自己的 capabilities team 构建**，不在训练数据里，但**也未经独立审计**。
3. 时延在**美西的笔记本上**测得，靠近其服务区域；其他地区读者应预期更差。
4. 竞争 LLM 是通过 **TypeSafe 自己的 structured-decision wrapper** 跑的。

来源：https://evals.typesafe.ai/ 、https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/ 、https://forkast.news/typesafe-ais-jev-is-not-an-llm-and-that-may-be-the-point/

### 1.3c 官方数字之间又自相矛盾：440x vs 444.6x vs 193.6x【关键发现】

explainx.ai 在 2026-09-21 指出：
> "a **Jev Playground claiming '440x cheaper than LLMs'**, and a new decision-model benchmark, **JevBench, with Jev reportedly leading at 75.3**. **Neither claim comes with a linked source article, and the 440x figure is already the second different 'Nx cheaper' number TypeSafe has published in a week.**"

→ 到 2026-09-21，TypeSafe 系对外给出的「便宜倍数」至少有 **444.6x、440x、40x–1,000x、40x–400x** 四个版本；「更快倍数」至少有 **193.6x、20x–200x、40x–200x** 三个版本。**报告应把「倍数不一致」本身作为一个事实呈现。**
⚠️ **未核实**：JevBench 的 75.3 分、Jev Playground 的 440x 声称——我只见到 explainx 的转述，**未找到一手来源**。

### 1.4 官方 early-access 页面自曝的能力天花板【官方，仅登录后可见】

Capital & Compute 引用（该页面非公开、需登录）：

- **推理深度**：官方称 Jev 在需要高推理的 System 2 任务上弱于大推理模型，**自己举的例子是数学推理和国际象棋**。
- **领域知识**：官方称 Jev 没有小众领域的深度知识，解决办法是把缺失上下文塞进 state。
- **「前沿级智能」这一条**：官方在 onboarding 页承认这是**最难辩护的一条宣称**，并说这个领域**没有人找到好的证明方式**，请用户自己实验判断。
- 官方称能「有盈利地」提供这些模型（公司单方面声明，无证据）。
- 官方称无法证明价格未被补贴，并预计价格会下跌而非上涨。

### 1.5 融资与团队（已核实到二手一手混合）

| 事实 | 值 | 来源 |
|---|---|---|
| 出隐时间 | 2026-09-15 | Business Wire 稿（2026-09-15） |
| 种子轮 | 约 $40M，DCVC 领投 | Business Wire；Forkast |
| 估值 | 约 $200M（reported） | Forkast |
| CEO/联创 | Diogo Almeida（前 OpenAI，InstructGPT 论文作者之一，RLHF 共同发明人） | Forkast |
| 其他联创 | Erik Gafni（CTO，前 DNA 测序多模态 AI 创业、Invitae/Freenome 早期员工）、Sasha Sheng（COO，前 Meta/FAIR News Feed） | Forkast、juejin 中文长文 |
| 命名来源 | Jevons Paradox（杰文斯悖论） | Forkast |
| 生产客户 / 收入 | **无具名客户、无披露收入**（截至 2026-09-18） | Forkast |

---

## 2. 第三方独立评测（本任务最核心的产出）

**这是目前唯一一组「测试者自己选任务、自己选对照组、自己定答案」的证据。** 全部集中在 2026-09-15 至 09-19 这 5 天内发布。

### 2.1 五组外部测试总表（Capital & Compute 汇总 + 我逐条查证）

| 测试者 | 任务与样本量 | 对照组 | 测到的数字 | 类型 |
|---|---|---|---|---|
| **Mike Taylor, Every** | 777 次判断 / 37 篇文档（含 10 篇故意 AI 风格仿作）；另称总计 1,709 次 | Claude Fable 5.1 | 约 **25x 更快、约 580x 更便宜**；777 次判断 <0.7s，约 $0.0000032/判断（≈1/4 美分）；writing-quality 测试中 12 段（6 干净 6 植入缺陷）里抓到 6/7 个植入缺陷，Fable 抓 7/7 | 【第三方独立】 |
| **Near Here**（英国活动发布商） | 活动列表审核，50 例 | Mistral Small 4、Gemini 3.5 Flash-Lite | **8.6x 和 58x 更便宜**；Jev 对 48/50，对照组 42 和 43；Arize 引用为「96% vs Gemini Flash-Lite 86%」；LLM 每题花约 910 output token，Jev 花 85（且不计费） | 【第三方独立】 |
| **gemanor benchmark** | Python code review，4 条规则，24 个程序族 ×5 版本 ×3 轮 = **1,080 次调用** | Gemini 3.8-Flash、Claude Fable 5.1（均 medium reasoning） | **45x 和 274x 更便宜**；中位响应 0.75s vs 3.59s vs 4.31s；正确率 **98.0% vs 100% vs 100%**；1000 次外推 $0.043 / $1.943 / $11.780；三轮间决策改变率 0.83% vs 0% vs 0% | 【第三方独立】 |
| **Paddy Alton, paddo.dev** | **9,081 条真实产品匹配裁决**（生产队列） | 无对照组 | 整队列 **$0.32**；**30% 弃权**（Refute 4,443 / Confirm 1,952 / **Abstain 2,686**） | 【第三方独立，唯一真实生产队列】 |
| **Laurie Voss, Arize AI** | 垃圾邮件分类，**18,514 封邮件**，**真实标签** | 用约 14,800 封标注邮件训练的 TF-IDF 逻辑回归 | **Jev 98.3% vs TF-IDF 98.4%**，差异不具统计显著性；两者在 466 封上分歧且几乎均分 | 【第三方独立，唯一用真实 ground truth 标签】 |
| **Capital & Compute（本站）** | 483 条真实 Search Console 查询；另 120 条复跑 | 无（换算到 GPT-5.6 Luna / Claude Haiku 4.5） | 中位 **314ms**、p95 **399ms**（落在官方 70–500ms 区间内，**官方唯一被精确复现的宣称**）；483 条共 **$0.0115** = **$0.0238/千次**；**57.8% 答案置信度 <0.5，94.4% <0.8** | 【第三方独立，自跑脚本已提交到仓库】 |

来源：
- https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds
- https://nearhere.events/blog/typesafe-jev-mistral-gemini-event-validation
- https://github.com/gemanor/jev-code-review-benchmark
- https://paddo.dev/blog/thirty-cent-judge
- https://arize.com/blog/typesafe-jev-llm-judge/
- https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/

### 2.2 三组独立测试者给出的「每次决策成本」高度互相吻合，但都远低于官方【关键发现】

| 测试者 | 每次决策成本（换算） |
|---|---|
| Near Here | $0.043 / 1,000 次 |
| gemanor code review | $0.043 / 1,000 次 |
| Paddy Alton | $0.035 / 1,000 次 |
| Capital & Compute（483 条真实查询） | $0.0238 / 1,000 次 |
| **TypeSafe 官方 evals 表格推算** | **$0.40 / 1,000 次** |

三个互不相关的测试者落在彼此 23% 以内，却只有官方自己数字的约 1/9。原因：**每次决策成本由你送进去的 state 体量决定，官方 evals 用的是异常肥的 context。**

### 2.3 「弃权率」（abstain rate）——官方营销完全没提的成本杀手【关键发现】

Capital & Compute 推导的公式：

```
blended multiple = M / (1 + a × M)
M = 已回答 case 上的倍数，a = 弃权率
当 M 变大时收敛到 1/a
```

以 Paddy Alton 实测 30% 弃权率为准：

| 弃权率 | blend 后成本/决策 | 对 Terra 的有效倍数 | 任何 Jev 价格下的天花板 |
|---|---|---|---|
| 0% | $0.00040 | 76x | 无 |
| 1% | $0.00070 | 43x | 100x |
| 5% | $0.00192 | 16x | 20x |
| 10% | $0.00344 | 8.8x | 10x |
| **30%（实测）** | **$0.00952** | **3.2x** | **3.3x** |

- 76x 的优势在弃权率超过约 **3.7%** 时掉到 20x 以下，超过约 **8.7%** 时掉到 10x 以下。
- 440x（对 Opus 5）同样塌到约 3.3x：**无论 Jev 多便宜，30% 弃权率把节省封顶在约 2/3**。
- Capital & Compute 自己薄 state 时弃权率 57.8%，天花板 1.7x。把 state 加厚（加 3 个字段）后，0.5 阈值下弃权率从 **65.0% 降到 40.0%**（−25 个百分点），平均置信度 +23%；但 0.8 严格阈值下不变（95.8%）。
- 结论：**Jev 的置信度是「你给它多少上下文」的函数，薄 state 是自己造成的弃权率。**

### 2.4 中文独立实测（硅星人 / 新浪转载）【第三方独立】

https://k.sina.com.cn/article_5952915720_162d2490806704v6wc.html?from=tech （作者｜董道力，来源：硅星人）

- 样本：**50 条中文电商客服问题**，每题 4 项判断（紧急度、售前概率、处理类别、严重度），**四项全对才算对**。
- 分组：便宜小模型组（含 Jev）、国产模型组（GLM 5.3 Flash、DeepSeek V4 Pro、Qwen 3.8 Flash、Kimi K3、MiniMax M3）、强模型组（GPT-5.5、Claude Opus 5、Claude Sonnet 5、Gemini 3.1 Pro Preview）。
- **结果**：Jev 平均约 **32–32.6 分 / 50**，完整准确率 **约 64%–65.2%**。
  - 在便宜小模型组排第二，**只比 DeepSeek V4 Flash 少 1.2 分**。
  - 在强模型组**排最后**。MiniMax M3 约 38 分，比 Jev 多做对约 5.4 题，**完整准确率高约 10.8 个百分点**。
  - 但成本差距「没有想象中那么大」：50 题 MiniMax M3 只多花约 **$0.0035**，平均每题约 1.80s。
- **速度/成本**：Jev 平均每题 **0.73–0.75s**，50 题总成本约 **$0.002**，两项均为测试中最低。DeepSeek V4 Flash 每题需 5.58s，成本约为 Jev 的 2.5 倍。
- **阈值附近的抖动**（重要工程细节）：人工标注严重度下限 2.00，Jev 给 **1.99**；某条临期食品问题人工紧急度 0.75，Jev 给 **0.71–0.72**。重复 15 次，**有 3 道题出现通过/失分交替**。
- 该测试自认不足：50 条中文样本不足以代表所有任务；且**不能验证概率校准**（它按题目判分，没做校准曲线）。

### 2.5 独立校准测试：scienthoon/jev-ood-calibration【第三方独立，最有批判价值】

仓库：https://github.com/scienthoon/jev-ood-calibration （MIT，3 stars，2026-09-19 创建）
跑法：Vercel AI Gateway `typesafe-ai/jev`，AI SDK 7.0.107 `experimental_evaluate`，`zeroDataRetention: true`，3,721 条公开 benchmark + 900 条自造合成项，0 失败调用。可复现成本约 **$0.06**。

**公开 benchmark（很可能在 Jev 训练集里）**

| 数据集 | n | Accuracy | NLL | ECE | ECE/噪声底 | Refit T |
|---|---|---|---|---|---|---|
| OpenBookQA (val) | 500 | 94.2% | 0.172 | 0.024 | 1.0× (0.024) | 0.96 |
| CommonsenseQA (val) | 1,221 | 88.1% | 0.395 | 0.032 | 1.7× (0.019) | 1.35 |
| HellaSwag (val, 2k) | 2,000 | 86.1% | 0.420 | 0.029 | 1.6× (0.018) | 1.00 |

> 该仓库明确指出：这些准确率**远高于 3–8B 模型 zero-shot 表现**，与「训练集包含这些数据集 train split」一致；污染无法证实也无法排除。因此校准数字应读作 **in-domain 校准**。

**自造合成客服工单（Jev 不可能见过）**

| 问题 | 类型 | n | Accuracy | 随机基线 | NLL | ECE | Refit T | 读数 |
|---|---|---|---|---|---|---|---|---|
| 该进哪个队列？ | choice(4) | 300 | 89.0% | 25% | 0.697 | 0.082 | **3.29** | 对，但错答也给 1.00 |
| 客户生气吗？ | boolean | 300 | 91.7% | ~50% | 0.275 | 0.079 | **0.66** | **欠自信** |
| 优先级（组织规则） | score(4档) | 300 | **44.7%** | 25% | 1.331 | 0.325 | **3.40** | 无从得知；平均声称概率 **0.74** |
| 全部 | | 900 | 75.1% | | 0.768 | 0.107 | **2.74** | |

- 900 条集合的 ECE 噪声底（完美校准模型、同样预测分布、200 次重采样）= **0.024**。实测 **0.107 是噪声底的 4.4 倍**。
- **优先级标签由「不在文本里」的规则定义**——这是关键设计：任何 zero-shot 模型都无法从文本恢复该标签。问题不是 44.7%，而是 **Jev 的概率没有反映它「不知道」**：平均给选中档位 0.74。
- **失准方向随问题类型翻转**：choice/score 过度自信（T 3.3–3.4），boolean 欠自信（T 0.66）。**因此固定阈值是否安全取决于问题类型，而不只是任务。**

**其他独立校准数据（该仓库引用）**

| 研究 | 数据 | 结果 |
|---|---|---|
| bitnovus/jev-spam-eval | 约 9.9k 真实邮件（5,733 ham/spam/phishing + 3,300 新 + 853 近期钓鱼） | **98.6%** 准确率（带上下文增强、无任务特定拟合）；**未报 ECE** |
| anisselbd/jev-phishing-bench | 2,000 封邮件 | Jev **62.6% [60.5, 64.7]**，ECE **0.154**（10 bins）；Claude Haiku 4.5 的 ECE 为 **0.097** |
| SamuelSacco/jev-exploration 难度梯度集 | 800 项（无污染） | ECE 为噪声底的 **2.1–2.5×**；误差集中在中段；p≥0.9 时每一档命中率都是 1.000（覆盖率 21.5–32.5%），**在该集合上 0.9 阈值是安全的**；建议「当作单调分数而非概率，本地自行校准」 |
| 该仓库对 bitnovus 的重分析 | — | 可靠性曲线**高估低概率、低估高概率** |

**该仓库的三个「下阈值前必读」脚注**

1. **概率被量化到 0.01，且频繁恰好是 0 或 1。** OpenBookQA 的 2,000 个选项概率里有 **1,051 个恰好为 0**。**有 1 项给正确答案 0.00**（给错误答案 1.00，confidence 0.99）。**概率恰好 0 无法被 temperature scaling 修复**——这一项贡献了 0.172 平均 NLL 中的 0.028。这同时也是对别处「confidence 1.000 时零失误」观察的反例。
2. **失准方向按类型翻转**（同一批输入上 choice/score 过度自信、boolean 欠自信），说明这是**按类型分别后处理**，不是单一已校准分布。**要按问题校准，不要按模型校准。**
3. **不要用 `confidence` 字段做阈值。** 在这些集合上它**从未优于 max probability**，有时差很多（合成集上 ECE 0.18）。

### 2.6 独立行为研究：RINNECODER/jev-behavior-study【第三方独立】

仓库：https://github.com/RINNECODER/jev-behavior-study （MIT，3 stars，2026-09-16 创建）
规模：**11,621 次文本研究请求** + 3 个 Snake 研究 + 3D City lab + 7 份详细报告。观测时间 2026-09-16~17。自述「独立、AI 辅助研究」。

- **中心结论**：表现取决于**确切任务与措辞框架**；**前置问题的正确答案不总能带来正确决策**；通过简单任务**不能**证明在更难版本上可靠。
- **3D 城市驾驶**：修正后的 pilot 完成 **0/12** 个完整任务；直接控制时在**全部 522 次转向调用中都选了直行**。原生图像驾驶标注为「不可用，等待经核实的图像接口」。
- **Snake 无协助（16 个新种子）**：原始提示 1/16 达标；改成**白话描述棋盘 + 显式优先级**后 **14/16**；绝对方向 12/16。最短移动比例 66.9% → 90.0%。
- **Snake 有协助（4,561 次调用，120 个固定状态，64 个 held-out 局）**：原始 Jev 0/16；把**精确路线事实**喂进去后 **16/16**；加 verifier 同 16/16；代码覆盖 0 次。

> 这组数字对「Jev 是否能自主决策」是相当不利的证据：加上正确答案就全对（16/16），不给就近乎全错（0/16）。

### 2.7 独立对标评测：4esv/jev-eval【第三方独立】

仓库：https://github.com/4esv/jev-eval （无 license，1 star）
跑法：`jev-1.13.0` vs `openai/gpt-5.6-terra`（经 OpenRouter），每任务 300 项，2026-09-17。

| 指标 | intent (77类) | sentiment (5档) | 正/负二分类 |
|---|---|---|---|
| Accuracy Jev / Terra | **0.78 / 0.85** | 0.57 / 0.59 | 0.97 / 0.97 |
| 超出噪声（95% CI） | borderline | 无差异 | 无差异 |
| ECE Jev / Terra | 0.11 / 0.08 | **0.20 / 0.30** | 0.04 / 0.02 |
| 中位时延 | 0.20s / 1.04s | 0.19s / 1.06s | 0.20s / 1.04s |
| 每千次成本 | $0.04 / $2.02 | $0.01 / $0.64 | $0.02 / $0.85 |

**关键条目**：
- **实际测得 5x 更快、41–50x 更便宜**，对照官方宣称的 **193x / 444x**。
- **Jev 对同一段文字计入约两倍 input token**（相同句子 340 vs 162）。
- 两个简单任务准确率持平；**77 路路由上低 6.7 个百分点**。
- 校准：一个任务优于 Terra，两个任务劣于 Terra。置信度对正确性的 AUROC：0.83/0.61/0.94（Jev），0.81/0.64/0.96（Terra）。
- **不是确定性的**：相同输入在 intent 上 **1.7%**、sentiment 上 **3.3%** 的条目改变标签。
- **「零幻觉」= 每个答案都是列出的选项**：对全部 1,800 次 Jev 调用成立；**对全部 1,800 次 Terra 调用在严格 JSON schema 下也成立**。
- Terra 用 `reasoning.effort=medium` 时在这些输入上只用 4–17 个 reasoning token，约 1s 答完，**且并不更准**。

### 2.8 fact-check 分析：explainx.ai【第三方分析，非原始测试】

https://explainx.ai/blog/jev-speed-cost-claims-fact-check-2026

| 问题 | 答案 |
|---|---|
| 宣称 | structured-output 任务上快 20–200x、便宜 40–400x |
| 谁测的 | TypeSafe 自测 |
| 对照什么 | 与前沿模型（GPT-6 Astra、Claude Fable 5.1）的**一致度**，非 ground truth |
| 独立测试 | Every：extraction 任务上约 25x 更快、约 580x 更便宜 —— "good but not perfect" |
| 官方自披露的准确率差 | 67.8%（Jev）vs 74.1%（最佳对照组） |

**该文提出的具体可检验批评**：
1. **一致性 ≠ 正确性**：若 Astra 与 Fable 5.1 在某类任务上有共同盲点，一个训练来「与这两个模型一致」的变体会**学会复现同一盲点**，却在这套方法下得高分。这是与 ground truth benchmark **结构性不同**的失效模式。
2. **苹果对苹果质疑（来自 HN 上线讨论区的单一评论者）**：被广泛引用的 **70ms vs 329s** 对比，据称是拿 Jev 对比一个**跑了完整 chain-of-thought 的 LLM**——而 CoT 是 Jev 结构上**完全做不到**的任务类别。若该描述准确，这不是两个系统做同一件事的速度差，而是拿 Jev 擅长的事对比一个根本更难的别的事。
3. **该文自认局限**：它综合二手来源（Arize AI、ts2.tech、Flowtivity、HN 帖子），**没跑自己的独立 benchmark**；70ms/329s 的批评是**单一 HN 评论者的说法**，非经审计的方法学控诉；**目前仍不存在**覆盖 Jev 全部用例的、逐任务的独立 benchmark。

### 2.9 LangChain agent-eval benchmark（目前「Jev vs LLM-as-judge」最强的一组第三方数据）

**来源层级说明**：原始出处是 **LangChain 的 X（Twitter）thread，作者 Daniel Shea 与 Seán Roche**（2026-09-20），配套 GitHub 仓库从该 thread 链接。我读到的是 explainx.ai 的详细转述（https://explainx.ai/blog/langchain-jev-agent-evals-benchmark-september-2026 ）。**⚠️ 我未直接读到 LangChain 的 X thread 原文**，因此下表标注为「第三方独立，经二手详细转述」。

**测试设计（够严谨，值得完整记录）**
- 目标 agent：用 LangChain 自家 **Deep Agents 0.7.15** 构建的 weather agent
- 测试集：**5 个 weather-request 示例**，定义为 LangSmith dataset，所有 judge 评同一批固定输入
- agent 的完整输出被**捕获为固定记录**存在 LangSmith 里 → **每个 judge 评的是同一份固定运行，而不是实时多变的 agent 行为**（这是 variance 比较有意义的前提）
- **人类 reviewer 独立按同一 rubric 标注每条固定响应，作为 oracle**
- 每个 judge 每条各评 **100 次**，四个 judge × 5 例 × 100 次 = **每个 judge 500 次重复判断**
- 每次采集两个信号：`quality`（连续分数）与 `does_pass`（二值）

**结果**

| Judge | Oracle 一致率（binary `does_pass`） | 每 case 平均方差（vs Jev） | 500 次总成本 | 平均时延 |
|---|---|---|---|---|
| **Jev** | **100%（500/500）** | **1×（0.0000149，最低）** | **$0.34** | **0.44 s** |
| GPT-5.6 Terra | 99.8% | **913× 更高** | 未公布 | — |
| GPT-5.6 Luna | 96.4% | **433× 更高** | 未公布 | — |
| Claude Sonnet 4.6 | **80.0%** | **92× 更高** | **$28.17** | — |

- Jev 每次调用 **$0.00035**；Claude Sonnet 4.6 在同样 500 次调用上花 **$28.17** → 差距约 **80,000×**。
- LangChain 还定义了一个组合指标 **signal value** = oracle 一致率 × 可重复性（同一 trace 两次独立调用给出同一判决的概率），**Jev 在该组合指标上得分最高**。
- LangChain 明确声明 variance 的差异是**观察性而非因果性**：一个假设是「Jev 的训练目标（typed answer 上的校准概率）更契合这种有界决策任务」，但实验不证明原因。

**LangChain 自己列出的三条局限（可直接引用）**
1. **测试很窄**：5 个 weather 示例、1 个目标 agent、1 个领域。换 agent / 换任务形态 / 换更难的判断，准确率和方差差距是否成立**未经验证**。
2. **低方差 ≠ 正确**：一个 judge 可以完全一致地一直错。「高准确率 + 低方差」的组合才是结果有意思的原因，**单看任何一个都不够**。
3. **便宜的评估能以同样快的速度放大错误**：一个低成本但系统性出错的 judge 会以规模化的方式产生坏信号。LangChain 的立场是**团队仍需要人在回路和 judge alignment**，而不是 Jev 取代了这两者。

**复现信息（LangChain 公开）**：GitHub 仓库 + 精确版本 `Deep Agents 0.7.15`、`langchain-openai 1.6.2`、`langsmith 0.12.6`、`tavily-python 0.8.3`。**temperature / top-p / seed / max tokens 全部用各 provider 默认值** —— 转述者指出这一点在你尝试精确复现 variance 数字时值得注意。
Jev 通过 **`langchain-typesafe==0.0.1a2`（alpha 阶段包）**访问；LLM judge 经 LangSmith Gateway 跑。**实验元数据里没有 Jev 的服务版本号**。

**结构性局限（与测试无关，永远适用）**：Jev 只回答对结构化 state 的类型化、有界问题。**它无法生成开放式批评、写自由形式的事后解释、或推理任何不能归约为 choice / score / yes-no 概率的判断。** 那些场景仍需要 LLM judge。

---

## 3. 开源复现／替代项目对比

### 3.1 apidog 对比表（本任务指定的核心来源，已完整读取）

来源：https://apidog.com/blog/openjev-open-source-jev-alternatives

**该文最重要的元结论（可直接引用）**：

> "None are benchmarked by a third party, and none are from TypeSafe."

**三类「开源 Jev」的实现捷径**：
1. **从冻结 chat 模型读 logits**（OpenJev/SemIf、mini-jev）
2. **从零训一个小 scorer**（jevlike）
3. **改解码引擎**（Apple Silicon 的 parallel-constrained-decoding、vLLM PR）

> **"None of them reproduce RLCD. That's the honest headline."**

| 项目 | 基座 | 复现的原语 | 校准 | HTTP server | 硬件 |
|---|---|---|---|---|---|
| OpenJev（现名 SemIf） | Qwen3.5-4B，冻结 | choice | 选项 logits 上的 softmax | 无（CLI + 浏览器 demo） | RTX 3090 级，CUDA |
| mini-jev | Qwen3-4B-Instruct，冻结 | choice、noul | 带 gap 的排序 | 有，端口 8765 | 8.5 GB 内存，MPS 或 CUDA |
| jevlike | 你自己训的 encoder | choice | 未声称 | 无 | CPU / MPS / CUDA |
| MLX engine | Qwen2.5-1.5B-Instruct-4bit | schema 字段 | 候选集上的 softmax | 有，端口 8000 | Apple Silicon，macOS 14+ |
| vLLM PR #57250 | DiffusionGemma | yes/no、choice、scale | logprobs + 熵 | 有，OpenAI 兼容 | vLLM 级 GPU，**未合并** |

**各项目的关键数字（均为【项目方自测】）**

**OpenJev / SemIf**（RTX 3090，Qwen3.5-4B）
- 直接 typed logits：**1.023 s** 得到 21 个概率对，对比自回归 JSON 数组 **5.332 s**（慢 5.21x）
- 在 **102 行 TypeSafe 子集**上 modal agreement **0.845**，对比已发表的 Jev **0.883**
  - ⚠️ **这是整组项目里唯一一处对真模型的对比，且是作者自己跑的 eval**
- 缺 `noul`/`score` 原语；概率是选项 logits 的 softmax，**不是 RLCD 校准过的置信度**
- ⚠️ **命名问题**：apidog 全文称其为 "OpenJev"，但该仓库现在已改名 **SemIf**（README 首行：「SemIf (formerly OpenJev)」）。apidog 文章在此点上是过时的。

**mini-jev**（Qwen3-4B-Instruct-2507，CLINC150 意图分类）
- **6,750 个配对观测**：JSON 0.909 准确率，字母读取 0.907，差 **−0.22 点**，95% CI **[−1.44, +1.04]**
- 32-token 文本上字母读取约 **4x 更快**
- README 自述：**"The letter shares are a ranking with a confidence gap, not calibrated probabilities."**（这句值得直接引用）
- 约 8.5 GB 内存，MIT，写作时 11 stars

**jevlike**（vinnylarouge）
- 约 **98%** on 合成菜单；**26%** on Wikispeedia（用冻结 Qwen2.5-0.5B encoder）vs 8% 打乱对照
- 一次前向「比被迫写 400 token 的小 decoder 快约 100 倍」
- README 自述：**"TypeSafe has not published its design. This repository is an independent starter model with the same input and output shape."** 并明确「**未展现与 Jev 同等的质量，也未复现 TypeSafe 的私有训练方法**」
- 忠实度是这组里**最低的**：你在自己的标签上训它，所以你得到的是**自己造的 classifier，不是能接受任意 criteria 的 decision model**
- apidog 记 764 stars；【本次核实】live = **1,097 stars**（MIT，2026-09-16 创建）

**MLX parallel-constrained-decoding（Apple Silicon）**
- M4 Max：4 字段欺诈 triage **420 ms 自回归 vs 75 ms 并行（5.6x）**；28 字段支持 triage **1,900 ms vs 270 ms（7.0x）**
- 声称 **100% schema 合法率**（因为从不采样自由文本）
- **只有时延，没有准确率**；这里的 "calibrated" 指候选集上的精确 softmax，**不是训练出来的校准**
- Apache 2.0；要求 M1 及以后、macOS 14+
- ⚠️ 该 HF Space 的 README **从未提及 Jev、TypeSafe 或 RLCD**，却在流传中被当作 "Typesafe.ai Jev open source alternative"

**vLLM PR #57250**（DiffusionGemma）
- 2026-09-16 开，**仍 open**；8.7 请求/秒（单 canvas 读），32 路并发时 54；语言分类语料上约 90% 准确率
- reviewer 指出**缺少 race-condition 测试**和**无界线程创建**为阻塞项
- **未合并前只适合读设计，不适合部署**

### 3.2 Laya（"开源版 Jev" 的最强竞品，也是最有争议的一处）

**基本事实（本次核实）**

| 项 | 值 | 来源 |
|---|---|---|
| GitHub | `NandhaKishorM/laya` — **5,028 stars**，450 forks，**Apache-2.0**，2026-09-18 创建，2026-09-20 最后推送 | 【本次核实】gh api |
| HF | `convaiinnovations/laya`（含 multilingual 子目录）、`convaiinnovations/laya-typed-decisions`，均 **Apache-2.0** | 【本次核实】HF API |
| 作者 | Nandakishor Mukkunnoth，Convai Innovations 创始人，自 2025-03 独自开发 | mer.vin |
| 背景论文 | arXiv:2503.23303（SalesRLAgent，2025-03）；arXiv:2510.01237（2025-09，置信度感知路由） | mer.vin |
| 架构 | 三个 checkpoint：`laya`（ModernBERT-large, **421M**, ctx 512）、`laya-multilingual`（mmBERT-base 256k vocab, **322M**, ctx 1024/8k）、`laya-typed-decisions`（ModernBERT-large 421M, ctx 1024）。路由为纯 Python Unicode script 检测 | mer.vin、note.com |
| 下载体积 | 英文单模型约 **808MB**；完整 bundle **2.5GB**；multilingual 子目录约 647MB | mer.vin |

**Laya 官方对比表的完整数字（mer.vin 转载）**

| Benchmark / 指标 | TypeSafe Jev 1.13.0 | Laya（含路由） | Delta |
|---|---|---|---|
| typed-decisions（2,000 决策） | 0.727 | **0.766** | +3.9 pts（超过 0.735 teacher 天花板） |
| AG News（4 标签） | 0.910 | **0.950** | +4.0 pts |
| DAIR Emotion（6 标签） | 0.480（Brier 0.846） | **0.595** | +11.5 pts；Jev 在 **16%** 的样本上给真实标签 **零概率** |
| Banking77（77 标签） | **0.870** | 0.425 | **Jev 领先** |
| 校准误差 ECE（越低越好） | 0.246 | **0.081** | 3x 更好（温度拟合后） |
| 时延 p50，1 问题 | 236–276 ms | **32.8 ms** | 7.8x |
| 时延 p50，10 问题批处理 | ~1,500 ms（串行） | **72.3 ms**（7.2 ms/q） | ~20x |
| 可用语言（>3x 随机） | 未公布 benchmark | **45 / 51** | — |
| 每百万 input token | $0.042（计量 API） | $0.00（自托管） | 100% 免费，可气隙 |
| 权重 | 闭源专有 API | 开源 safetensors，Apache 2.0 | — |

**typed-decisions 细分（400 case，2,000 决策）**

| 模型 | Accuracy | Soft acc | Brier | ECE | Score MAE |
|---|---|---|---|---|---|
| `laya-typed-decisions` | **0.766** | 0.471 | 0.062 | 0.213 | 0.242 |
| `laya` | 0.362 | 0.332 | 0.316 | 0.175 | 0.694 |
| `laya-multilingual` | 0.342 | 0.326 | 0.439 | 0.285 | 0.687 |
| *Jev 1.13.0（已发表）* | *0.727* | **0.580** | *0.148* | *0.144* | *0.391* |
| *teacher 自一致天花板* | *0.735* | | | | |
| *每题多数类* | *0.461* | | | | |
| *随机猜* | *0.318* | | | | |

**Laya 自己声明的局限（值得引用，项目方很诚实）**
- **高基数 choice 崩溃**：Banking77（77 标签）0.425 vs Jev 0.870。选项共享固定 head_max_len 预算（英文 192 token、多语 256），77 个选项只剩约 3–4 token/标签。Jev 开箱支持最多 255 选项。
- **zero-shot 近随机**：开箱 typed-decisions 0.362 / 0.342，**低于 0.461 多数类基线**，只比 0.318 随机稍好。**0.766 这个头条数字需要在该 benchmark 自己的 train split 上微调**。「把 Laya 当作可专业化的快速基座，不是 zero-shot decision oracle。」
- **soft 分布匹配输给 Jev**：argmax 赢了，但对 teacher 完整概率分布的 soft accuracy 是 0.471 vs 0.580。
- **`score` 是最弱的原语**：SST-5 ordinal 准确率 0.372。
- **开箱原始校准更差**：base checkpoint 原始 ECE 0.213 vs Jev 0.144；**0.081 是做了领域温度拟合之后**的结果。`laya-multilingual` **完全没有预拟合温度**，必须自己拟合。
- **必须刻意选 checkpoint**：英文 checkpoint 在英文外崩溃，多语 checkpoint 在英文上更弱。没有「就用这个」的单一答案。

**Laya 的多语言发现（最有价值的负面发现）**

MASSIVE 51 语言扫描：英文调优的 encoder **在拉丁字母之外不是优雅退化，而是静默且自信地失败**。

| 语言 | Accuracy | Mean confidence |
|---|---|---|
| 高棉语 | **0.000** | **0.952** |
| 亚美尼亚语 | 0.050（恰为随机） | 0.885 |
| 希伯来语 | 0.060 | 0.964 |
| 孟加拉语 | 0.080 | 0.945 |
| 印地语 | 0.100 | 0.941 |

> 全部 51 种语言中，英文 checkpoint 的平均置信度**从未低于 0.885**，无论实际准确率是 82% 还是 0%。**置信度门控在这里保护不了你**：选哪个 checkpoint 必须在 forward pass 之前决定。

**Laya 的独立性问题（关键批判点）**

Laya 自己的 README 明确写（我可引用原文）：

> "Every Laya figure is what `Router().predict(...)` actually returns — the checkpoint the router selects for that input, not a hand-picked best of three. **Jev figures are third-party published, never measured here (no TypeSafe API access)**, so sample sizes and prompts differ."

> "For reference, TypeSafe Jev has been independently measured at 236-276 ms p50 ([AbdelStark](https://github.com/AbdelStark/jev-benchmarks), [nibzard](https://github.com/nibzard/decision-model-benchmark))"

**结论**：Laya vs Jev 的对比是 **Convai 单方测量 Laya + 引用他人发表的 Jev 数字**，**不是受控 A/B**。mer.vin 也明确写：「Sample sizes and prompts differ between the two, so treat this as directional, not a controlled A/B.」**但 mer.vin 的标题和正文仍用了「Beating Jev」的框架。**

**关于「Laya 是开源版 Jev」这个说法的定性问题**
- mer.vin 的叙事框架：Mukkunnoth 2025 年 3 月就发布了原创工作 → 2026 年 9 月 TypeSafe 作为「全新突破」发布同一概念、藏在计量 API 后面 → 他「从头重建」并发布 Laya。
- 引用原文（mer.vin 转述 Mukkunnoth 的话）：「I worked on this literally one year back in March 2025 … Then a well-funded frontier lab called TypeSafe AI launched Jev. They proposed the exact same non-autoregressive decision concept as if it was a brand-new scientific breakthrough.」
- **但 Laya 的 README/HF 卡都没有自称为「Jev 的开源版本」**——它自称「Laya，一个开源的非自回归决策模型家族」。把它叫 "the open source version of JEV" 是**媒体报道的框架**（mer.vin 标题、hn.today 标题、ecosistemastartup 的西语报道、ZAKER 的中文报道），而不是项目方的自称。这本身构成一个「命名误导」案例。
- ⚠️ **未核实**：我的 WebSearch 未能找到 Mukkunnoth 或 Convai 官方页面直接说「Laya 是 Jev 的开源版」；该表述全部来自第三方媒体标题。

### 3.3 其他开源复现（本次用 gh api 一手核实）

| 仓库 | Stars | License | 基座 / 说明 | 创建 |
|---|---|---|---|---|
| `browser-use/jev-ultrafast` | **12,585** | MIT | Browser Use 官方出品；Jev 选 operation + DOM element | 2026-09-16 |
| `TheoLeeCJ/SemIf` | **2,523** | MIT | 原 OpenJev；冻结 Qwen3.5-4B 读 logits；homepage=openjev.com | 2026-09-16 |
| `TianyuCodings/NanoJev` | **1,519** | MIT | 0.6B 复刻，Qwen3-0.6B + decision heads；发布 HF 权重 + 数据集 | 2026-09-17 |
| `jaredpalmer/kev` | **1,161** | Apache-2.0 | 0.8B/4B/9B，Qwen3.5 base（LoRA adapter） | 2026-09-17 |
| `vinnylarouge/jevlike` | **1,097** | MIT | 从零训 option scorer | 2026-09-16 |
| `razorback16/openjev` | **220** | Apache-2.0 | DiffusionGemma + vLLM 兼容服务 | 2026-09-18 |
| `wkzyx/von` | **241** | Apache-2.0 | 自称「开源 System One 决策模型，sub-15ms，非自回归，本地 Jev 替代品」 | 2026-09-18 |
| `ekzhang/openjev-sglang` | **239** | — | Qwen3.6-35B-A3B + SGLang radix cache；声称「64 tasks in <1s」 | 2026-09-17 |
| `Heman10x-NGU/openJev-verdict-2.0` | **205** | NOASSERTION | 自称 151M 非自回归决策引擎，**在 LocalLLaMA/typed-decisions 上击败 Jev 和 Laya（77.10% acc, 0.0636 Brier, 0.0144 ECE）** | 2026-09-19 |
| `featherless-ai/simple-jev` | **404** | — | 「Turn any open model into a classifier/jev endpoint」 | 2026-09-18 |
| `mizorewww/laya-mlx` | **1,930** | Apache-2.0 | Laya 的 MLX 原生运行时，M3 Max 上 7–14ms | 2026-09-19 |
| `mizorewww/laya-coreml` | **453** | Apache-2.0 | Laya 的 Core ML/ANE 端口，M3 Max 上 ~5ms | 2026-09-19 |

**【本次核实】GitHub 全站搜索规模**
```
gh api "search/repositories?q=jev&per_page=1" --jq '.total_count'          → 7330
gh api "search/repositories?q=jev+created:>2026-09-01&per_page=1" --jq '.total_count' → 4126
gh api "search/repositories?q=typesafe+jev&per_page=1" --jq '.total_count' → 1505
```
> 注意：`q=jev` 会命中大量无关仓库（jEveAssets、Jeva、tinystruct 等）。

### 3.4 kev 的家族 benchmark（唯一公开自己 base model 与 Jev 并列对比的项目）【项目方自测】

来源：`gh api repos/jaredpalmer/kev/contents/README.md`

| 模型 | Base | Accuracy: Trained Sources | Accuracy: New Sources | Brier: New Sources |
|---|---|---|---|---|
| Kev-0.8B | Qwen3.5-0.8B-Base | 0.829 / 0.827 | 0.643 / 0.668 | 0.513 / 0.473 |
| Kev-4B | Qwen3.5-4B-Base | 0.877 / 0.870 | 0.794 / 0.832 | 0.316 / 0.266 |
| Kev-9B | Qwen3.5-9B-Base | 0.876 / 0.873 | **0.812 / 0.837** | **0.291 / 0.243** |
| **Jev** | Hosted | **0.845** / – | **0.857** / – | **0.211** / – |

（每格为 development / test；"Trained sources" = 训练数据集的 held-out 样本；"New sources" = 未训练过的数据集与策略规则类型）

**kev 自己的诚实声明（可引用）**：
> "Kev-9B trails Jev by about 4.5 points on the new-source development set. **We don't know which datasets Jev was trained on, so this isn't a controlled comparison of the two architectures.**"

> 注：在新数据源上 Jev 的 Brier（0.211）明显优于 Kev-9B（0.291/0.243），即 **Jev 的分布质量仍更好**；而 kev 在 accuracy 上接近或反超。这两件事需分开陈述。

### 3.5 NanoJev 的游戏 benchmark（对 Jev 不利的第三方数字）【项目方自测】

来源：`gh api repos/TianyuCodings/NanoJev/contents/README.md`

完整 **274-case test set**，相同 observation 接口、candidate actions 与 seeded epsilon-greedy controller：

| 模型 | Maze | Snake | ViZDoom Basic | Predict Position |
|---|---|---|---|---|
| **NanoJev** | 4/10 | **8/8** | **128/128** | **27/128** |
| Jev | 7/10 | 8/8 | **56/128** | 11/128 |
| Untuned Qwen3-0.6B | 2/10 | 0/8 | **56/128** | 11/128 |

- ViZDoom Basic：NanoJev **1.40s 内一枪击杀**；Jev 和 Untuned Qwen **各开 19 枪未击杀**。
- 50×50 Maze：NanoJev **225 次尝试**到达出口，Jev **2,738 次**，Untuned Qwen 4,726 次。
- **关键观察**：Jev 在 ViZDoom Basic 上的 56/128 **与未微调的 Qwen3-0.6B 完全相同**——即在该任务上 Jev 相对裸 base model 无增益。
- Test + OOD 合计 548 cases/model，每条轨迹都过独立 simulator replay。

> ⚠️ 这是**项目方自测**，且用自家 0.6B 模型对比一个通用 hosted 模型，任务选择偏向自己的训练分布。但「Jev ≈ untuned Qwen」这一行仍需在报告里呈现。

---

## 4. 生态目录站点核实

### 4.1 https://jevbest.com/zh/ —— bestjev

**【本次核实】页面上直接读到的统计口径**

```
标题：503 个 Jev AI 开源项目、SDK 与工具
分类（页面导航栏原文）：
  全部项目 503
  官方项目 6
  SDK 与客户端 43
  框架与集成 31
  Agent 工具 120
  浏览器与计算机操作 42
  应用 57
  游戏与模拟 53
  演示与试验场 46
  基准测试与研究 93
  其他列表 12
筛选维度：10 个分类、25 种语言
最近更新：2026 年 9 月 20 日
整理者：heyjunpenn
```
> 分类求和：6+43+31+120+42+57+53+46+93+12 = **503** ✅ 内部自洽。

**官方背书状态（页面原文，可直接引用）**：
> "bestjev 是一个**独立、由社区维护**的 Jev 开源项目目录。"
> "**bestjev 与 TypeSafe AI 无隶属关系，也未获得其官方背书。**"

**核验机制（页面原文）**：
> "我们会检查每个条目的公开依据，包括上游仓库、项目文档以及可以确认的 Jev 用法。**Star 数记录的是核验当天的快照，只供参考，不代表项目质量。**"

**提交流程**：需提供公开 GitHub 仓库地址 + 说明如何使用 Jev（附代码/文档/演示链接）→ 人工核验 → 收录。

**【关键发现】目录 Star 快照 vs GitHub 实时值的偏差**（我逐条对比）

| 仓库 | jevbest 显示（快照） | 本次 gh api 实时 | 偏差 |
|---|---|---|---|
| `browser-use/jev-ultrafast` | 9,291 | **12,585** | −3,294（低 26%） |
| `tamaratran/fast-jev-compaction` | 4,427 | **5,375** | −948（低 18%） |
| `TheoLeeCJ/SemIf` | 2,023 | **2,523** | −500（低 20%） |
| `TianyuCodings/NanoJev` | 1,074 | **1,519** | −445（低 29%） |
| `vinnylarouge/jevlike` | 1,008 | **1,097** | −89 |
| `different-ai/openwork` | 23,654 | **23,678** | −24 |
| `vercel/eve` | 5,274 | **5,285** | −11 |
| `typesafe-ai/skills` | **765** | **1,259** | **−494（低 39%）** |
| `Anil-matcha/awesome-jev-by-typesafe` | 641 | **719** | −78 |
| `awlevin/typesafe-computer-use` | 537 | **657** | −120（低 18%） |
| `devagrawal09/jev-review` | 366 | **420** | −54 |

> 所有快照都是**偏低的旧数据**，符合「核验当天快照」的自述。**引用该目录的 star 数会系统性低估**。目录自己已声明不代表质量。

**【关键发现】「官方项目 6」这一分类的存在**
- 该分类包含 `typesafe-ai/skills`（【本次核实】真实存在，MIT，**1,259 stars**，2026-08-24 创建，描述「Agent skills for building with TypeSafe's System One API」，homepage=typesafe.ai）——这是**真正的 TypeSafe 官方仓库**。
- ⚠️ **但目录本身非官方**：它有一个内部「官方项目」标签，是分类标签，不等于目录获得官方背书。这两个概念易被混淆，报告里需明确区分。

**目录背后的仓库**
- `heyjunpenn/awesome-jev` — 【本次核实】**38 stars**，描述 "A verified, community-maintained catalog of **503** open-source projects built with Jev."
- ⚠️ **一个 38 stars 的仓库号称核验了 503 个仓库**——这个不对称本身值得在报告里指出。数据库来源标注为「可机读目录数据」。

### 4.2 https://madewithjev.com/github-repos —— Made with Jev

**【本次核实】页面上直接读到的统计口径**

```
页面 <title>: "Jev GitHub repos: 195 open-source projects — Made with Jev"
页面内标题计数（tab）：
  All 386
  Jev Engineering 15
  GitHub 195
  Skills 11
  X posts 136
  YouTube 18
  Sites 9
  Resources 91
```

> ⚠️ **内部不一致**：分类求和 15+195+11+136+18+9+91 = **475**，但 "All" 标 **386**。口径未说明。（可能 "All" 是去重后的提交/build 数，但页面未解释。）

> ⚠️ **与任务简报中的「143 个仓库」不符**：我 2026-09-21 实测是 **195**。143 应为更早的快照。报告中若引用「143」需注明时点。

**运营者与背书状态（从页面 JSON-LD 结构化数据读到）**

```json
{"@type":"Person","@id":"https://madewithjev.com/#publisher",
 "name":"Jon Kraayenjon",
 "sameAs":["https://x.com/kraayenjon","https://www.threads.com/@kraayenjon"]}
```
页脚原文：**"Made with Jev — The #1 directory of projects built with Jev. Not affiliated with TypeSafe AI."**

- 页面有 **"Advertise"** 入口、**"Submit a build"** 入口、**"Buy me a coffee"** 链接 → 该站有商业化意图，非纯公益目录。
- 站点还挂了一个名为 **"AI Slop Detector"** 的免费工具（与 Jev 目录无直接关系）。
- ⚠️ 页面描述里说「Each entry links to its source and **shows the cost and speed its author reported**」→ **明确是"作者自报"的数字，不是目录核验的数字**。这一点对报告很重要。

### 4.3 awesome 列表全景（本次用 gh api 一手核实）

**搜索 `awesome-jev in:name` 找到的列表（按 stars）**

| 仓库 | Stars | 自报规模 / 备注 |
|---|---|---|
| `Anil-matcha/awesome-jev-by-typesafe` | **719** | MIT；README 明写「**This is an independent community collection. It is not an official TypeSafe AI repository.**」 |
| `yibie/awesome-jev` | **673** | **无 license**；脚本生成的聚合 README |
| `v-modal/awesome-jev-tools` | **566** | **无 license**；与 yibie 版本内容高度重叠 |
| `cobanov/awesome-jev` | **277** | CC0-1.0；自报「community catalog to **155**」 |
| `logicrw/awesome-jev-projects` | **240** | MIT；badge「Curated Projects **358+**」 |
| `fatwang2/awesome-jev` | **181** | — |
| `AnotiaWang/awesome-jev` | **129** | — |
| `OmniJev/awesome-jev-gallery` | **114** | 聚焦论文与开源复现 |
| `valentynkit/awesome-jev-typesafe` | **112** | — |
| `hellogumbo/awesome-jev` | **104** | — |
| `kraayenjon/awesome-jev` | **70** | 与 madewithjev.com 同为 kraayenjon |
| `AppitStudio/awesome-jev` | **65** | — |
| `heyjunpenn/awesome-jev` | **38** | jevbest.com 的数据源，自称 503 项目 |
| `yzfly/awesome-jev-zh` | **35** | **中文精选**，含中文上手指南 |
| `walidboulanouar/awesome-jev-use-cases` | **22** | 自报「74 demos ranked by likes, 150+ GitHub repos」；**sponsored by AY Automate** |
| `anandi1989/awesome-jev-usecases` | **13** | — |
| `aliaihub/awesome-jev-usecases` | **12** | — |
| `wh000wh000/awesome-jev-live` | **5** | 自称「每 2 小时用 20 种语言重建」 |
| 另有 `Promethe-us/`、`BeatAPI/`、`Frank-ZY-Dou/`、`ckaraca/`、`MrJev/`、`whyashthakker/`、`daftAI2026/` | 5–15 | 均 5–15 stars 区间 |
| `AbdelStark/awesome-typesafe` | **401** | MIT；覆盖 TypeSafe 全景（不只 Jev） |

> **至少 20+ 个 awesome-jev 列表**，多数创建于 2026-09-16~09-20 的 5 天内，描述高度雷同。

**各列表的免责声明原文（可直接引用，说明彼此都声明非官方）**

- `yibie/awesome-jev` + `v-modal/awesome-jev-tools`（同一模板）：
  > "**A listing is not an endorsement.** This project applies *inclusion* rules only — public, citable, genuinely uses Jev for a typed decision, one-sentence summary. It does **not** review code quality, security, maturity, or whether a project runs at all."
  > "We do not verify that a project compiles, that its tests pass, that its published numbers reproduce, or that its license permits your use."
  > 自报局限表中有一条：「Is there a license? | **A few entries have none, which limits reuse and redistribution.**」
- `cobanov/awesome-jev`：
  > "These projects explore Jev-like interfaces or open implementations. They are independent efforts, **not official TypeSafe releases or verified reproductions of its proprietary architecture, RLCD training, or calibration.**"
  > "**Inclusion means the evidence is inspectable, not that benchmarks were independently rerun.**"
  > "**Input boundary:** the hosted Jev model is text-only. Browser, audio, image, and robotics projects supply extracted text or structured observations, or use separate perception models."
- `AbdelStark/awesome-typesafe`：
  > "**Independent community project.** This repository is not affiliated with or endorsed by TypeSafe AI. Community entries are labeled by section; **inclusion is not a claim that TypeSafe has reviewed or approved them.**"
  > "*Last reviewed: 2026-09-17.*"

### 4.4 官方渠道核实【本次核实】

| 渠道 | 事实 | 来源 |
|---|---|---|
| Vercel AI Gateway | Jev 于 2026-09-16 上线；模型 ID `typesafe-ai/jev`；经 AI SDK 7 的实验性 `evaluate` API；AI SDK **7.0.105 起**支持 | https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway |
| Vercel 采用数据 | 「**AI Gateway 历史上采用最快的模型**」；**24 小时内近 13% 的付费团队**在用；是 **GPT-5.6 家族的 2 倍**、**Fable 5.1 份额的 6 倍以上**；**18 小时达到 10%**；其他近期发布 40 小时后仍低于 7% | https://vercel.com/blog/ai-gateway-jev-model-launch |
| Cloudflare Workers AI | 模型 ID `typesafe/jev`，上下文 32,000 token | claudemax 中文长文引用 Cloudflare 文档 |
| Pydantic AI | `pydantic-ai-slim[typesafe]`；`TypeSafeModel('jev-latest')`；`output_type` 的每个字段即一个问题 | https://pydantic.dev/docs/ai/models/typesafe/ |
| LangChain | `langchain-typesafe` 包，暴露 `TypeSafeClassifier`；另有实验性 `ModelRouterMiddleware`、`AutoModeMiddleware`（Jev 检查 bash 工具调用，执行前阻断） | https://www.langchain.com/blog/building-a-harness-with-jev |
| Venice | 2026-09-18 晚把 Jev 放上 beta Decisions API，`POST /api/v1/decisions`，model `jev-latest`，按 TypeSafe 的 $0.042 计费；Venice 称不留 state 或答案副本 | jevainews.com |
| 官方 SDK | Python / JavaScript | Anil-matcha 列表 badge 链接 |
| 官方 skills 仓库 | `typesafe-ai/skills`，MIT，**1,259 stars**（本次核实） | gh api |

> ⚠️ **注意**：`typesafe-ai/skills` 创建于 **2026-08-24**，即出隐（09-15）之前就已存在，说明官方在发布前就在铺垫生态。

---

## 5. 批判与风险

### 5.1 供应商锁定与架构依赖

**可引用的事实**

1. **无权重、无论文、无自托管**：官方确认闭源；cndba 中文分析明确「无公开模型权重、无训练代码、无完整架构论文；仅提供官方云端 API 服务（Vercel/Cloudflare 托管）；**不支持本地私有化部署，国内无官方开放接口**」。
   来源：https://www.cndba.cn/article/17105
2. **early access**：还在候补名单制。Capital & Compute 指出「early access 意味着速率限制随时变动，企业条款仍在成形，用今天的限制做容量规划为时过早」。
3. **价格可持续性未证明**：官方发布博客只说「无法证明价格未被补贴」，并**预计价格会下跌而非上涨**；onboarding 页称能盈利（单方面声明）。→ 价格是 early-access 贴纸价，不是长期合同价。
4. **第三方测试者拿不到 API 直接对比**：Laya 作者明确写「**no TypeSafe API access**」。→ 所有「开源 vs Jev」的对比都是拿别人发表的 Jev 数字凑出来的，没有一次受控 A/B。
5. **迁移成本的不对称**：迁进去容易（只是改一个 model 名字，Pydantic AI 甚至能一行切换），**迁出来难**，因为你的代码开始以「有校准概率可用」为前提写阈值和自动分支。这是锁定的真正形态——不是协议锁定，是**架构假设锁定**。
6. **Arize 特别指出的架构性代价**：Jev 不生成解释。Arize 原话：「The biggest loss is the explanation. TypeSafe's docs say plainly that System One models don't generate explanations of their reasoning, and NearHere's test noted the same thing: a category and probabilities came back, nothing else.」→ 要拿到「为什么错」的方向性信号，必须另跑 LLM judge，这本身是一次重新架构。
   来源：https://arize.com/blog/typesafe-jev-llm-judge/

### 5.2 数据出境与合规（中国大陆场景）

**claudemax.shop 的中文落地指南原文（可引用）**：
> "**数据合规照旧。** 把业务数据交给境外模型属于向境外提供数据，涉及个人信息的要先评估。"
> "**当它是早期访问。** 服务稳定性与定价都可能变化，架构、权重与参数量未公开，也没有自托管方案。"

**juejin.cn 长文的原文（可引用）**：
> "1. **闭源，纯云端。** 没有可以下载到自己机器上跑的模型文件、没有论文、不能本地部署，调用走 early access 排队。
> 2. **中文没验过。** 公开示例全是英文，校准表现在中文语料上没有独立数据。
> 3. **数据出境。** 审核类业务把用户内容发到境外第三方，多数企业场景过不了合规。"

**juejin 文章总结的方案对照表（可直接引用为报告配图/表格）**

| 方案 | 检查者与选手不同物种 | 检查者无利益冲突 | 最后谁拍板 | 能装自己机器 | 综合 |
|---|---|---|---|---|---|
| 大模型自查输出 | ✗ | ✗ | 视实现 | 视模型 | 不推荐 |
| 另一个大模型当裁判 | △ 同物种 | ✓ | 视实现 | 视模型 | 谨慎 |
| 专用判断小模型 | ✓ | ✓ | ✓ | ✓ | **推荐** |
| 格式卡口 | ✓ 硬保证 | ✓ | ✓ | ✓ | **推荐（格式层）** |
| **Jev 类云端判断模型** | ✓ | ✓ | ✓ | **✗** | **理念可学，落地问合规** |

**技术层面对数据出境的部分缓解（本次核实）**
- Vercel AI Gateway 示例中可设 `providerOptions: { gateway: { zeroDataRetention: true } }`；Vercel changelog 提到 Jev 支持 **Zero Data Retention 与 No Training**，**按请求启用**；调用会出现在日志与自定义报表里，计入预算。
- Venice 声称不留 state 或答案副本（Venice 单方面声明，我未独立验证）。
- ⚠️ **未核实**：TypeSafe 官方是否有 ZDR/No-Training 的默认设置或合同级承诺；是否有面向中国大陆的合规方案（如境内节点、数据本地化）。所有材料均未见。
- 独立校准测试使用了 `zeroDataRetention: true`（scienthoon 仓库自述），说明该参数在实际调用中可用。

### 5.3 概率校准是否可信（本任务最关键的一条）

**支持校准的第三方证据**
- Arize 的 18,514 封垃圾邮件测试：Jev 零样本 98.3% vs TF-IDF（~14,800 标注样本训练）98.4%，统计上无显著差异。Arize 评价：「**Matching a purpose-trained classifier with no training data at all is the strongest evidence published so far that the calibration claim is doing real work, and it is worth more than any of the cost multiples.**」（Arize 同时声明尚未跑自己的完整 benchmark 套件）
- 同一测试的校准曲线：Jev 打分 <0.1 的邮件中，0.1% 是垃圾邮件；≥0.9 的邮件中 **99.9%** 是垃圾邮件；**0.5–0.6 区间只有 38%**。把打分为 0.3–0.7 的 **4.6%** 邮件转人工，其余保持 **99.5%** 准确率。
- Arize 引用的 2025 年 JudgeBench 研究（14 个模型）：LLM judge 把预测堆在 90–100% 置信度区间，而实际准确率远低于此 —— 这正说明「可用的概率」为什么有价值。

**反对/限制校准可信度的第三方证据**
- scienthoon 独立校准测试（见 §2.5）：**自造无污染任务上 ECE 0.107，是噪声底的 4.4 倍**；**不可知任务上 Choice/Score 过度自信（T 3.29/3.40）**，平均给选中档位 0.74；**方向随类型翻转（boolean T 0.66）**；**概率量化到 0.01，OpenBookQA 2,000 个概率里 1,051 个恰好为 0，有力给正确答案 0.00**；**`confidence` 字段在这些集合上从未优于 max probability，合成集上 ECE 0.18**。→ 结论：「**当作单调分数而非概率，本地自行校准**」。
- 4esv/jev-eval：ECE 在三个任务上一个赢两个输给 Terra（0.11/0.08、0.20/0.30、0.04/0.02）。
- 硅星人中文实测：**阈值附近的抖动**（2.00 vs 1.99；0.75 vs 0.71–0.72），15 次重复有 3 题通过/失分交替。
- Capital & Compute：**薄 state 时 57.8% 置信度 <0.5**，94.4% <0.8；加厚 state 后平均置信度 +23%。→ 置信度是 **state 体量的函数**，不是模型的固有属性。
- Laya 项目方给出的对照：Jev 开箱 ECE **0.144** vs Laya base 0.213（Laya 拟合后 0.081）。即 Jev 原始校准优于 Laya base，但不如拟合后的 Laya。
- **架构级原因（Archer 逆向分析的核心发现，可引用）**：官方 Python adapter 的 `confidence_metrics.py`（revision fb52b103）里，Choice 的 confidence 是 **`c = (p_max − 1/K) / (1 − 1/K)`**，即「领先答案比均匀分布高出多少」。**这是普通算术，不是另一个学出来的「答案正确」估计。** Archer 原话：「It measures how far the leading answer stands above a uniform distribution. **It is not another learned estimate that the answer is correct.**」Score 用另一个公式。
  来源：https://archerhume.com/posts/jevs-architecture-unmasked
  
> **给报告的判断**：官方从未公布 RLCD 的配方，也未发表论文或同行评审 benchmark。**「概率经过训练校准」目前只有官方宣称 + 部分第三方在特定任务上的正面结果**；**要落地必须在自己的数据上画校准曲线**（这一条多家独立来源一致）。

### 5.4 「是否只是把 LLM 当分类器的包装」

这是社区最常见的质疑。以下是可引用的正反两面。

**支持「不只是包装」的证据（Archer 的黑盒逆向，方法学扎实）**
来源：https://archerhume.com/posts/jevs-architecture-unmasked （基于 2026-09-17 对 `jev-1.13.0` 的调查；1,029 条 instrumented probe + 6,800 条 benchmark 记录）

1. **`output_tokens` 是纯计费字段，不反映生成**：对 yes/no 问题，计数恰好 = 4 个共享 token + 15 × 答案数 + 每个问题标识符长度。而官方文档说标识符「不发送给底层模型、不参与推理」。**一个随模型从未见过的文本变化的计数，是推理之后从序列化响应算出来的。** 答案为 0.0 和 0.01 花费相同，尽管每个数字本来各算一个 token。
2. **tokenizer 不属于任何公开 tokenizer**：测了 **192 个公开 tokenizer、415 次探测**，全部不匹配。最接近的是 Qwen（415 个里 348 个一致）。→ 排除「未改动公开 tokenizer」，但不排除公开 base model。
3. **延迟与 output token 数无关**：200 选项的问题（1,911 output token）和 2 选项的一样快，服务端时间只随 input 长度增长。255 选项返回报 2,714 output token。
4. **问题之间行为隔离**：把一个「密文 ZEBRA-7741」声明放到兄弟问题里，探针问「另一个问题提到什么代码」→ 报告概率 **0.00**；把同一声明**移到 state 里** → **0.90–0.92**。（每组 5 次重复）
5. **选项之间会相互作用**（对「只是独立打分再 softmax」的证伪）：在 4 个选项（bank/provider/customer/unknown）后追加一个不相关的第 5 选项 `weather: Bad weather caused it`。若每个选项有固定 logit 且温度不变，共享分母会抵消，**两个现有选项的几率不可能改变**。实测：**10 个随机化 block 全部下降**，log-odds 从 **+0.38 降到 +0.11**，平均变化 **−0.28**，配对 t 区间约 **[−0.36, −0.19]**。
6. **选项边界不可被文本伪造**：注入假选项从未顶掉真选项。
7. **上下文限制与 KV 共享高度一致**：单分支（state + 一个问题）上限约 32,768 token，整请求约 65,536。一个 23k token 的 state 加 5,000 个问题仍在限内——**如果每个问题处理自己的 state 副本，该请求会超过 1 亿 token**。
8. **问题数量扩展性**：约 100 个问题以内服务端时间几乎不变，之后稳步上升；token 对 token，**问题文本的成本约为 state 的两倍**。图 2 数据：1 个问题中位 86.5ms，1,500 个问题中位 610ms / 最快 408ms。
9. **MMLU 1,200 项 10-bin ECE = 0.0313**（预测高度集中在确定端：990 项落在 0.9–1.0 箱）。
10. **新生成数学题上的置信度跟随难度**：三位数乘法 86.7% 准确 / 平均 top 概率 0.83；两步文字题 32% / 0.30；模指数 56% / 0.35（这个例外是**欠自信**）。
11. **选项顺序敏感性（对部署是坏消息）**：颠倒选项顺序把技术支持分类的概率从约 **0.84–0.89 挪到 0.93–0.96**。对 0.9 附近的阈值，这意味着**标签和证据完全相同但动作会变**。
12. **参考卡位置实验**：把 reference card 放在选项**最后**时 16/16 全对（平均正确概率约 0.88）；放在**第一** 12/16；放在**中间** 11/16；把卡片移到 state 里 **48/48**。→ 支持「决定能读到完整选项列表」，但同时也暴露**显著的位置敏感**。

**Archer 的核心判断（可引用）**
> "Its usefulness comes from matching the computational graph to the job. A decision service needs to read evidence, compare permitted outcomes, and expose uncertainty. **A transformer can do that without turning every decision into a sentence first.**"

> "**None of this requires diffusion. Parallel classification has existed for decades.** The interesting combination is a broadly capable transformer, shared contextual computation, a typed output interface, and training that rewards useful uncertainty."

**Archer 明确区分「读概率」与「生成描述概率的文本」**
> "The important distinction is between **reading out probabilities** and **generating text that describes probabilities**. A generated '91%' is a token sequence. A classifier's 0.91 is an entry in its predictive distribution. **Either can be miscalibrated. Neither becomes trustworthy solely because of its format.**"

**Archer 未确定的部分（诚实声明，报告须保留）**
- 无法从外部区分 causal decoder 与 bidirectional encoder；他**假设**是 causal decoder（理由：MMLU-Pro 84.6% 需要前沿规模预训练，该规模全是 causal decoder）。
- **稀疏 MoE 是最不确定的假设**，纯属推断。
- 无法确定是「末位 slot head」还是「pointer-style scorer」。

**「只是包装」论的旁证（对报告同样重要）**
- 4esv/jev-eval：**「零幻觉」= 每个答案都是列出的选项。这对全部 1,800 次 Jev 调用成立；但对全部 1,800 次 Terra 调用在严格 JSON schema 下也成立。** 即这个性质**不是 Jev 独有**，用 schema 约束的 LLM 同样具备。
- Arize 直接说：「TypeSafe also claims Jev 'can't hallucinate', but that **really feels like an over-reach**. Jev can't return an answer outside the schema you gave it. Within that schema, it could still be giving the wrong answer.」
- juejin.cn 的「官方说法 vs 实际含义」对照表（可整表引用）：

| 官方说法 | 实际含义 |
|---|---|
| "不会幻觉" | 输出**必然**落在你预设的格式里，格式错误为零。**但判断错误照旧会发生** |
| 快 40–200 倍，成本最多降两个数量级 | **TypeSafe 自测，无第三方复现**；官方博客注明"这些数字处于真实收益的高端" |
| 端到端 70–500 毫秒 | 官方值，**只对"判别类"任务成立** |
| 准确率 | 据其评测图估算（**作者自行估算，非官方口径**），Jev 平均准确率与一款廉价小模型基本持平，比最强模型低几个百分点 |

- juejin 的另一条重要指控（可引用）：
  > "TypeSafe 自己的评测文档写得很直白，那套业务评测的『标准答案』**没有人工标注**，直接由 GPT-6 Astra 与 Claude Fable 5.1 的平均回答生成。连这套评测的裁判本身，都是模型给模型当。**讽刺的是，Jev 自己的准确率数字，恰恰也是用这套『模型当裁判』的评测量出来的。**"

### 5.5 MIT 复现项目重新分发 Qwen 权重的许可证合规问题

**⚠️ 我的核实结论：这一风险真实存在但被夸大，而且我找到的问题方向与通常说法不同。**

**实测事实**

| 事实 | 值 | 来源 |
|---|---|---|
| Qwen3.5-4B 的许可证 | **Apache-2.0**（`cardData.license = "apache-2.0"`，`license_link` 指向 HF 上的 LICENSE） | 【本次核实】HF API `Qwen/Qwen3.5-4B` |
| Qwen3.5-4B 下载量 | **6,819,426**（HF downloads） | 【本次核实】HF API |
| NanoJev 基座 | `Qwen/Qwen3-0.6B` | 【本次核实】HF tag `base_model:Qwen/Qwen3-0.6B` |
| NanoJev HF 卡片 | **`cardData` 里没有任何 `license` 字段**；GitHub 仓库是 MIT | 【本次核实】HF API `C-Tianyu/NanoJev` |
| kev-4b HF 卡片 | `license: apache-2.0`，`library_name: peft`，`base_model: Qwen/Qwen3.5-4B-Base`，`base_model_relation: adapter` | 【本次核实】HF API |
| kev GitHub 仓库 | **Apache-2.0**，README 明写「All three are built on Qwen3.5 bases」 | 【本次核实】gh api |
| SemIf | **MIT**；但它是**从 HF 下载冻结的 Qwen 权重来读 logits，不重新分发权重** | 仓库 README：「Run the owned examples: `semif-score --mode direct --model Qwen/Qwen3.5-4B --revision 851bf6e8...`」+ 要求设 `HF_HOME` |
| Laya | Apache-2.0（HF 与 GitHub 一致，`license:apache-2.0`），基座是 **ModernBERT-large / mmBERT-base**（不是 Qwen） | 【本次核实】HF API |

**分析（供报告使用）**

1. **「MIT 项目重新分发 Qwen 权重」这个描述不准确。** 我核实到的权重重分发项目（kev、NanoJev）的细节是：
   - **kev**：GitHub Apache-2.0 + HF Apache-2.0，且发布形式是 **LoRA adapter**（`library_name: peft`、`base_model_relation: adapter`），不是权重合并体。**Apache-2.0 到 Apache-2.0，无冲突。** README 也明确了 base。
   - **NanoJev**：GitHub **MIT**，HF 权重仓库**根本没声明 license**。它基于 Qwen3-0.6B（Apache-2.0）。**这里的实际风险不是「MIT 覆盖了 Qwen」，而是「交付物完全缺少许可证声明」**——这比「许可证冲突」更麻烦：下游用户没有任何授权依据，Apache-2.0 第 4 条要求的 NOTICE/变更声明也无处可查。
   
2. **纯 MIT 项目（SemIf、jevlike）反而没有这个问题**，因为它们**只下载不重分发**权重。SemIf 甚至在随机种子上固定了 `--revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` 以保证可复现。

3. **如果真有 MIT 项目分发合并后的 Qwen 权重**，那才是问题：Apache-2.0 第 4 条要求保留版权/专利/商标声明与 NOTICE、并标注修改过的文件；MIT 缺少这些机制，且 Apache-2.0 的**专利授权**在被以 MIT 再许可时会丢失。本报告应区分这两种情况，不要笼统说「MIT 项目分发 Qwen 权重有问题」。

4. **仓库层面普遍存在的许可证缺口（我用 gh api 实测）**——这是更普遍、更可核实的问题：

| 仓库 | License |
|---|---|
| `ekzhang/openjev-sglang` | **null（无）** |
| `featherless-ai/simple-jev` | **null（无）** |
| `yibie/awesome-jev` | **null（无）** |
| `v-modal/awesome-jev-tools` | **null（无）** |
| `Heman10x-NGU/openJev-verdict-2.0` | **NOASSERTION**（GitHub 无法识别） |
| `reticlehq/reticle` | **NOASSERTION** |
| `realZachi/pg-jev` | **NOASSERTION** |
| `4esv/jev-eval` | **null（无）** |
| `C-Tianyu/NanoJev`（HF 卡片） | **无 license 字段** |
| `Sac-Y/Jev-cu` | null；`rmalde/minecraft-agent` null；`fhshaik/typesafe-mario` null；`dabit3/jev-experiments` null |

   `v-modal/awesome-jev-tools` 自己也在局限表里承认：「A few entries have none, which limits reuse and redistribution.」

5. **商标/命名合规**：SemIf 的 README 有一段值得引用的声明：
   > "**Independent research project.** SemIf was formerly called OpenJev. It is not affiliated with or endorsed by TypeSafe. **Jev, TypeSafe, and other names and marks are the property of their respective owners. No infringement is intended.**"
   
   对比之下，`wkzyx/von` 自述「The open-source System One decision model…**local drop-in alternative to TypeSafe Jev**」，`Heman10x-NGU/openJev-verdict-2.0` 自述「**beating TypeSafe Jev & Laya**」，`he-jev/laya`（0 stars）描述直接写「**open source jev by laya**」——这些用法风险更高。

### 5.6 「把复现项目直接叫 JEV 是否误导」

**支持「是误导」的证据**

1. **apidog 的明确结论**（可直接引用）：
   > "So 'run Jev locally' **can't mean Jev**. It means a cluster of days-old community projects, led by OpenJev, that reproduce the idea with open models."
   > "**None of them reproduce RLCD. That's the honest headline.**"
   > "Every row is a frozen or self-trained model reading logits. That gets you Jev's shape: typed answers, a probability per option, one forward pass. **It doesn't get you Jev's central claim, that RLCD makes those probabilities honest.**"
2. **项目方自己都在否认**（这是最有说服力的证据）：
   - SemIf：「This project reproduces that **interface pattern** with open models; **it does not reproduce Jev's undisclosed model or training.**」
   - jevlike：「TypeSafe has not published its design. This repository is an **independent starter model with the same input and output shape**.」+「**did not show equal quality with Jev or reproduce TypeSafe's private training method**」
   - SemIf 仓库描述：「Semantic ifs from open models, on a 3090 at home. **Independent; not affiliated with Jev or TypeSafe.**」
   - mini-jev：自述「**a correspondence of terms, not a reproduction of their model**」
   - cobanov 列表：「**not official TypeSafe releases or verified reproductions of its proprietary architecture, RLCD training, or calibration**」
3. **命名混乱的具体案例**：
   - **OpenJev → SemIf 改名**：apidog 文章仍全篇称 "OpenJev"，但该仓库已改名 SemIf。→ **一手资料本身就已经过时**，二手报道会跟着错。
   - **`openjev` 这个名字至少被三个不同仓库用**：`TheoLeeCJ/SemIf`（原 OpenJev，2,523 stars）、`razorback16/openjev`（220 stars，DiffusionGemma）、`zhihz/openjev`（双语概率问题）。还有 `ekzhang/openjev-sglang`（239 stars）。另有 `Heman10x-NGU/openJev-verdict-2.0`。→ **「OpenJev」不是一个项目，是一堆同名项目。**
   - **Laya 被媒体叫做「the open source version of Jev」**，但 Laya 自己的 README/HF 卡从未这样自称，且其作者的原工作是 **2025-03 就发布的另立研究**（SalesRLAgent）。把它框成「Jev 的开源版」在时间线上是反的。
   - **`leisc/laya-jev-ultrafast`、`he-jev/laya`、`KonghaYao/laya-jev`** 等 0-star 仓库直接叫「laya-jev」。
4. **同名污染**：`q=jev` 的 GitHub 搜索命中 7,330 个仓库，其中包含 `jevajs/Jeva`（JavaScript 游戏框架，222 stars）、`GoldenGnu/jeveassets`（EVE Online 工具，194 stars）、`killop/anything_about_game`（4,113 stars）等完全无关项目。

**支持「不算误导，因为声明到位」的证据**
- 我读到的**每一个**主要复现项目 README 都在显著位置声明了「非官方 / 不复现训练方法 / 独立」。SemIf 甚至声明了商标归属。**从项目方看，命名伦理基本合格；问题主要出在媒体报道与目录网站的归类上。**

---

## 6. 真实落地场景与可核验数字

### 6.1 浏览器自动化

**`browser-use/jev-ultrafast`**（Browser Use 官方出品，MIT，**12,585 stars**，2026-09-16 创建）
来源：`gh api repos/browser-use/jev-ultrafast/contents/docs/performance.md`

- 演示任务：Zürich → London 的 Google Flights 单程票搜索，**7.073 秒**（1x 速度，单条自然语言目标，含文字生成与加载等待）。
- **配对对比**（6 次交替运行，同一任务、同一 Chrome profile、同一目标、独立结果校验器、1120×780 视口、`jev-1.13.0`、`inception/mercury-2.5`、关闭 text reasoning、有 action/request 预算、两端都排除初始导航）：

| 配对 | 原始 runtime | 优化后 runtime | 校验 |
|---|---|---|---|
| 1 | 11.214 s | 6.964 s | 双双通过 |
| 2 | 8.984 s | 7.913 s | 双双通过 |
| 3 | 9.450 s | 7.092 s | 双双通过 |
| **中位** | **9.450 s** | **7.092 s** | **3/3 each** |

- 中位任务时间 **降低 25.0%**；中位 TypeSafe 请求数 **22 → 17**；中位浏览器协议调用数 **1,092 → 101**。
- 项目方自注：「**Three pairs are too few for a strong statistical claim (two-sided sign-test p = 0.25).**」
- 录制运行：**17 次 Jev 请求**、10 次交互 + 1 次显式 WAIT、2 次 helper 调用。**Jev 中位延迟 178 ms**。搜索在 **5.217 s** 执行，最终校验完成 **7.073 s**。
- Token：**90,558 TypeSafe input tokens**，6,325 output tokens，跨全部请求。
- 成本：OpenRouter 对两次文字调用报 **$0.00006272**（只是 text-helper 的账，不是总任务成本；TypeSafe 响应含 token 数但无账单金额）。
- 文字生成实测：**Zurich 581 ms**、**London 346 ms**。
- 其他抽查：Wikipedia 打开 Gödel 不完备性定理文章 **2.798 s**；本地酒店 fixture（搜 Lisbon、Design、Free cancellation、打开 Casa Flora）**1.896 s**。
- **项目方声明的局限**（可引用）：「This DOM reader supports common HTML and ARIA controls; it does not implement the full accessible-name algorithm or traverse shadow roots/frames… **Canvas, uploads, new tabs, nested scrolling, and arbitrary keyboard widgets remain unsupported. A valid operation can still be wrong, and DONE is never independent evidence of success.**」

**`awlevin/typesafe-computer-use`**（MIT，**657 stars**，macOS）
来源：`gh api repos/awlevin/typesafe-computer-use/contents/README.md`

| 指标 | typesafe (jev) | Claude Opus 5, 裸截图 | 倍数 |
|---|---|---|---|
| input token | 4,882 | 4,785 | 相同 |
| 每次决策成本 | **$0.0002** | $0.032 | **155x 更便宜** |
| 每次决策成本（含历史的真实循环） | $0.0002 | $0.035–0.08 | 170x–390x |
| 每 12 步任务成本 | $0.003 | $0.40–0.90 | 130x–300x |
| 模型延迟 | **0.13–0.38 s** | 5.2 s | 14x–40x |
| 端到端单步（含截图与 OCR） | 约 **1.5 s** | 约 5.5 s | 3.7x |

- 项目方自曝的诚实局限：「The honest caveat: the big model read the event dates off the pixels and compared them…」（Claude 从像素读日期，Jev 不能看图）
- 机制：确定性读屏 + 小分类器选下一步动作，只在需要自由文本时调写作模型。**从不把截图发给大模型。**

**`droidrun/mobile-jev`**（MIT，284 stars，移动端）；`jkudish/jev-browser`（MIT，194 stars）；`Sac-Y/Jev-cu`（493 stars，**无 license**）；`juancristobalgd1/jevremote`（Playwright + Jev 可复现文本优先浏览器自动化实验）。

### 6.2 E2E 测试 / 测试循环

- **`jarbon.medium.com`（Jason Arbon）：「I Put Jev in a Playwright Browser Testing Loop. It's fast, but…」**（2026-09-20）—— 标题本身即结论。
  ⚠️ **未核实**：该 URL 抓取被拒（解析到内网地址 10.36.28.67），**我未能读到正文**。报告若引用需另行获取。
- **`juancristobalgd1/jevRemote`**：Playwright（Chromium）+ Jev 的可复现浏览器自动化实验，CLI 参数 `TARGET_URL` / `GOAL` / `MAX_STEPS` / `HEADLESS`，含 TypeScript 类型检查脚本。⚠️ 无具体性能数字。
- ⚠️ **未找到**有分量的、带数字的「Jev 做 E2E 测试」独立案例。这一格在报告里应标注「信息不足」。

### 6.3 Code review 门禁 / coding agent

**`gemanor/jev-code-review-benchmark`**（MIT，**4 stars**）—— 完整数字见 §2.1
- 4 条规则 × 24 个程序族 × 5 版本 × 3 轮 = **1,080 次主研究调用**
- 1,000 次审查外推：**$0.043（Jev）/ $1.943（Flash）/ $11.780（Fable）**
- 中位响应：**0.75 s / 3.59 s / 4.31 s**
- 正确率：**98.0% / 100% / 100%**；Jev 的 95% 区间 **[94.7%, 100%]**
- 规则遵守分：99.5% / 100% / 100%
- 三轮间决策改变率：**0.83% / 0% / 0%**
- 项目方明确局限：「these are small constructed examples with explicit rules… do not measure production code review, human readability, open-ended bug discovery, or other task types.」
- 项目方还做了「Jev 打头 + 部分 case 送大模型」的**成本外推（明确声明未测准确率）**。

**`devagrawal09/jev-review`**（MIT，420 stars）—— 分阶段代码审查工作流 + 本地 dashboard。
**`thruwire/foreman`**（MIT，441 stars）—— 「软件工厂 foreman」，坐在 Codex worker 之上，让 Jev 独立判断实现是否完整、测试是否充分、是否需要人。
**`coldteadotai/abide`** —— agent 监督：读 coding agent 的每一次编辑，让 Jev 标出规则违反。**项目方报告：独立 reviewer 确认了 39 个被标记编辑中的 10 个、以及 15 个被标记 turn 中的 11 个。**（⚠️ 这个「假阳性率约 74%」的数字来自 awesome 列表转述，我未读 abide 原 README 核实，标注【未核实】）
**`gargpratyush/jev-router`**（MIT，265 stars）—— 把 Claude Code 任务路由到最便宜的能做该事的模型（madewithjev 记「121」）。
**`tamaratran/fast-jev-compaction`**（MIT，**5,375 stars**，2026-09-17 创建）—— Claude Code 插件
- 机制：**不用摘要**。每个 `tool_use` 配对的 `tool_result` 都问 Jev 两个 `noul` 问题：**call 该不该留**、**result 该不该原样留**。`keepResult ≥ 阈值` → 全留；否则 `keepCall ≥ 阈值` → 留 call、结果截断到前 N 字符；否则 call 和 result 一起删。用户/助手文本永远逐字保留且有序。
- 工程细节：state 默认压到 **25k token**（分级压缩策略），请求上限 **30k**（Jev 的 32k 限制之下），多个请求**并发**发送并合并答案。token 计不用 tokenizer（6 字母≈1 词、数字≈半 token、其他符号≈1 token），"calibrated to land a little above the counts Jev reports"。
- **失败即抛异常**，由调用方（或 Claude Code hook）决定 fallback。

### 6.4 内容审核 / 反钓鱼 / 护栏

| 案例 | 数字 | 来源与类型 |
|---|---|---|
| 垃圾邮件（Arize/Laurie Voss） | **18,514 封真实邮件**，Jev 零样本 **98.3%** vs TF-IDF（~14,800 标注训练）**98.4%**，差异不显著；两者在 466 封上分歧几乎均分 | 【第三方独立，真实标签】https://arize.com/blog/typesafe-jev-llm-judge/ |
| 垃圾邮件（bitnovus/jev-spam-eval） | 约 **9.9k** 真实邮件（5,733 ham/spam/phishing + 3,300 新 + 853 近期钓鱼），**98.6%** 准确率（带上下文增强、无任务特定拟合）；**未报 ECE** | 【第三方独立】经 scienthoon 与 awesome 列表转引 |
| 钓鱼（anisselbd/jev-phishing-bench） | **2,000 封邮件**，Jev **62.6% [60.5, 64.7]**，**ECE 0.154**（10 bins）；Claude Haiku 4.5 ECE **0.097** | 【第三方独立，对 Jev 不利】经 scienthoon 转引 |
| 邮件垃圾过滤（Enron） | **0.993 accuracy, 0.993 F1, 0.013 ECE** | 【项目方自测】Laya README 引用的对照数据集 |
| 钓鱼检测 | **0.980 accuracy, 0.979 F1, 0.012 ECE** | 【项目方自测】同上 |
| LLM 护栏 / jailbreak（held-out ToxicChat） | **0.755–0.762 accuracy**；**50% selective coverage 时准确率达 0.931** | 【项目方自测】Laya README |
| 事件列表审核（Near Here） | 50 例，Jev **48/50** vs Mistral Small 4 **42**、Gemini 3.5 Flash-Lite **43** | 【第三方独立】 |
| prompt-injection（Laya 自己的测试） | laya 0.698 / laya-multilingual 0.578（held out, n=116） | 【项目方自测】Laya README |
| 官方护栏配方 | TypeSafe docs 内有完整的 LLM guardrail 与 citation-check 配方 | 【官方】经 Capital & Compute 转引 |
| `openlayer-ai/jevals` | 「Agent evals and guardrails in one request. Built on Jev, Kev and Laya.」5 stars | 【本次核实】gh api |

### 6.5 RAG / 检索

- **LangChain 官方博文 demo**：`ModelRouterMiddleware`（Jev 按用户消息选模型：`openai:luna` 或 `openai:sol`）、`AutoModeMiddleware`（Jev 在工具执行前检查风险调用并阻断，示例针对 `bash`）。
  来源：https://www.langchain.com/blog/building-a-harness-with-jev
- **`llama-index-jev`**（WiktorB2004）：Jev 对每段检索结果 `Score`，用 `Choice`/`Noul` 选 query engine。**nfcorpus nDCG@5 从 0.340 → 0.396，约 $0.0003/query。**（⚠️ 数字来自 awesome 列表转述，未读原 README）
- **Laya 对照**：RAG passage relevance filtering **0.657 accuracy**（单次前向）。
- **`openlayer-ai/jevals`**、**`superagents-lab/jev-search`**（MIT，326 stars，Search1API，现场 demo jev.s1.dev）。

### 6.5b Agent 评测 / LLM-as-judge 替代（目前证据最强的一类落地场景）

- **LangChain agent-eval benchmark**（完整数字见 §2.9）：同样是 5 条 Deep Agents weather-tool trace，四个 judge 各评 100 次 = 每 judge 500 次判断，对照**人类 oracle**：
  - Jev **100%（500/500）**，GPT-5.6 Terra 99.8%，Luna 96.4%，**Claude Sonnet 4.6 仅 80.0%**
  - 方差：Jev 最低（0.0000149），Terra 高 913×，Luna 高 433×，Claude 高 92×
  - 成本：Jev **$0.00035/call，总 $0.34**；Claude Sonnet 4.6 **总 $28.17**（≈80,000×）
  - 时延：Jev 平均 **0.44 s**
  - ⚠️ 该测试同时是 **Jev 做「别的模型的裁判」的最强证据**，也是最窄的测试（5 例、1 agent、1 领域）
- **Arize 的架构建议（可直接引用为落地范式）**：
  > 「用决策模型跑**每一条** trace 做广覆盖测量与监控；在需要书面解释来改进系统时，**抽样失败案例再走一遍 LLM judge**。」Arize 明确指出这可能要求重新架构系统。
- **Arize 的 threshold 落地公式（来自其垃圾邮件测试）**：把打分为 **0.3–0.7 的 4.6%** 邮件送人工，其余保持 **99.5%** 准确率。给出的分桶校准：<0.1 → 0.1% 是垃圾邮件；≥0.9 → **99.9%** 是垃圾邮件；**0.5–0.6 → 只有 38%**。
- **`openlayer-ai/jevals`**：「Agent evals and guardrails in one request. Built on Jev, Kev and Laya.」
- **LangChain 的 `AutoModeMiddleware`**：Jev 在工具执行前检查风险调用并阻断（示例针对 `bash`）—— 官方博文把这条明确框为「以前只有闭源 harness 才有的能力，现在可以给所有 agent 加上」。
- **`tamaratran/fast-jev-compaction`**：Jev 替代 Claude Code 的压缩摘要（见 §6.3）。

### 6.6 其他被报道的场景与数字

| 场景 | 数字 | 来源 |
|---|---|---|
| **税务单据分类** `kyotofin/tax-doc-classifier` | 「**100% strict accuracy across 261 IRS forms, ~$0.001 per page**」（Apache-2.0，302 stars） | 仓库描述【项目方自测，措辞需谨慎对待——"100% strict accuracy" 未见独立复现】 |
| **交易** `jarrodwatts/jev-trader` | 每 **300ms** 区块（Monad）做一次 buy/sell 决策，在 Kuru 的 MON-USDC 下真实成交；MIT，1,584 stars | 仓库 + madewithjev |
| **Doom demo（官方）** | 约 **10 次决策/秒**，跑满一小时 **$7** | 官方发布博客；juejin 引用；StartupHub 报道 |
| **红警（社区）** | 社区用 Jev 驱动即时战略游戏 agent，**一天额度花 $0.1** | juejin 引用「网黑哥」微信文章 |
| **无人机** `jev-drone` | 模拟无人机每秒向 Jev 问 **2.5 次**判断 | madewithjev |
| **广告审计** | 有人 **40 秒扫完 724 条在投广告、花 9 美分** | juejin 转述社区案例 |
| **macOS 计算机操作** | 约 **$0.0002/步** | awlevin |
| **Django/YouTube sponsor 跳过** | Chrome 扩展实时检测赞助片段并跳过，**约 $0.005/视频**（原型，BYOK，开源） | madewithjev 引 Tony Dinh @tdinh_me |
| **1kpapers classifier** | madewithjev 首页 collage 提到 | madewithjev |
| **Vercel 内部用例** | Vercel CEO 发帖称 Jev 在某个 safety-review 步骤上 **p95 比之前用的小 GPT 模型快最多 18x** | thepromptindex 转述；**同一来源明确标注：「comes from a social post without published methodology, so file it under 'promising anecdote.'」** |
| **What3words** | **未核实**（我见到多个二手来源提及但未找到一手确认） |
| **Browserbase** | LangChain 博文称「Kyle Jeong from Browserbase is powering browser use agents for fractions of a cent」 | 无具体数字 |
| **邮件 triage at scale** | LangChain 称「Ryan Vogel is doing email triage at scale」 | 无具体数字 |

---

## 7. 未核实 / 存疑清单（报告必须标注）

| # | 事项 | 状态 |
|---|---|---|
| 1 | 「社区一条 thread 说 Jev 用 100% 合成数据训练」 | apidog 明确标注为 **unverified rumor**。**不要引用为事实。** |
| 2 | LangChain agent-eval benchmark 的**一手原文** | 原始出处是 **LangChain 的 X thread（Daniel Shea、Seán Roche，2026-09-20）**，我读的是 explainx.ai 的详细转述。**数字与设计已足够详细可引用，但报告若需最高可信度应直接取 X thread 或其 GitHub 仓库。** 见 §2.9 |
| 3 | Bespoke Nimble 9B 模型「66%→90%」 | 仅 explainx.ai 提及，**未核实** |
| 3b | **JevBench** 声称 Jev 领先、得分 **75.3** | 仅 explainx.ai（2026-09-21）提及，「**Neither claim comes with a linked source article**」。**未核实** |
| 3c | **Jev Playground** 声称「440x cheaper than LLMs」 | 同上，**无一手来源**。但「TypeSafe 系在一周内给出过至少 4 个不同的便宜倍数」这一点已被多源确认，见 §1.3c |
| 4 | `coldteadotai/abide` 的「39 个标记编辑中 10 个被独立 reviewer 确认」 | 来自 awesome 列表转述，**未读原 README** |
| 5 | `llama-index-jev` 的 nDCG@5 0.340→0.396、$0.0003/query | 来自 awesome 列表转述，**未读原 README** |
| 6 | `jarbon.medium.com` 的 Playwright 测试循环文章结论 | **抓取失败（解析到内网地址 10.36.28.67），未读到正文** |
| 7 | note.com 的 Laya 盈亏平衡分析（「52.6 million requests per month」） | **抓取失败（网络错误）**，仅从搜索摘要得知结论：单次成本低于此数时自托管才划算 |
| 8 | wavect.io 的「Laya vs Jev: What the Benchmarks Mean for AI Startup Moat」 | 仅见搜索摘要，**未读全文** |
| 9 | TypeSafe 官方 evals 站点 evals.typesafe.ai 的数据 | ✅ **已解决**：#1.3 的全部数字与四条工作流明细均由我直接从该站点 HTML 解析得到（另有第三方 Capital & Compute 独立推算印证）。**已完成一手核实** |
| 10 | TypeSafe 官方博客 typesafe.ai/blog/introducing-system-one-models-and-jev 一手全文 | ✅ **基本解决**：我未自己抓取全文，但 #1.3 的官方方法学原文、四个工作流数据均为一手；发布博客的 193.6x/444.6x/$0.042/70–500ms 等条目被至少 6 个独立二手来源一致转述 |
| 11 | 是否存在面向中国大陆的合规方案 / 境内节点 | **未找到任何信息** |
| 12 | TypeSafe 的 ZDR / No-Training 是否为默认、是否有合同级承诺 | **未核实**。只确认可按请求启用 |
| 13 | `tamaratran/fast-jev-compaction` 5,375 stars、`browser-use/jev-ultrafast` 12,585 stars 等的高星速 | **未做 star-history 审计**。5 天内 12.5k stars 对一个知名组织的项目不算异常，但**报告中不宜把 star 数当作质量信号**——目录站自己也这么说 |
| 14 | Jev 训练数据是否包含 OpenBookQA / CommonsenseQA / HellaSwag / MMLU 的 train split | scienthoon 明确写「**We cannot verify contamination either way**」，但指出准确率「consistent with」训练集包含这些 split |
| 15 | 中文语料上的概率校准独立数据 | **无**。juejin 明确「校准表现在中文语料上没有独立数据」 |
| 16 | Jev 是否使用稀疏 MoE | Archer 自述这是**最不确定**的假设，纯推断 |
| 17 | Jev 的 base model 是什么 | **未知**。tokenizer 不属于任何 192 个公开 tokenizer；最接近 Qwen（415 探测中 348 一致），但不能确定 |
| 18 | `hev` / `hev-*` 系列仓库 | 在 gh 搜索中出现但我在 apidog 文章里看到的是 "OpenJev"。**未核实是否有名为 hev 的独立主流项目** |
| 19 | madewithjev.com 的 All=386 vs 分类求和 475 | **口径未说明**，站方未解释 |
| 20 | madewithjev 提到的「143 个仓库」 | **我实测为 195**（2026-09-21）。143 应为更早快照 |

---

## 8. 参考链接全集

### 第三方独立测试（原始出处）
- https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds
- https://nearhere.events/blog/typesafe-jev-mistral-gemini-event-validation
- https://github.com/gemanor/jev-code-review-benchmark
- https://paddo.dev/blog/thirty-cent-judge
- https://arize.com/blog/typesafe-jev-llm-judge/
- https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/
- https://github.com/scienthoon/jev-ood-calibration
- https://github.com/RINNECODER/jev-behavior-study
- https://github.com/4esv/jev-eval
- https://github.com/SamuelSacco/jev-exploration
- https://github.com/bitnovus/jev-spam-eval
- https://github.com/anisselbd/jev-phishing-bench
- https://github.com/AbdelStark/jev-benchmarks
- https://github.com/nibzard/decision-model-benchmark
- https://archerhume.com/posts/jevs-architecture-unmasked

### 分析 / 批评 / fact-check
- https://apidog.com/blog/openjev-open-source-jev-alternatives
- https://explainx.ai/blog/jev-speed-cost-claims-fact-check-2026
- https://explainx.ai/blog/langchain-jev-agent-evals-benchmark-september-2026（LangChain agent-eval benchmark 详细转述，原始出处是 LangChain X thread）
- https://explainx.ai/blog/jevbench-jev-playground-claims（JevBench 75.3 / 440x，**无一手来源**）
- https://explainx.ai/catch-up-on-ai/2026-09-20
- https://forkast.news/typesafe-ais-jev-is-not-an-llm-and-that-may-be-the-point/
- https://tech.yahoo.com/ai/meta-ai/articles/typesafe-ai-jev-not-llm-205510286.html（Forkast 转载）
- https://mer.vin/news/laya-the-33ms-open-source-decision-model-beating-jev/
- https://hn.today/s/laya-the-open-source-version-of-jev
- https://wavect.io/blog/laya-vs-jev-benchmark-ai-startup-moat/
- https://note.com/genelab_999/n/n97cb6ae0e4e7（Laya 盈亏平衡，抓取失败）
- https://ecosistemastartup.com/convai-lanza-laya-el-rival-open-source-de-jev-8-veces-mas-rapido/
- https://es.news.hada.io/topic?id=33944
- https://www.techspot.com/article/3172-meet-jev/
- https://vedcraft.com/tech-trends/gen-ai/jev-typesafe-system-one-model/
- https://lmrank.com/blog/jev-system-one-pivot-rlhf-co-inventor-ditched-language-models/
- https://www.ayautomate.com/blog/jev-typesafe-system-one-model
- https://www.progressiverobot.com/2026/09/16/jev-model-typesafe-programmatic-logic/
- https://blog.mushroom.cv/blog/typesafe-ai-jev-system-one-model-rlcd-decision-ai-enterprise/
- https://mortalapps.com/blog/typesafe-jev-decision-model-vs-llm-architecture/
- https://www.remio.ai/post/typesafe-jev-ai-model-challenges-the-llm-first-software-stack
- https://cellcog.ai/blog/jev-typesafe-decision-model/
- https://www.thepromptindex.com/jev-typesafe-system-one-model-guide.html
- https://news.agentcommunity.org/issues/2026-09-18-memory-gates-agents
- https://doomers.ai/work/typesafe-ai-case-study
- https://startupfortune.com/typesafe-ais-decision-model-jev-becomes-vercels-fastest-adopted-launch/
- https://www.tao.media/vercel-says-jev-saw-fastest-first-day-adoption-in-ai-gateway-history/
- https://notifire.in/ai/why-developers-are-flocking-to-this-new-ai-model
- https://jevainews.com/ 与 https://jevainews.com/access/
- https://www.llmrumors.com/news/typesafe-ai-jev-system-one-model-use-cases

### 中文来源
- https://juejin.cn/post/7687445339747794953（稀土掘金，「让英雄去查英雄」长文，批评视角最完整的中文来源）
- https://k.sina.com.cn/article_5952915720_162d2490806704v6wc.html?from=tech（硅星人 50 条中文客服实测）
- https://www.163.com/dy/article/L7A1FH0A0511DPVD.html（深度解读：关于 Jev 的几大疑问）
- https://www.cndba.cn/article/17105（开源/闭源状态澄清 + Jev+DeepSeek 架构）
- https://claudemax.shop/blog/typesafe-jev-use-cases-and-integration（中文落地指南，含数据出境提醒与 ¥11 邀请函销售）
- https://app.myzaker.com/news/article.php?pk=6aaf56508e9f094eeb7e2b7e（ZAKER 转载 Laya 中文报道）
- https://gist.github.com/pjburnhill/adf8d28efcad9df037bfdece178ef965（TypeSafe Jev 综合项目参考 gist）

### 生态目录
- https://jevbest.com/zh/（bestjev，503 项目）
- https://github.com/heyjunpenn/awesome-jev（bestjev 数据源，38 stars）
- https://madewithjev.com/github-repos（195 repos，运营者 Jon Kraayenjon）
- https://github.com/kraayenjon/awesome-jev
- https://logicrw.github.io/awesome-jev-projects/en/ 与 https://github.com/logicrw/awesome-jev-projects
- https://abdelstark.github.io/awesome-typesafe/

### 官方与平台集成
- https://typesafe.ai/blog/introducing-system-one-models-and-jev
- https://evals.typesafe.ai/ （**四个工作流的逐模型数据，本文件 §1.3 一手来源**）
- https://evals.typesafe.ai/security-incidents
- https://evals.typesafe.ai/invoice-processing
- https://evals.typesafe.ai/customer-service
- https://evals.typesafe.ai/agent-trace-observability
- https://docs.typesafe.ai/models
- https://docs.typesafe.ai/concepts/system-one
- https://docs.typesafe.ai/introduction
- https://docs.typesafe.ai/api
- https://docs.typesafe.ai/concepts/use-case-map
- https://evals.typesafe.ai/
- https://www.businesswire.com/news/home/20260915525333/en/
- https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway
- https://vercel.com/blog/ai-gateway-jev-model-launch
- https://www.langchain.com/blog/building-a-harness-with-jev
- https://pydantic.dev/docs/ai/models/typesafe/
- https://github.com/typesafe-ai/skills
- https://github.com/typesafe-ai/typesafe-sdk-python
- https://github.com/typesafe-ai/typesafe-sdk-js

### 复现 / 替代项目
- https://github.com/NandhaKishorM/laya
- https://huggingface.co/convaiinnovations/laya
- https://huggingface.co/convaiinnovations/laya-typed-decisions
- https://github.com/TheoLeeCJ/SemIf（原 OpenJev）
- https://github.com/receptron/laya（Node.js/TS via ONNX Runtime，MIT，38 stars）
- https://github.com/jaredpalmer/kev ＋ https://huggingface.co/collections/jaredpalmer/kev-6aad9d0ea49f2589665e07cd
- https://github.com/TianyuCodings/NanoJev ＋ https://huggingface.co/C-Tianyu/NanoJev
- https://github.com/vinnylarouge/jevlike
- https://github.com/razorback16/openjev
- https://github.com/ekzhang/openjev-sglang
- https://github.com/wfzyx/von
- https://github.com/featherless-ai/simple-jev
- https://github.com/Heman10x-NGU/openJev-verdict-2.0
- https://github.com/mizorewww/laya-mlx ＋ https://github.com/mizorewww/laya-coreml
- https://github.com/0xBakeer/arbiter
- https://github.com/openlayer-ai/jevals

---

## 9. 可直接用于报告的对照表素材（汇总）

### 表 A：Jev 的倍数宣称 — 官方 vs 第三方

| 来源 | 速度倍数 | 成本倍数 | 类型 |
|---|---|---|---|
| TypeSafe 首页 | 193.6x | 444.6x | 【官方】 |
| TypeSafe 发布博客 | 40x–200x | 未公布 | 【官方】 |
| TypeSafe early-access onboarding（非公开） | 20x–200x | 40x–1,000x | 【官方】 |
| 按官方 evals 表手算 | 约 25x–95x | 76x–440x | 【第三方推算】 |
| **Every** | **约 25x**（vs Fable 5.1） | **约 580x**（vs Fable 5.1） | 【第三方独立】 |
| **Near Here** | — | **8.6x**（vs Mistral Small 4）/ **58x**（vs Gemini 3.5 Flash-Lite） | 【第三方独立】 |
| **gemanor** | 4.8x–5.7x 时延 | **45x**（vs Gemini 3.8-Flash）/ **274x**（vs Fable 5.1） | 【第三方独立】 |
| **4esv/jev-eval** | **5x** | **41x–50x**（vs GPT-5.6 Terra） | 【第三方独立】 |
| **硅星人（中文）** | 0.73–0.75s vs DeepSeek V4 Flash 5.58s | 50 题 $0.002 | 【第三方独立】 |
| **Capital & Compute** | 中位 314ms（复现官方 70–500ms 区间） | $0.0238/千次 | 【第三方独立】 |

### 表 B：Jev 准确率 — 官方（一手）vs 各独立测试

**B-1 官方 evals 逐工作流（一手，见 §1.3b）— 最强的一格说明 Jev 的表现高度任务依赖**

| 工作流 | Jev | 该工作流最佳 | Jev 在 9 个模型中的排名 | Jev 成本排名 |
|---|---|---|---|---|
| Security Incidents | **61.7%**（$0.0001, 0.3s） | Opus 5 workflow 66.2% | 第 3 | **第 1（最低）** |
| Invoice Processing | **61.8%**（$0.0011, 0.5s） | Sol workflow 79.1% | **第 8（仅胜 Haiku 4.5）** | 第 2 |
| Customer Service | **76.0%**（$0.0001, 0.4s） | Sol workflow 78.3% | 第 4 | **第 1** |
| Agent Trace Observability | **71.6%**（$0.0003, 0.5s） | Sol workflow 76.6% | 并列第 6 | **第 1** |
| 四者平均 | **67.8%** | Sol workflow 74.1% | — | **第 1** |

> ⚠️ **发票处理工作流上 Jev 几乎垫底**，输给包括最便宜的 Luna（67.8%）和 DS V4 Flash（69.8%）在内的 8 个模型。**这是「Jev 不是通解」的最硬证据，且是官方自己公布的数据。**

**B-2 官方平均 vs 各第三方**

| 测试 | 任务 | Jev | 对照组 | 结论 |
|---|---|---|---|---|
| 官方 evals（一手） | 4 个自建工作流平均 | **67.8%** | Terra(wf) 67.9% / Sonnet5(wf) 67.8% / Sol(wf) 74.1% / Opus5(wf) 73.1% | 与 Terra、Sonnet 5 持平；落后 Sol/Opus 5 五点几 |
| **LangChain（2026-09-20，第三方）** | **500 次重复判断，binary does_pass，对照人类 oracle** | **100%（500/500）** | Terra 99.8% / Luna 96.4% / **Claude Sonnet 4.6 80.0%** | **Jev 第一**；方差最低（对手高 92–913 倍）；$0.00035/call，总 $0.34 vs Claude $28.17 |
| Arize | 18,514 封垃圾邮件（真标签） | **98.3%** | TF-IDF 98.4% | 统计持平 |
| gemanor | 1,080 次 Python 规则审查 | **98.0%** | Gemini 3.8-Flash 100% / Fable 5.1 100% | 落后 2 点 |
| 4esv | intent 77 类 | **0.78** | Terra 0.85 | 落后 7 点 |
| 4esv | sentiment 5 档 | 0.57 | Terra 0.59 | 持平 |
| 4esv | 正/负二分类 | 0.97 | Terra 0.97 | 持平 |
| Every | 12 段写作质量（7 个植入缺陷） | 6/7 | Fable 5.1 7/7 | 落后 1 个 |
| Near Here | 50 例活动列表审核 | 48/50 | Mistral Small 4 42 / Gemini Flash-Lite 43 | 领先 |
| 硅星人（中文） | 50 条中文客服（4 项全对才算） | **64–65.2%**（32–32.6/50） | 便宜组第一 DeepSeek V4 Flash 多 1.2 分；强组 MiniMax M3 高 10.8 点 | **便宜组第二，强组最后** |
| scienthoon | 900 条自造合成工单 | 75.1%（不可知子任务 **44.7%**） | — | 不可知任务上概率未反映无知 |
| RINNECODER | Snake 8 食物（16 种子） | 1/16（无协助）；0/16（有协助原始提示） | 喂入精确路线事实后 16/16 | **加答案即全对** |
| RINNECODER | 3D 城市驾驶 | **0/12** 完整任务；522 次转向全选直行 | — | 该项目方自测 |
| NanoJev（项目方） | ViZDoom Basic | **56/128 = 与未微调 Qwen3-0.6B 相同** | NanoJev 128/128 | **Jev 相对裸 base model 无增益** |
| kev（项目方） | typed-decisions 新数据源 | **0.857**（acc）/ **0.211**（Brier） | Kev-9B 0.812/0.837 acc、0.291/0.243 Brier | **Jev 分布质量更好，准确率接近** |
| Laya（项目方） | typed-decisions 2,000 决策 | 0.727 | Laya-typed-decisions 0.766（需微调） | Laya argmax 领先，soft 落后 |

### 表 C：Jev 的校准证据

| 测试 | 数据集 | ECE | 备注 |
|---|---|---|---|
| 官方 | 未公布 | 未公布 | 配方未公开，无论文 |
| scienthoon | OpenBookQA (n=500) | **0.024** | 噪声底 0.024，比值 1.0× |
| scienthoon | CommonsenseQA (n=1,221) | 0.032 | 噪声底 0.019，1.7× |
| scienthoon | HellaSwag (n=2,000) | 0.029 | 噪声底 0.018，1.6× |
| scienthoon | 自造工单 (n=900) | **0.107** | 噪声底 0.024，**4.4×** |
| scienthoon | 同上，score 子任务 | **0.325** | Refit T **3.40**（高度过度自信） |
| scienthoon | 同上，boolean 子任务 | 0.079 | Refit T **0.66**（欠自信） |
| scienthoon | `confidence` 字段（合成集） | **0.18** | 比 max probability 更差 |
| 4esv | intent 77 类 | 0.11 | Terra 0.08 |
| 4esv | sentiment 5 档 | 0.20 | Terra 0.30（Jev 更好） |
| 4esv | 正/负 | 0.04 | Terra 0.02 |
| Archer | MMLU 1,200 项（10 bins） | **0.0313** | 990 项落在 0.9–1.0 箱 |
| Laya 项目方 | typed-decisions | **0.144** | Jev 开箱；Laya base 0.213，拟合后 0.081 |
| bitnovus | 9.9k 邮件 | 未报 | jev-exploration 重分析：高估低概率、低估高概率 |
| anisselbd | 2,000 钓鱼邮件 | **0.154** | Claude Haiku 4.5 为 0.097（Jev 更差） |

### 表 D：生态规模（三种口径，互不一致，报告需注明）

| 口径 | 数值 | 来源 | 备注 |
|---|---|---|---|
| GitHub `q=jev` 全站 | **7,330** | gh api | 含大量无关项目 |
| GitHub `q=jev created:>2026-09-01` | **4,126** | gh api | 9 月以来的 |
| GitHub `q=typesafe+jev` | **1,505** | gh api | — |
| jevbest / bestjev | **503**（人工核验；10 分类、25 语言） | jevbest.com | 自声明非官方；Star 快照系统性偏低 |
| madewithjev「GitHub」tab | **195** | madewithjev.com | 【本次核实】实测 |
| madewithjev「All」tab | **386** | madewithjev.com | 与分类求和 475 **不一致** |
| cobanov/awesome-jev | **155** | README | — |
| logicrw/awesome-jev-projects | **358+** | badge | — |
| walidboulanouar/awesome-jev-use-cases | 74 demos / 150+ repos | README | sponsored by AY Automate |
| Reddit 人工 review | 从 **287** 个仓库中筛出 **20** 个真正解释模型的 | v-modal 列表引用 r/LLMDevs | 【未核实原文】 |
| 官方 skills 仓库 | `typesafe-ai/skills`，1,259 stars | gh api | **创建于 2026-08-24，早于出隐** |
