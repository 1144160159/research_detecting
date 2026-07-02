# [793] Robust Malicious Network Traffic Detection Framework With Automated Drift Detection, Identification, and Adaptation

## 1. 基本信息

论文：Robust Malicious Network Traffic Detection Framework With Automated Drift Detection, Identification, and Adaptation  
中文可译为：面向自动漂移检测、识别与适配的鲁棒恶意网络流量检测框架。

作者：Xueying Han, Jian Qin, Changzhi Zhao 等。  
年份与来源：2026，IEEE Transactions on Information Forensics and Security。  
DOI：10.1109/TIFS.2026.3694664。  
主题：恶意流量检测、概念漂移、对比学习、漂移识别、模型自适应。  
本地正文：`综合分析\_data\full_text_cache_plain\793.txt`，正文包未截断。  
本地代码：`source\Argus`，仓库名 Argus。

## 2. 中文翻译与核心摘要

这篇论文的核心不是再做一个静态恶意流量分类器，而是提出一个面向动态网络环境的闭环检测框架 Argus：先对已知分布流量做准确分类，同时识别偏离训练分布的漂移流量；再自动判断漂移流量是正常演化还是恶意攻击；最后把新流量纳入模型更新，尽量在学习新模式时不忘掉旧知识。

Argus 的关键路径是：会话级特征抽取，分别建模统计特征和行为序列特征；用自编码器加对比学习形成紧凑的类内表示；用“最近类的重构损失分布”而不是全局阈值判断漂移；对漂移样本，用特征空间聚类和 IP 交互图密度判断恶意性；模型更新时加入距离约束，避免更新过程把旧类表示空间冲散。

论文声称 Argus 在多种漂移场景下平均 F1 超过 95%，极端漂移下 F1 仍有 88.22%，漂移识别模块无需人工介入且准确率稳定超过 97%。

## 3. 论文解决的具体问题

传统恶意流量检测默认训练集和测试集满足静态 i.i.d. 分布，但真实网络里这个假设很脆弱。正常业务会变化，用户行为会变化，攻击工具、攻击目标和攻击手法也会变化，导致测试时的流量分布偏离训练时分布，即概念漂移。

论文指出现有路线各有缺口：周期性重训需要大量新标注数据；鲁棒特征或预训练方法通常只能抗轻微扰动；漂移检测方法能报警但不能自动判断漂移流量是否恶意，仍然把大量工作留给安全运营人员。Argus 试图解决的具体问题是：在无实时标签的在线流量中，同时完成已知类分类、未知漂移发现、漂移恶意性识别和持续适配。

## 4. 创新点深度提炼

第一，Argus 把“检测恶意流量”和“处理概念漂移”做成闭环，而不是只做分类或只做漂移报警。论文明确拆成分类与漂移检测、漂移识别、模型适配三个连续问题。

第二，ACLearner 把自编码器和对比学习结合起来。自编码器提供重构误差，对比学习让同类样本更紧凑、异类样本更分离。它不是直接用粗粒度 normal/malicious 标签，而是先在正常和恶意内部预聚类，形成更细的训练类。

第三，漂移检测采用“最近类条件重构损失”。样本先在 latent 空间找到最近类中心，再看它的重构损失是否落在该类的分布范围内。这个设计比全局重构误差更细，也比单纯距离阈值更稳定。

第四，漂移识别利用双空间假设：恶意漂移通常在特征空间集中，同时在物理空间呈现较密集的主机交互；正常漂移可能在特征上相似，但参与主机更分散。代码中对应 DBSCAN 聚类加 NetworkX 多重图密度判定。

第五，模型适配不是简单增量训练。non-drifting 数据更新时约束新旧 latent 表示距离；drifting 数据更新时约束旧样本到旧类中心距离的变化，从而给新类留出表达空间，同时保护旧类结构。

## 5. 科学问题与研究假设

科学问题一：如何在无在线标签的情况下区分“已知分布内流量”和“未知漂移流量”？  
假设：如果类表示足够紧凑，则样本对最近类的重构损失能反映它是否真正属于该类。

科学问题二：漂移流量是否能自动判定恶意性？  
假设：恶意活动由明确攻击目标驱动，更容易在特征空间和主机交互空间同时形成密集结构；正常业务变化则更分散。

科学问题三：模型能否在持续更新中保留旧知识？  
假设：通过历史数据回放和 latent 空间距离约束，可以降低灾难性遗忘，同时吸收新流量模式。

科学问题四：统计特征和行为序列特征是否互补？  
假设：统计特征捕获整体流量属性，行为序列特征捕获包长和方向的交互模式，两者 bagging 能降低单一特征失效风险。

## 6. 科学方法与技术路线

Argus 部署在核心交换机镜像口，覆盖南北向和东西向流量。处理单元是会话，即五元组相同的一组包。论文假设离线训练阶段有带标签正常/恶意数据，在线阶段面对连续无标签流。

技术路线如下：

1. 特征抽取：统计特征包括包数、字节数、包长统计、包间隔、TCP flag 等；行为特征包括包长序列和方向序列。代码中统计特征是 23 维，行为特征被组织成 `2 x sequence_length` 的方向分离包长矩阵，默认长度 50。
2. 预聚类：用较粗的 `ngram`/包长桶特征对正常和恶意训练流量分别聚类，丢弃过小簇，得到细粒度 `(label, cluster)`。
3. 模型训练：统计分支是 MLP 自编码器，序列分支是 Transformer 自编码器；损失由重构损失和对比损失组成。
4. 分类与漂移检测：分别用统计分支和序列分支找最近类中心，并计算重构损失相对最近类分布的 sigma 偏离。两分支都不漂移且类别一致时判为 known/certain，否则进入 drifting/uncertain。
5. 漂移识别：拼接两个 latent 表示后用 DBSCAN 聚类；噪声判正常；非噪声簇构造 IP 多重图，用边/节点、边/连通分量阈值判断恶意。
6. 模型适配：用 non-drifting 数据扩展旧类覆盖，用 drifting 数据引入新类；更新时加入旧表示或旧中心距离约束。

## 7. 实验设计与实验步骤

数据：论文重组 CICIDS2018、CICIDS2017、MCFP、ISCX-NonVPN，并加入自采 NormTI，构造 CICIDD 和 MalReal。CICIDD 中 C-D1 是基线，C-D2 引入 DoS Hulk、SSH Bruteforce、Web/XSS/SQL 等变体或新类，C-D3 来自 CICIDS2017，模拟跨时间和跨环境漂移。MalReal 中 M-D1 是 NormTI 正常流加 Trickbot/Emotet/Dridex，M-D2 加 Zeus，M-D3 加 miner、spyware、WannaCry 等，M-D4 用 ISCX-NonVPN 正常流测试正常流环境漂移。

预处理：以会话为单位抽取统计特征和行为特征；用包长桶 `ngram` 特征做预聚类；统计特征归一化；行为序列截断或补齐到固定长度。

模型/基线：Argus 与 FS-Net、CPS-Guard、ACID、CADE、AOC-IDS 比较。CADE 主要是漂移检测器，论文对其输出做了后处理用于恶意检测对比。

训练：初始模型分别在 C-D1 和 M-D1 训练；测试覆盖各子集。适配实验用 C-D2、C-D3、M-D2、M-D4 的训练部分更新模型，再在对应测试集和旧测试集上核查性能。

指标：恶意检测用 Accuracy、Recall、Precision、F1；漂移相关用 DR 和 NDR 表示漂移/非漂移比例。

消融/敏感性：消融包括只用统计分支、只用行为分支、去掉正常/恶意预聚类、用距离阈值替代类条件重构损失、只看特征空间或直接把漂移全判恶意、去掉更新约束。敏感性分析覆盖 `k`、`φcdr`、margin、损失权重、`nσ`、DBSCAN `Eps/MinPts`、图密度阈值和回放比例。

结果核查：重点不是只看总 F1，还要看漂移比例是否随数据集设计的漂移等级变化、known 类是否仍被判为 non-drift、新类是否进入 drift、更新后旧数据性能是否保持。

## 8. 关键结果、结论与证据

Argus 在整体检测上明显优于基线。正文给出的关键证据包括：平均 F1 超过 95%；极端漂移条件下 F1 仍为 88.22%；MalReal 各子集 F1 均超过 93%；CICIDD 上 F1 波动只有 9.24%，MalReal 上只有 4.67%。

与此相比，FS-Net 在同分布 C-D1 上 F1 为 97.43%，但到 C-D3 降到 31.55%，说明静态监督模型对长期漂移非常脆弱。CPS-Guard 在 C-D3 可到 75.07%，但在 MalReal 低召回，说明只建正常基线不适合正常/恶意边界接近的场景。AOC-IDS 在 M-D4 正常环境漂移下 F1 只有 46.94%。

漂移检测结果与数据设计吻合：CICIDD 恶意流量漂移比例从 C-D1 到 C-D3 由 2.67% 升至 94.67%；C-D2 中 DDoS 和 Botnet 等已知类 non-drift 超过 98%，WebBruteforce 和 DoS Hulk 更多被标为 drift；C-D3 的 Botnet 有 98% 被识别为漂移；M-D4 中正常流量各类漂移比例都超过 50%，FTP 最高到 84%。

漂移识别模块也提供了关键支撑：non-drifting 流量检测准确率超过 97%；drifting 流量恶意识别 F1 多数超过 85%。CADE 在 C-D3 上甚至把恶意流量误判为无漂移，导致 non-drifting 恶意检测 F1 只有 0.33%，这反衬了“检测漂移之后还要识别漂移性质”的必要性。

适配实验说明 Argus 更新后能提升新数据表现，同时 M-D1/C-D1 等旧数据性能基本保持；C-D2 更新还会降低 C-D3 的漂移比例，说明新攻击空间对后续相似攻击有覆盖作用。

## 9. 局限性与待解决问题

正文包未截断，因此本文理解不受正文缺页影响。但提供的纯文本中部分表格行数值没有完整保留，本文只引用正文可见的明确数字；若要逐项复核 Table II 到 Table VI 的全部数值，仍建议回到 PDF 表格核对。

方法层面，Argus 依赖“恶意漂移更集中”的假设。低频扫描、慢速横向移动、高度分布式攻击可能不形成明显特征密度，论文也承认这是分布式方法的边界。

相反，某些突发、集中、业务驱动的合法流量也可能同时满足未知、特征相似、主机交互密集三个条件，引发误报。论文建议用事件或主机白名单缓解，但这仍然引入运维先验。

系统假设上，Argus 以完整会话为处理单元，长连接或持续流可能带来检测延迟。论文虽报告 30,000 sessions 的效率，但真实高速链路的长尾会话、内存压力和在线调度仍需工程验证。

适配方面，自标注数据用于更新存在污染风险。距离约束能降低冲击，但不能从根本上保证所有漂移识别标签正确。长期多轮更新中的类合并、时间衰减、样本选择仍是待解决问题。

## 10. 与本项目的关系

这篇论文与“异常检测、恶意流量、暗网与攻击检测”方向强相关，价值主要在开放世界检测思路。它不是把未知流量简单归为异常，而是把未知样本继续细分为正常演化和恶意漂移，这对真实网络安全运营更有意义。

对本项目可借鉴的部分包括：双特征分支降低单点失效；类条件重构损失用于漂移检测；漂移样本的特征聚类加主机交互图密度判断；模型更新时加入表示空间约束。若本项目涉及暗网、Tor、VPN 或匿名通信流量，这种方法尤其适合处理跨时间、跨环境和跨攻击工具的分布变化。

需要谨慎迁移的是漂移识别假设。暗网扫描、分布式探测和低速攻击可能天然稀疏，不能完全依赖密度聚类；可考虑加入时间聚合、目的端口模式、服务角色、资产重要性或图时序特征。

## 11. 代码对照分析

代码包结构与论文流程基本一致。`README.md` 说明两个数据集目录按编号顺序运行：训练、分类与漂移检测、漂移识别、模型适配。`dataset_address` 给出数据下载线索，但代码内部大量路径仍是作者本机 `/home/hxy/...`，复现前必须改路径。

`dataconfig_ids2018.py` 对应 CICIDD。`part1` 基本对应 C-D1 初始训练；`part2` 包含 Hulk、SSH、Web/XSS/SQL 等，对应 C-D2；`part4` 使用 IDS2017 Monday、botnet、bruteforce、dos、portscan、webattack，对应 C-D3 的跨数据集漂移。

`dataconfig_ctu.py` 对应 MalReal，虽然文件名仍带 ctu。里面包含 2024 年 NormTI 日期流量、MCFP 恶意软件样本，以及 ISCX-NonVPN 的 scp、skype、youtube、netflix 等正常应用流量。`part4_normal_files` 明显对应 M-D4 的正常环境漂移。

`myutil.py` 是核心实现。`label_cluster_attack_for_train`、`label_cluster_normal_for_train` 用 `ngram` 特征做 KMeans/DBSCAN 预聚类并丢弃小簇。`StaSeqTrafficNormalizedDataset` 加载 pickle，构造 23 维统计特征和双方向包长序列。`MyModelStaAE` 是统计特征自编码器，`MyModelTransformer` 是行为序列 Transformer 自编码器，`ContraLossEucNewM2` 按 `(label, cluster)` 定义正负样本对，`train_model` 同时训练两个分支。

分类与漂移检测对应 `get_*mid_info`、`get_sta_info*`、`get_test_result_ksigma*`、`generate_new_data_new`、`eval_model_stage1/2`。代码中 `used_uncertain_row = 'cla_md_recon_uncertain_3'`，即使用最近类重构损失的 3σ 判据；`dist_co_certain` 检查 seq 和 sta 两个分支类别是否一致。

漂移识别对应 `split_get_uncertain_data`、`cluster_uncertain_data_latent`、`process_single_cluster`、`get_final_class`、`cluster_pair_data_all`。实现上先拼接 8 维 seq latent 和 8 维 sta latent 做 DBSCAN，再用 IP 多重图计算 `edge_div_node` 与 `edge_div_com`，噪声簇判正常，超过阈值判恶意。

适配对应 `4_certain_update.py`、`5_uncertain_update.py` 及 `myutil.py` 中的 `certain_train_update_model`、`uncertain_train_update_model_to_center_uc`、`combine_two_distribution_*`。certain 更新约束新旧 latent 距离；uncertain 更新约束旧样本到旧中心距离变化。需要注意，代码默认参数与论文参数不完全一致，例如脚本默认 `idcl_eps=0.5`、`k=1`，论文实验中 CICIDD/MalReal 分别使用不同 `k` 与 DBSCAN `Eps`，复现实验应按论文传参。

## 12. 本篇精华

- Argus 的价值在闭环：检测已知类、发现漂移、识别漂移恶意性、再适配模型。
- 类条件重构损失是核心漂移检测点，比全局重构误差和纯距离阈值更贴合细粒度类差异。
- 预聚类解决了 normal/malicious 粗标签过粗的问题，让对比学习有更清晰的类内紧凑目标。
- 漂移识别的关键假设是“恶意漂移在特征空间和物理主机空间同时集中”，代码中落地为 DBSCAN + IP 多重图密度。
- 统计特征和行为序列特征并行建模，不只是提升准确率，也降低某一类特征对漂移不敏感时的失效风险。
- 适配模块的科学意义是控制表示空间变化，而不是盲目增量训练。
- 论文最强证据来自极端漂移和更新实验：静态基线大幅退化，而 Argus 仍保持较高 F1 且旧数据性能基本稳定。

## 13. 建议精读路线

先读 Introduction 和 Problem Definition，把三大挑战记清楚：分类与漂移检测、漂移识别、模型适配。

再读 Section III-C 到 III-F，这是方法主体。重点画出 ACLearner、类条件重构损失、DBSCAN+物理图、距离约束更新四个模块之间的数据流。

然后读 Evaluation 的数据集构造部分。C-D1/C-D2/C-D3 和 M-D1/M-D2/M-D3/M-D4 的漂移来源，是理解实验说服力的关键。

接着读检测性能、详细漂移分析和适配实验，优先看 Table II-IV、Figure 3-6。不要只看总 F1，要同时看 DR/NDR 是否符合预期。

最后对照代码阅读：先看 `dataconfig_ids2018.py` 和 `dataconfig_ctu.py` 的数据划分，再看 `myutil.py` 的模型、漂移检测、漂移识别和更新函数，最后按 `CICIDD/` 或 `MalReal/` 的编号脚本串起完整复现实验流程。