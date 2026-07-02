# [321] Unveiling malicious DNS behavior profiling and generating benchmark dataset through application layer traffic analysis

## 1. 基本信息

- 编号：321
- 中文题名：通过应用层流量分析揭示恶意 DNS 行为画像并生成基准数据集
- 年份/来源：2024，Computers and Electrical Engineering
- DOI：10.1016/j.compeleceng.2024.109436
- 作者：MohammadMoein Shafi，Arash Habibi Lashkari，Hardhik Mohanty
- PDF：`paper/10.1016_j.compeleceng.2024.109436.pdf`
- 主题关键词：DNS 分析、行为画像、应用层安全、异常检测、模式提取、行为相似度、ALFlowLyzer、BCCC-CIC-Bell-DNS-2024
- 已有分类：数据集、基准、综述与开源工具；二级关联为网络流量监测、测量与工具
- 与当前异常检测方向相关性：弱相关，分数 4
- 正文包状态：未截断
- 本地代码包状态：未发现该论文对应代码

## 2. 中文翻译与核心摘要

这篇论文的核心不是单纯提出一个 DNS 恶意流量分类器，而是把“数据集重构、应用层 DNS 流定义、特征抽取工具、行为画像模型”放在同一条技术链上。作者认为，现有 DNS 数据集往往存在标签粒度、特征覆盖、流定义和数据质量不足的问题，导致后续机器学习或深度学习检测模型即使精度看似较高，也很难支撑可复核、可解释的 DNS 行为分析。

论文首先整合 CIC-Bell-DNS-2021 与 CIC-Bell-DNS-EXF-2021，清洗原始 PCAP，重新以 DNS Flow 为单位生成 CSV，并发布 BCCC-CIC-Bell-DNS-2024。然后提出 ALFlowLyzer，用于从应用层和流统计层抽取 120 余个 DNS/通用流特征。最后，作者构建行为画像模型：先按活动类别建立特征相关图并做特征选择，再用高斯混合模型刻画特征取值范围，用 FP-Growth 抽取范围之间的共现规则，最后通过一个带权重学习的神经网络结构整合多个 profile 完成分类。

论文报告的最终结果较好：五类任务中 Benign、Malware、Spam、Phishing、Exfiltration 的 F1 分数分别为 96.7、98.4、99.1、97.5、98.8，整体准确率声称超过 99%。不过，其贡献更应被理解为“DNS 行为画像与数据集构建框架”，而不只是一个高分分类模型。

## 3. 论文解决的具体问题

论文瞄准的是 DNS 恶意行为检测中的几个实际痛点：DNS 流量常被组织默认放行，攻击者可借 DNS 做 exfiltration、tunneling、amplification、poisoning、hijacking 等活动；传统规则和黑名单方法更新慢、泛化差；普通 ML/DL 方法高度依赖数据集，而公开 DNS 数据集又存在特征不足、标签不一致、粒度不统一、攻击类型覆盖有限等问题。

更具体地说，作者想解决三层问题。第一，数据层面：如何从已有 DNS 数据集中生成一个更干净、更统一、更适合行为建模的基准数据集。第二，表征层面：如何定义 DNS Flow，使每一行样本真正代表应用层 DNS 行为，而不是简单的包级记录或 UDP 五元组流。第三，模型层面：如何用特征分布范围和特征相关关系构造可解释 profile，而不是直接把全量特征扔给黑盒分类器。

## 4. 创新点深度提炼

第一项创新是 DNS Flow 概念。作者没有沿用传统网络层 flow，而是强调 DNS 应用层事务，使用 DNS header 中的 transaction ID 结合网络层基本属性和时间信息来区分 DNS 行为，并通过最大流持续时间和最大 idle time 控制 flow 终止。这一点对 DNS cache poisoning、低速 exfiltration 等行为尤其重要。

第二项创新是 ALFlowLyzer。该工具从 PCAP 中生成应用层 flow CSV，论文中围绕 DNS 提取 lexical、statistical、resource record、third-party、size、delta-length、delta-time、side-based 等特征。它把 DNS 元数据和通用流统计放到同一特征空间，避免只依赖域名字符串或只依赖包长度时间序列。

第三项创新是按活动建立相关图的特征选择。每个 DNS 活动类别都有自己的特征相关图，边权来自相关系数，低权重边被剪掉，再寻找强相关路径作为 profile 特征集。这个思想比全局统一选特征更贴近“不同攻击行为依赖不同特征组合”的假设。

第四项创新是 profile 创建过程。模型不是直接分类，而是先用高斯混合模型估计特征在某活动中的主要取值区间，再用 FP-Growth 抽取不同特征区间之间的共现模式，形成行为规则式 profile。

第五项创新是行为相似度指标。作者用不同活动的特征相关图边权差异来度量行为相似度，并据此发现 CIC-Bell-DNS-EXF-2021 中 audio、video、image、compressed、exe、text 等 exfiltration 子类高度相似，最终合并为 Exfiltration 大类。

## 5. 科学问题与研究假设

论文背后的科学问题可以概括为：DNS 恶意活动是否能通过应用层 flow 的特征分布和特征相关结构被稳定画像？如果可以，那么这种画像是否比普通分类器更可解释、更适合数据集清洗、标签合并和潜在未知攻击识别？

主要研究假设有五个。其一，不同 DNS 活动在单个特征的取值范围上存在可区分行为，例如域名长度、包长均值、发送字节数、TTL 多样性等。其二，不同活动不仅特征值不同，特征之间的相关关系也不同。其三，强相关特征组合比全局重要特征更适合行为 profile 构造。其四，应用层 DNS Flow 比包级或传统流级记录更能表达 DNS 攻击行为。其五，未知或零日 DNS 攻击会偏离已有 profile，或只与多个恶意 profile 局部重叠，因此可被标为 Unknown/Zero-day。

## 6. 科学方法与技术路线

技术路线可以拆成六步：先审视公开 DNS 数据集的不足，再选择 CIC-Bell-DNS-2021 与 CIC-Bell-DNS-EXF-2021 作为整合对象；随后清洗 PCAP，删除与官网/论文描述不一致的文件和格式异常包；接着用 ALFlowLyzer 按 DNS Flow 重新抽取特征并生成 CSV；然后基于原始标签与行为相似度重新整理标签，尤其把多个 exfiltration 文件类型合并为 Exfiltration；之后构建每类活动的相关图，选择 profile 特征，计算取值范围并抽取关联规则；最后用神经网络结构学习各 profile 的权重，输出多分类结果。

这套方法的关键思想是把“行为”拆为两个层次：单特征的有效区间，以及多特征区间之间的共现关系。前者由高斯混合模型捕捉，后者由关联规则捕捉，神经网络只负责整合不同 profile 的贡献权重。

## 7. 实验设计与实验步骤

数据：原始数据来自 CIC-Bell-DNS-2021 和 CIC-Bell-DNS-EXF-2021。新数据集 BCCC-CIC-Bell-DNS-2024 包含 Benign 3,545,212 条 flow，Malware 81,698 条，Spam 30,371 条，Phishing 43,348 条，以及六个 exfiltration 子类共 196,740 条，合计约 3,897,369 条 flow。最终建模时使用 Benign、Malware、Spam、Phishing、Exfiltration 五类。

预处理：检查原始 PCAP 与数据集说明是否一致，删除不匹配文件和格式异常包；用 ALFlowLyzer 重新按 DNS Flow 生成 CSV；每行由包级/域名级改为 flow 级；清理 WHOIS 等第三方特征，因为这些特征存在大量空值，尤其恶意域名缺失更严重，保留可能引入偏差。

模型/基线：作者的模型包含图相关特征选择、MoG 范围计算、FP-Growth 模式抽取、差分进化调参、profile 权重神经网络。对比方法包括 KNN、MLP、Deep NN、CNN、ELM、LSTM、RF+CNN 等，但其中部分方法使用不同数据集，因此对比更像横向参考，不是严格同数据同划分 benchmark。

训练：每类活动独立做特征选择，每类构建两个 profile，每个 profile 四个特征。相关图中低于 0.3 的边被剪除。FP-Growth 的 minimum support 由 Differential Evolution 搜索，优化目标强调提高准确率并降低误报。神经网络部分使用 softmax 输出，损失函数为 categorical cross-entropy，优化器选择 Adagrad。

指标：主表报告 precision、recall、F1-score；比较表报告 accuracy。论文还在参数优化中提到 false positive rate，但没有给出完整 FPR 表、混淆矩阵或每类样本划分细节。

消融/敏感性：论文比较了 Pearson、Spearman、KendallTau 在行为相似度计算中的表现，并声称 Pearson 在准确性与效率上更适合。还提到测试过不同 optimizer，Adagrad 表现较好。但对阈值 0.3、profile 数量、每个 profile 特征数、训练/测试划分等关键设置缺少系统消融。

结果核查：复核时应重点检查三个点：一是 Table 4 中 Malware 第二个 profile 出现 `{F121, F63, F84, F84}`，疑似重复特征或排版错误；二是 exfiltration 子类合并是否会让任务变容易；三是高达 99% 的准确率是否受类别不平衡和同源数据切分影响。

## 8. 关键结果、结论与证据

最直接的结果是五类 DNS 行为的分类性能较高：Benign 的 precision/recall/F1 为 95.5/98.1/96.7，Malware 为 100/97.0/98.4，Spam 为 99.3/99.0/99.1，Phishing 为 96.1/99.1/97.5，Exfiltration 为 99.7/98.1/98.8。说明该 profile 体系对整合后的五类标签有较强区分能力。

第二个重要结论是 exfiltration 的不同文件类型在 DNS 行为上高度相似。论文通过行为相似度和特征分布图发现 audio、video、image、exe、compressed、text 等类别之间难以形成稳定差异，因此合并为 Exfiltration。这是一个值得重视的标签工程结论：原始文件类型标签不一定等价于可观测网络行为类别。

第三个结论是 DNS profiling 不应只看 DNS 专属字段。最终入选特征中大量来自 size、delta-length、side-based 等通用流特征，例如 sending bytes、packet length statistics、delta length、packet rate 等；Exfiltration profile 才明显引入 domain_name_len、character entropy、continuous numeric length、distinct TTL values 等 DNS 元数据特征。这说明恶意 DNS 行为往往由应用语义和流统计共同表达。

## 9. 局限性与待解决问题

第一，实验复现细节不足。论文没有充分说明训练/验证/测试划分方式、随机种子、是否按时间或场景隔离、是否避免同源流泄漏，这会影响 99% 准确率的可信度。

第二，对比实验公平性有限。Table 6 中部分方法使用不同数据集、不同任务设置，二分类与多分类也混在一起，因此不能严格证明该方法全面优于所有 prior works，只能说明在作者实验条件下表现较好。

第三，零日攻击能力更多是概念推导。论文讨论了 Unknown/Zero-day 的判定逻辑，但没有设计真正的 leave-one-attack-out、跨数据集或时间外推实验来验证未知攻击识别能力。

第四，WHOIS 第三方特征被移除是合理的，但也暴露出方法对外部信息完整性的敏感性。若未来重新引入第三方情报，需要处理缺失机制、查询时间漂移、隐私保护和攻击者注册信息伪造问题。

第五，正文包未截断，本次理解覆盖了提供的完整正文；但若用于正式综述或复现实验，仍建议回到 PDF 核查图表细节、Table 4 疑似重复特征、数据集网页说明和 ALFlowLyzer 实际实现。

## 10. 与本项目的关系

对“异常检测”项目而言，这篇论文的相关性偏弱但有方法参考价值。它不是通用异常检测理论论文，而是 DNS 场景下的基准数据集与行为画像工程。若你的项目关注网络流量异常检测、NIDS 数据集构建或应用层协议建模，它的 DNS Flow 定义、特征分层、标签清洗和行为相似度都值得借鉴。

最有迁移价值的是三点：用应用层事务而不是粗粒度五元组定义样本；用“特征范围 + 关联规则”构造可解释 profile；用行为相似度反向检查标签是否真的可区分。这些思想可迁移到 HTTP、TLS、MQTT、工业协议等其他应用层异常检测任务。

## 11. 代码对照分析

本地代码包标注为“未发现；无”，因此不能给出本地目录、关键文件或运行命令的逐文件对应。论文中公开的是 ALFlowLyzer 项目与 BCCC-CIC-Bell-DNS-2024 数据集页面，但本次没有本地源码可读。

按论文方法推断，若后续获取 ALFlowLyzer 源码，应重点找四类模块：PCAP 解析与 DNS transaction ID 聚合模块，对应 DNS Flow 创建；DNS metadata feature extractor，对应 F1-F51；flow statistical feature extractor，对应包长、delta length、delta time、rate 等 F52-F127；CSV writer 或 dataset generation 脚本，对应从原始 PCAP 到 flow-level CSV 的转换。

需要注意，论文的数据可用性声明主要说 ALFlowLyzer 源码公开，并不等价于完整 profiling model 训练代码公开。图相关特征选择、MoG 范围计算、FP-Growth profile 抽取、DE 调参和神经网络权重学习，可能不在 ALFlowLyzer 中，而是作者实验代码的一部分。复现时应把“特征抽取工具”和“论文分类模型实现”分开核查。

## 12. 本篇精华

- 这篇论文的核心贡献是把 DNS 数据集重构、应用层 flow 定义、特征抽取和行为画像建模连成闭环。
- DNS Flow 是全文最实用的概念：用 DNS transaction ID 和网络/时间属性表达应用层 DNS 事务，比包级或普通 UDP flow 更贴近攻击行为。
- 作者认为恶意 DNS 行为由两部分构成：单个特征的取值范围，以及多个特征范围之间的相关共现模式。
- BCCC-CIC-Bell-DNS-2024 本质上是对两个 CIC-Bell 数据集的清洗、重标注和 flow-level 重构，最终五类建模标签包括 Benign、Malware、Spam、Phishing、Exfiltration。
- Exfiltration 子类被合并是重要结论：文件类型标签在 DNS 流量行为上未必可分。
- 最终入选特征不只包含 DNS 字符串特征，很多来自包长、发送字节数、delta length 和 packet rate，说明 DNS 恶意检测不能只做域名词法分析。
- 99% 准确率需要谨慎看待，关键复现点是数据切分、同源流泄漏、类别不平衡和缺失的混淆矩阵。
- 对综述写作而言，它适合归入“DNS 行为画像 + 数据集构建 + 应用层流量特征工程”，而不是单纯深度学习检测模型。

## 13. 建议精读路线

先读 Introduction 和 Related Works 的 synthesis，抓住作者认为现有 DNS 检测与数据集的缺口。然后重点读 Section 4 和 Section 5，因为 DNS Flow、ALFlowLyzer、数据集整合与标签合并是这篇论文最可复用的部分。

第二轮再读 Section 3，尤其是 feature selection、range calculation、pattern extraction 和 neural network structure，理解作者如何把相关图、MoG、FP-Growth、DE 和 Adagrad 串起来。最后读 Section 6 和 Section 7 时不要只看指标，要重点核查 Table 3、Table 4、Fig. 6、Fig. 8、Fig. 9，以及关于 Exfiltration 合并和 zero-day profiling 的论证强度。

<!-- codex-cli-deep-read: complete -->
