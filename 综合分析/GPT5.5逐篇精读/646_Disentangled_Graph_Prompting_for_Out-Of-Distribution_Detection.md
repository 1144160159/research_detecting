# [646] Disentangled Graph Prompting for Out-Of-Distribution Detection

## 1. 基本信息

- 题名：Disentangled Graph Prompting for Out-Of-Distribution Detection
- 中文译名：面向分布外检测的解耦图提示方法
- 年份：2026
- 来源：IEEE Transactions on Knowledge and Data Engineering, Vol. 38, No. 7
- DOI：10.1109/TKDE.2026.3678022
- 作者：Cheng Yang, Yu Hao, Qi Zhang, Chuan Shi
- 代码：BUPT-GAMMA/DGP，本地目录 `source\DGP`
- 任务类型：图级 OOD 检测，即训练阶段只见 ID 图，测试阶段判断图样本是否来自训练分布。
- 正文包状态：未截断。本次理解主要基于 `646.txt` 和本地代码仓库。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：当测试图和训练图来自不同分布时，如何在没有 OOD 样本监督的情况下，让图神经网络更可靠地识别“陌生图”。

作者认为，以往图 OOD 方法多是端到端训练 GNN，并从节点、子图、图或生成过程等角度刻画 ID 模式。但由于训练阶段没有 OOD 图，端到端编码器缺少直接监督，容易把“适合分类的特征”和“适合识别分布边界的特征”混在一起。DGP 的思路是改用“预训练 + 提示”：先用自监督图对比学习训练 GNN 编码器，然后冻结编码器，只学习两个图提示生成器，对输入图的已有边重新赋权。

两个提示视角分别是：

- class-specific prompt：突出能区分 ID 类别的结构模式。
- class-agnostic prompt：突出 ID 图之间共享、但不直接服务类别判别的结构模式。

测试时，DGP 将两个提示图送入冻结 GNN，得到两类表示，再用 Mahalanobis 距离类评分判断 ID/OOD。论文在 10 组图 OOD 数据对上报告：DGP 平均 AUC 相对最佳基线 SEGO 提升 3.63%，相对 fine-tuned GNN 提升 13.65%，并在 8/10 数据集上达到最好结果。

## 3. 论文解决的具体问题

论文解决的是图级分布外检测，不是传统节点异常检测，也不是图分类泛化。形式上，训练集只有来自 `P_ID` 的带标签图，测试图可能来自 `P_ID` 或 `P_OOD`。模型要输出一个检测分数，使 ID 与 OOD 图在分数空间可分。

它针对三个具体困难：

1. OOD 样本训练阶段不可见，无法直接学习“什么是 OOD”。
2. 图结构的 ID 模式不是单一的。某些结构用于区分类别，某些结构是 ID 图共同具有的背景或约束，两者都可能帮助识别 OOD。
3. 预训练 GNN 已经学到较好的结构表征，但直接 fine-tune 可能破坏预训练能力，且对 OOD 检测目标并不一定更优。

因此，DGP 的问题定义可以概括为：如何在冻结预训练图编码器的前提下，通过可学习的图提示把 ID 图的细粒度结构模式显式暴露出来，从而改善图级 OOD 检测。

## 4. 创新点深度提炼

第一，论文把图 OOD 检测放进“预训练 + prompting”范式，而不是继续端到端训练检测器。这个选择很关键：OOD 检测缺少负样本，预训练编码器反而可能比强行监督微调更稳。

第二，DGP 不是学习一个统一 prompt，而是把 ID 模式拆成 class-specific 和 class-agnostic 两个视角。前者由图标签监督，要求提示图仍能预测 ID 类别；后者被约束为接近均匀类别分布，迫使它避开类别判别信息，捕捉跨类别共享的 ID 指纹。

第三，prompt 的作用点落在边权上。它不新建节点、不改写节点特征，而是用 MLP 根据端点节点表示为已有边生成权重。这使方法贴合 GNN message passing，也保持了线性于边数的复杂度。

第四，论文用距离正则防止平凡解。如果 class-specific prompt 只把所有边权都放大，分类损失可能很好，但没有真正筛出关键结构。距离项通过推动提示图表示远离原图表示，鼓励生成器保留“足够但不冗余”的结构。

第五，DGP 的检测阶段丢弃分类 predictor，只保留 prompt generator 和冻结 GNN，再用 Mahalanobis 距离评分。这说明 predictor 是训练 prompt 的工具，而不是最终检测器本身。

## 5. 科学问题与研究假设

核心科学问题是：只利用 ID 图标签，能否把图中的 ID 模式拆解成互补的结构视角，并让冻结预训练 GNN 更适合 OOD 检测？

论文隐含了几条研究假设：

- 预训练 GNN 已经具备可迁移的图结构表征能力，冻结后仍能作为可靠特征空间。
- OOD 图与 ID 图的差异会体现在关键结构模式的缺失、弱化或异常组合上。
- ID 类标签不仅服务分类，也能反向监督“哪些结构是 ID 内部可解释的判别模式”。
- 类别无关的共享结构同样包含 ID 边界信息，不能只看分类相关子结构。
- 对已有边重新赋权足以形成有效 prompt，不必显式增删节点或生成新边。
- Mahalanobis 类距离可以在 prompt 表征空间中度量测试图偏离 ID 分布的程度。

## 6. 科学方法与技术路线

DGP 的技术路线分四步。

1. 预训练编码器  
   用 GCL 或 SimGRACE 自监督训练 GNN 编码器。论文采用 3 层 GIN，隐藏维和输出维为 32，投影头为两层 MLP。完成后冻结编码器参数。

2. 生成两个提示图  
   对输入图先用冻结 GNN 得到节点表示。对每条已有边 `(i, j)`，拼接两个端点表示，输入 MLP，输出边权。两个独立 MLP 分别生成 class-specific prompt graph 和 class-agnostic prompt graph。

3. 用 ID 标签训练提示生成器  
   class-specific 分支经过 GNN 和 predictor 后，要预测真实 ID 类别，用交叉熵约束。class-agnostic 分支则要接近均匀类别分布，使它学习不依赖具体类别的 ID 共享模式。两者合成 disentanglement loss。

4. 用距离正则避免平凡提示  
   论文设计距离项，避免提示图简单复制或全量放大原图结构。最终测试时，两个 prompt 表征分别计算 Mahalanobis 类分数，并用 `gamma` 加权融合。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 10 组 ID/OOD 图数据对，来自 TU datasets 和 OGB，覆盖分子、社交网络、生物信息图。正文中明确出现的例子包括 `BZR-COX2`、`PTC_MR-MUTAG`、`IMDB-M-IMDB-B`，代码中还显式支持 `ogbg-molbbbp+ogbg-molbace`、`ogbg-molfreesolv+ogbg-moltoxcast`、`ogbg-moltox21+ogbg-molsider`。

2. 预处理  
   ID 图按 80%/10%/10% 划分为训练、验证、测试。验证和测试阶段分别混入等量 OOD 图。社交网络无节点/边标签时使用节点度或常量特征；OGB 分子数据使用原始节点特征并转为 float。

3. 模型与基线  
   DGP 使用 GCL 和 SimGRACE 两种预训练编码器，形成 DGP-GCL 与 DGP-SimGRACE。基线包括非图 OOD 方法、预训练 GNN、fine-tuned GNN、图异常检测方法 OCGIN/GLocalKD，以及 GraphDE、GOOD-D、AAGOD、GOODAT、HGOE、SEGO 等图 OOD 方法。

4. 训练  
   先自监督预训练 GNN；再冻结 GNN，训练两个 prompt generator 和 predictor。优化目标包括 class-specific loss、class-agnostic loss 和距离正则。超参数包括 `lambda`、`gamma`、`alpha_1`、`alpha_2`、GNN 学习率和 DGP 学习率。

5. 指标  
   使用 AUC、AUPR、FPR95。AUC/AUPR 越高越好，FPR95 越低越好。

6. 消融/敏感性  
   V0 去掉 class-agnostic 分支，V1 去掉 class-specific 分支，V2 去掉距离正则。另做预训练初始化对比、超参数敏感性、prompt generator MLP 层数分析、效率分析和 prompt 可视化。

7. 结果核查  
   需要检查验证集最佳 epoch、测试 AUC/FPR95/AUPR、ID/OOD 分数分布重叠、随机初始化是否显著退化、prompt 边权是否确实突出不同结构区域。

## 8. 关键结果、结论与证据

论文最重要的结论是：细粒度 ID 模式建模和预训练 prompting 可以互补，且比直接 fine-tune 更适合图 OOD 检测。

主要证据包括：

- 非图 OOD 方法迁移到图数据后平均 AUC 只有 48.95%，说明忽略结构关系会明显失效。
- DGP 相对直接预训练 GNN 平均 AUC 提升 19.86%，相对 fine-tuned GNN 提升 13.65%，相对 AAGOD 提升 13.39%。
- DGP 相对最佳图 OOD 基线 SEGO 平均 AUC 提升 3.63%，并在 8/10 数据集上取得最佳结果。
- 分数分布可视化中，预训练 GNN 的 ID/OOD 平均重叠为 0.69，DGP 降到 0.44，重叠相对减少 35.94%。
- 随机初始化编码器明显差于 GCL/SimGRACE 预训练编码器，说明 DGP 的效果不是 prompt generator 单独带来的。
- 消融实验显示 V0、V1、V2 都弱于完整模型，说明两个分支和距离正则都不是装饰项。
- 效率实验显示 DGP-GCL 训练耗时显著低于若干强基线，例如 BZR-COX2 上约 7.48s，而 SEGO 和 GOOD-D 分别约 353.35s 和 277.23s。

## 9. 局限性与待解决问题

第一，实验仍主要是标准图学习基准，不是网络安全真实日志、攻击链图或威胁情报图。对于安全场景中的时间漂移、对抗规避、低频新型攻击，论文尚未证明有效。

第二，方法依赖 ID 图标签。若安全数据只有正常样本、没有细粒度 ID 类别，class-specific 分支的监督来源需要重新设计。

第三，prompt 只调整已有边权，不生成新边或节点。对于攻击图中“新增异常连接”“跨域跳转边”“罕见通信路径”这类 OOD 信号，单纯重赋权可能不够。

第四，验证集混入 OOD 图用于模型选择和调参。严格部署时，OOD 验证样本往往不可得，因此阈值、超参数和早停策略还需要无 OOD 验证的版本。

第五，Mahalanobis 距离依赖均值/协方差估计，高维小样本或多峰 ID 分布下可能不稳定。论文提到可用聚类，但主设置仍偏简单。

第六，class-agnostic 分支用“预测均匀分布”作为代理目标，这个约束并不唯一。均匀输出可能表示捕捉了共享 ID 指纹，也可能只是 predictor 不确定，二者需要更强解释证据区分。

第七，正文包未截断；不过纯文本里的表格数值没有完整保留逐项明细。如果要写正式综述表或复现实验表，仍建议回到 PDF 核对 Table II 的每个数据集数值。

## 10. 与本项目的关系

这篇论文与“网络安全异常检测”是中相关，价值主要在方法论而非直接场景复用。

可迁移的部分包括：

- 将主机、IP、进程、域名、告警、漏洞、威胁情报实体构造成图，做图级或子图级未知攻击检测。
- 把不同已知攻击族、业务类型或正常行为簇当作 ID 类别，用 class-specific prompt 学习类别判别结构。
- 用 class-agnostic prompt 捕捉“正常网络/正常业务图”共有的结构约束，例如通信拓扑、服务依赖、认证路径。
- 对安全运营有意义的是：prompt 边权可作为解释线索，帮助分析哪些连接、依赖或行为路径导致某个样本被判为 OOD。

但要注意，论文没有在网络流量、APT 图、恶意软件行为图或威胁情报知识图谱上验证。若用于本项目，更适合作为“图表示 + 未知威胁检测”的候选框架，需要重新设计数据切分、时间外推验证和攻击语义解释。

## 11. 代码对照分析

我阅读了 `source\DGP` 的主要源码，论文方法与代码大致对应如下：

- 参数入口：[arguments.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\arguments.py:39>)  
  定义 `lambda_`、`alpha_1`、`alpha_2`、`gamma`、`dgp_lr`、`model_type` 等论文超参数。

- 数据加载：[data_loader.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\data_loader.py:127>)  
  `get_ood_dataset` 负责解析 `--DS_pair`，划分 ID 训练/验证/测试，并拼接 OOD 验证/测试样本。

- 图增强：[aug.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\aug.py:233>)  
  实现 GCL 的 node dropping、edge perturbation、subgraph、mask nodes 和 random augmentation。

- 编码器：[gin.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\gin.py:16>) 与 [wgin_conv.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\My_LA\convs\wgin_conv.py:11>)  
  `Encoder` 是支持 `edge_weight` 的多层 GIN；`WGINConv.message` 中用 `edge_weight` 乘邻居消息，对应论文“通过修改边权生成 prompt graph”。

- DGP-GCL 主入口：[DGP_GCL.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\DGP_GCL.py:19>)  
  `PromptGenerator` 用端点节点表示拼接后输出边权；`DGP` 包含两个 prompt generator 和 predictor；`run_gcl`、`run_gcl_ft`、`run_dgp_gcl` 分别对应预训练、微调基线和 DGP-GCL。

- DGP-Sim 主入口：[DGP_Sim.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\DGP_Sim.py:20>)  
  结构与 GCL 版本类似，但预训练阶段用 SimGRACE 的参数扰动视图。

- 损失与评分：[losses.py](<F:\泉城实验室\二期\论文\异常检测\source\DGP\losses.py:7>)、`DGP_GCL.py`/`DGP_Sim.py` 中的 `ssd` 与 `metric`  
  `ssd` 实现 Mahalanobis 类距离；`metric` 计算 AUC/FPR95/AUPR。`losses.py` 更多是 GCL/InfoMax 相关遗留组件。

复现注意点：

- 当前仓库没有 `data` 和 `DGP_model` 目录，不能直接跑出论文结果，需要先准备 TU/OGB 数据并预训练模型。
- README 的入口是 `python DGP_GCL.py` 和 `python DGP_Sim.py`；但 [run_grid_search.sh](<F:\泉城实验室\二期\论文\异常检测\source\DGP\run_grid_search.sh:44>) 中写成了 `DGP-GCL.py`，文件名与仓库实际文件不一致。
- `DGP_GCL.py` 中测试阶段构造了训练集 prompt 表征，但当前代码路径里没有真正用它计算测试 Mahalanobis 分数；这与论文“相对 ID 训练分布评分”的叙述需要复核。
- `DGP_Sim.py` 的测试评分更接近论文公式，会用训练集 specific/agnostic prompt 表征作为 Mahalanobis 参考。
- `DGP_Sim.py` 中部分训练损失直接对 logits 调用 `nll_loss`/`kl_div`，严格来说应检查是否缺少 `log_softmax`。复现实验前建议先做单批次 loss sanity check。

## 12. 本篇精华

- DGP 的核心不是“再训练一个更强 GNN”，而是冻结预训练 GNN，用边权 prompt 把它引向 OOD 检测任务。
- 论文把 ID 模式拆成 class-specific 与 class-agnostic：一个负责类别判别结构，一个负责跨类别共享结构。
- class-agnostic 分支是本文最有意思的部分，它承认“对分类没用的信息”可能对 OOD 边界很有用。
- 距离正则解决 prompt 学习的平凡解问题，否则生成器可能把所有边都放大而不形成真正结构选择。
- 实验结论支持 prompting 优于 fine-tuning，尤其是在 OOD 负样本缺失时，保留预训练结构空间更稳。
- 对安全异常检测的启发是：未知威胁不一定要直接建模，可以先建模“已知正常/已知攻击图的多视角结构边界”。
- 代码能帮助理解方法，但不是完全无坑的复现工程，Mahalanobis 评分路径和脚本文件名需要特别核查。

## 13. 建议精读路线

1. 先读 Section III 的问题定义和 Mahalanobis scoring，明确论文到底在做图级 OOD，而不是节点异常检测。
2. 再读 Fig. 2 和 Section IV-B，理解 prompt graph generator 为什么作用在边权上。
3. 重点精读 Section IV-C：class-specific loss、class-agnostic loss、distance loss 是整篇论文的核心。
4. 读实验设置时关注数据划分：训练只用 ID，验证/测试混入等量 OOD，这会影响部署解释。
5. 看消融实验优先于看总表：V0/V1/V2 能证明两个分支和距离正则各自的必要性。
6. 最后对照代码读 `DGP_GCL.py`、`DGP_Sim.py`、`data_loader.py`、`gin.py`，确认论文公式如何落到边权、冻结编码器和 Mahalanobis 评分。

<!-- codex-cli-deep-read: complete -->
