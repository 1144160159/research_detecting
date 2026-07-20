# Zotero-Codex 异常检测科研流水线

本文档把当前“异常检测”项目改造成一条可追溯科研流水线：Zotero 保存证据，Codex 运行流程，当前工作区保存每一步可复查产物。

## 核心分工

| 组件 | 负责什么 | 不负责什么 |
|---|---|---|
| Zotero | 文献条目、PDF、附件、标签、笔记、引用键、阅读状态 | 不承载长篇流程推理和多轮任务记录 |
| Codex | 检索、筛选、证据抽取、选题批判、综述组织、交付物生成 | 不作为长期文献库 |
| 本工作区 | 简报、筛选矩阵、证据卡、综述提纲、实验记录、论文草稿 | 不替代 Zotero 的文献元数据 |

一句话规则：**Zotero 存证据，Codex 跑流程，工作区留中间产物。**

## Zotero 集合结构

在 Zotero 中建立顶层集合：

```text
异常检测
  00_Inbox_待筛选
  01_Core_核心证据
    Evidence-OpenEMTD_可信开放集加密恶意流量检测
    DA-FDIDS_AI驱动网络流量检测
  02_Methods_方法谱系
    MTS_多变量时序异常检测
    Graph_图异常检测
    OpenSet_OOD_开放集与未知攻击检测
    EncryptedTraffic_加密恶意流量检测
    IDS_NIDS_网络入侵检测
    XAI_可信解释与可验证性
    Multimodal_多模态融合
  03_Datasets_Benchmarks
  04_Reproduction_Code
  05_Writing_Cited
  90_Rejected_排除但留痕
```

当前 `paper/` 下已有 858 篇 PDF。建议先导入到 `00_Inbox_待筛选`，不要一次性要求 AI 读完。每一批 30-50 篇，筛完再进核心集合。

## 标签体系

Zotero 标签用稳定前缀，避免后期混乱。

| 标签类型 | 示例 |
|---|---|
| 阅读状态 | `ad/status/inbox`, `ad/status/screened`, `ad/status/read`, `ad/status/extracted`, `ad/status/cited` |
| 证据角色 | `ad/role/survey`, `ad/role/baseline`, `ad/role/method`, `ad/role/dataset`, `ad/role/metric`, `ad/role/threat-model` |
| 研究方向 | `ad/domain/encrypted-traffic`, `ad/domain/network-ids`, `ad/domain/time-series`, `ad/domain/graph`, `ad/domain/open-set`, `ad/domain/multimodal` |
| 证据强度 | `ad/evidence/must-cite`, `ad/evidence/support`, `ad/evidence/contrast`, `ad/evidence/gap` |
| 风险标记 | `ad/risk/dataset-leakage`, `ad/risk/weak-baseline`, `ad/risk/no-code`, `ad/risk/unclear-metric`, `ad/risk/small-sample` |

## Zotero 条目笔记模板

每篇核心论文至少保留一条 Zotero 子笔记：

```markdown
# Evidence Card

Citation Key:
Research Line: Evidence-OpenEMTD / DA-FDIDS / Survey / Other
Decision: keep / maybe / reject

## 1. 研究问题

## 2. 方法贡献

## 3. 数据集与实验设置

## 4. 指标与主要结果

## 5. 可引用证据
- 原文结论：
- 可支撑本文哪个论点：

## 6. 局限与风险
- 数据集：
- 基线：
- 泛化：
- 复现：

## 7. 与本项目关系
- 可进入章节：
- 可支撑图表：
- 是否必须引用：
```

## 本地工作区产物

所有 Codex 产物放入 `zotero-workflow/` 或对应专题目录。每个产物必须写清楚：

```text
输入 Zotero 集合：
输入文献范围：
排除标准：
输出文件：
回写 Zotero 的标签/笔记：
下一步动作：
```

## 推荐最小链路

1. Zotero 建集合与标签，导入 `paper/` 的第一批 PDF。
2. 在 Zotero 中完成标题/摘要级筛选，给每篇打 `keep/maybe/reject`。
3. 导出 Better BibTeX 到 `zotero-workflow/exports/异常检测.bib`。
4. 用 `paper-search-mcp` 补充公开来源候选论文，并保存检索结果。
5. 用筛选类 skills 生成筛选矩阵和排除理由。
6. Codex 基于 `.bib`、已有 `文献.md`、专题目录生成研究简报。
7. Codex 生成 3-5 个候选选题，每个选题必须列依据文献和风险。
8. Codex 以审稿人视角检查研究问题、证据缺口和章节结构。
9. 综述草稿只允许引用 Zotero 中已标为 `ad/status/extracted` 或 `ad/status/cited` 的文献。
10. 完成每一步后，把结论回写到 Zotero 条目笔记或集合笔记。

已安装工具与 skills 见：`zotero-workflow/06_科研工具接入清单.md`。

## 批量导入建议

不要直接一次性让 Zotero 识别 858 篇。建议：

1. 每批 30-50 篇导入。
2. 先按题名/摘要筛选，保留核心论文再做全文元数据修正。
3. 对 DOI 文件名的 PDF，优先用 DOI 补全元数据。
4. 元数据不完整的 PDF 暂放 `00_Inbox_待筛选`，不要混入核心集合。
5. 对明显无关论文，放入 `90_Rejected_排除但留痕`，保留排除理由。

## 交付规则

论文正文中的每个关键断言至少对应一个 Zotero 条目或证据卡。禁止出现“AI 说某论文如何”但 Zotero 中找不到条目、笔记和引用键的情况。
