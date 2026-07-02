# [037] Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization

## 1. 基本信息

- 编号：037
- 题名：Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization
- 作者：Iman Sharafaldin, Arash Habibi Lashkari, Ali A. Ghorbani
- 年份：2018
- DOI：10.5220/0006639801080116
- 来源：ICISSP 2018
- 主题归类：入侵检测与网络异常检测；数据集、基准、综述与开源工具
- 核心对象：CICIDS2017 数据集的生成、攻击流量刻画、特征选择与机器学习基线评估
- 本地代码状态：未发现该论文对应本地开源代码包

## 2. 中文翻译与核心摘要

这篇论文的核心不是提出一个新的检测模型，而是试图回答“入侵检测研究到底应当用什么样的数据集来评估”这个更基础的问题。作者认为，DARPA98、KDD99、DEFCON、CAIDA、Kyoto、ISCX2012、ADFA 等常用数据集存在过时、流量单一、攻击类型不足、匿名化过重、缺少完整特征和元数据等问题，因此很难支撑现代 IDS/IPS 的可靠评估。

论文的直接产出是 CICIDS2017：一个在受控但尽量贴近真实网络的测试床中采集的入侵检测数据集。它包含正常流量和多类攻击流量，覆盖 Brute Force、Heartbleed、Botnet、DoS、DDoS、Web Attack、Infiltration、PortScan 等场景。作者使用 CICFlowMeter 从 pcap 中提取 80 多个基于网络流的统计特征，并用机器学习方法分析不同攻击类别的有效特征组合。

这篇文章的价值主要体现在两个层面：第一，它把“数据集质量”本身作为科学对象，提出并对照 11 个评估维度；第二，它为后续大量 CICIDS2017 相关异常检测论文提供了数据来源和初始基线。

## 3. 论文解决的具体问题

论文要解决的具体问题可以拆成三层：

第一，现有 IDS 数据集不能充分代表现代网络环境。许多经典数据集来源于上世纪末或早期网络环境，协议、系统、攻击工具和正常用户行为都已经明显过时。尤其是 HTTPS、现代 Web 攻击、Botnet、DDoS、横向扫描等行为，在老数据集中覆盖不足或缺失。

第二，缺少可复现、可公开、带标签、带特征的综合基准。真实企业流量往往因隐私和合规原因不能公开；公开数据集又经常被高度匿名化，导致 payload、协议、地址关系、元数据被破坏，影响 IDS 方法的真实评价。

第三，异常检测论文常把模型指标当作主要贡献，却忽略了数据集偏差。作者关注的是：如果数据集本身缺少流量多样性、攻击多样性、完整交互和准确标签，那么再高的 Precision、Recall、F1 也可能只是对数据集伪规律的拟合。

## 4. 创新点深度提炼

1. 从“模型驱动”转向“基准驱动”。论文没有追求复杂模型，而是强调可靠数据集是异常检测研究的前提。这对 IDS 领域很重要，因为模型评估高度依赖数据分布。

2. 用 11 个维度系统审视 IDS 数据集：Attack Diversity、Anonymity、Available Protocols、Complete Capture、Complete Interaction、Complete Network Configuration、Complete Traffic、Feature Set、Heterogeneity、Labelling、Metadata。这个框架让“数据集是否可靠”从主观判断变成较结构化的评价。

3. 构建了双网络测试床：Attack-Network 与 Victim-Network 分离，Victim-Network 中包含防火墙、路由器、交换机、域控、不同 Windows/Linux/Mac 主机，并通过镜像端口完整采集流量。这比只在单机或 honeypot 上采集更接近真实网络。

4. 引入 B-Profile 生成正常用户行为。作者试图用用户画像代理生成 HTTP、HTTPS、FTP、SSH、Email 等正常流量，使背景流量不只是静态脚本或重复请求。

5. 同时发布 pcap 与 flow-level CSV 特征。对研究者而言，这降低了使用门槛：既可以直接用特征表做机器学习，也可以回到原始流量重新提取特征或研究协议行为。

6. 不只生成数据集，还做了攻击类别的特征刻画。论文用 RandomForestRegressor 估计不同攻击类别下的重要特征，例如 DoS 与 Flow IAT、Flow Duration 相关，Brute Force 与 Initial Window Bytes 和 TCP flags 相关。

## 5. 科学问题与研究假设

核心科学问题是：怎样构造一个足够可靠的 IDS 评估数据集，使其既能公开共享，又能覆盖现代网络中的正常行为和典型攻击行为？

论文隐含了几个研究假设：

- 如果测试床包含多操作系统、多服务、多协议和真实攻击工具，那么采集到的数据会比传统模拟数据更适合 IDS 评估。
- 如果正常流量由用户画像驱动，而不是简单脚本重复生成，那么误报评估会更可信。
- 如果数据集覆盖完整网络交互、完整采集、准确标签和元数据，那么它能缓解旧数据集不可复现、不可解释的问题。
- 不同攻击族在 flow-level 统计特征上存在可区分模式，因此可以用特征重要性分析得到每类攻击的关键检测线索。
- 常见机器学习模型在该数据集上应能形成合理基线，从而证明数据集具备可学习性和可评价性。

## 6. 科学方法与技术路线

论文采用的是“数据集工程 + 流量特征工程 + 机器学习基线评估”的路线。

首先，作者回顾并批判 1998 到 2016 年间 11 个公开 IDS 数据集，指出它们在流量多样性、攻击覆盖、匿名化、标签、元数据和协议覆盖方面的不足。

其次，构建实验网络。Victim-Network 模拟受害企业网络，包含服务器、工作站、防火墙、交换机、路由器、域控和多种操作系统；Attack-Network 独立部署攻击机，主要使用 Kali 与 Windows 主机发起攻击。

再次，生成正常与攻击流量。正常流量由 B-Profile 代理根据 25 个用户的抽象行为生成；攻击流量按日程执行，包括 FTP/SSH 暴力破解、Slowloris/Slowhttptest/Hulk/GoldenEye、Heartbleed、Web Brute Force、XSS、SQL Injection、Infiltration、Botnet、DDoS 和多种 Nmap PortScan。

最后，用 CICFlowMeter 提取 80 多个网络流特征，进行特征选择和机器学习评估。模型包括 KNN、Random Forest、ID3、AdaBoost、MLP、Naive Bayes、QDA，指标包括 Precision、Recall、F1 和执行时间。

## 7. 实验设计与实验步骤

1. 数据：采集周期为 2017 年 7 月 3 日星期一 09:00 到 7 月 7 日星期五 17:00。星期一只有正常流量；星期二到星期五分时段执行 Brute Force、DoS、Heartbleed、Web Attack、Infiltration、Botnet、DDoS、PortScan 等攻击。

2. 预处理：通过 Victim-Network 主交换机镜像端口完整抓包，得到 pcap；再用 CICFlowMeter 按 SourceIP、SourcePort、DestinationIP、DestinationPort、Protocol 定义 flow，并提取 80 多个统计特征。

3. 标签：按照攻击执行日程和攻击时间窗口对 flow 进行标注。标签粒度包括 Benign 以及各类攻击，如 FTP-Patator、SSH-Patator、DoS Hulk、DoS GoldenEye、DoS Slowloris、Heartbleed、Web Attack、Infiltration、Bot、DDoS、PortScan 等。

4. 模型/基线：使用七个传统机器学习算法作为基线：KNN、RF、ID3、AdaBoost、MLP、Naive Bayes、QDA。论文重点不是调参，而是证明数据集可用于多模型评估。

5. 训练：先用 RandomForestRegressor 计算特征重要性，再结合不同类别上特征均值的标准化差异，得到每类攻击的短特征集合；之后用选中特征训练和测试不同分类器。

6. 指标：使用 Precision、Recall、F1 三个分类指标，并报告训练测试执行时间。论文采用加权平均形式汇总多类别结果。

7. 消融/敏感性：论文没有做严格意义上的消融实验，也没有系统分析训练集比例、类别不平衡、时间切分、随机种子、参数变化对结果的影响。比较接近“敏感性分析”的部分是按攻击类别列出关键特征，但仍不等同于完整消融。

8. 结果核查：作者用 11 个数据集质量维度与历史数据集对照，声称 CICIDS2017 覆盖完整网络配置、完整流量、标签、完整交互、完整捕获、常见协议、攻击多样性、异构性、特征集和元数据等要求。

## 8. 关键结果、结论与证据

论文最重要的结论是：CICIDS2017 相比旧数据集更适合作为现代 IDS 评估基准，因为它同时覆盖真实化测试床、多协议正常流量、多类攻击、完整抓包、flow 特征、标签和元数据。

特征层面的结论包括：

- DoS 类攻击的重要特征集中在 Flow IAT、Flow Duration、Fwd IAT、Backward Packet Length 等时间间隔和包长度统计上。
- Heartbleed 与 Flow Duration、Subflow Fwd/Bwd Bytes、Backward Packet Length Std 等特征相关。
- FTP/SSH Brute Force 与 Init Win Fwd Bytes、ACK/PSH/SYN flags、Fwd Packets/s 等特征相关。
- Web Attack 与 Init Window Bytes、Subflow Fwd Bytes、Total Length of Fwd Packets 等前向流量特征相关。
- Infiltration、Bot、PortScan、DDoS 分别表现出不同的流量长度、方向性、包速率和标志位特征组合。

模型结果方面，ID3 的 F1 约为 0.98，RF 的 F1 约为 0.97，KNN 的 F1 约为 0.96。考虑执行时间，RF 仅约 74.39 秒，明显快于 KNN 的 1908.23 秒，因此作者认为 Random Forest 在准确率和效率之间最优。Naive Bayes 的 Recall 和 F1 很低，说明简单独立性假设不适合该特征分布。

## 9. 局限性与待解决问题

第一，数据仍然是实验室生成，不是真实企业生产网长期采集。虽然测试床较完整，但用户行为、组织业务、资产规模和攻击者策略仍然经过人工设计，不能等同于真实互联网攻防环境。

第二，标签依赖攻击时间表。按时间窗口标注在数据集生成阶段很常见，但如果正常流量与攻击流量高度同步，模型可能学到时间段、主机、端口或工具痕迹，而不是真正泛化的攻击语义。

第三，攻击覆盖仍有限。论文声称覆盖常见攻击族，但没有覆盖后来更常见的云环境攻击、加密恶意流量、横向移动高级持续威胁、供应链攻击、C2 隐蔽通信、IoT 攻击等。

第四，机器学习评估比较初步。论文没有详细说明训练/测试划分方式、类别分布、参数设置、随机种子、交叉验证、时间外泛化测试，也没有报告混淆矩阵。因此模型指标更适合作为初始基线，而非最终性能结论。

第五，特征选择方法存在解释风险。RandomForestRegressor 用于类别相关特征排序可以提供经验线索，但如果没有独立测试和消融验证，不能证明这些特征就是攻击本质特征。

第六，正文包未截断，本次理解覆盖了提供的完整正文内容；但若用于正式综述或复现实验，仍建议回到 PDF 核查表格排版、图 1 网络拓扑细节、表 5 比较项以及数据集外部说明文档。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，尤其适合作为数据集与基准章节的核心文献。它可以支撑以下论述：

- CICIDS2017 为什么成为后续网络异常检测研究的常用数据集。
- 传统 IDS 数据集从 DARPA/KDD 到 CICIDS2017 的演化逻辑。
- 网络异常检测中“数据集偏差”比模型选择更基础。
- flow-level 特征工程在深度学习兴起前后的持续价值。
- 使用 CICIDS2017 时需要警惕时间切分、主机泄露、类别不平衡和工具指纹等问题。

如果本项目要做模型实验，CICIDS2017 可以作为基准数据集之一，但不宜只报告随机划分下的高准确率。更有价值的做法是按日期、攻击族或主机进行更严格划分，检验模型能否跨时间、跨攻击、跨环境泛化。

## 11. 代码对照分析

本地代码包状态为“未发现；无”，因此没有该论文作者方法的本地源码可逐文件复核。不过论文中可以明确对应出若干实现线索：

- 数据采集：对应 pcap 抓包流程，关键不是模型代码，而是测试床、镜像端口、攻击执行脚本和时间表。
- 数据预处理：最可能对应 CICFlowMeter。论文明确使用 CICFlowMeter 从 pcap 提取 80 多个 flow 特征，并输出 CSV。
- 标签生成：应对应按日期和攻击时间窗口合并 flow 与 label 的脚本或人工规则。论文提到详细攻击时间会在数据集文档中发布。
- 攻击执行：部分攻击使用公开工具，如 Patator、Slowloris、Slowhttptest、Hulk、GoldenEye、Heartleech、Metasploit、Ares、LOIC、Nmap；Web Attack 自动化使用 Selenium 代码。
- 特征选择：对应 scikit-learn 的 RandomForestRegressor，流程是计算特征重要性，再结合各类别标准化均值差异形成每类攻击的特征权重。
- 模型训练与评估：对应 scikit-learn 中 KNN、Random Forest、ID3/决策树、AdaBoost、MLP、Naive Bayes、QDA 的训练测试脚本，输出 Precision、Recall、F1 和执行时间。
- 复现入口：如果后续补充代码，应优先寻找 `CICFlowMeter`、`feature_selection`、`RandomForestRegressor`、`classification`、`metrics`、`label`、`attack_schedule` 等关键词或文件名。

## 12. 本篇精华

- 这篇论文的核心贡献是 CICIDS2017 数据集，而不是新 IDS 模型。
- 作者把 IDS 数据集质量拆成 11 个维度，强调数据基准本身需要科学评价。
- CICIDS2017 的关键优势是双网络测试床、完整抓包、多协议正常流量、多攻击族和 flow-level 特征。
- 正常流量由 B-Profile 代理生成，试图缓解旧数据集正常行为过于单调的问题。
- 攻击流量覆盖 Brute Force、DoS、DDoS、Web Attack、Infiltration、Botnet、Heartbleed、PortScan 等典型场景。
- 论文用 CICFlowMeter 提取 80 多个特征，并指出不同攻击族依赖不同的时间、长度、方向和 TCP 标志位特征。
- RF、ID3、KNN 在该数据集上表现较好；RF 在准确率和执行时间之间最均衡。
- 使用 CICIDS2017 做后续研究时，必须警惕实验室生成数据、时间窗口标签、随机划分泄露和工具指纹导致的虚高性能。

## 13. 建议精读路线

1. 先读 Introduction 和 Available Datasets，理解作者为什么认为旧数据集不足。这部分适合写综述中的数据集演化背景。

2. 再读 Testbed Architecture、Benign Profile Agent 和 Attack Profiles，重点关注正常流量如何生成、攻击流量如何执行、网络拓扑是否足够真实。

3. 精读 Dataset 部分的每日攻击安排。后续使用 CICIDS2017 时，标签、日期、攻击时段是避免数据泄露的关键。

4. 读 Analysis 部分时，不要只看模型分数，更要看每类攻击对应的关键特征，这对设计可解释异常检测方法很有用。

5. 最后对照 Table 5 的 11 维数据集比较，但要保持批判：作者对自家数据集的评价偏积极，复现实验时仍需独立检查类别分布、划分方式和泛化能力。