# [490] MKF-ADS: Multi-Knowledge Fusion Based Anomaly Detection System in Vehicular Control Area Networks

## 1. 基本信息

- 论文题名：MKF-ADS: Multi-Knowledge Fusion Based Anomaly Detection System in Vehicular Control Area Networks
- 作者：Pengzhou Cheng, Shouxuan Liu, Zongru Wu, Lixing Tan, Gongshen Liu
- 年份：2025
- 来源：IEEE Transactions on Vehicular Technology, Vol. 74, No. 9
- DOI：10.1109/TVT.2025.3564575
- 主题：车载 CAN 总线异常检测、预测式入侵检测、多知识融合、知识蒸馏、轻量化模型
- 数据集：HCRL Car-Hacking CAN intrusion dataset；ROAD CAN intrusion dataset
- 代码状态：本地未发现该论文对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文提出 MKF-ADS，一个面向车载 CAN 总线的多知识融合异常检测系统。论文的核心判断是：CAN 总线缺乏认证和加密，攻击者一旦通过 OBD-II、无线接口或被攻陷 ECU 接入总线，就可以注入、重放、伪装或篡改消息；而现有异常检测模型往往只建模时间关系、空间关系或上下文关系中的一部分，导致复杂攻击下误报高、漏报高，或者模型过重，不适合车载环境。

MKF-ADS 采用预测式异常检测范式：只学习正常 CAN 消息中物理信号的演化规律，在线阶段预测下一时刻信号，并用真实值与预测值之间的偏差判断异常。方法上，它先用 READ 逆向工程算法从 CAN payload 中抽取有意义的物理信号边界，降低 64-bit 原始数据维度；然后构造两个知识模块：

- STcAM：轻量学生模型，用 Conv1D 提取信号间空间特征，用 BiLSTM 建模时间依赖，用 soft attention 聚焦关键时间步。
- PatchST：教师模型，将多变量时间序列拆成独立单变量序列，通过 patch-based Transformer 捕捉长程上下文知识。

最后，论文用跨知识蒸馏把 PatchST 的上下文预测能力迁移给 STcAM，使在线检测主要依赖轻量化 STcAM，同时获得一部分 Transformer 的上下文建模收益。

## 3. 论文解决的具体问题

论文解决的是车载 CAN 总线异常检测中的三个具体矛盾。

第一，CAN 协议本身不提供身份认证、加密和消息完整性保护。攻击者只要能控制某个 ECU 或接入 OBD-II，就可能发送高优先级消息、随机消息、重放历史消息、伪造合法 ECU 消息，甚至在 masquerade attack 中先删除合法消息再注入伪造消息。

第二，现有预测式 IDS 的特征建模不足。只用 LSTM 的方法能捕捉时间依赖，但没有充分利用 payload 内部物理信号结构；CNN-LSTM 能增加空间特征，但对长程上下文依赖仍弱；BERT/GPT 类模型能建模上下文，但参数量和计算开销不适合车载实时部署。

第三，车载 IDS 不能只追求离线 F1-score。它还必须控制误报率、检测时间、模型参数量和内存占用。论文特别强调 IVN 资源受限，因此要在复杂知识建模与轻量部署之间取得平衡。

## 4. 创新点深度提炼

1. **把 CAN 异常检测明确建模为物理信号预测问题**  
   它不是直接分类 CAN 帧，也不是重构整段序列，而是对同一 CAN ID 下的多变量物理信号进行下一步预测。异常来自“真实信号偏离正常演化轨迹”。

2. **用 READ 先恢复有效信号边界，避免粗暴处理 64-bit payload**  
   论文没有把每个 CAN frame 的 64 个 bit 等价看待，而是用 bit flip rate 和边界判定抽取连续物理信号。例如 CAN ID 0x260 从 64 bit 缩减为 41 bit 有效信号。这一点对车载场景很关键，因为不同 bit 的语义和变化规律并不相同。

3. **STcAM 是为车载部署裁剪过的空间-时间-注意力模块**  
   Conv1D 抓局部空间关系，BiLSTM 抓窗口内双向时间关系，attention 给关键时间步更高权重。它不是单纯堆深模型，而是把 filter size、hidden units 等参数压到较小规模。

4. **PatchST 引入上下文知识，但不直接作为在线主模型**  
   PatchST 借鉴 PatchTST 思路，把长时间序列切成 patch，降低 Transformer token 数和注意力复杂度；同时采用 channel-independence，把多变量序列拆成多个单变量序列处理。

5. **跨知识蒸馏是本文真正的融合机制**  
   PatchST 作为教师，STcAM 作为学生。学生既用 MAE 学真实预测目标，也通过 KL divergence 模仿教师预测。这比简单拼接 CNN、LSTM、Transformer 更符合车载部署约束。

6. **实验覆盖攻击类型较全，并加入真实车载效率评估**  
   论文覆盖 DoS、Fuzzy、Suspension、Replay、Spoofing、Masquerade 六类攻击，还在 ROAD 数据集和真实车辆 Jetson AGX Xavier 上验证时间和资源开销。

## 5. 科学问题与研究假设

核心科学问题是：在车载 CAN 总线异常检测中，如何在低计算资源约束下融合空间、时间和上下文知识，从而提升复杂攻击尤其是细粒度伪造攻击的检测稳定性？

论文隐含了几个研究假设：

- 正常 CAN 消息具有稳定的周期性和物理信号演化规律，可以通过历史窗口预测未来信号。
- 攻击消息即使使用合法 CAN ID 或接近正常值，也会在时间、空间或上下文关系上造成可检测偏差。
- 空间-时间知识与上下文知识是互补的：前者轻量、适合部署，后者表达力强、适合作为教师。
- 知识蒸馏可以把复杂 Transformer 的上下文能力迁移到轻量学生模型中，从而降低在线检测成本。
- 对 CAN payload 先做信号级抽取，比直接按 64-bit 建模更符合车辆物理语义，也更利于模型收敛。

## 6. 科学方法与技术路线

技术路线可以概括为“信号抽取 → 时间序列预测 → 多知识蒸馏 → 阈值检测”。

首先，论文按 CAN ID 分组处理消息。对每个候选 ID 的 payload 使用 READ 和边界划分算法，恢复有效物理信号边界。随后用滑动窗口构造多变量时间序列样本，窗口长度候选为 8、16、32、64，最终主要采用 16。

其次，对每个窗口输入 `X ∈ R^{M×T}`，预测下一时刻或未来若干步的物理信号 `Y ∈ R^{M×1}`。输入经过 min-max 归一化，保证不同信号处在相近数值范围。

模型部分分两路：

- STcAM 路径：`Conv1D → ReLU → BiLSTM → soft attention → dropout → dense prediction`
- PatchST 路径：`channel split → patching → embedding + position encoding → Transformer encoder → flatten → linear head`

训练时，损失函数由两部分组成：

- `Lpred`：学生预测值与真实值之间的 MAE。
- `LCKD`：学生 cross-head 输出与教师 PatchST 输出之间的 KL divergence。

最终目标为 `L = αLpred + βLCKD`。在线检测时，主要根据预测误差构造 anomaly score，并用正常消息误差分布的 K-sigma 右边界作为阈值。

## 7. 实验设计与实验步骤

**数据**

实验主要使用 HCRL Car-Hacking CAN intrusion dataset。该数据来自真实车辆 OBD-II 端口，字段包括 Timestamp、CAN ID、DLC、DATA[0]-DATA[7]。论文还使用 ROAD 数据集验证泛化性，尤其是 spoofing 和 masquerade 攻击。

**预处理**

1. 按 CAN ID 分离原始 CAN 消息。
2. 使用 READ 算法和边界判定提取有效物理信号。
3. 仅保留关键功能区域、周期约 10 ms、有效特征数大于 15 的 CAN ID。
4. 用滑动窗口 `T` 聚合最近消息，形成二维多变量时间序列。
5. 将 bit/信号转换为十进制数值。
6. 对每个特征做 min-max normalization。
7. 按 80% 训练、20% 测试划分正常数据。

**模型/基线**

对比模型包括：

- LSTM-P：基于 LSTM 预测下一包 64-bit 表示。
- LSTM-E：改进预测目标和优化方式的 LSTM。
- DeepConvGRU：空间卷积加 GRU。
- ConvLSTM-GNB：空间-时间预测模块加 GNB，论文为公平只取其预测部分。
- CLAM：CNN-LSTM 加 attention。
- STcAM：本文学生模块。
- PatchST：本文教师模块。
- MKF-ADS：本文最终蒸馏融合模型。

**训练**

论文使用 PyTorch 1.13，Adam 优化器，学习率 `1e-2`，训练 3000 epochs，并使用 early stopping。PatchST 的 patch length 为 4，stride 为 1，embedding dimension 为 8，Transformer heads 为 2。STcAM 通过 grid search 选择窗口长度、卷积 filter size、LSTM hidden units 和 batch size。

**指标**

预测性能使用 MAE、RMSE、MAPE。检测性能使用 Precision、Recall、F1-score、Error Rate、False Alarm Rate。论文把异常序列作为正类，正常序列作为负类。

**消融/敏感性**

论文做了几类敏感性与泛化检查：

- 窗口长度、filter size、hidden units、batch size 的 grid search。
- K-sigma 阈值中 K 的变化对误报和漏报的影响。
- 不同 CAN ID 上的预测和检测效果。
- 未来 1 到 5 个 time steps 的多步预测效果。
- ROAD 数据集上的跨场景验证。
- 真实车载设备上的参数量、FLOPs、MACs、内存、检测时间对比。

**结果核查**

论文先确认正常消息预测误差足够低，再在六类攻击下生成或选取异常序列，观察 anomaly score 是否越过阈值。粗粒度攻击中，异常值明显偏离正常轨迹；细粒度攻击中，攻击值接近正常值，但频率、时序或上下文不一致仍会触发偏差。

## 8. 关键结果、结论与证据

预测结果上，MKF-ADS 的 MAE 达到约 0.0305，优于 CLAM 的 0.0391，也优于单独 STcAM 的 0.0325。论文认为提升来自 PatchST 上下文知识对 STcAM 的蒸馏增强。PatchST 单独预测误差最低，但不适合作为在线部署主模型。

检测结果上，MKF-ADS 在六类攻击中整体保持较高 F1-score。论文给出的关键数字包括：

- DoS：Precision 98.7%，Recall 100%，F1 99.3%
- Fuzzy：Precision 96.7%，Recall 100%，F1 98.3%
- Replay：Precision 96.1%，Recall 100%
- Suspension：Precision 98.6%，Recall 97.2%
- Spoofing：F1 约 95.6%
- Masquerade：Precision 91.6%，Recall 87.5%，F1 约 93.3%

从这些结果看，模型对注入型攻击、随机攻击和时序错位攻击最强，对 masquerade 这种“删除正常消息再注入伪造消息”的隐蔽攻击最困难。

效率结果是论文的重要支撑。MKF-ADS 仅约 1,952 个参数，检测时间约 2.28 ms，并在 NVIDIA Jetson AGX Xavier 上完成车辆级评估。相比更重的 CNN-RNN 或 Transformer 类方法，它的计算成本明显更适合车载 IVN 部署。

论文的总结性结论是：通过让轻量 STcAM 学习 PatchST 的上下文知识，MKF-ADS 在预测误差、检测 F1、误报率和部署效率之间取得了较好的折中。

## 9. 局限性与待解决问题

第一，模型仍然依赖 CAN ID 分组和候选 ID 筛选。论文只选择了周期性强、有效特征数足够多的 CAN ID，因此对于低频、非周期、事件触发型 CAN 消息，效果仍需单独验证。

第二，阈值机制仍是 K-sigma 统计阈值。它简单、可解释，但对车辆工况变化、驾驶行为变化、环境噪声和长期漂移的适应性有限。K 值过小会误报，过大会漏报，论文也承认需要权衡。

第三，多步预测能力下降明显。预测 1 到 5 个时间步时，步数越多误差越大；这会限制早期攻击预警能力，而不仅是攻击发生后的检测。

第四，masquerade 和渐进式 spoofing 仍是难点。攻击者如果控制信号变化幅度，使伪造值短时间内贴近正常轨迹，模型可能只产生较弱 anomaly score。

第五，知识蒸馏的可解释性不足。论文提出未来要研究噪声对知识融合的影响，以及用可解释分析实现更精确的知识融合。这说明当前蒸馏过程虽然有效，但还不能清楚解释哪些上下文知识被迁移、何时迁移会伤害学生模型。

第六，论文正文包未截断，本次理解覆盖所给全文；但若用于复现实验，仍需回到 PDF 核对表格中未完全转写出的数值细节和图中曲线坐标。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”高度相关，尤其适合作为车联网、工业控制网络、IoT 边缘安全中的预测式异常检测代表工作。

对本项目的直接启发包括：

- 可以把协议流量异常检测从“包级分类”转为“信号演化预测”。
- 对高维 payload 不应直接建模，应先做语义边界或稳定字段抽取。
- 边缘安全场景下，可以用大模型/重模型做教师，用轻量模型部署在线检测。
- 对复杂攻击，应同时关注数值偏差、频率变化、时序错位和上下文一致性。
- 误报率、检测延迟、参数量应与 F1-score 同等重要，尤其在实时系统中。

如果本项目研究工业互联网、车联网或 CAN/Modbus/以太网控制流量，这篇论文可以作为“多知识融合 + 轻量蒸馏 + 预测误差阈值”的方法基线。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法逐文件对应真实实现。不过根据论文方法，如果复现 MKF-ADS，代码目录大概率应拆成以下部分：

- `data_preprocess/` 或 `preprocessing.py`  
  对应 CAN 日志读取、按 CAN ID 分组、READ 信号边界抽取、bit flip rate 分析、滑动窗口生成、十进制转换、min-max normalization。

- `models/stcam.py`  
  对应 STcAM：Conv1D、BiLSTM、attention、dropout、dense prediction。在线部署时最核心的文件应是这个模块。

- `models/patchst.py`  
  对应 PatchST：channel independence、patching、embedding、position encoding、Transformer encoder、linear head。

- `models/mkf_ads.py` 或 `distillation.py`  
  对应教师 PatchST 与学生 STcAM 的联合训练，包含 `Lpred`、`LCKD` 和 `α/β` 加权目标。

- `train.py`  
  对应正常数据训练、grid search、early stopping、模型保存。

- `evaluate.py`  
  对应 MAE、RMSE、MAPE、Precision、Recall、F1、ER、FAR 计算。

- `threshold.py`  
  对应 K-sigma 阈值选择和不同攻击场景下的阈值分析。

- `attack_simulation.py` 或 `datasets/attack_generator.py`  
  对应 DoS、Fuzzy、Suspension、Replay、Spoofing、Masquerade 六类攻击序列构造。

- `deployment/jetson_eval.py`  
  对应 Jetson AGX Xavier 上的参数量、FLOPs、MACs、内存和检测时间评估。

复现时最容易出错的地方不是神经网络结构，而是 READ 信号边界抽取和攻击样本构造。若信号边界、窗口切片或阈值标定与论文不同，检测结果会明显偏移。

## 12. 本篇精华

1. MKF-ADS 的核心不是“堆模型”，而是用 Transformer 教师增强轻量 CNN-BiLSTM-attention 学生，使在线模型适合车载部署。

2. 论文把 CAN IDS 视为多变量物理信号预测问题，而不是传统二分类问题；异常来自真实值对预测轨迹的偏离。

3. READ 信号抽取是关键前置步骤，它把无语义的 64-bit payload 转成更接近车辆物理状态的有效信号。

4. STcAM 负责可部署性，PatchST 负责上下文表达力，知识蒸馏负责把二者连接起来。

5. 六类攻击中，DoS、Fuzzy、Replay、Suspension 检测较强，Spoofing 和 Masquerade 更能暴露模型对细粒度伪造的局限。

6. 论文同时评估 F1、FAR、参数量、检测时间，这比只报告分类精度更接近真实车载 IDS 要求。

7. 未来真正难点在跨 CAN ID 统一建模、非周期消息检测、多步早期预警、阈值自适应和知识融合可解释性。

## 13. 建议精读路线

1. 先读 Introduction 和 Table I，理解作者为何认为现有方法在“特征知识不足”和“模型过重”之间摇摆。

2. 再读 Section III-B 的攻击模型，把六类攻击按“消息注入”和“内容伪造”分类，这是理解后续实验的前提。

3. 重点读 Section IV-B 的数据预处理，尤其是 READ、边界划分、滑动窗口和归一化。复现成败很大程度取决于这里。

4. 精读 Section IV-C，画出 STcAM、PatchST 和 Cross Knowledge Distillation 的数据流，不要只看公式。

5. 阅读 Section V-B 时重点关注阈值选择和细粒度攻击图，那里最能体现预测式 ADS 的优势和脆弱点。

6. 最后读 Section V-D 的车辆级效率评估，判断方法是否真适合边缘部署，而不是只在服务器上表现好。