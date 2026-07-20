# Zotero Workflow for Anomaly Detection

本目录保存 Zotero-Codex 科研流水线的中间产物。Zotero 是文献证据库，本目录是流程记录库。

## 目录职责

| 路径 | 用途 |
|---|---|
| `exports/` | Zotero / Better BibTeX 导出的 `.bib`、`.csv`、检索结果 |
| `briefs/` | 主题简报、研究问题简报、组会简报 |
| `screening/` | 文献筛选矩阵、排除理由、批次记录 |
| `evidence-cards/` | 从 Zotero 核心论文抽取出的证据卡 |
| `ideas/` | 选题脑暴、研究问题评估、风险清单 |
| `surveys/` | 综述提纲、证据地图、综述草稿 |
| `prompts/` | 可复用 Codex 提示词 |

## 文件命名

```text
YYYYMMDD_阶段_主题.md
YYYYMMDD_screening_batchNN.csv
YYYYMMDD_evidence_map_主题.md
```

示例：

```text
20260709_research-brief_Evidence-OpenEMTD.md
20260709_idea-brainstorm_DA-FDIDS.md
20260709_screening_batch01.csv
```

## 每个产物必须包含

- `Zotero Collection`
- `Evidence Scope`
- `Input Files`
- `Output Decision`
- `Zotero Writeback`
- `Next Step`

## 起步文件

- [Zotero 接管操作 SOP](00_Zotero接管操作SOP.md)
- [第一批 Zotero 接管种子文献](screening/20260709_first_batch_seed.md)
- [科研工具接入清单](06_科研工具接入清单.md)
- [自动化流水线说明](AUTOMATION.md)

## 自动化入口

当前自动化主题：加密流量异常检测，重点关注开放集、自监督、多模态和入侵检测。

默认只做 dry-run，不扫描全文、不发起网络检索、不写 Zotero：

```powershell
.\zotero-workflow\run_pipeline.ps1 -Stage init
.\zotero-workflow\run_pipeline.ps1 -Stage local-index
.\zotero-workflow\run_pipeline.ps1 -Stage external-search
```

明确加 `-Run` 后才执行真实工作：

```powershell
.\zotero-workflow\run_pipeline.ps1 -Stage local-index -Run -Limit 50
.\zotero-workflow\run_pipeline.ps1 -Stage external-search -Run -Sources semantic,arxiv,crossref,core,openalex,unpaywall,dblp
.\zotero-workflow\run_pipeline.ps1 -Stage merge-screen -Run
```

外部检索结果保存到 `exports/`，并同步一份兼容副本到 `external-search/`。每个来源最多 3 篇；Semantic Scholar 每次运行最多 1 次请求，并保留限速等待策略。

Zotero 写入只允许在筛选矩阵确认后执行：

```powershell
.\zotero-workflow\run_pipeline.ps1 -Stage zotero-batch -Run
.\zotero-workflow\run_pipeline.ps1 -Stage zotero-import -Run
```

不得跳过 `screening/` 中的 keep/maybe/reject 留痕。例外情况必须记录到阶段产物登记表。

## 阶段门

| 阶段 | 进入条件 | 退出条件 |
|---|---|---|
| 检索 | 有明确主题和关键词 | 结果进入 Zotero Inbox，并保留检索式 |
| 筛选 | 有 Zotero Inbox 批次 | 每篇论文有 keep/maybe/reject 和理由 |
| 阅读和解析 | 核心论文已进入 Zotero | MinerU/全文解析结果进入 Zotero 笔记或 `evidence-cards/` |
| 证据卡 | 有 Zotero 条目、citation key 和全文/摘要 | 每篇记录研究问题、方法、数据集、实验结果、限制、可引用结论 |
| 简报 | 至少 10 篇 keep/maybe 且有证据卡 | 形成一页主题地图和阅读顺序 |
| 选题 | 有主题简报 | 3-5 个候选问题，每个有证据和风险 |
| 综述 | 核心文献有证据卡 | 章节提纲中的每个断言有文献支撑 |
| 写作 | 有提纲和证据地图 | 草稿引用键全部可在 Zotero 找到 |

## 硬规则

- 没有 Zotero 条目的内容，不进入正文。
- 没有 citation key 的内容，不进入正文。
- 没有证据卡的内容，不进入正文。
- reject 必须保留排除理由，并进入 `90_Rejected_排除但留痕` 或筛选矩阵。
