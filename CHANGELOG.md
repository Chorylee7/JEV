# Changelog

## v1.2.2 — 2026-09-29

- **修复目录跳转**：章节标题改用显式 `<a id>` 锚点。原因：emoji 标题使 GitHub 自动 slug 产生前导 `-`（`--快速参考卡-...`），🏗️/⚠️ 还引入不可见变体选择符字符，导致原链接全部失效；显式锚点不受 slug 规则影响（已在线上渲染验证）。

## v1.2.1 — 2026-09-29

- README / REPORT-EN 视觉改版：居中头部 + shields 徽章 + 导航行、章节标题图标、居中页脚。

## v1.2 — 2026-09-29

**新增交付物**
- **快速参考卡**：README 顶部新增"Quick Reference Card"（15 行关键结论一表速览）。
- **`REPORT-EN.md`**：全英文版报告（README v1.1 的完整英文翻译，582 行，证据标记映射为 [Official]/[Third-party]/[Vendor-reported]/[Unverified]）。
- **`eval/` 评估脚手架**：在你自己的 JSONL 样本上实测 JEV（或本地 Laya / mock）的准确率、弃权率、自动处理区间准确率、ECE、抖动（flip rate）、串联成功率、成本与延迟。核心零依赖（stdlib），mock 模式可无 key 冒烟。已通过冒烟测试（`reports/smoke`，gitignored）。
- `.gitignore`：排除 `reports/`、`__pycache__/` 等。

## v1.1 — 2026-09-29

**数据刷新（gh api 当日快照）**
- star / fork / 许可证快照从 2026-09-21 更新至 2026-09-29。
- 生态总量：GitHub `q=jev` 仓库 7,330 → **14,028**（8 天 +91%）。

**项目层面的重要变化**
- **Laya 成为生态绝对主导者**：5,060 → **28,058**★（+454%），HF likes 1,204 → 4,395；MLX 移植 `mizorewww/laya-mlx` 1,938 → 6,604★。
- **SemIf 二次更名**：`TheoLeeCJ/SemIf` → `TheoLeeCJ/SemIf-OpenJev`（4,547★）。
- **Together AI 下场**：`togethercomputer/tev1`（165★，MIT），基于 Qwen3.5-4B 微调的 open-weight 决策模型——首家正规公司发布 JEV 类开源替代。
- 新增 entrant：`ollaya-dev/ollaya`（916★，本地服务化）、`Liuziyu77/Valen`（474★，多模态训练框架）、`allebee/jevk5`（123★，open-weight 替代）、`dzhng/jevgrep`（1,574★，代码检索应用）。
- 显著增长：`browser-use/jev-ultrafast` 12.6k → 21.3k★、`jaredpalmer/kev` 1.2k → 7.7k★、`tamaratran/fast-jev-compaction` 5.4k → 7.2k★、`yibie/awesome-jev` 674 → 1,950★。
- 许可证变化：`featherless-ai/simple-jev` 由无许可证补为 Apache-2.0。

**官方信息核实更新**
- 官方版本仍为 `jev-1.13.0`（无 preview 构建），限速仍声明动态调整。
- 数据政策已在官方 Models 页核实："Jev is not trained on customer requests or responses"；ZDR 仅企业版。原"未核实"项已转为已核实。

**仓库元信息**
- 新增 `LICENSE`（CC BY 4.0）、`CITATION.cff`、`CHANGELOG.md`。
- `data/open-source-projects.csv` 刷新至 09-29 并新增 8 行。

## v1.0 — 2026-09-21

- 初版报告（中英对照）：JEV 官方事实 / 官方主张 vs 独立验证 / 开源生态全景 / 自训开放权重模型 / 选型建议 / 风险与局限。
- 附 5 份原始核实记录与 30 行项目元数据表。
