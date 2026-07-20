# Recent SOTA baseline triage

更新时间：2026-07-18

## 已进入 strict 流级协议

- EFC：公开实现与当前流级表格输入接近；3 场景 pilot 中 AUROC 0.680736、OSCR 0.583681，低于 CAEOS 的 0.762808/0.699321，未通过扩展门。
- HCRP-OSD：已实现 1D residual CNN + 2D CNN + ARPL 论文结构适配器，并在 strict-v4 相同六场景、seed7、相同 split fingerprint 上完成 pilot。五项指标均落后于 CAEOS，16 方法未知指标平均秩第 12，停止扩展。该结果不是作者代码复现。
- ARPL：same-split tabular adapter 已在 strict-v4 六场景完成。Known F1/AUROC/AUPR/FPR95/OSCR 为 0.654862/0.695232/0.460482/0.551397/0.525703，18 方法平均秩第 15，四项未知指标均未击败 CAEOS，停止扩展。
- PALM/SSD+：same-split tabular-view adapter 已按 500 epoch 论文预算完成 strict-v4 六场景。Known F1/AUROC/AUPR/FPR95/OSCR 为 0.657173/0.765526/0.578564/0.543612/0.531623，18 方法平均秩第 12，四项未知指标均未击败 CAEOS，停止扩展。该结果不是作者代码复现。
- ODIN：按原论文/OpenOOD温度缩放与输入梯度符号扰动公式完成冻结MLP表格适配。为遵守无未知类调参边界，固定`T=1000`、标准化坐标`epsilon=0.001`，不复用原论文OOD留出调参。14场景Known F1/AUROC/AUPR/FPR95/OSCR为0.749150/0.686378/0.474673/0.542374/0.585939，相对Energy四项平均有向增益-0.001087，停止102场景扩展。
- ASH-S：按作者代码在冻结MLP倒数第二层实现ASH-S@90，GELU负值按既有SCALE适配边界先ReLU截断。14场景Known F1/AUROC/AUPR/FPR95/OSCR为0.706656/0.562880/0.405167/0.795492/0.457863，相对Energy四项平均有向增益-0.153814，7/7套件退化，停止102场景扩展。

## 可审计但暂不进入主表

- Guardians of the Network：2025 年流量分类 benchmark 比较 7 种方法和 14 个流量数据集，可用于检查闭集流级分类覆盖。论文指向的 GitHub 仓库在 2026-07-18 检查时不可用；在代码、开放集划分、未知类隔离和连续风险分数可审计前不进入主表。
- OpenPN：论文可检索，但未确认有公开、可审计的作者实现。

## 异构输入，仅作单列实验或未来工作

- DIDS-MFL：依赖 `src,dst,t,dt,msg` 时序图、PyG/TGNMemory/MGD；当前 strict 主表主动移除标识字段，不能称为原方法复现。
- SAFE-NID：以原始包和 Transformer 为核心，属于 packet-level 输入。
- OVID：开放词汇入侵检测依赖视觉/语言对齐输入，不能与流级闭集已知分类加未知检测主表直接混排。
- MGN-OSR：从原始流量、TLS 握手和统计特征生成 RGB 图像；作者仓库仅公开部分特征/RGB 生成材料，主方法未公开。
- VAEMax：依赖 flow payload 序列、1D-CNN、OpenMax 和逐类 VAE；与无 payload 的 strict 表格输入不一致，且未确认作者完整公开实现。

## 来源

- Guardians of the Network paper: https://link.springer.com/article/10.1007/s10489-025-06422-4
- Guardians of the Network code link: https://github.com/UOttawa-Cyber-Range-Research/GuardiansOfTheNetwork
- HCRP-OSD paper: https://onlinelibrary.wiley.com/doi/abs/10.1002/cpe.70010
- DIDS-MFL repository: https://github.com/qcydm/DIDS-MFL
- DIDS-MFL paper: https://doi.org/10.1109/TPAMI.2025.3595671
- SAFE-NID code: https://github.com/SRI-CSL/trinity-packet
- OpenPN paper: https://doi.org/10.1177/0926227X251414058
- MGN-OSR paper: https://doi.org/10.1016/j.comnet.2024.110824
- MGN-OSR partial repository: https://github.com/BeerHan/Code-and-data-for-MGN-OSR
- VAEMax preprint: https://arxiv.org/abs/2403.04193
- ODIN paper: https://arxiv.org/abs/1706.02690
- OpenOOD ODIN postprocessor: https://github.com/Jingkang50/OpenOOD/blob/main/openood/postprocessors/odin_postprocessor.py
- ASH paper: https://arxiv.org/abs/2209.09858
- ASH official code: https://github.com/andrijazz/ash/blob/main/ash.py
