# [121] Bi-ETC: A Bidirectional Encrypted Traffic Classification Model Based on BERT and BiLSTM

## 1. 基本信息

- 编号：121
- 题名：Bi-ETC: A Bidirectional Encrypted Traffic Classification Model Based on BERT and BiLSTM
- 中文题名：Bi-ETC：一种基于 BERT 与 BiLSTM 的双向加密流量分类模型
- 年份：2023
- 来源：2023 8th International Conference on Data Science in Cyberspace (DSC)
- DOI：10.1109/DSC59305.2023.00037
- 任务类型：加密流量应用识别 / 加密流量分类
- 数据集：ISCX VPN
- 本地代码状态：未发现对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文关注的是：在数据包内容被加密、端口和明文字段逐渐失效的情况下，如何仍然从加密流量的字节序列中识别应用类别。

作者的核心判断是：加密隐藏了明文内容，但并没有完全抹平应用流量的内在模式。不同应用在加密后的 payload 中仍可能保留统计差异、上下文依赖和序列结构。已有 BERT 类预训练方法能从加密字节 token 中学习隐式表示，但作者认为它们对 token 序列之间的长距离依赖捕获不足；CNN 类方法能捕获局部模式，但对长距离上下文建模有限。

因此，论文提出 Bi-ETC：先用 BERT 对加密流量 payload 的 token 序列做上下文表示，再把 BERT 输出的 token-level 表征送入 BiLSTM，以捕获前向和后向的长距离序列依赖。模型还把 BERT 中代表整包语义的 `[CLS]` 特征复制到 BiLSTM 输入序列末尾，形成 `[CLS]-tokens-[CLS]`，让前向和后向 LSTM 都更容易接触到包级特征。最终通过带 PReLU 的分类层输出应用类别。

在 ISCX VPN 数据集的 17 类应用识别任务上，Bi-ETC 报告了 99.70% accuracy 和 99.43% F1-score，略高于 ET-BERT(packet) 和 BFCN 等强基线。

## 3. 论文解决的具体问题

论文解决的不是泛泛的“流量分类”，而是更具体的加密流量应用识别问题：

1. 传统端口识别、DPI、明文指纹方法在加密场景下可靠性下降。
2. 机器学习方法依赖人工统计特征，特征设计成本高，且不保证对分类真正有效。
3. 深度学习方法可以直接学习原始流量模式，但通常需要大量标注样本。
4. 预训练模型能利用无标注流量学习表示，但单独使用 BERT 的 `[CLS]` 或 FFNN 分类时，可能没有充分利用 token 序列的长距离关系。
5. CNN 增强方法能补充局部依赖，却不适合强调长序列中的前后文依赖。

所以，Bi-ETC 试图回答的问题是：在只使用加密 payload、尽量不依赖明文和人工特征的前提下，能否通过“BERT 表征 + BiLSTM 序列建模 + `[CLS]` 包级特征强化”提高加密应用识别性能？

## 4. 创新点深度提炼

第一，论文把 BERT 输出的 token 表征继续交给 BiLSTM，而不是只使用 `[CLS]` 进入分类器。这个设计的动机是：BERT 已经提取了上下文化 token 表示，但分类时若只取 `[CLS]`，可能浪费大量 token-level 信息；BiLSTM 可以在 BERT 表征空间里继续建模 token 序列的前后依赖。

第二，作者提出 `[CLS]-tokens-[CLS]` 的 BiLSTM 输入策略。BERT 头部 `[CLS]` 被视为整包级别的语义特征。将它复制到序列尾部后，前向 LSTM 和后向 LSTM 在序列两端都能更直接地接触包级表示，缓解 LSTM 长序列传播中的遗忘问题。

第三，论文把包级特征和 token 级上下文放在同一条序列建模路径中处理。其含义是：分类不是单靠某个全局向量，也不是单靠局部 byte n-gram，而是让整包摘要特征与 payload token 序列共同参与双向时序建模。

第四，作者比较了 PReLU 与 tanh 作为分类层激活函数的效果，并认为 PReLU 对负半轴的可学习缩放有助于提高分类表现。这个创新较弱，但属于论文模型细节的一部分。

第五，实验把 Bi-ETC 与传统指纹、机器学习、深度学习、预训练模型共 11 类方法比较，试图证明该方法不仅优于早期方法，也能在强预训练基线 ET-BERT(packet)、BFCN 上获得增益。

## 5. 科学问题与研究假设

论文背后的科学问题可以概括为：

加密后的 payload 是否仍包含足以区分应用类型的隐式模式？如果有，怎样的神经网络结构更适合提取这些模式？

对应的研究假设有四个：

1. 加密流量不是完全随机的，不同应用生成的加密字节序列仍存在可学习的分布差异。
2. BERT 可以把十六进制 bi-gram token 转换为具有上下文信息的 token 表征。
3. BERT 输出的 token 序列仍保留时序结构，继续使用 BiLSTM 能补充长距离依赖建模。
4. `[CLS]` 包级特征对分类非常重要，把它放在 BiLSTM 输入序列的首尾两端，可以增强模型对整包语义的记忆和利用。

这些假设中，前三个较合理；第四个更偏工程经验，需要依赖消融实验支撑。论文确实做了 `[CLS]-tokens` 与 `[CLS]-tokens-[CLS]` 对比，但没有给出非常细的统计显著性分析。

## 6. 科学方法与技术路线

技术路线可以拆成六步：

1. 数据清洗  
   删除重传、乱序、ICMP、DNS 等与应用分类目标关系不强或可能扰乱模式的数据包，只保留 IP 数据包。

2. payload 提取  
   丢弃 Ethernet、IP、传输层头部，只截取传输层 payload。这样模型不依赖端口、IP 地址、协议头字段等显式信息。

3. 十六进制与 bi-gram 编码  
   将 payload 转成十六进制字符串，再用 bi-gram 方式编码为 token 序列。例如图中出现的 `781d`、`1dc3`、`c35f`、`f302` 这类 token，可理解为相邻字节组合后的离散单元。

4. BERT 表征提取  
   在 token 序列头部加入 `[CLS]`，输入 BERT。BERT 输出 `[CLS]` 和每个 traffic token 的上下文向量。

5. BiLSTM 双向序列建模  
   将 BERT 输出序列输入 BiLSTM。论文关键策略是把头部 `[CLS]` 特征复制到序列末尾，形成首尾都有包级特征的输入。

6. 分类  
   拼接或组合前向、后向 LSTM 的最后输出，经 dropout、PReLU 和 SoftMax 分类，输出 17 类应用标签。

## 7. 实验设计与实验步骤

可复核流程如下。

数据：使用 ISCX VPN 数据集。论文将 VPN session 中的 pcap 按应用重新定义为 17 类：AIM Chat、Email、Facebook、Gmail、Hangout、ICQ、Netflix、SCP、Skype、Spotify、Tor、Torrent、Vimeo、VoipBuster、VPN-FTPS、VPN-SFTP、Youtube。

预处理：过滤重传、乱序和网络查询类数据包，例如 ICMP、DNS；仅保留 IP 包；去除链路层、IP 层和传输层头部；只使用传输层 payload；转为十六进制；用 bi-gram 构造 token 序列。每类最多取 5000 个样本，AIM Chat 为 1340，ICQ 为 823，用于观察类别不平衡下的效果。训练、验证、测试按 8:1:1 划分。

模型：主模型为 BERT + BiLSTM。BERT 输入长度为 128，BERT hidden size 为 768，BiLSTM hidden size 为 768，BiLSTM 层数为 2。BiLSTM 输入采用 `[CLS]-tokens-[CLS]`。输出经 dropout 和带 PReLU 的分类层，再用 SoftMax 做 17 类分类。

基线：论文比较了 FlowPrint、AppScanner、BIND、DF、FS-Net、Tree-RNN、Deep Packet、PERT、CBD、ET-BERT(flow)、ET-BERT(packet)、BFCN。覆盖了指纹、传统机器学习、深度学习和预训练模型。

训练：epoch 为 15，batch size 为 32，初始学习率为 2e-5，warmup ratio 为 0.1，dropout 为 0.1，优化器为 AdamW，损失函数为交叉熵。实验硬件为 8 张 Tesla T4 GPU。

指标：使用 accuracy、precision、recall、F1-score。因为是多分类任务，论文先按类别计算 TP、FP、TN、FN，再汇总报告整体结果。

消融/敏感性：一组对照比较 BERT-FFNN、BERT-LSTM、BERT-BiLSTM，用来验证 BiLSTM 是否比单向 LSTM 和直接 FFNN 更能利用 token 序列。另一组比较 `[CLS]-tokens` 与 `[CLS]-tokens-[CLS]`，验证尾部复制 `[CLS]` 的作用。第三组比较 tanh 与 PReLU 激活函数。

结果核查：主表中 Bi-ETC 的 accuracy 为 0.9970，precision 为 0.9934，recall 为 0.9951，F1-score 为 0.9943。类别表显示多数类别接近 1.000，ICQ 这类小样本类别 F1 为 0.958，说明不平衡类别仍是相对薄弱点。混淆矩阵据称主对角线颜色很深，表示类别间混淆较少。

## 8. 关键结果、结论与证据

最核心结果是：Bi-ETC 在 ISCX VPN 17 类应用识别上达到 99.70% accuracy 和 99.43% F1-score。

与强基线相比，提升幅度不大但有意义：ET-BERT(packet) 的 accuracy 为 0.9962、F1 为 0.9941；BFCN 的 accuracy 为 0.9965、F1 为 0.9941；Bi-ETC 分别提升到 0.9970 和 0.9943。也就是说，论文的主要价值不是把性能从低水平拉到高水平，而是在强预训练模型已经接近饱和的公开数据集上进一步挤出小幅增益。

类别级结果显示，Netflix、Spotify、Tor、Vimeo、VPN-FTPS、Youtube 等类别几乎满分；AIM Chat 和 ICQ 明显更难，尤其 ICQ 只有 823 个样本，Bi-ETC 的 precision 为 0.941、recall 为 0.976、F1 为 0.958。这说明模型对小样本类别有一定鲁棒性，但精度仍受数据量影响。

消融实验支持两个判断：一是 BERT-BiLSTM 优于 BERT-FFNN 和 BERT-LSTM，说明利用双向序列上下文确有帮助；二是 `[CLS]-tokens-[CLS]` 比只在头部放 `[CLS]` 收敛更快、最终准确率更高，说明首尾包级特征强化对 BiLSTM 有正作用。

论文最后结论是：BERT 负责学习加密 traffic token 的隐式表示，BiLSTM 负责捕获 token 表征之间的上下文和长距离依赖，两者结合能提升加密应用识别效果。

## 9. 局限性与待解决问题

第一，实验主要集中在 ISCX VPN 一个公开数据集上。该数据集常用于加密流量分类，但数据年代、应用版本、加密协议栈和真实网络环境都可能与当前网络存在差异。模型在跨数据集、跨时间、跨网络环境下的泛化能力没有被充分验证。

第二，性能已经接近饱和，Bi-ETC 相对 ET-BERT(packet)、BFCN 的提升很小。论文没有提供多次重复实验的均值、方差或显著性检验，因此很难判断 0.02% 到 0.08% 级别的提升是否稳定。

第三，数据划分可能存在流量泄漏风险。论文说按样本 8:1:1 划分，但没有明确说明是否按 pcap、session、flow 或时间隔离划分。如果同一会话或高度相似的数据包同时出现在训练和测试中，结果会偏乐观。

第四，预训练细节不足。论文提到 BERT-FFNN 是预训练阶段模型，也说 ISCX VPN 出现在预训练大规模无标注数据中，但没有完整交代预训练语料规模、任务设计、训练轮数和是否存在测试分布泄漏。

第五，模型计算成本较高。BERT 后接两层 BiLSTM，且实验使用 8 张 Tesla T4。论文没有报告推理时延、吞吐量、模型参数量和部署成本，这对在线流量识别很关键。

第六，预处理选择可能影响现实适用性。删除重传、乱序、DNS、ICMP，并只保留 payload，有助于实验干净，但真实网络中的异常检测和安全监测往往恰恰需要利用这些“非理想”现象。

第七，论文图表和文字存在一些不严谨之处，例如 accuracy 拼写错误、引用编号疑似错位、混淆矩阵标题出现 “TETBB model” 这类不一致表述。这不直接否定方法，但提示复现实验时需要谨慎核对原 PDF 和代码实现。

## 10. 与本项目的关系

本项目方向是异常检测，该论文虽然主任务是加密流量应用识别，但相关性很强。

它的启发在于：即便 payload 被加密，字节序列分布、包级摘要特征、token 上下文和时序依赖仍可作为行为建模对象。异常检测可以借鉴这种思路，把“应用类别监督分类”改造为“正常行为表征学习 + 偏离检测”。

可迁移的部分包括：payload 十六进制 bi-gram token 化、BERT 式预训练、`[CLS]` 包级表示、BiLSTM 捕获长距离依赖、基于 packet-level 表征进一步聚合到 flow/session-level。

需要谨慎的地方是：异常检测比闭集分类更难。论文的 17 类识别是在已知类别内做分类，而实际异常往往是未知类、低频类、概念漂移或混合攻击流量。若直接照搬 SoftMax 分类框架，可能无法处理开放集异常。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法逐文件对应到实际源码。

如果复现 Bi-ETC，合理的代码结构应大致对应以下模块：

- 数据预处理：读取 pcap，过滤重传、乱序、ICMP、DNS，提取传输层 payload，转十六进制，生成 bi-gram token。
- 数据集构造：按 17 个应用标签重标注 ISCX VPN，每类最多 5000 样本，划分 train/valid/test。
- tokenizer/vocab：维护十六进制 bi-gram token 到 id 的映射，并插入 `[CLS]`。
- BERT 模型：加载或训练 traffic BERT，输出 `[CLS]` 和 token hidden states。
- BiLSTM 分类器：接收 BERT hidden states，构造 `[CLS]-tokens-[CLS]`，经过 2 层 BiLSTM、dropout、PReLU、SoftMax。
- 训练脚本：AdamW、交叉熵、warmup、batch size 32、epoch 15、学习率 2e-5。
- 评估脚本：输出 accuracy、precision、recall、F1 和混淆矩阵。
- 消融脚本：切换 BERT-FFNN、BERT-LSTM、BERT-BiLSTM，切换 `[CLS]` 是否复制到尾部，切换 tanh/PReLU。

复现时最关键的不是模型代码本身，而是数据划分粒度和预训练设置。若这两处与论文不一致，最终指标可能差异很大。

## 12. 本篇精华

- Bi-ETC 的核心不是重新设计 BERT，而是在 BERT traffic token 表征之后加入 BiLSTM，补足长距离序列依赖建模。
- `[CLS]-tokens-[CLS]` 是本文最有辨识度的结构设计：把包级摘要特征放到 BiLSTM 序列两端，增强双向 LSTM 对整包信息的利用。
- 方法完全基于加密 payload，不依赖端口、IP、协议头或明文字段，符合加密流量分类的现实约束。
- ISCX VPN 上 Bi-ETC 达到 99.70% accuracy、99.43% F1，但相对 ET-BERT(packet)、BFCN 的提升很小，需要关注统计显著性和数据泄漏风险。
- 小样本类别 ICQ 的 F1 为 0.958，说明模型虽有一定不平衡鲁棒性，但低资源类别仍是短板。
- 对异常检测的主要启发是：可以把加密 payload 表征作为行为基线，再从闭集分类扩展到开放集、未知异常和跨域迁移。
- 论文最大的待补强点是泛化验证：跨数据集、跨时间、跨协议版本、真实在线环境下是否仍有效尚未证明。

## 13. 建议精读路线

第一遍读摘要、Introduction 和 Motivation，抓住作者为什么认为 BERT 之后还需要 BiLSTM：关键是“预训练表示不足以显式捕获长距离 token 关系”。

第二遍重点读 Methodology，尤其是数据预处理和模型结构图。要弄清楚输入不是完整数据包，而是去头后的 transport payload；token 不是自然语言词，而是十六进制 bi-gram。

第三遍精读实验设置，特别关注 ISCX VPN 的 17 类重标注、每类采样上限、8:1:1 划分、BERT 长度 128、hidden size 768、BiLSTM 2 层这些复现参数。

第四遍读对比实验和消融实验，不只看最终分数，还要看 BERT-FFNN、BERT-LSTM、BERT-BiLSTM 的差异，以及 `[CLS]` 复制到尾部是否真正解释了性能提升。

第五遍带着质疑读局限：检查是否存在数据泄漏、预训练语料重叠、单数据集过拟合、指标接近饱和但缺少显著性检验等问题。对于本项目，建议把它作为“加密流量表征学习”的参考，而不是直接作为异常检测完整方案。