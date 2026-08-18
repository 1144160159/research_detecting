# 081 鲁棒性很重要：预训练可提升加密流量分析性能 / Pretrain-Robust

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / I Introduction | 第 2 至 3 节 | 已覆盖 |
| II Related Work | 第 4 节 | 已覆盖 |
| III Robustness Evaluation | 第 5 至 8 节 | 已覆盖 |
| IV BERT-ps | 第 9 至 11 节 | 已覆盖 |
| V–VI Experiments | 第 12 至 17 节 | 已覆盖 |
| VII–VIII Discussion/Conclusion/Appendix | 第 18 至 20 节 | 已覆盖 |

## 1. 文献身份

- 标题：Robustness Matters: Pre-Training Can Enhance the Performance of Encrypted Traffic Analysis。
- 作者：Luming Yang、Lin Liu、Jun-Jie Huang、Jiangyong Shi、Shaojing Fu、Yongjun Wang、Jinshu Su。
- 期刊：IEEE Transactions on Information Forensics and Security，20，2025，10588–10602。
- DOI：10.1109/TIFS.2025.3613970。
- 代码：`Shangshu-LAB/BERT-ps`。
- 方法：packet-length-sequence BERT 预训练＋PA-curve/PA-area 原始流扰动鲁棒性评价。
- 定位：CAEOS packet-sequence encoder 与鲁棒性压力测试基线；不是开放集拒识方法。

## 2. 摘要缩译

既有加密流量分析重视准确率，却忽视网络噪声下预测稳定性。仅报告扰动准确率既忽略样本差异，直接在 feature space 加噪又难以反映真实流变化。

论文提出 PA-curve 描述每个样本正确决策的稳定性分布，并以曲线面积 PA-area 联合量化 accuracy 与 robustness。作者还在约 12.1 TB 无标签流量上预训练 packet-length BERT，在五个下游数据集验证 packet loss、retransmission、disorder 下的鲁棒性。

## 3. 引言缩译

ML、DL 和预训练模型在干净测试集上都可能取得高准确率，但实际网络的突发、路由、拥塞、设备丢包与更新会改变 packet sequence。靠近 decision boundary 的样本比远离边界的样本更易受扰动，同一个准确率无法反映这种局部差异。

作者主张在 raw network flow 上施加可解释扰动，再统计扰动邻域中的预测类别分布。PA-curve 越靠右代表越稳定，越靠上代表越准确。

## 4. 相关工作缩译

传统 ML 使用 packet statistics、TLS metadata、Markov fingerprint、path signature；DL 使用 FS-Net、Traffic Interaction Graph；预训练包括 PERT、ET-BERT、Flow-MAE、YaTC、TrafficFormer、NetMamba。

既有鲁棒性研究涵盖 feature-space Gaussian/Laplacian noise、adversarial examples、concept drift、replay rate、TCP-aware augmentation 和 randomized smoothing。论文批评不保持 feature correlation 的人工扰动会产生不真实结论。

## 5. 网络流与三类扰动

流表示为 packet sequence：

> x = ⟨P₁, P₂, …, Pₙ⟩，分类器 f:X→Y。

扰动 ε 来自 Υ(σ)，扰动样本为：

> x̃ = x ⊕ ε。

三种 raw-sequence perturbation：

- Packet loss：每个 packet 以概率 σ 删除。
- Retransmission：每个 packet 以概率 σ 复制重传。
- Disorder：每个 packet 以概率 σ 与下一 packet 交换。

作者假定协议校验使扰动不修改 payload content，只改变 packet-length sequence。模拟是标准化压力测试，不等于真实 TCP 重放或端到端测量。

## 6. 样本级决策稳定性

对样本 x 的扰动邻域，最高和次高类别为：

> cᴬ = arg maxᶜ Pr[f(x⊕ε)=c]，

> cᴮ = arg max(c≠cᴬ) Pr[f(x⊕ε)=c]。

定义 probability margin：

> Δp = pᴬ − pᴮ。

只有 c_A 等于真值时，该 margin 才计入正确鲁棒性。margin 大表示扰动邻域中预测更稳定，但它不是模型 softmax calibration，也不是对未知类别的拒识概率。

## 7. Monte Carlo 与置信界

每个样本重复 N 次扰动，统计最高/次高类别次数。用 Clopper–Pearson 区间求 p_A 下界与 p_B 上界：

> Δp̂ = p̲ᴬ − p̄ᴮ。

实验 N=1000，置信系数 0.999，即 α=0.001。作者观察 N>200 后估计趋稳，但正式设置每样本约需 0.53 秒，计算开销为 O(N)。

该置信界控制 Monte Carlo 比例估计误差，不是对数据集总体性能的 bootstrap CI。

## 8. PA-curve 与 PA-area

测试集有 N 个样本。对稳定性门槛 t，PA-curve 纵坐标为：

> PA(t) = (1÷N)Σᵢ₌₁ᴺ 𝟙[cᴬ⁽ⁱ⁾=yᵢ ∧ Δp̂ᵢ≥t]。

面积：

> PA-area = ∫₀¹PA(t)dt。

离散实现为相邻曲线点的梯形积分。σ→0 时，扰动邻域收缩、Δp→1，PA-area 退化为 clean accuracy。

因此 PA-area 同时混合准确性与稳定性；适合比较同一任务和同一扰动分布下的模型，不适合替代单独的 clean Macro-F1、扰动后性能下降与 open-set 指标。

## 9. Packet-Length Tokenization

Zeek 按五元组形成双向 flow。删除没有 transport-layer payload 的 SYN/ACK 等功能包，也删除少于 5 个非零 payload packet 的 mouse flow。

token 为带方向的 transport payload length：上行正、下行负；长度范围 1–1500，两个方向，共加 [CLS]、[SEP]、[PAD]、[MASK]、[UNK] 五个特殊 token。

该输入包含 packet payload length，但不包含 payload bytes；它属于 packet-sequence/timing 之外的长度序列模态。

## 10. BERT-ps 结构

模型由 packet-length embedding、bidirectional Transformer encoder、classification head 构成。位置 i 的 embedding：

> Eᵢ = Eᵢˡᵉⁿ + Eᵢᵖᵒˢ。

[CLS] 表示经全连接和 Softmax 得到：

> p = Softmax(Wx+b)。

模型参考 BERT-base，并另有 base、middle、small、mini、tiny 规模，用于研究参数量与鲁棒性的关系。

## 11. 预训练与微调

Masked Language Modeling 随机 mask 15% token，其中 80% 替换为 [MASK]，10% 随机 token，10% 保持。损失为：

> Lᴹᴸᴹ = −Σᵢ₌₁ᵏ log Pr(maskᵢ=tokenᵢ ∣ X̃;Θ)。

下游使用交叉熵：

> Lᶜˡˢ = −(1÷N)ΣᵢΣᶜ yᵢc log pᵢc。

为防止随机初始化 head 破坏稳定预训练参数，先冻结 backbone warm-up classification head，再 full-parameter fine-tuning。

## 12. 预训练数据与计算条件

作者在某网络 gateway 一周采集约 12.1 TB PCAP，解析为 7611 万 packet-length sequences、约 29.6 亿 token。来源域、应用分布、隐私过滤、训练污染及与下游重叠检查披露不足。

实验硬件为 AMD EPYC 7542、8×RTX 6000 Ada、512 GB RAM，PyTorch 2.2.1。大规模预训练资源显著高于 CAEOS 单卡 48 GB 条件，正式比较应使用发布 checkpoint 或控制 compute budget。

## 13. 五个下游数据集

- DataCon2020：sandbox 中 malware 与 normal exe 的 TLS/SSL 流，二分类。
- DataCon2021-p1：6 种 encrypted proxy 软件分类。
- DataCon2021-p2：同一代理下 22 个网站识别。
- EBSNN-dataset：应用与网站流量，清洗后 22 类。
- CSTNET-TLS1.3：Alexa Top-5000 TLS 1.3 流量中选择 80 类。

这些都是固定标签闭集分类；只有 DataCon2020 涉及恶意/良性，且仍不是已知攻击家族＋未知家族拒识。

## 14. 对比方法

Packet-length baselines：AppScanner、ETC-PS、FlowLens、FS-Net、GraphDApp。预训练 bytes baselines：ET-BERT、YaTC、NetMamba、TrafficFormer。

作者称 byte-pretrained 模型在 DataCon2021-p2 encrypted tunnel 中失败，而 BERT-ps 仍约 90%；CSTNET-TLS1.3 accuracy 97.5%。这一比较同时改变输入表示、预训练语料和模型，不能单独归因于 packet-length sequence。

## 15. 准确率结果

BERT-ps 在五个任务上均优于从头训练的 packet-length 版本。DataCon2021-p2 和 CSTNET-TLS1.3 相对已有 packet-sequence SOTA accuracy 约高 7% 和 5%；DataCon2020 与 EBSNN 相对最佳预训练模型约低 1.2% 和 2.5%。

预训练相对从头训练：DataCon2021-p2 Accuracy/Macro-F1 约提升 2.8%，DataCon2020 二分类提升不足 0.8%。这些是 closed-set 成绩，不可推导未知检测。

## 16. 鲁棒性结果

BERT-ps 在 loss、retransmission、disorder 不同 σ 下的 PA-curve 通常更靠右上，PA-area 下降更慢。相对从头训练，常见噪声下最高约提升 10% PA-area。

Packet loss 影响最大，因为直接减少 token；retransmission 对 BERT-ps 影响很小；disorder 从 0.1 增到 0.6 时 PA-area 降幅不足 2%。AppScanner/FlowLens 使用 order-independent statistics，因此 disorder 曲线也较平。

结果说明不同输入的扰动不变性不同，不能只比较平均 PA-area，还应报告 clean performance 和每类扰动敏感性。

## 17. 规模、增强与效率

大于 BERT-small 后预训练模型通常才稳定优于 baselines；tiny 版本可能更差，说明“预训练”本身不是充分条件。

训练时加入 loss 0.2、retransmission 0.2、disorder 0.3 的 data augmentation 可改善鲁棒性，但总体弱于预训练＋微调。该结论受预训练数据量与算力不对等影响，不能概括为预训练永远优于增强。

BERT-ps 处理 1000 flows 约 0.59 秒；feature extraction 约 0.07 秒/千流，主要耗时在 inference。大模型对 edge deployment 的参数、能耗和 GPU 依赖明显。

## 18. 局限缩译

- PA 指标需大量 Monte Carlo inference。
- 仅模拟三种独立均匀扰动，未覆盖混合、非均匀、burst loss、capture truncation、direction error 与 concept drift。
- 大模型预训练和部署成本高。
- BERT-ps 没有专门设计新的鲁棒结构，结论主要来自规模与预训练数据。
- 论文没有开放集、置信校准或错误拒识分析。

## 19. 结论缩译

PA-curve 用 decision probability margin 的分布同时表达正确率与稳定性，PA-area 提供单值量化。TB 级流量预训练的 BERT-ps 在五个加密流量任务上取得较强准确率和网络噪声鲁棒性，表明大规模预训练除表示能力外还可改善稳定性。

## 20. 指标附录

论文 accuracy：

> Acc = (1÷N)Σᵢ𝟙[ŷᵢ=yᵢ]。

类别 c 的 F1：

> F1ᶜ = 2PᶜRᶜ ÷ (Pᶜ+Rᶜ)。

Macro-F1：

> Macro-F1 = (1÷|Y|)Σ(c∈Y)F1ᶜ。

# 第二部分：独立技术分析

## A. 一句话结论

Pretrain-Robust 应作为 CAEOS 的 packet-sequence 强 encoder 与扰动稳健性基线；它证明 clean accuracy 不足以代表部署性能，但闭集 PA-area 也不能替代三层开放集指标，更不能证明证据冲突机制有效。

## B. 两条交付线

### 工程线

在同一 packet-length input 上对 BERT-ps checkpoint、scratch Transformer 与现有 sequence encoder 做公平比较；把 loss/retransmission/disorder 施加在 PCAP/packet sequence 层，并保留原始标签和配对模态。

### 论文线

把该文放入“预训练与鲁棒性”支线。主文单独报告 clean 三层指标与扰动后指标，不用 PA-area 一个数掩盖已知识别下降、未知拒识下降或 Benign FAR 上升。

## C. 协议审计

- Downstream task：固定标签 closed-set supervised fine-tuning。
- Pretraining：大规模无标签 gateway traffic，潜在下游域重叠未审计。
- Noise：测试时合成 packet loss/retransmission/disorder。
- Split：正文未给 capture/device/grouped split 证据。
- Unknown：没有 unknown family、unknown-blind threshold 或 rejection head。
- Protocol：`P1-closed-set-supervised-robustness/P3-pretrain-overlap-and-group-split-unclear`。

## D. 三层指标判断

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Accuracy、Macro-F1 | Macro-F1、BA、per-class Recall、Benign FAR | 部分可用 |
| 未知检测 | 无 | AUROC、AUPR-Out、FPR95、Unknown-F1 | 缺失 |
| 联合开放集 | 无 | OSCR、Known Acceptance、Unknown Rejection | 缺失 |
| 校准/鲁棒 | PA-curve、PA-area | ECE、Brier、NLL＋扰动三层指标 | 互补但不可替代 |

## E. PA-area 的边界

PA-area 高可能来自 clean accuracy 高、margin 稳定或两者共同作用。它不区分：

- 对正确类别稳定与对错误类别稳定。
- 已知攻击稳定分类与未知攻击稳定误归类。
- 概率 margin 与概率校准。
- 随机扰动鲁棒与域外泛化。

CAEOS 应同时报告 clean metric、perturbed metric、absolute drop、PA-area 和 calibration shift。

## F. 与证据冲突的关系

网络扰动会使 payload、sequence、statistics 三模态受损程度不同，是检验 conflict 的天然场景。真正有效的冲突机制应在单模态丢包/错序时提高不确定性或拒识，而不是继续高置信输出错误已知类。

必须比较：无冲突融合、质量感知 gating、conflict risk、单模态缺失 mask，并在同一扰动强度下检查 Known Macro-F1、Unknown AUROC、OSCR、ECE 与 Benign FAR。

## G. 采纳与否决

### 采纳

- Packet-length sequence encoder/checkpoint。
- Raw sequence 三类标准扰动。
- PA-curve 作为补充鲁棒性图。
- SFT 与 TFS 同结构消融。
- 参数规模、增强和效率对照。

### 有条件采纳

- Monte Carlo N 可先做 200/500/1000 精度成本消融。
- Packet loss 应增加 burst loss 与 capture truncation。
- Pretrained checkpoint 需查训练语料与下游重叠。

### 不采纳

- 不用 PA-area 替代 OSR 三层指标。
- 不把 closed-set 97.5% 写成已知恶意分类目标达成。
- 不把 packet length 称为 payload byte 模态。
- 不以不同输入/预训练资源的比较证明单一机制优越。
- 不删除短流后隐去覆盖率和类别偏差。

## H. CAEOS 可执行实验

1. `E-ROBUST-01`：BERT-ps checkpoint vs scratch，同 input/split/fine-tune budget。
2. `E-ROBUST-02`：loss、burst-loss、retransmission、disorder、truncation 单扰动曲线。
3. `E-ROBUST-03`：混合与非均匀扰动。
4. `E-ROBUST-04`：每个模态独立扰动与全模态同步扰动。
5. `E-ROBUST-05`：clean/perturbed 三层指标、ECE 和 PA-area 联合报告。
6. `E-ROBUST-06`：conflict/no-conflict 在模态矛盾样本上的 paired test。
7. `E-ROBUST-07`：短流保留/删除覆盖率及类别分布审计。
8. `E-ROBUST-08`：吞吐、显存、延迟、参数量与性能 Pareto。

## I. 可引用与不可引用主张

### 可引用

- BERT-ps 在约 12.1 TB、7611 万 flows 上 MLM 预训练。
- 输入是带方向 transport payload-length sequence，不是 payload bytes。
- PA-area 融合 clean accuracy 与扰动邻域 decision stability。
- 测试覆盖 loss、retransmission、disorder，使用 Clopper–Pearson 置信界。
- 预训练相对 scratch 在常见噪声下最高约提升 10% PA-area。

### 不可引用

- 预训练自动提高 unknown rejection。
- PA-area 等同 AUROC、FPR95 或 OSCR。
- 12.1 TB 预训练语料与下游完全无重叠。
- Packet-length sequence 等同 payload modality。
- 随机独立丢包完整模拟真实网络。
- 大模型一定比数据增强更好。

## J. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 IEEE/DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P1-closed-set-supervised-robustness/P3-pretrain-overlap-and-group-split-unclear`
- G5 方法门：通过
- G6 结果门：通过，五数据集、三扰动、规模/增强/效率已核读
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
