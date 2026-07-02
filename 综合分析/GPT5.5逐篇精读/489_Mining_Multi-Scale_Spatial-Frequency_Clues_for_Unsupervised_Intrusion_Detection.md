# [489] Mining Multi-Scale Spatial-Frequency Clues for Unsupervised Intrusion Detection

## 1. 基本信息

- 编号：489
- 中文题名：面向无监督入侵检测的多尺度空间-频率线索挖掘
- 年份与来源：2025，IEEE Transactions on Information Forensics and Security，Vol. 20
- DOI：10.1109/TIFS.2025.3620090
- 任务类型：无监督网络入侵检测，重点是未知攻击、动态图流量、低误报检测
- 核心方法：MSF-IDS，由多尺度频率编码器、NAPH 空间拓扑编码器、自监督表示增强器、无监督聚类检测器组成
- 代码状态：本地已下载，目录为 `source\MSF-IDS`
- 正文包状态：未截断；但正文缓存中若干表格单元格没有完整保留，精确表格数值仍建议回 PDF 复核

## 2. 中文翻译与核心摘要

这篇论文讨论的是：在没有流量标签的情况下，如何利用网络流量特征和通信拓扑识别未知攻击，同时把误报率降下来。作者认为，现有 GCN 类无监督入侵检测模型虽然能融合流量特征与拓扑，但由于本质上偏低通滤波，会压掉攻击流量中有区分度的高频信息；同时，单尺度邻域聚合会让正常与异常表示越来越相似，导致高 FPR。

论文提出 MSF-IDS。频率侧用 Daubechies 小波和 Beta 图小波保留多尺度频率信号；空间侧提出 NAPH，把持续同调引入动态网络，通过时间过滤、局部子图、持久图和持久热力图提取可学习的拓扑表示；随后用自监督双视图增强和自表达/子空间聚类检测器突出攻击相关信息。实验覆盖二分类、多分类、在线检测、消融、可视化和复杂度分析，主张 MSF-IDS 能显著降低 GCN-based UNIDS 的误报率并提升 F1/AUC。

## 3. 论文解决的具体问题

论文真正抓住的问题不是“再做一个无监督 IDS”，而是 GCN 无监督 IDS 的高误报瓶颈。作者举例：AGNN 在 CIC-ToN-IoT 上 F1 达 88.48%，但 FPR 为 21.33%；SOM-DAGMM F1 只有 78.13%，FPR 却较低，为 15.88%。更尖锐的是，监督版 3D-IDS 的 FPR 仅 3.27%，但把分类器换成无监督聚类后 FPR 上升到 19.37%。

作者把原因归结为两个层面：

- 频率层面：攻击流量的频谱分布相对正常流量有明显右移，高频成分是区分异常的重要证据；传统 GCN 低通聚合会把这些高频攻击线索滤掉。
- 空间层面：随着 GCN 层数增加，表示进一步趋同，熵和 FPR 上升，MSE 下降，说明正常与攻击表示被混在一起。

所以论文的核心问题可以概括为：如何在无标签、动态图、网络规模较大的流量场景中，同时保留多尺度频率差异和多尺度拓扑差异，从而降低误报率。

## 4. 创新点深度提炼

1. 高 FPR 归因比较清晰。论文不是只报告 GCN 表现差，而是从频谱右移、GCN 后左移、层数加深导致表示趋同三个角度解释误报来源。

2. 频率编码器把异常检测中的“高频异常线索”具体化。Daubechies 小波用于快速提取/压缩多尺度信息，Beta 图小波覆盖不同频段，避免单一低通图卷积把攻击信息抹平。

3. NAPH 是论文最有辨识度的部分。它把持续同调从静态点云扩展到动态网络：用时间过滤构造嵌套复形，用局部 k-hop 子图控制规模，再把 persistence diagram 转换成 heatmap，使拓扑特征可以进入深度模型。

4. 自监督增强器服务于“无标签可分性”。双视图扰动和对比式一致性损失让表示对真实噪声更稳健；自表达矩阵和子空间聚类再把潜在簇结构显式化。

5. 论文不只做离线实验，还讨论在线部署。20% 流量作为在线流式检测，离线模型周期性更新在线检测器，体现了实际 IDS 中“性能-成本”折中。

## 5. 科学问题与研究假设

科学问题：无监督 IDS 中，攻击与正常流量的差异是否主要隐藏在单尺度 GCN 容易丢失的空间-频率结构里？

研究假设：

- H1：攻击流量包含更多高频特征模式，低通 GCN 会削弱这些模式。
- H2：单尺度拓扑聚合会造成过平滑，使正常与异常流量表示趋同。
- H3：动态网络中的攻击会改变局部拓扑的持久性结构，持续同调可以捕捉这类多尺度空间异常。
- H4：即使没有标签，双视图自监督和子空间聚类也能把攻击相关表示从噪声中凸显出来。
- H5：只要 NAPH 控制在局部子图和热力图表示上，持续同调可以扩展到较大规模网络流量。

## 6. 科学方法与技术路线

整体输入是网络拓扑 `G` 和流量特征 `F_ij`，输出是流量类型或异常簇。技术路线如下：

1. 频率编码：先用 Daubechies 小波处理原始流量特征，再用一组 Beta 图小波覆盖不同频段，最后把多尺度频率特征与原始特征拼接。
2. 空间编码：对目标节点构造时间过滤下的局部动态子网；使用 GUDHI 类持续同调流程得到 birth-death 拓扑摘要；再转成持久热力图并 flatten 为可学习向量。
3. 动态节点表示：借鉴 TGN 思路，用节点历史记忆和当前消息更新动态节点表示。
4. 自监督增强：随机删边/特征 mask 得到双视图，用相似性约束拉近同一节点不同视图、拉远负样本。
5. 无监督检测：先学习自表达相似矩阵，再用 MLP 输出 membership，经子空间聚类逻辑得到类别分配。
6. 部署思路：离线模型定期重训，在线检测器在短时间窗口内增量检测，减少频繁重训成本。

## 7. 实验设计与实验步骤

可复核流程应按以下顺序走：

1. 数据：使用 CIC-ToN-IoT、CIC-BoT-IoT、NF-UQ-NIDS、NF-UNSW-NB15-v2、NF-BoT-IoT-v2。论文给出的规模从约 239 万到 3776 万流不等，且类别极不均衡，例如 NF-BoT-IoT-v2 中攻击占 99.64%，良性仅 0.36%。

2. 预处理：过滤无效 IP/端口；将源/目的 IP 与端口编码成节点；时间戳排序并归一化；流量字段做 min-max 归一化；按攻击类型适当采样缓解不均衡；保存为 PyTorch Geometric `TemporalData`。

3. 模型与基线：MSF-IDS 对比 9 个基线，包括 EULER、AGNN、ClenshawGCN、APPNP、GmapAD、AGC、DSVD、OmniAnomaly、SOM-DAGMM。多分类实验选 AGNN、APPNP、AGC 三个代表基线。

4. 训练配置：Beta 小波尺度参数 `C=4`；NAPH 邻居跳数为 2，最大邻居采样 1024；Adam 优化器，weight decay 为 `1e-5`；训练不超过 100 epoch；硬件为 Intel Xeon Gold 6330、RTX A40/A100。

5. 指标：二分类主要看 F1-score 和 ROC-AUC；论文讨论中还重点看 FPR。在线检测报告 F1、AUC、FPR，也提到 NMI。

6. 消融/敏感性：移除频率编码器、Daubechies 小波、NAPH、自监督增强器、子空间聚类检测器；改变 Beta、drop feature rate、表示维度 64/128/256，观察 F1 与 FPR。

7. 结果核查：除了看平均 F1/AUC，还必须核查 FPR 是否真的下降；尤其要复核混淆矩阵、正负类定义、采样比例和标签对齐方式，因为无监督聚类结果需要映射到真实标签后才能算 F1/FPR。

## 8. 关键结果、结论与证据

论文的主结论是：多尺度空间-频率线索能降低 GCN-based UNIDS 的误报率。

关键证据包括：

- 动机实验中，GCN 类方法有较高 FPR；监督 3D-IDS 转为无监督后 FPR 从 3.27% 上升到 19.37%，说明无监督设定下误报是主要瓶颈。
- 二分类中，MSF-IDS 在 5 个数据集上整体优于 9 个基线。相比 EULER，MSF-IDS 在 CIC-ToN-IoT 上 F1 提升 5.50 个点；相比 SOM-DAGMM，在 NF-UNSW-NB15-v2 上 F1 提升 1.84 个点，AUC 提升 26.39 个点。
- 多分类中，MSF-IDS 的 F1 增益为 18.85% 到 88.30%；在 CIC-ToN-IoT 上比 AGNN 高 9.03 个点。FPR 在三个数据集上最低，降幅为 28.75% 到 54.78%；CIC-ToN-IoT 上 FPR 低至 6.71%。
- 在线检测中，相比 EULER，MSF-IDS 的 F1 提升 27.16 个点，AUC 提升 32.69 个点，FPR 低 4.60 个点。
- 时间成本上，10000 条在线流量检测耗时 10.98s，而离线检测含重训为 878.73s；NAPH 对 10000 个流量节点计算约 0.78s。
- 消融显示，自监督增强器最关键，移除后 F1 下降 14.48 个点；完整模型在 CIC-ToN-IoT 上 F1 为 92.22%，且 FPR 最低。

## 9. 局限性与待解决问题

1. 正文包未截断，但若干表格单元格在纯文本缓存中没有完整呈现，尤其 Table III、VI、VII 的具体数值需要回 PDF 或原表复核。

2. 正文多次引用 supplementary appendix，例如威胁模型、证明、更多频谱分析、实现细节、数据集细节和超参敏感性；本次正文包未包含这些补充材料，严格复现仍需查看补充文件。

3. NAPH 的“可微/端到端”表述需要谨慎。论文称其可接入端到端深度模型，但代码里持续同调主要通过 GUDHI 和 Persim 生成固定 heatmap 特征，更像可学习模型的输入/教师线索，而不是常规意义上对 birth-death 过程全链路反传。

4. 数据极不均衡，论文使用采样、重加权或过采样思路缓解，但真实部署中良性/攻击比例漂移会影响 FPR 和阈值选择。

5. 在线性能仍弱于离线，作者也承认需进一步缩小 offline-online gap。

6. 代码发布更偏研究原型：存在硬编码路径、requirements 不完整、部分数据保存语句被注释、指标公式需复核等问题。

7. 对小样本、少样本未知攻击的适应仍是未来工作，论文结论最后也明确提到 few-shot/small-sample UNIDS。

## 10. 与本项目的关系

这篇论文与“异常检测/网络异常检测”方向强相关，价值主要在三点：

- 可作为无监督网络入侵检测综述中的高 FPR 问题代表论文。它把 GCN 过平滑、频率低通和误报率联系起来，适合放在“图学习 IDS 的局限”部分。
- 可作为动态拓扑异常检测方法参考。NAPH 提供了把持续同调用于动态网络流的思路，适合扩展到 IoT、工业控制、移动网络、AIOps 通信图等场景。
- 可作为本项目的强基线或模块来源。若项目已有流量图构建流程，可以单独试验频率特征增强、NAPH heatmap、双视图自监督增强这三个组件，看哪个最能降低误报。

## 11. 代码对照分析

代码主线与论文模块大致对应，但不是完全“一键论文复现”。

- 运行入口：离线检测在 [main_Intrusion Detector.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/main_Intrusion Detector.py:347>)；在线检测在 [main_Intrusion Detector Online.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/main_Intrusion Detector Online.py:475>)。
- 参数与模型装配：[options.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/options.py:29>) 定义 `dataroot`、batch size、drop feature rate、embedding dim、TGNMemory、LastNeighborLoader 和 ClusterModel。
- 数据预处理：[datasets_CIC.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/Data/datasets_CIC.py:42>) 与 [datasets_NF.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/Data/datasets_NF.py:46>) 负责 CSV 清洗、IP+端口编码、时间排序、归一化、采样和 `TemporalData` 构造。
- 频率编码：[Frequency Encoder.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/Spatial-Frequency Encoders/Frequency Encoder.py:13>) 实现图拉普拉斯特征值、Beta wavelet、Daubechies wavelet，并把频率特征拼到 `data.msg`；但它是独立预处理脚本，主训练脚本默认读取已处理 `.pt`。
- NAPH 空间编码：[Spatial Encoder_NAPH.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/Spatial-Frequency Encoders/Spatial Encoder_NAPH.py:75>) 和 [utils/ph_cc.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/utils/ph_cc.py:212>) 使用 `k_hop_subgraph`、`gudhi.SimplexTree`、`PersistenceImager` 生成 PH heatmap 特征。
- 自监督增强与检测：[SEComm.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/Self_Supervised_Representation_Augmentor/SEComm.py:27>) 中有 `MergeLayer` 对比损失、`drop_feature`、`SelfExpr` 自表达矩阵和 `ClusterModel` softmax 聚类头。
- NAPH GUI：[app.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/NAPH_source codes/app.py:37>) 调用 [main_new.py](</F:/泉城实验室/二期/论文/异常检测/source/MSF-IDS/NAPH_source codes/utils/main_new.py:30>)，上传 CSV 后生成网络图、barcode、persistent diagram、heatmap 和扁平张量。
- 复现注意：`requirements.txt` 只列了部分依赖；源码中还使用 `PyQt5`、`z3`、`munkres`、`torch_scatter`、`line_profiler` 等。主脚本中预训练停止、SE 层迭代和聚类评估会读取标签用于判断或映射，若要严格无监督复现，需要去掉这些标签驱动选择，只保留最终评估用标签。

## 12. 本篇精华

1. 论文最重要的洞察是：GCN-based UNIDS 的高 FPR 不是偶然，而是低通滤波和单尺度拓扑聚合共同导致的表示混淆。
2. 攻击流量在频谱上更偏高频，保留高频并不是噪声放大，而是异常检测中的判别信息保留。
3. NAPH 的价值在于把动态流量图转为可学习的拓扑摘要，使“拓扑异常”不再只是邻接矩阵聚合。
4. MSF-IDS 的性能提升来自组合效应：频率多尺度、拓扑多尺度、自监督增强、子空间聚类缺一都会退化。
5. 误报率应成为无监督 IDS 的主指标之一，只看 F1/AUC 容易掩盖实际部署成本。
6. 在线-离线混合部署是本文很实用的部分：在线检测负责低成本响应，离线周期更新负责性能恢复。
7. 代码可参考模块设计，但直接复现实验前必须清理硬编码路径、补全依赖、核查 FPR 公式和标签使用位置。

## 13. 建议精读路线

1. 先读 Introduction 的 Fig. 2 逻辑：理解高频右移、GCN 左移、层数加深导致 FPR 上升，这是全篇动机。
2. 再读 Model 的频率编码器：重点看 Daubechies + Beta wavelet 如何对应“保留多尺度频率”。
3. 精读 NAPH 的 Definition 6-8：时间过滤、NATA、persistent heatmap 是论文与普通图 IDS 拉开差异的核心。
4. 接着读自监督增强器和检测器：把 Eq. 14-17 与代码中的 `MergeLayer`、`SelfExpr`、`ClusterModel` 对起来。
5. 实验部分优先看二分类、多分类、在线检测和消融，不必先纠结所有表格细节。
6. 最后回到代码，按 `Data -> Frequency Encoder -> ph_cc/NAPH -> main -> SEComm` 的顺序读，能最快判断哪些模块可迁移到自己的异常检测项目中。

<!-- codex-cli-deep-read: complete -->
