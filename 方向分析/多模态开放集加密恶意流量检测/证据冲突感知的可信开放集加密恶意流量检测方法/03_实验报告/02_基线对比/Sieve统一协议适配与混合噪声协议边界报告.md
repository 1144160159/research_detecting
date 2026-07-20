# Sieve统一协议适配与混合噪声协议边界报告

## 1. 来源与复现边界

Sieve来自2026年IEEE TDSC论文《Fine-Grained Detection and Analysis of Unknown Encrypted Malicious Traffic From Mixed Noisy Labels》，DOI为`10.1109/TDSC.2026.3697849`。官方仓库为`https://github.com/niebikong/Sieve`，2026-07-15核验HEAD为`d071e7abe362c23364ca6206197e0d9224df491f`。

论文原协议同时向训练集注入闭集错标和开集污染：Mal TLS2023作为23类已知流量，随机选择CipherSpectrum三类作为开集训练噪声，并以完整CipherSpectrum作为未知测试集。当前统一39任务则要求未知类完整离开训练、模型选择和阈值校准。因此本报告结果属于**Sieve核心算法的同划分适配**，不能替代或冒充论文混合噪声原协议结果。

CipherSpectrum官方下载需要提交姓名、邮箱、机构，并同意将姓名和机构列入数据用户页面。该授权信息不能代填，原协议复现保留为独立待办。

## 2. 官方实现审计与无泄漏适配

适配器保留以下核心机制：

1. 1D DeepResNet四层残差表征和多层池化特征；
2. 邻域一致性干净样本筛选与高置信标签扩展；
3. 类均衡监督训练、Mixup和批内自监督对比损失；
4. 选中训练子集上的类条件伪逆Mahalanobis未知风险。

官方仓库当前不能直接进入统一实验，原因包括作者机器绝对路径、在每轮训练后使用测试集准确率选择最佳checkpoint、全数据缩放后再切分，以及训练入口提供一个增强视图但训练循环解包两个视图。适配器分别改为命令行数据路径、已知验证Macro-F1选模、只用已知训练统计量预处理，并显式生成弱/强两个对比视图。未知阈值沿用统一协议，只使用独立已知验证风险的95%分位数。

实现与入口：

- `source/CAEOS-EMTD/caeos/sieve.py`
- `source/CAEOS-EMTD/train_sieve_open_set.py`
- `source/CAEOS-EMTD/run_neural_baseline_matrix.py --models sieve`

## 3. HIKARI 12次确认

HIKARI四个未知场景、seed 7/11/19的100轮上限确认结果如下。

| 方法 | AUROC | 标准差 | 最低值 | Known Macro-F1 | OSCR | 胜/平/负 |
|---|---:|---:|---:|---:|---:|---:|
| CAEOS v1.4.4 | `0.890776` | `0.073500` | `0.737747` | `0.974263` | `0.859763` | - |
| Sieve | `0.683302` | `0.315836` | `0.111273` | `0.931087` | `0.653100` | CAEOS `10/0/2` |

配对Wilcoxon为`p=0.012207`。Sieve仅在Bruteforce-XML seed7和Brutefoce seed11上取得AUROC优势，分别领先`0.036142`和`0.010114`；XMRIGCC三个种子仅为`0.250416/0.157043/0.111273`，暴露出类条件Mahalanobis风险的强场景依赖。

## 4. 同协议39次主结果

| 数据集 | 次数 | CAEOS AUROC | Sieve AUROC | CAEOS胜/平/负 | Wilcoxon p |
|---|---:|---:|---:|---:|---:|
| DoH | 9 | `0.867092` | `0.739576` | `9/0/0` | `0.003906` |
| Mal_TLS | 18 | `0.993660` | `0.834467` | `18/0/0` | `7.63e-06` |
| HIKARI | 12 | `0.890776` | `0.683302` | `10/0/2` | `0.012207` |
| 总计 | 39 | `0.932796` | `0.766057` | `37/0/2` | `9.09e-11` |

| 指标 | CAEOS v1.4.4 | Sieve | CAEOS定向优势 |
|---|---:|---:|---:|
| Known Macro-F1 | `0.974016` | `0.824835` | `+0.149181` |
| Unknown AUROC | `0.932796` | `0.766057` | `+0.166739` |
| Unknown AUPR | `0.934910` | `0.698239` | `+0.236671` |
| FPR95 | `0.175892` | `0.453812` | 改善`0.277919` |
| OSCR | `0.907870` | `0.659123` | `+0.248747` |

Sieve在统一矩阵中的AUROC与CLOSR的`0.767187`接近，低于Open-Detect的`0.792297`，高于FOSS、RoNeTC和CADE。同协议结果证明CAEOS总体领先，但不否定Sieve在混合标签噪声原任务上的论文贡献。

## 5. 固定融合与自有算法决策

将CAEOS和Sieve风险分别映射到各自已知验证经验分位数后，测试四种预注册固定融合。

| 融合 | 39次AUROC | 相对CAEOS | 胜/平/负 |
|---|---:|---:|---:|
| `rank_mean` | `0.880019` | `-0.052772` | `7/0/32` |
| `rank_union` | `0.901399` | `-0.031392` | `6/0/33` |
| `rank_max` | `0.909584` | `-0.023207` | `1/0/38` |
| `rank_min` | `0.837208` | `-0.095583` | `6/0/33` |

固定融合全部回退，不能利用两个Sieve胜例而不同时破坏大量任务。稳定算法继续保持v1.4.4；不依据外层未知标签构造场景级Sieve切换器。下一项自有算法优化应在新数据集或预注册拆分上检验，而不是继续对这39个外层任务调门。

## 6. 复现产物

- HIKARI 12次确认：`source/CAEOS-EMTD/results/sieve_same_split_confirmation_12`
- 完整39次矩阵：`source/CAEOS-EMTD/results/sieve_same_split_full39`
- 完整压缩归档：`source/CAEOS-EMTD/results/sieve_same_split_full39_metrics.tgz`
- 配对汇总：`source/CAEOS-EMTD/results/sieve_same_split_full39/comparison`
- 固定融合：`source/CAEOS-EMTD/results/sieve_same_split_full39/caeos_sieve_fixed_fusion.json`

结论：Sieve已作为第六项安全/网络开放集强基线进入统一39任务矩阵；其原始混合噪声协议与当前完整未知留出协议分开管理。
