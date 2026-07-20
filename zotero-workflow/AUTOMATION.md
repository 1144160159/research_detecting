# Actual Zotero-Codex Research Pipeline

Topic:

```text
加密流量异常检测，重点关注开放集、自监督、多模态和入侵检测。
```

This file is the canonical operating procedure for the local workflow. Zotero is
the evidence store. `zotero-workflow/` is the traceable process log.

## 1. Literature Search

Use `paper-search-mcp` first. Do not ask AI to write a review directly from a
topic prompt.

Recommended sources:

```text
semantic, arxiv, crossref, core, openalex, unpaywall, dblp
```

Default limits:

- at most 3 papers per source
- Semantic Scholar: one request per run
- search output goes to `zotero-workflow/exports/`

Command:

```powershell
.\zotero-workflow\run_pipeline.ps1 -Stage external-search -Run -Sources semantic,arxiv,crossref,core,openalex,unpaywall,dblp
```

Expected output:

```text
zotero-workflow/exports/*_external_search_results.jsonl
zotero-workflow/exports/*_external_search_summary.json
```

## 2. Import Into Zotero

The Zotero collection tree must exist before import:

```text
异常检测/
  00_Inbox_待筛选
  01_Core_核心证据
  02_Method_方法
  03_Datasets_数据集
  04_Surveys_综述
  90_Rejected_排除但留痕
```

Every imported item must have at least one traceability/status tag:

```text
ad/status/inbox
ad/status/screened
ad/status/rejected
ad/evidence/must-cite
```

New search results should enter `00_Inbox_待筛选` with `ad/status/inbox`.
Only screened keep items should enter `01_Core_核心证据`.

## 3. Screening

Screen in batches of 30-50 papers. Do not process the full 858-PDF local corpus
as one screening batch.

Output:

```text
zotero-workflow/screening/*_screening_batch_auto.csv
```

Allowed decisions:

```text
keep, maybe, reject
```

Every reject must include an exclusion reason. The screening matrix is the
authoritative decision log.

## 4. Reading And Parsing

For core papers, use Zotero MinerU Parser or equivalent full-text parsing. The
structured output must be stored as a Zotero note or an evidence card.

Evidence cards go to:

```text
zotero-workflow/evidence-cards/
```

Each evidence card records:

- research question
- method
- dataset
- experimental results
- limitations
- quotable conclusions
- citation key

## 5. Research Brief

After roughly 10 keep/maybe papers have evidence cards, generate a one-page
research brief:

```text
zotero-workflow/briefs/
```

The brief must answer:

- key papers
- disputes and gaps
- technical routes
- recommended reading order

## 6. Topic Selection

Generate 3-5 candidate research directions:

```text
zotero-workflow/ideas/
```

Each direction must include:

- evidence base
- innovation point
- experimental feasibility
- largest risk
- follow-up search questions

## 7. Survey And Manuscript Writing

Build an evidence map before writing prose:

```text
zotero-workflow/surveys/
```

Hard rule:

```text
No Zotero item, no citation key, no evidence card: do not include it in the manuscript.
```

## Current Reconciliation

On 2026-07-10, one minimal batch was imported directly into
`01_Core_核心证据` after user confirmation to auto-promote all remaining
non-keep items to keep. This was useful for bootstrapping but bypassed the
normal Inbox-first path. It has been reconciled by:

- creating the full standard collection tree
- marking all 63 current Core items with `ad/status/screened`
- keeping the screening matrix as the decision log
- recording metadata corrections under `zotero-import/`

Future batches must follow the Inbox-first workflow.
