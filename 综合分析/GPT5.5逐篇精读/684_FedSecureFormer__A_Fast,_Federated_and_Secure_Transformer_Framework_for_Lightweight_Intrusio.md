# [684] FedSecureFormer: A Fast, Federated and Secure Transformer Framework for Lightweight Intrusion Detection in Connected and Autonomous Vehicles

## 1. 基本信息

- 题名：FedSecureFormer: A Fast, Federated and Secure Transformer Framework for Lightweight Intrusion Detection in Connected and Autonomous Vehicles
- 年份：2026
- 来源：IEEE Transactions on Vehicular Technology
- DOI：10.1109/TVT.2026.3681531
- 研究对象：车联网 / CAV 场景中的轻量级入侵检测
- 方法关键词：Transformer、Federated Learning、Differential Privacy、VeReMi Extension、Hist-AttnGAN、Jetson Nano
- 代码状态：本地未发现该论文对应开源代码包
- 正文状态：本次正文包完整，未截断；但论文为 IEEE accepted author version，正式出版版本仍可能有细节变化

## 2. 中文翻译与核心摘要

这篇论文提出 FedSecureFormer，一个面向网联自动驾驶车辆 CAV 的轻量级 Transformer 入侵检测框架。它试图同时解决四件事：检测精度、边缘实时性、联邦部署、隐私保护。

论文的核心思路是：用一个仅约 1.7M 参数的 6 层 encoder-only Transformer，对 VeReMi Extension 中车辆广播消息序列进行多分类检测。每个样本是 20 个时间步、9 个特征的序列。模型不是直接使用普通均值池化，而是在编码器之后加入多头注意力池化，用可学习查询向量从时间序列中提取攻击相关表示。

结果上，集中式训练达到 93.69% 准确率，整体 recall 为 82.05%，F1 为 84.04%。在联邦学习中使用 FedAvg，20 个客户端、100 轮、每轮 1 个本地 epoch，性能相对集中式下降约 1.03%。加入差分隐私后，最佳配置为 noise multiplier 0.001、clip norm 5，准确率为 82.7%，隐私预算为 ε=6.329、δ=1e-5。论文还用带 LSTM 与注意力的直方图约束 GAN 生成未知攻击样本，FedSecureFormer 对这类未知样本达到 88% 检测准确率。最突出的部署结果是 Jetson Nano 上单车推理时间 3.7775 ms，显著快于对比方法。

## 3. 论文解决的具体问题

论文瞄准的不是一般 IDS，而是 CAV 中“要能部署”的入侵检测问题。作者认为现有工作主要有几类不足：

1. 过度关注检测准确率，忽略实时推理  
   CAV 中攻击检测不是离线分类任务。车辆与 RSU 需要快速响应，慢几十或几百毫秒可能已经影响告警、证书吊销或车辆行为决策。

2. 模型偏大或计算不适合边缘设备  
   很多 Transformer 或深度模型能提升准确率，但在 Jetson Nano、Raspberry Pi 一类设备上部署不现实。

3. CAV 数据天然分布式且隐私敏感  
   车辆和 RSU 不宜集中上传原始轨迹、速度、加速度等信息。集中训练存在隐私暴露、单点故障和非 IID 适应性差的问题。

4. 攻击类别复杂且长尾严重  
   VeReMi Extension 中正常类 A(0) 有 165373 个序列，而很多攻击类只有约 3700 个序列。类别不平衡会导致模型看似准确率高，但对少数攻击类别召回不足。

5. 未知攻击检测不足  
   车联网攻击形式会演化，单纯在已知攻击类别上分类不能说明模型面对新型异常时是否可靠。

## 4. 创新点深度提炼

第一，论文把“轻量级 Transformer”作为核心，而不是直接套用大模型或复杂混合网络。FedSecureFormer 使用 6 层 encoder-only Transformer、2 个自注意力头、64 维投影，参数量控制在 1.7M。它保留 Transformer 捕捉时间依赖的能力，同时避免大规模 encoder 带来的部署负担。

第二，注意力池化是模型设计中比较关键的细节。普通 mean pooling 对时间步一视同仁，而攻击行为可能只在局部时间段显著。论文使用 4 头 multi-head attention pooling，让模型用可学习查询从编码后的序列中提取更有判别力的上下文。

第三，论文不是只给集中式结果，而是把同一模型放入 Flower 联邦学习框架，用 FedAvg 和 FedProx 对比。FedAvg 在 20 客户端设置下效果最好，说明这个模型在分布式训练中没有明显崩塌。

第四，差分隐私不是停留在概念层面。作者实际加入梯度裁剪和高斯噪声，并用 RDP accountant 给出 ε、δ。虽然 ε=6.329 不算非常强隐私，但至少把隐私-性能权衡量化了。

第五，未知攻击检测采用 Hist-AttnGAN 辅助评估。GAN 生成的样本不是为了扩充训练集，而是作为未知攻击测试数据，检验分类器对未见异常序列的反应。这一点比只在固定测试集上报告高准确率更接近安全问题本质。

第六，Jetson Nano 部署结果是本文最有工程说服力的部分。3.7775 ms/vehicle 的推理延迟使论文从“算法有效”推进到“边缘可用”。

## 5. 科学问题与研究假设

核心科学问题可以概括为：在 CAV 资源受限、数据分散且攻击类别不平衡的环境下，能否设计一个既轻量、又能捕捉时序依赖、还能通过联邦学习和差分隐私部署的 IDS？

论文隐含了几个研究假设：

1. CAV 攻击行为在短时间窗口内具有可学习的时序模式  
   因此 20 个时间步、9 个运动相关特征足以支撑分类。

2. 自注意力比 CNN-LSTM、TCN 更适合捕捉跨时间步的攻击依赖  
   尤其是 replay、delay、Sybil、DoS 等行为，不一定只表现为局部突变。

3. 小型 Transformer 可以达到接近甚至超过复杂模型的检测效果  
   模型容量不是越大越好，6 层、2 头、64 维投影可能正好处在性能与延迟的平衡点。

4. FedAvg 对该任务已经足够稳定  
   在相对同质的客户端设置中，FedProx 的近端项反而可能压低性能。

5. 适度 DP 噪声可以提供隐私保护，同时不显著破坏模型效用  
   这一假设依赖精细调参，因为噪声稍大性能就明显下降。

## 6. 科学方法与技术路线

技术路线可以分为五层。

第一层是数据建模。论文使用 VeReMi Extension 数据集，将车辆消息转为固定长度序列。每个样本为 `[20, 9]`，包括时间戳以及位置、速度、加速度、方向等运动特征。标签为 A(0) 正常与 A(1)-A(19) 攻击类别。

第二层是轻量 Transformer。输入先经过线性投影到 64 维，再加入可学习绝对位置编码。之后进入 6 层 encoder，每层包含多头自注意力、FFN、LayerNorm 和残差连接。编码后使用多头注意力池化形成全局表示，再接全连接分类层和 softmax。

第三层是集中式训练与结构消融。作者比较 CNN-LSTM、BiLSTM、TCN、不同层数/注意力头/池化方式的 Transformer，确定最终配置。

第四层是联邦学习部署。各客户端本地训练 FedSecureFormer，只上传模型参数或梯度更新，服务器用 FedAvg 聚合。类别不平衡通过 weighted cross-entropy 处理。

第五层是隐私与未知攻击验证。DP 部分对梯度裁剪并加入高斯噪声，使用 RDP accountant 计算隐私预算。未知攻击部分使用 Hist-AttnGAN 生成未见序列，再用 FedSecureFormer 判断是否能检测。

## 7. 实验设计与实验步骤

1. 数据  
   使用 VeReMi Extension。攻击类别包括 A(0) 正常，以及 A(1)-A(19) 共 19 类攻击。正常类远多于多数攻击类，类别分布明显不平衡。

2. 预处理  
   从原始车辆消息中选取 9 个特征。使用滑动窗口构造序列，窗口大小为 20，步长为 10。短于 20 的序列丢弃。最终每个样本形状为 `[20, 9]`。数据按 70:15:15 划分为训练、验证、测试，并保留原始类别不平衡。

3. 模型与基线  
   基线包括多种 Hybrid CNN-LSTM、BiLSTM 变体和 TCN。Transformer 变体比较 mean pooling、single-head attention pooling、multi-head attention pooling，不同 encoder 层数和注意力头数。

4. 训练  
   集中式训练使用 Adam，学习率 0.0003，batch size 128，训练 100 epochs，损失函数为 smooth L1。联邦学习使用 Flower，20 clients、100 rounds、每轮 1 local epoch、batch size 64，损失函数改为 weighted cross-entropy。

5. 指标  
   报告 accuracy、precision、recall、F1-score，并给出按攻击类别的 recall。部署部分报告 Jetson Nano 上 data setup、prediction 和总 inference time。

6. 消融与敏感性  
   消融包括 encoder 层数、attention heads、pooling 方法、projection dimension。FL 部分比较 FedAvg 与 FedProx，DP 部分比较不同 noise multiplier 和 clip norm。

7. 未知攻击评估  
   使用 Hist-AttnGAN 生成未见攻击序列。GAN 由 LSTM、multi-head attention、feature-wise projection heads 和 LSTM discriminator 组成。生成样本通过 FedSecureFormer 检测，并基于模型置信度尝试 0.3 到 0.9 的 similarity threshold，最终阈值 0.5 最优。

8. 结果核查  
   需要重点核查三点：一是整体 accuracy 高是否由 A(0) 正常类主导；二是 A(11)、A(12)、A(17)、A(19) 等难类表现是否足够；三是 Jetson Nano 推理时间是否包含完整预处理链路，还是只包含模型前向推理。

## 8. 关键结果、结论与证据

集中式 FedSecureFormer 达到 accuracy 0.9369、precision 0.8798、recall 0.8205、F1 0.8404。相比 TCN 的 accuracy 0.8918、recall 0.8179，FedSecureFormer 主要提升在总体准确率和部分类别 recall。

按类别看，模型在 A(3)、A(7)、A(8)、A(18) 上 recall 达到 1.0，在 A(1)、A(5)、A(6)、A(13)、A(16) 上也接近或超过 0.95。但它并非所有类别都强：A(11) recall 0.5297，A(12) 0.5888，A(17) 0.3209，A(19) 0.7133，说明 replay、delay、traffic congestion sybil 等类别仍是短板。

联邦学习中，FedAvg 最优。论文称相对集中式性能下降约 1.03%，表明模型可迁移到分布式训练场景。FedProx 表现较差，尤其在 5、7 客户端实验中 recall 和 precision 都不理想，说明该任务下近端约束并未带来收益。

差分隐私实验表明噪声敏感。noise multiplier 超过 0.5 时性能明显下降。最佳 DP 配置 accuracy 0.827、precision 0.898、recall 0.749、F1 0.797，隐私预算为 `(ε=6.329, δ=1e-5)`。

部署结果最强：Jetson Nano 平均推理时间 3.7775 ms/vehicle，对比文献中 251-512 ms 的方法有数量级提升。这个结果支撑了“lightweight”和“real-time”的主张。

## 9. 局限性与待解决问题

第一，未知攻击检测的定义还不够严格。GAN 生成的“未知攻击”是否真的代表现实中新型攻击，仍需要更多物理和协议层约束验证。文中也承认生成分布较窄，目标不是多样性，这会削弱未知攻击评估的外推性。

第二，类别不平衡仍然明显影响难类。A(17) recall 只有 0.3209，A(11)、A(12) 也偏低。整体准确率 93.69% 不能掩盖个别攻击类别检测不足。

第三，FL 场景的 non-IID 程度没有展开得足够细。论文说模拟真实流量差异，但没有充分说明客户端划分策略、每个客户端类别分布、是否存在极端 label skew 或 feature skew。

第四，DP 设置偏弱且敏感。ε=6.329 是可报告的隐私保证，但不是很强；noise multiplier 稍大性能迅速下降，说明隐私强度与实用检测能力之间仍有张力。

第五，Jetson Nano 推理结果很有价值，但还需确认端到端链路。真实部署中还包括消息解析、窗口维护、标准化、通信、告警逻辑和 RSU/CA 联动，论文主要报告模型推理时间。

第六，论文没有提供本地代码包，复现实验需要重新实现数据处理、模型、FL、DP、GAN 和部署基准。

## 10. 与本项目的关系

对于“入侵检测与网络异常检测”方向，这篇论文强相关。它把异常检测从单机分类推进到 CAV 边缘安全场景，覆盖了时序建模、类别不平衡、联邦学习、隐私保护和边缘推理。

对 IoT、车联网、工业互联网与边缘安全方向，它提供了一个可参考范式：轻量时序模型 + 分布式训练 + 隐私约束 + 设备端延迟评估。这个组合比单纯追求 SOTA accuracy 更适合工程安全系统。

对本项目综述而言，可以把它归入“面向车联网的轻量联邦 Transformer IDS”。它的价值不只是模型结构，而是把 CAV IDS 的实用约束同时纳入实验：攻击多分类、未知攻击、FL、DP、Jetson Nano。

## 11. 代码对照分析

本地未发现该论文对应开源代码包，因此不能给出真实源码文件级对应关系，也不能确认作者实现细节。下面是基于论文方法的可复现代码模块映射，不是实际存在的文件名。

- 数据预处理模块  
  应实现 VeReMi Extension 读取、9 特征抽取、按车辆或消息序列排序、窗口大小 20/步长 10 的滑窗、短序列丢弃、70:15:15 划分、类别分布统计和 class weight 计算。

- 模型模块  
  应包含 `FedSecureFormer`：线性投影、可学习位置编码、6 层 Transformer encoder、2-head self-attention、FFN、multi-head attention pooling、分类头。还应包含 CNN-LSTM、BiLSTM、TCN 等基线。

- 训练模块  
  集中式训练需支持 Adam、learning rate 0.0003、batch size 128、100 epochs、smooth L1 loss，并输出 per-class metrics。

- 联邦学习模块  
  应基于 Flower 实现 client/server、FedAvg、FedProx、本地 epoch、round 数、客户端数量、按样本数加权聚合和 weighted cross-entropy。

- 差分隐私模块  
  应实现 per-batch gradient clipping、高斯噪声注入、noise multiplier、clip norm，以及 RDP accountant 计算 `(ε, δ)`。

- GAN 模块  
  应实现 Hist-AttnGAN：LSTM generator、multi-head attention、9 个 feature projection heads、LSTM discriminator、Wasserstein loss、gradient penalty、CDF histogram loss。

- 评估与部署模块  
  应输出 accuracy、precision、recall、F1、per-class recall、未知攻击阈值实验、Jetson Nano 推理时间。部署计时应区分数据准备、模型预测和总耗时。

## 12. 本篇精华

1. FedSecureFormer 的核心贡献不是“用了 Transformer”，而是把 Transformer 压到 1.7M 参数，并在 Jetson Nano 上做到 3.7775 ms/vehicle。

2. 论文把 CAV IDS 从集中式检测扩展到 FedAvg 联邦部署，20 客户端下性能下降很小，证明轻量模型适合分布式边缘训练。

3. 多头注意力池化是关键结构选择，比 mean pooling 更适合从车辆时序消息中抽取攻击片段。

4. VeReMi Extension 上整体指标很强，但 A(11)、A(12)、A(17) 等难类仍暴露了 replay、delay、Sybil 类攻击检测不足。

5. 差分隐私可用但脆弱：最佳 DP-FL 配置仅损失约 4.04%，但噪声稍大性能会明显下滑。

6. Hist-AttnGAN 用于未知攻击检测是一个有启发的评估设计，但生成样本是否覆盖真实未知威胁仍需谨慎看待。

7. FedAvg 明显优于 FedProx，说明该实验设置下客户端异质性可能没有强到需要近端正则。

8. 这篇论文适合作为“轻量化 + 联邦学习 + 车联网 IDS + 边缘部署”的代表性工作引用。

## 13. 建议精读路线

建议先读 Introduction 和 Literature Survey，抓住作者批评现有工作的四个点：实时性、轻量化、联邦隐私、未知攻击。

第二步精读 Section IV，重点看 FedSecureFormer 的结构：6 层 encoder、2 个注意力头、4 头注意力池化、64 维投影，以及 FL-DP 的训练公式。

第三步读 Dataset Specification，确认 20×9 输入、滑窗步长 10、类别分布和训练/验证/测试划分。这部分决定能否复现。

第四步重点读 Table III、Table IV、Table V、Table VIII、Table IX。它们分别对应结构消融、分类效果、SOTA 对比、DP 权衡和部署延迟。

最后反向审视局限：不要只引用 93.69% accuracy，应同时报告 A(17) recall 0.3209、A(11) 0.5297、A(12) 0.5888，以及 DP 与未知攻击评估的不确定性。

<!-- codex-cli-deep-read: complete -->
