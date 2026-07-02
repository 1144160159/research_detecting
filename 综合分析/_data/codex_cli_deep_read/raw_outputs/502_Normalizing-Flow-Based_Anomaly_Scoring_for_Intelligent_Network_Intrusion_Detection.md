# [502] Normalizing-Flow-Based Anomaly Scoring for Intelligent Network Intrusion Detection

## 1. 基本信息

题录给出的题名是 **Normalizing-Flow-Based Anomaly Scoring for Intelligent Network Intrusion Detection**，年份 2025，DOI 为 `10.1109/qpain66474.2025.11171745`，来源标注为 QPAIN 2025。正文包实际呈现的是 **SAFE-NID: Self-Attention with Normalizing-Flow Encodings for Network Intrusion Detection**，标注发表于 TMLR 2025-03；代码仓库 README 也对应 SAFE-NID。因此这里应视为同一研究线索的正文/代码版本，但题名、会议信息与正文头部存在不一致，后续引用时建议回到 PDF/DOI 核验。

作者包括 Brian Matejek、Ashish Gehani、Nathaniel D. Bastian、Daniel J. Clouse、Bradford Kline、Susmit Jha，机构涉及 SRI International、Army Cyber Institute 和美国国防部相关实验室。主题属于入侵检测、网络异常检测、OOD/零日攻击检测与模型安全监测。

## 2. 中文翻译与核心摘要

可译为：**基于归一化流异常评分的智能网络入侵检测**；正文版本题名可译为：**SAFE-NID：用于网络入侵检测的自注意力与归一化流编码方法**。

论文的核心不是再提出一个“更高准确率”的 NIDS 分类器，而是指出：包级深度模型在已知攻击上可以轻松超过 99% 准确率，但面对训练时从未出现的攻击类别和自然流量漂移时会非常自信地犯错。SAFE-NID 的回答是：先用轻量 encoder-only Transformer 对单包 payload 与安全挑选的 header context 做二分类，再用 normalizing flow 学习分类器内部特征的类条件分布，把低似然样本作为 OOD/零日可疑包交给进一步调查。

## 3. 论文解决的具体问题

论文针对三个实际痛点：

1. 流级 IDS 有天然滞后性。CICFlowMeter、Zeek 等 flow summary 要等连接结束后才能得到持续时间、包数、速率等统计量，不适合毫秒级拦截。
2. 深度 NIDS 的高测试集准确率掩盖了开放世界失败。已知攻击检测很强，但训练集中缺失的攻击类型会被误判为 benign。
3. 网络流量长期演化导致概念漂移。例如 2015 到 2017 年 HTTP/HTTPS 使用比例明显变化，旧模型跨数据集迁移时准确率接近随机甚至带有系统性偏差。

因此论文真正解决的是：**如何在包级实时检测框架里，为一个判别式入侵检测模型增加“我不可信”的异常评分机制。**

## 4. 创新点深度提炼

第一，论文把问题从 flow-level 转向 packet-level，并认真处理了标签继承难题。作者不是简单把 flow 标签复制到包，而是用五元组、反向五元组、时间窗精度缓冲和冲突丢弃规则，把公开 flow-level 数据集转成 packet-level 数据集。

第二，header 特征选择有防泄漏意识。模型使用 IPv4 total length、源/目的端口分桶、TCP flags，但刻意排除源/目的 IP、TTL、protocol 等可能学习测试床配置的字段。

第三，OOD safeguard 建在 DNN 内部特征上，而不是 softmax 输出上。论文的判断是：零日攻击在 payload 原空间中变化可能很小，但在分类器学习出的 feature space 中更容易分离。

第四，normalizing flow 不是单独做无监督异常检测，而是类条件地包裹已有分类器：推理时先看分类器预测为 benign 还是 attack，再用对应类别的 flow 计算特征似然。这个设计更贴近部署，因为它是在“模型作出某个判断后”评估该判断是否可信。

第五，实验不是只报 AUROC，而是同时关注严重不均衡场景下的 TPR at TNR=95%/85% 和微秒级延迟，说明作者关心告警带宽与实时性。

## 5. 科学问题与研究假设

科学问题可以概括为：**在没有零日样本暴露的情况下，仅利用已知 benign/attack 训练数据，能否识别分类器遇到的未知攻击或流量漂移？**

主要研究假设是：

1. 包级 payload 与少量可泛化 header context 足以训练出高准确率 NIDS。
2. 已知类的内部表征分布比原始 payload 分布更适合 OOD 检测。
3. 类条件 normalizing flow 比 softmax、energy 等输出层置信度更能识别零日输入。
4. withheld attack category 可以近似模拟零日攻击；跨 UNSW-NB15 与 CIC-IDS-2017 可以近似模拟自然概念漂移。
5. safeguard 的额外延迟相对 DNN 推理和 flow 结束等待时间足够小，具备部署意义。

## 6. 科学方法与技术路线

技术路线是一个“判别分类器 + 生成式可信度监测器”的组合。

输入侧：每个包取前 1500 字节 payload；FNN/CNN 将字节归一化到 `[0,1]`，Transformer 则把每个字节当作 0-255 的 token。header context 共 23 维：8 个 TCP flag、1 个 total length 归一化值、源端口 7 维分桶、目的端口 7 维分桶。

分类器侧：SAFE-NID 主模型是 encoder-only Transformer，256 词表，1500 位置长度，384 维 embedding，2 个 Transformer block，6 个 attention heads，mean pooling 后拼接 header context，再接 256/128/64 的 MLP 输出 benign/attack。

safeguard 侧：从分类器中间层抽特征，对 benign 与 attack 分别训练 normalizing flow。推理时，分类器预测类别 `ŷ`，系统只查询 `ŷ` 对应的 flow；若负对数似然高，则认为该包落在训练分布外，需要进一步调查。

## 7. 实验设计与实验步骤

数据：使用 UNSW-NB15 与 CIC-IDS-2017。处理后 UNSW-NB15 约 4975 万 benign 包、245.8 万 attack 包，9 类攻击；CIC-IDS-2017 约 2918 万 benign 包、122 万 attack 包，14 类攻击。

预处理：用 flow CSV 与 pcap 匹配。先为 `(src_ip, src_port, dst_ip, dst_port, protocol)` 和反向五元组建索引；再用 packet timestamp 匹配 flow 的起止时间，并补偿 flow 时间字段精度较粗的问题；若同一包匹配到多个不同类别 flow，则丢弃；保留 TCP/UDP 非空 payload。

模型/基线：判别模型包括 FNN、CNN、Transformer。OOD 方法包括 MSP、Energy、Gaussian kernel density/Mahalanobis 和 Normalizing Flow。ODIN 也在附录中测试，但因不做参数调优和 outlier exposure，效果不稳定。

训练：训练/验证数据取一半恶意样本和等量 benign，75% 训练、25% 验证，10 个随机 split。FNN/CNN 训练 20 epoch，Transformer 训练 6 epoch。normalizing flow 每类训练一个，20 个 block，clamping=2.0，512 epoch，并加 `N(0,0.05)` 噪声稳定训练。

指标：已知类分类用 Accuracy、AUROC、F1；OOD 用 AUROC、TPR at TNR=95%、TPR at TNR=85%。后两个指标很关键，因为真实 IDS 不能把大量正常流量都丢给人工分析。

消融/敏感性：normalizing flow 的 clamping 在 0.5 到 3.0 间影响很小；block 数从 5 到 30 增加时验证损失下降，20 个 block 是性能与延迟折中点。

结果核查：先确认已知类分类是否超过 99%；再看 withheld attack recall 是否崩溃；最后用 OOD 分数检查这些崩溃样本是否能被 safeguard 捕获，而不是只看分类准确率。

## 8. 关键结果、结论与证据

已知攻击检测很强：UNSW-NB15 上 FNN accuracy 0.9951、F1 0.9953；CIC-IDS-2017 上 Transformer accuracy 0.9965、F1 0.9966。

零日模拟暴露了核心失败：CIC-IDS-2017 中 FTP-Patator、SSH-Patator、Infiltration 在作为已知类时 recall 接近 99% 或更高，但被排除训练后分别降到约 0.30%、0.27%、7.80%。这说明分类器不是学到了“攻击的一般本质”，而是在许多类别上依赖已见模式。

SAFE-NID 的 OOD 检测明显更稳：Transformer + Normalizing Flow 在 FTP-Patator、Infiltration、SSH-Patator 上 AUROC 分别约 0.9936、0.9668、0.9901；其中 FTP-Patator 和 SSH-Patator 在 TNR=95% 时 TPR 达到 100%。

概念漂移也被捕获：跨 UNSW-NB15/CIC-IDS-2017 推理时，分类 accuracy 大幅降至约 0.40-0.52；Transformer + Normalizing Flow 对 CIC-IDS-2017 OOD 的 AUROC 约 0.9259，对 UNSW-NB15 OOD 约 0.9583。Gaussian kernel density 在 UNSW-NB15 漂移场景甚至略高，约 0.9636。

延迟证据支持“可部署但需权衡”：FNN、CNN、Transformer 单包推理分别约 144.60、172.58、2418.02 微秒；safeguard 约 23-60 微秒。Transformer 更准但明显更慢，论文也承认高吞吐场景可能需要换用轻模型或模型压缩。

## 9. 局限性与待解决问题

本次理解基于提供的正文包；由于正文包被标注为截断，仍需回到 PDF 复核被截断部分，尤其是 6.5-6.7 中消融、延迟和 broader impact 的完整表述与表格排版。

方法层面，withheld known attack 只是零日近似，不等于真实未知漏洞。公开测试床流量规模虽大，但生成环境、攻击脚本和标签机制仍可能与真实企业网有差异。包级分析低延迟，但牺牲了 session/flow 级上下文，容易错过横跨多个包的行为模式。论文也没有处理自适应对手，即攻击者知道 normalizing flow safeguard 后构造规避样本。

工程层面，Transformer 单包 2.4ms 在高速链路上仍偏重；代码配置大量使用 `~/trinity-packet` 路径，Windows 复现需要改路径；README 还提示 CIC 每个 split 可能产生约 90GB 临时文件，复现实验的存储成本不低。

## 10. 与本项目的关系

对“异常检测”项目来说，这篇文章最有价值的是方法范式：**不要只训练闭集分类器，而要在分类器内部表征上训练一个异常评分器**。这适合迁移到加密流量分类、应用识别、IoT 异常检测和 AI 安全监控中。

如果本项目已有一个流量分类模型，可以借鉴 SAFE-NID：保留分类头用于已知类别识别，同时抽取倒数第一或倒数第二隐藏层，用 normalizing flow 或 Mahalanobis 建类条件分布，把高 NLL/高距离样本作为未知应用、未知攻击或漂移告警。

但如果本项目目标是加密流量，不能过度依赖 payload 内容。SAFE-NID 的端口分桶、长度、flags 思路可以保留，但更应加入时间序列、包长序列、方向序列和 flow/session 统计，形成包级低延迟与流级上下文的混合检测。

## 11. 代码对照分析

代码仓库与论文主体高度对应。依赖环境在 [environment.yml](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/environment.yml)，包含 `dpkt`、`torch`、`freia`、`pytorch-ood`、`scikit-learn` 等。

数据预处理主要在 [preprocess.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/context_pcap/preprocess.py:433)：`pcap_to_dataframe`、`generate_flow_labels_hash`、`read_pcap_data` 对应论文附录 A 的 flow-to-packet 转换。数据集封装在 [dataset.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/context_pcap/dataset.py:87)，其中 `HEADER_LENGTH=23`、端口分桶、payload hex 到 byte token 的转换都能对应 4.3 节。

模型定义分散在 [transformer.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/context_pcap/transformer.py)、[cnn.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/context_pcap/cnn.py)、[fnn.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/context_pcap/fnn.py)。Transformer 文件中可见 256 字节词表、1500 位置编码、384 embedding、2 层 block、6 heads、mean pooling 和 `linear1/2/3` 可抽取层。

训练、推理和评估主逻辑在 [network_model.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/data_structures/network_model.py) 与 [experiment.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/data_structures/experiment.py:1016)。后者实现 `run_training`、`run_inference`、feature extraction、MSP、Energy/ODIN、Mahalanobis、`train_normalizing_flows` 和 `calculate_normalizing_flows`。

Normalizing flow safeguard 在 [iaf.py](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/code/netflow/detectors/iaf.py)，用 FrEIA `SequenceINN` 和 `AllInOneBlock`，默认 20 blocks、clamping=2.0，训练/推理时加入 0.05 高斯噪声。实验配置示例在 [OOD-Infiltration Transformer 配置](F:/泉城实验室/二期/论文/异常检测/source/trinity-packet/SAFE-NID/configs/experiments/OOD-Infiltration-model-ContextTransformer-header_context.exp)，其中 ID examples 明确排除了 Infiltration，OOD examples 只放 Infiltration。

运行线索：`conda env create -f environment.yml`、`conda activate trinity_packet_env`；`notebooks/data_processing.ipynb` 生成 split 和 unbalanced chunks；`notebooks/experiment_pipeline.ipynb` 调用 `ContextPCAPExperiment` 完成训练、推理、特征抽取、Mahalanobis 与 normalizing flow 评分。本次是只读精读，没有实际训练复现实验。

## 12. 本篇精华

1. 高闭集准确率不是安全性：NIDS 在已知攻击上超过 99%，但 withheld 攻击可被几乎全部判成 benign。
2. OOD 检测应看内部表征，不应只信 softmax/logits；MSP 和 Energy 在本文零日场景下明显不足。
3. 类条件 normalizing flow 的关键是“按预测类别查分布”，它评估的是模型这次判断是否落在该类训练特征流形上。
4. 包级检测真正难点不只在模型，而在如何从 flow-level 标签可靠地产生 packet-level 标签。
5. Header context 要防数据泄漏；IP、协议等字段在测试床里可能给出虚假高分。
6. Transformer + Normalizing Flow 在零日 OOD 上 AUROC 约 0.97-0.99，是论文最强证据链。
7. 部署时要在准确率和吞吐之间选型：SAFE-NID 最强但 Transformer 延迟最高，FNN/CNN 更轻但 OOD 质量较弱。

## 13. 建议精读路线

先读 Introduction 的 Figures 1-3，抓住“原始 payload 空间难分、内部特征空间可分、safeguard 介入决策”的主线。

再精读 4.2 和 Appendix A，理解 flow-to-packet 标签转换；这部分是做网络异常检测数据集时最容易被忽略、也最容易产生伪结论的地方。

然后读 4.3、4.4、4.7，把 header 特征、Transformer 结构、normalizing flow safeguard 串起来。读到这里后对照 `context_pcap/dataset.py`、`transformer.py`、`detectors/iaf.py` 看代码。

最后集中看 Tables 5-11：Table 5 证明闭集强，Table 6 证明零日失败，Tables 9-10 证明 safeguard 有效，Table 11 说明部署成本。消融和结论部分用于提炼后续改进方向。