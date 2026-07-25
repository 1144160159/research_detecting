# Recent SOTA baseline triage

更新时间：2026-07-25

## 2026-07-25 出版社记录刷新

- CLOSR 已正式对应 IEEE TNSM 2026 论文 *A Novel Contrastive Loss for Zero-Day Network Intrusion Detection*（DOI `10.1109/TNSM.2026.3652529`），作者仓库明确同时提供 CLAD 与 CLOSR。2026-07-25 查询的官方 HEAD 为 `79da4d1f...40f8`；本地 `source/CLOSR` 的README、requirements、train/eval和核心 `closr_loss.py` 五个关键文件与该HEAD逐SHA一致。它就是本项目已完成39任务统一协议适配的CLOSR，不得作为第43种方法重复计数；正式出版只增强基线身份，不改变既有负扩展结论。
- MalRAG（arXiv:2511.14129）是2025年新出现的直接开放集恶意流量识别路线，但任务人口是“已被IDS标记为可疑的流”，输入依赖payload、包长序列和到达间隔，多视图检索后调用Qwen3-32B等冻结LLM，公开指标为已知/新颖流量precision、recall、normalized accuracy。它没有覆盖未知良性误报安全，输入与成本也不等同于strict-v4无payload流级表格。当前公开记录未验证作者实现，故进入异构相关工作和未来独立协议候选，不做低保真表格适配、不增加正式方法数。
- OLPFF 已由 Information Sciences 记录为 2026 年论文（Vol. 753, 123646），任务同时覆盖开放集与长尾加密流量；它仍是本项目已登记的高优先级直接候选。出版社摘要不能补齐10种设置的类身份、长尾构造、known-only阈值来源、seed或作者实现，因此不改变“只进相关工作/独立协议候选、不进入 strict-v4 主表”的结论。
- TAO-Net 已由 Neurocomputing 记录为 2026 年论文（Vol. 679, 133170）。其第一阶段融合Transformer层间平滑性与PCA残差做ID/OOD检测，第二阶段使用生成式标签器处理OOD；本项目已有直接基线审计，当前流级表格stage-1适配不能冒充包含生成式第二阶段的完整原方法，故不重复计数。
- M3S-UPD 仍是2025年未知模式发现候选，本项目已有三场景pilot负/停止扩展证据；本次刷新没有形成新的主表准入理由。
- ETC-IMC（JISA 2026, 104433）解决少标注自监督加密流量分类与泛化，出版社摘要未给出静态开放集未知攻击拒识协议、known-only阈值或本项目五项未知指标。它可进入闭集/少样本相关工作，但不构成当前开放集主表缺口。
- EFC、MGN-OSR、CLOSR、OpenCBD、OLPFF、TAO-Net、M3S-UPD、MalRAG及其输入/代码/泄漏边界已覆盖当前检索返回的直接方法族。刷新后仍没有证据支持增加第43个低保真适配器；正式方法总账保持42，资源继续优先给MDR试点、保留种子确认、恶意外部、PARROT良性安全和部署效率。

## 已进入 strict 流级协议

- EFC：公开实现与当前流级表格输入接近；3 场景 pilot 中 AUROC 0.680736、OSCR 0.583681，低于 CAEOS 的 0.762808/0.699321，未通过扩展门。
- HCRP-OSD：已实现 1D residual CNN + 2D CNN + ARPL 论文结构适配器，并在 strict-v4 相同六场景、seed7、相同 split fingerprint 上完成 pilot。五项指标均落后于 CAEOS，16 方法未知指标平均秩第 12，停止扩展。该结果不是作者代码复现。
- ARPL：same-split tabular adapter 已在 strict-v4 六场景完成。Known F1/AUROC/AUPR/FPR95/OSCR 为 0.654862/0.695232/0.460482/0.551397/0.525703，18 方法平均秩第 15，四项未知指标均未击败 CAEOS，停止扩展。
- PALM/SSD+：same-split tabular-view adapter 已按 500 epoch 论文预算完成 strict-v4 六场景。Known F1/AUROC/AUPR/FPR95/OSCR 为 0.657173/0.765526/0.578564/0.543612/0.531623，18 方法平均秩第 12，四项未知指标均未击败 CAEOS，停止扩展。该结果不是作者代码复现。
- ODIN：按原论文/OpenOOD温度缩放与输入梯度符号扰动公式完成冻结MLP表格适配。为遵守无未知类调参边界，固定`T=1000`、标准化坐标`epsilon=0.001`，不复用原论文OOD留出调参。14场景Known F1/AUROC/AUPR/FPR95/OSCR为0.749150/0.686378/0.474673/0.542374/0.585939，相对Energy四项平均有向增益-0.001087，停止102场景扩展。
- ASH-S：按作者代码在冻结MLP倒数第二层实现ASH-S@90，GELU负值按既有SCALE适配边界先ReLU截断。14场景Known F1/AUROC/AUPR/FPR95/OSCR为0.706656/0.562880/0.405167/0.795492/0.457863，相对Energy四项平均有向增益-0.153814，7/7套件退化，停止102场景扩展。

## 可审计但暂不进入主表

- MEDAF：AAAI 2024通用OSR方法，官方commit `5d532833...3d16`和离线bundle `6c026975...78c4`已双端固定。原生实现因known/unknown test联合选阈值、逐epoch读取test及2D空间注意力输入差异而不准入。`MEDAF-Tabular adapter` 已在零结果时冻结42报告同拆分执行链，protocol canonical/file为 `b1ee2001...bc25/40b6f62c...6225`，GPU合并回归 `14/14 PASS`；watcher `2021310` 依次等待Pairwise比较summary和MDR pilot，当前metrics/summary/audit仍为 `0/0/0`，不增加正式方法数。
- OpenCBD：2022年开放全文直接处理加密未知流量，ISCXVPN2016协议为8个known、5个unknown、每类1,000个10包payload序列；阈值来自known-training最大1%异常距离，不用unknown/test拟合。GPU有5个原始ZIP候选，但作者代码、固定类表、seed、依赖和机器可读配置均未发布，且payload序列与strict-v4无payload流级表格不同。只进入相关工作和协议附录，不做低保真表格适配，不增加正式方法数。
- Guardians of the Network：2025 年流量分类 benchmark 比较 7 种方法和 14 个流量数据集，可用于检查闭集流级分类覆盖。论文指向的 GitHub 仓库在 2026-07-18 检查时不可用；在代码、开放集划分、未知类隔离和连续风险分数可审计前不进入主表。
- OpenPN：2026年Journal of Computer Security直接开放集网络检测工作。出版社为restricted access，OpenAlex记录closed且无仓储全文；三组GitHub repository查询均为0，公开检索未验证作者实现，但负检索不等于证明代码不存在。摘要确认完整框架在OpenPN识别后由专家确认未知类、执行k-reciprocal聚类并持续学习，因此整体不兼容静态零未知暴露；第一层OpenPN仅保留全文/作者代码可用后的条件候选。audit canonical/file为 `a5a0248a...3505/9245cd2b...141a`，本地/GPU `6/6 PASS`，模型指标和正式方法增量均为0。
- CNN-RPL：IEEE Access 2024直接DDoS开放集方法，官方全文给出7个Conv1D、3次MaxPool、二维RPL嵌入、18,872参数、10个种子及CICIDS2017→CICDDoS2019跨数据集协议。GPU两套原始源候选为2/2；但作者实现未验证，唯一同名GitHub仓库commit `a4c35262...3238`是非作者sklearn学生项目且把CNN列为未来工作。论文未发布确定预处理、完整pool/scheduler参数或processed manifest，并称 `lambda=0.3`、阈值0.7为优化未知识别而选择，未记录known-only validation。只进入相关工作和数据就绪的原生外部协议候选；禁止把既有ARPL adapter改名为CNN-RPL，模型指标和正式方法增量均为0。
- SINFlow：CMC 2025直接未知DDoS方法，使用AE编码、二分类DNN与GIS密度估计；阈值为known-training log-density第1百分位。GPU已有CICIDS2017与CICDDoS2019原始候选2/2，底层2021 SINF官方仓库固定commit `450ee7bf...a58`。但该仓库不是2025 IDS实现；论文缺AE/DNN结构、epoch、GIS迭代/切片参数、缩放拟合范围和跨数据集特征映射，且正文的10次/16种子/20次训练互相矛盾。原始CSV实际为79/88列、共享78列，论文未发布processed manifest。静态未知模块只报告ODR，0.9999 F1来自专家标注未知后的增量学习，禁止当作zero-shot成绩。evidence/audit canonical为 `783454e4...f82f/698f398b...f892`，本地/GPU `10/10 PASS`、8工件逐SHA一致；只进入相关工作和数据就绪的原生外部协议候选，正式方法增量0。

## 异构输入，仅作单列实验或未来工作

- MalRAG：以IDS预筛后的可疑流为人口，依赖payload、包长/到达间隔序列、多视图检索和大语言模型推理；不评价全流量未知良性误报，不能与strict-v4流级表格同主表直接比较。
- DIDS-MFL：依赖 `src,dst,t,dt,msg` 时序图、PyG/TGNMemory/MGD；当前 strict 主表主动移除标识字段，不能称为原方法复现。
- SAFE-NID：以原始包和 Transformer 为核心，属于 packet-level 输入。
- OVID：开放词汇入侵检测依赖视觉/语言对齐输入，不能与流级闭集已知分类加未知检测主表直接混排。
- MGN-OSR：从原始流量、TLS 握手和统计特征生成 RGB 图像；作者仓库仅公开部分特征/RGB 生成材料，主方法未公开。
- VAEMax：依赖 flow payload 序列、1D-CNN、OpenMax 和逐类 VAE；与无 payload 的 strict 表格输入不一致，且未确认作者完整公开实现。

## 来源

- MEDAF paper: https://doi.org/10.1609/aaai.v38i6.28385
- MEDAF official code: https://github.com/Vanixxz/MEDAF
- Guardians of the Network paper: https://link.springer.com/article/10.1007/s10489-025-06422-4
- Guardians of the Network code link: https://github.com/UOttawa-Cyber-Range-Research/GuardiansOfTheNetwork
- OpenCBD paper: https://doi.org/10.1155/2022/1746373
- HCRP-OSD paper: https://onlinelibrary.wiley.com/doi/abs/10.1002/cpe.70010
- DIDS-MFL repository: https://github.com/qcydm/DIDS-MFL
- DIDS-MFL paper: https://doi.org/10.1109/TPAMI.2025.3595671
- SAFE-NID code: https://github.com/SRI-CSL/trinity-packet
- OpenPN paper: https://doi.org/10.1177/0926227X251414058
- CNN-RPL paper: https://doi.org/10.1109/ACCESS.2024.3388149
- SINFlow paper: https://doi.org/10.32604/cmc.2025.061001
- SINF core code: https://github.com/biweidai/SINF
- MGN-OSR paper: https://doi.org/10.1016/j.comnet.2024.110824
- MGN-OSR partial repository: https://github.com/BeerHan/Code-and-data-for-MGN-OSR
- VAEMax preprint: https://arxiv.org/abs/2403.04193
- ODIN paper: https://arxiv.org/abs/1706.02690
- OpenOOD ODIN postprocessor: https://github.com/Jingkang50/OpenOOD/blob/main/openood/postprocessors/odin_postprocessor.py
- ASH paper: https://arxiv.org/abs/2209.09858
- ASH official code: https://github.com/andrijazz/ash/blob/main/ash.py
- OLPFF publisher record: https://doi.org/10.1016/j.ins.2026.123646
- TAO-Net publisher record: https://doi.org/10.1016/j.neucom.2026.133170
- M3S-UPD preprint: https://arxiv.org/abs/2505.21462
- ETC-IMC publisher record: https://doi.org/10.1016/j.jisa.2026.104433
- CLOSR paper: https://doi.org/10.1109/TNSM.2026.3652529
- CLOSR official code: https://github.com/jackwilkie/CLOSR
- MalRAG preprint: https://arxiv.org/abs/2511.14129
