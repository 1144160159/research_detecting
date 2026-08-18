# 099 CAIDS：基于自动编码器与双随机森林的未知攻击防御

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | PDF页 | 本卡 | 状态 |
|---|---:|---|---|
| Abstract / Introduction / Related Work | 1-3 | 第1-3节 | 已覆盖 |
| System / Unknown Model / Preprocessing | 3-6 | 第4-6节 | 已覆盖 |
| Known Model | 6-8 | 第7节 | 已覆盖 |
| Experiments / Results | 8-11 | 第8-9节 | 已覆盖 |
| Conclusion | 11 | 第10节 | 已覆盖 |

## 1. 身份与摘要缩译

作者为 Chen Zhang、Lu Zheng、Huakun Huang 和 Chunhua Su，发表于 IEEE Transactions on Vehicular Technology，75(3)，2026，DOI 10.1109/TVT.2025.3613343。

CAIDS 由两层组成：AE 只学习 normal traffic，以重构误差识别异常/“unknown flow”；CDDRF 通过分层 K-fold 生成高置信和低置信训练子集，训练两棵 Random Forest 系统以识别 normal 与 known attack。论文在 EDGE-IIoT、UNSW-NB15、CICIDS2017 和 TON-IoT 上评估。

## 2. 引言与相关工作缩译

作者认为静态 IoV IDS 无法持续处理未知流量，深度模型成本又较高。相关工作包括自动更新 IDS、GAN normality model、CNN-LSTM、IoT-PRIDS、层级分类和 DS 融合。CAIDS 选择简单 AE＋RF，以重构阈值处理新攻击，以 confidence-driven dual RF 提高难样本分类。

## 3. 系统任务缩译

第一层以 normal-only AE 判断流量是否偏离正常分布；重构误差 Φ>P 时判为 unknown flow，否则进入 known-flow 分支。第二层 CDDRF 再在 normal/known attack 标签上分类。系统术语存在歧义：第一层实际识别的是“异常”，其中也可能包含训练已见攻击，不等同于 OSR 中“非任何已知攻击类”的 unknown。

论文还允许把系统最终确认的 normal 流加入 rolling buffer，定期更新 normal reconstruction-error 的 95% 分位阈值，例如每小时或每 500 个新正常样本更新。

## 4. 数据与预处理缩译

数据处理包括删除高基数字段、one-hot categorical、缺失值均值填充、标准化和 PCA。AE 训练/验证只使用 normal；测试包含 normal 和被选作 unknown 的攻击。TON-IoT normal 随机按 70%/30% 分训练测试，选定攻击类型及其组合只出现在测试。

严重协议问题是：论文说明不同 unknown test set 分别执行 PCA 和 feature encoding，导致输入维度和编码随目标未知集合改变。若 PCA/编码拟合读取测试整体分布，则属于 target-test exposure，不能与 strict-v4 比较。

## 5. AE unknown 模型缩译

AE 最小化重构均方误差。normal validation 的误差分布给出阈值 τₘₛₑ，测试样本 x 的规则为：

r(x) = ‖x − x̂‖²

r(x)>τₘₛₑ ⇒ abnormal/unknown；否则 ⇒ known-flow branch

阈值使用 normal validation 是可取的 known-only 原则，但论文同时按 unknown 测试复杂度独立预处理，破坏了整体严格性。

## 6. CDDRF known 模型缩译

训练集做 stratified K-fold。每折用 K−1 折训练初始 RF，对留出折得到 out-of-fold confidence。按阈值 r 把样本分为 high-confidence 子集 aᵣ 和 low-confidence 子集 bᵣ，分别训练 RFₐ 与 RFᵦ，推理时再投票。

作者在独立 UNSW-NB15 validation 上扫描 r = 0.0,0.1,…,1.0，以 F1 选择 r = 0.9，然后在其他数据集使用该静态阈值。这个阈值不是 unknown risk threshold，而是 known classifier 的数据分层阈值。

## 7. 已知检测结果缩译

EDGE-IIoT 上 CDDRF F1 为 99.72%，RF 96.44%，XGBoost 90.41%，LSTM 82.12%，1D-CNN 73.81%，Transformer 72.98%。CICIDS2017 中 CDDRF 比 Logistic Regression 高 3.25 个百分点、比 LSTM 高 6.85；TON-IoT 分别高 9.18 和 1.70 个百分点。论文未统一报告 Macro-F1、Balanced Accuracy 或真实 benign FAR。

## 8. 未知检测结果缩译

unknown complexity = 1 时，AE 报告 benign FPR 0.50%、attack FNR 0.58%；complexity = 3 时 FPR 0.92%、FNR 仍约 0.58%。unknown 类不超过 3 时 AUC>0.95，最高约 0.99。复杂度继续增加后，攻击重构误差与 benign 重叠，固定阈值无法同时保持低 FPR 和高 hit rate，AUC 明显下降。

单类复杂度下，CDDRF F1 99.72%、AUC 0.9997；AE F1 97.00%、AUC 0.9891；论文把二者平均成 CAIDS 综合 F1 98.36%。这种跨阶段平均不是 OSCR，也不能表示单个测试流同时被正确分类和拒识。

## 9. 讨论与结论缩译

作者承认 unknown complexity 上升后 AE 拟合和识别能力下降，未来需降低资源成本、加强实时性和对抗鲁棒性。系统的在线 normal 更新还存在污染风险：被误接收为 normal 的攻击会逐步进入 buffer，抬高阈值并扩大漏报。

# 第二部分：独立技术分析

## A. 协议、任务与状态

- 角色：A-未知攻击二阶段基线；状态：`project_mapped`。
- 本地 PDF：`paper/10.1109_TVT.2025.3613343.pdf`。
- 协议：`P0-normal-threshold/P3-target-test-preprocessing`，整体按较差者判 P3。
- 输入：单一 tabular flow features；不是多模态。
- Zotero/Citation Key：pending。

## B. 与严格开放集任务的差异

CAIDS 第一层把偏离 normal 的流量都称 unknown，但 CAEOS 的 unknown 是“非任何已知攻击家族”。已知攻击若先被 AE 拒为 unknown，在 CAEOS 已知恶意分类中必须算错。论文没有明确执行这一联合计分，且把两阶段 F1 平均会掩盖错误路由。

## C. 95%/5%安全门

complexity≤3 的 FPR/FNR 数字看似通过 5% 门槛，但不是 strict-v4 多家族联合 OSR，也未证明五种以上未知类时达标。没有 Known Macro-F1、Unknown AUPR、FPR@95TPR、OSCR、ECE、Brier、NLL。目标测试集独立 PCA/编码进一步削弱结论。

## D. 采纳与实验动作

采纳 normal-only AE＋known-only 95% reconstruction threshold 作为基础异常基线；否决按目标 unknown 重做 PCA、跨阶段平均 F1 和未经防污染的在线更新。

`E-CAIDS-01`：训练折拟合一次预处理器；每个 leave-family-out 场景重新训练但禁止读取 unknown；AE 阈值由 known validation 冻结；CDDRF 和 CAEOS 用同一输入。被 AE 拒绝的 known attack 计入错误，报告六主指标和开放集混淆矩阵。若 complexity 增大后 FPR95 或 OSCR显著恶化，则只保留为低复杂度基线。

## E. 最终审计

- G0-G1、G3-G9：通过。
- G2：DOI 已核，Zotero 待核。
- G10：未通过；最终状态 `project_mapped`。
