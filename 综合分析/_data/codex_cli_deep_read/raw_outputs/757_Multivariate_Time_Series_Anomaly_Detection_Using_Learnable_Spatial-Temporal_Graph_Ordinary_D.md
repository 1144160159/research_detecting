# [757] Multivariate Time Series Anomaly Detection Using Learnable Spatial-Temporal Graph Ordinary Differential Equations Network

## 1. 基本信息
题名可译为：**基于可学习时空图常微分方程网络的多变量时间序列异常检测**。论文面向 IoT/工业控制系统中的传感器多变量时间序列异常检测，发表于 IEEE TDSC，DOI 为 `10.1109/TDSC.2025.3640165`。正文页眉版本是 2026 年 3/4 月刊，但元数据与 DOI 发布年份归为 2025。

作者核心问题域是：工业 IoT 中攻击或故障会改变物理过程状态，传感器 MTS 是直接观测面；模型在只用正常训练数据的半无监督设定下，通过预测误差识别异常。

## 2. 中文翻译与核心摘要
MAD-ODE 的主张是：现有 GNN 异常检测要么依赖专家预定义图，要么纯粹学习图结构而忽视已有先验；同时传统离散 GCN 难以加深，容易过平滑，捕获远距离传感器依赖不足。

论文提出一个混合图学习框架：一条图来自原始数据的静态余弦相似性，提供稳定、可解释的传感器邻接；另一条图是全参数可学习图，用 Gumbel-Softmax 处理离散邻接，并用 DTW 先验图约束。预测器采用 STGODE，在两个图上建模时空依赖，最后用预测误差、归一化最大传感器误差和阈值搜索输出异常。

## 3. 论文解决的具体问题
论文不是泛泛做“时间序列异常检测”，而是针对工业 IoT/SCADA 传感器数据中的两类结构性难点：

第一，传感器之间确实有物理或过程依赖，但真实图结构往往隐藏、昂贵或难以由专家完整给出。纯图结构学习又容易“盲学”，尤其在正常样本有限、异常稀疏时不稳定。

第二，异常传播可能跨过程、跨传感器并带延迟。例如 SWaT 中 AIT-202 被操纵后，影响 P203，再进一步影响 AIT-501。浅层 GCN 或割裂的时间/空间建模难以捕获这种长距离、延迟型依赖。

## 4. 创新点深度提炼
核心创新不是单独用了图，也不是单独用了 ODE，而是把**先验图、学习图和连续深度图卷积**组合成一个面向 MTSAD 的预测式检测框架。

静态图 `ACOS` 用 top-k 余弦相似性表达稳定相似关系，降低纯学习图的不确定性；可学习图 `AFPM` 用全邻接参数表达潜在复杂依赖，并由 DTW 图引导，使时间延迟相关性进入图学习目标。STGODE 则用 TCN-ODE-TCN 的结构替代简单堆叠 GCN，试图缓解过平滑并扩大有效感受野。

从异常检测视角看，创新点还包括把“图学习质量”显式纳入损失，而不是只靠最终预测误差间接塑造图结构。

## 5. 科学问题与研究假设
科学问题可以概括为三问：部分可靠先验能否提升未知传感器图学习？连续深度图卷积能否比浅层离散 GCN 更好捕获长程依赖？正常行为预测误差能否稳定地区分物理攻击造成的偏离？

论文隐含的研究假设是：正常数据足以刻画系统稳定行为；异常会在至少一个传感器上产生可观测偏差；余弦相似、DTW 相似和反向传播学习到的邻接分别覆盖不同类型的依赖；最大传感器异常分数可以代表时间戳级异常。

## 6. 科学方法与技术路线
输入是多变量时间序列 `X ∈ R^{M×N}`，每个历史窗口 `Xt` 用于预测后续传感器值。训练集只含正常样本，检测时用预测误差作为异常证据。

技术路线是：先从训练数据构造 `ACOS`，每个传感器选 top-k 余弦近邻；再计算 DTW 距离图 `ADTW`，用阈值控制稀疏度；同时学习全参数邻接 `AFPM`，用 Gumbel-Softmax 近似离散边采样。预测器 STGODE 在静态图和学习图上分别提取时空特征，聚合后经 MLP 得到预测值。总损失由预测误差和图学习交叉熵正则构成。异常分数按传感器误差标准化后取最大值，再做阈值搜索和 point adjustment。

## 7. 实验设计与实验步骤
可复核流程如下：

1. 数据：SWaT、WADI、MSL、SMAP、SMD。SWaT/WADI 原始数据按 10 秒下采样并取区间中位数；训练集只保留正常片段，测试集使用官方异常标签。

2. 预处理：滑动窗口切分历史序列，论文默认窗口 `w=12`；各传感器误差需要按均值/标准差或中位数/IQR 归一化，避免量纲大的传感器支配分数。

3. 模型/基线：MAD-ODE 对比 AE、IF、DAGMM、LSTM-NDT、LSTM-VAE、MAD-GAN、OmniAnomaly、USAD、MTAD-GAT、GDN、FuSAGNet、GTA、MGCLAD、MEGLAD、FuGLAD、MSTGAD。

4. 训练：Python 3.8、PyTorch 1.10、CUDA 11.3；论文设置静态图 `k=10`，DTW 阈值 `ε=0.6`，最大 30 epoch。训练目标是正常序列预测，图正则约束学习图贴近 DTW 先验。

5. 指标：Precision、Recall、F1，并报告 AUC/AUPR 这类阈值无关指标。

6. 消融/敏感性：比较 Only COS、Only FPM、ADP+COS、ADP+FPM；测试窗口大小 `6/12/15/21/30` 和图损失权重 `λ1`；加入高斯噪声和 1%、2%、5% 缺失值检验鲁棒性。

7. 结果核查：不仅看平均 F1，还要检查 WADI 这类高维、低异常率数据集；同时结合案例图确认学习到的边是否符合过程传播链路。

## 8. 关键结果、结论与证据
论文给出的主要结论是：MAD-ODE 在五个数据集上取得最佳平均表现，单数据集上通常为最佳或次优；MGCLAD 在 WADI 上强，但其他数据集弱，MSTGAD 在 SWaT/SMAP 上强但 WADI 弱，而 MAD-ODE 更稳定。

消融实验支持两个图都必要：只用静态图或只用 FPM 图都会下降，用 ADP 替换任一图也下降。敏感性实验显示 MSL、SMAP、SMD 对窗口不太敏感，SWaT/WADI 的窗口变大反而可能掩盖短异常。鲁棒性实验显示噪声和缺失对 MSL/SMD 影响小，对 SWaT/WADI/SMAP 有轻微下降。案例研究中，AIT-202 攻击经 P203 影响 AIT-501，模型的预测变化和学习图关系与物理过程解释一致。

正文包中的表格数值没有以可读文本完整展开，因此这里不逐项复述具体数值，只使用论文正文对表 III-VI 的文字解释。

## 9. 局限性与待解决问题
论文自身承认后续需要降低误报，并扩展到异常诊断和根因分析。方法上还有几个关键限制：DTW 图构建复杂度为 `O(N²M²)`，高维长序列代价高；阈值搜索和 point adjustment 会让离线 F1 更好，但部署时未必有标签可调阈值；最大传感器分数假设简单，可能忽略多传感器弱异常的组合证据。

威胁模型也偏理想化：假设攻击者不能刻意规避检测，且物理攻击必然留下可观测传感器偏差。正文包标记为未截断，但 plaintext 中表格数值和图形细节仍需回 PDF 复核。

## 10. 与本项目的关系
对“时序、日志、KPI 与云原生异常检测”方向，这篇最有价值的是**混合先验图 + 可学习图 + 预测误差检测**范式。云原生场景中，传感器可类比为服务、Pod、主机、KPI 指标；静态图可由调用链、部署拓扑、CMDB 或服务依赖生成，学习图补充隐藏依赖。

对“图学习、知识图谱与威胁情报”方向，它不是语义知识图谱论文，但提供了把结构先验注入异常检测模型的可借鉴方式。对入侵检测/网络异常检测，它更贴近 ICS 物理过程攻击，而不是流量包级或日志文本检测；适合作为工业控制、AIOps KPI、遥测异常检测的中高相关工作。

## 11. 代码对照分析
本地仓库在 `source\MAD-ODE`。运行线索见 [README.md](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/README.md:35)，但源码复核发现配置和依赖不完整。

数据预处理主要在 [scripts/generate_msl_dataset.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/scripts/generate_msl_dataset.py:63)、`generate_smap_dataset.py`、`generate_swat_dataset.py`、`generate_wadi_dataset*.py`，逻辑是 CSV 最后一列为标签，`x_offsets=-11..0`，`y_offsets=1..12`，保存 `train/val/test.npz`。注意 `generate_swat_dataset.py` 默认路径写成 `smd`，`generate_wadi_dataset.py` 默认路径写成 `smap` 且标签 reshape 有风险。

训练入口是 [train.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/train.py:81)：读取 YAML、构造或加载 `data/{dataset}_dtw_distance.npy`，用 `fastdtw` 计算 DTW 先验，然后调用 `GTSSupervisor`。但仓库中没有检索到 `.yaml` 配置文件，README 提到的 `generate_smd_dataset` 也未见对应脚本。

图构建与训练损失在 [model/pytorch/supervisor.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/model/pytorch/supervisor.py:47)：DTW 距离经高斯核和 `0.6` 阈值生成先验图；静态图由 `kneighbors_graph(train_feas.T, k, metric='cosine')` 生成；训练时损失是预测 MSE 加两个 BCE 图正则。这里和论文的 MAE + `λ1` 单图正则口径不完全一致。

模型主体在 [model/pytorch/model.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/model/pytorch/model.py:155)、[modelode.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/modelode.py:115)、[odegcn.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/odegcn.py:20)。`modelode.py` 实现 TCN-ODEG-TCN 的 STGODE 双图分支，`odegcn.py` 用 `torchdiffeq.odeint(..., method='euler')` 求解。一个重要源码疑点是：`model.py` 中 FPM 的 `self.logits` 看起来不是 `nn.Parameter`，按当前代码未必真正可学习；这需要回到作者原始提交或修正后再复现实验。

评估链路在 [test.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/test.py:85)、[mai.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/mai.py:94)、`err_scores.py`、`evaluate.py`、`eval_methods.py`。`test.py` 最终只取第一个预测步；`mai.py` 用预测误差分数、滑动平均和每时刻最大传感器分数做 grid search。当前 [jump/metrics.py](F:/泉城实验室/二期/论文/异常检测/source/MAD-ODE/jump/metrics.py:307) 中存在将 best Precision/Recall/F1 硬编码为 `1` 的问题，若原样运行会污染结果。由于当前环境只读且缺少数据/配置，我没有运行训练复现。

## 12. 本篇精华
1. MAD-ODE 解决的是“未知传感器依赖 + 长程异常传播”两个问题，而不是单纯换一个预测器。
2. 混合图学习是全文核心：余弦静态图给稳定先验，FPM 学隐藏关系，DTW 图把延迟相关性注入学习过程。
3. STGODE 的价值在于用连续深度图卷积缓解深层 GCN 过平滑，并扩大跨传感器、跨时间的感受野。
4. 检测本质仍是正常行为预测误差法，阈值搜索和 point adjustment 对最终 F1 影响很大。
5. 消融结果支持“静态图 + 学习图”缺一不可，ADP 替换方案不如论文设计。
6. WADI 是最能暴露方法鲁棒性的场景：高维、长序列、低异常率，MAD-ODE 的稳定性优于若干强基线。
7. 代码包有复现风险：配置缺失、依赖文件不完整、数据脚本默认路径错位、FPM 可学习性和评估函数需要核查。

## 13. 建议精读路线
先读 Introduction 和 Threat Model，把 SWaT 的 AIT-202 案例当作异常传播主线。随后精读 Fig. 2/Fig. 3 和公式 6-13，理解 COS、DTW、FPM 三种图信息各自承担什么角色。

第二步读 STGODE 部分，重点看公式 14-19：它为什么不是简单堆 GCN，而是把图扩散、时间卷积和 ODE 连续演化放在同一预测器里。

第三步读实验：先看数据集和基线，再看表 III-VI、窗口/λ1 敏感性、鲁棒性和案例研究。最后对照代码按 `train.py -> supervisor.py -> model.py -> modelode.py/odegcn.py -> test.py/mai.py` 走一遍，并优先修复配置、依赖和评估函数后再复现。