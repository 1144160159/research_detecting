# [788] Revisiting the Intrusion Detection in In-Vehicle Networks

## 1. 基本信息

- 编号：788
- 题名：Revisiting the Intrusion Detection in In-Vehicle Networks
- 作者：Muhammad Asif Khan, Hamid Menouar, Mohamed Abdallah
- 期刊：IEEE Transactions on Intelligent Transportation Systems
- DOI：10.1109/TITS.2025.3628885
- 元数据年份：2025；正文显示发表时间为 2025-12-12，期刊卷期为 2026 年 1 月
- 主题：车载网络 CAN 总线入侵检测、动态窗口、多标签攻击检测、自动驾驶车内网络安全
- 本地代码状态：未发现该论文对应代码包

## 2. 中文翻译与核心摘要

这篇论文讨论的是自动驾驶车辆内部网络，也就是 IVN/In-Vehicle Network 中的入侵检测问题。车辆内部的 ECU、传感器和执行器通常通过 CAN 总线通信，而传统 CAN 协议缺少身份认证、加密和访问控制，因此攻击者一旦接入总线，就可能伪造、注入、重放或泛洪 CAN 帧。

论文提出的核心方法是 DWIDS，即 Dynamic Windowing Intrusion Detection System。它不是固定使用一个窗口长度去切分 CAN 流量，而是根据检测到的异常、误报、漏报和检测时延动态调整窗口大小。直觉是：有攻击迹象时缩短窗口以提高响应速度和定位精度；正常流量下扩大窗口以提升上下文和效率。

论文同时重新审视了两个常见范式：

- 单帧检测：每条 CAN 帧作为一个样本，适合识别单个恶意帧即可造成影响的攻击，如 Gear spoofing、RPM spoofing。
- 多帧/窗口检测：多个连续 CAN 帧组成一个样本，适合识别 DoS、Fuzzy、Replay 等需要从时序或统计模式中判断的攻击。

核心结论是：IVN 入侵检测中很多公开数据集上的高准确率并不一定说明问题已经被解决，因为数据集、攻击形式和评价方式都可能偏理想化；但如果合理使用 CAN ID、Data 字段、类别权重、多标签窗口标注和动态窗口策略，轻量模型也可以在 CHD 和 IVN-IDS Challenge 两个数据集上取得较高检测效果。

## 3. 论文解决的具体问题

论文针对的具体问题不是“能不能训练一个分类器识别 CAN 攻击”这么简单，而是重新追问 IVN IDS 的几个基础设定是否合理：

1. 现有方法过度依赖固定窗口  
   很多 LSTM、CNN 或统计窗口方法用固定窗口长度切分 CAN 流量，但不同攻击的时间尺度不同。DoS 需要看高频泛洪模式，Spoofing 可能单帧就危险，Replay 又需要捕捉重复片段。固定窗口很难同时兼顾低时延和低误报。

2. 现有高分结果可能掩盖真实难度  
   许多论文报告 99% 以上准确率，但车载攻击数据集通常类别极不平衡。正常帧数量远多于攻击帧，单看 accuracy 容易高估模型能力。

3. 单攻击、单标签假设不符合现实  
   真实车内网络中，一个短时间窗口可能同时包含正常帧和多类攻击帧。传统单标签窗口分类会把混合窗口压成一个标签，丢失攻击共现信息。

4. 复杂深度模型难以部署  
   Per-CAN-ID LSTM、大型 CNN、GAN、LLM 类方法虽然指标高，但计算负担、训练稳定性、解释性和 ECU 部署可行性都存在问题。

5. 特征选择缺乏反思  
   一些研究只用 CAN ID，一些研究不用 payload。论文认为 payload/Data 字段虽然和厂商相关，但它包含最直接的语义信息；完全舍弃 payload 会限制检测能力。

## 4. 创新点深度提炼

1. 从“重新审视问题设定”切入  
   论文的价值不只在提出 DWIDS，还在系统质疑 IVN IDS 领域常见实验范式：固定窗口、单数据集、单攻击、单标签、过度强调 accuracy、忽略部署时延。

2. 动态窗口机制  
   DWIDS 的核心是把窗口大小视为运行时可调参数，而不是训练前固定超参数。窗口根据异常状态和性能指标反馈调整：异常时缩短窗口，正常时扩大窗口，若 FP/FN/Latency 超阈值则继续微调。

3. 单帧与多帧检测并行讨论  
   论文没有把所有攻击都强行塞入同一种建模方式，而是指出不同攻击适合不同粒度：Spoofing 更适合单帧敏感检测，DoS/Fuzzy/Replay 更适合序列或窗口统计检测。

4. 多标签窗口建模  
   多帧窗口中可能同时存在多类攻击。论文用 multi-label 表示窗口内出现过的所有类别，而不是给窗口强行指定唯一攻击标签。这一点比传统 chunk-level single-label 更接近实际流量。

5. 对 CAN ID 依赖性的实验反查  
   论文分别做了包含 CAN ID 和不包含 CAN ID 的单帧实验，用来判断模型是否只是记住某些 ID。结果显示不含 CAN ID 仍能取得较高性能，但 Fuzzy 攻击误分类增加，说明 CAN ID 有帮助但不是唯一信息源。

6. 强调轻量模型可部署性  
   DWIDS 是 model-agnostic，可以搭配 DT、RF、XGBoost、MLP、1D-CNN、LSTM 等模型。论文倾向于使用 MLP、1D-CNN 这类更适合 ECU 或边缘设备部署的模型，而不是大型深度架构。

## 5. 科学问题与研究假设

论文背后的科学问题可以概括为：

- IVN 入侵检测的高指标到底来自模型能力，还是来自数据集简单、标签模式明显、攻击注入方式固定？
- 固定窗口是否适合同时检测 DoS、Fuzzy、Spoofing、Replay 等不同时间尺度的攻击？
- 一个窗口内如果出现多种攻击，单标签分类是否会损失关键信息？
- CAN ID、payload/Data 字段在泛化和攻击识别中分别贡献了什么？
- 在资源受限车载环境中，能否用轻量模型和自适应窗口实现足够高的检测性能？

论文隐含的主要假设包括：

- 攻击会改变 CAN 帧的 ID 分布、Data 字段模式或短时间序列结构。
- 动态调整窗口可以在检测速度和检测准确性之间取得更好平衡。
- 多标签窗口比单标签窗口更适合真实混合攻击场景。
- 使用类别权重可以缓解 CHD 和 IVN-IDS Challenge 中攻击类别不平衡带来的偏置。
- 轻量模型配合合理预处理和窗口策略，足以完成多数公开数据集上的 IVN IDS 任务。

## 6. 科学方法与技术路线

论文技术路线可以分成三层。

第一层是数据预处理。原始 CAN 帧经过字段转换：去掉 timestamp，将 CAN ID 和 Data 字段从十六进制或字符串转换为十进制数值，再映射成张量。标签从原始标记转换为 Normal、DoS、Fuzzy、Gear、RPM 等类别编号。

第二层是单帧检测。每条 CAN 帧作为一个样本，分别测试“CAN ID + Data”和“仅 Data”两种特征组合。模型包括 DT、RF、XGBoost、MLP、CNN、LSTM。这个部分主要用于回答：单帧粒度是否已经能识别多数攻击，以及 CAN ID 是否导致过拟合。

第三层是多帧/窗口检测。连续 CAN 帧按时间窗口或固定帧数堆叠为 chunk，再转成 2D heatmap 或 3D RGB image。每个 chunk 的标签不是单一类别，而是一个长度为类别数的 multi-hot 向量，表示该窗口内出现过哪些攻击类型。DWIDS 在这一层引入动态窗口：根据异常、FP、FN、Latency 调整窗口大小。

整体思想是：用单帧模型处理瞬时危险攻击，用窗口模型处理模式型攻击，再用动态窗口机制平衡检测响应和上下文充分性。

## 7. 实验设计与实验步骤

数据：

- CHD/HCRL Car-Hacking Dataset：来自真实车辆 OBD-II 端口 CAN 流量，包含 DoS、Fuzzy、Gear spoofing、RPM spoofing。
- IVN-IDS Challenge Dataset：来自 HYUNDAI Sonata、KIA Soul、CHEVROLET Spark，包含 Fuzzy、Malfunction、Replay 等攻击。
- 两个数据集都存在类别不平衡，正常流量占比高，少数攻击类别样本更少。

预处理：

1. 合并不同攻击类型的数据文件。
2. 移除 timestamp，避免模型过度依赖采集时间。
3. 将 CAN ID 和 Data 字段转换为十进制数值。
4. 将标签映射为整数类别，例如 Normal、DoS、Fuzzy、Gear、RPM。
5. 对类别不平衡问题使用 class weights。
6. 单帧实验中，每一帧是一个样本。
7. 多帧实验中，按时间窗口或固定帧数组成 chunk，并进行 padding，使其可转为方形 2D heatmap 或 3D image。
8. 对 chunk 使用 multi-label 标注：窗口中出现过的类别对应位置置 1。

模型/基线：

- 单帧基线：Decision Tree、Random Forest、XGBoost、MLP、CNN、LSTM。
- 多帧/DWIDS：窗口化输入，支持 2D heatmap、RGB image 和多标签分类。
- 论文强调 DWIDS 与具体分类器解耦，可搭配轻量模型部署。

训练：

- 训练集/测试集划分为 70%/30%。
- Scikit-learn 实现 DT、RF。
- xgboost 库实现 XGBoost。
- PyTorch 实现 MLP、CNN、LSTM。
- 深度模型训练最多 10 个 epoch。
- 使用较朴素或默认参数，目标不是极致调参，而是判断 IDS 任务本身难度和方法合理性。

指标：

- Accuracy
- Precision
- Recall/TPR
- F1-score
- FPR
- TNR

论文明确指出，IVN IDS 中 Recall 和 FPR 比 Accuracy 更关键：漏报攻击可能直接影响车辆安全；误报过多会损害系统可信度。

消融/敏感性：

- 是否使用 CAN ID：比较“CAN ID + Data”和“仅 Data”。
- 单帧 vs 多帧：比较每帧分类与窗口分类。
- 固定窗口 vs 动态窗口：DWIDS 的主张是根据异常和性能反馈调整窗口。
- 类别不平衡影响：通过 confusion matrix 和 weighted/macro 指标观察少数类表现。
- 攻击类型差异：DoS、Gear、RPM 较容易，Fuzzy 更难。

结果核查：

- 不能只看 accuracy，应检查每类 precision、recall、F1。
- 需要看 confusion matrix，确认模型是否真的识别攻击类，而不是只识别正常类。
- 特别关注 Fuzzy、Replay 等更接近开放变化的攻击。
- 对多标签窗口，应确认窗口内多攻击共存时是否被正确标注和识别。

## 8. 关键结果、结论与证据

1. 单帧检测已经能取得很高性能  
   在 CHD 上，六类基线模型多数指标都很高。即使去掉 CAN ID，仅使用 Data 字段，模型仍然表现较好。这说明公开数据集中攻击帧的 payload 或数据模式本身已经很容易被模型捕捉。

2. CAN ID 有帮助，但不是全部原因  
   加入 CAN ID 后，多数模型对 DoS、Gear、RPM spoofing 几乎接近完美识别；去掉 CAN ID 后，Fuzzy 攻击误分类增加。这说明 CAN ID 对检测有贡献，尤其对随机 ID 分布或特定 ECU ID 注入的攻击有帮助。

3. Fuzzy 是更有挑战性的攻击  
   Fuzzy 攻击使用大量随机 CAN ID，且这些 ID 可能和正常帧 ID 重叠，Data 字段也变化较大。因此模型更容易混淆 Fuzzy 与正常或其他类别。

4. 多标签 DWIDS 在两个数据集上保持较高表现  
   论文报告 DWIDS 在 CHD 和 IVN-IDS Challenge 上的平均 precision、recall、F1 大致处于 0.96-0.98 区间，并且对少数类攻击仍有较好结果。

5. 动态窗口的主要价值是响应性  
   DWIDS 不只是为了提高离线指标，而是为了让 IDS 在运行时根据风险状态调整检测粒度。异常出现时缩短窗口，减少检测延迟；正常时扩大窗口，提高效率并降低误报。

6. 论文结论偏实践导向  
   作者认为 IVN IDS 不应盲目追求复杂模型，而应关注真实部署中的延迟、窗口粒度、类别不平衡、多攻击共存和跨车辆泛化。

## 9. 局限性与待解决问题

1. 动态窗口机制仍偏概念化  
   Algorithm 2 给出了 FP、FN、Latency 驱动的窗口调整逻辑，但在线环境中 FP/FN 的实时获得并不容易，因为真实部署时没有即时真值标签。实际系统需要代理指标、延迟标签或人工反馈机制。

2. 缺少更细的延迟与资源评估  
   论文提到 Jetson Nano 和 10-50 ms 推理时间，但正文包中没有看到完整硬件测试表、内存占用、吞吐率、窗口调整开销等细节。

3. 数据集仍然偏公开基准  
   CHD 和 IVN-IDS Challenge 被广泛使用，但攻击多为注入、重放或合成形式，未必覆盖真实攻击者的低速、隐蔽、渐进式攻击。

4. 跨车辆泛化仍需更强验证  
   论文强调跨车辆数据集，但不同厂商 CAN payload 语义差异很大。若使用 Data 字段，泛化能力会受到车辆型号和厂商私有编码影响。

5. 多标签窗口可能带来定位问题  
   窗口级 multi-label 能识别窗口中有哪些攻击，但不能自然指出是哪几帧恶意、攻击起止位置在哪里。实际防御需要更细粒度告警。

6. 与认证/加密机制的协同尚未实现  
   论文结尾建议结合车内认证和加密，但 DWIDS 本身仍是检测系统，不能阻止恶意帧上总线。

7. 本次正文包未截断  
   提供信息显示“是否截断：False”，因此本次理解基于完整正文包；但如需复现实验，仍需回到 PDF 核对表 IV、表 V 的具体数值和图中细节。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”高度相关，尤其适合作为车联网、IoT、工业互联网边缘安全方向的代表文献。

对本项目的启发主要有三点：

1. 异常检测不能只追求高 accuracy  
   在工业控制、车联网和 IoT 场景中，攻击稀有且代价高，Recall、FPR、检测延迟比 accuracy 更能反映工程价值。

2. 窗口长度应成为研究对象  
   很多异常检测任务都涉及滑动窗口，但窗口通常被当作固定超参数。DWIDS 提醒我们：窗口可以根据风险状态自适应变化。

3. 多标签异常更接近真实系统  
   网络攻击往往不是单一标签事件。一个时间段内可能同时出现扫描、注入、重放、泛洪等行为。多标签建模比单标签分类更符合安全语义。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此不能把论文方法直接映射到真实源码文件。若后续发现代码，建议重点寻找以下模块：

- 数据预处理：可能包含 CSV 读取、CAN ID/Data 十六进制转十进制、标签映射、timestamp 删除、class weight 计算。
- 单帧模型：可能包含 DT、RF、XGBoost、MLP、CNN、LSTM 的训练脚本。
- 窗口构造：应实现按时间或帧数切 chunk、padding、heatmap/RGB image 生成。
- 多标签生成：应实现窗口内 `multi_label[l] = 1` 的 multi-hot 标签逻辑。
- DWIDS 控制逻辑：应包含 `W0`、`Wmin`、`Wmax`、`delta_W`、`FPmax`、`FNmax`、`Lmax` 等参数。
- 评估脚本：应输出 accuracy、precision、recall、F1、FPR、confusion matrix，以及按类别指标。

从论文描述看，复现项目可组织为：

- `preprocess.py`：处理 CHD 和 IVN-IDS 原始 CSV。
- `build_windows.py`：生成单帧样本和窗口样本。
- `models.py`：定义 MLP、1D-CNN、LSTM 或 2D-CNN。
- `train_single_frame.py`：训练单帧基线。
- `train_multilabel.py`：训练窗口多标签模型。
- `dwids.py`：实现动态窗口控制策略。
- `evaluate.py`：计算指标并生成混淆矩阵。

## 12. 本篇精华

1. IVN IDS 的高准确率需要被重新审视，尤其要警惕类别不平衡和公开数据集攻击模式过于固定带来的虚高结果。

2. CAN 总线攻击并非都适合同一种检测粒度：Spoofing 可能单帧致命，DoS/Fuzzy/Replay 更需要窗口上下文。

3. DWIDS 的关键思想是让窗口大小随异常态势变化，而不是把窗口长度固定为离线调参结果。

4. 多标签窗口比单标签窗口更合理，因为一个时间窗口内可能同时包含正常帧和多种攻击帧。

5. CAN ID 是有效特征，但不能只依赖 CAN ID；payload/Data 字段虽然影响跨车泛化，却提供了重要检测信息。

6. Fuzzy 攻击比 DoS、Gear、RPM spoofing 更难，因为它的 ID 和数据模式更分散、更接近开放变化。

7. 车载 IDS 的评价必须重视 Recall、FPR 和检测延迟，单看 Accuracy 不足以支撑安全结论。

8. 论文真正有价值的地方在于把“模型精度问题”提升为“实时部署、窗口粒度、多标签、安全代价”的系统问题。

## 13. 建议精读路线

1. 先读 Introduction 和 Related Work  
   重点看作者如何批评已有 IVN IDS：固定窗口、单数据集、复杂模型、指标选择不当。

2. 再读 Section II-B Analysis  
   这是论文最值得精读的部分，尤其是特征选择、样本窗口大小、评价指标三段。

3. 接着读 Section III  
   把 Method 1、Method 2 和 DWIDS 区分清楚：单帧检测是基线分析，多帧检测是窗口建模，DWIDS 是动态窗口策略。

4. 精读 Algorithm 1 和 Algorithm 2  
   Algorithm 1 对应多标签窗口样本构造；Algorithm 2 对应在线窗口调节逻辑。复现时这两处最关键。

5. 最后读 Results and Discussion  
   重点看包含/不包含 CAN ID 的对比、confusion matrix 中 Fuzzy 攻击的误分类，以及表 IV、表 V 的多标签结果。

6. 如果用于综述写作  
   建议把这篇归为“自适应窗口与多标签 IVN IDS”，同时在局限中指出其动态反馈机制在线真值来源不足、真实部署评估仍不充分。