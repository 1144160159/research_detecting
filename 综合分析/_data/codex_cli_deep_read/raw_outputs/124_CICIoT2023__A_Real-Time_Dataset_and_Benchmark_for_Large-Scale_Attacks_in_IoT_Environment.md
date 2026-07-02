# [124] CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment

## 1. 基本信息

- 论文：CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment
- 年份/来源：2023，Sensors
- DOI：10.3390/s23135941
- 作者机构：Canadian Institute for Cybersecurity / University of New Brunswick 团队
- 主题定位：IoT 恶意流量数据集、真实设备攻击测试床、入侵检测基准
- 正文状态：本次正文包完整，未截断。
- 代码包状态：存在两个本地仓库，但更像第三方复现实验/扩展分析，不是论文原始 pcap 到 csv 特征抽取官方代码。

## 2. 中文翻译与核心摘要

这篇论文的核心不是提出一个新的检测算法，而是构建并发布一个面向 IoT 攻击检测的大规模真实设备数据集 CICIoT2023。作者认为现有 IoT 安全数据集常见问题是：设备数量少、攻击类型覆盖不足、拓扑不够真实、攻击者往往是普通计算机而非 IoT 设备。为缓解这些问题，他们搭建了包含 105 个 IoT 设备的实验室网络，其中部分设备作为攻击者，部分作为受害者，执行 33 种攻击，并归入 DDoS、DoS、Recon、Web-based、Brute Force、Spoofing、Mirai 七类。

数据以 pcap 和 csv 两种形式提供。pcap 保留原始网络流量，csv 则是从固定包窗口中抽取的流量统计特征。论文进一步用 Logistic Regression、Perceptron、AdaBoost、Random Forest 和 DNN 做二分类、8 类分组分类、34 类细粒度分类，给出一个可对照的机器学习基准。

一句话概括：CICIoT2023 的价值在于“真实 IoT 拓扑 + 攻击覆盖广 + 恶意 IoT 设备发起攻击 + pcap/csv 双格式 + 多粒度基准”。

## 3. 论文解决的具体问题

论文面对的是 IoT 入侵检测研究中的数据基础问题，而不是单一模型优化问题：

- 现有 IoT 攻击数据集往往设备规模小，难以体现智能家居/边缘 IoT 网络中多品牌、多协议、多设备共存的流量复杂性。
- 攻击类型覆盖不全，尤其缺少多个 DDoS/DoS 变体、Web 攻击、Spoofing、Mirai 变体在同一数据集中的统一采集。
- 很多数据集让普通 PC 发起攻击，和“受感染 IoT 设备攻击其他 IoT 设备”的现实威胁链不完全一致。
- 研究者缺少同时支持原始流量重抽特征和直接训练 ML 模型的公开资源。
- 对检测任务本身也缺少多粒度基准：恶意/正常二分类、攻击类别分类、具体攻击类型分类的难度不同，需要分别评估。

## 4. 创新点深度提炼

1. **真实设备规模是主要创新**  
   论文使用 105 个 IoT 设备，包含摄像头、音箱、插座、灯、传感器、网关、Raspberry Pi 等。这个规模使数据更接近真实智能环境，而不是几台设备的小实验。

2. **攻击者也是 IoT 侧设备**  
   攻击由 Raspberry Pi 等恶意 IoT 设备发起，目标是其他 IoT 设备。这一点比“PC 攻击 IoT 设备”的传统实验更贴近 Mirai 类 botnet 的威胁模型。

3. **攻击谱系覆盖广**  
   33 种攻击横跨 DDoS、DoS、Recon、Web、Brute Force、Spoofing、Mirai。尤其 DDoS/DoS 细分很充分，包括 ICMP/UDP/TCP/HTTP Flood、SYN Flood、RSTFIN、PSHACK、Fragmentation、SlowLoris 等。

4. **同时提供 pcap 与 csv**  
   pcap 允许研究者重新设计特征，csv 则降低入门成本。论文的 csv 特征来自 DPKT，对固定包窗口统计，适合传统 ML 和深度学习基准。

5. **多粒度 benchmark 设计清楚**  
   同一数据集被组织成 34 类、8 类、2 类任务，可以观察“检测恶意”到“识别具体攻击”的性能退化。

6. **创新边界要看清**  
   论文的贡献主要是数据集和基准，不是新的异常检测模型。RF 和 DNN 的高性能证明数据可用，但不等于提出了更强检测方法。

## 5. 科学问题与研究假设

科学问题可以抽象为三层：

- **数据层问题**：真实 IoT 多设备拓扑中采集的攻击流量，是否能形成可公开复用的、足够丰富的安全分析数据资源？
- **可分性问题**：基于流量统计、协议、flag、包长、速率、IAT 等特征，能否区分正常流量、攻击大类和具体攻击类型？
- **泛化难题**：当攻击样本严重不平衡，且 Web、Recon、Spoofing 等低流量/行为相似攻击混杂时，常规 ML 是否还能稳定识别？

隐含研究假设包括：

- 真实 IoT 设备产生的攻击流量比模拟拓扑更能反映实际部署风险。
- 固定包窗口统计特征足以让 ML 模型捕捉大量攻击，尤其是流量型攻击。
- 分类粒度越细，模型越容易暴露类间相似性和类别不平衡问题。
- 高容量非线性模型，如 Random Forest、DNN，会明显优于线性模型和简单感知机。

## 6. 科学方法与技术路线

技术路线可以分成六步：

1. **搭建 IoT 实验室拓扑**  
   网络由 ASUS 路由器、Windows 10 共享连接、Cisco switch、Gigamon Network Tap、Netgear switch、VeraPlus 控制器、Zigbee/Z-Wave hub 和大量 IoT 设备组成。

2. **划分攻击侧与受害侧**  
   7 个 Raspberry Pi 主要承担恶意活动发起任务，其他 IoT 设备作为受害者或正常流量源。

3. **采集 benign 与 malicious 场景**  
   benign 流量来自 16 小时真实设备空闲与人工交互，包括传感器、音箱请求、摄像头视频访问等。恶意流量按攻击类型单独执行实验。

4. **抓包与合并**  
   网络 tap 将双向流量送入两个 monitor，通过 Wireshark 存储 pcap，再用 mergecap 合并同一实验的流量。

5. **数据处理与特征抽取**  
   原始流量约 548 GB。作者用 TCPDUMP 切成 10 MB 小块，再用 DPKT 并行抽取特征，去除空特征包。论文列出 47 个字段，其中 timestamp 只用于排序，训练时移除，实际常用 46 个 X 特征。

6. **机器学习评估**  
   使用 PySpark 混合与打乱数据，按 80/20 划分训练测试集，StandardScaler 标准化，然后训练 LR、Perceptron、AdaBoost、RF、DNN，分别做 34 类、8 类、2 类任务。

## 7. 实验设计与实验步骤

可复核流程如下：

1. **数据**  
   使用 CICIoT2023 的 pcap 或 csv。论文统计总行数约 46,686,579，其中 DDoS 约 33,984,560，DoS 约 8,090,738，Mirai 约 2,634,124，Benign 约 1,098,195，Spoofing、Recon、Web、Brute Force 明显更少。

2. **预处理**  
   pcap 侧：Wireshark 抓包，mergecap 合并，TCPDUMP 切块，DPKT 抽特征。  
   csv 侧：删除 timestamp，去除空特征包；DDoS/DoS/Mirai 等大流量攻击按 100 包窗口聚合，低流量攻击和 benign 按 10 包窗口聚合；再合并、打乱。

3. **模型/基线**  
   论文基线包括 Logistic Regression、Perceptron、AdaBoost、Random Forest、Deep Neural Network。RF 和 DNN 是主要强基线，线性模型用于反映任务难度。

4. **训练**  
   数据分成训练集 80%、测试集 20%；所有特征用 StandardScaler 标准化。分别构建 34 类、8 类、2 类标签体系。

5. **指标**  
   使用 Accuracy、Recall、Precision、F1-score。由于类别极度不平衡，F1 和按类混淆矩阵比 Accuracy 更有解释力。

6. **消融/敏感性**  
   论文没有严格的特征消融或超参敏感性实验，但通过 2/8/34 类任务展示分类粒度敏感性。代码包中额外有 SMOTE、class weight、SelectKBest、RandomizedSearchCV、联邦学习数据划分等扩展实验，可作为后续复现实验补充。

7. **结果核查**  
   核查时不要只看 accuracy。需要重点看 Web、Brute Force、Recon、Spoofing、Benign 的混淆情况，因为这些类别最能暴露数据不平衡和行为相似问题。

## 8. 关键结果、结论与证据

最重要的结论是：**CICIoT2023 对流量型攻击很容易分类，但对低频、语义接近或弱流量攻击仍然困难。**

关键证据：

- 二分类中所有模型 accuracy 都很高，但 F1 拉开差距。RF 的二分类 F1 约 0.965，DNN 约 0.940，LR 约 0.876，Perceptron 约 0.811。
- 8 类分组分类中，RF accuracy 约 0.994，但 F1 只有约 0.719；DNN accuracy 约 0.991，F1 约 0.697。说明 accuracy 被 DDoS/DoS 大类样本支配。
- 34 类细粒度分类中，RF accuracy 约 0.992，F1 约 0.714；DNN accuracy 约 0.986，F1 约 0.672。LR、Perceptron、AdaBoost 的 F1 均低于 0.5 左右，无法稳定细分攻击。
- 混淆矩阵显示 DDoS、DoS、Mirai 识别较好；Web-based 攻击常被误判为 Benign、Recon 或 Spoofing；Brute Force 也较难。这与其样本少、流量模式不如洪泛攻击显著有关。
- 论文最后给出的合理结论是：该数据集适合作为 IoT 安全分析与 IDS 的起点，但后续需要更强模型、更好的特征解释、迁移性分析和类别不平衡处理。

## 9. 局限性与待解决问题

- **类别不平衡非常严重**：DDoS 占主导，Web 和 Brute Force 样本极少。高 accuracy 不能代表各类攻击都检测良好。
- **标签可能存在场景级粗标风险**：论文说明每次攻击实验中捕获的整体流量标为该攻击，若背景正常流量混入，可能带来标签噪声。
- **缺少设备无关/时间无关泛化验证**：论文采用随机 80/20 划分，没有充分验证“新设备、新时间、新拓扑”上的泛化。
- **真实时间语义有限**：所谓 real-time 更偏向真实实验环境实时抓包，不等于已验证在线检测延迟、吞吐和部署开销。
- **DNN 细节不足**：论文报告 DNN 结果，但架构、调参、训练细节不够充分，复现实验需要额外确认。
- **Zigbee/Z-Wave 设备主要经 hub 暴露到网络侧**：因此数据更偏 IP 网络流量 IDS，不是低层无线协议安全数据。
- **正文包未截断**：本次理解不受缺页影响；若要引用图 2 拓扑或表格精确排版，仍建议回到 PDF 做最终校对。

## 10. 与本项目的关系

这篇论文与“异常检测、恶意流量、IoT、车联网、工业互联网与边缘安全”方向是中等相关。

可直接利用的地方：

- 作为 IoT 恶意流量检测 benchmark，适合验证异常检测模型在二分类、攻击大类、具体攻击类型三种任务上的表现。
- 类别不平衡很明显，适合研究长尾攻击识别、代价敏感学习、重采样、宏平均指标。
- 真实设备拓扑适合支撑“边缘安全”“智能家居/轻量 IoT 设备安全”的综述论据。
- pcap/csv 双格式适合做特征工程、流量窗口建模、序列建模或图建模。

需要谨慎迁移的地方：

- 它不是车联网或工业控制协议数据集，不能直接代表 CAN、V2X、Modbus、OPC UA 等场景。
- 它更偏网络流量分类，而不是主机日志、固件行为、设备侧遥测异常检测。
- 暗网关联较弱，主要是恶意流量和 IoT botnet 关联。

## 11. 代码对照分析

两个代码仓库都没有看到论文原始的 TCPDUMP/DPKT pcap 到 csv 特征抽取脚本，因此不能完整复现论文的数据生成链路。它们主要对应 csv/parquet 后的建模、探索和扩展实验。

| 目录 | 对应作用 | 关键文件 |
|---|---|---|
| `source\CICIoT2023` | 第三方 Colab/Kaggle 风格集中式 ML 实验 | [README.md](<F:\泉城实验室\二期\论文\异常检测\source\CICIoT2023\README.md>), `EDA_CICIoT23.ipynb`, `IoTTraffic_DecisionTreeClassifier.ipynb`, `IoT_Traffic_Application_Attack_prediction.ipynb`, `Detecting_Malicious_Traffic_over_IoT_SMOTE_.ipynb` |
| `source\plumpmonkey_CICIoT2023` | 更接近论文 benchmark 复现，并扩展到联邦学习 | [includes.py](<F:\泉城实验室\二期\论文\异常检测\source\plumpmonkey_CICIoT2023\includes.py>), `example.ipynb`, `CICIoT2023-MLclassifier.ipynb`, `our_notebook.ipynb`, `03-Federated Learning.ipynb` |

具体对应关系：

- **数据预处理**
  - `source\CICIoT2023\EDA_CICIoT23.ipynb`：把多个 csv 合并并转成 parquet，README 提到压缩为约 5.6GB parquet，路径偏 Google Drive/Kaggle。
  - `source\plumpmonkey_CICIoT2023\01-Data_Exploration.ipynb`：读取 `../datasets/CICIoT2023/` 下 csv，检查字段和标签分布。
  - `includes.py`：集中定义 46 个特征列、`label` 列，以及 34/8/7/2 类标签映射。这里的特征列正好对应论文移除 timestamp 后的训练输入。

- **模型训练**
  - `plumpmonkey_CICIoT2023\example.ipynb`：论文式入门复现，使用 `StandardScaler.partial_fit` 和 LogisticRegression，覆盖 34 类、8 类、2 类。34 类和 8 类 LR 输出与论文表 6 基本一致。
  - `plumpmonkey_CICIoT2023\CICIoT2023-MLclassifier.ipynb`、`our_notebook.ipynb`：集中式 LR、Perceptron、AdaBoost、RandomForest、MLP 训练，与论文 ML 评估最接近。
  - `CICIoT2023\IoTTraffic_DecisionTreeClassifier.ipynb`：Decision Tree、class weight、SMOTE、分组标签实验。
  - `CICIoT2023\IoT_Traffic_Application_Attack_prediction.ipynb`：Decision Tree、RandomForest、GaussianNB、SMOTE、RandomizedSearchCV、SelectKBest 特征选择。
  - `CICIoT2023\Detecting_Malicious_Traffic_over_IoT_SMOTE_.ipynb`：更完整的重采样与模型对照，包含 RF feature importance、SMOTE、DT/RF/NB、按类 recall 分析。

- **评估**
  - 两个仓库均使用 accuracy、recall、precision、f1，与论文一致。
  - `plumpmonkey` 的 notebooks 更适合复现论文表 6；`Jaquelinedops` 更适合探索重采样、特征选择和 recall 优先的改进策略。

- **联邦学习扩展**
  - `plumpmonkey_CICIoT2023\03-Federated Learning.ipynb` 使用 Flower + TensorFlow，提供 `STRATIFIED`、`LEAVE_ONE_OUT`、`ONE_CLASS`、`HALF_BENIGN` 四种客户端数据划分。模型是简单 Dense(50)-Dense(25)-softmax。该部分不是原论文内容，但对边缘 IoT/分布式 IDS 研究很有用。
  - `Output\generate_class_split_bar_graph.py` 用来解析联邦实验输出里的客户端类别分布并画图。

- **需要剔除或警惕**
  - `Benchmarking_NER.ipynb` 是 CoNLL2003 命名实体识别/Transformer benchmark，和 CICIoT2023 无关。
  - `Detecting_Malicious_Traffic_over_IoT_SMOTE_.ipynb` 中存在 notebook 执行状态问题，例如 `BernoulliNB` 未定义报错，以及部分单元疑似把 DecisionTree 的预测变量写成 RandomForest 结果。用于论文复现实验前需要清理。
  - 两个仓库都依赖外部大数据路径，未包含完整数据本体；运行前需要准备 CICIoT2023 csv 或 parquet。

## 12. 本篇精华

- CICIoT2023 的核心贡献是数据集，不是算法：105 个真实 IoT 设备、33 种攻击、7 个攻击大类，攻击由恶意 IoT 设备发起。
- 数据集最大优点是 pcap/csv 双格式：既能直接训练 ML，也能回到原始流量重做特征工程。
- 论文基准显示 RF 和 DNN 明显强于 LR、Perceptron、AdaBoost，但细粒度分类的 macro F1 并不高，说明任务并非“已解决”。
- DDoS、DoS、Mirai 这类流量型攻击易识别；Web、Brute Force、Recon、Spoofing 更能检验模型能力。
- 类别不平衡是理解结果的关键：DDoS 样本量压倒性大，accuracy 容易虚高，必须看 F1、recall 和混淆矩阵。
- 对异常检测项目而言，它适合作为 IoT 网络流量基准，也适合研究重采样、长尾类别、联邦学习和跨设备泛化。
- 代码包能支撑 csv/parquet 后的建模复现与扩展，但不能复现论文最前端的 pcap 抓包和 DPKT 特征抽取流程。

## 13. 建议精读路线

1. 先读第 3 节：重点看实验室拓扑、攻击者/受害者划分、105 个设备和网络 tap 采集方式。
2. 再读表 2、表 3：把 33 种攻击、工具、行数和类别不平衡记清楚。
3. 精读第 4 节：理解 pcap 到 csv、10MB 切块、DPKT 特征、10/100 包窗口聚合、timestamp 删除。
4. 精读第 5 节和表 6：不要只看 accuracy，要比较 2/8/34 类任务下 F1 的退化。
5. 看表 7、表 8：重点分析 Web、Brute Force、Recon、Spoofing、Benign 的混淆。
6. 代码复现先走 `plumpmonkey_CICIoT2023\example.ipynb` 和 `includes.py`，再看集中式 `CICIoT2023-MLclassifier.ipynb`。
7. 如果做改进研究，再读 `Detecting_Malicious_Traffic_over_IoT_SMOTE_.ipynb` 和 `03-Federated Learning.ipynb`，分别用于重采样/特征选择和边缘联邦学习扩展。