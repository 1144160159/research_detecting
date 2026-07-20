# 神经开放集与 ARPL 基线对比报告

## 1. 目的与公平性约束

本轮实验检验 v1.4.1 是否只优于内部树风险候选，而未覆盖通用开放集识别基线。对照统一使用 HIKARI-2021、DoHBrw2020、Mal_TLS2023 的外层攻击类留出协议，未知类仅进入测试集；预处理、神经模型、协方差、近邻索引、Weibull 尾部和拒识阈值均只使用已知训练集或已知验证集。HIKARI 与 Mal_TLS 使用输入特征指纹分组，DoH 使用 CaptureId 分组。

比较方法包括 MSP、Energy、MaxLogit、Mahalanobis、KNN、OpenMax、ViM、相对 Mahalanobis和 ARPL。ARPL 按官方开源代码的 reciprocal-point 类别分数、可学习半径和 margin ranking 约束实现；未启用依赖图像 GAN 的 ARPL+CS，因此结果标记为 ARPL。

## 2. 三数据集结果

| 数据集 | 运行数 | v1.4.1 门控 | 最强固定神经基线 | 门控胜负 |
|---|---:|---:|---:|---:|
| HIKARI-2021 | 12 | `0.880130±0.079239` | KNN `0.811960±0.157397` | `8/0/4` |
| DoHBrw2020 | 9 | `0.867093±0.059342` | KNN `0.784061±0.049692` | `8/0/1` |
| Mal_TLS2023 | 18 | `0.993660±0.003404` | 相对 Mahalanobis `0.981932±0.010440` | `17/0/1` |
| 合计 | 39 | `0.929520±0.079364` | KNN `0.883127±0.128115` | `33/0/6` |

门控相对固定 KNN 平均提高 `0.046393`，Wilcoxon `p=3.4036e-05`。相对 Mahalanobis、ViM、Energy、OpenMax、MSP 和 ARPL 的平均增益分别为 `0.061312`、`0.152635`、`0.157500`、`0.200419`、`0.222599` 和 `0.210269`。其中门控对 MSP 和 OpenMax 均为 `38/39` 获胜，对 ARPL 为 `36/39` 获胜。

## 3. HIKARI Probing 边界诊断

普通 MLP-Mahalanobis 在 Probing 三个种子上的平均 AUROC 为 `0.804017`，高于门控支持路径的 `0.773811`，说明 Probing 在神经嵌入的共享协方差空间中存在补充可分性。但是该评分在 XMRIGCC 上均值仅 `0.510734`，KNN 也仅为 `0.683202`，而原门控为 `0.843758`。按测试结果逐次选择神经评分得到的 oracle 均值为 `0.848766`，仍低于门控 `0.880130`，且 oracle 不可部署。

监督对比训练未消除方向依赖。其 Mahalanobis 在 Probing 上为 `0.804706`，但在 XMRIGCC 上降至 `0.641336`。固定 0.25、0.5、0.75 权重平均、Cauchy、Bonferroni 并集均未超过原支持风险的12次全局均值 `0.880129`。因此 Probing 的局部提升不能作为增加神经分支的依据。

## 4. 被否决组件

| 组件 | 结果 | 决策 |
|---|---|---|
| OpenMax | HIKARI均值 `0.433569`，最低 `0.059551` | 否决 |
| ARPL | 39次均值 `0.719251`，HIKARI最低 `0.050995` | 否决 |
| ViM | HIKARI均值 `0.499208`，DoH均值 `0.753206` | 否决 |
| 相对 Mahalanobis | Mal_TLS强，但HIKARI方向反转 | 否决统一使用 |
| 双侧经验尾 | HIKARI最差降至 `0.000904` | 否决 |
| 监督对比嵌入 | Probing提高，XMRIGCC显著下降 | 否决统一使用 |
| 双空间固定融合 | 12次均值低于原支持路径 | 否决 |

## 5. 与论文最好结果的关系

Open-Detect 论文在 Malicious TLS 上采用32×32灰度流量图和随机 `23/1、21/3、19/5` 类划分，报告未知检测 Accuracy/F1，而本方案采用结构化侧信道、多恶意家族留出、指纹分组和 AUROC。Open-Detect 发布代码还使用已知测试集选择模型，并用测试标签的 Youden 指数选择阈值；其 AUROC不受阈值影响，但 Accuracy/F1 与当前已知验证分位数协议不能直接比较。

因此当前只能作两层结论：第一，v1.4.1 是本项目已经实现的同协议基线中的最优方案；第二，尚未证明优于所有论文方法。Open-Detect、FOSS、CVAE-EVT等方法需要在相同原始输入、外层家族留出、无泄漏分组和已知验证校准协议下复现后，才能形成严格 SOTA 结论。

## Open-Detect 代码预复现

使用发布仓库自带 `mal_32_1c_train.npz` 和 `mal_32_1c_test.npz`，保持 split0 的23个已知类/1个未知类和官方模型损失，执行20轮、batch 512的加速预实验。结果为已知 Accuracy `0.958748`、已知 Macro-F1 `0.959497`、未知 AUROC `0.920705`。该结果证明发布代码与数据可运行，但不是论文100轮完整复现，也不是本方案同协议对比。

发布实现使用已知测试集进行模型选择，Accuracy/F1 阈值还可由测试标签的 Youden 指数确定；本项目仅把阈值无关的 AUROC 作为预实验参照。后续若要形成论文直接比较，需要把 Open-Detect 迁移到相同攻击家族留出、指纹/采集分组和独立已知验证校准协议，而不能把 `0.920705` 与当前三数据集平均值直接排序。

## 6. 产物

- 代码：`source/CAEOS-EMTD/caeos/neural_open_set.py`
- 统一入口：`source/CAEOS-EMTD/train_neural_open_set.py`
- 矩阵运行器：`source/CAEOS-EMTD/run_neural_baseline_matrix.py`
- 统计脚本：`source/CAEOS-EMTD/summarize_neural_comparison.py`
- 固定基线统计：`source/CAEOS-EMTD/results/neural_open_set_comparison`
- ARPL统计：`source/CAEOS-EMTD/results/arpl_comparison`
