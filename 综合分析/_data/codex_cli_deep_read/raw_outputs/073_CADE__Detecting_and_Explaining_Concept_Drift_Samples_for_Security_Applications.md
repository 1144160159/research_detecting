# [073] CADE: Detecting and Explaining Concept Drift Samples for Security Applications

## 1. 基本信息

- 论文：CADE: Detecting and Explaining Concept Drift Samples for Security Applications
- 中文题名：CADE：面向安全应用的概念漂移样本检测与解释
- 年份/来源：2021，30th USENIX Security Symposium
- 作者：Limin Yang, Wenbo Guo, Qingying Hao, Arridhana Ciptadi, Ali Ahmadzadeh, Xinyu Xing, Gang Wang
- DOI：无
- 本地 PDF：[paper](<F:\泉城实验室\二期\论文\异常检测\paper\CADE - Detecting and Explaining Concept Drift Samples for Security Applications.pdf>)
- 本地代码：[source\CADE](<F:\泉城实验室\二期\论文\异常检测\source\CADE>)
- 备注：你提供的 `PAPER_TEXT` 正文包为空；我基于本地 PDF、补充材料 PDF 和代码包进行阅读与对照。

## 2. 中文翻译与核心摘要

这篇论文关注安全分类器部署后的“闭世界”失效问题：模型训练时只见过若干已知家族，但上线后会遇到新恶意软件家族、新网络攻击类型或旧家族的新变体。传统分类器会强行把这些样本归入已知类，导致高置信误判。CADE 的目标不是替换原分类器，而是在其旁边加一个漂移检测与解释模块。

核心思想是：用已知标签训练一个对比自编码器，把高维安全特征映射到低维潜空间；在这个空间中，同类样本应聚得更紧，不同类样本应分得更开。检测时，计算测试样本到各已知类中心的距离，并用每类自己的 MAD 统计量判断它是否对所有旧类都是离群点。解释时，不再解释分类边界，而是解释“为什么该样本离最近旧类中心这么远”：寻找一小组原始特征，把它们替换为最近旧类参考样本的特征值后，样本在潜空间中会明显靠近旧类中心。

## 3. 论文解决的具体问题

论文解决的是安全应用中的实例级概念漂移识别问题，具体是：

1. 已部署的恶意软件家族分类器、入侵检测分类器，会遇到训练期不存在的新家族/新攻击类型。
2. 传统概念漂移检测通常依赖一批新标签后做统计判断，不能在单个样本到来时给出可操作提示。
3. 高维稀疏安全特征空间里，普通距离度量容易失效，离群空间又非常大。
4. 安全分析员不仅要知道“这是漂移”，还需要知道“哪些特征让它不像任何旧类”，否则难以做人工研判、家族命名或规则更新。

## 4. 创新点深度提炼

- **从分类置信度转向距离学习**：CADE 不依赖原分类器 softmax 置信度，而是单独学习一个适合漂移检测的潜空间距离。
- **对比自编码器用于安全漂移检测**：自编码器保留输入可重构性，对比损失利用已有标签压缩类内距离、扩大类间距离。
- **每类自适应阈值**：使用每个旧类的中心距离分布和 MAD，而不是设一个全局距离阈值。
- **实例级检测与排序**：检测每个到达样本，并按到最近中心的距离排序，贴近安全分析员“先看最可疑样本”的工作方式。
- **距离解释而非边界解释**：论文指出边界解释在稀疏离群空间中很难成功跨越边界，因此改为解释距离变化。
- **解释仍落在原始特征空间**：不在潜变量上解释，而是选择原始权限、API、网络流统计等可读特征，增强语义可解释性。

## 5. 科学问题与研究假设

科学问题可以概括为：已有标签是否足以学习一个可泛化的安全样本相似性空间，使未知家族样本在该空间中稳定远离所有已知类，并能通过少量原始特征解释这种远离？

主要研究假设：

- 已知家族标签中包含足够的“相似/不相似”监督信号，可学习比原始高维空间更可靠的距离。
- 新家族或新攻击类型不会自然落入某个旧类紧密簇内，而会表现为对所有旧类的距离异常。
- 每个旧类的紧密程度不同，因此 MAD 这种类内稳健统计量比固定阈值更合理。
- 将漂移样本的少量关键特征替换为最近旧类代表样本的特征值，可以显著缩短潜空间距离；这些特征就是漂移语义的候选解释。
- 分析员可通过排序列表和稀疏解释更高效地发现新家族或重要变体。

## 6. 科学方法与技术路线

CADE 的技术路线是“原分类器 + 对比表征 + MAD 检测 + 距离解释”。

1. **原分类器**：仍训练 MLP/RF 做已知家族分类，论文实验主用 MLP。
2. **对比自编码器 CAE**：编码器 `f` 把输入映射到低维潜空间，解码器保持重构能力；对比损失让同类靠近、异类至少相隔 margin。
3. **中心与 MAD 建模**：对每个已知类计算潜空间中心、训练样本到中心的距离中位数和 MAD。
4. **漂移判定**：测试样本若相对所有已知类的标准化距离异常分数都超过阈值，则判为漂移；最近中心对应“最相似旧类”。
5. **漂移排序**：按到最近中心的距离降序排序，越远越优先检查。
6. **距离解释**：选择 mask，使漂移样本在原始特征空间被少量替换后，编码结果尽量靠近最近旧类中心，同时用 elastic-net 控制特征数量。

## 7. 实验设计与实验步骤

1. **数据**  
   - Drebin：Android 恶意软件家族归因。选 8 个样本数不少于 100 的家族，每次留 1 个家族作为未见家族。  
   - IDS2018：网络入侵检测。使用 Benign、SSH-Bruteforce、DoS-Hulk、Infiltration，每次留 1 个攻击类作为未见攻击类。  
   - 行业 PE 数据：Blue Hexagon 内部 Windows PE 恶意软件样本，验证更复杂多家族场景。

2. **预处理**  
   - Drebin：按时间划分 80/20；训练集特征建表；VarianceThreshold 过滤低方差特征。代码中 `drebin_new_7` 为 `X_train=(2547,1340)`、`X_test=(768,1340)`。  
   - IDS2018：去 NaN/Infinity/重复流，按时间排序；端口和协议 one-hot，其他 77 个统计特征 MinMax 归一化；最终 83 维。`IDS_new_Infilteration` 为 `X_train=(97170,83)`、`X_test=(33530,83)`。

3. **模型/基线**  
   - CADE：对比自编码器 + MAD。  
   - Vanilla AE：同结构自编码器，但无对比损失，用来验证对比学习贡献。  
   - Transcend：基于 non-conformity / credibility p-value 的漂移检测基线。  
   - 解释基线：Random、Boundary-based、COIN，补充材料还讨论了 gradient-based 方法。

4. **训练设置**  
   - Drebin：MLP `100-30`；CAE `512-128-32`，latent 维度为已知类数；margin=10，`lambda=0.1`，MAD 阈值 3.5。  
   - IDS2018：MLP `30`；CAE `64-32-16`；batch size 512；其他关键阈值同上。  
   - 运行脚本集中在 `run_drebin_cade.sh`、`run_ids_cade.sh`、`run_*_pure_ae.sh`。

5. **指标**  
   - 检测：Precision、Recall、F1、normalized inspection effort。  
   - 解释：扰动后样本到最近中心的平均距离；扰动后是否跨过检测边界；案例语义一致性。

6. **消融/敏感性**  
   - 主要消融是 CADE vs Vanilla AE，验证对比损失是否让潜空间簇更紧。  
   - 论文附录讨论超参数敏感性，正文局限中承认 MAD 阈值等仍为经验设定。

7. **结果核查**  
   - 代码包中已有检测汇总：[average_drebin_result](<F:\泉城实验室\二期\论文\异常检测\source\CADE\reports\average_drebin\average_drebin_result_margin10.0_mad3.5_lambda0.1.txt>)、[average_IDS_result](<F:\泉城实验室\二期\论文\异常检测\source\CADE\reports\average_IDS\average_IDS_result_margin10.0_mad3.5_lambda0.1.txt>)。  
   - 解释结果在 `reports/exp_evaluation/`，可复核 Table 4/6 附近的距离与成功率。

## 8. 关键结果、结论与证据

- 漂移检测上，CADE 明显优于 Vanilla AE。代码汇总中，Drebin 平均 F1 为 **95.95%**，IDS2018 平均 F1 为 **95.61%**；Vanilla AE 分别为 **72.44%** 和 **74.24%**。
- 论文正文给出的整体结论是：Drebin 上 CADE 平均 F1 约 **0.96**，两个基线约 **0.80** 和 **0.72**；CADE 的方差更小，排序质量更稳定。
- 解释 fidelity 上，Drebin-FakeDoc 的原始距离为 **5.363**，CADE 扰动后降到 **0.065**；IDS2018-Infiltration 原始距离为 **11.715**，CADE 降到约 **2.35**。
- CADE 选出的解释特征数量较小：Drebin 平均约 **44.7** 个，占 1340 维约 3%；IDS 平均约 **16.2** 个，占 83 维约 20%。
- 边界跨越实验显示，解释“距离”比解释“边界”更适合漂移样本；Drebin 上 CADE 可使约 **97.64%** 的扰动样本回到边界内，而随机、COIN、边界方法几乎为 0。
- 行业 PE 数据上，训练已知家族数 N=5/10/15 时，F1 分别约 **0.97/0.95/0.87**，说明方法在更多未知家族场景仍有可用性。
- 论文最后的判断是：CADE 适合作为监督安全分类器的旁路组件，用于发现未知类、排序人工调查对象，并给出可读的特征级线索。

## 9. 局限性与待解决问题

- 论文主要评估“新家族”漂移，对旧家族内部演化只做了有限探索。
- 所有漂移样本被排成一个列表，但真实场景中可能包含多个新家族或多个子簇，后续应先聚类再抽代表样本分析。
- MAD 阈值、margin、解释正则项等关键超参数仍偏经验化。
- 假设训练标签干净；若存在误标、投毒或家族标签粗糙，中心与 MAD 都会受影响。
- 对大规模、多家族工业数据的验证仍受限于高质量家族标签，论文行业实验最多用 15 个已知训练家族。
- 解释是“朝最近旧类中心移动”的反事实式解释，不等价于真实因果机制，也不保证扰动后的恶意软件或网络流在业务语义上完全有效。
- 代码依赖较旧：Python 3.6、TensorFlow 1.x、Keras 2.2.x，复现实验需要旧环境。
- 本次用户提供的正文包为空；我已回到本地 PDF 和补充材料阅读，不属于正文包截断，但若要逐字核表，仍建议以原 PDF 表格为准。

## 10. 与本项目的关系

这篇与“异常检测/跨域安全检测”有方法论关系，但不是直接面向通用网络异常检测的论文。它更像是安全分类器上线后的未知类发现组件。

对本项目可借鉴之处：

- 如果你的任务存在训练域与部署域差异，可借鉴“对比表征 + 类中心 + 稳健阈值”的检测框架。
- 如果异常类型需要人工研判，可借鉴它的“按距离排序 + 少量特征解释”设计。
- 对网络流异常检测尤其有参考价值：IDS2018 实验说明连续统计特征与类别特征混合时，仍可用参考样本替换方式做解释。
- 但若本项目关注无标签异常检测、加密流量识别或时序预测，CADE 的已知类标签依赖较强，需要改造成自监督/弱监督形式。

## 11. 代码对照分析

- 入口流程：[main.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\main.py>)  
  对应论文全流程：准备数据、训练 MLP/RF、训练 CAE/Vanilla AE、检测、评估、解释。

- 数据处理：  
  - Drebin：`cade/data.py` 中 `prepare_drebin_data()`、`load_features()` 对应时间划分、特征选择、未见家族标签重映射。  
  - IDS2018：`IDS_data_preprocess/clean_data.py` 负责清洗；`gen_IDS_data.py` 负责按场景构造 seen/unseen、归一化和 one-hot。  
  - 配置路径在 [cade/config.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\cade\config.py>)。

- 模型：  
  - [cade/autoencoder.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\cade\autoencoder.py>) 实现 `Autoencoder` 和 `ContrastiveAE`。  
  - `ContrastiveAE.train()` 中构造同类/异类 pair，联合重构损失与对比损失。实现版对比损失写法与论文公式细节略有差异，但核心行为一致：同类拉近，异类推到 margin 外。

- 分类器：  
  - [cade/classifier.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\cade\classifier.py>) 实现 MLP 和 RF。论文主实验使用 MLP。

- 漂移检测：  
  - [cade/detect.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\cade\detect.py>) 对应 Algorithm 1：编码训练/测试样本，计算类中心、距离、MAD 和漂移标记。

- 评估：  
  - [cade/evaluate.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\cade\evaluate.py>) 负责合并分类与检测结果、计算 precision/recall/F1 和 inspection effort。  
  - `average_all_detection_results.py` 生成论文 Table 3 风格的平均结果。

- 解释：  
  - [cade/explain_by_distance.py](<F:\泉城实验室\二期\论文\异常检测\source\CADE\cade\explain_by_distance.py>) 是 CADE 主解释方法。  
  - `cade/mask_exp_by_distance_mask_m1.py` 实现 mask 优化、Gumbel/Concrete 近似和 elastic-net 稀疏项。  
  - `cade/explain_global_approximation_loose_boundary.py` 是边界近似解释基线。  
  - `evaluate_explanation_by_distance.py` 复核解释距离、随机基线、梯度基线和跨边界比例。

- 运行线索：  
  - 检测：`run_drebin_cade.sh`、`run_ids_cade.sh`。  
  - Vanilla AE：`run_drebin_pure_ae.sh`、`run_ids_pure_ae.sh`。  
  - 解释：`run_cade_exp_drebin_fakedoc.sh`、`run_cade_exp_ids_infiltration.sh`。  
  - 环境：`requirements-tensorflow-cpu.txt` 指向 TensorFlow 1.10/Keras 2.2.5。

## 12. 本篇精华

- CADE 的关键不是“又做了一个异常检测器”，而是把安全分类器的未知类问题转成了可学习距离空间中的离群检测。
- 对比学习是核心增益来源：Vanilla AE 只会压缩数据，不保证类内紧、类间远。
- MAD 的价值在于每个旧类都有自己的半径尺度，适合家族紧密程度不一致的安全数据。
- 解释模块抓住了漂移检测的本质：漂移是距离异常，不是常规分类边界两侧的分类差异。
- 特征替换用最近中心样本作参考，解决了安全特征中二值、类别、连续值混杂时的非法扰动问题。
- 实验设计很实用：每次隐藏一个家族，模拟上线后遇到未知家族，再用 inspection effort 衡量分析员成本。
- 论文最值得借鉴的是“检测-排序-解释”闭环，而不是单一 F1 指标。
- 主要风险是标签质量和场景假设：若训练家族本身混乱或存在强烈家族内演化，CADE 会把有价值变体和真正新家族一起报出来。

## 13. 建议精读路线

1. 先读 Introduction，明确它反对的是闭世界分类器和批量统计式 drift detection。
2. 精读 Section 3.1-3.2，抓住对比自编码器、类中心、MAD 三件事。
3. 对照 Algorithm 1 和 `cade/detect.py`，确认检测分数如何计算。
4. 精读 Section 3.3，重点理解为什么边界解释在离群空间中不稳定，以及距离解释的反事实含义。
5. 读 Section 4 的 Drebin/IDS 实验设置，关注“隐藏一个家族”的可复现实验范式。
6. 读 Section 5 的 Table 4/6 和案例，判断解释是否真的有安全语义。
7. 最后读 Discussion/Limitations，再回到代码的 `main.py` 和运行脚本，形成可复现实验清单。