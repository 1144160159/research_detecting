# [164] A Survey on Time-Series Pre-Trained Models

## 1. 基本信息

- 论文：A Survey on Time-Series Pre-Trained Models
- 作者：Qianli Ma 等
- 年份：2024
- 来源：IEEE Transactions on Knowledge and Data Engineering, Vol. 36, No. 12
- DOI：10.1109/TKDE.2024.3475809
- 类型：综述论文，带大规模统一实验
- 主题：时间序列预训练模型、迁移学习、自监督学习、Transformer、异常检测
- 与本项目相关性：弱相关但有方法论价值。它不是网络安全异常检测专文，但系统总结了时间序列预训练、表示学习和异常检测评测，对跨域异常检测、工业监测、KPI/流量序列异常检测有参考意义。
- 正文完整性：本次正文包未截断。
- 代码状态：本地未发现该论文对应代码包。论文正文声明作者开源了实验代码和数据，但本次材料未提供本地源码目录。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：在时间序列挖掘任务中，深度模型依赖大量标注数据，而现实中标注昂贵、跨域分布差异大，能否像 NLP/CV 一样通过预训练模型缓解数据稀缺并提升下游泛化？

论文把 Time-Series Pre-Trained Models，简称 TS-PTMs，整理为三大类：

- 监督式预训练：用分类或预测任务作为预训练目标。
- 无监督预训练：主要用重构、去噪重构、mask-and-predict。
- 自监督预训练：主要用一致性学习、对比学习、伪标签学习。

这篇综述不是单纯罗列模型，而是做了统一实验：27 种方法、434 个数据集、679 组迁移学习场景，覆盖分类、预测、异常检测三类任务。它得到的总体判断是：传统迁移学习在小型 UCR 数据集上不稳定，容易出现负迁移；patch 化处理、Transformer 架构、LLM 微调和一致性预训练在不同任务上显示出更强潜力；异常检测方向尤其值得关注 patch-based contrastive/Transformer 方法，但评价指标变化后，TS-PTM 并没有全面压倒传统方法。

## 3. 论文解决的具体问题

论文要解决的不是某一个单点算法问题，而是时间序列预训练研究中的几个结构性问题。

第一，时间序列缺乏像 ImageNet 或大语料库那样统一、规模巨大、语义相对稳定的预训练数据。时间序列片段不像词语那样有跨场景共享语义，同一形状在医疗、电力、金融、网络流量中可能含义完全不同。

第二，时间序列预训练目标尚未统一。分类、预测、重构、对比学习、伪标签、LLM 重编程都能用，但哪类目标更适合下游任务并不清楚。

第三，时间序列迁移学习存在明显负迁移风险。源域和目标域相似时可能受益，不相似时预训练会损害性能。

第四，已有综述多偏向表示学习分类，而缺少在统一预处理、统一环境、统一评价下对代表方法的横向实验。

第五，异常检测中的“进步幻觉”问题。传统 F1、Point Adjustment、affiliation、VUS 等指标可能给出不同排序，单一指标容易夸大方法优势。

## 4. 创新点深度提炼

论文的第一个创新是分类框架清晰。作者按预训练技术而不是按模型结构分类，把 TS-PTMs 分成监督、无监督、自监督三大路线，再细分为 classification-based、forecasting-based、reconstruction-based、consistency-based、pseudo-labeling-based。这比简单按 CNN/RNN/Transformer 分类更贴近预训练问题本质。

第二个创新是把早期迁移学习、领域适配、模型重编程、LLM 时间序列化放在同一脉络下讨论。比如 Voice2Series 和 Time-LLM 都被理解为通过输入重编程和标签/语义映射，把外部大模型知识迁移到时间序列任务。

第三个创新是实验规模较大。分类部分使用 UCR/UEA 和独立场景数据集；预测部分比较 TS2Vec、CoST、GPT4TS、TEMPO、Informer、Autoformer、PatchTST、iTransformer、DLinear、TimesNet 等；异常检测部分比较 TS2Vec、TimesNet、GPT4TS、DCdetector、SPOT、DSPOT、LSTM-VAE、DONUT、SR、Anomaly Transformer。

第四个创新是把“patch 策略”提升为未来重点。论文反复指出，在预测和异常检测中，将时间序列切成 patch 再送入 Transformer 或 LLM，是当前最有前景的技术路线之一。

第五个创新是对未来方向的判断较务实。作者没有简单宣称“大模型统治时间序列”，而是指出 LLM 直接用于时间序列仍有争议，时间序列专用大规模预训练数据和专用预训练范式仍可能是主路线。

## 5. 科学问题与研究假设

核心科学问题可以概括为：时间序列是否存在可跨任务、跨数据集、跨领域迁移的通用表征？如果存在，应当通过什么预训练任务、模型结构和数据组织方式获得？

论文隐含了几组研究假设。

第一，预训练可以提供比随机初始化更好的模型起点，尤其在目标数据稀缺时能提升泛化。

第二，时间序列的内在属性，包括时间依赖、多尺度结构、频域结构、趋势/季节性、变量间关系，是设计 TS-PTMs 的关键。

第三，源域和目标域相似性决定迁移学习成败。简单“多数据预训练”不一定可靠，负迁移是时间序列预训练必须面对的问题。

第四，自监督一致性目标可以缓解标注稀缺，因为它从同一样本的不同视图、不同时间片、不同上下文中构造监督信号。

第五，patch 化可以降低长序列建模难度，并让 Transformer/LLM 更容易处理时间序列。

## 6. 科学方法与技术路线

论文的技术路线是“综述分类 + 统一实验 + 未来问题归纳”。

监督式路线中，classification-based PTMs 用有标签源数据训练分类编码器，再迁移到目标任务。典型形式包括 universal encoder、aligned encoder、model reprogramming。universal encoder 试图学习通用时间序列表征；aligned encoder 用 MMD、对抗训练、因果结构对齐等方法缓解源目标分布差异；model reprogramming 则把语音模型或语言模型改造成时间序列模型。

forecasting-based PTMs 把未来值预测作为天然监督信号。RNN、TCN、Transformer、GNN 都可以作为预测骨干。该路线的关键是利用时间依赖和动态规律，但递归预测有误差累积风险，Transformer 一次性输出多步预测更受关注。

无监督路线以重构为中心。AutoEncoder、Denoising AutoEncoder、Transformer encoder 的 mask-and-predict 都属于这一类。其逻辑是：如果模型能从扰动或缺失输入恢复原始时间序列，就会学习到有用表征。

自监督路线以一致性和伪标签为中心。对比学习中，正负样本构造是关键。论文区分了 subseries consistency、temporal consistency、transformation consistency、contextual consistency。TS2Vec 属于 contextual consistency 的代表，DCdetector 则在异常检测中体现了 patch + contrastive 的潜力。

## 7. 实验设计与实验步骤

可复核流程如下。

数据：

- 分类：UCR 单变量分类数据集、UEA 多变量分类数据集，以及 4 个独立时间序列场景数据集。
- 预测：9 个公开多变量预测数据集，包括 ETT、Electricity、Weather、ILI 等。
- 异常检测：Yahoo、KPI、UCR anomaly detection archive，以及 7 个多变量异常检测数据集。

预处理：

- UCR/UEA 原始数据没有固定验证集，作者将训练集和测试集合并后重新划分。
- 分类任务使用五折交叉验证，并按 60%/20%/20% 划分训练、验证、测试。
- 预测任务按已有工作 TS2Vec、TimesNet 的标准预处理方式处理。
- 异常检测任务按序列片段 `[x1, ..., xt]` 判断最后一个点 `xt` 是否异常。

模型/基线：

- 分类：FCN、TimesNet、TST、T-Loss、SelfTime、TS-TCC、TS2Vec、PatchTST、GPT4TS。
- 迁移学习：监督分类迁移、无监督 RNN decoder 重构迁移、无监督 FCN decoder 重构迁移。
- 预测：TS2Vec、CoST、GPT4TS、TEMPO、LogTrans、Informer、Autoformer、PatchTST、iTransformer、DLinear、TCN、TimesNet。
- 异常检测：TS2Vec、TimesNet、GPT4TS、DCdetector、SPOT、DSPOT、LSTM-VAE、DONUT、SR、Anomaly Transformer。

训练：

- 迁移学习先在源数据集预训练，再在目标数据集微调。
- 自监督方法先通过重构或对比目标学习表征，再接下游头或微调。
- GPT4TS 采用 patch 策略并微调预训练语言模型的部分参数。
- 异常检测中模型输出异常分数，再根据阈值或评价协议判断异常点。

指标：

- 分类：平均测试准确率、平均排名、显著性检验 P-value。
- 预测：MSE 和 MAE。
- 异常检测：F1、Precision、Recall、F1-PA%K、affiliation precision/recall、VUS 等。

消融/敏感性：

- 论文重点比较预训练策略差异，而不是单个模型内部消融。
- 迁移实验实际上检验了源数据规模、源目标相似性、监督/无监督预训练目标对迁移效果的影响。
- 异常检测部分通过多评价指标揭示不同指标对方法排序的敏感性。

结果核查：

- 检查是否存在负迁移，尤其是 UCR 小数据集迁移。
- 检查不同指标下异常检测排名是否一致。
- 检查 patch-based 方法是否在预测和异常检测上稳定占优。
- 检查 LLM-based 方法是否真的优于从头训练或普通 Transformer，而不是只因 patch 和注意力结构受益。

## 8. 关键结果、结论与证据

分类任务中，传统迁移学习在 UCR 小数据集上表现不稳定，正迁移数量并不理想。监督分类迁移整体强于无监督重构迁移，但在最小目标数据集上，带对称 FCN decoder 的无监督重构迁移有时并不显著弱于监督迁移。

在 4 个独立大场景数据集上，迁移学习比 UCR 上更有效。这支持一个判断：时间序列预训练需要足够大的源数据，UCR 这类小型数据集很难支撑稳定预训练。

分类横向比较中，UCR 上 TS2Vec 和 GPT4TS 表现最好；UEA 上 GPT4TS 最好，FCN 直接监督训练也很强，PatchTST 优于 TS2Vec。这说明多变量时间序列中 patch + Transformer 的优势更明显，而普通自监督表征并非总是占优。

预测任务中，iTransformer 和 GPT4TS 整体表现突出。CoST 在 Weather 和 ILI 上表现好，说明显式建模趋势与季节性仍很重要。论文据此认为，patch 化、Transformer、LLM 微调是时间序列预测预训练的重要方向。

异常检测中，传统 F1/P/R 下 TS2Vec 和 Anomaly Transformer 表现较强；但在更严格或更新的指标上，DONUT、DCdetector 等方法表现会改变排序。UCR anomaly archive 上 DCdetector 在综合指标上较强，多变量异常检测中 DCdetector 在多数数据集领先。论文最终判断：异常检测中 patch + contrastive + Transformer 是值得继续探索的路线，但 TS-PTMs 尚未全面替代传统异常检测方法。

## 9. 局限性与待解决问题

第一，时间序列大规模通用预训练数据仍缺失。没有类似 ImageNet 或通用文本语料的基础设施，导致 TS-PTM 难以形成统一预训练范式。

第二，跨域语义不稳定。一个时间片、一个形状模式或一个频率成分在不同领域中含义不同，这让“通用表征”比 NLP 中的词向量更难。

第三，迁移学习有明显负迁移风险。源目标数据不相似时，预训练模型可能反而降低性能。

第四，异常检测评价仍不稳定。不同指标对连续异常、点异常、检测延迟和异常区间覆盖的偏好不同，单看 F1 或 PA 容易得出片面结论。

第五，LLM 用于时间序列的机制仍不清楚。GPT4TS 等方法有效，但效果可能来自 patch、注意力结构、优化技巧，而不一定来自语言预训练知识本身。

第六，网络安全场景尚未被充分覆盖。论文异常检测数据更多是 Yahoo、KPI、UCR archive 和通用多变量数据，对真实网络流量、主机日志、攻击链、多源安全事件的讨论不足。

第七，鲁棒性方向刚起步。论文提出对抗攻击、噪声标签是未来方向，但没有展开统一实验。对于安全异常检测，这恰恰是关键问题。

## 10. 与本项目的关系

本项目关注网络安全与异常检测，这篇论文的直接相关性不强，因为它不是面向入侵检测、恶意流量检测或安全日志分析的专门论文。但它提供了三类有价值参考。

第一，方法范式参考。安全时序数据同样存在标注昂贵、攻击样本稀缺、环境漂移、跨域迁移困难等问题，TS-PTM 的预训练/微调框架可以用于流量序列、KPI 序列、主机行为序列。

第二，异常检测评测参考。论文强调不能只看传统 F1，需要结合 Point Adjustment、affiliation、VUS 等指标。这对安全异常检测尤其重要，因为攻击往往是区间事件而非孤立点。

第三，模型选择参考。对于多变量安全遥测数据，patch-based Transformer、DCdetector 类对比学习、TS2Vec 类上下文一致性表征，比简单 RNN/AE 更值得作为基线。

但要谨慎：网络安全数据有强对抗性、概念漂移、弱标签、告警延迟、攻击阶段依赖等特点，不能直接把通用时间序列结论平移过来。

## 11. 代码对照分析

本次材料说明“未发现该论文对应的本地开源代码”，因此无法做本地源码级逐文件对应。论文正文中提到作者开源了代码和数据，仓库地址为 `https://github.com/qianlima-lab/time-series-ptms`，但该代码未包含在本次代码包中。

基于论文实验设计，若后续拿到官方仓库，建议重点查找以下模块：

- 数据预处理：应对应 UCR/UEA 合并重划分、五折交叉验证、预测数据标准化、异常检测滑窗构造。
- 模型目录：应包含 FCN、TST、TS2Vec、PatchTST、GPT4TS、TimesNet、CoST、DCdetector 等实现或封装。
- 训练脚本：应区分 classification、forecasting、anomaly detection 三类入口。
- 迁移学习脚本：应包含源数据预训练、目标数据微调、正/负迁移统计。
- 评价脚本：分类 accuracy/rank/P-value，预测 MSE/MAE，异常检测 F1、PA、affiliation、VUS。
- 配置文件：应记录 27 种方法、434 个数据集、679 组迁移场景的实验参数。

对本项目来说，若复现实验，最值得优先运行的不是全部 27 个方法，而是异常检测相关的 TS2Vec、DCdetector、GPT4TS/patch-based Transformer、DONUT 传统基线，并统一评价指标。

## 12. 本篇精华

- 时间序列预训练的根本难点不是模型不够大，而是缺少跨领域语义稳定的大规模预训练数据。
- 传统迁移学习在 UCR 这类小数据集上不稳定，源目标相似性决定正迁移还是负迁移。
- patch 策略是贯穿分类、预测、异常检测的关键技术，它让 Transformer/LLM 更适合处理长时间序列。
- TS2Vec 证明上下文一致性自监督可以学习通用时间序列表征，但在多变量任务上不一定优于 patch-based Transformer。
- GPT4TS 等 LLM 方法表现强，但其优势来源仍需拆解，不能简单归因于语言知识迁移。
- 异常检测不能只看传统 F1，指标变化会显著改变模型排序。
- DCdetector 在异常检测中显示出 patch + contrastive + Transformer 的潜力，是安全时序异常检测可重点借鉴的路线。
- 未来关键问题包括大规模时间序列数据集、对抗鲁棒性、噪声标签、跨域迁移、时间序列与文本的多模态预训练。

## 13. 建议精读路线

建议先读 Introduction 和 Background，抓住作者为什么认为时间序列需要预训练模型：标注稀缺、表示学习困难、迁移学习可缓解数据不足。

第二步读 Section III 的 taxonomy。重点画出监督、无监督、自监督三条路线，并把 universal encoder、aligned encoder、model reprogramming、mask-and-predict、contrastive learning 对应起来。

第三步精读实验部分。分类看 Table I-III，预测看 Table IV，异常检测看 Table V-VI。不要只看最优数值，要关注作者如何解释负迁移、patch 策略和评价指标差异。

第四步重点读 Future Directions。对本项目最有用的是 large-scale datasets、inherent properties、adversarial attacks、noisy labels、LLM for time series。

第五步若后续拿到代码，优先复现异常检测部分，再迁移到网络流量/KPI/主机日志数据，观察 patch-based 和 consistency-based 方法在安全场景中的鲁棒性。

<!-- codex-cli-deep-read: complete -->
