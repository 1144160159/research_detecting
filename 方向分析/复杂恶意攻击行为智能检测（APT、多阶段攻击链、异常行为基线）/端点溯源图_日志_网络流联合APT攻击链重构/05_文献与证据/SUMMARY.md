# 论文筛选与补充摘要

## 2026-07-29：Log2vec

- 候选：1 篇；纳入：1 篇；排除：0 篇。
- 第一阶段相关性评分：9/10。论文直接处理企业日志中的内部威胁与 APT，方法包含异构图构建、关系感知图嵌入以及无需攻击样本的聚类检测。
- 第二阶段全文核验：通过。PDF 共 18 页，题名、作者、CCS 2019 会议信息和 DOI `10.1145/3319535.3363224` 一致。
- 项目定位：作为“日志关系编码/异构图表示/无监督检测”基线或候选组件；不能直接支撑“端点溯源图—日志—网络流概率对齐”和“可校准攻击链证据重构”的核心创新。
- 本地文件：`paper/10.1145_3319535.3363224.pdf`。
- 完整性：SHA-256 `F2710D4CFCB2C6CAE530B7DB3C0832734958C0DC8D88914F6EAD3F6912C70EF3`。
- 当前本地 `paper/` 共 890 个 PDF；`papers_enriched.json` 尚未重建。

## 2026-07-29：第二轮定向扩充（34 篇）

- 本轮围绕“端点溯源图 + 审计/应用日志 + 网络流 + APT 攻击链重构”完成 36 篇候选论文的逐篇筛选：34 篇取得可验证全文并完成 PDF 头、页数、标题与 SHA-256 校验；另 2 篇未取得可验证全文。
- 本地 `paper/` 中 PDF 总量由 890 篇增至 924 篇，临时 `.part` 文件为 0。本轮只增加论文资料，未向 GPU 服务器数据集目录写入论文。
- 本轮新增来源构成：四大安全顶会 29 篇，IEEE TDSC 1 篇，USENIX ATC 1 篇，ACM Computing Surveys 1 篇，ACSAC 1 篇，ACM REP 1 篇。
- 结合原有论文，当前与本方向直接相关的核心池为 71 篇，其中四大安全顶会或 IEEE TIFS/TDSC 论文 65 篇。

### 可直接进入方案设计的组件

- 多源日志融合与因果对齐：ALchemist、ALASTOR、CLARION、Dossier。
- 溯源依赖压缩、攻击因果筛选与图缩减：Dependence-Preserving Data Compaction、MCI、ProTracer、Winnower、PrioTracker、RAIN、MPI、NodeMerge、High-Fidelity Reduction、PalanTír。
- 审计可信性与对抗鲁棒性：CUSTOS、Logging to the Danger Zone、MARSARA、HardLog、OMNILOG、PROVNINJA。
- 在线检测、查询和攻击链重构：SAQL、PAGODA、DeepCASE、AIQL、Hopper。
- 评测边界与复现要求：On the Forensic Validity of Approximated Audit Logs、Sometimes Simpler is Better、Reproducibility of Provenance-based Intrusion Detection Systems。

### 尚未取得可验证全文

- P-Gaussian（IEEE TDSC，DOI `10.1109/TDSC.2019.2960353`）：Unpaywall 核验为非开放获取，本轮未下载。
- PIDS Survey（ACM Computing Surveys，DOI `10.1145/3539605`）：Unpaywall 标注可开放获取，但出版商端点返回 403，且未找到可验证的作者版 PDF，因此保留为“元数据已核验、全文未取得”。

### 追踪边界

- 全部逐篇状态以 `papers-reviewed.json` 为准，来源、页数和 SHA-256 以 `补充顶会顶刊PDF下载清单_20260729.md` 为准。
- `papers_enriched.json` 仍是此前 858 篇快照，本轮未重建；在重建索引前不得把它作为 924 篇现状统计依据。

## 2026-07-29：71篇全文精读与蓝图修订

- 完成 71/71 篇核心论文全文精读，共核验 1239 页；71 份 PDF 的文本页覆盖率均为 1.0。
- 每篇均登记问题、方法、数据/切分、基线、指标、主要证据、复现状态、内部/外部/构念/统计有效性边界和至少三个页码定位。
- 精读后将论文中心问题收紧为“跨源候选边在歧义条件下的校准、最小充分证据子图和可信拒绝”，不把多源、GNN 或 ATT&CK 本身作为创新。
- 横向移动边新增硬约束：认证/登录会话和网络流共同支持；仅 IP、五元组或成功登录只能形成候选。
- 端到端复现被提升为论文 P0 门；复杂 GNN 与图压缩后置，合成数据只用于压力和失败边界。
- 交付位于 `08_论文精读/`：逐篇证据卡、71篇总表、方法组件综合、指标与实验标准、精读后蓝图修订说明。
