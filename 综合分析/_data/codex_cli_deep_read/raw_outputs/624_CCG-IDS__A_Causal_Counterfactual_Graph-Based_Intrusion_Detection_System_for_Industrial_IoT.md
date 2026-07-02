# [624] CCG-IDS: A Causal Counterfactual Graph-Based Intrusion Detection System for Industrial IoT

## 1. 基本信息

- 题名：CCG-IDS: A Causal Counterfactual Graph-Based Intrusion Detection System for Industrial IIoT
- 年份：2026
- 来源：IEEE Transactions on Industrial Informatics
- DOI：10.1109/TII.2026.3667569
- 主题：工业物联网入侵检测、主机溯源图、图神经网络、低误报校准、反事实解释
- 数据集：EVTX-ATTACK-SAMPLES、DARPA OpTC
- 代码状态：本地未发现该论文对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文提出 CCG-IDS，一个面向工业物联网主机侧日志的可解释图神经网络入侵检测系统。它把 Windows/OpTC 等异构审计日志统一成事件五元组 `{主体, 动作, 客体, 时间, 主机}`，再按 1 分钟时间窗构造溯源子图。模型不是给单个节点打异常分，而是直接判断一个时间窗子图是否包含攻击行为。

核心做法是：GraphSAGE 编码窗口图，使用均值池化和缩放求和池化的双读出表示同时捕获整体行为与稀疏异常；训练时结合类别加权交叉熵和低误报排序损失；推理时用 isotonic calibration、Fisher 信息近似不确定性和 conformal 阈值控制低误报或零误报工作点；报警后通过删除关键边的反事实搜索找到“移除哪些事件后报警就不成立”的最小证据链，再由受约束 LLM 生成 JSON 安全报告。

论文最想解决的不是单纯 AUC 更高，而是工业场景里 IDS 必须同时做到：低误报、跨日志源可迁移、能解释为什么报警。

## 3. 论文解决的具体问题

论文针对的是 IIoT 主机审计日志中的 APT、横向移动、隐蔽执行等行为检测。此类攻击在溯源图里常表现为少量异常边混在大量正常事件中，因此传统异常检测容易出现两个极端：要么漏掉稀疏攻击信号，要么产生大量误报。

作者认为现有 provenance IDS 的关键缺口有四个：攻击信号稀疏、低误报难以保证、跨组织/跨数据源泛化弱、GNN 判定缺少可供分析员核查的因果证据。ThreatTrace 更偏节点角色偏离检测，FLASH 更偏丰富节点表示和可扩展图表征；CCG-IDS 则把检测单位改成“时间窗口子图”，并把阈值校准和反事实解释纳入完整工作流。

## 4. 创新点深度提炼

第一，检测语义从节点异常转向窗口级溯源子图判定。这个变化很重要，因为工业安全分析通常不是孤立调查一个进程节点，而是调查一段时间内的一组相关行为。

第二，双读出池化有明确的异常检测动机。mean pooling 稳定但会稀释少数攻击事件，sum pooling 对计数型异常敏感但受图规模影响。论文用 `mean + 1/sqrt(N) scaled-sum` 兼顾规模稳定性和稀疏信号捕捉。

第三，低误报不是事后调阈值，而是进入训练和部署设计。训练中用 hard negative 排序损失强化低 FPR 边界，部署中用校准概率、Fisher 不确定性和 conformal 阈值形成低 FPR/zero-FP 两种模式。

第四，解释不是注意力可视化，而是反事实必要性：如果删掉某些边，报警分数跌破阈值，则这些边构成决策关键证据。CDS 用单边删除造成的攻击概率下降来排序证据，逻辑上比“相关性热力图”更贴近分析员问的“为什么这条报警成立”。

第五，LLM 只做报告生成，不参与检测决策。论文明确限制 LLM 输入为已抽取证据，输出固定 JSON schema，并用解析和 schema 校验防止幻觉。这一点避免了把检测可信度建立在生成模型自由推理上。

## 5. 科学问题与研究假设

科学问题可以概括为：在异构工业主机日志中，能否通过时间窗溯源图学习得到稳定、低误报且可解释的攻击判定？

核心假设有四个。其一，攻击行为会在窗口级溯源子图中形成可学习的结构和语义模式。其二，少数关键边足以决定攻击窗口的判定，因此反事实删除可以恢复决策证据链。其三，Fisher 梯度敏感性可作为模型不确定性的近似信号，用于保守报警。其四，在 benign validation windows 上做 conformal-style 阈值设定，可以比普通阈值搜索更适合工业低误报部署。

## 6. 科学方法与技术路线

技术路线是“日志标准化 -> 窗口溯源图 -> GNN 图分类 -> 校准风险分数 -> 阈值报警 -> 反事实证据 -> 结构化报告”。

具体地，原始事件被规范为五元组，节点包括进程、文件、远程端点/套接字、用户、主机、注册表等，边表示主体到客体的交互。重复事件在窗口内合并为带权边，边属性包含动作类型、相对时间、端口、计数等。

模型层面使用多层 GraphSAGE 生成节点表示，再通过双读出得到图表示，MLP 输出攻击概率和 margin。训练目标由类别加权 CE 与低 FPR 排序损失组成，后者只关注最容易误报的 hard negatives。验证阶段用 isotonic regression 校准概率，并用 head 参数梯度范数与图表示梯度范数构造 Fisher uncertainty，最后融合为风险分数。

解释层面，给定报警图，算法寻找最小边集 `S`，使得 `G \ S` 的攻击风险低于阈值。由于精确求解 NP-hard，论文采用基于 CDS 的贪心近似，并从高 CDS 边的连通闭包中重构攻击路径子图。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：EVTX 来自 Windows 工控主机安全日志样本；OpTC 来自 DARPA APT 仿真数据，使用 9 月 25 日 host-side eCAR 事件，规模约 15GB。
2. 预处理：用 python-evtx/lxml 解析 EVTX，用 ijson 分布式解析 OpTC eCAR；统一映射为 `{sub, act, obj, τ, ψ}`；实体去重，构造有向溯源图；按 60 秒窗口切分。
3. 标注：EVTX 依据 host prefix `atk/ben` 和已知攻击时间标注；OpTC 使用官方 ground truth/IoC。
4. 图导出：每个时间窗生成 PyTorch Geometric 图对象，保存为 `.pt`；时间顺序划分 70/15/15 训练、验证、测试。
5. 模型与基线：主模型为 GraphSAGE + dual readout + MLP；对比 ThreatTrace、FLASH，以及 Isolation Forest、One-Class SVM、LOF、PCA 重构误差等传统方法。
6. 训练：类别加权交叉熵处理攻击/正常不平衡；低 FPR ranking loss 聚焦 top-α hard negatives；DropEdge 做图结构正则。
7. 指标：ROC-AUC、AUPR、F1、TPR@FPR=1/5/10%、pAUC@10%、Precision@K/Recall@K；解释指标包括 comprehensiveness、sufficiency、sparsity、stability、runtime。
8. 消融/敏感性：移除 dual readout、移除 DropEdge、不同 Fisher uncertainty 范围、不同阈值策略、CDS vs random、Greedy vs OneShot，并测试跨域阈值迁移。
9. 结果核查：重点不只看 AUC，还要核对同一 ROC 下不同阈值产生的 FP/TP trade-off，尤其 zero-FP 和低 FPR 模式是否牺牲过多召回。

## 8. 关键结果、结论与证据

EVTX 上 ROC/PR 表现强，AUPR 约 0.9218；OpTC 上 AUC 为 0.9641、AUPR 为 0.9698，说明模型在更大、更复杂数据上仍保持稳定排序能力。pAUC@10% 分别为 EVTX 0.8723、OpTC 0.8372，表明低误报区间内仍能维持较高平均召回。

阈值比较体现了论文的部署价值。RAW 阈值更激进，召回高但误报也高；Fisher-calibrated 阈值在 OpTC 上达到 FPR=0、TPR=0.6208，在 EVTX 上将 FPR 从 0.1028 降到 0.0748，召回仅从 1.000 降到 0.9778。也就是说，Fisher/Conformal 机制主要提供可控误报的部署开关。

与 ThreatTrace 相比，CCG-IDS 在 OpTC Attack 3 上 precision、recall、F1 均有约 5%-6% 的提升；与 FLASH 相比，F1 和 precision 相当，recall/AUC 略优，但 CCG-IDS 额外提供校准和反事实解释。消融显示 dual readout 和 DropEdge 对低 FPR 工作点尤其关键：去掉它们会显著增加 FP。

## 9. 局限性与待解决问题

论文虽然强调 causal/counterfactual，但其“因果”主要是 provenance 依赖图和反事实边删除意义上的操作性因果，并非严格的结构因果模型识别。边删除能证明“对模型决策必要”，但不能直接证明真实攻击因果机制。

跨域实验也显示阈值迁移存在风险。源域 conformal 阈值直接迁到目标域可能因分数分布漂移而失效，因此实际部署仍需要目标环境 benign validation 数据做再校准。

解释模块的稳定性存在天然挑战。最小反事实边集可能不唯一，Jaccard 稳定性较低并不一定表示解释无效，但会影响分析员复现同一证据链的体验。

LLM 报告模块虽被约束为 JSON，但论文没有充分证明报告质量对不同攻击类型、不同证据粒度、不同 prompt 的鲁棒性。另一个问题是 Qwen-32B fine-tuning 成本较高，边缘或工业现场部署未必方便。

本次正文包标记为未截断，因此上述理解不受正文截断影响；但若用于正式引用，仍建议回到 PDF 核对表格数值、图题编号和实验配置细节。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，尤其适合作为图学习异常检测、工业互联网安全、主机溯源图 IDS、低误报部署和可解释检测的核心参考。

如果本项目关注网络流量异常，它提供的启发是：把检测单位从单条流/单个节点提升到时间窗事件图，并用低 FPR 指标作为主优化目标。如果本项目关注安全运营落地，它的 conformal threshold、zero-FP 模式、Precision@K 和结构化报告设计非常值得借鉴。如果本项目关注论文创新，则“图检测 + 不确定性校准 + 反事实解释”的组合是一个可迁移框架。

## 11. 代码对照分析

本地未发现该论文对应代码包，因此不能逐文件确认实现。但若复现该论文，合理的代码结构应与方法模块一一对应：

- 数据预处理：应包含 EVTX/eCAR 解析、五元组标准化、实体 canonicalization、60 秒窗口切分、PyG 图导出，可能文件名类似 `parse_evtx.py`、`parse_optc.py`、`build_graphs.py`、`dataset.py`。
- 模型：应包含 GraphSAGE 编码器、dual readout、MLP head、DropEdge，可能在 `models/graphsage.py`、`models/ccg_ids.py`。
- 训练：应实现 weighted CE、hard negative ranking loss、temporal split、checkpoint，可能在 `train.py`、`losses.py`。
- 校准与阈值：应包含 isotonic regression、Fisher uncertainty、weighted quantile、zero-FP threshold，可能在 `calibration.py`、`thresholds.py`、`uncertainty.py`。
- 评估：应计算 AUC、AUPR、TPR@FPR、pAUC、Precision@K、跨域迁移和消融，可能在 `evaluate.py`、`ablation.py`。
- 解释：应实现 CDS、贪心边删除、mask 优化、路径重构，可能在 `explain/counterfactual.py`。
- 报告：应有 JSON schema、prompt 模板、grounding 校验，可能在 `reporting/llm_report.py`。

由于没有源码，不能确认论文中的 Qwen-32B 微调、GPU 运行参数、表格复现实验脚本是否公开。

## 12. 本篇精华

- CCG-IDS 的核心不是又一个 GNN IDS，而是把低误报部署和解释证据链纳入同一个检测闭环。
- 时间窗溯源子图比节点级异常更贴近安全分析员的调查单位，也更适合控制报警流。
- 双读出池化解决了图规模变化和稀疏攻击信号之间的张力，是论文中较实用的结构设计。
- Fisher uncertainty + conformal threshold 提供了低 FPR/zero-FP 两种部署模式，但跨域阈值仍需目标 benign 数据再校准。
- 反事实解释回答的是“删掉哪些事件后报警不成立”，比注意力权重更接近可核查证据。
- 论文实验较重视低 FPR 区间指标，如 pAUC、TPR@FPR、Precision@K，这比只报告 AUC 更符合工业 IDS 场景。
- LLM 被限制为报告生成器而非检测器，这是安全系统中较稳妥的生成式 AI 用法。

## 13. 建议精读路线

先读 Introduction 和 Table I/II，明确作者如何区别 ThreatTrace、FLASH 与自己的窗口级检测范式。第二步读 Methodology 的五元组建图、dual readout、Fisher uncertainty、conformal threshold，这四部分构成可复现主线。第三步精读 counterfactual explainer，重点理解 CDS 与“必要证据链”的含义。

实验部分建议按“整体性能 -> 低误报阈值 -> 消融 -> 解释评估 -> 跨域迁移”顺序读。不要只看 F1 和 AUC，重点看 Table IV、IX、X、XI、XII，因为这些表最能体现论文真正贡献：在报警预算受限时如何选择阈值，以及解释是否真的改变模型判定。