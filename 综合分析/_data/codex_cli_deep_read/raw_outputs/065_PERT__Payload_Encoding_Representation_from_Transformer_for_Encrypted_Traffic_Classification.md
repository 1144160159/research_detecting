# [065] PERT: Payload Encoding Representation from Transformer for Encrypted Traffic Classification

## 1. 基本信息

- 题名：PERT: Payload Encoding Representation from Transformer for Encrypted Traffic Classification
- 中文题名：PERT：面向加密流量分类的基于 Transformer 的载荷编码表示
- 年份与来源：2020，ITU Kaleidoscope: Industry-Driven Digital Transformation
- DOI：10.23919/ituk50268.2020.9303204
- 作者与机构：Hong Ye He、Zhi Guo Yang、Xiang Ning Chen，ZTE
- 任务类型：加密流量分类、应用识别、端到端流量表示学习
- 正文状态：提供的正文包未截断；但 PDF 抽取文本中有少量编码乱码，主要不影响方法与实验理解。
- 代码状态：本地未发现该论文对应开源代码包。

## 2. 中文翻译与核心摘要

这篇论文的核心意思是：不要再把加密流量 payload 简单当作灰度图交给 CNN，而是把 payload 字节序列当作一种“类语言序列”，用 Transformer/BERT 式动态词嵌入学习上下文表示。作者将两个字节组成一个 token，即 bigram，构造最大约 65536 的字节对词表；再用无标签流量做 masked language model 预训练，使编码器先学会 payload 字节对的上下文分布；最后把预训练编码器迁移到流级分类任务中。

PERT 的分类流程是：对一个 flow 取前若干个 packet；每个 packet 的 payload 转为 bigram token 序列；每个 packet 前加 `cls` 标记；Transformer/ALBERT 编码后取每个 packet 的 `cls` 向量；把多个 packet 的 `cls` 向量拼接；接 softmax 完成流级类别预测。

论文在 ISCX2016 VPN-nonVPN 数据集和作者自采的 100 类 Android HTTPS 应用流量上验证。PERT 在 ISCX 上 F1 达到 0.9323，在 Android HTTPS 上 F1 达到 0.9007，均高于传统统计特征方法、CNN 方法和 HAST 系列方法。

## 3. 论文解决的具体问题

论文要解决的不是泛泛的“流量分类”，而是一个更具体的问题：当 payload 被加密、DPI 关键字不可用、端口号也不可靠时，如何从早期流量包中自动学习可用于应用或流量类别识别的表示。

传统 ML 方法依赖人工统计特征，例如端口、长度、到达间隔、方向等；CNN 类方法则把原始字节映射成一维或二维“图像”。作者认为后一种做法虽然端到端，但把字节当像素并不自然，因为 payload 字节的顺序和上下文关系更接近离散序列，而不是视觉图像。PERT 因此试图回答：加密 payload 中残留的协议握手、实现习惯、长度结构和字节上下文分布，能否通过 NLP 式动态嵌入被捕获，并转化为分类优势。

## 4. 创新点深度提炼

1. 将 payload 字节建模为“类语言序列”。论文没有沿用 CNN 灰度图路线，而是把字节序列转成 token 序列，直接引入 Transformer 表示学习。

2. 使用双字节 bigram tokenization。单字节只有 256 种取值，表达能力偏弱；两个字节组合扩展到 0-65535 的 token 空间，使 payload 序列更接近 NLP 中的词表规模，也让模型能够学习更细的局部字节模式。

3. 引入动态上下文嵌入。传统 Word2Vec 式静态嵌入给同一 token 固定向量，而 PERT 借助 Transformer 自注意力，让同一字节对在不同上下文中拥有不同表示，这正契合协议字段、握手片段和加密载荷前缀的上下文依赖性。

4. 将 BERT 的“预训练 + 微调”迁移到加密流量分类。作者先用大量无标签 packet payload 做 masked LM 预训练，再在有标签 flow 分类上微调，这一点是论文的主要方法贡献。

5. 采用 packet-level 预训练、flow-level 分类。直接把整个 flow 串成长序列做 Transformer 编码成本过高，因此作者先对单包 payload 建模，再在流级把多个包的 `cls` 表示合并。

6. 发现简单拼接可替代 LSTM 合并。论文比较了拼接与 LSTM 合并 encoded packet 的方式，结论是最终精度差别不大，但拼接收敛更快，工程上更划算。

## 5. 科学问题与研究假设

科学问题可以概括为：加密流量 payload 中是否仍存在可学习的上下文分布特征，并且这种特征是否更适合用 Transformer 式序列模型捕获，而不是 CNN 图像模型或人工统计特征捕获。

论文隐含了几条研究假设：

- 假设 1：即使 payload 加密，flow 前几个 packet 仍包含足够的可见或半结构化信息，例如握手细节、协议实现痕迹和早期载荷模式。
- 假设 2：payload 字节对之间存在上下文依赖，Transformer 自注意力可以学习这种依赖。
- 假设 3：无标签流量中包含可迁移的通用 payload 分布，masked LM 预训练能改善下游分类。
- 假设 4：flow 级类别可以由前 5-10 个 packet 的 packet-level 表示近似决定。
- 假设 5：复杂的 packet 序列合并器不一定必要，拼接多个 packet 的 `cls` 向量已经能保留足够分类信息。

## 6. 科学方法与技术路线

PERT 的技术路线分为四层。

第一层是 payload tokenization。对每个 packet 提取 payload bytes，把相邻两个字节组成 bigram token，token 取值范围相当于 0-65535。这样，原始二进制 payload 被转成离散 token 序列。

第二层是 Transformer 编码。每个 token 先得到初始 embedding，然后经过多层 self-attention 和前馈网络。自注意力通过 Query、Key、Value 计算 token 与上下文中其他 token 的关系，多头机制让模型从多个子空间学习 payload 上下文结构。

第三层是 packet-level 预训练。作者采用 BERT 类 masked language model：随机遮蔽 payload bigram，模型根据上下文预测被遮蔽 token。预训练数据不需要标签，只需要大量原始流量 packet。

第四层是 flow-level 分类。对每条 flow 取前 `M` 个 packet，默认 `packet_num=5`；每个 packet 前加 `cls`；编码后取各 packet 的 `cls` 向量；将这些向量拼接后送入 softmax 分类层。微调时，分类损失会反向更新预训练编码器。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据准备：收集三类数据。无标签流量用于预训练，要求覆盖尽可能多的主流协议；ISCX2016 VPN-nonVPN 用于公开数据集评估，并按 DeepTraffic 的预处理与标注方式整理成 12 类；Android 数据集由作者采集 100 个中国 Android 应用流量，只保留 HTTPS flows。

2. 预处理：按五元组切分 flow；对 flow 中前若干 packet 提取 payload；每个 packet 的 payload 按两个字节组成 bigram token；单包输入长度设为 128 个 token；分类时每个 packet 前加入 `cls`；预训练时随机 mask 部分 token。

3. 预训练模型：论文实际使用 HuggingFace Transformers 中较轻量的 ALBERT 实现。关键配置为 `hidden_size=768`、`num_hidden_layers=12`、`num_attention_heads=12`、`intermediate_size=3072`、`input_length=128`。预训练使用 4 张 Nvidia Tesla P100。

4. 分类模型：编码器结构与预训练阶段一致；默认取每条 flow 前 5 个 packet；每个 packet 得到一个 `cls` 表示；拼接后接 softmax 分类层；`softmax_hidden=768`，`dropout=0.5`。微调阶段作者认为单 GPU 足够。

5. 对比基线：ML-1 是基于基本流统计特征的决策树；ML-2 在 ML-1 基础上加入前 10 个 packet 的端口、方向、长度、到达间隔等时间序列特征；CNN 包括 1D-CNN 和 2D-CNN，使用 flow 前 784 字节；HAST-I 直接学习 flow 前 784 字节；HAST-II 先做 packet-level 编码，再用 LSTM 合并。

6. 训练与验证：随机选择 90% 样本训练，10% 样本验证。指标采用平均 Precision、Recall、F1。

7. 消融与敏感性：一组实验改变 `packet_num`，观察使用更多前序包的收益；另一组比较 encoded packets 的合并方式，包括 PERT 拼接、PERT+LSTM、HAST+拼接、HAST+LSTM。

8. 结果核查：重点检查两张主表、packet 数量曲线和收敛曲线。应确认同一数据划分、同一预处理、同一类别定义下比较，否则 ISCX 上结果容易因标注与预处理差异而不可比。

## 8. 关键结果、结论与证据

ISCX 数据集上，PERT 的 Precision、Recall、F1 分别为 0.9327、0.9322、0.9323。最强传统增强特征方法 ML-2 的 F1 为 0.8898，HAST-I 为 0.8742，CNN-1D 为 0.8610。也就是说，PERT 相比 ML-2 仍有约 4.25 个百分点的 F1 提升。

Android HTTPS 数据集上，PERT 的 Precision、Recall、F1 分别为 0.9042、0.9003、0.9007。HAST-I 的 F1 为 0.8167，CNN-1D 为 0.7668，ML-2 为 0.7321。这个结果更能体现论文主张：当所有流量都是 HTTPS，传统统计特征更难区分类别，端到端表示学习的优势更明显。

关于 packet 数量，使用更多前序 packet 会提升 F1，但收益递减。Android 数据集上使用 20 个 packet 时 F1 为 91.35%，相比默认 5 个 packet 只提升 1.28 个百分点。作者因此建议 PERT 使用 5-10 个 packet 即可。

关于合并策略，LSTM 与拼接的最终分类精度差异不显著，但拼接收敛更快。因此论文选择“packet-level Transformer 编码 + flow-level 拼接分类”作为计算成本与效果之间的折中方案。

## 9. 局限性与待解决问题

第一，论文没有给出对应开源代码，本次也未发现本地代码包，因此无法核验数据切分、padding/truncation、mask 比例、类别映射、训练轮数、优化器等复现关键细节。

第二，预训练数据和 Android HTTPS 数据集并未公开到足够可复核的程度。尤其 Android 100 类应用流量可能包含设备、地区、服务端、采集时间等环境偏差，模型学到的可能不完全是应用本质行为。

第三，论文缺少 PERT 无预训练版本的消融。它证明了 PERT 总体强于基线，但没有清楚拆分“Transformer 架构本身”和“masked LM 预训练”各自贡献。

第四，评估采用随机 90/10 划分，缺少跨时间、跨设备、跨网络环境、跨版本应用的泛化验证。对真实部署而言，分布漂移可能比论文设置更困难。

第五，效率讨论不充分。预训练需要 4 张 P100，推理时每条 flow 要编码多个 packet；论文只说 fine-tuning 单 GPU 足够，没有给出吞吐、延迟、内存和在线分类成本。

第六，PERT 是闭集分类方法，不是异常检测方法。未知应用、未知攻击、协议升级、规避样本和开放集识别都不是本文直接解决的问题。

第七，正文包未截断；但提供的 PDF 文本抽取存在若干乱码，图 5、图 6 的曲线细节和部分排版公式若要严谨复现，仍建议回到原 PDF 核对。

## 10. 与本项目的关系

这篇论文与“异常检测”项目的关系很强，但要准确定位：它提供的是加密流量表征学习与闭集分类框架，不是直接的异常检测框架。

对本项目有价值的部分主要有三点。第一，PERT 的自监督预训练思想适合安全场景，因为真实网络中无标签流量远多于标注攻击样本。第二，packet-level 编码再 flow-level 聚合的架构，可以迁移到恶意流量检测、应用识别、VPN/代理识别和未知流量聚类。第三，Transformer 学到的 `cls` embedding 可以作为下游异常检测器的输入，例如接一类分类、聚类、距离度量、开放集分类或少样本检测模块。

需要注意的是，如果项目目标是“异常”而非“类别”，不能直接照搬 softmax 闭集分类。更合理的扩展是：先用 PERT 预训练得到通用 payload encoder，再在正常流量上学习正常簇或正常分布；或者用已知攻击/正常样本做监督检测，同时保留未知类拒识机制。

## 11. 代码对照分析

本地未发现该论文对应代码包，因此无法进行真实源码逐文件对应。论文中明确提到的实现线索包括：ISCX 预处理参考 DeepTraffic 项目，模型实现使用 PyTorch，预训练编码器使用 HuggingFace Transformers，并选择 ALBERT 作为优化版 BERT。

如果复现，代码结构应大致对应如下：

| 论文模块 | 可能的源码角色 | 关键实现点 |
|---|---|---|
| PCAP/flow 处理 | `preprocess/pcap_to_flow.py` | 五元组切流，提取前 `M` 个 packet，过滤 HTTPS 或按数据集规则标注 |
| payload tokenization | `tokenizer/payload_bigram.py` | 两字节合成 0-65535 token，处理 padding、截断、特殊符号 `cls`、`unk` |
| MLM 预训练数据 | `pretrain/build_mlm_dataset.py` | 对 packet token 序列随机 mask，生成 masked positions 与 labels |
| PERT/ALBERT 编码器 | `models/pert_encoder.py` | `hidden_size=768`、12 层、12 heads、长度 128，输出 packet 的 `cls` 向量 |
| 流级分类器 | `models/flow_classifier.py` | 对前 5 个 packet 分别编码，拼接 `cls`，dropout 后 softmax |
| 训练脚本 | `train_pretrain.py`、`train_classifier.py` | 先无监督预训练，再加载 encoder 权重微调 |
| 评估脚本 | `evaluate.py` | 平均 Precision、Recall、F1，复现实验表 3 和表 4 |
| 消融实验 | `experiments/packet_num.py`、`experiments/merge_strategy.py` | 比较 packet 数量、拼接与 LSTM 合并方式 |

最需要警惕的复现点是 ISCX 的标注流程。论文自己也指出，同一 ISCX 数据集在不同工作中的结果差异很大，主要来自原始数据处理和标签方式不同。

## 12. 本篇精华

- PERT 的核心不是“用 Transformer 做分类”这么简单，而是把加密 payload 重新定义为可自监督建模的离散序列。
- bigram tokenization 是方法成立的关键桥梁：它把 256 取值的裸字节扩展为更适合嵌入学习的字节对词表。
- packet-level MLM 预训练利用了大量无标签流量，是安全场景中非常实用的思想。
- flow-level 分类没有直接编码长 flow，而是编码多个 packet 后拼接 `cls`，这是对 Transformer 成本的工程折中。
- 在纯 HTTPS Android 100 类任务上，PERT 相比 HAST-I 提升约 8.4 个 F1 百分点，说明上下文 payload 表示对强加密场景更有价值。
- 使用更多 packet 有收益但很快递减，5-10 个 packet 是论文推荐的效果/成本平衡点。
- 拼接 encoded packet 与 LSTM 合并精度接近，但拼接更快，说明复杂时序合并器不一定是瓶颈。
- 论文最大的短板是可复现性与泛化验证不足，尤其缺少代码、预训练数据细节和无预训练消融。

## 13. 建议精读路线

1. 先读引言和相关工作，抓住作者为什么反对单纯把 payload 当图像处理。
2. 精读 3.1 的 bigram tokenization，这是 PERT 从网络流量跨到 NLP 框架的关键。
3. 快速读 3.2 的 Transformer 公式，只需理解 self-attention 如何让字节对表示依赖上下文。
4. 重点读 3.3 和 3.4，区分 packet-level 预训练与 flow-level 微调，这是论文真正的方法设计。
5. 精读 4.1 的数据集和参数设置，尤其 ISCX 标注、Android HTTPS 采集、ALBERT 参数和 `packet_num`。
6. 对照表 3、表 4 看 PERT 相对 ML、CNN、HAST 的收益，不只看最高分，还要看 HTTPS 场景下统计特征失效的趋势。
7. 最后读 4.3、4.4，把 packet 数量和合并方式视为工程部署问题，而不是单纯的消融实验。