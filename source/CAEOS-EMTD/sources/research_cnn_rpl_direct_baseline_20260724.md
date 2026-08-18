# CNN-RPL direct-baseline admission audit

更新时间：2026-07-24

## 结论

CNN-RPL 是 2024 年 IEEE Access 的直接 DDoS 开放集识别工作，论文身份、官方全文、损失、主要网络结构、训练种子和两套原始数据源均已核验；GPU 上 CICIDS2017 与 CICDDoS2019 原始候选覆盖为 `2/2`。它应进入直接领域相关工作，并保留为原生外部协议候选。

当前不能执行、计数或进入 strict-v4 主表。作者实现未验证；GitHub 唯一同名仓库是 2026 年的非作者学生项目，实际使用 Passive Aggressive、Random Forest 和 Decision Tree，并把 CNN 写成未来增强，不是论文的 7 个 Conv1D、二维嵌入 CNN-RPL。论文没有发布确定的输入特征顺序、缩放/插补/过滤流程、完整 pooling 参数、MultiStepLR milestones/gamma 或预处理数据 manifest。

更关键的是，论文固定 `lambda=0.3`、阈值 `0.7`，并明确写明这些值为优化未知识别而选择且可随未知分布调整，却没有记录独立 known-only validation。该选择边界不能证明 unknown/test 零参与。已有 ARPL 表格适配器只能代表 RPL 方法族，不能改名为 CNN-RPL 复现；按图猜预处理再复用 ARPL 也不能增加正式方法数。

## 官方身份与全文

- 题名：Open-Set Recognition in Unknown DDoS Attacks Detection With Reciprocal Points Learning
- 作者：Chin-Shiuh Shieh、Fu-An Ho、Mong-Fong Horng、Thanh-Tuan Nguyen、Prasun Chakrabarti
- 期刊：IEEE Access 12, 56461-56476 (2024)
- DOI：`10.1109/ACCESS.2024.3388149`
- IEEE document：`10497567`
- DBLP key：`journals/access/ShiehHHNC24`
- 官方 PDF SHA256：`fb3816fc94bf39fee75507f33d5750eed6764500f9367e9d8720062af2715421`
- 抽取文本 SHA256：`742a68797b9e494279ce9005d9e74f4726f5a29a7fbdf00682efa8cce07ebfc5`

## 可验证方法契约

论文图和参数表可确认：

1. 7 个 Conv1D 运算、3 次 MaxPool、卷积后 PReLU。
2. Flatten 后映射为二维 deep feature，并输出 6 个 known 类。
3. 总参数量为 18,872。
4. 损失为 `L = Lc + lambda * Lo`。
5. 未知分数由二维特征到类中心的指数距离函数产生。
6. 训练为 100 epoch、学习率 0.003、batch 512、Adam、MultiStepLR。
7. 固定 10 个种子：`0,42,123,222,419,844,918,1344,65536,815149`。
8. 论文给出 80:20 train/test 比例。

当前不可唯一重建：

1. 输入特征的精确 75/80 维映射、列顺序、删列规则。
2. 缺失/无穷值、缩放、异常值与类别不均衡处理。
3. 全部 pooling stride/padding 与 MultiStepLR milestones/gamma。
4. Table 2 数量到官方 CSV 行的确定映射和 checksum。
5. `lambda=0.3` 与阈值 `0.7` 的独立 known-only 选择过程。
6. capture/session group-disjoint 拆分。

## 数据覆盖

GPU 路径：

- CICIDS2017：`/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cicids2017/raw`
- CICDDoS2019：`/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CICDDoS2019`

已核验：

- CICIDS2017 `MachineLearningCSV.zip` 包含 Wednesday 与 Friday-DDoS CSV。
- Wednesday PCAP：13,420,789,612 字节。
- Friday PCAP：8,839,309,056 字节。
- CICDDoS2019 `CSV-01-12.zip` 包含 LDAP、MSSQL、DNS、NetBIOS、NTP、UDP、SNMP、SSDP、SYN。
- 两个 CICDDoS2019 CSV ZIP 均存在，大小分别为 2,330,434,641 与 918,815,761 字节。

这证明源数据候选齐全，不证明论文预处理数据身份闭合。

## 代码检索与排除

GitHub repository API 结果：

| 查询 | 结果数 |
|---|---:|
| `3388149` | 0 |
| 完整标题 | 1 |
| `"CNN-RPL" DDoS` | 0 |

唯一同名仓库固定在 commit `a4c352624707a76bf8ad921b6e9210b67b513238`。仓库作者不在论文作者表，代码没有 PyTorch、Conv1D 或 reciprocal-point loss；Flask 入口使用 sklearn 的 Passive Aggressive、Random Forest、Decision Tree，并以随机 70/30 拆分训练。README 把 CNN/RNN 列为 future enhancements。该仓库只能作为同名误识别的反证，不能作为作者实现。

## strict-v4 准入

| 层次 | 决策 | 原因 |
|---|---|---|
| 论文身份与全文 | 准入 | IEEE PDF、DBLP、DOI一致 |
| 直接领域相关工作 | 准入 | DDoS、flow-level、OSR、RPL均直接相关 |
| 原生外部协议数据 | 条件准入 | 两套原始源齐全，但预处理manifest缺失 |
| 原生执行 | 不准入 | 作者代码、精确预处理和调度参数不完整 |
| strict-v4主表 | 不准入 | unknown-informed阈值风险、无group split、指标不全 |
| ARPL改名为CNN-RPL | 禁止 | 方法族相关不等于论文实现 |
| 正式方法增量 | 0 | 未生成本地模型指标 |

重新准入至少需要作者实现或精确输入规范、预处理 manifest、known-only 阈值选择、完整调度参数、组不相交拆分及 strict-v4 六指标。

机器证据位于 `results/strict_v4_cnn_rpl_direct_baseline_audit/`。

## 机器证据

- evidence canonical：`a507519581cab87c9dcde2c5eaafe9f13fd75df36de86abba11b3775b1603194`
- evidence file：`cba1234947ea8ca3da9752ffd3c492d6e9fe95764b11d60d0ea29a132a60093a`
- audit canonical：`933429d49416249848616ef30d7ae3ae77f664f7f2e11dc24b7066f8b8b62c72`
- audit file：`4b8b6ffdfd348aa5391dc94fdd959713d330075432f9631d09eb1f082a6c072a`
- auditor SHA：`b58c9ce2a7350f29f7e8c022d9518a9e044d5ab9f83b911e2f94e3b572490a32`
- test SHA：`654d9dc5fede013cb70810667fdd77e5c441f6a42c344a49935c2f43c6137236`
- 本地/GPU真实工件重算：`8/8 PASS`
- `native_execution_admitted=false`
- `strict_v4_main_table_admitted=false`
- `native_external_protocol_data_ready=true`
- `baseline_count_increment=0`
