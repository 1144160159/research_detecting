# [566] TrafficFormer: An Efficient Pre-trained Model for Traffic Data

## 1. 基本信息

- 题名：TrafficFormer: An Efficient Pre-trained Model for Traffic Data
- 中文题名：TrafficFormer：一种面向网络流量数据的高效预训练模型
- 年份/来源：2025 IEEE Symposium on Security and Privacy (S&P)
- DOI：10.1109/sp61157.2025.00102
- 论文主题：网络流量自监督预训练、加密流量分类、协议交互理解、少标签场景迁移学习
- 相关性判断：对异常检测“中高相关”。它不是直接做通用异常检测，而是提供可迁移的流量表示学习方法，对恶意流量检测、少标签入侵/异常分类、协议行为建模有直接借鉴价值。
- 正文包状态：本次正文包未截断。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：网络流量数据蕴含协议交互逻辑和实体行为模式，但标注成本高、标注数据少，导致传统深度流量分类模型在真实场景中泛化受限。TrafficFormer 借鉴 BERT 式预训练，但没有简单套用 NLP 任务，而是把流量的“包方向、包顺序、同一流归属、头部随机字段冗余”作为设计中心。

方法上，论文把流量切成 flow 和 burst，将包字节转为 bigram，再用 BPE/WordPiece 构造词表。预训练阶段包含 MBM 和 SODF 两个任务：MBM 预测被 mask 的 burst token，SODF 用五分类任务迫使模型区分同 burst 正序/乱序、同 flow 相邻 burst 正序/乱序、不同 flow 拼接。微调阶段提出 RIFA，通过随机替换 IPID、端口、TCP seq/ack、timestamp、TLS random 等随机初始化字段，保留语义但削弱捷径特征。

实验表明，TrafficFormer 在多个流量分类任务上整体优于 ET-BERT、YaTC 以及传统 ML/DL 方法；更重要的是，论文提出了协议理解任务，用方向判断、丢包检测、乱序检测、包字段预测来衡量模型是否学到了协议交互逻辑，而不只是数据集标签相关性。

## 3. 论文解决的具体问题

第一，流量分类严重依赖标签，但网络流量标注不像图像/文本那样直观，尤其是恶意流量往往淹没在大规模背景流量中，且攻击模式变化快。论文要解决的是少标签条件下，如何利用大量未标注流量学习可迁移表示。

第二，已有流量预训练方法主要把流量“改造成”文本或图像，再套用 MLM、NSP、MIM。例如 ET-BERT 的 burst 级 NSP 类任务更像判断两段是否来自同一 burst，容易被 IP、IPID、序列号等相似字段 shortcut 解决，未充分学习方向和顺序。

第三，流量数据中存在大量结构化但无语义或弱语义字段。随机初始化字段的具体值通常不决定应用/恶意性，但模型可能记住这些值，导致过拟合采集环境。

第四，传统评估只看分类准确率，难以判断模型是否理解协议交互。TrafficFormer 试图把“协议理解能力”作为流量预训练模型的评价对象。

## 4. 创新点深度提炼

1. **SODF 把流量预训练从“句子关系判断”推进到“协议交互关系判断”**  
   SODF 五分类不是简单同源/不同源二分类，而是同时覆盖同 burst 内顺序、相邻 burst 方向关系、同 flow 归属和跨 flow 负例。它对应的不是 NLP 中句子连贯性，而是网络协议中包序、方向和会话一致性。

2. **MBM 保留序列上下文学习，但输入单位是 burst 而非自然语言句子**  
   MBM 学的是同方向连续包内部的 token 关系。论文的判断是：流量像语言一样有序列性，但包乱序的后果比词乱序更严重，因此仅靠 MLM 不够，必须补充方向/顺序任务。

3. **RIFA 是基于协议知识的数据增强，而不是通用扰动**  
   它不是在特征空间做 SMOTE/GAN，也不是随便擦除字节，而是只改随机初始化字段，并保持 seq/ack/IPID 等后续变化模式。这一点很关键：它削弱具体随机值，同时保留协议状态转移。

4. **引入协议理解任务作为预训练模型评价维度**  
   方向判断、丢包检测、乱序检测、字段预测比普通分类更接近“模型是否知道 TCP/IP 交互逻辑”。这对安全方向很有价值，因为异常检测往往关心行为逻辑偏离，而不仅是应用标签。

5. **用少量早期包实现快速判别**  
   TrafficFormer 微调主要使用每个 flow 前 5 个包。虽然这会牺牲某些依赖长流统计的任务，但适合在线检测、早期阻断和低延迟分类。

## 5. 科学问题与研究假设

- 科学问题 1：未标注流量中是否存在可被 Transformer 预训练捕捉的通用协议语义？
- 假设 1：包字节 token 的上下文预测能学习局部字段和载荷结构。
- 假设 2：方向、顺序、同一 flow 关系是流量区别于自然语言的核心结构，显式建模会提升迁移能力。
- 假设 3：随机初始化字段的具体值会诱导模型走捷径，随机化这些字段可提高泛化。
- 假设 4：如果模型真正学到协议交互逻辑，它应在丢包、乱序、字段预测等任务上优于只学表面模式的预训练模型。
- 假设 5：前几个包中包含足够的握手、方向、头部结构信息，可支持早期分类。

## 6. 科学方法与技术路线

TrafficFormer 的技术路线是“流量结构化切分 + 字节级词化 + BERT 编码器 + 交通专用自监督任务 + 协议知识增强”。

数据先按五元组切成 flow，再按连续同方向包切成 burst。每个包取以太网层之后 64 字节，转为十六进制字符串，再生成重叠 bigram，例如 `4504008bd0` 变为 `4504, 0400, 008b, 8bd0`。随后用 BPE/WordPiece 形成最大约 65K 的词表。

模型结构基本是 BERT-base 量级：hidden size 768，12 层 Transformer，12 heads，最大序列长度 512。输入 embedding 包含 token、position、segment 三部分。

预训练损失为多任务组合：MBM 负责 masked token 预测，SODF 负责五分类。论文设置 λ=0.1，代码中也对应 `loss_mlm/10 + loss_sp`。微调时加载预训练权重，再对应用指纹、服务识别、网站指纹、恶意流量检测等任务训练分类头。

## 7. 实验设计与实验步骤

1. **数据**：预训练使用 ISCX-NonVPN、CICMalAnal2017 正常软件流量、Browser 数据集，总量约 20GB、60 万余 flows。微调用 Cross-Platform Android/iOS、CSTNET-TLS1.3、ISCX-VPN Service/App、USTC-TFC。协议理解使用 CSTNET-TLS1.3 和 CICMalAnal2017 的非重叠 benign 数据。

2. **预处理**：用 SplitCap 按 flow/session 切分；过滤小于 2KB 或少于 3 个包的 flow；少于 10 条 flow 的类别删除；超过 500 条的类别下采样。预训练数据进一步切 burst，包字节转 bigram，再构造词表和 `dataset.pt`。

3. **模型/基线**：TrafficFormer 与 ET-BERT、YaTC 比较；传统/深度基线包括 Appscanner、BIND、DeepFP、GraphDapp。ML/DL 基线可用全 flow，预训练方法主要用前 5 个包，这一点影响 ISCX-VPN(App) 的结果解释。

4. **训练**：预训练 batch size 64，3 张 A100，有效 batch 192；Adam，学习率 2e-5，linear decay，warm-up 0.1；总步数 500K，但 loss 在约 120K 稳定，选 120K checkpoint。微调通常训练 20 轮；TrafficFormer w/ EA 因增强 5 倍，为保持训练量改为 4 轮。

5. **指标**：分类任务报告 accuracy、macro precision、macro recall、macro F1。协议理解前三项报告 F1，字段预测报告准确率。

6. **消融/敏感性**：无预训练、不同预训练步数、不同增强倍数、不同输入字节范围与包数量、bigram vs gram、`[CLS]`/max/mean pooling。

7. **结果核查**：需要分别看裸 TrafficFormer 和 TrafficFormer w/ EA。部分表中最佳结果来自增强版本；裸模型并非每个数据集都压过所有基线。

## 8. 关键结果、结论与证据

流量分类上，RIFA 增强后的 TrafficFormer 整体最强。Cross-Platform Android 的 F1 从 ET-BERT 的 0.5162 提升到 TrafficFormer w/ EA 的 0.6167；iOS 从 0.3680 提升到 0.4689，说明在类别多、应用共享第三方域名的困难场景下，预训练和增强都有效。

CSTNET-TLS1.3 中，裸 TrafficFormer F1 为 0.8014，低于 YaTC 的 0.8133，但 w/ EA 达到 0.8338，说明该数据集上增强贡献很大。ISCX-VPN(Service) 中 w/ EA F1 为 0.9580，高于 ET-BERT 的 0.9454。USTC-TFC 恶意流量检测中，TrafficFormer w/ EA F1 为 0.9830，高于 ET-BERT 的 0.9727。

ISCX-VPN(App) 是一个重要例外：使用全流量时 GraphDapp 的 F1 最高，为 0.7419，TrafficFormer w/ EA 为 0.7129。但若限制传统/DL 方法也只用前 5 个包，它们明显低于预训练方法。这说明 TrafficFormer 更适合早期判别，而不一定在所有长流量统计任务上压倒全流图模型。

协议理解任务更支持论文主张。TrafficFormer 在方向判断几乎满分；在 CSTNET 的丢包检测和乱序检测上分别达到 0.8923 和 0.8837，优于 ET-BERT 和 YaTC；字段预测在 CSTNET 上达到 0.8361，比 ET-BERT 高约 5.14 个百分点。CIC 字段预测中 YaTC 略高于 TrafficFormer，这是论文结果中的例外，不能忽略。

消融显示预训练非常关键：无预训练时 ISCX-VPN(Service) F1 下降 85.17 个百分点，ISCX-VPN(App) 下降 66.05 个百分点。增强倍数也有收益，但存在饱和；输入内容实验显示 14-38 字节区间很关键，说明 IP/TCP 头部信息不是简单噪声。

## 9. 局限性与待解决问题

论文自身承认三类限制：第一，Transformer 输入长度有限，长 flow 会带来显存和注意力分散问题；第二，只用原始包字节，未显式使用包间隔、速率等时间特征，对 DDoS、扫描等依赖时序统计的异常检测可能不足；第三，当前是单 flow 检测，多 flow 场景如网页访问、横向移动、多连接攻击还需建模跨流关系。

从实验设计看，协议理解任务多是合成扰动任务，能测试模型是否感知局部协议逻辑，但还不能完全代表真实网络中的丢包、重传、NAT、代理、TLS 版本差异和流量混合。分类数据也主要来自公开数据集，真实部署中的开放集、新应用、新恶意家族和采集环境漂移仍未充分解决。

从代码复现看，仓库有明显工程化缺口：多处硬编码 `/mnt/data/zgm/ET-BERT/...` 临时目录；依赖外部 `SplitCap.exe`、`mono`、`editcap`；部分路径清理使用 Linux 命令；`dataset_extract` 依赖未在函数内定义的 `_category`；`vocab_gen.py` 使用 `tokenizers` 但 `requirements.txt` 未列出。代码默认还主要处理 IPv4，IPv6 分支不完整。

## 10. 与本项目的关系

如果本项目关注异常检测，TrafficFormer 的价值不在于直接给出一个异常分数，而在于提供“少标签流量表征”的基础组件。它适合用于恶意流量分类、攻击家族识别、未知异常前的表示预训练、以及协议状态偏离检测。

对异常检测尤其值得借鉴的是 SODF 和协议理解评估。异常流量常常表现为方向、顺序、状态转移或字段演化异常，而不仅是 payload 内容异常。可以把 SODF 式任务扩展为 TCP 状态机一致性、DNS 查询-响应匹配、TLS 握手阶段一致性等自监督任务。

已有粗分类“图学习、知识图谱与威胁情报”并不准确。本文主轴更接近“加密流量表示学习 / 网络流量基础模型 / 自监督异常检测前置表征”。GraphDapp 只是基线，不是本文方法核心。

## 11. 代码对照分析

| 论文环节 | 对应代码 | 阅读后的判断 |
|---|---|---|
| 依赖环境 | `source/TrafficFormer/requirements.txt` | 包含 PyTorch 2.0.1、scapy、flowcontainer、sklearn 等；缺少 `tokenizers`，但 `vocab_gen.py` 需要它。 |
| 预训练语料生成 | `data_generation/pretrain_data_gen.py`、`data_generation/utils.py` | `pretrain_dataset_generation` 完成 pcapng 转 pcap、SplitCap 切流、burst 生成；`get_bursts` 按方向切 burst；`bigram_generation` 生成重叠 bigram。 |
| 词表生成 | `data_generation/vocab_gen.py` | `build_BPE` 用 WordPiece 训练约 65K 词表，`build_vocab` 加入 `[PAD] [SEP] [CLS] [UNK] [MASK]`。 |
| 预训练输入构造 | `pre-training/preprocess.py`、`uer/utils/data.py` | `--target bertflow` 会使用 `BertFlowDataset`；`mask_seq` 实现 15% mask 和 BERT 式 80/10/10 替换策略。 |
| SODF 实现 | `uer/utils/data.py`、`uer/targets/bertflow_target.py` | 代码中称为 MSP，分类头输出 5 类；`create_ins_from_doc` 构造同 burst 正/反序、跨 flow、同 flow 相邻 burst 正/反序样本。 |
| 损失函数 | `uer/trainer.py` | `loss = loss_mlm/10 + loss_sp`，与论文 λ=0.1 一致。 |
| 模型结构 | `models/bert/base_config.json`、`uer/model_builder.py`、`uer/models/model.py` | BERT-base 量级：768 hidden、12 层、12 heads、512 长度；embedding/encoder/target 组合式构建。 |
| 微调数据生成与 RIFA | `data_generation/finetuning_data_gen.py` | `random_ip_port`、`random_tcp_ts_option`、`random_tls_randomtime` 在生成数据时随机化字段；`enhance_based_tsv` 在 TSV 层面对 IPID、IP、端口、seq/ack 做增强，并保持差分模式。 |
| 分类微调 | `fine-tuning/run_classifier.py` | 加载预训练权重 `strict=False`，默认用 `[CLS]`/first pooling，NLLLoss 分类，输出 macro/micro/weighted 指标。 |
| 字段预测任务 | `fine-tuning/run_mlm.py` | 针对最后一个包 mask IPID、IP、端口、seq、ack、TCP header length、flags 等字段；方向字段随机保留一个用于提示方向。 |
| 复现实验注意点 | README 与源码 | README 给出预训练、微调命令；但临时目录、外部工具、IPv6、`[SEP]` 文本分隔与 tokenizer 默认行为都需要复核和修补。 |

一个值得注意的细节：论文说微调阶段包 token 直接拼接、不插入 `[SEP]`；仓库默认 `get_feature_flow(add_sep=True)` 会在每个包前写入文本 `[SEP]`。若按 README 默认 `BertTokenizer` 运行，需确认实际是否改用 `--tokenizer space` 或修改 tokenizer，否则该分隔符可能不会作为真正 special token 处理。

## 12. 本篇精华

- TrafficFormer 的核心不是“把流量喂给 BERT”，而是用 SODF 把包方向、顺序和 flow 归属变成自监督信号。
- RIFA 的价值在于区分“随机初始化字段的具体值”和“字段变化模式”，前者应弱化，后者应保留。
- 协议理解任务是本文最值得借鉴的评价创新，比单纯分类指标更接近安全检测中的行为逻辑建模。
- 预训练在小样本流量任务上收益巨大，尤其 ISCX-VPN 这类样本少的数据集，无预训练几乎学不起来。
- 早期包分类是 TrafficFormer 的强项，但面对需要长流统计的任务，全流图模型仍可能更强。
- 实验结果要区分裸 TrafficFormer 与 TrafficFormer w/ EA；部分数据集的最佳性能主要来自增强版本。
- 对异常检测项目，可把 SODF 扩展为协议状态一致性、跨流关系一致性、时间间隔异常等自监督任务。

## 13. 建议精读路线

1. 先读 Introduction 和 Table 1，明确它相对 PERT、ET-BERT、YaTC 的差别不是表示形式，而是预训练任务和微调增强。
2. 精读 3.2，尤其是 SODF 五类样本构造，画出每类对应的协议含义。
3. 精读 3.3，把 RIFA 中每个字段为什么可随机化、如何保持语义写成自己的表。
4. 读 4.2 时重点看例外：CSTNET 裸模型不总是最优，ISCX-VPN(App) 全流 GraphDapp F1 更高。
5. 精读 4.3，把四个协议理解任务改写成本项目可复用的异常检测任务。
6. 用 4.4 的消融判断哪些设计真正关键：预训练、增强、输入字节范围、pooling。
7. 读代码时按 `data_generation` → `uer/utils/data.py` → `uer/targets/bertflow_target.py` → `uer/trainer.py` → `fine-tuning` 的顺序走，先理解数据如何变成五分类样本，再看模型。