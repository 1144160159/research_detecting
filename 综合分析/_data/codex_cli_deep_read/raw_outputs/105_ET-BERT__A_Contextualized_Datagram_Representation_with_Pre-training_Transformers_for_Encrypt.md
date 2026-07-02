# [105] ET-BERT: A Contextualized Datagram Representation with Pre-training Transformers for Encrypted Traffic Classification

## 1. 基本信息

- 论文：ET-BERT: A Contextualized Datagram Representation with Pre-training Transformers for Encrypted Traffic Classification
- 作者：Xinjie Lin, Gang Xiong, Gaopeng Gou, Zhen Li, Junzheng Shi, Jing Yu
- 发表：WWW 2022，DOI: `10.1145/3485447.3512217`
- 主题：加密流量分类、应用识别、恶意流量分类、VPN/Tor/TLS 1.3 场景迁移
- 正文包状态：本次提供正文未截断。
- 代码：本地仓库 `source\ET-BERT` 已核查，主体基于 UER-py 改造。

## 2. 中文翻译与核心摘要

题名可译为：**ET-BERT：一种用于加密流量分类的、基于预训练 Transformer 的上下文化数据报表示方法**。

这篇论文的核心不是再设计一个监督式流量分类器，而是把“加密流量中仍然保留的传输结构和密文字节相关性”当作可学习对象。作者认为，虽然载荷语义不可见，但流量并非完全随机：应用层内容组织、请求/响应方向、BURST 片段、加密实现差异都会留下统计与上下文痕迹。ET-BERT 先在约 30GB 无标签流量上预训练，再用少量有标签数据微调，覆盖通用应用识别、恶意流量、VPN、Tor、TLS 1.3 等任务。

## 3. 论文解决的具体问题

论文针对的是**加密场景下分类特征失效与泛化不足**的问题。DPI 依赖明文字段，在 TLS 1.3、VPN、Tor 等场景下越来越不可用；统计特征依赖人工经验；监督深度模型依赖大量标注样本，遇到长尾应用、类别不均衡或新加密协议时容易过拟合。

更具体地说，它要解决三件事：第一，从没有语义的密文字节中构造可被 Transformer 学习的输入单元；第二，用无标签开放域流量学习跨任务表示；第三，让该表示能迁移到小样本、多类别、类别不均衡的加密流量分类任务。

## 4. 创新点深度提炼

1. **把预训练范式引入加密流量分类，但不是简单套 BERT。** PERT 已经尝试过 Transformer 表示，ET-BERT 的重点在于为流量设计输入结构和自监督任务。
2. **Datagram2Token 将数据报转成类语言 token。** 论文用十六进制 bigram 表示相邻字节组合，并引入 `[CLS]`、`[SEP]`、`[MASK]`、segment embedding、position embedding。
3. **BURST 是关键抽象。** BURST 表示同一会话中连续同方向包的片段，作者把它看成应用层内容加载与请求响应行为在网络层的投影。
4. **MBM 学习字节上下文。** Masked BURST Model 类似 MLM，随机遮盖 15% token，让模型从上下文恢复密文字节片段。
5. **SBP 学习传输片段关系。** Same-origin BURST Prediction 判断两个 sub-BURST 是否来自同一 BURST，等价于把 BERT 的 NSP 改造成流量传输结构判别。
6. **给出随机性解释。** 作者用 NIST 随机性测试分析不同密码套件不完美随机的现实条件，解释为什么密文分类仍可能成立。
7. **覆盖 TLS 1.3 数据集。** CSTNET-TLS 1.3 是论文自建数据，强调新协议下传统明文/指纹方法退化而 ET-BERT 仍有效。

## 5. 科学问题与研究假设

科学问题可以概括为：**在不可见明文语义的条件下，密文字节序列和传输结构是否仍携带足够稳定、可迁移的类别信息？**

论文隐含了四个假设：加密实现与应用行为不会产生完美随机流量；同一应用或服务的 BURST 组织方式存在可学习规律；无标签大规模流量预训练能减少标注数据依赖；基于 `[CLS]` 的上下文化表示能同时服务 packet-level 与 flow-level 分类。

## 6. 科学方法与技术路线

技术路线是“PCAP/flow -> BURST -> bigram token -> Transformer 预训练 -> 下游微调”。模型主干是 12 层 Transformer、12 个注意力头、hidden size 768，配置也出现在 [bert_base_config.json](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\bert_base_config.json:1>)。

预训练阶段使用约 30GB 无标签流量，包括公开数据和 CSTNET 被动采集数据，协议覆盖 QUIC、TLS、FTP、HTTP、SSH 等。微调阶段把 packet 或 flow 转成同样的 token 序列，取 `[CLS]` 表示接分类头。论文中 flow-level 使用一个 flow 内连续 5 个包拼接，packet-level 使用单包输入。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：准备 Cross-Platform iOS/Android、USTC-TFC、ISCX-VPN-Service/App、ISCX-Tor、CSTNET-TLS 1.3；任务覆盖 GEAC、EMC、ETCV、EACT、EAC-1.3。
2. 预处理：去除 ARP、DHCP；去除 Ethernet/IP/TCP 端口等强标识头部；按五元组切会话；按方向生成 BURST；用十六进制 bigram 生成 token。
3. 预训练：构造 BURST 语料，生成词表，运行 `preprocess.py` 生成 `dataset.pt`，再用 `pre-training/pretrain.py` 训练 MBM+SBP，论文设置 batch 32、500k steps、学习率 `2e-5`、warmup 0.1。
4. 微调：每类最多采样 500 flows 和 5000 packets，按 8:1:1 划分训练/验证/测试；flow-level 学习率 `6e-5`，packet-level `2e-5`，10 epochs，batch 32，dropout 0.5。
5. 基线：FlowPrint、AppScanner、CUMUL、BIND、K-fp、DF、FS-Net、GraphDApp、TSCRNN、Deeppacket、PERT。
6. 指标：用 macro Accuracy、Precision、Recall、F1，避免类别不均衡掩盖小类性能。
7. 消融/敏感性：去掉 SBP、去掉 MBM、去掉 BURST、去掉预训练；比较 flow、concatenated-flow、packet；做 40%/20%/10% few-shot。
8. 结果核查：重点检查是否有头部泄漏、SNI 标签依赖、同一 flow 是否跨集合泄漏，以及 packet-level 高分是否来自同源会话片段重复。

## 8. 关键结果、结论与证据

ET-BERT 在多个任务上刷新结果：Cross-Platform Android F1 约 92.5%，ISCX-VPN-Service F1 98.9%，CSTNET-TLS 1.3 F1 97.4%。相对已有最好方法，论文报告在通用应用、恶意流量、VPN、Tor、TLS 1.3 上分别提升约 5.4%、0.2%、5.2%、4.4%、10.0%。

消融最能说明问题：在 ISCX-VPN-App 采样设置中，完整模型 F1 为 0.9395；去掉 SBP 降到 0.8998，去掉 MBM 降到 0.8462，去掉 BURST 降到 0.9258，而不做预训练直接监督训练只有 0.5638。这说明性能主要来自“无标签预训练 + 字节上下文 + BURST 传输结构”的组合，而不是单纯 Transformer 容量。

## 9. 局限性与待解决问题

论文自己承认三类风险：流量模式会随应用内容和时间漂移，固定预训练表示可能过期；TLS 1.3 后续 ECH 会隐藏 SNI，使 CSTNET-TLS 1.3 这类标签获取方式失效；预训练数据若被投毒，模型可能继承后门。

我认为还应补充：实验基本是闭集分类，不等价于真实网络中的开放集未知应用发现；随机性解释更像经验相关性分析，还不是严格因果证明；packet-level 高分需要特别警惕同源会话切分带来的近重复样本；代码复现依赖大量外部数据、SplitCap、tshark、硬编码 Windows 路径，工程可复现性弱于论文方法本身。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，但它本质上是**加密流量表征学习与闭集分类**，不是直接的异常检测算法。它可作为本项目的三类基础能力：无标签流量预训练、加密载荷不可见条件下的特征编码、低标注样本下的恶意/异常流量微调。

如果用于本项目，建议不要只复现分类准确率，而是抽取 `[CLS]` embedding 做聚类、离群检测、少样本新类识别和跨时间漂移评估；同时要把标签泄漏、会话切分、SNI/ECH 依赖作为实验设计的红线。

## 11. 代码对照分析

仓库复现说明集中在 [README.md](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\README.md:69>) 和 [data_process/README.md](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\README.md:4>)。

- 预训练 BURST 语料：核心是 [dataset_generation.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\dataset_generation.py:462>) 的 `pretrain_dataset_generation`、[get_burst_feature](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\dataset_generation.py:88>) 和 [bigram_generation](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\dataset_generation.py:70>)。
- 词表：`vocab_process/main.py` 中 [build_BPE](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\vocab_process\main.py:104>) 和 [build_vocab](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\vocab_process\main.py:133>) 对应论文 bigram/WordPiece 词表。本地 `encryptd_vocab.txt` 约 60005 行，论文的 65536 更像 bigram 取值上限。
- 预训练样本构造：`preprocess.py` 调用 UER 数据构造；[BertDataset](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\uer\utils\data.py:272>) 生成 `[CLS] A [SEP] B [SEP]`，`mask_seq` 在 [data.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\uer\utils\data.py:12>) 实现 15% mask。
- MBM/SBP 目标：实现复用 UER 的 BERT 目标，[BertTarget](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\uer\targets\bert_target.py:6>) 同时返回 MLM loss 和 NSP-like loss；训练器在 [trainer.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\uer\trainer.py:164>) 中处理。注意源码里 loss 是 `loss_mlm/10 + loss_sp`，与论文公式 `L_MBM + L_SBP` 表述不完全一致。
- 微调数据：`data_process/main.py` 设置 120 类、packet 数据路径、样本数和 `dataset_level`，见 [main.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\main.py:24>)；flow/packet 特征分别在 [get_feature_flow](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\dataset_generation.py:154>) 和 [get_feature_packet](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\data_process\dataset_generation.py:137>)。
- 分类器：微调入口是 [run_classifier.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\fine-tuning\run_classifier.py:21>)，分类头默认取 `[CLS]`，位置在 [run_classifier.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\fine-tuning\run_classifier.py:53>)。
- 推理：入口是 [run_classifier_infer.py](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\inference\run_classifier_infer.py:67>)。但本地推理脚本 [第 20 行](<F:\泉城实验室\二期\论文\异常检测\source\ET-BERT\inference\run_classifier_infer.py:20>) 直接 `from run_classifier import Classifier`，而文件实际在 `fine-tuning` 目录，按 README 从根目录运行时可能需要调整导入路径。

## 12. 本篇精华

- ET-BERT 的核心贡献是把加密流量分类从“有监督特征学习”推进到“无标签流量表征预训练”。
- BURST 是方法成败的关键，它把纯字节序列变成带有请求/响应方向和应用层加载结构的信息片段。
- MBM 捕捉密文字节上下文，SBP 捕捉传输片段同源关系，二者消融都显著掉点。
- 论文的强结果不只来自模型大，而来自预训练数据、BURST 输入结构和任务设计的组合。
- TLS 1.3 上 10% 级提升说明新加密协议下仍有可学习侧信道式模式，但这也意味着隐私与安全边界值得讨论。
- 代码实现主要是 UER-py 的 BERT 框架加交通语料构造，复现重点应放在 PCAP 清洗、切分、去头部和无泄漏划分。
- 对异常检测项目最有价值的是 ET-BERT embedding，而不仅是论文中的 closed-set 分类头。

## 13. 建议精读路线

先读 Introduction 和 Related Work，明确它批评 DPI、统计特征、监督深度模型的逻辑。第二步精读 Section 3.2 和 3.3，把 BURST、bigram token、MBM、SBP 画成自己的流程图。第三步看 Table 1、Table 2、Table 3，理解不同任务为什么难度不同。第四步重点看 Table 4 消融，这是判断创新是否有效的核心证据。最后读 Discussion，并对照代码中的 `data_process/`、`uer/utils/data.py`、`uer/targets/bert_target.py`、`fine-tuning/run_classifier.py`，确认论文概念如何落到工程实现。