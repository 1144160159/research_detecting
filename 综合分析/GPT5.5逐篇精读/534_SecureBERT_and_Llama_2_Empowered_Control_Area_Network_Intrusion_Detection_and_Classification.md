# [534] SecureBERT and Llama 2 Empowered Control Area Network Intrusion Detection and Classification

## 1. 基本信息

- 题名：SecureBERT and Llama 2 Empowered Control Area Network Intrusion Detection and Classification
- 作者：Xuemei Li, Huirong Fu
- 年份：2025
- 来源：IEEE Transactions on Intelligent Transportation Systems, Vol. 26, No. 10
- DOI：10.1109/TITS.2025.3596915
- 研究对象：车载 CAN 总线入侵检测与攻击分类
- 方法类型：预训练 Transformer 微调，包括 BERT、SecureBERT、Llama 2
- 本地代码状态：未发现该论文对应的本地开源代码包
- 正文完整性：本次正文包未截断，基于完整正文缓存进行理解

## 2. 中文翻译与核心摘要

这篇论文研究的是：能否把面向自然语言或网络安全文本预训练的大模型，直接迁移到车载 CAN 报文入侵检测任务中，用原始 CAN 日志文本完成攻击检测和攻击类型分类。

作者提出三个模型：

- CAN-C-BERT：基于通用 BERT base，加分类头。
- CAN-SecureBERT：基于网络安全语料预训练的 SecureBERT，加分类头。
- CAN-LLAMA2：基于 Llama 2 7B，通过 LoRA 参数高效微调，加分类头。

论文的核心结论是：CAN 报文虽然不是自然语言，但其字段序列、十六进制值、ID、DLC、时间戳等具有可学习的“结构化语义”。预训练 Transformer 经过少量监督微调后，可以直接从 CAN 日志中学习攻击模式，不必依赖复杂特征工程。

最佳模型 CAN-LLAMA2 在 Car Hacking Dataset 上达到 BA、Precision、Detection Rate、F1 均为 0.999993，FAR 为 3.10e-6。作者强调这个误报率比 MTH-IDS 低约 52 倍。论文还发现，SecureBERT 相比普通 BERT 的提升并不显著，说明“网络安全领域预训练知识”不一定直接转化为 CAN 入侵检测能力；模型容量和结构复杂度可能更关键。

## 3. 论文解决的具体问题

论文针对的是车载 CAN 网络中的入侵检测与攻击分类问题。CAN 总线缺少内建认证和加密机制，ECU 之间通过广播方式通信，攻击者一旦接入车内网络，就可能注入高优先级报文、伪造 RPM/Gear 信息或随机 fuzz 报文。

传统 CAN IDS 存在几个问题：

- 依赖物理层特征，如电压指纹、时钟偏移，部署成本高。
- 依赖人工特征工程，如报文频率、熵、时间间隔、Hamming distance。
- 多数方法只能做异常检测，不能细粒度区分 DoS、Fuzzy、RPM spoofing、Gear spoofing。
- 很多模型需要大量训练数据，而真实车辆攻击数据采集困难。
- IDS 在车端部署时资源受限，云端/边缘协同检测架构仍需要高精度分类器。

这篇论文把问题重新表述为：给定一条 CAN message log，将其当成 token 序列输入预训练 Transformer，通过微调学习类别标签，实现多分类入侵检测。

## 4. 创新点深度提炼

第一，论文将 CAN 报文日志作为“类文本序列”处理，而不是先做人工特征抽取。字段如 Timestamp、CAN ID、DLC、DATA[0-7]、Flag 被视作模型可 token 化的输入序列。这个视角把 CAN IDS 从特征工程范式推进到预训练模型迁移范式。

第二，论文首次系统比较了通用语言模型、网络安全领域语言模型和大语言模型在 CAN 入侵检测上的适配效果。CAN-C-BERT、CAN-SecureBERT、CAN-LLAMA2 形成了从 110M、123M 到 7B 参数规模的梯度比较。

第三，CAN-LLAMA2 使用 LoRA 微调，只更新约 0.57% 参数，约 4000 万参数。这说明大模型可以在保留原有语言能力的同时，通过 adapter/LoRA 承载车载安全下游任务。论文把它设想为 VSOC 可复用的基础模型。

第四，论文关注了误报率 FAR，而不是只报告 accuracy。对车载安全运营而言，FAR 极低才有实际意义。作者用“每天 1000 万条 CAN 消息”的量级解释 FAR 的运营影响，这比单纯追求高准确率更贴近 IDS 场景。

第五，论文做了跨数据集验证。除了 Car Hacking Dataset，还在 can-train-and-test 数据集上验证不同 OEM、不同车型下的泛化能力，说明模型不是只在单一车辆数据上过拟合。

## 5. 科学问题与研究假设

核心科学问题可以概括为三个：

1. CAN 报文是否具有足够稳定的序列模式，使预训练 Transformer 能通过 token 表征学习攻击行为？
2. 网络安全语料预训练的 SecureBERT 是否比通用 BERT 更适合 CAN IDS？
3. 更大规模的 Llama 2 是否能在少量 CAN 监督样本下表现出更强泛化能力？

论文隐含的研究假设是：

- CAN 报文字段之间存在类似上下文依赖的关系，例如 CAN ID、DLC 和 DATA 字节组合可以反映正常或异常行为。
- 预训练模型虽然不是在 CAN 数据上训练的，但其注意力机制和序列建模能力可迁移到结构化日志。
- 大模型的容量、层数和预训练知识规模，有助于捕获 Fuzzy、DoS 等更复杂或更微妙的攻击模式。
- 经过平衡采样后，即使只使用 1%、5%、10% 的训练数据，也可以得到接近饱和的检测效果。

## 6. 科学方法与技术路线

论文技术路线如下：

1. 将 CAN message log 作为输入文本序列。
2. 分别使用 BERT tokenizer、SecureBERT tokenizer、Llama 2 tokenizer 进行 tokenization。
3. 使用预训练模型提取序列表征。
4. 对 BERT/SecureBERT，取 `[CLS]` token embedding 输入分类头。
5. 对 Llama 2，取最后 token 或 `[EOS]` embedding 输入分类头。
6. 分类头由全连接隐藏层、输出层和 softmax 组成。
7. 使用交叉熵损失进行多分类训练。
8. BERT 和 SecureBERT 全参数微调；Llama 2 用 4-bit 加载和 LoRA 微调。
9. 使用 AdamW 优化器，并通过 TPE 搜索部分超参数。
10. 使用 BA、Precision、Detection Rate、F1、FAR 评价模型。

方法上的关键在于：论文没有把 Transformer 当成普通深度分类器，而是利用预训练模型已有的序列表征能力，再用少量 CAN 标注样本把它“拉”到车载安全任务空间中。

## 7. 实验设计与实验步骤

可复核流程如下。

数据：

- Car Hacking Dataset：来自 Hyundai YF Sonata，通过 OBD-II 采集，包含 BENIGN、DoS、Fuzzy、RPM spoofing、Gear spoofing。
- can-train-and-test Dataset：来自 2 个 OEM、4 种车型，包括 2017 Subaru Forester、2016 Chevrolet Silverado、2011 Chevrolet Traverse、2011 Chevrolet Impala。标签格式被转换为与 Car Hacking Dataset 一致。

预处理：

- 保留 CAN 日志字段：Timestamp、CAN ID、DLC、DATA[0] 到 DATA[7]、Flag。
- 论文强调不做传统特征工程。
- 对训练子集进行预平衡采样：攻击样本取 1%、5%、10% 等比例，正常样本按更小比例抽取以缓解类别不平衡。
- Car Hacking Dataset 先按 70% 训练、30% 测试划分；训练部分再抽取子集，并划分训练/验证。

模型/基线：

- CAN-C-BERT：BERT base，约 110M 参数。
- CAN-SecureBERT：SecureBERT，约 123M 参数。
- CAN-LLAMA2：Llama 2 7B，32 个 decoder blocks，半精度/4-bit 加载，LoRA 微调。
- 对比基线包括 MTH-IDS 以及相关 CAN IDS 文献中的 CNN、GAN、LSTM autoencoder、SOM、timing-based 等方法。

训练：

- 三个模型均训练 10 epochs。
- CAN-C-BERT/CAN-SecureBERT：train batch size 4，eval batch size 32，learning rate 5e-5，weight decay 0.01。
- CAN-LLAMA2：train batch size 4，eval batch size 16，gradient accumulation 4，learning rate 3e-5，weight decay 0.01。
- LoRA 参数：r=16，alpha=64，dropout=0.1，bias=0。
- 优化器：AdamW。
- 超参数搜索：TPE Bayesian optimization，目标是降低训练和验证损失。

指标：

- Balanced Accuracy：应对类别不平衡。
- Precision：衡量报警可信度。
- Detection Rate/Recall：衡量攻击检出率。
- False Alarm Rate：衡量误报负担。
- F1：综合 Precision 与 Recall。
- Model parameter size、训练时间、推理速度：衡量部署代价。

消融/敏感性：

- 比较 1%、5%、10% 训练数据下的性能。
- 比较未微调直接加分类头的效果。
- 比较 BERT、SecureBERT、Llama 2 的模型容量和领域预训练影响。
- 比较 Car Hacking Dataset 与 can-train-and-test 上的泛化表现。
- 使用 SHAP 分析输入 token 对分类结果的贡献。

结果核查：

- 未微调模型基本随机预测，证明微调必要。
- 训练和验证 loss 在 10 epochs 内接近 0。
- 10% 数据训练优于 1% 和 5%，但增益逐渐减小。
- DoS、Gear spoofing、RPM spoofing 基本达到 100%。
- Fuzzy attack 仍是最容易出错的类型。
- CAN-LLAMA2 整体最好，CAN-SecureBERT 次之。

## 8. 关键结果、结论与证据

最重要的结果是 CAN-LLAMA2 在 10% 训练数据下达到 BA、Precision、Detection Rate、F1 均为 0.999993，FAR 为 3.10e-6。论文据此估算，如果每天处理 1000 万条 CAN 消息，误报约 31 条。相比 MTH-IDS，误报率降低约 52 倍。

第二个关键结果是 CAN-SecureBERT 表现接近 CAN-LLAMA2，并且推理速度明显优于 Llama 2。论文结论中称 SecureBERT 是性能第二、推理速度更好的折中方案。

第三个关键结果是模型使用更大训练比例时泛化更好。1% 数据已经可以取得很高性能，但 10% 数据的验证损失更低、指标更稳定。这说明少量样本可行，但更多数据仍有价值。

第四个关键结果是领域预训练并非决定性因素。SecureBERT 比普通 BERT 略好，但差异没有 Llama 2 相比 BERT/SecureBERT 那么明显。论文据此认为，模型架构复杂度和参数规模可能比“是否网络安全预训练”更重要。

第五个关键结果来自 SHAP 分析。模型判断正常报文时更多关注 DLC 和数据字段模式；判断 DoS 时 CAN ID 贡献很大；判断 Fuzzy 时 timestamp、CAN ID、DLC 和前几个数据字节重要；Gear/RPM spoofing 则集中依赖特定 data 字节。这说明模型不是完全黑箱地“记标签”，而是在利用报文字段组合特征。

## 9. 局限性与待解决问题

本次正文包未截断，因此不需要额外回 PDF 复核缺失部分。不过仍建议后续复核 PDF 中的表格数值和图中曲线，因为正文抽取可能不能完整保留表格排版细节。

论文自身局限主要有五点。

第一，计算资源开销很大。CAN-LLAMA2 训练 1% 数据就需要约 118 分钟，推理速度约比 BERT/SecureBERT 慢 8 倍。对于车端实时 IDS，这种模型很难直接部署。

第二，攻击类型仍较有限。主要围绕 DoS、Fuzzy、RPM spoofing、Gear spoofing。真实车载攻击可能包括重放、诊断服务滥用、低频 stealthy injection、跨 ECU 协同攻击等。

第三，Fuzzy attack 仍是弱点。三个模型在 DoS、Gear、RPM 上几乎完美，但 Fuzzy 报文仍出现少量误判。这类攻击随机性高，可能更依赖时序上下文而非单条报文模式。

第四，论文声称“不需要预处理”，但实际仍有格式统一、标签转换、采样平衡、tokenization 等步骤。它消除了人工特征工程，但不是完全无处理。

第五，鲁棒性尚未充分验证。作者在 future work 中明确提出要测试 input-level perturbation 和 protocol-level adversarial manipulation。这说明当前模型面对对抗扰动、规避攻击、分布漂移时的可靠性仍未证明。

## 10. 与本项目的关系

该论文与“异常检测/入侵检测与网络异常检测”方向强相关，尤其适合支撑以下研究线索：

- 将安全日志、网络流量、协议报文转化为 token 序列，用预训练模型做异常检测。
- 比较通用预训练、领域预训练、大模型 LoRA 微调在安全任务中的迁移能力。
- 探索少样本条件下的网络异常检测。
- 关注误报率 FAR 对安全运营的实际影响。
- 将车端轻量异常检测与云端/边缘大模型分类结合。

对本项目最有启发的是：异常检测不一定只依赖统计特征或时序模型，也可以把结构化协议日志看作“半结构化语言”，用 Transformer 学习字段之间的隐含关系。不过需要警惕的是，CAN 报文短、格式固定、攻击注入模式明显，论文中的近乎完美结果未必能直接迁移到更开放、更复杂的企业网络流量或主机日志场景。

## 11. 代码对照分析

本地状态显示未发现该论文对应的开源代码包，因此不能给出真实源码文件级对应关系。以下是根据论文方法推断的复现实装结构，用于后续寻找或自建代码时对照。

可能的数据预处理模块：

- `data_preprocess.py`
- `dataset.py`
- `can_dataset.py`

应负责读取 Car Hacking Dataset 和 can-train-and-test，统一字段格式，处理 BENIGN/DoS/Fuzzy/RPM/Gear 标签，完成 70/30 划分、1%/5%/10% 子集抽样和平衡采样。

可能的 tokenizer 与输入构造模块：

- `tokenization.py`
- `collator.py`

应负责把一条 CAN 报文拼接为文本序列，例如 timestamp、CAN ID、DLC、DATA 字节序列，再调用 BERT/SecureBERT/Llama 2 tokenizer 生成 `input_ids`、`attention_mask`。

可能的模型文件：

- `models/can_c_bert.py`
- `models/can_securebert.py`
- `models/can_llama2.py`

其中 BERT/SecureBERT 应使用 HuggingFace `AutoModel` 或 `AutoModelForSequenceClassification`；Llama 2 应使用 `AutoModelForSequenceClassification` 或自定义 `[EOS]` embedding 分类头，并结合 PEFT LoRA。

可能的训练脚本：

- `train_bert.py`
- `train_securebert.py`
- `train_llama2_lora.py`
- `train.py`

应包含 AdamW、cross entropy、10 epochs、batch size、learning rate、weight decay、gradient accumulation、4-bit quantization、LoRA 配置等。

可能的评估脚本：

- `evaluate.py`
- `metrics.py`

应计算 BA、Precision、Detection Rate/Recall、F1、FAR，并按攻击类型输出分类性能表。

可能的解释性分析脚本：

- `explain_shap.py`

应复现论文中的 SHAP token 贡献分析，输出单条 CAN message 的 token 贡献热力图和 top contributing tokens。

如果后续要复现，优先确认三个运行线索：HuggingFace 模型名、CAN 报文文本拼接格式、类别标签映射。论文性能极高，复现时这三处差异会显著影响结果。

## 12. 本篇精华

1. 论文把 CAN 入侵检测转化为“结构化日志文本分类”，用预训练 Transformer 直接处理原始 CAN message log，弱化传统特征工程。

2. CAN-LLAMA2 通过 LoRA 只更新约 0.57% 参数，却取得最佳性能，说明大模型可作为车载安全多任务基础模型。

3. SecureBERT 的领域预训练优势并不压倒普通 BERT，模型规模和结构复杂度可能比安全语料预训练更关键。

4. FAR 是本文最有实际意义的指标；CAN-LLAMA2 的 FAR 为 3.10e-6，对 VSOC 告警负担有直接解释价值。

5. 模型在 DoS、Gear spoofing、RPM spoofing 上几乎完美，Fuzzy attack 仍是最难分类的攻击类型。

6. 未微调的预训练模型无法直接识别 CAN 攻击，说明 Transformer 的迁移能力必须通过任务监督激活。

7. 论文提出了较现实的部署思路：车端部署轻量异常检测，云端或边缘部署大模型分类器。

8. 这篇文章适合在综述中归入“LLM/预训练模型赋能车载网络 IDS”类别，但部署代价和对抗鲁棒性仍是开放问题。

## 13. 建议精读路线

第一遍先读 Introduction 和 Contributions，抓住作者为什么认为传统 CAN IDS 受限，以及为什么选择 BERT、SecureBERT、Llama 2。

第二遍重点读 Model Architecture 和 Fine-Tuning Process，弄清 `[CLS]` 与 `[EOS]` 分类头差异、LoRA 如何降低 Llama 2 微调成本。

第三遍精读 Datasets 和 Experiments，特别关注数据划分、平衡采样、1%/5%/10% 训练数据设置。论文性能极高，复现时最容易出问题的地方就在数据处理。

第四遍读 Results 和 Discussions，重点比较 CAN-C-BERT、CAN-SecureBERT、CAN-LLAMA2，而不是只看最高分。

第五遍读 SHAP 解释部分，理解模型到底从哪些 CAN 字段中获得分类依据。

最后回看 Future Works，把计算开销、对抗鲁棒性、未知攻击检测作为后续研究切入点。

<!-- codex-cli-deep-read: complete -->
