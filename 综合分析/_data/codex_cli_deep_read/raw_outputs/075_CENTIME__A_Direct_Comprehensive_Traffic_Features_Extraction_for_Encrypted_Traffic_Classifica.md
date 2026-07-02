# [075] CENTIME: A Direct Comprehensive Traffic Features Extraction for Encrypted Traffic Classification

## 1. 基本信息
- 论文：CENTIME: A Direct Comprehensive Traffic Features Extraction for Encrypted Traffic Classification
- 中文题意：CENTIME：面向加密流量分类的直接综合流量特征提取框架
- 年份/会议：2021，IEEE ICCCS
- DOI：10.1109/icccs52626.2021.9449280
- 作者：Maonan Wang, Kangfeng Zheng, Xinyi Ning, Yanqing Yang, Xiujuan Wang
- 任务类型：加密流量分类、应用类型识别、VPN/non-VPN 流量识别
- 数据集：ISCX VPN-nonVPN，论文最终使用 12 类流量
- 代码：`source\Traffic-Classification`

## 2. 中文翻译与核心摘要
这篇论文的核心意思是：只看人工统计特征，模型效果依赖专家设计；只看原始流量字节，深度模型必须把 session 截断或补零到固定长度，会丢掉包数、持续时间、包间隔等全局结构信息。CENTIME 试图把两类信息合并：一支 ResNet 从统一长度的原始字节序列中学习局部模式，另一支 AutoEncoder 把 26 个统计特征压缩成低维表示，再与 ResNet 特征拼接分类。

它不是单纯提出一个更深的分类器，而是围绕“统一长度造成的信息损失”来补偿：原始字节负责捕捉协议/负载形态的局部序列模式，统计特征负责保留 session 级时间、包长、包数、标志位等结构信息。最终在 ISCX VPN-nonVPN 上取得约 0.998 的 F1，优于论文比较的 CNN、Deep Packet、SPCaps 等方法。

## 3. 论文解决的具体问题
论文针对的是加密环境下无法依赖端口、明文载荷和 DPI 的流量分类问题。更具体地说，它处理的是 12 类应用/业务类型识别：Email、Chat、File Transfer、P2P、Streaming、VoIP 及其 VPN 版本。

它指出两个主流路线的缺陷：统计特征方法需要人工针对任务调特征，迁移成本高；原始字节深度学习方法虽然端到端，但 CNN/ResNet 输入固定，必须截断或补零，导致 session 总包数、首末包时间跨度、最小/最大包间隔等全局信息被抹掉。

## 4. 创新点深度提炼
第一，论文把“原始流量字节特征”和“session 统计结构特征”显式融合，目标不是简单堆特征，而是用统计特征补偿原始流量统一长度后的结构损失。

第二，使用 1D ResNet 处理字节序列。作者认为流量本质是序列，不应强行把 784 bytes 看成 28×28 图像后用 2D 卷积学习人工空间邻接关系。

第三，去掉中间 pooling 层，避免池化过早丢弃字节级细节。代码中仍使用 `AdaptiveAvgPool1d(1)` 做最终全局压缩，但没有使用 CNN 基线中的 MaxPool 级联。

第四，AutoEncoder 将 26 维统计特征压缩到 9 维，既降低维度，也通过重构约束保留统计信息。代码中对应 `26 -> 18 -> 9 -> 18 -> 26`。

第五，论文不只报告最终精度，还围绕统一长度、1D/2D 卷积、是否 pooling 做了 21 组实验，结论更像一次结构性验证。

## 5. 科学问题与研究假设
核心科学问题是：加密流量分类中，固定长度原始字节表示是否足够？如果不够，session 级统计信息能否补回被截断/补零破坏的全局结构？

主要假设包括：
- 不同应用流量即使加密，仍在包序列字节形态和统计行为上有可分模式。
- session 的前 784/1024/4096 字节包含足够强的局部判别信号。
- 包数、持续时间、包间隔、包长分布等统计特征与原始字节特征互补。
- 1D 卷积比 2D 卷积更符合流量序列结构。
- 移除中间 pooling 能减少细粒度字节信息损失。

## 6. 科学方法与技术路线
技术路线可以概括为三段。

数据预处理：原始 pcap 按 session 切分，删除或屏蔽容易导致过拟合的地址字段，去除空文件和重复文件，再把 session 统一成 784、1024、4096 bytes。

流量信息提取：一方面，把统一长度字节输入 1D ResNet，得到 256 维原始流量表示；另一方面，从原始 session 提取 26 个统计特征，包括 TCP flags、DNS/TCP/UDP/ICMP 比例、duration、delta time、packet length、payload length、packet number 等，再由 AutoEncoder 压缩成 9 维。

分类：将 256 维 ResNet 表示与 9 维统计表示拼接为 265 维综合特征，经全连接层输出 12 类预测。

## 7. 实验设计与实验步骤
可复核流程如下：

1. 数据：使用 ISCX VPN-nonVPN，删除类别描述含糊的文件，保留 12 类；训练/测试按 90%/10% 随机划分。
2. 预处理：pcapng 转 pcap；按文件名映射到 12 类；用 SplitCap 按 session 切分；计算 26 个统计特征；匿名化 IP/MAC，代码中还清零端口；session 截断/补零到 784、1024、4096 bytes；保存为 `train-pcap.npy`、`train-statistic.npy`、`train-labels.npy` 等。
3. 模型/基线：CENTIME 对比 CNN1D、CNN2D、CNN1D-noPooling、CNN2D-noPooling、ResNet1D、ResNet2D，并与 FlowPic、Deep Packet、CNN+LSTM、SPCaps 等公开方法比较。
4. 训练：PyTorch，Adam，初始学习率 0.001，150 epochs；论文写 batch size 256。代码中 CENTIME 默认 dataloader 是 256，普通 `train_pipeline` 配置里是 128。
5. 指标：Accuracy、Precision、Recall、F1，代码使用 sklearn 计算 weighted precision/recall/F1。
6. 消融/敏感性：比较三种统一长度；比较有无 pooling；比较 1D 与 2D 卷积；比较 ResNet1D 与加入统计特征后的 CENTIME。
7. 结果核查：看 Table III 的 21 组结果、Table IV 的 SOTA 对比，以及 t-SNE 可视化中同类聚集、VPN/non-VPN 大致分离的现象。

## 8. 关键结果、结论与证据
最强结果来自 CENTIME。784 bytes 时 Accuracy 0.9979、F1 0.9980；1024 bytes 时 Accuracy 0.9972、F1 0.9973；4096 bytes 时 Accuracy 0.9977、F1 0.9979。

关键对比很清楚：784 bytes 下，ResNet1D 的 F1 为 0.9913，CENTIME 提升到 0.9980，说明统计特征确实带来增益；CNN1D-noPooling 明显优于 CNN1D-Pooling，支持“中间池化会丢失有效字节信息”的判断；ResNet1D 明显优于 ResNet2D，支持“流量按序列处理更合理”的判断。

统一长度不是越长越好。论文解释是，大多数 session 小于 1000 bytes，拉到 4096 bytes 会引入大量 0x00 padding，无效信息增加，普通 CNN 尤其受影响。

t-SNE 可视化显示综合特征在二维空间中同类聚集，不同类分离，VPN 流量与 non-VPN 流量也呈现明显区域差异。这是论文用来支撑“综合特征具有类别表征能力”的主要可解释证据。

## 9. 局限性与待解决问题
正文包标记为未截断，本次理解不受正文截断影响；但若要正式引用图表数值，仍建议回 PDF 复核 Table IV 的排版对齐。

主要局限有四点。第一，ISCX VPN-nonVPN 严重不均衡，代码随包 784 测试集中 VoIP 有 3720 条，而 VPN_Email 只有 15 条、VPN_P2P 只有 26 条，Accuracy 和 weighted F1 容易被大类主导。第二，实验集中在单一公开数据集，且数据集较旧，跨数据集、跨采集环境、跨新型加密协议的泛化没有充分验证。第三，统计特征提取需要解析 session，代码用 scapy 逐文件计算，实时部署成本比纯端到端字节模型高。第四，随机 session 划分可能让同一原始采集文件中的相似 session 同时进入训练和测试，泛化难度可能低于按应用/采集文件隔离的设置。

代码与论文还有复现差异：论文写统计特征用 min-max，代码 CENTIME 使用固定 mean/std 标准化；论文写学习率每 25 epoch 衰减 0.9，代码 `helper.py` 是每 30 epoch 乘 0.1；当前本地随包数据有 784/1024 目录，checkpoint 主要是 784，配置却默认指向 4096，需要改配置或补齐数据。

## 10. 与本项目的关系
这篇与“加密流量分类与应用识别”强相关，也可服务“跨域异常检测”。它的启发在于：异常检测不应只依赖原始 payload-like 字节，也不应只依赖统计特征；更稳妥的是把局部序列模式与全局行为统计融合。

对本项目可借鉴三点：用 1D 时序卷积处理流量字节；用统计特征保留 session 结构；把 AutoEncoder 的 latent 表示和重构误差扩展为异常检测信号。若项目目标是未知应用、未知攻击或跨域部署，则需要进一步做跨数据集验证、时间切分验证和开放集检测，而不能只追求封闭集 12 类高精度。

## 11. 代码对照分析
代码入口与论文三阶段基本对应。

- 运行入口：`TrafficFlowClassification/__main__.py` 暴露 `preprocess_pipeline`、`train_pipeline`、`CENTIME_train_pipeline`。
- 配置：`TrafficFlowClassification/entry/traffic_classification.yaml` 控制数据路径、统一长度、batch、epoch、模型名、label2index。
- 数据预处理：`entry/preprocess.py` 串起 pcap 转换、分类搬运、session 切分、统计特征、匿名化、截断/补零、train/test 划分和 npy 保存。
- 类别映射：`preprocess/pcapTransfer.py` 把原始 ISCX 文件名映射到 Email、Chat、FT、P2P、Streaming、VoIP 及 VPN 类。
- session 切分：`preprocess/pcap2session.py` 调用 SplitCap。
- 统计特征：`preprocess/FeaturesCalc.py` 定义 26 个特征；`statistic_feature2json.py` 遍历 session 生成 JSON。
- 匿名化与统一长度：`anonymizeSession.py` 清零 MAC/IP/端口；`pcapTrim.py` 截断或补零。
- npy 数据：`pcap2npy.py` 将 pcap 二进制转 uint8 数组，并绑定统计特征和标签。
- CENTIME 模型：`models/resnet1d_ae.py` 是核心实现，ResNet 输出 256 维，AE 输出 9 维，拼接后分类。
- 基线模型：`models/cnn1d.py`、`cnn1d_noPooling.py`、`cnn2d.py`、`cnn2d_noPooling.py`、`resnet18_1d.py`、`resnet18_2d.py`。
- 训练评估：`entry/CENTIME_Train.py` 使用交叉熵加 L1 重构损失；`utils/evaluate_tools.py` 输出 Accuracy、Precision、Recall、F1 和混淆矩阵。
- 随包数据：`data/npy_data/784_session_all` 中训练集 49,986 条、测试集 5,618 条；测试 pcap shape 为 `(5618, 784)`，统计特征 shape 为 `(5618, 26)`。

## 12. 本篇精华
- CENTIME 的核心不是“再造一个分类器”，而是补偿原始流量固定长度化导致的全局结构信息损失。
- 1D ResNet 处理流量字节比 2D 图像化更合理，因为字节流天然是序列，不是二维空间。
- 移除中间 pooling 对加密流量分类有明显帮助，说明局部字节细节仍有判别价值。
- 26 个统计特征主要承担 session 结构建模：包数、持续时间、包间隔、包长、payload 和协议/flag 比例。
- 784 bytes 已足够强，盲目拉长到 4096 bytes 会引入大量 padding，普通 CNN 性能反而下降。
- CENTIME 相比 ResNet1D 的增益不大但稳定，说明原始字节已经很强，统计特征是锦上添花而非唯一信息源。
- 最大风险是数据集和划分方式：高精度未必等于真实跨环境泛化能力。
- 对异常检测项目，最值得迁移的是“字节序列表征 + 行为统计表征 + AE 压缩/重构”的组合思想。

## 13. 建议精读路线
先读 Introduction，抓住两个痛点：人工统计特征依赖专家、原始字节统一长度损失结构信息。

再读 Section III，重点看 Fig.1 和 Fig.4，把 IFS、INUIT、ERIC 三部分对应到数据、模型和分类头。

然后精读 26 个统计特征和统一长度设置，理解为什么作者强调 duration、delta time、Num_pkts 这些无法从截断字节中可靠恢复的信息。

接着看 Table III，不要只看 CENTIME 最高分，要重点比较三组消融：784/1024/4096、pooling/noPooling、1D/2D。

最后结合代码读 `resnet1d_ae.py` 和 `CENTIME_Train.py`，特别注意论文描述与代码实现的归一化、学习率衰减、数据目录配置差异。