# [423] Evolving ML-Based Intrusion Detection: Cyber Threat Intelligence for Dynamic Model Updates

## 1. 基本信息

- 论文题名：Evolving ML-Based Intrusion Detection: Cyber Threat Intelligence for Dynamic Model Updates
- 年份：2025
- DOI：10.1109/TMLCN.2025.3564587
- 来源：IEEE Transactions on Machine Learning in Communications and Networking
- 作者：Ying-Dar Lin、Yi-Hsin Lu、Ren-Hung Hwang、Yuan-Cheng Lai、Didik Sudyana、Wei-Bin Lee
- 主题归类：入侵检测与网络异常检测
- 关联方向：网络流量异常检测、CTI 威胁情报、IoC、在线学习、混合机器学习 IDS
- 本地代码状态：未发现论文对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：传统 ML-based IDS 通常依赖离线预训练模型，面对新型攻击、端口混淆、端口跳变等行为变化时，模型更新滞后，容易出现防御空窗。另一方面，现有 CTI 应用多停留在抽取 IoC 并写入黑名单，攻击者可以通过代理、更换端口、行为扰动等方式绕过静态封禁。

作者提出 DICI，即 Dynamic IDS with CTI Integrated。它不是简单把 CTI 当成封禁列表，而是把 CTI 转化为 IDS 的增量训练数据。系统包含两个模型：一个是负责检测网络流量的 IDS Model，另一个是负责解析结构化 CTI 报告并生成训练标签/训练样本的 CTI Transfer Model。IDS 遇到无法明确分类的 outlier 流量时，会提取 IoC，查询 CTI 平台，得到结构化情报报告，再由 CTI Transfer Model 判断该 IoC 更接近良性还是恶意，并回查原始 sighting 流量，把相关流量转化为新的 IDS 训练数据。

实验中，DICI 相比未集成 CTI 的 IDS，F1 从 80.22% 提升到 89.52%，提升 9.29 个百分点。CTI Transfer Model 中使用 ML 方法，相比规则式方法，平均 F1 提升 30.92%。论文由此论证：CTI 的价值不应只停留在黑名单，而应成为 IDS 在线更新的数据来源。

## 3. 论文解决的具体问题

论文针对的是 ML-based IDS 的“模型老化”问题。离线训练的 IDS 在训练集分布固定时效果较好，但真实网络攻击持续变化，新攻击可能在下一次人工更新或周期性重训前已经发生。此时模型对新行为缺少可靠判断，尤其是那些既不像正常流量、又不完全符合旧攻击模式的流量。

第二个问题是 CTI 使用方式过窄。许多研究和工程系统把 CTI 报告中的 IP、域名、hash 等 IoC 抽出来，形成 IoC database 或 blocklist。这种方法部署简单，但语义层次低：它阻断的是“已知标识符”，不是学习“攻击行为”。攻击者只要更换 IP、使用代理、改变端口策略，就可能绕过。

第三个问题是 sighting 与 CTI 没有充分闭环。论文中 sighting 指真实网络观测，例如 NetFlow、系统日志。CTI 是外部威胁知识，sighting 是内部真实流量证据。DICI 试图把二者关联起来：先用 sighting 发现 outlier，再用 CTI 验证 IoC，再回到 sighting 生成训练样本，最终更新 IDS。

## 4. 创新点深度提炼

第一，论文把 CTI 从“封禁资源”提升为“训练数据生成器”。这比传统 IoC 黑名单更有研究意义，因为它让 IDS 学到与攻击相关的流量特征，而不是只记住某个 IP 是否恶意。

第二，提出双模型架构。IDS Model 负责流量检测，CTI Transfer Model 负责情报到训练样本的转换。这个拆分较清晰：前者处理 NetFlow 级别 sighting，后者处理 VirusTotal 等平台返回的结构化 CTI 报告。

第三，IDS Model 使用监督与无监督混合机制。SVM 负责较可靠的已知模式分类，K-means 负责捕捉异常分布。当 SVM 认为良性但 K-means 认为异常时，系统不直接判恶意，而是标记为 outlier，交给 CTI 流程继续分析。这一设计避免了无监督模型高误报直接污染最终告警。

第四，论文显式比较了三种 CTI 利用方式：无 CTI、IoC database、CTI Transfer Model。结果显示 CTI Transfer Model 的 recall 提升明显，说明它更擅长减少漏报。

第五，论文尝试回答结构化 CTI 报告是否适合 ML 解析。实验显示 KMeans++ 明显优于规则式方法，但也发现特征数量并非越多越好，强调 CTI 特征质量比数量更关键。

## 5. 科学问题与研究假设

论文背后的科学问题可以概括为三层。

第一，实时或近实时 CTI 是否能缓解 ML-based IDS 的模型老化？作者的假设是：如果 IDS 能把新出现的 outlier 与 CTI 关联，并把确认后的流量重新纳入训练，则模型可以随威胁演化动态更新。

第二，CTI Transfer Model 是否优于静态 IoC database？作者假设：结构化 CTI 报告包含比单个 IoC 更丰富的上下文，例如安全厂商分析结果、声誉、归属信息、历史分析时间等，因此用模型解析 CTI 并生成训练数据，比简单查黑名单更有效。

第三，ML 是否优于规则式 CTI 分析？作者假设：规则方法依赖固定阈值和专家条件，面对复杂、多源、时间变化的 CTI 报告时适应性不足；ML 能从多个 CTI 属性中学习更灵活的威胁判别模式。

## 6. 科学方法与技术路线

DICI 的技术路线是一个闭环：

1. 网络流量进入 IDS Model。
2. IDS Model 由 SVM 与 K-means 组成，输出 benign、malicious 或 outlier。
3. 对 outlier 流量提取 IoC，论文主要使用源 IP 作为 IoC。
4. 使用 CTI API 查询结构化 CTI 报告，实验中选择 VirusTotal。
5. CTI Transfer Model 解析 CTI 报告，判断 IoC 对应威胁状态。
6. 对被判定为恶意的 IoC 回查 sighting 数据，找到相关 NetFlow 流量。
7. 将这些 sighting 标注为训练样本，积累到阈值后触发 IDS Model 在线更新。
8. CTI Transfer Model 自身也在 CTI 报告累计到阈值后进行在线学习。

关键思想是：outlier 是系统最有价值的学习入口。良性和已知恶意流量，IDS 已有一定识别能力；真正需要 CTI 补强的是模型不确定的边界样本和新型行为。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用两类数据。第一类是 sighting dataset，来自专有威胁情报防火墙采集的 NetFlow，时间范围写为 2023 年 1 月 6 日至 2023 年 6 月 31 日、以及 2023 年 10 月 1 日至 2023 年 10 月 31 日，共约 8 个月，2,774,241 条 flow，137.3 MB。第二类是 CTI dataset，对 sighting 中 IP 通过 VirusTotal API 查询，保存 2,112 份结构化 CTI 报告，48.4 MB。

2. 预处理  
   sighting 数据使用 Nfdump 处理 NetFlow。移除 time_start、time_end、src_ip、dest_ip、src_port 等元数据字段，避免模型直接依赖网络标识符。缺失值通过填补和删除高缺失记录处理。类别变量使用 one-hot 编码，数值特征标准化。类别不平衡通过 undersampling 缓解。CTI 数据同样进行缺失处理、one-hot、标准化和欠采样，并排除 IP 本身作为训练特征。

3. 模型与基线  
   IDS Model：SVM 作为监督分类器，K-means 作为无监督异常检测器。  
   CTI Transfer Model：主要使用 KMeans++，并与 KMeans、rule-based classifier 比较。  
   基线包括：无 CTI 的 ML-based IDS、无 CTI 的 LSTM-based DL IDS、IDS + IoC database、IoC database alone、规则式 CTI 解析。

4. 训练  
   IDS 初始为离线预训练模型，随后在 DICI 中通过 CTI 生成的新 sighting training data 在线更新。CTI Transfer Model 随 CTI 报告积累到阈值后更新。论文还考察 batch size 和 epoch 对在线学习效果的影响。

5. 指标  
   主要指标是 F1 score，同时报告 precision、recall、false positive rate、false negative rate。资源指标包括训练时间、内存占用和 CPU 利用率。

6. 消融与敏感性  
   消融包括：是否集成 CTI、使用 CTI Transfer Model 还是 IoC database、ML CTI 解析还是规则式解析、不同 sighting 类型生成训练数据的效果。敏感性实验包括 CTI 特征数量、batch size、epoch 对 F1 和 loss 的影响。

7. 结果核查  
   核查重点包括：F1 是否随在线迭代稳定提升；outlier-only 是否确实带来最高增益；CTI Transfer Model 是否在 recall 上优于 IoC database；资源开销是否低于 DL baseline；端口混淆和端口跳变案例是否能由 CTI 更新后重新识别。

## 8. 关键结果、结论与证据

最核心结果是 DICI 的 F1 达到 89.52%，未集成 CTI 的离线 ML IDS 为 80.22%，提升 9.29 个百分点。这个结果直接支持论文主张：CTI 作为动态训练来源，可以缓解 IDS 模型老化。

在混合 IDS 内部，SVM 的误报率为 7.70%，漏报率为 4.95%；KMeans 的误报率高达 42.78%，漏报率为 34.69%。这说明 KMeans 单独作为检测器并不理想，但它适合作为 outlier 发现器，把不确定样本交给 CTI 进一步验证。

在 CTI Transfer Model 与 IoC database 对比中，DICI 的 precision 相比 IDS + IoC database 略降约 0.39%，但 recall 提升 12.61%，F1 提升 7.16%。这说明它的主要价值是减少漏报，而不是提高告警纯度。

在 ML 与 DL 对比中，论文使用 LSTM-based IDS 作为 DL baseline。ML-IDS 训练时间 3.22 秒、内存 17.43 MB、CPU 36.6%；DL-IDS 训练时间 59.30 秒、内存 65.14 MB、CPU 79.5%。作者据此认为，在 CTI 增量样本有限、需要快速更新的 IDS 场景下，传统 ML 比 DL 更适合。

CTI Transfer Model 中，KMeans++ 相比 rule-based classifier 平均 F1 提升 30.92%。此外，CTI 特征数量增加并不必然提升 F1，少于 5 个特征时效果差，使用全部约 110 个特征也没有额外收益。论文因此强调 CTI 平台应提升关键特征质量，而不是堆叠字段。

## 9. 局限性与待解决问题

第一，数据不可公开。sighting dataset 来自专有威胁情报防火墙，CTI 报告来自 VirusTotal 本地缓存。论文强调这样做是为了真实 CTI 关联和可重复性，但外部研究者很难完整复现实验。

第二，CTI 来源单一。论文比较了 Shodan、MalwareBazaar、ThreatMiner、GreyNoise、VirusTotal，最后只使用 VirusTotal。这样可以提高实验一致性，但也会引入平台偏差。不同 CTI 平台的判定口径、覆盖范围和更新时间可能差异很大。

第三，源 IP 被作为主要 IoC，表达能力有限。现代攻击常使用代理、NAT、云主机、CDN、短期基础设施，仅依赖 IP 容易出现误判或过期情报问题。论文虽然试图超越黑名单，但触发 CTI 查询的核心仍然依赖 IP。

第四，标签可信度存在传递风险。sighting 初始标签来自防火墙内置机制，CTI 标签来自外部平台，再由 CTI Transfer Model 回灌 IDS。如果 CTI 报告过期或防火墙标签有偏，在线学习可能把错误标签放大。

第五，在线学习的安全性还不充分。攻击者可能通过投毒样本、低频扰动或诱导 CTI 查询污染增量训练集。论文讨论了对抗攻击现实性，但对数据投毒、概念漂移检测、回滚机制、置信度门控等工程问题展开不足。

第六，论文正文包未截断，本次理解基于完整提供文本。但文中仍有若干需要回 PDF 复核的细节，例如“June 31, 2023”这一日期不合法，部分图号叙述与图注存在不一致，表格中的具体字段和超参数细节在正文包中不完全直观。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”强相关，尤其适合支撑本项目中关于动态异常检测、威胁情报增强检测、模型持续更新的部分。

如果本项目关注网络异常检测模型，本篇的启发是：不要只把异常检测模型当作一次性训练器，而应设计“异常样本发现-外部知识验证-训练集更新-模型再训练”的闭环。尤其是 outlier 不应简单计入误报，而可以成为主动学习或情报查询的触发点。

如果本项目关注图学习或知识图谱，这篇论文虽然没有真正构建 CTI 知识图谱，但它提出了 sighting-CTI correlation 的框架。后续可以把 IP、ASN、国家、厂商判定、历史分析、流量行为、攻击技术之间建图，用 GNN 或异构图学习替代 KMeans++，提升跨 IoC 的关联推理能力。

如果本项目希望落地，DICI 更像一个工程框架：流量采集、异常检测、CTI 查询、情报缓存、样本标注、在线更新。它可以作为系统设计章节的重要参考。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法逐文件对应源码实现。根据论文方法，如果复现 DICI，代码目录大概率应拆成以下模块：

- 数据预处理：对应 Nfdump NetFlow 解析、缺失值处理、字段删除、one-hot 编码、标准化、欠采样。可能文件名类似 `preprocess_sighting.py`、`netflow_parser.py`、`feature_engineering.py`。
- CTI 查询与缓存：对应 VirusTotal API 查询、IP 去重、结构化 JSON 保存、查询限额控制、缓存复用。可能文件名类似 `cti_lookup.py`、`virustotal_client.py`、`cti_cache.py`。
- CTI 特征抽取：对应从结构化 CTI 报告中提取 ownership、last analysis、reputation、vendor assessments、country、votes 等特征。可能文件名类似 `cti_features.py`。
- IDS 模型：对应 SVM、KMeans、混合决策逻辑、outlier 生成。可能文件名类似 `ids_model.py`、`hybrid_detector.py`。
- CTI Transfer Model：对应 KMeans++、规则式 baseline、CTI 到 sighting label 的转换。可能文件名类似 `cti_transfer_model.py`。
- 在线学习流程：对应阈值 p、q，批量更新，batch size/epoch 实验。可能文件名类似 `online_update.py`、`train_incremental.py`。
- 评估：对应 F1、precision、recall、FPR、FNR、资源消耗、消融实验、端口混淆/端口跳变案例。可能文件名类似 `evaluate.py`、`ablation.py`、`plot_results.py`。

复现时最关键的运行线索是：先构建 sighting 数据和 CTI 本地缓存，再训练初始 IDS，然后只对 IDS 判为 outlier 的流量触发 CTI Transfer Model，最后把 CTI 验证后的 sighting 回灌 IDS，而不是把所有 CTI 记录直接用于 IDS 训练。

## 12. 本篇精华

1. DICI 的核心不是“用 CTI 查黑名单”，而是“用 CTI 生成 IDS 增量训练数据”。
2. outlier 是系统最有价值的样本入口，能把无监督检测的不确定性转化为 CTI 驱动的主动学习机会。
3. SVM + KMeans 的混合 IDS 设计并不追求 KMeans 单独高精度，而是利用它发现 SVM 覆盖不到的新行为。
4. CTI Transfer Model 相比 IoC database 的主要收益在 recall，说明它更适合补漏报。
5. KMeans++ 解析结构化 CTI 报告显著优于规则方法，但 CTI 特征数量越多不等于效果越好。
6. 在增量样本有限、需要快速更新的 IDS 场景下，传统 ML 可能比 DL 更实用。
7. 论文最大的工程启发是建立 sighting、IoC、CTI、模型更新之间的闭环。
8. 最大短板是数据不可公开、CTI 单源、标签传递误差和在线学习安全性仍未充分解决。

## 13. 建议精读路线

建议先读 Introduction 和 Problem Formulation，抓住论文真正要解决的“静态 IDS 防御空窗”与“CTI 黑名单化使用不足”两个矛盾。

第二步读 Figure 1、Figure 2、Figure 3 附近内容，重点理解 sighting、outlier、IoC、CTI report、CTI Transfer Model、IDS online update 之间的数据流。

第三步读 Implementation，特别是 IDS Model 的混合决策规则。这里决定了为什么 outlier 会触发 CTI，而不是直接判恶意。

第四步读 Results，按三个问题整理：CTI 是否提升 IDS、CTI Transfer Model 是否优于 IoC database、ML 是否优于规则式 CTI 处理。

最后回看局限：数据私有、VirusTotal 单源、IP-IoC 依赖、在线学习投毒风险。这些点正适合作为综述中的批判性分析或后续研究切入点。

<!-- codex-cli-deep-read: complete -->
