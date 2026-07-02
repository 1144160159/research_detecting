# [812] StatGraph: Effective In-Vehicle Intrusion Detection via Multi-View Statistical Graph Learning

## 1. 基本信息

- 论文：StatGraph: Effective In-Vehicle Intrusion Detection via Multi-View Statistical Graph Learning
- 作者：Kai Wang、Qiguang Jiang、Bailing Wang、Yulei Wu、Hongke Zhang
- 来源：IEEE Transactions on Mobile Computing
- DOI：10.1109/TMC.2025.3636517
- 主题：车载 CAN 总线入侵检测、伪装攻击检测、图学习、细粒度异常定位
- 正文包状态：未截断。
- 代码：`source\StatGraph`，包含 `StatGraph-CarHacking`、`StatGraph-ROAD` 和 `BaselineModels`。

## 2. 中文翻译与核心摘要

这篇论文提出 STATGRAPH：一种面向车载网络 CAN 总线的细粒度入侵检测框架。它的核心想法不是把一段 CAN 流量整体判为“正常/异常”，而是把检测窗口中的每条 CAN 消息都作为可分类对象，从而定位具体恶意报文。

方法上，作者构造两个互补视角的图：

- TCG，即 Timing Correlation Graph：以窗口内不同 CAN ID 为节点，统计 ID 转移关系，用来捕获较长时间范围内的周期性、频率和 ID 序列规律。
- CRG，即 Coupling Relationship Graph：以每条 CAN 消息为节点，把相邻消息和同 ID 消息连起来，用来保留消息级上下文、同 ID payload 一致性和短期耦合关系。

随后，STATGRAPH 把 TCG 提取的统计特征拼入每条消息节点特征，再用 CRG 生成邻接矩阵，输入轻量 GCN 做消息级多分类。论文重点强调它对 masquerade attack 的价值：伪装攻击通常保持合法 ID、发送周期和交互模式，只篡改 payload，因此只看 ID 频率或窗口统计很容易漏报。

## 3. 论文解决的具体问题

论文针对的是车载 CAN 入侵检测中的三个具体痛点。

第一，现有深度学习方法常把一个窗口内所有消息整体贴标签。只要窗口中有一条攻击消息，整个窗口就被当作攻击样本。这种方法可以做报警，但无法指出哪一条 CAN frame 异常，事后溯源、ECU 定位和安全响应都很粗糙。

第二，现有图检测方法多建模 CAN ID 的共现、频率或转移统计，对简单注入攻击有效，但对伪装攻击不够敏感。伪装攻击先让合法 ECU 静默，再由被攻陷 ECU 用相同 ID 和近似周期发送报文，只改 payload，因此“看起来像正常流量”。

第三，车载场景要求实时、低开销、可部署。论文不只追求离线检测精度，还把模型放到 Jetson Nano/Orin Nano 一类车端硬件上评估推理时间和内存，尝试说明它不是纯实验室模型。

## 4. 创新点深度提炼

1. **双图视角不是简单堆特征，而是分工明确。** TCG 负责全局统计规律，CRG 负责消息级局部耦合。前者更像“这个窗口的通信节奏是否正常”，后者更像“这条消息和前后消息、同 ID 历史消息是否协调”。

2. **把窗口级图统计下沉到消息级特征。** 每条 CAN 消息的特征不只是 `ID + 8 bytes payload`，还拼入 TCG 的统计属性，使单条消息携带其所在窗口的结构背景。

3. **CRG 保留了消息级粒度。** 每条消息都是一个节点，边来自相邻关系和同 ID 相似关系。这比“一个 ID 一个节点”的图更适合定位具体恶意帧。

4. **提出 Identification Granularity, IG。** 传统 Accuracy/F1 不能区分“窗口判对但消息定位错”的情况，IG 用来衡量模型在窗口内识别具体消息状态的能力。

5. **系统性评估 ROAD 的五类伪装攻击。** 论文把 correlated signal、max speedometer、reverse light off/on、max engine coolant temp 等真实车辆攻击纳入实验，强化了对复杂 payload 篡改攻击的覆盖。

6. **给出车云协同部署框架。** 云侧训练和调参，车端只做实时推理；这符合车载 IDS 的资源约束。

## 5. 科学问题与研究假设

论文背后的科学问题可以概括为：在攻击者尽量保持 CAN ID、发送周期和交互外观不变的情况下，能否通过多视角图结构学习捕获 payload 和局部耦合关系中的异常？

它的研究假设有三条：

- 正常 CAN 流量存在稳定的 ID 转移、周期和窗口内结构统计，攻击会扰动这些统计规律。
- 同一 CAN ID 的 payload 变化不是随机的，而是受物理信号和 ECU 状态约束；伪装攻击即便模拟时序，也会破坏这种局部一致性。
- 将全局统计上下文和局部消息耦合同时输入 GCN，可以让浅层模型学到足够强的判别表示，并保持边缘设备可部署性。

## 6. 科学方法与技术路线

技术路线是“窗口切分 -> 双图构造 -> 特征融合 -> GCN 消息分类”。

1. CAN 流按固定窗口切分。Car Hacking 最优窗口为 `N=50`，ROAD 最优窗口为 `N=400`。
2. 构造 TCG。窗口内唯一 CAN ID 是节点；若当前 ID 跟随前一个 ID 出现，则建立反向统计边，并累加权重。论文解释为让后出现的 ID 在 GCN 聚合中吸收历史上下文。
3. 从 TCG 提取统计特征。正文写的是节点数、边数、最大度等；代码实现中实际写入的是边数、最大边权、节点数。
4. 构造 CRG。窗口中每条 CAN 消息是节点；相邻消息连边，同 ID 消息连边。代码为控制复杂度，同 ID 历史连接只取最近若干个。
5. 输入 GCN。节点特征维度为 12：`CAN ID + 8 payload bytes + 3 个 TCG 统计特征`；邻接矩阵来自 CRG；输出为每条消息的类别。
6. 用交叉熵训练，用 Accuracy、Precision、Recall、F1 和 IG 评估。

## 7. 实验设计与实验步骤

**数据。** 使用 Car Hacking 和 ROAD 两个真实 CAN 数据集。Car Hacking 包含 normal、DoS、Fuzzy、Gear spoofing、RPM spoofing；ROAD 包含五类伪装攻击，且更接近本文关注的 stealthy payload manipulation。

**预处理。** Car Hacking 将十六进制 ID/payload 转为整数，按窗口切分。ROAD 先把 raw log 和带标签 CSV 通过 timestamp 与 ID 对齐，再转成与 Car Hacking 相似的 `ID, Data[0..7], Label` 格式。

**模型与基线。** STATGRAPH 对比 Graph-based IDS、G-IDCS threshold/RF、EfficientNet、MobileNetV3、CANet、CAN-RF、CAN-MLP、CAN-LSTM。图统计类基线偏窗口级，CNN 类基线把连续消息转成图像，传统 ML/RNN 类基线用于消息级或序列级对照。

**训练。** 论文设置隐藏维度 `h=32`、Adam、学习率 `1e-3`、L2 正则。代码中 Car Hacking 使用 `N=50, batch_size=40, nclass=5`，ROAD 使用 `N=400, batch_size=5, nclass=6`。两者每个 mini-batch 实际都形成约 2000 个消息节点的稀疏图。

**指标。** 常规指标是 Accuracy、Precision、Recall、F1；新增 IG 评估消息级定位能力。运行效率用推理时间和内存占用评估，设备包括云端 PC 和车端 Jetson 平台。

**消融/敏感性。** 论文测试窗口大小、隐藏维度、batch size；并做 Node ablation 和 Edge ablation，分别去掉 TCG 全局特征或 CRG 关联结构。

**结果核查。** 表 VI/VII 给出两数据集性能；表 VIII 检查不同实时粒度下 F1 和 IG；图 10 验证 TCG/CRG 两部分贡献。代码 `predict32.py` 中也保留了 Car Hacking 的一次测试输出注释，F1 为 0.9403。

## 8. 关键结果、结论与证据

论文报告 STATGRAPH 在两个数据集上都取得最稳健的结果：Car Hacking 上约 99% 以上准确率、F1 约 94%；ROAD 上 Accuracy 为 97.91%、F1 为 97.46%。摘要中声称相对 SOTA 的 F1 提升分别达到 7% 和 22%。

更重要的结论不是“分数最高”，而是它在 ROAD 伪装攻击上仍能保持高 F1。ROAD 攻击保持正常 ID 和频率，只改变物理信号对应的 payload；这说明 CRG 中同 ID 消息耦合、相邻消息上下文和 payload 字节共同起了作用。

消融实验也支持论文主张：去掉 TCG 后节点表示退化，整体指标下降；去掉 CRG 后对低频或隐蔽攻击的召回下降，说明局部关联结构对 stealthy attack 很关键。

## 9. 局限性与待解决问题

第一，固定窗口 `N` 是现实部署中的弱点。真实 CAN 负载会随车况变化，固定窗口可能在不同工况下覆盖不同物理时间长度。论文也承认需要自适应窗口或多尺度窗口。

第二，仍是监督学习框架，依赖带标签攻击数据。对未知 ECU、未知车型、零日攻击的泛化能力没有被充分证明。

第三，类别不平衡问题明显，尤其 ROAD 中正常样本占比高。高 Accuracy 可能掩盖少数攻击类别的召回风险，因此 F1、IG 和混淆矩阵必须一起看。

第四，解释性还不够。论文提到未来可用 GNNExplainer、Integrated Gradients，但当前实验没有系统展示“哪条边/哪个 payload 字节导致判定”。

第五，代码和论文存在少量实现差异：正文称 dropout 很小，但主训练脚本使用 `dropout=0.5`；正文说 TCG 特征含最大度，代码更像是最大边权；ROAD 与 Car Hacking 的 GCN 层数也不同。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”强相关，尤其适合作为车联网、工业互联网、IoT 边缘安全方向的图学习方法样例。

对本项目可借鉴的点有三类：

- **方法层面：** 将全局统计图和局部关系图分开建模，再融合到 GCN，比单一时序模型或单一图统计更适合复杂协议流量。
- **评估层面：** IG 可以迁移到工业协议、CAN、Modbus、TSN 等场景，用于衡量异常定位粒度，而不是只看窗口报警。
- **工程层面：** 云端训练、边缘端推理的部署思路适合资源受限安全网关；代码中稀疏邻接矩阵和小型 GCN 也符合轻量化方向。

## 11. 代码对照分析

代码主目录为 `source\StatGraph`。核心对应关系如下：

| 论文模块 | 代码位置 | 作用 |
|---|---|---|
| 数据集说明 | `Dataset/Car Hacking Dataset/Readme.txt`、`Dataset/ROAD/Readme.txt` | 说明 Car Hacking 与 ROAD 来源、攻击类型 |
| ROAD 原始对齐 | `BaselineModels/ROAD/Origin_preprocess_ROAD.py` | 用 timestamp 和 ID 匹配 raw log 与 CSV 标签 |
| TCG 节点特征 | `StatGraph-CarHacking/dataprocess50_40/nodes/*.py`、`StatGraph-ROAD/dataprocess400_5/nodes/*.py` | 生成 `ID + payload + TCG统计 + label` |
| CRG 邻接边 | `StatGraph-CarHacking/dataprocess50_40/edges/*.py`、`StatGraph-ROAD/dataprocess400_5/edges/*.py` | 生成相邻消息边和同 ID 消息边 |
| 节点合并 | `merge node vectors 50_40.py`、`merge node vectors 400_5.py` | 合并为 `train_nodes.csv / val_nodes.csv / test_nodes.csv` |
| 训练入口 | `StatGraph-CarHacking/ModelAdapting/run50_40/train32.py`、`StatGraph-ROAD/ModelAdapting/run400_5/train32.py` | 加载节点/边，训练 GCN，保存 `gcn32.pkl` |
| 推理入口 | `predict32.py` | 加载 `gcn32.pkl` 做测试并输出混淆矩阵 |
| 工具函数 | `utils.py` | one-hot、邻接矩阵归一化、scipy sparse 转 torch sparse |
| 基线模型 | `BaselineModels/*/CANet`、`EfficientNet`、`MobileNet`、`Chi-test` | 对应论文比较方法 |

代码中 TCG 的 `Graph.record()` 负责提取图统计；CRG 边生成脚本中 `(j, j-1, 1)` 对应相邻消息连边，同 ID 历史索引对应相似关系连边。训练脚本中 `GraphConvolution` 实现 `A X W` 的稀疏图卷积，随后接 ReLU、dropout 和线性分类层。

运行线索是：先进入对应 `dataprocess*` 目录生成节点和边，再运行 `ModelAdapting/run*/train32.py`，最后运行 `predict32.py`。当前包中 ROAD 处理后 CSV 已存在；Car Hacking 目录只看到 `normal_16_id.zip`，攻击 CSV 可能需要按 README 补齐。

## 12. 本篇精华

1. STATGRAPH 的核心贡献是把车载 IDS 从窗口级报警推进到消息级定位。
2. TCG 捕获 CAN ID 的全局周期和统计结构，CRG 捕获相邻消息与同 ID payload 的局部耦合。
3. 伪装攻击难点在于时序和 ID 像正常流量，真正异常藏在 payload 与信号协同变化中。
4. IG 是本文很有复用价值的评价指标，可用于衡量异常检测的定位粒度。
5. ROAD 五类 masquerade attack 比 Car Hacking 更能检验复杂攻击检测能力。
6. 代码实现证明方法并不复杂：核心是预处理构图加浅层 GCN，而非大型深度模型。
7. 真正的工程挑战在数据标注、窗口自适应、跨车型泛化和解释性，而不是单纯提高 F1。

## 13. 建议精读路线

建议先读 Introduction 和 Threat Model，明确为什么 fabrication attack 已不够代表真实威胁，masquerade attack 才是论文重点。

第二步精读 Methodology，尤其对照 TCG 和 CRG：一个是“ID 统计图”，一个是“消息耦合图”。读的时候要注意 TCG 的节点是 CAN ID，而 CRG 的节点是单条消息。

第三步看 Experiment 的 Dataset Details 和 Fine-Grained Potential Exploration。这里能理解为什么作者要提出 IG，以及为什么窗口级检测在车载实时场景中不够。

最后回到代码目录读 `dataprocess50_40`、`dataprocess400_5` 和 `train32.py`。重点确认三件事：节点特征如何写入、边三元组如何生成、GCN 如何加载稀疏邻接矩阵。