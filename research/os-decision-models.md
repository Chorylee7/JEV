# JEV 调研 · 开源决策模型原始资料（核实于 2026-09-21）

核实工具：`gh api`（账号 Chorylee7）、HF Hub API、arXiv API、PyPI JSON API、FetchURL。所有 star/likes/日期均为当日实时 API 返回值。

---

## 1. Laya（Convai Innovations / Nandakishor Mukkunnoth）

### 1.1 仓库与发布物（已核实）

| 项目 | 链接 | 状态（2026-09-21 gh api / HF API） |
|---|---|---|
| 主 GitHub 仓库 | https://github.com/NandhaKishorM/laya | star 5060、fork 454、Apache-2.0、创建于 2026-09-18T04:46Z、最近推送 2026-09-20T17:44Z、open issues 26 |
| HF 主权重（English，仓库根含全部三个 checkpoint 的子目录结构） | https://huggingface.co/convaiinnovations/laya | likes 1204，创建于 2026-09-18T05:05Z，license tag apache-2.0，pipeline text-classification |
| HF 多语言权重 | https://huggingface.co/convaiinnovations/laya-multilingual | likes 81，创建 2026-09-19T03:23Z，apache-2.0 |
| HF typed-decisions 微调权重 | https://huggingface.co/convaiinnovations/laya-typed-decisions | likes 45，创建 2026-09-18T17:45Z，apache-2.0 |
| PyPI | https://pypi.org/project/laya/ | 版本 0.3.4，14 个 release（已核实可达） |
| 在线 Demo | https://huggingface.co/spaces/convaiinnovations/laya-demo | HTTP 200 可达 |
| 作者工程文章 | https://dev.to/nandakishor_m_6cc0adfde9f/i-built-non-autoregressive-decision-models-a-year-ago-then-a-frontier-lab-called-it-a-18me | HTTP 200 可达 |
| 作者 GitHub | https://github.com/NandhaKishorM | 85 个公开仓库，账号 2019 年创建 |

注意：GitHub 上没有 `convaiinnovations` 组织（gh api 404）；HF 上的 `convaiinnovations` 是组织/作者名。主代码仓库就是个人账号 `NandhaKishorM/laya`。

### 1.2 架构与规模（来源：HF 模型卡 + GitHub README，项目方宣称）

- 非自回归、双向编码器 + 从零训练的决策头（2 层 transformer、option-marker scorer、act/escalate 头）。每个选项在自己的 `[MASK]` token 处打分，对该问题的选项做 softmax；答案空间在请求时定义，新 schema 无需重训。
- `laya`（英文）：ModernBERT-large（395M）+ 决策头 = **421M**，上下文 512（head_max_len 192）。
- `laya-multilingual`：mmBERT-base（22 层、256k 词表）= **322M**，上下文 1024（编码器 RoPE 可到 8192）。
- `laya-typed-decisions`：ModernBERT-large，421M，上下文 1024。
- 一次前向/批量回答一次调用中的所有问题。

### 1.3 训练方法（项目方宣称）

RLCD（Reinforcement Learning for Calibrated Decisions）：策略输出分布，对 logits 加零均值高斯噪声探索，奖励为严格适当评分规则（log + spherical，序数问题用 ranked probability score），REINFORCE + 组均值基线（GRPO 风格）。多轮对话用 TD(λ=1.0)。微调 notebook：Kaggle 2×T4，4 epoch、约 30k 问题、4–5 小时（`notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb`）。

### 1.4 训练数据公开性

- **未发现官方公开发布的 Laya 训练数据集**：HF `convaiinnovations` 名下的 dataset 列表中没有 laya 相关数据集（仅有 llama2-new、Nadi_Indic466k、bilingual-coding-qa、physics-reasoning、fastapi-qwen-api 等旧项目）。
- README 披露训练混合成分：AG News、BoolQ "in training mix"；DAIR Emotion、prompt-injections、SST-5 为 held out。
- typed-decisions 基准数据本身由社区上传（如 `LocalLLaMA/typed-decisions`，2026-09-16 创建，非作者本人）。
- 结论：**权重开放、训练代码（notebook）开放、训练数据未完整公开**。

### 1.5 官方基准数字（项目方自测，Tesla T4；Jev 数字为第三方已发布值，非项目方实测）

Laya vs TypeSafe Jev 1.13.0（来源：HF 模型卡 / BENCHMARKS.md）：

| 指标 | Jev 1.13.0 | Laya（routed） |
|---|---|---|
| typed-decisions（2,000 decisions） | 0.727 | 0.766（teacher 自洽上限 0.735） |
| AG News | 0.910 | 0.950 |
| DAIR Emotion | 0.480（Brier 0.846） | 0.595 |
| Banking77 | 0.870（72 labels） | 0.425（77 labels） |
| ECE（越低越好） | 0.246 | 0.081（温度拟合后） |
| p50 延迟 1 问 | 236–276 ms | 32.8 ms（约 7.8×） |

三个 checkpoint 在 typed-decisions 上（400 cases / 2,000 decisions，项目方实测）：
laya-typed-decisions 0.766 / soft acc 0.471 / Brier 0.062 / ECE 0.213 / score MAE 0.242；base laya 0.362；multilingual 0.342（多数类基线 0.461、随机 0.318）。按 primitive：noul 0.857、choice 0.733、score 0.723。按工作流：invoice 0.804、security 0.766、customer service 0.764、agent-trace 0.730。

HF 仓库 `eval/results.md`（校准后）：in-task 总体 acc 0.753 / ECE 0.030 / Brier 0.308，50% 覆盖率下 acc 0.947；zero-shot 总体 acc 0.651 / ECE 0.204。延迟：1 问 p50 38.4ms、10 问 156ms、50 问 721.4ms。

多语言（51 语言，MASSIVE intent 20 选项）：英文 checkpoint 在非拉丁文字上静默崩塌（Khmer 准确率 0.000 但置信度 0.952）；宏观平均 0.227、macro ECE 0.733，51 语言中只有 23 个超过 3× 随机。multilingual 为 45/51。Router 用纯 Python Unicode 文字检测（<0.5–0.73ms）在前向之前选 checkpoint。

英文 held-out 任务：AG News 0.947（训练混合内）、BoolQ 0.830（混合内）、DAIR Emotion 0.573、prompt-injections 0.698（n=116）、SST-5 0.372。

实际工作流（mer.vin 文章转述项目方数字）：Enron 垃圾邮件 0.993 acc / ECE 0.013；钓鱼检测 0.980；ToxicChat 越狱 0.755–0.762（50% 选择性覆盖时 0.931）；RAG 相关性过滤 0.657；10 类工单路由 0.522。

### 1.6 已知局限（项目方自述）

- base checkpoint zero-shot 接近随机（0.362/0.342 vs 随机 0.318、多数类 0.461）；0.766 来自在该基准自身训练集上微调的 checkpoint——"是快速特化基座，不是 zero-shot 决策引擎"。
- 高基数 choice（默认设置 >20 选项）退化：Banking77 77 选项时每 label 仅 ~3–4 token（head_max_len 192/256 共享预算），0.425 vs Jev 0.870。缓解：运行时调大 `head_max_len=512`，或分层 coarse-to-fine。
- soft accuracy 落后 Jev（0.471 vs 0.580）：argmax 更准但分布与 teacher 匹配更差。
- score 是最弱 primitive（SST-5 0.372）。
- 出厂过自信：需按 (问题类型, 选项数) 拟合温度，ECE 0.466→0.081（英文）、0.314→0.106（多语言，出厂完全无拟合温度）。
- 部署坑：默认 `max_loaded=1` 时语言切换会触发 7.4s（CPU）/10.3s（T4）重载；需 `Router(preload=True)`。

### 1.7 硬件需求

- 官方 SDK（PyTorch/transformers）：CPU 193–464ms/问；T4 GPU 32.8–39.5ms/问；微调用 Kaggle 免费 2×T4。
- 已知坑：`transformers` 在装有 TF 时 import 探测可能死锁，需 `USE_TF=0`。

### 1.8 mizorewww/laya-mlx（第三方 MLX 移植，非官方）

- https://github.com/mizorewww/laya-mlx — star 1938、fork 99、Apache-2.0，创建/推送 2026-09-19。
- Apple Silicon 原生 MLX 推理，无 PyTorch/cloud。M3 Max（40 GPU 核、128GiB）：英文 421M 单短问 P50 13.42ms，多语言 322M 7.39ms；50 问吞吐 146.8 / 395.0 q/s；峰值显存 943.6 / 687.6 MiB。
- 移植保真：63/63 验证题在 FP32/FP16 下与上游选中答案一致（378/378 比较）。明确声明是独立移植，非 Convai 官方发布。权重在 https://huggingface.co/aac6fef/laya-mlx 。

### 1.9 第三方独立验证（与项目方宣称区分）

- **AbdelStark/jev-benchmarks**（https://github.com/AbdelStark/jev-benchmarks ，star 12，Apache-2.0，2026-09-17）：独立实测 **Jev**（非 Laya）vs GLiNER2.5，300 样本。证实 Jev 侧数字：AG News 0.910、Banking77 0.870、DAIR Emotion 0.480（Brier 0.846、16% 样本真实标签零概率）、Jev p50 延迟 236–256ms（从法国调托管 API）。即 Laya 对比表中的 Jev 数字有独立出处。
- **nibzard/decision-model-benchmark**（https://github.com/nibzard/decision-model-benchmark ，2026-09-18，0 star）：Laya README 引用的另一 Jev 延迟来源。
- **yibie/laya-jev-lab**（2026-09-20，0 star）：自称独立测量 Jev vs Laya 及本地级联；**尚未核实其具体数字**。
- **elcronos/jev-vs-open-decision-models**（2026-09-20，0 star）：自称 zero-shot 对比 Jev 1.13 vs PrismNLI-0.4B vs Laya；**尚未核实具体数字**。
- 结论：Laya 侧所有精度/校准数字目前**只有项目方自测**（数字与 HF eval/results.md 自洽），Jev 侧数字有 AbdelStark 独立佐证；尚无高关注度的第三方复测 Laya 精度。

---

## 2. 2025 年 3 月的 RL 非自回归决策论文（已核实存在）

- **arXiv:2503.23303**《SalesRLAgent: A Reinforcement Learning Approach for Real-Time Sales Conversion Prediction and Optimization》，Nandakishor Mukkunnoth，提交 2025-03-30。摘要（arXiv API 核实）：把销售对话转化概率预测当作序列决策问题，PPO 训练，GPT-4o 生成合成数据，Azure OpenAI 3072 维 embedding + 逐轮状态跟踪 + 元学习；自称转化预测 96.7% 准确率、85ms vs GPT-4 3450ms。链接：https://arxiv.org/abs/2503.23303 。**注意**：PDF 仅 11KB，是短文/技术报告体量；领域限于销售对话，不是通用 typed-decision 框架。
- **arXiv:2510.01237**《Confidence-Aware Routing for Large Language Model Reliability Enhancement》，同一作者，2025-09-23 提交。主题是生成前的置信度感知路由（多信号幻觉缓解），https://arxiv.org/abs/2510.01237 。mer.vin 称其"形式化了 schema-based RL 决策"，从摘要看该论文实际是 LLM 路由/幻觉缓解方向，与 Laya 的决策头框架关系属作者自述谱系，**论文本身不是 Laya 的技术报告**。
- mer.vin 文章称 SalesRLAgent 当时"发布了权重、开放数据集和 PyPI 包"——**未核实/未找到**：HF 搜 SalesRLAgent 无模型与数据集；PyPI `salesrlagent`/`SalesRLAgent`/`sales-rl-agent` 均 404；GitHub 搜索未见对应仓库（作者 85 个公开仓库中未见）。可能已删除/改名，或报道夸大。
- **Laya 本身没有正式技术报告/论文**；最接近的文档是 HF 模型卡、BENCHMARKS.md 和 Dev.to 工程文章。

---

## 3. 「严格 schema + 要概率」场景的其他替代方案

### 3.1 ModernBERT 类判别式分类器（已核实存在）

- https://huggingface.co/answerdotai/ModernBERT-base （Apache-2.0，2024-12-11 发布，当月下载 4.4M）与 /ModernBERT-large（月下载 63 万）。8192 上下文双向编码器。
- 用法：分类头微调（noul=二分类 sigmoid、choice=softmax、score=序数回归/分箱）。概率校准：softmax 原生过自信，需温度缩放（Guo et al. 2017, ICML《On Calibration of Modern Neural Networks》，arXiv:1706.04599）后 ECE 可达 0.02–0.08 量级（文献经验值，非本次实测）。
- 标注量：单任务通常数百至数千条标注即可微调到可用水平（AG News 类任务全量微调接近 SOTA）；每新增一个 schema 需重新训练一个头（与 Laya/Jev 的"请求时定义答案空间"不同）。
- 延迟：395M 模型单次前向，GPU 个位数到数十 ms，CPU 百 ms 级；无 API 成本。
- **GLiNER2.5**（https://huggingface.co/fastino/gliner2.5-multi-v1 ，Apache-2.0）：zero-shot 带每标签概率的判别式模型，AbdelStark 实测 M4 Max CPU 上 4–6 标签任务 p50 ~44ms，但 AG News 0.700 / Banking77 0.610 明显低于 Jev（第三方数据）。

### 3.2 Embedding + 规则/阈值

- 路线：embedding 模型（如 mmBERT https://huggingface.co/jhu-clsp/mmBERT-base ，MIT，2025-07 发布）编码 state 与选项描述，最近邻/余弦 + 阈值；或逻辑回归/高斯过程头。
- 概率：余弦相似度不是概率；需 Platt scaling / isotonic 拟合才能当概率用，校准质量取决于验证集，分布外漂移时无保证。
- 标注量：可 zero-shot（靠选项文本语义），几十个标注样本即可拟合校准曲线。
- 延迟：编码一次 + 向量运算，CPU 即可 10–50ms 级。
- 适用：选项语义清晰、基数不大、精度要求中等的路由/去重/匹配。

### 3.3 微调小生成模型输出 JSON

- 路线：Qwen/Llama 1–4B SFT 输出固定 JSON schema（可加 logit bias / 约束解码保证 schema 合法）。
- 概率：生成的"confidence"字段是 token 采样产物，**无校准保证**（语言模型自述置信度文献中普遍过自信）；要真概率需读 option token logits 或另训校准层——此时已接近"判别式头"路线。
- 标注量：每 schema 数百至数千条。
- 延迟：自回归解码，即使小模型也要 100ms–1s 级，且概率多一次额外前向。
- 结论：在"严格 schema + 校准概率 + 低延迟"三要素同时成立时，判别式路线（Laya / ModernBERT 分类头）结构上优于生成式路线。

---

## 4. 媒体报道源（二手，转述时已压缩）

- mer.vin 报道：https://mer.vin/news/laya-the-33ms-open-source-decision-model-beating-jev/ （含作者背景、时间线、全部基准转述；文中"released the weights, the dataset, and the paper"针对的是 2025-03 的 SalesRLAgent，其权重/数据集本次未找到）
- hn.today 摘要：https://hn.today/s/laya-the-open-source-version-of-jev （AI 生成的摘要页，内容与官方 README 一致，无新增独立数据）

## 5. 未完成/未核实清单

- Laya 全部精度、校准、多语言数字：仅项目方自测，无独立复测（yibie/laya-jev-lab、elcronos 两个第三方仓库内容未逐条核实）。
- SalesRLAgent（2025-03）的权重/数据集/PyPI 包：未找到，媒体报道与可查证事实不符或未留痕。
- Laya 训练数据：未公开发布，仅成分部分披露。
- Jev 官方定价 $0.042/Mtok 与规格：以任务给定背景为准，本次未独立核实 TypeSafe 官网。
