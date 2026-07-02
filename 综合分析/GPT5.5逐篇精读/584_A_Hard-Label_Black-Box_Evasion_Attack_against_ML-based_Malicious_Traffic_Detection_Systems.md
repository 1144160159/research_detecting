# [584] A Hard-Label Black-Box Evasion Attack against ML-based Malicious Traffic Detection Systems

## 1. 基本信息

- 编号：584
- 题名：A Hard-Label Black-Box Evasion Attack against ML-based Malicious Traffic Detection Systems
- 中文题名：面向机器学习恶意流量检测系统的硬标签黑盒逃逸攻击
- 年份：2026
- 来源：NDSS 2026
- DOI：10.14722/ndss.2026.230916
- 作者机构：清华大学、北京理工大学、中关村实验室
- 主题归类：恶意流量检测、对抗样本、黑盒攻击、强化学习、流量伪装
- 本地 PDF：`paper/10.14722_ndss.2026.230916.pdf`
- 正文包：`综合分析_data/full_text_cache_plain/584.txt`
- 代码包状态：本地未发现该论文对应开源代码；论文正文中声称源码位于 `https://github.com/09nat/NetMasquerade`

## 2. 中文翻译与核心摘要

这篇论文研究一个很现实的问题：攻击者不知道检测模型结构、参数、训练数据、特征提取器，只能通过“流量是否被放行/阻断”得到硬标签反馈，是否仍能构造可用的恶意流量逃逸样本。

作者提出 NetMasquerade。它不是直接在特征空间里改几个数，而是在真实网络流量空间里修改包序列，主要操作包括调整包间隔、插入无功能的 chaff packet，并尽量保持攻击原本功能不变。方法分两阶段：第一阶段用公开 benign 流量训练 Traffic-BERT，学习良性流量中包大小序列和包间时延序列的联合模式；第二阶段用强化学习决定“改哪个位置、插入哪个位置”，再让 Traffic-BERT 填补被 mask 的包级特征，使恶意流量逐步靠近良性流量分布。

论文的核心结论是：现有基于统计模式的 ML 恶意流量检测器，即使声称对已有扰动具有经验鲁棒性或认证鲁棒性，在硬标签黑盒设定下仍可被高成功率逃逸。作者在 6 类检测系统、12 种攻击流量上评估，报告 NetMasquerade 平均 ASR 高于 96.65%，多数场景只需要不超过 10 步修改，并能达到较低在线生成延迟。

## 3. 论文解决的具体问题

论文瞄准的是“真实攻击者能否逃逸 ML 流量检测系统”这一问题，而不是常见的理想化白盒对抗样本问题。

具体约束包括：

1. 攻击者没有目标模型内部知识：不知道模型类型、参数、训练数据、特征工程。
2. 攻击者只有硬标签反馈：通过探测流量是否收到回包，推断流量是否被 IDS/IPS 放行。
3. 攻击必须在流量空间成立：不能只修改离线特征向量，必须能转化为真实包序列。
4. 攻击要跨协议、跨任务：不能依赖 Tor、隧道、加密协议、特定审查系统等特殊前提。
5. 修改不能破坏恶意功能：例如 DoS 仍要维持速率，payload 型攻击不能改变有效载荷语义。
6. 修改开销要小：过多包级扰动会改变带宽、时序和流结构，反而可能被检测。

这使论文问题比传统 adversarial ML 更接近网络安全实战：攻击者面对的是一个闭源、在线、只返回动作结果的检测系统。

## 4. 创新点深度提炼

第一，论文把 ML 恶意流量检测逃逸问题推进到“硬标签黑盒”设定。已有不少方法要么依赖白盒梯度，要么依赖训练集、特征提取器或模型转移性；NetMasquerade 只依赖放行/阻断信号，现实性更强。

第二，作者提出 Traffic-BERT，用良性流量预训练来形成“良性流量模式先验”。它不只是把 BERT 套到流量上，而是针对包大小和 IPD 两个异构序列设计了双向交叉注意力，使模型能同时捕获单一特征内部依赖和 size-IPD 之间的联合关系。

第三，NetMasquerade 把逃逸流量生成建模为有限时域 MDP。每一步动作只决定修改或插入一个包级位置，Traffic-BERT 负责生成良性化的具体特征值，RL 负责找到最有效的最少修改位置。这种分工避免了让 RL 直接在巨大连续/离散空间里搜索完整包序列。

第四，奖励函数不仅看逃逸成功，还显式加入 dissimilarity penalty 和 effectiveness penalty。前者迫使模型少改、快改；后者保证攻击功能，特别是 DoS 场景中的速率不被削弱。

第五，论文强调流量空间攻击对特征空间防御的绕过能力。NetMasquerade 的小规模包级操作，映射到目标检测器特征空间后可能形成大幅特征变化，因此 Lp 范数约束、随机平滑等特征空间鲁棒性方法并不天然有效。

## 5. 科学问题与研究假设

核心科学问题可以表述为：

> 在仅有硬标签反馈且无目标模型知识的条件下，是否可以利用公开良性流量先验，把恶意流量变换为足够接近良性分布、同时保持恶意功能的真实网络流量？

论文建立了几个关键假设：

1. 许多 ML 流量检测器主要依赖统计模式，例如包大小、包间时延、流级分布特征，而不检查 payload。
2. 良性流量分布比恶意流量更稠密，攻击者可以把恶意流量向良性 manifold 迁移。
3. 公开良性流量虽然不同于目标系统训练数据，但仍包含可迁移的互联网背景流量模式。
4. 在线检测系统的放行/阻断行为可被攻击者间接观测，例如 TCP 回包、UDP/QUIC 响应、ICMP unreachable、TTL/IPID 侧信道。
5. 只修改时序或插入无效包，可以在多数场景中保留攻击语义。
6. 目标检测边界在训练/探测期间近似静态，否则 RL 学到的策略会失效或收敛变慢。

其中第 6 点尤其关键：论文后续防御建议也指出，引入推理随机性可能扩大攻击者搜索空间。

## 6. 科学方法与技术路线

技术路线分为两个阶段。

第一阶段是良性流量模式学习。作者从 MAWI 公开骨干网流量中抽取良性流，使用包大小和 IPD 两类序列作为基础表示。由于流长呈长尾分布，短流 padding，长流 chunking。包大小直接离散化为 token，超过 MTU 的归为 `[UNK]`；IPD 先取 log10，再按区间散列为 token。随后训练 Traffic-BERT，通过 Mask-Fill 任务恢复被 mask 的包大小和 IPD token。

Traffic-BERT 的核心结构是在 self-attention 后加入 bi-cross attention。包大小序列和 IPD 序列先分别学习内部上下文，再互相作为 query/key/value 的来源进行跨特征融合。这样模型不只知道“某个包大小是否常见”，还学习“某种包大小与前后时延组合是否像真实良性流”。

第二阶段是对抗流量生成。恶意流被表示为状态 `s=(P,H)`，即包大小序列和 IPD 序列。动作空间包括修改某个已有包的 IPD，或在某个位置插入 chaff packet。策略网络采用 GRU，优化算法是 SAC。每一步策略网络选择位置，Traffic-BERT 填补 mask，系统把生成流量发给目标检测器探测，依据是否放行计算奖励。

奖励由三部分组成：逃逸收益 `rE`、修改惩罚 `rD`、攻击有效性惩罚/约束 `rM`。训练时通过真实反馈更新策略；推理时如果没有实时反馈，则用 Q-network 估计终止条件，避免无限修改。

## 7. 实验设计与实验步骤

可复核流程如下。

1. 数据准备  
   良性背景流量来自 MAWI Samplepoint-F，主要使用 2023 年 6 月数据训练 Traffic-BERT；部分目标检测器训练需要补充 benign 流量时使用 2023 年 8 月 MAWI，以避免与 Traffic-BERT 训练集重合。恶意流量包括 4 大类 12 种：OS Scan、Fuzz Scan、SSDP DoS、SYN DoS、Mirai、Zeus、Storm、Waledac、Webshell、XSS、CSRF、Spam。

2. 预处理  
   对流提取包大小序列和包间时延序列。短流 padding 到固定长度，长流滑窗 chunking。IPD 取对数后离散成 token；包大小按 MTU 范围离散，异常超大包归入 `[UNK]`。Traffic-BERT 默认固定长度 `n=512`。

3. 良性模型训练  
   使用 MAWI 良性流训练 Traffic-BERT。训练任务是双序列 Mask-Fill：随机选择 15% 位置，同时 mask 包大小和 IPD，其中 80% 替换为 `[MASK]`，10% 随机 token，10% 保持不变。

4. 目标检测系统训练  
   评估 6 个检测器：Whisper、FlowLens、NetBeacon、Vanilla feature + RNN、CICFlowMeter + MLP、Kitsune。它们覆盖频域特征、分布特征、树模型、RNN、MLP、自编码器等不同范式。论文先报告无逃逸时 AUC 和 F1，确认目标检测器本身性能较强。

5. 对抗训练  
   对每个目标系统和攻击类型，NetMasquerade 用硬标签反馈训练 RL 策略。策略网络选择修改/插入位置，Traffic-BERT 生成具体良性化特征，DPDK worker 发包并收集反馈。训练目标是高 ASR、少步数、低功能损失。

6. 基线对比  
   Baseline 包括 Random Mutation、Mutate-and-Inject、Traffic Manipulator、Amoeba。前两者代表传统扰动，Traffic Manipulator 代表灰盒 adversarial traffic 方法，Amoeba 代表黑盒 RL 型规避网络审查方法。

7. 指标  
   检测器性能使用 AUC 和 F1；攻击性能使用 ASR。额外评估带宽分布、KL divergence、吞吐 PPS、训练收敛速度、探测预算、噪声反馈鲁棒性。

8. 消融与敏感性  
   消融包括只保留 Traffic-BERT 随机选位置、只保留 RL 但用随机/均值填充替代 Traffic-BERT。敏感性包括最大修改步数 `τ`、Q-value 终止阈值 `ξ'`、探测预算、反馈噪声比例。

9. 结果核查  
   重点核查三点：NetMasquerade 是否在大多数场景 ASR 最高；是否不超过 10 步即可接近最优逃逸；是否保持 DoS 带宽分布相近。论文给出 SSDP Flood 和 SYN DoS 的 KL divergence 分别约为 0.009 和 0.013，支持“攻击功能未显著削弱”的说法。

## 8. 关键结果、结论与证据

最重要结果是 NetMasquerade 对 6 个检测系统均取得高 ASR。论文报告平均 ASR 分别约为 Whisper 0.9878、FlowLens 0.9717、NetBeacon 0.9809、Vanilla 0.9782、CICFlowMeter+MLP 0.9626、Kitsune 0.991。相比最佳 baseline，提升幅度在不同检测器上从约 2.61% 到 21.88% 不等。

第二个结果是修改量小。作者把最大修改步数控制在不超过 10。Figure 7 显示，在复杂场景 FlowLens/Zeus 中，10 步内能接近有反馈情况下的理想 ASR。过高的修改步数不一定更好，因为策略可能在高阈值下做过度修改。

第三个结果是攻击功能保持较好。对 SSDP Flood 和 SYN DoS，作者比较原始与对抗流量带宽分布，KL divergence 很小，说明 NetMasquerade 没有明显削弱高率攻击，也没有引入易观察的时延伪影。

第四个结果是训练和推理效率可接受。Traffic-BERT 离线预训练约 75 小时；在线 RL 阶段通常约 1 小时收敛。推理吞吐上，NetMasquerade 比 Traffic Manipulator 平均快约 69.6 倍，并且比 Amoeba 更适合长流场景。

第五个结果是对有限探测和噪声反馈有一定鲁棒性。在 200、500、1000 probe 预算下，ASR 快速上升；反馈噪声为 5% 时 ASR 平均下降约 0.063，30% 噪声下性能下降但没有完全崩溃。

第六个结果是现有认证防御不足。针对 BARS 的实验显示，NetMasquerade 仍能保持高 ASR。原因是 BARS 认证的是特征空间扰动边界，而 NetMasquerade 在流量空间插包/改时序后，投影到特征空间可能超出其认证范围。

## 9. 局限性与待解决问题

第一，威胁模型依赖可探测硬标签反馈。论文给出了 TCP/UDP/ICMP/侧信道获取反馈的路径，但真实部署中，云防护、NAT、负载均衡、限速策略和非确定性丢包都可能让反馈更混杂。

第二，目标模型静态边界假设较强。如果防御方引入随机模型、动态阈值、流级速率限制或主动欺骗反馈，RL 策略的收敛速度和可迁移性可能明显下降。

第三，攻击功能约束还不够通用。论文对 DoS 用速率作为 effectiveness penalty，对 payload 型攻击则认为不改 payload 即可保持有效，但真实协议状态、服务端解析、会话时序、TLS/QUIC 行为可能对插包和时延更敏感。

第四，Traffic-BERT 只建模包大小和 IPD。许多检测器还可能结合方向、burst、五元组上下文、连接状态、TLS 指纹、DNS/HTTP 元数据、跨流图结构。NetMasquerade 对这些更丰富特征的逃逸能力仍需扩展验证。

第五，实验场景数存在口径需要复核。正文声称 80 个 attack scenarios，但主表按 6 个检测器 × 12 种攻击更接近 72 个场景，另有 BARS 防御实验。这个统计口径在科研引用时应回到 PDF 表格和实验说明确认。

第六，代码本地未发现，复现实验存在障碍。论文虽给出 GitHub 地址，但当前本地代码包缺失，因此无法核查实现细节、默认参数、数据划分脚本、DPDK 发包逻辑和 baseline 适配是否完全一致。

本次正文包未截断，因此上述理解不受正文缺失影响；但若要用于正式综述或复现实验，仍建议回到 PDF 对图表、公式编号和附录表格做一次人工校对。

## 10. 与本项目的关系

这篇论文与“异常检测/恶意流量检测”项目强相关，因为它直接挑战了基于统计特征和深度学习的流量异常检测器的鲁棒性。

对本项目的启发有三点：

1. 仅追求 AUC/F1 不够。论文中 6 个检测器无逃逸时性能都很高，但在黑盒逃逸下 ASR 仍接近饱和。
2. 需要从流量空间做鲁棒性评估。特征空间扰动不能代表真实攻击者能做什么，也不能覆盖插包、延迟、分片、错误序列号等网络层操作。
3. 防御设计应考虑动态性和跨流上下文。若模型只依赖单流包大小/IPD，很容易被良性模式迁移攻击；结合协议状态、跨流关系、主动随机化和 traffic-space adversarial training 可能更有效。

如果本项目正在做恶意流量检测模型，NetMasquerade 可以作为“强黑盒逃逸威胁模型”的参考；如果本项目正在做鲁棒异常检测，它可以作为反例基准，用来说明现有模型在真实可执行扰动下的脆弱性。

## 11. 代码对照分析

本地未发现该论文代码包，因此不能给出本地文件级映射。根据论文方法，若复现 NetMasquerade，代码目录大概率应包含以下模块：

- 数据预处理  
  可能对应 `data/`、`preprocess/`、`feature_extraction/`。功能包括 pcap/flow 解析、流长统计、padding/chunking、包大小 token 化、IPD log 离散化、MAWI benign 过滤、Kitsune/PeerRush/HyperVision 数据适配。

- Traffic-BERT 模型  
  可能对应 `models/traffic_bert.py`、`bert.py`、`tokenizer.py`。关键实现应包括 token embedding、position embedding、self-attention、bi-cross attention、Mask-Fill head、双序列同步 mask 策略、可选 constrained decoding。

- 强化学习攻击器  
  可能对应 `rl/agent.py`、`sac.py`、`policy.py`、`q_network.py`、`environment.py`。核心应包括 GRU policy network、double Q-network、SAC 更新、invalid action masking、reward 计算、Q-value 推理终止条件。

- 流量还原与发包  
  论文提到 Python 生成 adversarial flow 后通过 socket 交给 Intel DPDK worker。可能存在 `dpdk/`、`packet_sender/`、`runtime/`、`worker.c`。关键是按 Traffic-BERT/RL 输出恢复包时间戳、插入 chaff packet、保持 payload 或生成同尺寸无效 payload，并用 TSC busy-wait 控制微秒级间隔。

- 目标检测器适配  
  可能对应 `detectors/whisper/`、`detectors/flowlens/`、`detectors/netbeacon/`、`detectors/kitsune/`、`baselines/`。应包含检测器训练、阈值选择、AUC/F1 计算、ASR 评估。

- baseline 复现  
  可能对应 `baselines/random_mutation.py`、`mutate_inject.py`、`traffic_manipulator/`、`amoeba/`。需要核查是否重新训练、是否统一修改步数、是否处理非法包大小。

由于本地无代码，当前只能建立“论文方法到潜在源码模块”的对应关系，不能确认真实仓库结构、运行命令或依赖文件。

## 12. 本篇精华

1. NetMasquerade 把恶意流量逃逸推进到硬标签黑盒设定，只依赖放行/阻断反馈，比白盒/灰盒对抗样本更接近现实。
2. Traffic-BERT 的价值在于学习良性流量的包大小-IPD 联合分布，为 RL 提供可迁移的 benign prior。
3. RL 不直接生成完整流量，而是选择最值得修改或插入的位置；具体 token 由 Traffic-BERT 填充，显著缩小搜索空间。
4. 攻击目标不是“特征像良性”这么简单，而是在逃逸、少改、保持攻击功能之间做多目标优化。
5. 现有高 AUC/F1 恶意流量检测器在流量空间对抗下仍高度脆弱，论文报告平均 ASR 超过 96.65%。
6. 特征空间认证鲁棒性无法自然覆盖插包和时序扰动，防御需要转向 traffic-space certification 或 traffic-space adversarial training。
7. 对实际部署而言，限制探测反馈、引入动态决策边界、融合协议状态和跨流上下文，可能比单纯增强特征模型更关键。
8. 论文的最大复现风险在于本地代码缺失和实验口径细节，尤其是 DPDK 发包、目标检测器重训、baseline 公平性和场景数统计。

## 13. 建议精读路线

第一遍先读 Introduction、Threat Model 和 Overview，抓住论文为什么强调 hard-label black-box，以及它和 Traffic Manipulator、Amoeba 的区别。

第二遍重点读 Section IV 和 V。Section IV 关注 Traffic-BERT 如何把网络流量变成 token 序列，尤其是 flow padding/chunking、IPD 离散化、bi-cross attention。Section V 关注 MDP 定义、动作空间、奖励函数和 SAC 训练流程。

第三遍读 Evaluation。建议先看 Table IV 确认目标检测器本身有效，再看 Table II 比较 ASR，随后看 Figure 7、8、10、11 理解修改步数、功能保持、探测预算和噪声反馈。

第四遍读 Appendix D 的消融实验。这里最能说明两个阶段为什么都必要：只有 Traffic-BERT 不会选关键位置，只有 RL 又缺少稳定有效的良性填充机制。

最后再读防御讨论。可把它整理成项目里的鲁棒性设计 checklist：是否只做特征空间鲁棒性、是否有流量空间扰动评估、是否依赖静态阈值、是否能抵抗少量插包和时延扰动。

<!-- codex-cli-deep-read: complete -->
