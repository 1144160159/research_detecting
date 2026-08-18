# 095 两阶段自适应 OOD 加密流量分类网络 / TAO-Net

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖

| 原文章节 | 本卡位置 | 状态 |
|---|---|---|
| Highlights / Abstract / Introduction | 第 2 至 3 节 | 已覆盖 |
| 2 Related Work / 3 Preliminaries | 第 4 至 5 节 | 已覆盖 |
| 4 Proposed Method | 第 6 至 10 节 | 已覆盖 |
| 5 Experiments | 第 11 至 14 节 | 已覆盖 |
| 6 Analyses / 7 Conclusion | 第 15 至 17 节 | 已覆盖 |

## 1. 文献身份

- 标题：TAO-Net: Two-stage Adaptive OOD Classification Network for Fine-grained Encrypted Traffic Classification。
- 作者：Zihao Wang、Wei Peng、Junming Zhang、Jian Li、Wenxin Fang。
- 版本：arXiv:2512.15753v1，2025 年 12 月 11 日，Elsevier 投稿预印本。
- 任务：先区分 ID/OOD，再分别用 Transformer 和 GPT-4o 输出具体应用标签。
- 方法定位：目标 OOD 标签空间已知的两阶段路由分类；不是严格 unknown-blind 开放集识别。

## 2. 摘要缩译

传统加密流量分类器只能处理预定义应用，新应用出现后通常被归为一个 Other 类。TAO-Net 第一阶段融合 PCA residual 与网络层间 transformation smoothness 区分 ID/OOD；第二阶段对 ID 使用 Transformer，对 OOD 使用 GPT-4o 和 Semantic-enhanced Prompt Strategy（SPS）生成具体应用名称。

论文在 CHNAPP、ISCXVPN、ISCXTor 上报告 Macro Precision 96.81% 至 97.70%、Macro-F1 96.77% 至 97.68%。

## 3. 引言缩译

作者把新应用、新加密方式和协议更新视为 OOD。单一 unknown 标签不能告诉管理员具体业务名称，因此提出“检测后生成标签”的两阶段结构。SPS 设置 Strict、Complete、Extended 三种 prompt，逐步扩大候选标签和跨数据集知识范围。

论文声称 OOD branch 不依赖预定义标签，但 Strict/Complete prompt 实际列出目标 OOD 或全部数据集标签，这一说法与实验实现不一致。

## 4. 相关工作缩译

论文回顾手工统计、CNN/RNN/Transformer、PacRep、ET-BERT，以及 MSP、ODIN、Mahalanobis、PCA residual 和 inter-layer smoothness OOD score。生成分类部分回顾 BERT、BART、T5、ChatGLM、LLaMA 与 GPT-4。

TAO-Net 的技术组合不是新流量 encoder，而是 OOD router、专用 ID classifier、外部 LLM 和 prompt label prior。

## 5. 问题定义

令 ID 与 OOD 标签集合分别为 Yᴵᴰ 和 Yᴼᴼᴰ，学习：

> ϕᴵᴰ: M → Yᴵᴰ。

> ϕᴼᴼᴰ: M → Yᴼᴼᴰ。

这里 Yᴼᴼᴰ 在实验中不是无界开放空间，而是数据集预先划出的 2 或 4 个具体应用类别。

## 6. 总体流程

第一阶段计算 hybrid OOD score S(X)，若 S(X) > δ 则路由到 GPT-4o，否则路由到 ID Transformer。第二阶段输出具体类别，而不是 unknown 标记。

这意味着最终性能同时受 OOD routing error、ID classifier error 与 LLM label generation error 影响，但论文主表没有分别报告三者。

## 7. LSTM 与 PCA residual

LSTM 对 token sequence 提取最终 hidden state：

> ϕ(Xᵢ) = hⱼ。

只用 ID training features 计算均值与 covariance：

> C = (1 ÷ N)Σᵢ[ϕ(Xᵢ) − μ][ϕ(Xᵢ) − μ]ᵀ。

按累计解释方差 γ 选择前 k 个 eigenvectors 为 principal subspace P，其余组成 residual subspace R：

> k = min{m ∣ Σᵢ₌₁…ₘλᵢ ÷ Σⱼλⱼ ≥ γ}。

Residual score 为：

> s₁(X) = ‖Pᴿϕ(X)‖₂。

## 8. Inter-layer Smoothness 与混合分数

层间变化 score 为：

> s₂(X) = Σₗ₌₁…ᴸ ‖Fₗ(X) − Fₗ₋₁(X)‖₂。

混合风险为：

> S(X) = αs₁(X) + (1 − α)s₂(X)。

决策为：

> OOD，当 S(X) > δ；否则 ID。

原文设 α = 0.6、δ = 0.75，但没有给出 score normalization、跨数据集尺度对齐，也未证明 δ 仅由 known validation 决定。

## 9. ID 分类支路

ID 流量进入 Transformer，利用 hidden states 做 scaled dot-product attention：

> A = Softmax(QKᵀ ÷ √dₖ)V。

最终类别分布：

> P(y ∣ X) = Softmax(WA + b)。

该支路只学习 ID classes。

## 10. OOD 生成与 SPS

GPT-4o 自回归输出 label tokens：

> P(ŷ ∣ X) = ∏ₜP(ŷₜ ∣ X, ŷ₍₍ₜ₎₎前)。

三种 SPS：

- Strict：prompt 只列当前实验的目标 OOD labels，生成空间最窄。
- Complete：列出当前数据集 ID 与 OOD 全部 labels。
- Extended：再加入其他数据集全部 labels。

主结果采用 Strict，等价于向模型显式提供真实目标未知候选集合，并非真正从无界开放空间发现新类别。

## 11. 数据与划分

| 数据集 | ID 类 | OOD 类 | Train | Validation | Test |
|---|---:|---:|---:|---:|---:|
| CHNAPP | 4 | 2 | 485,782 | 64,391 | 64,392 |
| ISCXVPN | 9 | 4 | 443,337 | 24,631 | 24,630 |
| ISCXTor | 8 | 4 | 450,001 | 82,287 | 82,287 |

Train 只含 ID；validation 和 test 均含 ID/OOD，比例 7:3。类别划分固定一次：例如 CHNAPP 把 WeChat/Weibo 作为 OOD；ISCXVPN 把 VoipBuster/YouTube/Vimeo/Spotify 作为 OOD。

未报告 capture/group isolation，也没有多个 leave-family-out scenarios。

## 12. 训练设置与基线

- OOD detector：Adam、learning rate 2 × 10⁻⁵、20 epochs、BCEWithLogitsLoss。
- ID branch：AdamW、learning rate 2 × 10⁻⁵、30 epochs。
- α = 0.6、δ = 0.75。
- GPT-4o：temperature 0.7、top-p 0.95。
- RTX 4090、seed 42，声称 5 次 independent runs 的均值和标准差，但主表只列单个小数结果，没有标准差。
- 基线：PacRep、ET-BERT、BERT/BART/T5、ChatGLM-3、LLaMA-3、GPT-4o。

基线任务并不完全等价：PacRep/ET-BERT 没有 OOD label generator，被迫把 OOD 归入 ID；GPT-4o 获得 label prompt；TAO-Net 又获得 oracle-like router 结构。

## 13. 指标与主结果

只报告 Macro Precision、Macro-F1、Micro-F1、Recall，没有单独 OOD detection AUROC/AUPR/FPR95，也没有 routing confusion matrix、Known Acceptance、Unknown Rejection 或 OSCR。

| 模型 | CHNAPP Macro-F1 | ISCXVPN Macro-F1 | ISCXTor Macro-F1 |
|---|---:|---:|---:|
| PacRep | 56.88% | 57.49% | 58.41% |
| ET-BERT | 54.12% | 60.47% | 58.29% |
| GPT-4o | 86.31% | 83.76% | 85.13% |
| TAO-Net | 96.77% | 96.83% | 97.68% |

TAO-Net 的高分是 ID 与预先命名 OOD 类别的联合多分类结果，不是 unknown rejection 成绩。

## 14. 消融与 SPS

PacRep baseline、OOD detector＋PacRep、OOD detector＋GPT-4o、full TAO-Net 的 Macro-F1 依次提高。Full 模型在三个数据集均最高，但 ablation 没有单独移除 residual 或 smoothness，也没有 α/δ known-only sensitivity。

Strict SPS 最强：CHNAPP 96.77%、ISCXVPN 96.83%、ISCXTor 97.68% Macro-F1。Complete 和 Extended 扩大标签集合后下降约 3 至 5 个百分点，直接说明性能依赖候选标签收窄。

## 15. 关键矛盾

论文称无需 predefined labels 识别 emerging applications，但：

1. OOD classes 在数据集划分时已知。
2. Validation 含同一批 target OOD。
3. Strict prompt 明确列出 target OOD labels。
4. 评价只接受这些预先定义的字符串标签。

因此该任务更准确地称为 target-category-aware zero-shot routing classification，而非 open-world category discovery。

## 16. 局限缩译与补充

原文承认 prompt label space 扩大后 precision 下降，未来需要更自适应 threshold 和更强 OOD classification。没有讨论 GPT-4o 版本漂移、API nondeterminism、数据隐私、成本、prompt injection、不可访问网络环境或恶意应用名称先验缺失。

## 17. 结论缩译

TAO-Net 展示了 OOD router 与 LLM label prior 可以在固定目标类别集合上获得高联合分类分数。它没有证明严格未知攻击拒识，也没有证明无需目标未知信息进行 threshold、prompt 或模型选择。

# 第二部分：独立技术分析

## A. 一句话结论

TAO-Net 不可进入 CAEOS P0 strict 主表；其 detector 组件可在 known-only 条件下重实现，但论文主结果属于 `P2-target-OOD-validation-and-label-prompt-exposure`，高达 97% 的 Macro-F1 不能作为严格开放集 SOTA 对照。

## B. 两条交付线映射

### 工程线

只移植 PCA residual、inter-layer smoothness 与 hybrid score。α、normalization、δ 必须完全用 known validation 冻结；GPT-4o branch 不进入安全验收主线。

### 论文线

把原 TAO-Net 放入 P2 exposure 表；另实现 `TAO-detector-strict` 作为组件消融。不得复用原文 96% 至 97% 联合分类结果作为 P0 baseline。

## C. 协议审计

- Train：只含 ID，表面为 P0。
- Validation：明确含 30% target OOD，threshold/hyperparameters 来源不透明。
- Prompt：Strict 直接注入 Yᴼᴼᴰ 标签集合。
- Test：与 validation 使用同一 OOD categories。
- Model selection：Strict/Complete/Extended 用 target test/validation 结果比较并宣称 Strict 最优。
- Seeds：声称 5 runs，但主表无 mean±std。
- Protocol：`P2-target-OOD-validation-and-label-prompt-exposure/P3-threshold-selection-unclear`。

## D. 与 CAEOS 任务差异

CAEOS 要求输出 known benign、known malicious family 或 unknown/reject。TAO-Net 在 router 判 OOD 后仍必须把样本归入已知候选 OOD application name，因此没有 unknown rejection 终态。

对于真正新恶意家族，名称可能从未出现在 GPT pretraining 或 prompt 中，且流量特征不能唯一推出品牌/家族名称。LLM 输出一个具体名称可能制造高风险假确定性。

## E. 指标审计

Macro-F1 把 ID 与 target OOD labels 一起平均，无法回答 detector 是否正确。至少应拆出：

- ID routing TPR 与 ID classification Macro-F1。
- OOD routing AUROC、AUPR、FPR95、threshold confusion。
- OOD label generation accuracy，条件于正确 routing。
- end-to-end OSCR/OpenAUC 与 abstention rate。

原文四项 aggregate classification metrics 不足以支撑开放集安全结论。

## F. 95%/5% 验收

原文 aggregate Macro-F1 超过 95%，但不是 Known Macro-F1；没有 Benign FAR，也没有 known-only threshold 下的 Known Acceptance。δ = 0.75 无法解释为 95% quantile。

所以 TAO-Net 没有证明通过任何 CAEOS 95%/5% 门。

## G. SPS 的反事实判断

Strict 优于 Complete/Extended，说明性能主要来自收窄 candidate label set，而非开放世界生成能力。真正开放环境标签集合扩大时，结果按论文自身证据会下降。

应增加：不给 OOD label names、使用错误候选列表、加入同义/新名称、加入完全未见恶意家族的反事实实验。

## H. 采纳与否决

### 采纳

- PCA residual score。
- Inter-layer smoothness score。
- 两者在冻结 normalization 后的 hybrid ablation。
- ID/OOD 路由与后续分类分阶段评价。

### 有条件采纳

- LLM 只作 analyst suggestion，不作为无拒识终态。
- Prompt 必须标记候选标签暴露等级。
- API model/version/prompt/temperature 固定并缓存输出。

### 不采纳

- 不把 Strict SPS 称为无预定义标签发现。
- 不用 target OOD validation 选 δ。
- 不把 aggregate Macro-F1 当 unknown detection 指标。
- 不把 GPT-4o 输出名称视为可验证恶意家族证据。
- 不把不等价 baseline 的低分解释为 TAO detector 优势。

## I. CAEOS 可执行实验

1. `E-TAO-01`：PCA residual、smoothness、hybrid 三项，known-only calibration。
2. `E-TAO-02`：δ 取 known 95% acceptance quantile，不使用 target unknown。
3. `E-TAO-03`：分别报告 routing、known classification、conditional OOD naming。
4. `E-TAO-04`：Strict label prompt、无 label prompt、错误 label prompt。
5. `E-TAO-05`：TAO score 对 Energy、k-LND3、Mahalanobis、CAEOS risk。
6. `E-TAO-06`：多个 leave-family-out scenarios 与 5 seeds。
7. `E-TAO-07`：LLM abstain 与 evidence-grounded verification。
8. `E-TAO-08`：离线缓存 GPT 输出，报告成本、延迟和版本。

## J. 可引用与不可引用主张

### 可引用

- TAO-Net 组合 PCA residual 与 inter-layer smoothness。
- 它把 ID 交给 Transformer、OOD 交给 GPT-4o。
- Strict SPS 明确限制为目标 OOD labels，且优于更大 label space。
- 固定数据集标签空间下联合 Macro-F1 达 96.77% 至 97.68%。

### 不可引用

- TAO-Net 无需预定义未知标签。
- 其 97% Macro-F1 是严格 unknown-blind OSR 结果。
- δ 只由 known validation 选择。
- GPT-4o 能从流量自主发现任意新应用或恶意家族。
- TAO-Net 已满足 95%/5% 安全门。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地全文抽取存在
- G2 身份门：通过至 arXiv 预印本，正式发表与 Zotero 待办
- G3 任务门：通过，target-label routing 与 strict OSR 已区分
- G4 协议门：通过，`P2-target-OOD-validation-and-label-prompt-exposure/P3-threshold-selection-unclear`
- G5 方法门：通过
- G6 结果门：通过，表 2 至 5、消融与 SPS 已核读
- G7 对比门：通过，不等价 baseline 已标注
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
