# [613] AUCp: Pseudo-AUC for Inference Model Selection with Unlabeled Validation Data in Abnormality Detection

## 1. 基本信息

- 题名译法：**AUCp：异常检测中使用无标签验证数据进行推理模型选择的伪 AUC**
- 年份与来源：2026，IEEE Transactions on Medical Imaging，DOI `10.1109/TMI.2026.3684946`
- 作者：Md Mahfuzur Rahman Siddiquee 等，Arizona State University / Mayo Clinic
- 任务属性：严格说是**异常检测中的无标签模型选择方法**，论文实验主体是医学影像异常/疾病检测；与“入侵检测与网络异常检测”的关系是方法论迁移，而不是网络流量检测论文。
- 正文状态：本次正文包未截断；但文本来自 accepted author version，最终出版排版可能有微调。
- 代码状态：已下载到 `source\AUCp`。当前仓库主要覆盖 AUCp 指标包、医学图像重构基线、自监督基线与 FAE 分支；未看到 HealthyGAN/Brainomaly 完整训练代码作为顶层可直接复现模块。

## 2. 中文翻译与核心摘要

这篇论文解决的不是“如何设计一个更强的异常检测模型”，而是一个更容易被忽视的问题：**无监督/自监督异常检测训练完成后，在没有带标签验证集时，应该选哪个 checkpoint 用于推理？**

作者提出 AUCp。做法非常朴素：已知训练集 `D_train` 只含正常样本，于是把训练正常样本标成伪负类；把无标签测试/验证混合集 `D_test` 的所有样本都临时标成伪正类；用模型产生的异常分数计算一次普通 ROC-AUC。这个伪 AUC 不需要真实异常标签，却可用于在多个训练 epoch/checkpoint 中选择推理模型。

核心观点是：如果训练正常集足够大、足够代表正常分布，而无标签测试集中确实含有一定比例异常，那么 AUCp 对 checkpoint 的排序会接近真实 AUC。论文用 HealthyGAN、Brainomaly 以及 CutPaste、FPI、PII/Poisson、NSA、AE、MemAE、AE-U、FAE 等大量实验说明，AUCp 往往比 FID、训练损失或最后 epoch 更适合作为推理模型选择准则。

## 3. 论文解决的具体问题

传统异常检测常说“不需要异常标签训练”，但很多论文在模型选择时仍偷偷依赖带标签验证集，或用合成异常、FID、重构误差、训练 loss 选择模型。这在真实部署中不成立：罕见病、早期异常、医院新域数据往往没有可靠标注验证集。

论文把问题具体化为：训练阶段只有正常样本；推理前有一个无标签混合集；模型在训练过程中保存了多个 checkpoint；现在需要选择一个最能分离正常与异常的 checkpoint，但不能看真实标签。

这对网络异常检测也很典型：训练集可能是“干净正常流量”，线上验证窗口只有未标注流量，里面可能混有攻击、扫描、异常行为；此时用验证 loss 选模型可能选到“重构正常和异常都很好”的模型，反而降低检测能力。

## 4. 创新点深度提炼

1. **把无标签模型选择问题转化为伪监督 AUC 计算**：AUCp 不是新模型，而是一个推理 checkpoint 选择指标，直接服务部署环节。
2. **目标对齐**：FID 衡量生成图像是否逼真，重构 loss 衡量输入是否被还原；AUCp 衡量训练正常样本与目标无标签集在异常分数上的可分性，更接近异常检测目标。
3. **形式化 Brainomaly 中的启发式**：论文说明 AUCp 的思想最早在 Brainomaly 中作为经验 heuristic 出现，本篇给出正式定义、理论关系和跨方法验证。
4. **给出伪标签与真实标签接近的数学论证**：在正常训练集足够大且代表性强时，伪标签与真实标签的 AUC 关系趋近一致。
5. **跨范式验证**：不仅比较 GAN 式无监督方法，还扩展到自监督合成异常、图像重构、特征重构方法。
6. **明确讨论失败条件**：训练正常集小/偏、无标签集中异常比例趋近 0、训练/测试正常分布偏移，都会削弱 AUCp。

## 5. 科学问题与研究假设

科学问题可以概括为：**在没有带标签验证集时，能否仅利用正常训练集和无标签目标集，选择出接近真实 AUC 最优的异常检测 checkpoint？**

主要假设包括：

- `D_train` 是正常样本集合，且足够大、覆盖正常模式。
- `D_test` 是无标签混合集，包含 `k` 个正常样本和 `d` 个异常样本，且 `d >= 1`，最好异常比例不太低。
- 模型异常分数方向一致：分数越高越异常。
- 训练正常和测试正常没有严重协变量偏移；否则 AUCp 可能只是在检测域差异。
- 对 checkpoint 选择而言，AUCp 的排序比其绝对值更重要。

## 6. 科学方法与技术路线

论文设定 `D_train` 含 `n-k` 个正常样本，`D_test` 含 `k` 个正常样本和 `d` 个异常样本，但测试标签未知。AUCp 构造伪标签：

- `D_train`：伪标签 0，正常/负类。
- `D_test`：伪标签 1，全当异常/正类。
- 对每个 checkpoint 计算异常分数，再计算普通 ROC-AUC，即 `AUCp = AUC(GTp, P)`。
- 选择 `AUCp` 最大的 checkpoint 作为推理模型。

理论上，论文先证明伪标签 `GTp` 与真实标签 `GT` 的差异只来自测试集中被误标成正类的 `k` 个正常样本；当正常样本总数 `n` 很大时，`AUC(GT, GTp) = 1 - k/n`，趋近 1。后续又给出一个更直观的混合分布关系：若测试正常与训练正常同分布，`AUCp = (1 - ρ)AUC + ρ·0.5`，其中 `ρ` 是伪正类中真实正常样本比例。因此 AUCp 的绝对值会被拉向 0.5，但排序仍可能可靠；若能估计 `ρ`，还可做偏差校正。

## 7. 实验设计与实验步骤

1. **数据**：无监督 MRI 实验使用 ADNI 阿尔茨海默病数据和机构 headache 数据；自监督/重构实验覆盖 RSNA、VinDr-CXR、Brain Tumor、BraTS21、LAG、ISIC2018、Camelyon16。
2. **预处理**：MRI 注册到 MNI152、去颅骨，转为 2D 切片并聚合到患者级；其他医学图像按各数据集格式裁剪/缩放，训练集只用正常类。
3. **模型/基线**：无监督部分比较 HealthyGAN、Brainomaly 与 ALAD、ALOOC、f-AnoGAN、GANomaly、DDAD；自监督部分用 CutPaste、FPI、FPI-Poisson/PII、NSA；重构部分用 AE、AE-L1、AE-SSIM、AE-Perceptual、MemAE、AE-U、FAE-MSE、FAE-SSIM。
4. **训练**：HealthyGAN/Brainomaly 训练 400k iterations，每 10k 保存 checkpoint；自监督和重构方法按 epoch 保存模型，后续逐 checkpoint 评估。
5. **指标**：真实 AUC 用于论文报告和相关性分析；AUCp 用于无标签 checkpoint 选择；GAN 部分还比较 FID；重构部分比较 reconstruction loss 选择。
6. **消融/敏感性**：FID vs AUCp，transductive vs inductive，最后 epoch vs AUCp，重构 loss vs AUCp，AUCp 与真实 AUC 的 Pearson 相关，训练正常集大小和测试异常比例仿真。
7. **结果核查**：每个 checkpoint 同时记录真实 AUC 和 AUCp，选取 AUCp 最大 epoch，再回看该 epoch 的真实 AUC 是否优于最后 epoch、FID 选择或 loss 选择。

## 8. 关键结果、结论与证据

- 在 AD 检测上，HealthyGAN 从平均 AUC 0.4910 提升到 0.5970；Brainomaly 从 0.6421 提升到 0.6550，并优于 f-AnoGAN 平均 0.6020。
- 在 headache 检测上，HealthyGAN 从 0.7695 到 0.8088；Brainomaly 从 0.8796 到 0.8960，明显高于 ALAD 的 0.6955。
- FID 与真实 AUC 的相关性较弱：AD/Headache 的 Pearson 大约 0.32 到 0.57；AUCp 更高，AD 两个 split 超过 0.95，HEAD DS1 也超过 0.95，但 HEAD DS2 只有 0.5986，说明并非全场景完美。
- 自监督结果中，AUCp 选择带来一些很大的增益：Brain 数据上 FPI 从 0.2932 到 0.8881，CutPaste 从 0.2208 到 0.8277，FPI-Poisson 从 0.2425 到 0.7809；VinDr-CXR 上 NSA 从 0.4999 到 0.7622。
- 重构模型也常受益，例如 Brain 上 MemAE 从 0.6030 到 0.8435，AE-U 从 0.9042 到 0.9380。
- 但表格里也有例外：如 BraTS21 上 NSA 从 0.8734 降到 0.8123，部分 AE/AE-SSIM 场景变化很小或略降；Headache transductive 的 HEAD DS2 中 AUCp 选中模型低于 FID 选中模型。论文总体结论成立，但“总是更好”的表述需要谨慎。

## 9. 局限性与待解决问题

AUCp 的关键风险是把所有无标签测试样本当正类。如果测试集几乎全是正常，AUCp 会趋近 0.5，无法提供可靠排序；如果训练正常集不代表真实正常空间，AUCp 可能选择“最能区分训练域和测试域”的模型，而不是最能检测异常的模型。

理论证明中的“训练正常集近似覆盖 universal normal feature set”很强，在医学影像的跨医院、跨设备、跨协议场景，以及网络流量的跨时间、跨业务、跨拓扑场景都容易被破坏。

此外，AUCp 使用无标签目标集做模型选择，严格讲有 transductive 成分。若论文评估在同一个 test mixture 上选 checkpoint 再报告真实 AUC，需要额外用 inductive split 证明泛化；本文做了这部分，但仍建议复现实验时区分“无标签验证混合集”和“最终测试集”。

代码层面也有待核查：当前 `ae_worker.py` 中存在把异常比例下采样到 1% 的评估逻辑，可能与论文表 VI/VII 的常规测试设定不一致；FAE 分支的 `ISIC2018_aucp` 看起来没有把测试正常样本改成伪正类，而是保留了真实 0 标签。由于当前环境没有 `git`，我无法判断这些是否为本地改动。

## 10. 与本项目的关系

如果本项目是网络安全/异常检测综述，本文应归为：**无标签模型选择、异常检测验证指标、部署阶段选择准则**，而不是入侵检测模型本身。

迁移到网络异常检测时，可以这样用：对每个 checkpoint，用正常训练流量计算异常分数作为负类；用一个无标签线上验证窗口计算异常分数作为伪正类；计算 AUCp 并选择最大 checkpoint。适用模型包括自编码器、预测式时序模型、对比学习流量表征、图异常检测和一类分类器。

必须额外注意网络场景的概念漂移和污染问题：正常业务高峰、协议升级、路由变化、采集点变化都可能让测试正常流量偏离训练正常流量，使 AUCp 偏向域偏移检测。网络攻击极低频时，AUCp 也会退化。因此在本项目中更适合把 AUCp 作为“无标签验证启发式”，并与时间切片稳定性、训练集污染检测、PU learning/MPE 异常比例估计联合使用。

## 11. 代码对照分析

- 公共指标：`source\AUCp\aucp\metric.py` 实现 `aucp_score`、`aucp_from_labels`、`estimate_auc_from_aucp`；本质是拼接训练正常分数和无标签测试分数，再调用 `sklearn.metrics.roc_auc_score`。
- checkpoint 选择：`source\AUCp\aucp\selector.py` 提供 `select_best_checkpoint`，支持传入 `(checkpoint, aucp)` 或分数数组，选择 AUCp 最大项。
- 路径配置：`source\AUCp\aucp\paths.py` 用 `AUCP_DATA_ROOT` 和 `AUCP_OUTPUT_ROOT` 管理数据和输出。
- 重构线：`reconstruction\train.py` 调度 AE、MemAE、AE-U、GANomaly 等 worker；`reconstruction\test.py` 逐 epoch 载入 checkpoint，先算真实 AUC，再用 `_aucp` loader 算 AUCp；`reconstruction\dataloaders\dataload.py` 中 `_aucp` 类把训练正常追加为 0，把测试集标成伪正类。
- 自监督 one-stage：`ssl\one_stage\train_med.py` 定义 CutPaste、FPI、FPI-Poisson、Shift-Intensity-M/NSA 等设置；`self_sup_data\self_sup_tasks.py` 负责贴片/泊松混合伪异常；`AUCP_test.py` 逐模型输出 `epoch, model_path, aucp, auc, ap`。
- 自监督 two-stage：`ssl\two_stage\run_training.py` 训练 CutPaste/AnatPaste 表征；`eval.py` 和 `aucp_eval.py` 用训练正常嵌入拟合密度，距离作为异常分数，再分别计算真实 AUC 与 AUCp。
- FAE：`reconstruction\feature-autoencoder\fae\models\feature_extractor.py` 用 ResNet18 提取多层特征；`models\models.py` 中 `FeatureReconstructor` 重构特征并用 MSE/SSIM 生成 anomaly map/score；`aucp_eval_fae.py` 遍历保存 checkpoint 计算 AUC/AUCp。
- 未覆盖或不完整处：当前仓库没有看到 HealthyGAN/Brainomaly 的完整训练管线；README 提到构建于相关项目之上。用户元数据中的 Quic/Tor/NSL 等网络数据集线索，在当前源码搜索中没有形成实际可运行入口。

## 12. 本篇精华

- AUCp 的价值在于解决“无标签验证集下选 checkpoint”，不是提出新异常检测网络。
- 它把训练正常样本视为负类、无标签目标集全视为正类，用普通 ROC-AUC 得到无标签选择准则。
- AUCp 的绝对数值有偏，但在正常训练集足够大、测试异常比例足够高、分布偏移较小时，checkpoint 排序接近真实 AUC。
- FID/重构 loss 与异常检测目标不对齐；论文证据显示 AUCp 通常更能选到检测性能好的模型。
- 最大增益出现在训练后期并非最优、最后 epoch 明显过拟合或欠拟合的自监督/重构方法上。
- AUCp 对异常比例极低和正常域偏移敏感；这正是网络安全场景迁移时最需要防范的点。
- 代码里的核心指标实现很轻量，可直接移植；实验代码较研究型，复现前要核查 `_aucp` 数据集标签逻辑和评估下采样逻辑。

## 13. 建议精读路线

1. 先读 Introduction，抓住“无监督训练不等于无标签模型选择”这个问题。
2. 精读 Section II 和 Fig. 1/3，手工推一遍 `D_train`、`D_test`、`GTp`、`AUCp` 的构造。
3. 对照 Section III，把无监督 MRI 实验和七个公开医学图像 benchmark 分开理解。
4. 精读 Tables II-V：重点看 AUCp 与 FID 的相关性和 transductive/inductive 差异，同时标出例外。
5. 精读 Tables VI-VIII 和 Fig. 5：理解 AUCp 在不同方法上的收益、相关性下降场景和失败条件。
6. 看代码时从 `aucp/metric.py` 与 `aucp/selector.py` 开始，再任选 `reconstruction/test.py` 或 `ssl/one_stage/AUCP_test.py` 跟一条完整实验链路。
7. 若服务本项目综述，可把本文放在“无标签验证/模型选择”小节，并与训练损失、合成异常验证、稳定性选择、PU learning 方法对比。

<!-- codex-cli-deep-read: complete -->
