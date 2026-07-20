# Zotero Import Batch

Screening source: `F:\泉城实验室\二期\论文\异常检测\zotero-workflow\screening\20260710_145443_screening_batch_auto.csv`
Confirmed keep items: 19
Local PDF items queued for MinerU: 19

## Zotero 操作

1. 在 Zotero 中确认集合存在：`异常检测/01_Core_核心证据`。
2. 对 manifest 中有 `file_path` 的本地 PDF，优先以链接附件方式导入或拖入核心集合。
3. 导入后补齐 DOI/标题，并写入 `zotero_tags` 字段中的标签。
4. 外部检索但无本地 PDF 的条目先建元数据条目，后续再补 PDF。

## MinerU 操作

1. 按 `confirmed_keep_mineru_queue.csv` 的 priority 顺序解析 PDF。
2. 每篇解析结果回写 Zotero 子笔记。
3. 关键结论再整理到 `zotero-workflow/evidence-cards/`。

## Files

- Manifest: `F:\泉城实验室\二期\论文\异常检测\zotero-workflow\zotero-import\20260710_151238_confirmed_keep_zotero_manifest.csv`
- MinerU queue: `F:\泉城实验室\二期\论文\异常检测\zotero-workflow\zotero-import\20260710_151238_confirmed_keep_mineru_queue.csv`
