# 019 MTRF：网络流时域-频域变换表征

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | PDF页 | 本卡 | 状态 |
|---|---:|---|---|
| Abstract / Introduction / Framework | 1-3 | 第1-3节 | 已覆盖 |
| Methodology | 4-7 | 第4-5节 | 已覆盖 |
| Experiments | 7-13 | 第6-8节 | 已覆盖 |
| Resources / Conclusion | 13-14 | 第9-10节 | 已覆盖 |

## 1. 文献身份与摘要缩译

作者为 Xinlei Wang、Mingshu He、Xiaojuan Wang 和 Shize Guo，发表于 IEEE Transactions on Dependable and Secure Computing，23(3)，2026，DOI 为 10.1109/TDSC.2025.3649110。

MTRF 面向少标注、资源受限 IoT 入侵检测，把每条网络流同时转换为时域序列和频域幅度表示。时域分支用动量编码器学习对网络诱导噪声稳定的短期趋势；频域分支用带 hard margin 的监督对比损失提升少数类分离。训练后的表征交给 Extra Trees、RF、DT 或 XGBoost 等轻量分类器。

## 2. 引言与框架缩译

论文认为端到端分类容易把丢包、重排、时延等环境噪声与攻击语义纠缠。时域适合表示趋势和局部波动，频域更稳定地表示周期性。二者分开训练可避免不可靠时域扰动污染频域表征。云端用少量样本训练 MTRF，雾节点负责表征，边端设备运行轻量分类器。

## 3. 相关工作缩译

相关工作涵盖端到端 IDS、自动编码器预训练、图表征、拓扑表征、监督对比学习和时序预测。作者批评现有多模态方法可能纠缠模态特有与共享信息，也指出大型预训练和多 GPU 方案不适合资源受限雾端。

## 4. 预处理与双域表征缩译

每条 flow 被组织为 N 个 packet、每包 M 个字段的矩阵 Fₖ，再展平为长度 N×M 的向量。论文模拟丢包、时延、重排和重传等网络诱导扰动，并把训练数据增强 8 倍。时域分支采用 query encoder 与动量更新的 key encoder，利用历史负样本队列保持表征一致。

频域分支对流表示做离散傅里叶变换，使用幅度谱。监督对比损失在类内拉近、类间推远，并用 margin γ 强化困难负样本。最终时域与频域表示拼接或联合输出给下游树模型。它是同一流派生的双视图，不是独立传感器多模态。

## 5. 实验协议缩译

论文用 UNSW-NB15、MQTT-IoT-IDS2020、USTC-TFC2016、CICDDoS2019 和 TON-IoT，构造 T1-T5 五种不同规模及平衡度任务。少样本任务中训练样本远少于测试样本，并比较 14 个表示/分类方案。全文未给出统一的 capture-grouped split 和独立 known-only validation；T1-T5 是闭集或二元检测任务，不是攻击家族开放集。

## 6. 主结果缩译

摘要报告 UNSW-NB15 平衡训练设置下 Accuracy 0.9699，其他最佳模型为 0.6300。MQTT 不平衡任务的最佳 F1 为 0.9802。TON-IoT 二元不平衡实验使用 9,500 benign、500 attack，其中训练 100、测试 9,900；MTRF-ET 得到 FP = 0、FN = 74，普通 ET 为 FP = 63、FN = 404。

这些结果说明表征对极少训练样本有潜力，但单次 FP = 0 不等于跨种子、跨场景 FAR 保证，也没有 unknown-positive FPR95。

## 7. 跨数据集与统计分析缩译

在 MQTT 上训练表征后直接应用到 USTC-TFC2016，Cridex 和 Geodo 的 AUC 从从头训练的 0.92/0.96 降到 0.90/0.94。用 CICDDoS2019 训练再迁移到 USTC-TFC2016，AUC 约下降 2%。论文据此称双域表示有一定跨数据集泛化，但攻击语义相似度与特征 schema 一致性仍会影响结论。

MANOVA 比较表征前后频域分布；表征后部分统计量显示更强类间分离。论文还可视化不同攻击类的幅度谱。

## 8. 资源消耗缩译

训练 RES 约 3.038 GB，CPU 约 13 cores，模型文件约 150 MB。雾端推理的资源占用较低。作者主张分离表征与分类便于按设备资源选择 ET、RF、DT 或 XGBoost。

## 9. 局限缩译

跨数据集只验证少数方向，schema、标签空间和攻击相似度没有系统控制；训练扰动是预设增强，并不覆盖真实缺失模态或对抗冲突；论文没有开放集拒识、校准和冻结阈值实验。

## 10. 结论缩译

MTRF 的主要贡献是时域与频域分离对比表征，在小样本、失衡和有限跨域下提高树模型性能。它应被视为双视图表征基线，而非未知攻击检测方法。

# 第二部分：独立技术分析

## A. 身份、协议与状态

- 角色：C-双视图强表征；状态：`project_mapped`。
- 本地 PDF：`paper/10.1109_TDSC.2025.3649110.pdf`。
- 协议：`P3-closed-set-small-sample-and-transfer`；没有 unknown 阈值。
- 多模态判定：时域与频域来自同一流，属于同源双视图。
- 公式格式：Unicode display；Zotero/Citation Key pending。

## B. CAEOS 采纳与95%/5%判断

采纳 DFT 幅度谱作为第三表征候选和网络扰动增强；不把其与独立 payload/statistics/source-context 三模态等同。论文只能支持闭集强表征和 FAR 组件候选，不能证明 Known Macro-F1、Unknown FPR95、OSCR 或校准达标。

`E-MTRF-01`：同一 strict-v4 split 下比较 sequence-only、statistics-only、frequency-only、time+frequency 和 CAEOS 三模态；预处理只在训练折拟合，5 seeds。若频域只改善闭集 F1 而 unknown AUROC/OSCR 不升，保留为闭集支线而不进入主融合。

## C. 最终审计

- G0-G1、G3-G9：通过。
- G2：DOI 已核，Zotero 待核。
- G10：未通过。
- 最终状态：`project_mapped`。
