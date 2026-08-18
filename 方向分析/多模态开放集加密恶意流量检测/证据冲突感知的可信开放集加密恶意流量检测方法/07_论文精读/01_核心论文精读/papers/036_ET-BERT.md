# 036 ET-BERT：使用预训练 Transformer 的上下文化数据报表示

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| 1 Introduction | 第 3 节 | 已覆盖 |
| 2 Related Work | 第 4 节 | 已覆盖 |
| 3 ET-BERT | 第 5 至 9 节 | 已覆盖 |
| 4 Experiments | 第 10 至 15 节 | 已覆盖 |
| 5 Discussion | 第 16 节 | 已覆盖 |
| 6 Conclusion | 第 17 节 | 已覆盖 |

## 1. 文献身份

- 标题：ET-BERT: A Contextualized Datagram Representation with Pre-training Transformers for Encrypted Traffic Classification。
- 中文题名：ET-BERT：使用预训练 Transformer 的上下文化数据报表示。
- 作者：Xinjie Lin、Gang Xiong、Gaopeng Gou、Zhen Li、Junzheng Shi、Jing Yu。
- 会议：The ACM Web Conference 2022，WWW 2022，页 633–642。
- DOI：10.1145/3485447.3512217。
- arXiv：2202.06335v2，2022-02-19。
- 本地全文：`paper/10.1145_3485447.3512217.pdf`。
- 方法定位：大规模无标签流量预训练的单源原始字节 Transformer；是强闭集表征基线，不是开放集或多模态方法。

## 2. 摘要缩译

加密流量分类需要在看不到明文的条件下识别应用、服务、协议或恶意软件。传统统计特征和监督深度模型依赖人工设计或大量标注，跨场景泛化有限。论文提出 ET-BERT，通过 Datagram2Token 把加密数据报转换成保留传输结构的 token，并设计 Masked BURST Model 与 Same-origin BURST Prediction 两个自监督任务，在约 30 GB 无标签流量上学习通用数据报表示。

预训练模型可用 packet-level 或 flow-level 两种方式微调。论文在跨平台应用、恶意流量、VPN、Tor 和 TLS 1.3 等五类任务上评估，报告多个闭集任务达到当时最优。其贡献主要是密文字节的上下文预训练，不包含未知类拒识。

## 3. 引言缩译

加密使 DPI 无法直接解析 payload。基于包长、到达间隔、证书、域名或统计量的方法可能依赖专家知识和环境字段；直接监督训练字节模型又需要大量标签。作者借鉴 BERT，但指出流量没有自然语言那样清晰的词义，因此要学习的是数据报的传输上下文，而不是明文语义。

ET-BERT 的三个核心设计是：

1. 用 BURST 保留同一会话中连续同方向数据包的结构。
2. 用 MBM 和 SBP 同时学习局部字节上下文与包间来源关系。
3. 用 packet 和 flow 两种微调视图适配不同粒度的闭集分类任务。

## 4. 相关工作缩译

相关方法包括 DPI、统计指纹、传统机器学习、CNN/RNN/图模型和预训练模型。FlowPrint 使用证书等明文字段构建应用指纹；DeepPacket、FS-Net 等从原始包或序列学习；PERT 把 payload 编码为 BERT 输入。

作者认为已有 BERT 式方法没有显式保护同一会话中包的方向转换与 BURST 结构。ET-BERT 不追求恢复明文，而是利用加密实现、协议封装、方向和传输组织中残留的统计模式。

## 5. 模型架构缩译

ET-BERT 采用类似 BERT-base 的编码器：12 个双向 Transformer block，每层 12 个注意力头，hidden dimension 为 768，最大 input tokens 为 512。

预训练阶段输入无标签 flow/BURST，输出数据报级通用表示；微调阶段输入带标签 packet 或 flow，把 `[CLS]` 的最终 hidden state 送入多分类头。所有参数端到端微调。

## 6. Datagram2Token 缩译

### 6.1 Flow 与 BURST

原始 trace 先按五元组切成双向 session flow。BURST 定义为同一 session 中时间相邻、方向一致的一组数据包。方向改变时形成新的 BURST。其结构可写为：

> BURST = {p₁源→目的，…，pₘ源→目的} 或 {p₁目的→源，…，pₙ目的→源}。

作者把 BURST 解释为应用层对象请求和响应在网络侧留下的传输片段。这个解释对 Web 流量较直观，但对 IoT 控制、扫描、DoS 和短恶意流未必成立。

### 6.2 BURST2Token

BURST 的十六进制序列以相邻两个字节组成一个 bi-gram，token 范围为 0 至 65,535；此外加入 `[CLS]`、`[SEP]`、`[PAD]` 和 `[MASK]`。每个 BURST 均分为 A、B 两个 sub-BURST，用 `[SEP]` 分隔并用 segment embedding 区分。

### 6.3 Token2Embedding

最终输入由 token、position 和 segment 三类 embedding 相加：

> E输入 = E词元 + E位置 + E分段。

三者维度均为 768。position embedding 表示传输顺序，segment embedding 表示 sub-BURST A/B；微调时一个 packet 或 flow 作为一个 segment。

## 7. 两个预训练任务缩译

### 7.1 Masked BURST Model

每个 token 以 15% 概率被选中。被选中的 token 有 80% 替换为 `[MASK]`，10% 替换为随机 token，10% 保持不变。模型根据双向上下文恢复原 token：

> L掩码 = −Σᵢ log P(tokenᵢ | X遮蔽；θ)。

该任务学习密文字节与协议结构的局部依赖，不等同于理解明文语义。

### 7.2 Same-origin BURST Prediction

给定 sub-BURST A 与 B，50% 的 B 是同一 BURST 的真实后半段，50% 从其他 BURST 随机抽取。二分类器判断二者是否同源：

> L同源 = −Σⱼ log P(yⱼ | Bⱼ；θ)。

总预训练损失为：

> L预训练 = L掩码 + L同源。

SBP 学习方向一致的传输片段关系，但随机负样本可能过于容易；论文没有报告 hard negative 或同应用异 flow 负样本实验。

## 8. 预训练语料缩译

预训练约使用 30 GB 无标签流量：约 15 GB 来自公开数据集 ISCX-VPN 和 CICIDS2017，约 15 GB 来自 CSTNET 被动采集。语料包含 QUIC、TLS、FTP、HTTP、SSH 等协议。

这一设置带来重要协议问题：ISCX-VPN 同时是下游 ETCV 任务数据源，CSTNET 又与作者自建 TLS 1.3 下游数据来自同一网络环境。论文没有给出预训练 PCAP manifest，也没有证明下游 validation/test flow 在预训练前被排除。因此这些任务属于目标域无标签预训练，甚至存在目标测试样本进入预训练的可能，不能直接视为严格 inductive 泛化。

## 9. 两种微调策略缩译

- `ET-BERT(packet)`：以单个 packet 的数据报字节为输入。
- `ET-BERT(flow)`：把同一 flow 中连续 5 个 packet 拼接为输入。

作者把 flow 版本用于与以 flow 为单位的传统方法比较，把 packet 版本用于更细粒度分类。两种版本的信息量、样本数和拆分单位不同，不能把二者的最高结果混合作为一个统一模型成绩。

## 10. 下游任务和数据集缩译

| 任务 | 数据集 | Flow 数 | Packet 数 | 标签数 |
|---|---|---:|---:|---:|
| 通用加密应用分类 | Cross-Platform iOS | 20,858 | 707,717 | 196 |
| 通用加密应用分类 | Cross-Platform Android | 27,846 | 656,044 | 215 |
| 加密恶意软件分类 | USTC-TFC2016 | 9,853 | 97,115 | 20 |
| VPN 服务分类 | ISCX-VPN-Service | 3,694 | 60,000 | 12 |
| VPN 应用分类 | ISCX-VPN-App | 2,329 | 77,163 | 17 |
| Tor 应用分类 | ISCX-Tor | 3,021 | 80,000 | 16 |
| TLS 1.3 应用分类 | CSTNET-TLS 1.3 | 46,372 | 581,709 | 120 |

USTC-TFC 包含 10 类 benign 应用和 10 类 malware。ISCX-VPN 同时按 service 和 application 两种标签组织。CSTNET-TLS 1.3 来自 2021 年 3–7 月对 Alexa Top-5000 中 120 个 TLS 1.3 应用的采集，并利用当时可见的 SNI 标注。

除 USTC-TFC 外，其余任务主要是应用/服务分类，不是恶意检测。即使类别名称很多，也不能解释为攻击细粒度家族。

## 11. 数据预处理与拆分缩译

作者删除 ARP 和 DHCP 包，删除 Ethernet header、IP header 和 TCP header 中的端口，以减少 IP/端口捷径。微调时每类最多随机选取 500 flows 和 5,000 packets，再按 8:1:1 随机划分 training、validation 和 testing。

论文没有说明先按 flow/capture 划分再抽 packet。若同一 flow 的 packet 被随机分到 training 和 testing，packet 版本会看到高度相似的同会话样本，形成严重 flow leakage。每类 packet 上限又是 flow 上限的 10 倍，packet 与 flow 结果不具备相同样本预算。

## 12. 指标与实现缩译

论文报告 Accuracy、Precision、Recall 和 F1，并明确对各类别指标取 macro average，以降低长尾类别影响。

预训练配置：batch size 32、500,000 steps、learning rate 2 × 10⁻⁵、warmup ratio 0.1。

微调配置：AdamW、10 epochs、flow learning rate 6 × 10⁻⁵、packet learning rate 2 × 10⁻⁵、batch size 32、dropout 0.5。实现使用 PyTorch 1.8.0 和 UER，运行在 NVIDIA Tesla V100S GPU。

论文没有报告随机种子、重复次数、置信区间、early stopping 规则，也没有逐 capture 的划分清单。

## 13. 闭集主结果缩译

### 13.1 ET-BERT 两种粒度结果

| 数据集 | Flow F1 | Packet F1 | 较高者 |
|---|---:|---:|---|
| Cross-Platform iOS | 96.43 | 97.54 | Packet |
| Cross-Platform Android | 92.46 | 92.06 | Flow |
| ISCX-VPN-Service | 97.33 | 98.90 | Packet |
| ISCX-VPN-App | 73.06 | 99.37 | Packet |
| ISCX-Tor | 58.86 | 99.21 | Packet |
| USTC-TFC | 99.30 | 99.16 | Flow |
| CSTNET-TLS 1.3 | 94.26 | 97.41 | Packet |

packet 与 flow 的差距在 ISCX-VPN-App 和 ISCX-Tor 上达到 26.31 和 40.35 个百分点。如此巨大的差异不能只解释为 packet 更细粒度，也与随机 packet split、同 flow 泄漏和样本量差异一致，需要严格 grouped 复现。

### 13.2 与基线比较

ET-BERT 在论文固定协议下多数任务领先 AppScanner、CUMUL、BIND、K-fp、FlowPrint、DF、FS-Net、GraphDApp、TSCRNN、DeepPacket 和 PERT。重要结果包括：

- USTC-TFC：ET-BERT(flow) Macro-F1 99.30%，PERT 99.11%，优势仅 0.19 个百分点。
- ISCX-Tor：ET-BERT(packet) 99.21%，而 flow 仅 58.86%。
- CSTNET-TLS 1.3：packet 97.41%，flow 94.26%，PERT 87.41%。
- Cross-Platform Android：flow 92.46%，packet 92.06%，均没有达到 95%。

USTC-TFC 中部分恶意流量包含未加密应用层数据，作者也承认这会降低任务难度。原文的 SOTA 主张成立于其固定闭集协议，不能外推到严格跨 flow、跨 capture 或开放集场景。

## 14. 消融实验缩译

消融在 ISCX-VPN-App 上进行，每类最多只选 100 packets/flows：

| 变体 | F1 |
|---|---:|
| ET-BERT(packet) 完整模型 | 93.95 |
| 去除 SBP | 89.98 |
| 去除 MBM | 84.62 |
| 去除 BURST，预训练用随机相邻 packet | 92.58 |
| ET-BERT(flow) | 73.87 |
| 分别编码 packet 后再拼接 flow | 69.61 |
| packet 不预训练 | 56.38 |

MBM 的贡献大于 SBP；BURST 相比随机相邻 packet 带来 1.37 个百分点；预训练相对直接监督训练带来 37.57 个百分点。由于消融仍沿用随机 packet 抽样，数值不能消除同 flow 泄漏风险。

## 15. 随机性、密码套件与少样本分析缩译

作者对 AES-GCM、AES-CBC、ChaCha20、ARC4 和 3DES 执行 15 类随机性检验，发现实际密文没有达到理想完全随机。ISCX-VPN、ISCX-Tor 和 USTC-TFC 包含 RC4、3DES 等较弱或波动更明显的密码套件，其分类 F1 接近 100%。这一分析支持模型可能利用密码实现和流量结构残留，但不能证明学到了稳定的应用语义。

少样本实验在 ISCX-VPN-Service 上每类取 500 个样本，再使用 40%、20% 和 10%。ET-BERT(packet) F1 分别为 95.78%、98.33% 和 91.55%。20% 反而高于 40%，说明单次随机抽样波动明显；没有 seeds 和 error bars 时不能给出单调样本效率结论。

## 16. 讨论缩译

作者讨论了两项限制：

- Generalizability：ECH 会隐藏 SNI，导致基于 SNI 的 TLS 1.3 标签失效；可通过主动访问和唯一进程标识辅助标注。
- Pre-training security：预训练依赖干净语料，攻击者可能注入低频 toxic token 形成 backdoor；加密流量中的具体投毒构造尚未研究。

此外，论文把“预测新类别”列为未来工作，反向证明当前 ET-BERT 没有解决开放集未知类别。

## 17. 结论缩译

ET-BERT 通过 BURST tokenization、MBM 与 SBP 在大量无标签流量上学习数据报上下文，再用少量标签适配多个闭集任务。论文证明预训练字节编码器具有较强分类能力，但没有建立 unknown rejection、风险校准或三模态证据融合。

# 第二部分：独立技术分析

## A. 一句话结论

ET-BERT 必须作为 CAEOS 的强字节编码器基线，但其目标域无标签预训练和随机 packet split 使最高结果可能含有跨测试或同 flow 信息；正式复现必须先修复数据协议，再讨论表征优劣。

## B. 协议审计

- closed-set：所有测试标签均出现在监督训练中。
- 预训练重叠：ISCX-VPN 同时用于预训练和下游微调/测试，CSTNET 预训练与 TLS 1.3 下游同环境。
- 预训练 manifest：未公开到 flow/capture 级，无法证明 test exclusion。
- packet split：8:1:1 随机划分，未声明按 flow 分组。
- capture split：未报告。
- 样本预算：每类 5,000 packets 对 500 flows，不等价。
- seeds/statistics：缺失。
- unknown/threshold：完全缺失。
- 协议等级：`P2-target-domain-unlabeled-pretraining/P3-packet-flow-leakage-risk`。
- 可比性：`C1-组件可比`；在重建 split 前不进入 strict-v4 主表。

## C. 是否属于多模态

不属于。packet、flow、BURST 是相同原始字节的不同组织粒度，MBM 与 SBP 是两个预训练目标，不是两个数据模态。模型只有一个 Transformer 编码空间和一个 `[CLS]` 分类表示。

在 CAEOS 三模态架构中，ET-BERT 最合适的位置是 byte/header-payload 分支编码器。流统计和关系上下文仍应由独立编码器产生，并通过可审计的可靠度/冲突机制融合。

## D. 与 YaTC 的关系

- ET-BERT：把相邻双字节视为 token，按 BURST 建模，偏 NLP/BERT 范式。
- YaTC：把固定 header/payload 字节组织成二维 patch，偏视觉 MAE 范式。
- 两者都是单源字节预训练，而不是多模态。
- ET-BERT 保留方向连续的 BURST，YaTC 更明确保护 packet/header/payload 空间边界。

CAEOS 应在相同基础数据、相同 grouped split 和相同拒识头下比较二者，不能直接引用各自论文的 Accuracy 横比。

## E. 对统一预处理的要求

基础数据必须保留 flow ID、packet ID、方向、时间顺序、header/payload 边界和原始字节。ET-BERT 视图可在实验时重新生成 BURST 和 bi-gram token。

删除 Ethernet/IP/port 是基线视图中的反捷径处理，不应不可逆写回基础数据。统一数据应保留原始字段并增加 masked view，使其他基线仍可使用协议头统计，同时保证同一规则可复现。

## F. 三层指标映射

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Macro Accuracy/Precision/Recall/F1 | Known Macro-F1、BA、per-class Recall、Benign FAR | 较强但协议需修复 |
| 未知检测 | 无 | AUROC、AUPR-Out、FPR@95TPR、Unknown-F1 | 缺失 |
| 联合开放集 | 无 | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL | 缺失 |

## G. 95%/5% 安全验收

USTC-TFC 的 closed-set Macro-F1 约 99%，但不能自动认定 CAEOS 已知恶意识别通过：它混合 10 类 benign 应用和 10 类 malware，且 packet/flow 拆分与明文残留存在风险。Cross-Platform Android 和多个 flow 版本本身低于 95%。

原文没有 benign FAR、FPR@95TPR 和 unknown 指标，无法判断误报是否低于 5%。结论只能是“闭集表征强，安全验收未评估”。

## H. CAEOS 采纳与否决

### 采纳

- 采纳 BURST 作为方向连续的传输结构视图。
- 采纳 MBM + SBP 双预训练目标作为字节编码器候选。
- 采纳去 IP/端口的捷径控制。
- 采纳 packet 与 flow 两种粒度分别报告。

### 有条件采纳

- 预训练只能使用 training split 或明确外部 source datasets。
- packet 数据必须按 flow/capture 分组后再划分。
- target-train unlabeled pretraining 可作为半监督附表，不能与 source-only 主表混合。
- 统一拒识头后才能比较 unknown AUROC、FPR95 和 OSCR。

### 不采纳

- 不使用 target test 的无标签流量预训练。
- 不随机拆 packet 后把同 flow 放入 train/test。
- 不混用 packet 和 flow 版本的最佳数字宣称单一模型 SOTA。
- 不把应用分类 F1 写成恶意攻击家族识别能力。
- 不把少样本单次随机结果当作稳定规律。

## I. CAEOS 可执行实验

1. `E-ETBERT-01`：官方 ET-BERT 编码器在 strict-v4 grouped split 上重跑 closed-set。
2. `E-ETBERT-02`：source-only、target-train-unlabeled、target-all-unlabeled 三种预训练边界审计，最后一种只作泄漏上界。
3. `E-ETBERT-03`：packet split 与 flow-grouped packet split 对照，量化同 flow 泄漏增益。
4. `E-ETBERT-04`：MBM-only、SBP-only、MBM+SBP、无预训练消融。
5. `E-ETBERT-05`：ET-BERT 与 YaTC 使用同字节预算、同 seeds、同数据 manifest 比较。
6. `E-ETBERT-06`：固定 ET-BERT encoder，比较 MSP、energy、prototype distance 和 CAEOS evidence-conflict head。
7. `E-ETBERT-07`：加入统计与关系模态，比较 concat、gating 与 conflict-aware fusion。
8. `E-ETBERT-08`：五种 seeds 下报告三层指标、ECE/Brier 与 95%/5% 安全表。

## J. 可引用与不可引用主张

### 可引用

- ET-BERT 使用约 30 GB 无标签流量进行 MBM 与 SBP 预训练。
- 模型通过 BURST 表示同一会话中连续同方向数据包。
- 在原文固定闭集协议下，ET-BERT 在 USTC-TFC 获得约 99.3% Macro-F1。
- 消融中去除预训练使小样本 ISCX-VPN-App F1 从 93.95% 降到 56.38%。
- 作者明确把新类别预测列为未来工作。

### 不可引用

- ET-BERT 已实现未知恶意流量检测。
- ET-BERT 是多模态模型。
- ET-BERT 的 99% 结果已排除同 flow 或预训练测试泄漏。
- ET-BERT 已满足 benign FAR < 5%。
- ET-BERT 所有 flow-level 任务都超过 95%。
- ET-BERT 的少样本性能随样本量单调稳定。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地 WWW PDF 与全文抽取存在
- G2 身份门：通过至 DOI、会议信息和 arXiv，Zotero 待办
- G3 任务门：通过，明确为闭集分类而非开放集
- G4 协议门：通过，`P2-target-domain-unlabeled-pretraining/P3-packet-flow-leakage-risk`
- G5 方法门：通过
- G6 结果门：通过，表 1 至表 5、图 3 至图 5 已核读
- G7 对比门：通过，但仅组件级可比
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
