# Zotero 接管异常检测操作 SOP

目标：让 Zotero 成为异常检测文献的主证据库，但保留当前工作区作为流程产物库。

## 当前环境事实

- Zotero 已升级到 9.0.6。
- 当前项目 PDF 库：`F:\泉城实验室\二期\论文\异常检测\paper`
- 当前 PDF 数量：858 篇。
- Zotero 本地 Connector 可用，但 Local API 未启用；因此本 SOP 默认使用 Zotero GUI 操作，不直接改 Zotero 数据库。

## 接管模式

### A. Zotero 完全接管 PDF

适合：希望 Zotero 同步、备份、检索、阅读全部集中管理。

做法：

1. 在 Zotero 建立 `异常检测` 顶层集合。
2. 每批从 `paper/` 拖入 30-50 篇 PDF 到 `00_Inbox_待筛选`。
3. 等待 Zotero 识别元数据。
4. 对无法识别的 PDF，用 DOI 或标题手工补全。
5. 给每篇添加状态标签。

代价：Zotero 会复制 PDF，磁盘占用会增加。

### B. Zotero 管元数据和笔记，PDF 保持项目原路径

适合：当前 `paper/` 已经是项目主数据源，不想复制 858 篇 PDF。

做法：

1. 在 Zotero 偏好设置中设置 Linked Attachment Base Directory 指向：

```text
F:\泉城实验室\二期\论文\异常检测
```

2. 只把核心论文导入 Zotero，非核心 PDF 保留在 `paper/`。
3. Zotero 条目笔记里记录原始 PDF 路径。
4. 筛选后进入核心集合的论文，再视需要复制进 Zotero 存储。

代价：跨机器同步时需要同步项目目录，否则链接附件会失效。

## 推荐选择

当前项目已有 858 篇 PDF，建议采用混合模式：

1. 先保留 `paper/` 作为原始全量库。
2. Zotero 先接管第一批 50 篇核心候选论文。
3. 进入 `01_Core_核心证据` 的论文再存入 Zotero。
4. 被排除论文只保留 Zotero 条目和排除理由，不必复制 PDF。

## 第一次执行步骤

1. 在 Zotero 建立集合树，参考 `../Zotero-Codex异常检测科研流水线.md`。
2. 导入 `screening/20260709_first_batch_seed.md` 中列出的第一批论文。
3. 每篇添加 `ad/status/inbox`。
4. 标题/摘要筛选后，改为：
   - `ad/status/screened`
   - `ad/evidence/must-cite` 或 `ad/evidence/support`
   - 不相关则加 `ad/status/rejected` 并移入 `90_Rejected_排除但留痕`
5. 核心论文完成 Zotero 子笔记。
6. 右键 Zotero 集合，导出 Better BibTeX 到：

```text
F:\泉城实验室\二期\论文\异常检测\zotero-workflow\exports\异常检测.bib
```

7. 用 `04_Codex提示词.md` 生成筛选矩阵和研究简报。

## 每周维护

| 动作 | 频率 | 完成标准 |
|---|---|---|
| Zotero 去重 | 每周 | Duplicate Items 清空或说明保留理由 |
| 元数据修正 | 每批导入后 | 标题、作者、年份、DOI 正确 |
| 标签补齐 | 每次筛选后 | 每篇至少一个 status 标签 |
| 证据卡回写 | 每读完核心论文 | Zotero 子笔记完整 |
| BibTeX 导出 | 每次写作前 | `.bib` 与 Zotero 集合一致 |

## 禁止事项

- 不把 AI 生成的参考文献直接写入论文。
- 不引用没有 Zotero 条目和 citation key 的文献。
- 不把 reject 论文直接删除；应保留排除理由。
- 不一次性批量识别 858 篇 PDF 后再处理，容易产生大量错误元数据。

