# Open-Detect 与 RoNeTC 统一协议对比及专家融合诊断

## 1. 目的与协议

本实验补齐两类与研究主题高度相关的方法。Open-Detect代表面向加密恶意流量未知攻击的高斯原型VAE；RoNeTC代表多视图Dirichlet意见、Dempster-Shafer融合与联合不确定性拒识。两者均保留论文核心目标和未知评分，但将原始图像或字节视图替换为CAEOS统一侧信道视图，因此属于同协议适配，不是原输入复现。

全部方法使用相同的DoH、Mal_TLS和HIKARI划分、样本上限与seed 7/11/19。未知类完全移出训练；模型选择只使用已知验证Macro-F1；拒识阈值只由已知验证风险的95%分位数确定。DoH为9次、Mal_TLS为18次、HIKARI为12次，共39次。

Open-Detect采用256维隐藏层、128维潜变量、100轮、生成约束权重0.005，并在第50/80轮用训练嵌入重置原型。RoNeTC采用三个独立视图编码器、Dirichlet证据损失、顺序Dempster-Shafer融合和联合意见不确定性风险，退火期10轮、训练上限100轮。服务器全套98项测试通过；两个正式矩阵均为39/39完成、0失败。

## 2. 全局结果

| 方法 | AUROC均值 | 标准差 | 最低值 | CAEOS差异 | CAEOS胜/平/负 | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| CAEOS v1.4.4门控 | `0.932796` | `0.075693` | `0.737747` | - | - | - |
| Open-Detect适配 | `0.792297` | `0.168835` | `0.349744` | `+0.140499` | `32/0/7` | `4.06e-07` |
| CLOSR适配 | `0.767187` | `0.229317` | `0.226182` | `+0.165609` | `33/0/6` | `2.40e-08` |
| RoNeTC适配 | `0.656010` | `0.238445` | `0.109809` | `+0.276786` | `38/0/1` | `3.64e-12` |
| CADE适配 | `0.630395` | `0.199313` | `0.040394` | `+0.302400` | `39/0/0` | `3.64e-12` |

Open-Detect的Known Macro-F1、Unknown AUPR、FPR95和OSCR分别为`0.948980`、`0.760402`、`0.434533`和`0.758458`；CAEOS对应为`0.974016`、`0.934910`、`0.175892`和`0.907870`。因此差异不仅来自阈值，排序质量、已知分类和开放集联合性能均支持CAEOS总体领先。

## 3. 分数据集结果与边界

| 数据集 | 运行数 | CAEOS | Open-Detect | RoNeTC |
|---|---:|---:|---:|---:|
| DoH | 9 | `0.867092` | `0.628822` | `0.616668` |
| Mal_TLS | 18 | `0.993660` | `0.909772` | `0.798031` |
| HIKARI | 12 | `0.890776` | `0.738691` | `0.472484` |

Open-Detect在HIKARI/Probing seed7、seed19，XMRIGCC seed7、seed11及Mal_TLS/Scanners三个seed上优于CAEOS，说明高斯原型VAE对部分结构距离型未知具有真实互补性。RoNeTC只在HIKARI/Bruteforce-XML seed19上优于CAEOS，且HIKARI均值仅`0.472484`。已知类分类精度可以很高而未知不确定性方向仍可反转，证明“低证据强度等于未知”不是稳定假设。

## 4. 自有算法优化诊断

首先将Open-Detect接入已知类内层留一专家门。HIKARI/Probing seed7中，Open-Detect外层比CAEOS高`0.027426`，但内层稳健目标低`0.373132`；XMRIGCC seed7外层高`0.082893`，内层目标低`0.198248`。无泄漏选择器均保留CAEOS。这说明外层优势不能由当前已知类伪未知任务预测，不能据此加入场景选择规则。

随后将两套风险分别映射到各自已知验证经验分位数，固定检验均值、概率并集、最大值和最小值融合。39次中最好的`rank_max`平均AUROC为`0.927336`，相对CAEOS下降`0.005455`，14胜25负；`rank_union`为`0.919691`，下降`0.013099`。固定融合也未满足升级条件。

因此稳定算法保持v1.4.4。Open-Detect专家门与固定融合均作为失败消融保留，不进入论文主方法。下一版优化应改变表征或诊断空间本身，而不是继续在外层困难任务上增加事后门控规则。

## 5. 当前SOTA范围

2025至2026年的TAO-Net、M3S-UPD和SiamXBERT分别引入LLM生成式未知细分类、半监督持续未知模式发现和未知类少样本适配。它们与当前“未知类训练期零样本、固定测试、不在线更新”的任务不同，应进入原协议复现层，不与本报告39次同协议分数直接配对。全面SOTA验收必须同时报告同协议适配表和原协议复现表，不能混合不同未知可见性、输入形态与更新权限。

## 6. 可复现产物

- 汇总表：`source/CAEOS-EMTD/results/external_strong_baselines_with_opendetect_ronetc_39`
- Open-Detect专家门先导：`source/CAEOS-EMTD/results/nested_opendetect_gate_pilot_20260714`
- Open-Detect固定融合：`source/CAEOS-EMTD/results/caeos_opendetect_fixed_fusion_exploratory_20260714`
- 适配实现：`source/CAEOS-EMTD/caeos/open_detect.py`、`source/CAEOS-EMTD/caeos/ronetc.py`
- 运行入口：`source/CAEOS-EMTD/run_neural_baseline_matrix.py`、`source/CAEOS-EMTD/run_nested_neural_gate_matrix.py`

