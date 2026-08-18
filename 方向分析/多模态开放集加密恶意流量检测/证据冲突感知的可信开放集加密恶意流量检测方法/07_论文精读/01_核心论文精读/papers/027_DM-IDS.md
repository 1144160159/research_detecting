# 027 DM-IDS：基于流特征与载荷字节双模态融合的网络入侵检测

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | PDF页 | 本卡 | 状态 |
|---|---:|---|---|
| Abstract / Introduction / Related Work | 1-4 | 第1-3节 | 已覆盖 |
| Dataset / Beeman / Architecture | 4-8 | 第4-6节 | 已覆盖 |
| Experiments / Zero-Day / Ablation | 8-14 | 第7-9节 | 已覆盖 |
| Discussion / Conclusion | 14 | 第10节 | 已覆盖 |

## 1. 身份与摘要缩译

作者为 Chao Zha、Zhiyu Wang、Yifei Fan、Bing Bai、Yinjie Zhang、Sainan Shi 和 Ruyun Zhang，发表于 IEEE TNSM 22(4)，2025，DOI 10.1109/TNSM.2025.3565614。

DM-IDS 从同一 PCAP/flow 中提取约 80 个流特征与前 128/256 bytes payload，分别用 attention-based FlowNet 和 convolutional PayloadNet 编码，再做 bilinear fusion。作者开发 C++ 多线程工具 Beeman 生成双视图，并在 CICIDS2017 和 CICIoT2023 上做已知攻击和“zero-day”留出实验。

## 2. 引言与相关工作缩译

流统计可扩展但对 payload 内攻击不敏感；payload 能揭示内容模式却在加密或内容弱区分攻击上失效。早期融合可能放大噪声，决策级 late fusion 又忽略跨视图交互。论文因此用双分支独立编码后做双线性交互。

## 3. Beeman 与预处理缩译

Beeman 以多线程 C++ 解析原始 PCAP，生成流向量 Vᶠ 和载荷向量 Vᵖ。payload 每字节转换成 8-bit binary 表示，形成 8 channels；超过长度截断，不足补齐，实验主要使用 256 bytes。双视图来自相同原始流，具备样本级对齐，属于同源双视图。

作者批评随机比例拆分会导致收敛过快和同源泄漏，采用按 timestamp 排序的前 70% 训练、后 30% 测试。该做法优于随机行拆分，但没有独立 validation，也未说明跨 PCAP/capture group 隔离。

## 4. 模型缩译

FlowNet 用多头注意力提取约 80 维统计序列中的全局关系；PayloadNet 用多个并行卷积块从 8-channel binary payload 中抽取局部模式。双线性融合显式计算两分支特征的乘性交互，再经分类器和交叉熵训练：

L꜀ₑ = −∑ᵢ yᵢ log pᵢ

论文与 concatenation、attention fusion 比较，认为 bilinear fusion 对两视图的选择偏置更小。

## 5. 数据与任务缩译

CICIDS2017 含 PCAP 和多种良性/攻击流；CICIoT2023 含大规模 IoT 攻击。论文为两个数据集建立不同 known/unknown settings。unknown 选择原则是与 known 攻击机制相似但细类不同，或机制显著不同。测试时只要留出类被判断为任意 attack 就算正确，不要求输出独立 unknown 标签或发现新类。

## 6. 结果缩译

CICIDS2017 多个已知类 recall 接近或超过 99%。与 flow-only 比较，加入 payload 对 FTP-Patator、DoS-Slowloris、DDoS、Bot、Brute-Force 和 Portscan 等类改善明显。推理延迟分解中 FlowNet 多在 0-10 微秒，PayloadNet 因高维载荷更慢，Fusion 多低于 1 微秒，总延迟估计不超过 60 微秒。

## 7. Zero-day 结果缩译

CICIoT2023 Setting 1 的 7 个留出攻击 recall 均高于 84%，其中 3 个超过 90%。Setting 2 更困难：3 类高于 87%，4 类约 50%，其余 3 类低于 50%。双视图优于 flow-only，但这种“留出类仍判 attack”是二元泛化，不是已知多类＋unknown 拒识的 OSR。

## 8. 消融与局限缩译

论文比较 128/256 payload bytes、flow-only、payload-only、concatenation、attention 和 bilinear fusion。双线性通常最好，但 payload 的收益依赖数据是否发布原始内容；对于 TLS 应用载荷，加密后字节语义与 CIC 明文/协议内容不同。作者承认 SSL-encrypted traffic 仍是主要挑战，未来需更有效可加密特征和真实部署。

## 9. 结论缩译

DM-IDS 是与 CAEOS 数据基础最直接的双视图工程参考：它证明同一流的 flow statistics 和 payload bytes 可统一生成、独立编码、再融合；但原任务与 strict OSR 不一致。

# 第二部分：独立技术分析

## A. 协议、模态与状态

- 角色：B-同源双视图直接基线；状态：`project_mapped`。
- 本地 PDF：`paper/10.1109_TNSM.2025.3565614.pdf`。
- 协议：`P3-binary-held-out-attack-without-frozen-unknown-threshold`。
- 多模态：payload bytes＋flow statistics，样本级对齐，属于真实同源双视图；尚缺独立 packet sequence 第三视图。
- G10：pending。

## B. 95%/5%与采纳

已知类部分结果超过 95%，但困难 Setting 2 多个 unknown attack recall 低于 50%，不能满足统一验收。论文没有 unknown AUROC/AUPR/FPR95、OSCR、Benign FAR 和校准。

采纳 Beeman 的“单次解析、双视图同流对齐”和 bilinear fusion 作为基线；不减少 CAEOS 当前的包数、字节数或特征，仅在实验读取阶段选择相同预算做公平对照。`E-DMIDS-01` 用统一基础 CSV/bytes 建立 flow-only、payload-only、sequence-only、bilinear 双视图和 CAEOS 三模态，strict-v4、5 seeds、六主指标。

## C. 最终审计

- G0-G1、G3-G9：通过。
- G2：DOI 已核，Zotero 待核。
- G10：未通过；最终状态 `project_mapped`。
