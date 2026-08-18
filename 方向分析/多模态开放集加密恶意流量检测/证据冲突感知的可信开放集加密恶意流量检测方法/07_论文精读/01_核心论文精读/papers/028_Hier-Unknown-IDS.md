# 028 面向未知攻击的分层入侵检测系统实证研究 / Hierarchical IDS for Unknown Attacks

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| I Introduction | 第 3 节 | 已覆盖 |
| II Related Work | 第 4 节 | 已覆盖 |
| III Datasets Description | 第 5 节 | 已覆盖 |
| IV Preliminaries | 第 6 节 | 已覆盖 |
| V Proposed Framework | 第 7 至 9 节 | 已覆盖 |
| VI Results and Discussion | 第 10 至 14 节 | 已覆盖 |
| VII Conclusion | 第 15 节 | 已覆盖 |

## 1. 文献身份

- 标题：Empirical Study of Hierarchical Intrusion Detection Systems for Unknown Attacks。
- 中文题名：面向未知攻击的分层入侵检测系统实证研究。
- 作者：Menaka Pushpa Arthur、Ganesan Ramachandran、Keshav Sood、Pavan Kaarthik、Srivarshinee Sridhar、Morshed Chowdhury。
- 期刊：IEEE Transactions on Network and Service Management，Vol. 22，No. 6，2025-12，页 5564–5581。
- DOI：10.1109/TNSM.2025.3600378。
- 本地全文：`paper/10.1109_TNSM.2025.3600378.pdf`。
- 研究对象：基于表格化网络流特征的分层 IDS，区分 benign、known attack 和 held-out unknown attack。
- 方法类型：异构传统机器学习/深度学习组合与贝叶斯超参数优化，不是端到端多模态加密流量模型。

## 2. 摘要缩译

传统 IDS 以闭集攻击类别训练，面对未见攻击时容易误分类。持续学习又依赖专家不断标注新样本。论文复现并扩展一种多层分级 IDS：第一阶段区分 benign 与 attack，第二阶段分类 known attack，第三阶段把不能可靠归入 known 的攻击确认为 unknown。作者在异常检测阶段比较多种无监督和半监督算法，在 known 多分类阶段比较多种监督算法，并用 Tree-structured Parzen Estimator（TPE）和 Gaussian Process Bayesian Optimization（BOGP）调参。

实验覆盖 5G-NIDD、WUSTL-IIoT、UNR-IDD 和 CICIDS2017。摘要报告增强系统对 unknown 的最高分类率分别为 96.2%、87%、96.8% 和 100%，并称计算时间约减半。但这些是按数据集选择最佳算法组合后的单点分类率，不是统一模型的跨数据集结果，也不是 FPR@95TPR。

## 3. 引言与研究问题缩译

论文把未知攻击问题归因于三点：闭集分类器会强制把 unknown 分入已知类；单层异常检测难以同时完成 benign 识别和细粒度攻击分类；不同数据集的类别分布和特征结构使单一算法难以普遍有效。

作者先复现 Verkerken 等人的三阶段 hierarchical IDS，再发现其跨数据集性能不稳定：小数据集上 unknown 可能较好，但 known 易被误拒；较大数据集上的 unknown 识别也只有约 80%。于是论文通过枚举 stage 1 和 stage 2 的异构算法，并用 BOGP 替代或比较 TPE，寻找各数据集最佳组合。

## 4. 相关工作缩译

已有未知攻击 IDS 包括聚类/outlier、开放集 reciprocal point、生成式未知样本、主动学习、持续更新、多层 signature/anomaly 混合模型。论文强调分层架构的好处：先学习 benign 边界，再在攻击子集中学习 known attack，最后对未确认攻击做 unknown 判定。

这种分解有利于诊断每一级错误，但会产生级联误差：stage 1 把攻击误判为 benign 后，后续阶段无法恢复；stage 2 或 stage 3 的阈值也可能把 known attack 错拒为 unknown。

## 5. 数据集与 unknown 构造缩译

| 数据集 | Benign 数 | Known attack 总数 | 实际抽样 known 数 | Unknown 数 | Known 标签 | Unknown 标签 |
|---|---:|---:|---:|---:|---|---|
| 5G-NIDD | 475,279 | 735,593 | 3,000 | 1,155 | UDPFlood、HTTPFlood、SlowrateDoS、SYNScan、TCPConnectScan、UDPScan、SYN-Flood | ICMPFlood |
| WUSTL-IIoT | 1,107,448 | 86,545 | 8,240 | 471 | DoS、Recon | CommInj、Backdoor |
| UNR-IDD | 3,773 | 32,615 | 5,615 | 1,022 | PortScan、TCP-SYN、Blackhole、Diversion | Overflow |
| CICIDS2017 | 2,095,057 | 425,694 | 1,948 | 47 | Botnet、BruteForce、DDoS、WebAttack、PortScan | Heartbleed、Infiltration |

unknown 不是现实时间线上首次出现的零日攻击，而是实验设计者从已有标注数据中留出的类别。CICIDS2017 的 Heartbleed 和 Infiltration 因样本少而被指定为 unknown；其他数据集也主要选择少数类。论文明确写道，选取低出现频率的 known attack 类模拟 unknown。

这种构造检验稀有类留出检测，但把“稀有”与“未知”绑定，不能代表高频 unknown 或语义上接近 known 的未知攻击。CICIDS2017 只有 47 个 unknown，100% 只意味着该次评测中 47 个样本全部命中，统计不确定性很大。

## 6. 候选算法缩译

stage 1 的异常检测候选包括 Autoencoder、Isolation Forest、isolated Nearest Neighbor Ensemble、Local Outlier Factor、k-means、One-Class SVM、Probabilistic Autoencoder 和 CNN-AE。它们主要利用 benign 或无标签结构区分 benign 与非 benign。

stage 2 的 known attack 分类候选包括 KNN、CART、Naive Bayes、Logistic Regression、MLP、Extra Trees、XGBoost、AdaBoost、CNN、Soft CNN、LSTM、GRU 等。论文分别用 TPE 与 BOGP 搜索超参数，并从大量组合中挑选每个数据集表现较好的 stage 1 和 stage 2 配对。

这是一项模型组合搜索研究，而不是固定架构一次训练后跨域验证。每个数据集可选择不同的最佳算法。

## 7. 三阶段框架缩译

第一阶段学习 benign 与 attack 的边界。若样本判为 benign，流程结束；非 benign 样本进入第二阶段。

第二阶段用监督多分类器识别 known attack。分类得分与阈值 τₘ 比较；不能被稳定确认为 known 的攻击送入第三阶段。

第三阶段把未确认样本的异常分数与 stage 1、stage 3 阈值联合比较，最终输出 unknown。原文对不同阶段分别使用 τᵦ、τₘ、τᵤ。复现系统得到的示例阈值为：

| 数据集 | τᵦ | τₘ | τᵤ |
|---|---:|---:|---:|
| 5G | 0.207 | 0.950 | −0.003 |
| WUSTL | 0.170 | 0.950 | −0.113 |
| UNR | 0.072 | 0.700 | −0.256 |
| CICIDS2017 | 0.001 | 0.914 | 0.995 |

阈值跨数据集差异极大，说明分数没有统一尺度。论文没有清楚说明 train/validation/test 拆分，也没有说明 BOGP/TPE 的目标函数和阈值是否只在独立 validation 上优化。

## 8. 代表性异常分数与指标公式缩译

Isolation Forest 的异常分数基于样本在随机树中的平均路径长度。论文用分段规则示意：高分判 anomaly、低分判 normal、中间分数判暂不确定。具体界限示例为 0.8 和 0.5，但最终系统又使用数据集特定优化阈值。

Balanced Accuracy 定义为：

> BA =（Sensitivity + Specificity）÷2。

Fβ 定义为：

> Fβ =（1 + β²）× Precision × Recall ÷（β² × Precision + Recall）。

论文报告 Accuracy、Precision、Recall、Balanced Accuracy 和 F-score，但最终 Fig. 14 的核心比较是 benign、known attack、unknown attack 三组分类准确率，而非完整开放集曲线。

## 9. 实验环境与复现信息缩译

实验运行在 NVIDIA H100 80GB 服务器，配置包括 48 CPU cores、1TB RAM 和 NVLink。论文声称使用 Python、PyTorch、TensorFlow 等环境。

但论文未给出：

- 明确 train/validation/test 比例。
- capture、时间或 flow-grouped 拆分规则。
- 随机种子和重复次数。
- BOGP/TPE 的搜索空间、迭代预算和优化集合。
- 每个候选算法的最终完整配置。
- unknown 是否参与超参数和阈值选择。

因此运行在 H100 只能说明计算环境，不能证明结果协议严格或可复现。

## 10. 原分层 IDS 的复现结果缩译

复现系统显示 stage 1 的 benign/attack 表现在不同数据集差异明显。CICIDS2017 的 benign accuracy 仅 68.7%，而 attack accuracy 为 96.0%；UNR 与 WUSTL 的 benign accuracy 接近 99.7% 和 99.6%。这说明数据不平衡与特征分布对第一阶段影响显著。

完整原系统对 unknown 的分类率为：5G 94.7%、WUSTL 82.8%、UNR 99.8%、CICIDS2017 87.2%。但部分 known attack 被大量错拒为 unknown，表明仅看 unknown recall 会掩盖 known 误拒。

## 11. 增强系统算法选择缩译

作者从 stage 1 候选和 stage 2 候选中按数据集选择最佳组合：

- 5G：GP 优化的 CNN stage 1，加 BOGP 优化的 Extra Trees stage 2。
- WUSTL：GP 优化的 LOF stage 1，加 BOGP 优化的 GRU stage 2。
- UNR：GP 优化的 LOF stage 1，加 TPE 优化的 Extra Trees stage 2。
- CICIDS2017：GP 优化的 CNN 或 OCSVM stage 1，加 BOGP 优化的 AdaBoost stage 2。

这些结果证明异构算法适配数据集有价值，但不构成一个统一的 SOTA 模型。算法选择过程若参考最终测试表现，会形成显著 selection bias。

## 12. 最终对照结果缩译

Fig. 14 的 per-group classification accuracy 为：

| 数据集 | 系统 | Benign | Known attack | Unknown attack |
|---|---|---:|---:|---:|
| 5G | 原系统 | 99.7 | 68.8 | 94.7 |
| 5G | 增强系统 | 99.6 | 85.0 | 96.2 |
| WUSTL | 原系统 | 99.6 | 97.8 | 82.8 |
| WUSTL | 增强系统 | 99.1 | 99.75 | 87.0 |
| UNR | 原系统 | 99.7 | 76.3 | 99.8 |
| UNR | 增强系统 | 100.0 | 86.0 | 96.8 |
| CICIDS2017 | 原系统 | 98.6 | 93.6 | 87.2 |
| CICIDS2017 | 增强系统 | 92.3 | 89.3 | 100.0 |

增强系统并非所有维度都改善：UNR unknown 从 99.8% 降至 96.8%；CICIDS2017 虽把 unknown 提至 100%，benign 和 known 分别降至 92.3% 和 89.3%。这正是单独摘录最高 unknown detection 会产生误导的原因。

## 13. 计算时间结果缩译

论文报告增强系统相对原系统降低约 50% 计算复杂度，并给出各 stage 的训练和测试耗时。例如原系统在部分数据集上的 stage 训练从毫秒到数分钟不等，复杂数据集推理也更慢。

但候选算法搜索、TPE/BOGP 调参和全组合比较的总搜索成本没有并入最终单模型耗时。因而“减少 50%”主要是选定配置后的运行时间，不是完成模型选择全流程的总成本。

## 14. 讨论缩译

作者总结：MLP、Extra Trees、XGBoost 在 stage 2 较强；LOF、iForest 和 CNN 类方法在 stage 1 较强；BOGP 通常优于 TPE。不同数据集需要不同组合，没有一个候选在所有场景占优。

论文承认未来仍需提升总体检测准确率，并在实时开放集流量上降低误报与推理时间。该承认说明当前 benchmark 结果不能直接外推到真实在线零日攻击。

## 15. 结论缩译

分层混合 IDS 比单层闭集 IDS 更适合把 benign、known attack 和 unknown attack 分开处理。通过异构算法组合与贝叶斯调参，论文在四个数据集上获得若干较高 unknown 分类率，并改善部分 known 分类。但最终方案是数据集特定组合，协议和模型选择细节不足，仍需真实开放集流量与严格低误报评估。

# 第二部分：独立技术分析

## A. 一句话结论

该文证明了“benign 门控、known 分类、unknown 确认”三级分解值得作为结构化基线，但其稀有类留出、数据集特定选模和未说明验证来源使结果只能列入弱协议实证附表，不能作为 CAEOS strict-v4 SOTA 主证据。

## B. 协议审计

- unknown 构造：从现有数据集中挑选低频攻击类别作为 held-out unknown。
- unknown 训练：正文意图是不进入监督训练，但未给出可审计拆分清单。
- threshold/model selection：TPE/BOGP 目标数据来源不明。
- split：没有 train/validation/test 比例和 grouped 规则。
- seeds：未报告多随机种子、均值或标准差。
- algorithm selection：按每个数据集最终表现挑选不同 stage 组合，存在 test-informed selection 风险。
- 协议等级：`P3-split-threshold-model-selection-unclear`。
- 主表资格：不能进入 strict P0 主表，可进入层次结构基线和协议风险附表。

## C. “零日攻击”语义审计

实验中的 unknown 是 Heartbleed、Infiltration、ICMPFlood、Overflow 等已有名称和完整标签的历史攻击，只是在该轮训练中留出。它模拟类别未知，不是按时间切分的真实 zero-day，也没有攻击发生前后时间线。因此论文只能支持 held-out attack class detection，不能证明真实零日提前发现。

## D. 数据抽样与统计风险

四个数据集对 known attack 做了大幅抽样，但论文未给出一致抽样规则。CICIDS2017 只有 47 个 unknown，结果对单个样本极其敏感；WUSTL 也只有 471 个 unknown。没有置信区间和 seed 重复时，100% 不能视为稳定上界。

此外，论文正文称 CICIDS2017 共 5,392,441 个样本，但表 II 所列 benign、known 和 unknown 合计明显不同，表明还有未解释的清洗或抽样阶段。CAEOS 不能照搬其样本计数，必须建立正式 manifest。

## E. 多模态与加密流量映射

原文输入是各数据集已有的表格化流特征，WUSTL 使用 Argus 41 维特征。它不是加密 payload 表征，也没有 packet/flow/payload 多模态融合。

可迁移的是层次决策结构，而非编码器：

1. 第一层做 benign 与 malicious 风险门控。
2. 第二层对已接受的 known malicious 做攻击家族分类。
3. 第三层对不满足 known 支持的恶意样本执行 unknown 拒识。

CAEOS 应使用共享多模态表征和统一风险校准实现该结构，避免三个独立模型的级联误差失控。

## F. 三层指标映射

| 层级 | 原文证据 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Known attack classification accuracy | Known Macro-F1、BA、per-class Recall、Benign FAR | 部分覆盖 |
| 未知检测 | Unknown attack classification accuracy | AUROC、AUPR-Out、FPR@95TPR、Unknown-F1 | 不充分 |
| 联合开放集 | benign/known/unknown 三组单点 accuracy | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 数据集特定阈值 | ECE、Brier、NLL | 缺失 |

该文自身的 trade-off 证明分层报告是必要的：CICIDS2017 unknown 提升时 benign 与 known 同时下降。

## G. 95%/5% 安全验收

四个数据集都不能完整通过 CAEOS 安全表：

- 5G：unknown 96.2%，但 known 仅 85.0%。
- WUSTL：known 99.75%，但 unknown 仅 87.0%。
- UNR：unknown 96.8%，但 known 仅 86.0%。
- CICIDS2017：unknown 100%，但 benign 92.3%、known 89.3%。

论文没有报告 Benign FAR，也没有 FPR@95TPR。Benign accuracy 92.3% 还意味着 CICIDS2017 的 benign error 达 7.7%，已经高于 5% 门槛，但该 error 是否全部对应恶意误报仍需混淆矩阵定义确认。

## H. CAEOS 采纳与否决

### 采纳

- 采纳 benign/known/unknown 的层次错误分解。
- 采纳统一报告每一级条件通过率和端到端结果。
- 采纳传统 iForest、LOF、OCSVM、Extra Trees 作为轻量基线。
- 采纳超参数优化预算和运行成本审计。

### 不采纳

- 不把低频类别自动定义为 unknown。
- 不按最终测试表现为每个数据集选择不同最佳模型后宣称统一 SOTA。
- 不以 47 个样本的 100% 宣称安全完成。
- 不把 H100 运行等同于 GPU 加速算法贡献。
- 不用单点 unknown accuracy 替代 AUROC、FPR95 和 OSCR。

## I. CAEOS 可执行实验

1. `E-HIER-01`：flat N+1、两阶段、三阶段模型在相同 split 上比较。
2. `E-HIER-02`：记录 stage 1 攻击漏检、stage 2 known 误分、stage 3 known 误拒的级联矩阵。
3. `E-ML-03`：iForest、LOF、OCSVM、Extra Trees 与深度风险在同一特征集比较。
4. `E-SPLIT-04`：leave-family-out 全矩阵，不按类别频率挑 unknown。
5. `E-STAT-05`：至少 5 seeds，并对小 unknown 类使用 bootstrap CI。
6. `E-OPT-06`：所有模型选择只用 known-only validation，冻结后评测 unknown。
7. `E-GATE-07`：逐场景填写 Known 95%、Benign FAR 5%、Unknown FPR95 5% 安全表。

## J. 可引用与不可引用主张

### 可引用

- 分层 IDS 可把 benign 门控、known 分类和 unknown 确认的错误来源分开。
- 不同数据集上的最佳传统算法组合并不相同。
- 增强系统在四个固定场景的 unknown 分类率为 96.2%、87.0%、96.8% 和 100%。
- unknown 提升可能伴随 benign 或 known 性能下降。

### 不可引用

- 增强系统在所有指标和数据集都优于原系统。
- CICIDS2017 的 100% 证明真实零日检测已经解决。
- 该方法满足 known 95% 和误报低于 5%。
- 该文是多模态加密恶意流量检测方法。
- BOGP 结果已证明 unknown-blind 阈值选择。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地 DOI PDF 与全文抽取存在
- G2 身份门：通过至 DOI、卷期页，Zotero 待办
- G3 任务门：通过，held-out attack class 而非真实时间零日
- G4 协议门：通过，`P3-split-threshold-model-selection-unclear`
- G5 方法门：通过
- G6 结果门：通过，表 II、III、VI 与 Fig. 14 已核读
- G7 对比门：通过，但模型按数据集选择且协议弱
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
