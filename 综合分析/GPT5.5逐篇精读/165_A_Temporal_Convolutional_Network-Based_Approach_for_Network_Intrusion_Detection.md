# [165] A Temporal Convolutional Network-Based Approach for Network Intrusion Detection

## 1. 基本信息

- 编号：165
- 题名：A Temporal Convolutional Network-Based Approach for Network Intrusion Detection
- 年份：2024
- DOI：10.1109/iciics63763.2024.10860234
- 来源：2024 International Conference on Integrated Intelligence and Communication Systems，ICIICS
- 任务类型：网络入侵检测、多分类异常检测
- 数据集：Edge-IIoTset / DNN-EdgeIIoT
- 分类目标：15 类，包括 Normal 与 14 类攻击
- 代码状态：本地未发现该论文对应开源代码
- 正文状态：本次正文包未截断

## 2. 中文翻译与核心摘要

这篇论文研究的是边缘计算与 IoT/IIoT 网络中的多类别入侵检测问题。作者认为，现代 IoT 网络流量具有明显的异构性和时序依赖：同一攻击行为往往不是由单个包或单个字段决定，而是由一段连续通信模式、协议字段组合和行为演化共同体现。传统机器学习方法难以适应攻击模式变化，普通 1D CNN 又偏重局部模式，CNN-LSTM、CNN-GRU 等混合模型虽然能建模时序，但训练慢、计算复杂、并行性差。

论文提出使用 Temporal Convolutional Network，TCN，构建网络入侵检测模型。核心结构是带残差连接的扩张卷积块，通过不同 dilation rate 扩大感受野，在不依赖循环结构的情况下捕获短期与长期依赖。模型在 Edge-IIoTset 的 15 类多分类任务上达到 96.72% 测试准确率、0.0668 测试损失，优于 1D CNN、CNN-GRU、CNN-LSTM、CNN-BiLSTM 和 CNN-LSTM-GRU。

核心结论是：在 Edge-IIoTset 这类 IoT/IIoT 网络流量数据上，TCN 能以更高并行效率和更稳定训练过程替代循环网络，并在整体准确率、加权 F1、若干攻击类别识别上取得优势。

## 3. 论文解决的具体问题

论文解决的问题不是一般意义上的“用深度学习做 IDS”，而是更具体的三个层面：

第一，面向边缘计算与 IoT/IIoT 场景的复杂攻击检测。Edge/IoT 网络中存在 DDoS、MITM、SQL injection、XSS、Uploading、Backdoor、Ransomware、Password、Scanning 等多种攻击。攻击类型之间的行为差异并不总是体现在单个字段，而是分布在 TCP、UDP、DNS、HTTP、MQTT、Modbus 等协议字段组合中。

第二，解决普通 CNN 对长程依赖建模不足的问题。1D CNN 对局部特征有效，例如 TCP flag、HTTP 字段、DNS query 等局部模式，但固定卷积核和有限层数限制了其远距离依赖捕获能力。

第三，解决 CNN-RNN 混合模型效率和稳定性问题。CNN-LSTM、CNN-GRU、CNN-BiLSTM 能增强序列建模，但循环结构天然难以并行，训练成本更高，也更容易受到梯度传播、过拟合和大规模样本训练效率的影响。TCN 被用来在“保持时序建模能力”和“提高并行训练效率”之间取得折中。

## 4. 创新点深度提炼

1. 将 TCN 用于 Edge-IIoTset 的 15 类多分类入侵检测  
   论文强调已有研究中 TCN 多用于其他数据集、DDoS 专项检测或 Edge-IIoTset 上的二分类任务，而针对 Edge-IIoTset 15 类攻击识别的 TCN 框架仍较少。因此，本文的主要新意在于把 TCN 放入更细粒度的 IoT/IIoT 多类别攻击识别场景。

2. 用扩张卷积替代循环结构进行时序模式捕获  
   作者没有采用 LSTM/GRU 逐步处理序列，而是用 dilated convolution 扩大感受野。这样既能覆盖远距离依赖，又保留卷积结构的并行计算优势。这一点对于大规模 IDS 数据比较关键，因为实际部署中检测速度和吞吐能力同样重要。

3. 使用残差块稳定训练  
   论文的 TCN 由三个 stacked residual blocks 组成。残差连接的作用是改善梯度流动，降低深层时序卷积网络训练不稳定风险。对于网络流量这类高维、稀疏、类别不平衡的数据，残差结构有助于避免模型在深层卷积后退化。

4. 与多个 CNN/RNN 混合基线进行同环境比较  
   对比模型包括 1D CNN、CNN-GRU、CNN-LSTM、CNN-BiLSTM、CNN-LSTM-GRU。虽然实验深度有限，但至少不是只和传统 ML 或单一 CNN 比较，而是针对“TCN 是否能替代循环网络”这一问题设置了相对直接的基线。

5. 给出按类别的分类报告  
   论文不仅报告整体 accuracy/loss，还列出 precision、recall、F1、support。对于异常检测论文来说，这比单一准确率更重要，因为 Edge-IIoTset 中 Normal 样本占绝对多数，少数类攻击的表现才真正反映模型价值。

## 5. 科学问题与研究假设

核心科学问题可以概括为：

在 IoT/IIoT 网络入侵检测中，不依赖循环结构的时序卷积模型，是否能够比 CNN-RNN 混合模型更有效地捕获网络流量中的多尺度时序依赖，并提升多类别攻击检测性能？

论文隐含的研究假设包括：

1. 网络流量中的攻击行为具有可学习的时序依赖  
   攻击类型并不是独立字段组合，而可能表现为一段通信序列中的模式，例如 DDoS 流量、扫描行为、注入行为、认证攻击等。

2. 扩张卷积足以覆盖 IDS 所需的长短期依赖  
   TCN 通过 dilation 扩大感受野，作者假设这种方式能够替代 LSTM/GRU 的记忆机制。

3. 残差连接能提升深层时序卷积网络训练稳定性  
   对于高维网络流量特征，单纯堆叠卷积可能导致梯度问题，残差块被假设能缓解这一点。

4. TCN 的并行性会带来更好的训练效率与部署潜力  
   论文未严格测量推理时延或训练时间，但在论述上认为 TCN 相比 RNN 更适合高吞吐 IDS。

5. Edge-IIoTset 能代表较复杂的 IoT/IIoT 攻击分布  
   作者把该数据集作为验证 TCN 泛化能力和多攻击识别能力的主要依据。

## 6. 科学方法与技术路线

论文技术路线可以拆成六步：

1. 数据集选择  
   使用 Edge-IIoTset 中的 DNN-EdgeIIoT CSV 数据。原始数据包含 61 个特征和两个标签列：Attack Label 与 Attack Type。本文使用 Attack Type 做 15 类多分类。

2. 数据清洗与编码  
   删除时间戳、IP 地址、部分协议细节字段、无意义字段和重复行。对 HTTP、DNS、MQTT 等类别型字段进行 label encoding 与 one-hot encoding。

3. 特征筛选与降维  
   使用哈希方法识别内容完全相同的重复列并删除。使用 Chi-Squared test 根据与 Attack Type 的关联程度进行特征排序与选择。

4. 类别保持式采样  
   使用 stratified sampling 将数据量缩小到原始规模的 0.25，同时保持 Attack Type 类别分布。预处理后样本数为 486,362。

5. 模型训练  
   比较 1D CNN、CNN-GRU、CNN-LSTM、CNN-BiLSTM、CNN-LSTM-GRU 和 TCN。TCN 使用因果卷积、扩张卷积、残差连接、flatten、128 神经元全连接层、dropout 和 softmax 分类层。

6. 评估  
   使用测试准确率、测试损失、precision、recall、F1-score、support 和混淆矩阵评估模型。重点观察 TCN 是否在整体性能和各攻击类别上优于基线模型。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 Edge-IIoTset / DNN-EdgeIIoT CSV。任务为 15 类分类，类别包括 Normal、DDoS UDP、DDoS ICMP、SQL injection、DDoS TCP、Vulnerability scanner、Password、DDoS HTTP、Uploading、Backdoor、Port Scanning、XSS、Ransomware、Fingerprinting、MITM。

2. 预处理  
   删除重复行。删除时间戳、IP 地址、无意义协议字段和 icmp.unused。对 HTTP、DNS、MQTT 相关类别字段做编码。对类别型特征 one-hot。用哈希方式删除内容重复列。用 Chi-Squared test 排序和选择与 Attack Type 相关的特征。用 stratified sampling 将数据缩小为 25%，保持类别比例。最终样本数为 486,362。

3. 数据划分  
   训练集 70%，测试集 20%，验证集 10%。论文给出的规模为：训练集 340,452，测试集 97,273，验证集 48,637。

4. 特征缩放  
   使用 StandardScaler。只在训练集上 fit，然后 transform 训练、验证和测试集，避免测试集信息泄漏。

5. 模型/基线  
   基线包括 1D CNN、CNN-GRU、CNN-LSTM、CNN-BiLSTM、CNN-LSTM-GRU。提出模型为 TCN，包含三个残差块，不同 dilation rate，随后 flatten、128 维全连接层、dropout、softmax。

6. 训练设置  
   环境为 Google Colab，NVIDIA T4 GPU。Python 3.10+，TensorFlow 2.17。训练 5 epochs，batch size 32，learning rate 0.001，Adam optimizer，loss 为 Sparse Categorical Crossentropy。

7. 指标  
   整体指标：test accuracy、test loss。分类指标：precision、recall、F1-score、support。辅助分析：TCN 混淆矩阵。

8. 消融/敏感性  
   论文没有严格做消融实验。没有分别移除 dilation、residual connection、dropout，也没有测试不同 dilation rate、残差块数量、采样比例、epochs、batch size 对结果的影响。因此这部分是论文实验设计的短板。

9. 结果核查  
   应重点核查三点：第一，TCN 的 96.72% 是否在多次随机划分下稳定；第二，Normal 类占比极高时，accuracy 是否掩盖少数类不足；第三，MITM 和 Fingerprinting 的 support 分别只有 18 和 39，F1=1.00 或 precision=1.00 的可信度需要结合混淆矩阵和原始样本分布复核。

## 8. 关键结果、结论与证据

整体性能方面，TCN 最优：

| 模型 | Test Accuracy | Test Loss |
|---|---:|---:|
| 1D CNN | 0.9618 | 0.0760 |
| CNN-GRU | 0.9638 | 0.0732 |
| CNN-LSTM | 0.9635 | 0.0739 |
| CNN-BiLSTM | 0.9640 | 0.0756 |
| CNN-LSTM-GRU | 0.9640 | 0.0733 |
| TCN | 0.9672 | 0.0668 |

TCN 相比最佳混合基线 CNN-BiLSTM / CNN-LSTM-GRU，准确率提升约 0.32 个百分点，loss 下降更明显。这个提升不算巨大，但方向一致：TCN 同时取得最高 accuracy 和最低 loss。

分类报告显示，TCN 对大类和若干攻击类表现较强：

- Normal：precision、recall、F1 均为 1.00
- DDoS UDP、DDoS ICMP：F1 均为 1.00
- DDoS TCP：F1 为 0.96
- Vulnerability scanner：F1 为 0.95
- Backdoor：F1 为 0.97
- Ransomware：F1 为 0.95
- Uploading：F1 为 0.75
- SQL injection：recall 为 1.00，但 precision 只有 0.55，说明模型倾向于把一部分其他类别误判为 SQL injection
- Password：recall 只有 0.33，F1 为 0.48，是明显短板
- Fingerprinting：support 只有 39，recall 为 0.36，F1 为 0.53，少数类识别不稳

关键结论是：TCN 的优势主要来自扩张卷积和残差块对多尺度依赖的建模，而不是单纯加深网络。它对常见攻击和部分类别的检测非常强，但对极少数类、边界模糊类攻击仍不够稳健。

## 9. 局限性与待解决问题

1. 数据集单一  
   论文只在 Edge-IIoTset 上验证，没有跨数据集测试，例如 CIC-IDS2017/2018、IoT-23、Bot-IoT、TON_IoT 等。因此“泛化到真实网络或其他 IoT 场景”的结论还不充分。

2. 类别不平衡问题没有被充分解决  
   Normal 有 349,906 条，而 MITM 只有 90 条，Fingerprinting 只有 213 条。测试集中 MITM support 仅 18，Fingerprinting support 仅 39。少数类的指标波动会很大，单次划分下的高 precision 或 F1 不应过度解读。

3. 没有报告训练时间、推理延迟和参数量  
   论文反复强调 TCN 相比 RNN 更快、更适合并行，但实验表格没有给出训练耗时、吞吐量、模型大小、FLOPs 或边缘设备推理延迟。这使得“适合边缘部署”的论证不够完整。

4. 缺少真正的消融实验  
   没有回答残差连接、扩张卷积、因果卷积、残差块数量、dropout 各自贡献多少。当前只能说明完整 TCN 比几个基线略好，不能证明每个设计组件都是必要的。

5. 时序构造细节不够清楚  
   Edge-IIoTset 是 CSV 特征表。论文说 TCN 捕获 temporal dependencies，但没有充分解释样本如何构造成序列窗口、窗口长度是多少、是否按流/session/时间排序、是否存在打乱后仍称为时序建模的问题。这是复现实验时最需要核查的地方。

6. 指标解释存在 accuracy 偏置  
   在 Normal 类占比极高的数据上，accuracy 容易偏高。论文虽然给出分类报告，但讨论仍偏重整体准确率。更适合 IDS 的评估还应包括 macro-F1、per-class recall、false alarm rate、detection rate、PR-AUC 等。

7. 正文包未截断  
   本次理解基于完整提供的正文包，不存在因正文截断造成的缺页问题。但如果要复现实验，仍建议回到 PDF 核对 Figure 1、Figure 2 以及表格排版中可能丢失的结构细节。

## 10. 与本项目的关系

该论文与“入侵检测与网络异常检测”强相关，尤其适合作为时序深度模型在 IoT/IIoT 安全检测中的代表工作。

对本项目有三点直接价值：

1. 可作为 TCN 用于网络异常检测的基线方案  
   如果本项目关注日志、KPI、流量或云原生指标的时序异常检测，TCN 的扩张卷积和残差结构可作为轻量替代 LSTM/GRU 的候选模型。

2. 可借鉴其多类别攻击建模方式  
   本文不是二分类，而是 15 类攻击识别。对于需要区分异常类型、攻击阶段、根因类别的项目，多分类设置比“normal/attack”更有参考价值。

3. 可作为反面提醒：必须说清楚“时序样本如何构造”  
   如果本项目使用 TCN，不能只把表格特征 reshape 后送入模型，而要明确时间窗口、排序依据、采样粒度、窗口标签策略，否则“时序建模”的科学性会受到质疑。

## 11. 代码对照分析

本地代码包状态为“未发现；无”，因此无法逐文件对应论文实现。若后续找到作者代码或自行复现，建议按以下线索建立目录映射：

| 论文环节 | 可能对应文件/目录 | 应检查内容 |
|---|---|---|
| 数据读取 | `data_loader.py`、`dataset.py`、`preprocess.py` | 是否读取 DNN-EdgeIIoT CSV，是否使用 Attack Type 作为 15 类标签 |
| 清洗与删列 | `preprocess.py`、`feature_engineering.py` | 是否删除 timestamp、IP、icmp.unused、重复行、重复列 |
| 编码 | `encoding.py`、`preprocess.py` | HTTP/DNS/MQTT 字段是 label encoding 还是 one-hot，训练/测试是否共享 encoder |
| 特征选择 | `feature_selection.py` | 是否实现 Chi-Squared test，选择了多少特征，是否只在训练集 fit |
| 采样 | `sampling.py` | 是否使用 stratified sampling，比例是否为 0.25 |
| 标准化 | `scaler.py`、`preprocess.py` | StandardScaler 是否只在训练集 fit |
| 模型定义 | `models/tcn.py` | 是否包含 causal conv、dilated conv、residual block、dropout、softmax |
| 基线模型 | `models/cnn.py`、`models/cnn_lstm.py`、`models/cnn_gru.py` | 是否实现 1D CNN、CNN-GRU、CNN-LSTM、CNN-BiLSTM、CNN-LSTM-GRU |
| 训练 | `train.py` | epochs=5、batch_size=32、lr=0.001、Adam、SparseCategoricalCrossentropy |
| 评估 | `evaluate.py`、`metrics.py` | accuracy、loss、classification_report、confusion_matrix |
| 复现实验配置 | `config.yaml`、`requirements.txt` | TensorFlow 2.17、Python 3.10+、随机种子、GPU 设置 |

特别需要警惕两类复现风险：

第一，数据泄漏。编码、特征选择、标准化如果在全量数据上 fit，再划分训练/测试，会高估性能。

第二，序列伪造。TCN 需要明确输入 shape，例如 `[batch, time_steps, features]`。如果只是把 tabular feature vector 当作“时间维”，那么模型捕获的是特征位置局部关系，而不是网络流量的真实时间依赖。

## 12. 本篇精华

1. 本文的核心价值是把 TCN 引入 Edge-IIoTset 的 15 类入侵检测，而不是只做 normal/attack 二分类。

2. TCN 的优势来自 causal convolution、dilated convolution 和 residual block：既扩大感受野，又避免 RNN 的串行训练瓶颈。

3. 在同一实验设置下，TCN 达到 96.72% accuracy 和 0.0668 loss，优于 1D CNN 与多种 CNN-RNN 混合模型。

4. 整体准确率提升不大，但 loss 更低，说明 TCN 的预测置信分布可能更稳定。

5. 少数类仍是短板，尤其 Password 和 Fingerprinting；MITM support 极小，相关指标不宜过度解读。

6. 论文最大方法学疑点是没有充分说明 Edge-IIoTset 表格样本如何构造成真正的时间序列。

7. 若用于综述，可将本文归为“基于时序卷积的 IoT/IIoT 多分类入侵检测”，并与 CNN-LSTM/CNN-GRU 类方法对比。

8. 若用于项目复现，必须补充消融实验、跨数据集验证、推理时延和边缘部署成本评估。

## 13. 建议精读路线

1. 先读 Introduction 和 Related Works  
   抓住作者的论证链：传统 ML 不够，CNN 时序不足，RNN 混合模型成本高，TCN 是替代方案。

2. 精读 Proposed Method 中的模型部分  
   重点看 TCN 的三个 residual blocks、dilation、flatten、dense、dropout、softmax。复现时要回 PDF 核对 Figure 1 的结构细节。

3. 精读 Dataset 与 Preprocessing  
   这是论文可信度的关键。特别关注删列、编码、Chi-Squared feature selection、stratified sampling 和 StandardScaler 的顺序。

4. 对照 Table III 看整体性能  
   重点比较 TCN 与 CNN-BiLSTM、CNN-LSTM-GRU 的差距。注意提升幅度并不大，不能夸大。

5. 对照 Table IX 看分类细节  
   不要只看 accuracy。重点分析 SQL injection、Password、Fingerprinting、Uploading、XSS 等类别的 precision/recall/F1。

6. 最后读 Conclusion  
   提炼作者承认的局限：单数据集、部署复杂度、动态环境评估不足、可解释性不足。对于科研汇报，这些正好可以转化为后续工作方向。

<!-- codex-cli-deep-read: complete -->
