# [249] Label-Free Multivariate Time Series Anomaly Detection

## 1. 基本信息

- 论文：Label-Free Multivariate Time Series Anomaly Detection
- 作者：Qihang Zhou, Shibo He, Haoyu Liu, Jiming Chen, Wenchao Meng
- 期刊：IEEE Transactions on Knowledge and Data Engineering, 2024
- DOI：10.1109/TKDE.2024.3349613
- 主题：无标签多变量时间序列异常检测、动态图结构学习、条件归一化流、实体级异常定位
- 方法名：MTGFlow 与 MTGFlow_cluster
- 论文定位：AAAI 2023 会议版 “Detecting Multivariate Time Series Anomalies with Zero Known Label” 的扩展版；TKDE 版新增/强化了 cluster-aware density estimation、OCC 设置、单变量 UCR 实验和更多可视化分析。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：现实中的多变量时间序列异常检测很难保证训练集完全干净，而大量传统 OCC 方法默认训练数据全是正常样本。一旦训练集混入异常，模型会把异常也学成“正常边界”的一部分，检测性能下降。

作者提出的 MTGFlow 不再把训练集当作纯正常分布，而是直接估计整个训练数据分布，并利用“异常样本通常落在低密度区域”这一假设做检测。难点在于，多变量时间序列中不同实体之间存在复杂、变化的依赖关系，不同实体自身的异常稀疏特征也不同。为此，论文用自注意力学习随时间变化的实体关系图，用 RNN 提取时间编码，再把动态图卷积后的时空条件送入实体感知的 normalizing flow，得到实体级密度估计。扩展版 MTGFlow_cluster 进一步把相似实体聚成簇，让同簇实体共享目标分布，以利用实体共性。

一句话概括：本文把多变量时序异常检测从“干净正常集上的一类分类”转向“污染训练集上的无标签密度估计”，并用动态图与实体/簇感知流模型解决 MTS 中依赖变化和实体异质性问题。

## 3. 论文解决的具体问题

论文针对的是 label-free MTS anomaly detection，即训练阶段没有任何已知标签，也不假设训练集全正常。这个设定比常见 OCC 更接近工业控制、服务器监控、智能电网、网络安全遥测等真实场景：异常可能已经混在历史数据里，人工清洗训练集成本高，甚至无法确认哪些时间段绝对正常。

具体挑战有三个：

- 训练数据污染：DeepSVDD、USAD、ALOCC、DROCC 等方法通常依赖“正常训练集”，一旦异常混入，模型会学习到错误边界或重构异常。
- 实体依赖是动态的：GANF 用静态 DAG 建模变量关系，但工业系统中阀门、水位、流量、泵等关系会随工况变化，静态结构不足。
- 实体异常表现不同：不同传感器或服务指标的工作机理不同，异常时不应被强行映射到同一个标准高斯空间；否则会牺牲细粒度密度估计能力。

## 4. 创新点深度提炼

第一，问题设定更现实。论文没有继续沿用“训练集全正常”的 OCC 假设，而是直接接受训练集可能被异常污染。方法训练时不使用标签，也不需要清洗正常集。

第二，动态图结构替代静态 DAG。MTGFlow 用 self-attention 根据每个滑动窗口动态生成实体间邻接矩阵。这样既能表达非对称关系，也能表达互相关系、周期性关系和随工况变化的关系，避免 GANF 中静态 DAG 的约束。

第三，实体感知 normalizing flow。GANF 把所有实体映射到同一目标分布，MTGFlow 则给每个实体设置不同的目标高斯均值，相当于让每个传感器/指标拥有自己的“正常密度坐标系”。这直接服务于细粒度异常定位。

第四，MTGFlow_cluster 引入实体共性。作者意识到“每个实体都完全独立建目标分布”也可能过细：同一生产线、同一区域、相同类型传感器往往有相似统计属性。因此扩展为簇级目标分布，让同簇实体共享密度形态，不同簇保持差异。

第五，检测与定位统一。窗口异常分数来自所有实体负 log likelihood 的均值；实体异常分数来自单实体 log likelihood，因此模型天然支持“哪个实体导致窗口异常”的解释。

## 5. 科学问题与研究假设

核心科学问题可以拆成三层：

- 在没有干净正常训练集的条件下，能否通过整体密度估计识别异常？
- 多变量时序中的实体依赖是否应被建模为动态关系，而非静态关系？
- 不同实体的异常稀疏性是否需要不同目标分布来刻画？

论文的主要假设是：异常样本在拟合的数据分布中更稀疏，因而具有更低似然。这一假设不是 MTGFlow 独有，而是密度估计类异常检测的基础。论文进一步假设，准确估计 MTS 密度必须同时处理实体间动态依赖和实体自身异质性；如果这两点处理不好，低密度假设即使成立，也会因为密度估计不准而失效。

## 6. 科学方法与技术路线

输入是多变量时间序列，包含 K 个实体，每个实体有 L 个观测点。模型先对每个实体做 z-score 标准化，再用滑动窗口切分为窗口样本，窗口大小 M、步长 S。只要窗口内任一时间点异常，该窗口在评估时被视为异常。

技术路线如下：

1. 时间建模：对每个实体窗口序列输入 RNN/LSTM，得到时间隐藏状态。
2. 关系建模：把每个实体窗口作为节点特征，通过 Query-Key self-attention 计算 K×K 注意力矩阵，作为当前窗口的动态图邻接矩阵。
3. 时空条件构造：用动态图对 RNN hidden states 做图卷积，并加入上一时刻历史信息，形成 spatio-temporal condition。
4. 密度估计：条件 normalizing flow 在时空条件约束下把原始序列映射到目标高斯分布。
5. 实体/簇目标分布：MTGFlow 为每个实体设置不同目标均值；MTGFlow_cluster 先用 KShape 聚类，再为每个簇设置目标均值。
6. 联合训练：动态图、RNN、图卷积、flow 全部通过最大似然联合优化。
7. 异常判别：窗口分数是实体负 log likelihood 均值；实体分数用于定位。论文还用 IQR 设计无标签阈值。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   多变量数据集包括 SWaT、WADI、PSM、MSL、SMD；额外在 UCR 250 个单变量子数据集上验证泛化。SWaT/WADI 属于工业控制系统数据，PSM/SMD 属于服务器或应用监控，MSL 属于航天器遥测。

2. 预处理  
   每个实体按时间维做 z-score 标准化。MTS 实验使用窗口大小 60、步长 10；UCR 异常持续时间短，窗口大小设为 10。窗口标签仅用于评估：窗口中存在任一异常点即记为异常窗口。

3. 数据划分  
   无监督设置下，论文跟随 GANF 的污染训练设定：使用原始测试序列切分训练/验证/测试，使训练部分可能含异常。OCC 设置下，使用原始正常训练集训练，再在测试集评估。

4. 模型/基线  
   基线包括 DeepSAD、DeepSVDD、ALOCC、DROCC、USAD、DAGMM、GANF。MTGFlow 使用一层 LSTM、一层 self-attention、MAF flow。MTGFlow_cluster 用 KShape 给实体分簇，默认簇数 20，并分析簇数敏感性。

5. 训练  
   Adam，学习率 0.002；MTS 训练 40 epoch；SWaT 使用 1 个 flow block、batch size 512；其他数据集使用 2 个 flow blocks、batch size 256。所有模块通过最大化 log likelihood 联合训练。

6. 指标  
   主指标是窗口级 AUROC。论文也讨论了基于 IQR 的阈值和实体级分数，但核心表格主要围绕 AUROC。

7. 消融/敏感性  
   消融包括去掉图结构、去掉实体感知 flow、二者都去掉；敏感性包括窗口大小、flow block 数量、cluster 数量、训练集中异常污染比例。

8. 结果核查  
   论文通过 ROC 曲线、log likelihood 时间曲线、正常/异常分数分布、动态关系图、实体级异常响应曲线验证：异常段似然更低，动态图确实随时间变化，不同实体对不同攻击区间响应不同。

## 8. 关键结果、结论与证据

主要结论是：MTGFlow 和 MTGFlow_cluster 在污染训练集的无标签设定下优于 OCC 与已有密度估计方法，尤其相对 GANF 的提升来自“动态图 + 实体级密度”的组合。

论文给出的关键证据包括：

- 在五个 MTS 基准上，MTGFlow/MTGFlow_cluster 的 AUROC 整体超过七个基线，SWaT 上相对 SOTA 有明显提升。
- OCC 对训练污染非常敏感。论文举例：DeepSVDD 在 SWaT 上从无监督污染设定的 66.8 AUROC 提升到 OCC 干净训练设定的 85.9；PSM 上从 67.5 到 85.5；DROCC 在 WADI 上从 75.6 到 89.0。这反过来说明污染训练会严重伤害 OCC，而 MTGFlow 两种设定表现接近，鲁棒性更好。
- 消融显示，去掉动态图或实体感知 flow 都会下降；论文总结中给出实体感知设计在 SWaT/WADI 上分别带来约 4.1 和 1.6 AUROC 提升，动态图分别带来约 2.4 和 0.6 AUROC 提升。
- cluster-aware 设计在合适簇数下进一步优于 MTGFlow，论文称 SWaT/WADI 上分别约提升 1.0 和 1.1 AUROC。
- UCR 单变量实验说明，尽管 MTGFlow 为 MTS 设计，在 K=1 时仍能用密度估计检测短促、非极值型异常。
- 可视化显示动态图有动态性、一致性、周期性和互依赖性；实体级分数显示不同传感器对不同攻击段响应不同，支持异常定位解释。

## 9. 局限性与待解决问题

本次正文包标注未截断，因此没有“缺页导致的理解缺口”；但仍建议后续回到 PDF 复核表格中的完整数值，因为正文抽取中 Table II、III、IV、V、VI 的具体矩阵数值没有全部以可读形式呈现。

方法层面的局限更值得关注：

- 低密度假设并非总成立。若异常反复出现、持续时间长、占比较高，flow 可能把异常区域也拟合成高密度。
- MTGFlow_cluster 对聚类质量敏感。论文自己承认默认 KShape 簇数 20 不一定适合所有数据集，SWaT 上合适簇数约 35；错误聚类会把不同机理实体混到一个目标分布里。
- 自注意力图不等于物理因果图。它可用于解释和定位线索，但不能直接当作真实因果依赖或攻击路径。
- 主评估偏重 AUROC，阈值化后的告警质量、误报成本、检测延迟、在线部署开销没有充分展开。
- K×K 动态注意力对实体数较大的系统有二次复杂度；虽然 flow 参数共享降低了参数量，但图学习和窗口级推理成本仍需评估。
- 论文面向连续数值型遥测，对日志文本、离散事件、网络包序列、协议字段等安全数据还需要额外编码层。

## 10. 与本项目的关系

这篇论文与“时序、日志、KPI 与云原生异常检测”方向关系较强，但不是直接的网络入侵检测模型。它最适合作为多指标遥测异常检测框架：例如主机 CPU/内存/网络吞吐、服务延迟、错误率、连接数、工业控制传感器、云原生组件 KPI 等。

对本项目有三点可借鉴：

- 无标签污染训练设定很实用。网络安全和云监控历史数据很难保证干净，MTGFlow 的 label-free 思路比纯 OCC 更贴近落地。
- 动态图适合建模系统依赖。微服务、主机、网络设备、工业传感器之间的依赖会随负载、策略、攻击阶段变化，静态拓扑不够。
- 实体级 log likelihood 可用于定位。安全告警不只要判断“异常”，还要指出哪个指标、主机、传感器或服务贡献最大。

但迁移时要注意：网络入侵检测常包含类别特征、协议状态、稀疏事件和攻击语义，不能直接把 MTGFlow 当作包级 IDS；更合理的是把它放在“多源安全遥测/KPI 异常检测”层。

## 11. 代码对照分析

元数据称“未发现该论文对应的本地开源代码”。我在工作区中实际看到了两份 MTGFlow 相关基线代码：`source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD` 与 `MTGFlow-CHD`。README 指向 AAAI 2023 版本并列出 TKDE 2024 引文，因此可作为参考实现，但它们明显经过本地任务改造，不应视为 TKDE 2024 完整官方实现。

核心对应关系如下：

- 模型主体：[`models/MTGFLOW.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/models/MTGFLOW.py>)  
  `ScaleDotProductAttention` 对应论文的 self-attention 动态图；`MTGFLOW` 类组合 LSTM、GNN 和 MAF；`test()` 中用 log_prob 均值作为窗口似然。

- 归一化流：[`models/NF.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/models/NF.py>)  
  包含 MADE、MAF、BatchNorm 等 flow 组件；`base_dist_mean` 按 `n_sensor` 设置，体现实体感知目标分布思想。

- 数据预处理：[`Dataset/wadi.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/Dataset/wadi.py>)、[`Dataset/psm.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/Dataset/psm.py>)、[`Dataset/smd_smap_msl.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/Dataset/smd_smap_msl.py>)  
  这些文件实现 StandardScaler、滑动窗口、窗口标签聚合，基本对应论文实验流程。

- 训练入口：[`train-ROAD.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/train-ROAD.py>) 与 [`train-CHD.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-CHD/train-CHD.py>)  
  训练目标是 `-model(x)`，即最大化 log likelihood；循环种子 15 到 19，训练 40 epoch，Adam，学习率 0.002。

- 测试入口：[`test-ROAD.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-ROAD/test-ROAD.py>) 与 [`test-CHD.py`](<F:/泉城实验室/二期/论文/异常检测/source/XIPHOS/Baseline-models/MTGFlow/MTGFlow-CHD/test-CHD.py>)  
  使用负 log likelihood 作为异常分数并计算 AUROC。

需要特别说明几处代码与论文不完全一致：

- 没看到 `MTGFlow_cluster`、KShape 或 cluster-aware target distribution 的实现。
- ROAD/CHD 的 `swat.py` 被改为 `ImageFolder` 数据入口，原始 SWaT 时间序列读取逻辑被注释，说明这是本地改造版。
- 训练脚本里模型窗口参数硬编码为 `27`，而论文 MTS 默认窗口是 `60`；这也与图像/局部改造数据有关。
- `locate()` 里似乎期望 `nf.log_prob()` 返回 `(log_prob, z)`，但当前 `MAF.log_prob()` 只返回 log_prob 张量；实体定位代码需要复核或修正。
- runner 脚本调用的是 `main.py`，但目录中实际是 `train-ROAD.py`/`train-CHD.py`，运行前需要改入口或补 main.py。

## 12. 本篇精华

- 这篇论文的核心贡献不是“又做了一个更深的时序模型”，而是把异常检测设定从干净正常训练集推进到真实的无标签污染训练集。
- MTGFlow 的关键判断是：MTS 密度估计不准，主要因为实体依赖动态变化且实体本身异质；动态图和实体感知 flow 分别对应这两个瓶颈。
- 相比 GANF 的静态 DAG，self-attention 动态图更适合工业控制和云系统中的工况变化、周期关系和互依赖关系。
- 实体感知目标分布让每个传感器/指标有自己的密度参照系，因此异常定位比单一全局分布更自然。
- MTGFlow_cluster 的思想很有价值：不是所有实体都应完全独立，位置、功能或工况相似的实体可以共享统计结构；但聚类质量是性能关键。
- 论文实验最有说服力的地方，是 OCC 方法在污染训练集下明显退化，而 MTGFlow 在无监督和 OCC 设置下表现接近。
- 对安全场景而言，它更适合“多源遥测/KPI 异常检测与定位”，不适合直接替代包级或日志语义级 IDS。
- 本地代码可作为 MTGFlow 主体参考，但缺失 TKDE 版 cluster 扩展，并且 SWaT 数据入口已被本地任务改造，复现实验前必须清理差异。

## 13. 建议精读路线

1. 先读 Introduction 中对 OCC 污染问题和 GANF 两个缺陷的讨论，这是全文动机。
2. 再读 Method 的 Problem Statement、Graph Structure Learning、Spatio-Temporal Condition、Entity/Cluster-Aware Normalizing Flow，重点理解“动态图 + 条件 flow + 实体目标分布”如何串起来。
3. 精读公式 6 到 15：它们分别对应动态图、时空条件、实体/簇密度估计、联合似然、窗口分数和实体阈值。
4. 实验部分优先看无监督与 OCC 对比，再看消融。消融比主表更能解释方法为什么有效。
5. 最后看动态图可视化和实体级 log likelihood 曲线，它们决定这篇论文是否能为安全告警解释提供支撑。
6. 若准备复现，先以 MSL/PSM/WADI 数据加载器和 `models/MTGFLOW.py` 为主，不要直接使用当前 ROAD/CHD 的 SWaT 图像入口来声称复现论文结果。

<!-- codex-cli-deep-read: complete -->
