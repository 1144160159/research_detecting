# CAEOS-EMTD 评价驱动的目标纠偏与执行路线

更新时间：2026-07-20 22:56（北京时间）。

评价来源：`C:\Users\LongShine\Downloads\CAEOS-EMTD评价.pdf`。

## 1. 纠偏后的总目标

“全面 SOTA”不再解释为继续增加方法数量或不断替换算法，而是要求以下证据分别闭环：

1. 准确性：冻结算法在独立新种子上相对最强外部比较器具有确认性优势；
2. 稳健性：缺失、噪声、置换、缩放、训练标签噪声等威胁下优雅退化；
3. 效率：同硬件、同输入、同计时边界下给出端到端训练与推理证据；
4. 真实异构输入：至少一个数据集不只是同一张表的 feature-group 切分；
5. 泛化：至少完成跨域或跨时间测试；
6. 可审计性：算法、版本、协议、结果目录和统计推断能够唯一对应。

任一维度未闭环时，不使用“全面 SOTA”。论文主命题收缩为：区分证据不足与可靠证据冲突，并通过条件归一化冲突和可靠度折扣，在不使用真实未知类别校准的条件下进行开放集流量检测。

## 2. 主算法与探索算法分轨

### 2.1 论文冻结主算法

- 框架：`CAEOS-EMTD`；
- 当前论文算法：`CAEOS-Pairwise`；
- 代码标识：`caeos_pairwise`；
- 当前状态：冻结 incumbent，Router、Tail-aware、Anchor 只作开发候选或消融；
- 替换规则：新候选必须先通过预注册开发试点，再使用完全未参与开发的三新种子完成 102 场景确认，且同时通过 bootstrap、Holm、Known F1 和每套件无回退门。

### 2.2 自有算法探索线

自有算法探索继续保留，但不得修改或污染论文主结果链。当前新候选为 `caeos_lcb_tail_aware`：

- 保留 Tail-aware 的单调 pairwise 排序头；
- 在 known-only 留一攻击伪未知折上，以四指标单侧置信下界选择 gamma 和收缩强度；
- 单独要求 AUPR 下界及最差折不低于冻结阈值；
- 证据不足时回退到 `cauchy_modality_support_union`；
- 试点 seed 为 `191`，14 个跨套件困难场景；
- 预留确认 seeds 为 `197/199/211`；
- 当前为 `0/14` 零结果协议，不能写入效果结论。

探索代码部署在独立 GPU 目录：

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720`

当前协议 SHA：`362d6c5eb096e770fe906f2f95c90b27d7c534a314a7d117d3f32fc6fc9592e1`。旧 SHA `27732c3ca05cf351d9c6f0428315d8099d5d7abfe399b059d8bd2ba3b295b302` 在 `0/14` 状态下被完整性加强版替代并归档。远端协议/实现哈希校验通过，watcher PID 为 `827015`。watcher 必须等待主论文终审完成且 GPU 连续空闲后才运行。

## 3. 基线策略纠偏

现有 30 方法 full102 发展表已经足够证明比较广度。主表只保留：MSP/Energy、Mahalanobis、KNN、OpenMax、ARPL、OpenDetect、一个训练型强基线、一个树模型开放集方案和 CAEOS 关键消融；其余方法进入扩展表或附录。

NPOS 扩展 watcher 已停止，真实结果保持 `0/14`。停止原因不是否定 NPOS，而是当前边际价值低于确认、污染、效率、真实异构模态和自有算法探索。若后续审稿或主表结构确实需要，再以单独资源预算恢复。

## 4. 新完成的确认性结果

Pairwise 与 OpenDetect 的独立确认已完成 `306/306`，失败 `0`。统计单位为 102 个场景，三个新种子 `137/139/149` 先在场景内平均。

| 指标 | Pairwise | OpenDetect | 有向均值增益 | bootstrap 95% CI | 判定 |
|---|---:|---:|---:|---:|---|
| Known macro-F1 | 0.794300 | 0.762873 | +0.031427 | [+0.026757, +0.036396] | 通过 |
| AUROC | 0.773355 | 0.716103 | +0.057252 | [+0.026906, +0.089224] | 通过 |
| AUPR | 0.584167 | 0.511447 | +0.072720 | [+0.043515, +0.103027] | 通过 |
| FPR95 | 0.485244 | 0.527120 | +0.041876 | [-0.017359, +0.101159] | 均值改善但未确认 |
| OSCR | 0.631643 | 0.582429 | +0.049214 | [+0.017861, +0.080428] | 通过 |

场景阻塞推断的主要确认门通过，但严格全指标/全套件替换门失败：

- FPR95 的 Holm/置信下界门未通过；
- CIC-IoT2023 四项未知指标均回退；
- CIC-ToN-IoT 的 AUROC、AUPR、FPR95 回退；
- NF-UNSW-NB15 的 FPR95 回退；
- CICIDS2017、Edge-IIoT、NF-CSE 和 USTC-TFC2016 四项均为非负增益。

因此可写结论是“Pairwise 相对 OpenDetect 具有确认性的总体优势，尤其体现在 Known F1、AUROC、AUPR 和 OSCR”；不可写结论是“所有指标和所有数据集均达到 SOTA”。综合准确性审计的 claim tier 为 `self_algorithm_confirmed_external_sota_unconfirmed`。

## 5. 真实异构模态与泛化纠偏

GPU 原始池核验结果：

- `Mal_TLS2023`：约 82 MB，已有 TLS 握手、IP 流统计、载荷统计和 30 位包序列四组输入，是当前最适合构建异构编码器实验的数据；
- `HIKARI2021`：约 547 MB，已有严格分组审计，更适合作为跨域/跨采集环境泛化测试；
- `LSNM2024`：约 2.4 GB，含 15 个恶意目录类别，但字段和多个 CSV 尚需统一，暂不直接进入确认主表。

真实异构模态实验的最低实现要求：

1. 流统计使用 MLP；
2. 包长/方向序列使用 TCN 或 Transformer；
3. TLS 握手字段使用独立离散/连续编码器；
4. 融合前分别输出类别证据、可靠度和缺失掩码；
5. 与“统一表格编码器 + feature groups”在相同拆分下比较；
6. 进行单模态缺失、噪声和延迟消融。

若该实验不能按以上条件完成，论文标题和全文统一使用 `multi-view`，不使用“真实多模态”或过宽的“Encrypted Malicious Traffic Detection”主张。

## 6. 执行优先级

### P0：主论文闭环

1. 完成同机效率 v2；
2. 完成 783 次候选污染矩阵；
3. 完成 Pairwise–OpenDetect 的 1530 次同条件配对污染评估；
4. 生成最终论文支撑性审计；
5. 固化唯一主结果目录和版本映射。

### P1：自有算法与安全实证

1. 运行 LCB Tail-aware 14 场景 seed191 试点；
2. 只有过门才创建 306 次新种子确认协议；
3. 将污染鲁棒性提升为正文主表；
4. 建立 Mal_TLS2023 异构编码器实验；
5. 建立 HIKARI2021 跨域测试。

### P2：理论与表达

补充冲突有界性、对称性、一致意见零冲突、条件归一化与总证据解耦、可靠度下降时污染影响单调减小，以及复杂度 `O(M^2 K)` 的性质说明。Router、Tail-aware、Anchor 和大量后处理分数不再并列包装为主要创新。

## 7. 投稿定位

- 冲高目标：IEEE TIFS；前提是 P0 完成，并至少补齐真实异构模态或跨域泛化；
- 现实目标：Computers & Security、RAID/ACSAC；
- TDSC：只有污染容错、效率和长期/跨域运行证据成为主线后再考虑；
- 当前不按 USENIX Security、CCS、NDSS、IEEE S&P 完成态进行表述。

本次纠偏不降低研究目标，而是把资源从“更多方法数量”转移到“可确认的自有算法、真实输入、攻击者模型、效率和可复现证据”。

## 8. 纠偏落地状态（22:56）

- 主链：OpenDetect 独立确认维持 `306/306`；正式效率协议 SHA 为 `1534d91600e5e0d8b9ec2941f6c8232f541b1adbff34918514f75730263c8593`，执行计划 SHA 为 `788e0fa73c072f459a5452d1d9acca36814527e88ab5cd3ac681b0b0190539f3`。watcher PID 为 `1127471`，executor PID 为 `1127506`，已从首个候选捕获自动进入 OpenDetect GPU 对照训练。
- 数值审计：首个全量候选捕获已经通过。源预测数组完全一致；参与风险计算的原始组件最大误差为 `2.220446049250313e-16`，低于 `1e-12`；部署运行时同设备重复前向风险差为 `0.0`。源经验尾风险差 `0.0019079552294392066` 保留为并列秩非连续诊断字段，不参与放宽判定。
- 自有算法：LCB Tail-aware 继续保留，完整性加强版协议 SHA 为 `362d6c5eb096e770fe906f2f95c90b27d7c534a314a7d117d3f32fc6fc9592e1`，仍为 `0/14`，watcher PID 为 `827015`。
- 真实异构输入：Mal_TLS2023 已完成 TLS 门控编码器、IP/载荷 MLP、包序列 TCN 的端到端代码烟测；烟测低精度不作为论文证据。成对开发协议已经冻结，协议 SHA 为 `a0d31ec5434e647942b94e3b23188ef5a560aa66d7037a7cc2d68ec9e6e53126`，比较统一 MLP 与异构编码器在 6 个未知家族上的表现，开发 seed 为 `191`，保留确认 seeds 为 `197/199/211`。
- 调度：异构编码器 watcher PID 为 `1020309`，必须等待 LCB 试点完成并连续确认 GPU 空闲后才运行，避免污染正式效率、污染鲁棒性和自有算法开发结果。

## 9. OpenDetect 数值等价纠偏与恢复（23:19）

- 首次 OpenDetect 训练捕获完成了 100 epochs，但训练过程内存 logits 与保存检查点重放风险的最大差为 `1.52587890625e-05`。预测数组完全一致；该差异属于 FP32 保存后重放诊断，不能冒充正式同设备影子等价，也不能通过简单放宽阈值解决。
- 使用同一检查点独立构造两个 CUDA 部署运行时复核后，预测数组完全一致，风险最大差为 `0.0`。训练捕获器已纠正为：正式门只比较独立同设备影子，继续要求 `1e-12`；训练内存输出仅写入 `source_score_diagnostic`，明确标记为非正式参考。
- 修复后的效率链回归测试为 `34/34 PASS`。OpenDetect 训练捕获实现 SHA 为 `a16d1877a1982817eaa6548e5b539952b040414157edac190182ce39d9e50e9e`，效率汇总器 SHA 为 `4158914eaade7e6e784aa1017d4ed5239328e728fe5f3bb7bba9e4213342d838`。
- 新正式效率协议 SHA 为 `c94035f4f87631aca8904074e57198bc24111e24df5749228d24469ac9408c0c`，新执行计划 SHA 为 `820b9115ee911ae86fe9c6a0a1ecbe582837e0837aad00845f6aa60cad28f2c0`。旧协议与旧计划以 `superseded-20260720-opendetect-shadow-fix` 后缀归档。
- 恢复 watcher PID 为 `1242820`，executor PID 为 `1242854`，已重新进入首个 OpenDetect 对照训练。此前通过的 Pairwise 候选捕获保持不变并由执行计划完整性检查复用。
- 修复后的首个真实训练捕获已经通过 `strict_v4_opendetect_runtime_equivalence_v2`：预测完全一致、同设备影子风险最大差 `0.0`、正式阈值 `1e-12`，来源诊断差仍为 `1.52587890625e-05` 且 `is_formal_equivalence_reference=false`。执行器已自动进入 `rep1`。
- 自有算法探索仍为必要实验，不因主链修复而取消。LCB Tail-aware 与 Mal_TLS2023 异构编码器 watcher 分别保持 `827015` 和 `1020309`，按“主终审 -> LCB 试点 -> 异构编码器试点”的独占 GPU 顺序自动执行。

## 10. 第 31 个强基线：WDiscOOD（23:52）

现有 30 方法已覆盖概率、能量、距离、近邻、ViM、Mahalanobis++、CEA、SIRC、ExCeL 和多种训练型开放集方法，但缺少同时建模类判别子空间与类无关残差子空间的 WLDA 路线。因此新增 ICCV 2023 WDiscOOD，而不是继续堆叠同类 logit 分数。

- 适配对象：冻结 strict-v4 MLP 的 pre-logit embedding；不重新训练主干。
- 拟合数据：仅已知训练集嵌入；拒识阈值仅由已知验证集 95% 接受率校准。
- 判别维度：固定为 `min(C-1, d-1)`；残差权重 `alpha=1.0`、ridge=`1e-6` 均在结果前固定，不使用未知测试数据选参。
- 分数：WLDA 判别空间中的最近已知类中心距离，加上判别残差空间中的已知训练总体中心距离。
- 试点：7 套件各 2 个由覆盖清单 SHA 决定的场景，共 14 场景；与同检查点标准 Mahalanobis 和同拆分 OpenDetect 比较。
- full102 扩展门：14/14、零失败、SHA/拆分/无泄漏检查全部通过；相对标准 Mahalanobis 四项未知指标有向均值非负；至少 5/7 套件非负；三方法平均秩不高于 2.0；Known F1 与来源 MLP 差不超过 `1e-12`。

代码、评估器、冻结协议、runner、summarizer 和 watcher 已部署，数值/协议测试 `8/8 PASS`。watcher PID 为 `1460599`，先等待正式效率 `execution_complete`，再冻结零结果协议；随后等待 LCB 与 Mal_TLS2023 异构探索完成，最后以 CPU 单进程执行，避免污染当前效率计时和自有算法结果。

## 11. 泛化证据二次纠偏：DoH 跨采集时间外推（00:35）

重新核查后，HIKARI2021 的攻击类别与单一来源主机高度绑定，现有 `SourceGroup`/指纹分组只能防止样本重复跨集合，不能把来源主机与攻击语义解耦。因此停止把 HIKARI 随机或指纹分组实验描述为“跨域泛化”。

DoHBrw2020 文件名含真实采集时间，且现有审计样本显示：`iodine` 为 2020-03-18 至 03-23，`dnscat2` 为 03-23 至 03-29，`dns2tcp` 为 03-30 至 04-01；可构建更严格但仍有边界的“同数据集跨采集时间外推”试点：

- 已知类固定为 `benign/dnscat2/iodine`，未知类固定为时间上更晚的 `dns2tcp`；
- 每个已知类内部按 `CaptureTime` 升序切为 70% 训练、15% 验证、15% 未来测试，`CaptureId` 不跨集合；
- 预处理只拟合早期训练数据，拒识阈值只由已知验证集校准；
- 三个新种子 `223/227/229` 比较冻结 CAEOS-Pairwise 与 OpenDetect；
- 五项有向均值至少四项非负才通过试点门，但结果只作为时间外推证据，不用于回调 Pairwise 参数，也不称为跨数据集或跨机构泛化。

已新增通用 `temporal_capture_grouped` 切分、DoH 时间解析/全采集准备器、零结果协议生成器、runner、summarizer 和测试。新增测试 `3/3 PASS`，既有严格切分回归 `1/1 PASS`。执行排在正式效率、LCB、Mal_TLS2023 和 WDiscOOD 之后，避免 GPU 与 I/O 干扰。

## 12. LCB 自有候选预运行完整性加固（2026-07-21）

在正式结果仍为 `0/14` 时审计发现，原分析器只核验 LCB 四个置信门参数，没有把伪未知最大混合强度、最差折阈值、边界困难样本比例、插值、每任务上限、风险策略名，以及 known-only 总门、最差折门与最终 endpoint 的一致性全部设为硬错误。算法与冻结门槛均未修改，只加强审计：

- 所有可配置参数必须与协议逐项相等；
- learned gate 的四项检查、`passes` 与 `selected_alpha` 必须自洽；
- robust fold gate 必须与 learned gate、`minimum_fold_gain` 自洽；
- 最终 `selected_risk` 必须严格等于总门决定的候选或冻结回退 endpoint；
- 任一字段缺失、漂移或矛盾均拒绝汇总。

协议/分析器与 tail-aware 数值回归合计 `11/11 PASS`。旧协议已保存为 `protocol_manifest.superseded-integrity-v1.json`，新协议 SHA 为 `362d6c5eb096e770fe906f2f95c90b27d7c534a314a7d117d3f32fc6fc9592e1`；远端和本地权威副本一致，冻结时仍无模型结果。

## 13. 外部失败集中度与下一候选方向（2026-07-21）

对三新种子 102 场景确认结果进行结果后诊断：AUROC/AUPR/FPR95/OSCR 分别有 `36/26/47/30` 个回退场景，灾难性回退分别为 `9/7/21/12` 个；每项指标最差 5 场景占其全部负收益质量的 `50.6%/53.8%/40.9%/51.6%`。这说明主要缺口是少数家族的尾部崩溃，而不是总体排序普遍落后。

严重场景定义为四项至少三项回退或任一项有向增益不高于 `-0.1`，共 `35` 个；冻结 LCB 试点覆盖 `7/35`。因此保持“LCB 先行、不得按外部标签换场景”的预注册纪律，但不把 LCB 试点等同于完整失败覆盖。若 LCB 确认后未覆盖场景仍主导回退，下一候选转向表示层或 known-only 安全路由；Mal_TLS2023 异构编码器先验证表示层假设。详细报告见 `Pairwise-OpenDetect失败集中度与自有算法决策_2026-07-21.md`。

## 14. 自有算法继续探索与 VOS 基线补齐（2026-07-21）

纠偏后不停止自有算法探索。`CAEOS-Pairwise` 只是当前确认性 incumbent；LCB Tail-aware 继续验证尾部下界选择，Mal_TLS2023 异构编码器继续验证真实模态表示是否能修复外部失败集中场景。两条路线均保持预注册门、隔离目录和失败即回退，不根据 OpenDetect 外部测试标签追加分数或改场景。

基线覆盖审计同时发现，现有方法虽包含 NPOS，但缺少 VOS 的“类条件共享协方差 + 低似然虚拟异常 + 能量正则”训练路线。现已新增独立 VOS 模块、训练器、14 场景零结果协议、冻结扩展门、SHA 绑定 runner、summarizer 和等待 DoH 完成后的 GPU watcher。官方核心公式与普通 energy 评估保留，队列、候选数、训练预算和优化器的表格适配均显式披露；VOS 不得被表述为自有算法。

静态编译通过，新增 VOS 单元/协议测试在本地与 GPU 项目均为 `7/7 PASS`，2-epoch CPU 合成训练成功生成完整三件套。远端协议在 `0/14` 结果下冻结，SHA 为 `9669965f282d5832b9dcaf460ed85b2882e14dbe4b1060376bd8498174f05903`；watcher PID `1930188` 正等待 DoH 完成，正式结果仍为 0。只有 14 场景全部完成且 Known F1、Top-2、指标广度、总体增益和套件稳健性门全部通过，才另行冻结 full102，不能在结果后修改门或自动扩展。另修正 DoH watcher 的 WDiscOOD 前置 marker 路径，防止其永久等待不存在的结果目录。

修复后进一步检查旧 DoH PID `1580766`：它只有一个 `sleep 300` 子进程、无运行产物，且已经在启动时缓存错误 prerequisite。该空等待进程已停止，修正版 watcher 以 PID `1935631` 重启并等待 `runs/strict_v4_wdiscood_pilot_seed7/pilot_complete`；WDiscOOD、DoH、VOS 的活动队列顺序现与冻结方案一致。

进一步对全部 watcher 做静态依赖复审时，发现 WDiscOOD 的 `--mlp-root` 仍错误指向 OpenDetect 独立基线目录。远端权威源实际分离为 `runs/strict_v4_full103_mlp_seed7` 与 `runs/strict_v4_full103_independent_baselines_seed7`。该入口已修正，并新增同时支持主项目和相邻 exploration checkout 的依赖测试，验证 LCB -> Mal_TLS -> WDiscOOD -> DoH -> VOS marker 及主终审前置关系；本地和远端均 `3/3 PASS`。旧 WDiscOOD PID `1460599` 仅有 sleep 子进程、协议和指标均为 0，已安全重启为 PID `1981960`。修复时效率正式训练块为 `20/21`，正在最后一个 USTC-TFC2016 Shifu OpenDetect 捕获。

修正后的 WDiscOOD 双源绑定已在正式结果仍为 `0/14` 时远端实跑协议生成器，协议 SHA 为 `dda13c3a24fa96566efa4b6f5f62c25439035d3c167076019e87f7dd64f7019f`，算法、协议和汇总测试合计 `8/8 PASS`。随后效率训练块完成 `21/21`，执行器进入 102 场景推理捕获；因此 WDiscOOD 继续等待，不会与主效率计时并行。

## 15. 效率链失败关闭与自有算法资源纠偏（2026-07-21）

远端实时核验发现效率 executor PID `1242854` 已退出，GPU 空闲但 `execution_complete` 与最终论文 readiness 均不存在。日志定位到第二个推理场景 `CIC-IoT2023/BrowserHijacking` 的 Pairwise runtime 捕获：

- 训练与场景指标已正常生成，预测数组完全一致；
- 参与冻结风险的原始组件相对训练器最大绝对差为 `2.220446049250313e-16`；
- 连续两次 runtime 推理的最终风险最大差为 `0.017439245148767935`，高于冻结的 `1e-12`；
- 失败发生在经验尾分数对并列/近并列组件值的秩映射，不得用测试标签、结果后调参或简单放宽容差绕过。

因此当前效率证据只能记录为：训练块 `21/21`，完整推理块 `1/102`，正式效率汇总仍为 0。已新增不产出正式证据的重复性诊断，逐层比较原始组件、并列稳定化组件和经验尾分数，远端 PID 为 `2372450`。诊断后若需要修改 runtime，必须冻结新的效率协议/执行计划并在新结果根重跑受影响证据，旧部分结果只作故障审计，不与新版本混合。

该故障还暴露了调度优先级问题：LCB watcher 同时等待最终 readiness，导致效率失败后 GPU 空闲也不能自动进入自有算法。纠偏规则调整为“先完成隔离数值诊断；若正式效率需要新版本重冻且耗时较长，则优先释放 GPU 给已冻结 LCB 试点，再恢复效率”，但不得让两者并行。LCB 与 Mal_TLS 异构试点仍是必要自有算法探索，WDiscOOD/VOS 仍是外部基线，不得相互替代。

进一步检查确认综合 SOTA 审计、独立外部确认和 seed191 缓存三个直接科学前置均已完成；`final_paper_readiness` 之所以缺失，是它还要求效率和污染汇总。用论文打包门阻塞 LCB 属于调度依赖错误。LCB watcher 已改为直接依赖 `strict_v4_comprehensive_sota_audit/audit_complete` 和 `strict_v4_final_efficiency_seed191_cache/caches_complete`，依赖回归本地/远端 `4/4 PASS`。旧 PID `827015` 已安全停止，新 PID `2439847` 会等待当前诊断结束并连续三次确认 GPU 空闲后启动，不与诊断并行。

实际交接时两项任务均以 CPU 为主，单看 GPU 空闲不足以识别诊断占用；LCB 在连续空闲检查后先启动了 Edge-IIoT Ransomware/Uploading 两路 seed191 训练。最后一次成功的远端只读核验为 `2/14`、失败 0，随后已进入 NF-CSE DDoS-HOIC/SQL-Injection。按自有算法优先级，非正式 runtime 诊断 PID `2372450` 已暂停，LCB 保持运行。后续 watcher 的独占门应同时检查 GPU 与显式队列 blocker，不能再仅以 `nvidia-smi` 判定 CPU 型实验是否空闲。

基线设计文档同步升级到 v1.5.0，30 方法主屏幕的精确构成为：5 个 CAEOS 路径、12 个统一 MLP 分数、5 个独立检测器、ReAct/DICE/SHE、SIRC、Entropy/Prototype、Mahalanobis++/ExCeL。WDiscOOD/VOS 仅为冻结的第 31/32 候选，当前均 `0/14`，过门后才进入 full102。

## 16. LCB 试点终态与 Pairwise 保留决策（2026-07-21）

LCB Tail-aware 已完成七套件 14 个冻结困难场景，`14/14`、失败 0。训练协议 SHA `362d6c5eb096e770fe906f2f95c90b27d7c534a314a7d117d3f32fc6fc9592e1` 保持不变。首次分析未生成完成标记，原因是完整性加固版分析器错误假设 `metrics.arguments` 保存完整 CLI 参数；实际 schema 只在该字段保存精简参数，完整执行命令位于每场景 `provenance.json.command`。

为避免结果后改协议，原协议、原分析器和 14 份训练结果全部保留。新增 `strict_v4_lcb_analysis_schema_correction_v1` 只读校正 manifest：

- 同时核验 metrics 顶层和 arguments 中的 `risk_policy`；
- 从 provenance command 唯一解析风险选择、策略、seed 和九个冻结参数；
- 核验 provenance 的 suite/scenario/seed 与结果身份一致；
- 将验证后的字段交给原冻结分析器，复用其 known-only 门、最差折门、endpoint 自洽和套件扩展门；
- 明确训练输出、场景、候选参数、选择门和扩展门全部不变，不新增测试标签选参。

本地/远端校正与原协议测试 `10/10 PASS`，校正 manifest SHA 为 `b79f0643ba5fb32f525bd2a93e89c3d4837ab63eaa02b879308b04290832204f`。最终四项总体有向增益分别为 AUROC `+0.008084`、AUPR `+0.002029`、FPR95 `+0.036745`、OSCR `+0.017994`；候选 endpoint 仅在 `2/14` 场景被 known-only 门选择。五项扩展检查中，总体四指标、Known F1、至少一个候选激活、6/7 套件全指标非回退均通过，唯一失败项是套件最差指标：`-0.033509 < -0.01`。其中 NF-UNSW Reconnaissance 虽通过 known-only 激活门，但测试 AUROC/AUPR/OSCR 分别退化 `-0.049135/-0.067019/-0.020835`；USTC-TFC Tinba 则四指标显著正增益。该异质性证明当前 known-only 门会误激活，严格决策为 `retain_caeos_pairwise_incumbent`，因此不冻结 306 次 LCB 确认协议，也不根据试点标签扩大激活范围。

该结果说明尾部稳健方向仍有局部价值，但当前 known-only 代理门不足以稳定识别应激活场景。下一项自有算法证据转向 Mal_TLS2023 真实异构编码器，用于判断剩余失败是否主要来自表示层，而不是继续叠加全局风险分数。

## 17. Mal_TLS2023 异构编码器试点终态（2026-07-21）

统一 MLP 与 `TLS gated + IP/payload MLP + packet TCN` 异构编码器已完成 6 个未知家族、seed191 的 `12/12` 配对训练，失败 0，拆分指纹逐场景一致。冻结协议 SHA 为 `a0d31ec5434e647942b94e3b23188ef5a560aa66d7037a7cc2d68ec9e6e53126`。

异构编码器相对统一 MLP 的平均有向增益为 AUROC `+0.007308`、AUPR `+0.002404`、FPR95 `+0.032313`、OSCR `+0.004916`；Known Macro-F1 平均约退化 `0.002525`，仍满足 `>= -0.01` 门。这说明真实异构表示不是完全无效，但三个稳定性门失败：

- 仅 `3/6` 场景四指标全非回退，低于要求的 4；
- 最低场景指标为 Qakbot AUPR `-0.116946`，低于 `-0.03`；Qakbot 四项均回退；
- ECE 只在 Scanners 略改善，其余五场景退化，平均约 `-0.041487`，未通过非负门；
- Scanners 虽 AUROC/AUPR/OSCR 改善，但 FPR95 回退 `-0.072632`。

冻结决策为 `retain_multi_view_claim_and_revise_encoder_candidate`，不启动保留种子 `197/199/211`。论文仍只能声明多视图证据融合，不能升级为已确认的异构多模态编码器贡献。下一版候选不得只加深 TCN 或按测试家族路由，应使用 known-validation 可验证的校准约束和保守残差融合，同时另设新开发种子，保留原确认种子不用。

LCB 与异构编码器两项自有候选均按门停止后，`CAEOS-Pairwise` 继续作为最优 incumbent。非正式 Pairwise runtime 重复性诊断已在独立 `browser_hijacking_v2` 路径恢复，PID `3631578`；其任务是修复效率证据链并解锁 WDiscOOD、DoH 与 VOS，不改变算法选择。

## 18. 自有算法继续探索：保守异构残差（2026-07-21）

全异构编码器的四项未知指标均值为正，但 Qakbot AUPR、Scanners FPR95 和平均 ECE 出现不可接受的回退。因此不继续增加 TCN 深度，也不使用未知测试标签选择路由；下一候选固定为 `mal_tls_conservative_residual`：每个专用分支以零初始化投影接入统一 MLP 主干，逐坐标残差经 `tanh` 限幅后乘固定系数 `0.25`。TLS 与 packet-sequence 使用专用残差，IP-flow 与 payload 保持 MLP。

参考组与候选组都使用相同的已知类验证集证据温度校准，温度只按 known-validation NLL 在冻结网格 `[0.5, 3.0]`、步长 `0.05` 上选择。开发种子改为 `193`，六个 Mal_TLS 家族共 `12` 个配对运行；`197/199/211` 继续保留，只有开发门全部通过才允许确认。协议在结果数为 0 时冻结，manifest SHA 为 `66fa6b6f9d1153873daaa92daf1ecf7a3a7c15d660d02667a28725811cfb7b9a`。本地/远端核心与协议测试 `6/6 PASS`；这只证明实验可执行，不证明候选有效，incumbent 仍是 `CAEOS-Pairwise`。

## 19. Pairwise 效率重复性根因与 v3 恢复（2026-07-21）

BrowserHijacking 三次重放诊断确认：预测数组一致，所有原始组件最大差仅 `3.3306690738754696e-16`；唯一发生秩跳变的组件是 `conflict`，其经验尾差为 `0.00018975332068316142`，经 Cauchy 组合放大后风险最大差为 `0.007412592539810969`。根因不是数据缺失或模型随机重训，而是多个相邻间距不超过 `1e-12` 的验证参考值仍被赋予不同经验秩。

runtime v2 将相邻近重复参考值预聚为同一簇，并统一使用簇首秩；远端回归 `8/8 PASS`。正式恢复不覆盖失败的 v2 部分结果，而使用 `strict_v4_final_efficiency_protocol_v3`、`execution_plan_v3`、`runs/..._v3` 和 `results/..._v3` 四个新根目录，且必须先由同场景三次重放证明风险差不超过 `1e-12`。WDiscOOD 改为等待 v3 汇总完成标志，避免把 v2 部分结果误判为完整证据。

## 20. 保守异构残差试点终态（2026-07-21）

seed193 已完成 `12/12`、失败 0，协议与逐场景拆分指纹校验通过。候选相对温度校准后的统一 MLP 的 AUROC/AUPR/FPR95/OSCR 平均有向增益分别为 `-0.003976/-0.006646/-0.014708/-0.001474`，四项均为负；六个家族中没有一个四指标全非回退。最差单项是 Qakbot FPR95 `-0.100303`，Scanners 的 AUROC/AUPR/FPR95/OSCR 也全部回退。

Known Macro-F1 平均改善 `+0.002946`，但 ECE 仍平均回退 `-0.000648`；两个方法在六场景均由 known-validation 选择温度 `0.5`。五个开发门只有 Known F1 门通过，决策为 `retain_caeos_pairwise_and_reject_residual_candidate`，不使用 `197/199/211`。该结果否定“仅靠限制专用分支幅度即可把闭集增益转化为开放集增益”；下一表示候选必须冻结已确认主干并加入已知类一致性约束，不能继续扫描残差系数。

## 21. 效率 v3 无效与 v4 连续空闲门（2026-07-21）

v3 watcher 与 seed193 候选几乎同时启动；executor 在 CUDA 上下文尚未出现在 `nvidia-smi` 的短窗口内越过瞬时空闲门，随后与候选训练发生重叠。发现时正式 `efficiency_metrics.json` 为 0，但已有 9 个中间文件，故停止 executor、标记整个 v3 目录 `valid_for_efficiency_claim=false`，并终止其遗留的 OpenDetect 捕获进程与 4 个 worker。任何 v3 中间文件都不复用。

v4 使用新的 protocol/plan/formal/summary 根目录，在 executor 前要求连续 5 次 GPU 空闲、每次间隔 30 秒，并将逐次观测写入日志。远端 Bash 与依赖测试 `5/5 PASS`；WDiscOOD 依赖已切换到 v4 汇总完成标志。该纠偏只保护测量隔离，不改变算法或比较器。

## 22. 保守残差失败分量诊断（2026-07-21）

只读诊断比较了 seed193 六个场景的七项原始分量 AUROC，不参与算法选择。候选相对统一 MLP 的平均分量增益为：normal-distance `-0.047792`、raw-conflict `-0.011538`、energy/uncertainty 各约 `-0.010686`、inverse-belief `-0.008346`；有效 conflict 与 prototype-distance 则分别略增 `+0.001896/+0.002475`。Qakbot 的 normal-distance AUROC 退化 `-0.125382`，解释了其复合风险和 FPR95 灾难性回退。

因此下一候选的硬约束不是继续压小残差，而是保持融合嵌入、prototype/normal distance、原始/有效 conflict 路径不变，只允许专用模态修改融合证据。该诊断标记为 `formal_selection_evidence=false`，只生成新假设；新候选必须重新冻结协议并使用未见种子。

## 23. 几何保持证据适配器冻结（2026-07-21）

新增 `mal_tls_geometry_preserving_adapter`：从同场景统一 MLP 检查点初始化并逐张量冻结全部主干、证据头、可靠度头、投影和分类参数；TLS gated 与 packet TCN 只在最终融合证据上输出零初始化、`tanh` 有界的 `0.25` 修正。训练只更新适配器，并使用权重 `1.0` 的已知类 clean-to-corrupted KL 一致性；参考和候选继续使用相同 known-validation 证据温度校准。

协议要求每个候选检查点的全部非适配器张量与配对参考逐位相等，并要求 `distance_auroc`、`normal_distance_auroc`、`conflict_auroc`、`raw_conflict_auroc` 的差不超过 `1e-12`。新开发种子为 `195`，确认种子仍为 `197/199/211`；协议在 `0/12` 时冻结，SHA 为 `2a490c9b0b3dbca0bce8351dbff1c5f937bbbf96eb8773166f0ef58e5b6e77c0`。远端训练、协议、分析和检查点审计测试 `8/8 PASS`。watcher 排在 VOS `analysis.json` 之后，当前只等待，不占用 GPU。

## 24. 效率 v4 首个严格等价重复（2026-07-21）

CIC-IoT2023 Recon-PingSweep rep0 的 Pairwise 与 OpenDetect 捕获均已完成并通过严格等价门。Pairwise 在 6,218 个测试样本上的预测数组完全一致，runtime shadow 风险最大差 `0.0`，源组件最大差 `3.3306690738754696e-16 <= 1e-12`；OpenDetect 同设备 CUDA shadow 的预测一致、风险差 `0.0`。Pairwise 相对源脚本的经验尾风险差 `0.028680` 仅保留为离散秩诊断，不参与等价门，源组件审计仍通过。

executor 已按冻结的奇偶交替顺序进入 rep1 OpenDetect 捕获。当前只能声明“首个重复的仪器等价成立”，训练/推理效率聚合和效率优劣结论仍必须等待 21 个训练块、102 个推理块与最终 summarizer 全部完成。

## 25. 自有算法优先与 GROOD 第 33 基线冻结（2026-07-21）

自有算法探索继续作为主目标。当前 `CAEOS-Pairwise` 是冻结 incumbent，seed195 几何保持证据适配器是下一项待运行自有候选；任何新外部基线不得插队或改变其协议。近期 SOTA 复核新增 TMLR 2025 GROOD：该方法基于合成 OOD 原型、最近类原型损失对 OOD 原型的梯度以及梯度空间 1NN，与已经完成的 GradNorm 负试点不是同一路线。

GROOD 的 tabular 适配只使用已知训练嵌入、logit 和标签拟合类原型、合成 OOD 原型与梯度库，禁用 validation OOD；known-validation 只用于部署阈值。官方代码提交绑定为 `8a5ecdfdad178b6793132bec5d23cfad224fba11`，远端核心和协议测试 `5/5 PASS`。14 场景协议在结果 `0/14` 时冻结，协议 SHA `536729683e3088e7071be2a8f3a3032c27cb850b3955d4ffd7a51e32b2255e59`，扩展门 SHA `77638190563e4642515c7d3fecef3b32c165588fcf0f5d06513038e8bf02d790`。watcher PID `193140` 只等待几何适配器 `analysis.json`，因此执行顺序为 WDiscOOD -> DoH -> VOS -> 几何适配器 -> GROOD。

现代负试点复审同时确认：ASH-S、NNGuide、NAC-UE、NECO、fDBD、GradNorm、OptFS、ODIN、AdaSCALE、LINe、KLM 和 DCC 均已有冻结的 14 场景证据，不应被误记为遗漏。NNGuide 相对 Energy 的四指标有向均值为 `+0.038906`，但只有 CIC-ToN-IoT、Edge-IIoT、NF-UNSW 三个套件非负，未达到 4/7 套件门；其余候选也未过各自冻结门，所以不能结果后补 full102。

北京时间 `2026-07-21 03:17`，效率 v4 已生成 Pairwise 候选捕获 `7`、OpenDetect 比较器捕获 `6`、严格等价文件 `13`，正式 `efficiency_metrics.json` 仍为 0。当前状态支持“仪器等价链持续通过并推进”，不支持效率优越结论。

## 26. 自有算法主线与后效率声明链恢复（2026-07-21）

自有算法探索是论文创新成立的必要条件，不能由继续增加外部基线替代。当前采用“双轨但不等价”的资源策略：外部基线用于确认比较充分性和 SOTA 边界，自有候选用于寻找可稳定替换 `CAEOS-Pairwise` 的算法增量。现阶段仍以 `CAEOS-Pairwise` 为 incumbent，seed195 几何保持证据适配器为正在排队的自有候选；只有其冻结的 12 场景开发门全部通过，才允许使用保留种子 `197/199/211`。WDiscOOD、VOS、GROOD 均是外部比较器，结果无论正负都不计作自有算法创新。

效率旧等待器在 v2 失败后退出，导致已经冻结的选后污染矩阵、Pairwise--OpenDetect 对比污染矩阵和最终论文就绪审计没有活动进程接续。新增 `wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh` 修复该断链，但不修改任何冻结算法或污染条件。它等待效率 v4、GROOD（当前队列最后一项）与综合准确率审计全部完成，再同时检查 GPU 进程和显式实验进程，连续 5 次空闲、每次间隔 30 秒后，串行执行：

1. 复用 SHA 为 `83415875d1f26c8f1c948dac65f498110a5f3a6080e2aba4fd4407aa05eea4f4` 的 783 次选后污染协议；哈希不一致立即停止，禁止重冻；
2. 只有在比较污染结果仍为 0 时才冻结 306 组、1,530 条件评估的 Pairwise--OpenDetect 对比协议，并支持结果级断点续跑；
3. 使用 `strict_v4_final_efficiency_v4/summary.json` 生成最终论文就绪审计，不再错误引用已失败的 v2；
4. 任一 schema、canonical SHA、拆分或完整性门失败均停止，不生成完成标记。

新增恢复链测试、既有比较污染测试和最终审计测试在服务器分别为 `5/5`、`6/6`、`2/2 PASS`，Bash 静态检查通过；修正空目录计数的 `pipefail` 异常路径后，等待器 PID 为 `260108`。北京时间 `2026-07-21 11:40` 的服务器只读快照显示效率 v4 的 Pairwise/OpenDetect 捕获为 `8/8`，正式 `efficiency_metrics.json` 和效率摘要仍为 0；WDiscOOD、DoH、VOS、seed195 适配器、GROOD和污染结果也均尚未完成。因此当前可以继续撰写方法、协议、已完成主结果和负结果，仍不能定稿效率、污染鲁棒性或“全面 SOTA”结论。

## 27. 自有算法连续确认与反事实冲突门（2026-07-21）

seed195 原队列只在开发分析后结束，缺少“通过则使用保留种子确认”的自动分支。新增 geometry confirmation branch：若 seed195 决策不是 `freeze_for_reserved_seed_confirmation`，写入 `not_required` 并放行下一候选；若通过，则先在确认结果为 0 时冻结 `197/199/211`、6 家族、参考/候选共 `36` 个运行的协议，再要求四项均值及 bootstrap 95% CI 下界为正、每个种子四项均值为正、至少 4/6 家族不回退、Known F1/ECE和全部几何不变门通过。分支 watcher PID 为 `393097`。

在未读取 seed195 结果的条件下，新增自有候选 `mal_tls_counterfactual_conflict_gate`。该候选冻结全部参考模型张量，只增加零初始化、有界的冲突条件证据衰减门；使用 known-training 中跨类别交换 TLS 与 packet-sequence 的反事实作为伪未知，目标是提高冲突样本不确定性，同时由教师一致性保护已知样本。开发种子为 `201`，确认种子预留 `203/205/207`；协议在 `0/12` 冻结，SHA 为 `d59cf35d41d34d41f94372d75f56f3bf73288f7c54a72ef148d66343cd82d8c7`。核心、协议、队列测试远端分别 `4/4`、`3/3`、`2/2 PASS`，确认分支测试 `4/4 PASS`；新候选 watcher PID `393098`。

为不破坏 seed195 已绑定的 `model.py/training.py/train.py` SHA，新候选部署到独立工程 `/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721`，只通过完成 marker 与原探索工程串联。seed201 之后新增保留种子确认和最终自有算法选择审计，GROOD 只等待最终选择 `audit_complete`；当前总顺序为效率 v4 -> WDiscOOD -> DoH -> VOS -> seed195 -> 条件确认 -> seed201 -> 条件确认 -> 自有算法选择 -> GROOD -> 污染与最终审计。

## 28. seed201 确认与最优自有算法选择冻结（2026-07-21）

seed201 的确认分支已补齐：开发门通过才允许在结果为 0 时冻结 `203/205/207`、6 家族、36 个配对运行；确认要求四项均值和 bootstrap 95% CI 下界为正、每个种子四项均值为正、至少 4/6 家族不回退，并重复验证 Known F1、ECE、反事实不确定性、margin、证据衰减和全部几何不变。开发失败只生成 `not_required`。确认分支 watcher PID 为 `447522`。

新增 `mal_tls_self_algorithm_selection_protocol_v2`，在两个确认分析均为 0 时冻结，SHA 为 `16579561e5140a9dc302a652a7bd7eabb1056a863838339272491ad2f5cfcdd7`。选择资格要求 pilot 与保留种子确认同时通过；两者均合格时先比较四指标最差 bootstrap 下界，再比较四指标平均增益，禁止结果后集成。v1 因缺少 pilot analysis schema 硬门在结果前被 v2 取代，未产生选择结果。v2 watcher PID 为 `525919`，GROOD watcher PID `447536` 已改为等待其 `audit_complete`。

相关确认、选择和队列测试本地/远端共 `10/10 PASS`，Bash 和 Python 编译通过。北京时间 `2026-07-21 12:39`，效率 v4 Pairwise/OpenDetect 捕获为 `15/15`，正式 `efficiency_metrics.json` 仍为 0；两个自有候选及确认分析仍未产生结果，`CAEOS-Pairwise` 继续作为唯一已确认 incumbent。

## 29. 自有算法必要性与GPU恶意数据扩展准入（2026-07-21）

自有算法探索继续作为论文成立的必要主线，不以新增外部基线或新增数据集替代。结论按三层管理：`CAEOS-Pairwise` 是当前已有独立确认的 incumbent；几何保持证据适配器和反事实冲突门是预注册的局部挑战者；只有 pilot 与保留种子确认同时通过，并在最差四指标 bootstrap 下界、四指标平均增益和 Known F1 非劣门上胜出，才允许更新最优自有算法。两个挑战者尚无结果，因此不得提前评价有效或无效。

GPU 数据根的只读审计确认两项首批候选：LSNM2024 有正常流量和 `15` 个路径级恶意家族、共 `21` 个 CSV，但存在 `59/60/61` 列混合且部分恶意文件无显式标签；CICDDoS2019 有 `16` 个路径级 DDoS 家族、`18` 个统一 88 列 CSV 并带 Label。LSNM 不能按源文件直接切分，因为多个家族只有单一文件；纠偏后要求按规范化双向五元组/会话分组，从恶意父路径派生缺失标签，并排除原始地址、内容字符串、校验和、流/采集 ID。CICDDoS 同样按五元组或指纹分组，只作为窄域 DDoS 家族外部套件，不替代宽域恶意覆盖。

新增 `gpu_malicious_dataset_expansion_protocol_v1` 在完整扫描和训练前冻结，协议 SHA 为 `6c8c76e3e7e5b477b7314c742aeaf7f5ec5c81f147130dc2fdfd4d19a8dafc0e`。它绑定三个 ZIP 的中央目录指纹，固定种子 `223/227/229`、攻击家族留一、每标签至少 3 个非重叠组、三组切分重叠为 0、外部套件禁止调参，以及“先完成当前效率/声明链，再完整扫描，再冻结标准化数据清单，最后运行基线与有资格的自有挑战者”的顺序。审计/协议测试本地和远端均 `3/3 PASS`。北京时间 `2026-07-21 12:56`，效率 v4 候选/OpenDetect 捕获为 `18/18`，正式效率指标仍为 0；全部七个串行 watcher 存活。

## 30. 全量准入审计器与效率推理起点（2026-07-21）

已实现 `audit_gpu_dataset_admission.py`，对 LSNM2024 和 CICDDoS2019 逐 ZIP 成员流式扫描，并把每个成员结果独立落盘以支持断点续跑。LSNM 使用双向地址/端口、协议和 120 秒间隔形成会话组；CICDDoS 使用双向五元组和时间戳形成流组。SQLite 组表精确检测同一组是否跨标签，避免用有限内存采样替代完整无泄漏审计。新增 LSNM 四模态配置只保留数值侧信道和应用字段存在性，明确排除地址、内容字符串、校验和和采集 ID。

执行协议在正式审计结果为 0 时冻结，绑定父协议、扫描器、两个特征配置和 runner，canonical manifest SHA 为 `b41ebb9eee0177376e62a2cc1aede9efebf0e9fca16c379910ce5d5bfcf6f69e`，协议文件 SHA 为 `26370f88a15605d778c5bcee33a4e5aac3c24c921a1ee3acd720012868ba7453`。本地/远端测试均 `10/10 PASS`，Bash静态检查通过。watcher PID `639026` 等待 `strict_v4_postefficiency_claim_chain_v2/chain_complete`，故当前只持有等待锁，不扫描数GB压缩数据，也不干扰正式测量。

北京时间 `2026-07-21 13:49`，效率 v4 的训练捕获已完成 `21/21`；首个推理场景 CIC-IoT2023/Backdoor-Malware 已生成原生设备和CPU归一化两套 `efficiency_metrics.json`，推理进度为 `1/102`。最终 summary、WDiscOOD、DoH、VOS、seed195、seed201、最终自有算法选择和 GROOD仍无新增结果。该状态只证明正式推理链已启动，不支持效率优越或新自有算法效果结论。

## 31. 准入后标准化数据准备链（2026-07-21）

新增 `prepare_gpu_external_datasets.py`，把全量准入与正式外部实验之间的空档补齐。准备器不做随机行抽样：对 LSNM 每标签最小哈希选择 500 个会话、每会话8行；对CICDDoS每标签选择4000个五元组流、每流1行。三个预注册种子在一次扫描中并行维护独立组集合，组被淘汰时对应行缓存同步删除，最终每标签最多4000行。LSNM原始内容字段只生成存在性标志，地址和时间只参与会话/流分组，所有模型特征必须为有限数值。

每个 seed CSV 都生成 sidecar，绑定全量审计SHA、扩展协议SHA、配置SHA、三个源ZIP SHA、行/组/标签计数和输出CSV SHA。准备执行协议在产物0时冻结，canonical manifest SHA `8d8d5a2cf5c5472f24f36dc6c69280a7bb8e94d931d431a59d922bbdc2b2bc43`，协议文件SHA `74128484c1efb1ee157b209a969ad8bad95d16507ee48e5061541ce4c139cc02`。本地/远端测试均 `13/13 PASS`，Bash静态检查通过。watcher PID `1174214` 只有在全量审计生成 `admission_passed` 后才运行；若审计失败则写入 `blocked_by_admission_failure` 并停止。当前准备manifest为0。

北京时间 `2026-07-21 14:02`，效率v4训练仍为 `21/21`，CIC-IoT2023 的 Backdoor-Malware 与 BrowserHijacking 两个推理场景均完成原生设备和CPU归一化指标，推理进度 `2/102`。最终效率summary和全部下游基线/自有算法结果仍为空，结论边界不变。

## 32. 自有算法运行时纠偏与污染场景重跑（2026-07-21）

自有算法探索继续是必要主线，但“最优”必须同时满足检测效果和可部署性。102 个已完成 Pairwise 准确率场景中，`88` 个选择 `cauchy_modality_support_union`，`14` 个选择 `pseudo_unknown_learned_blend`。静态审计发现冻结 runtime 对两类分支一律计算全局 KNN、逐视图 KNN、类别 KNN、LOF、全部经验尾和归一化项；参考分支最终只使用 conflict、tree-disagreement、distance 与逐视图 KNN。更主要的瓶颈是全局 RandomForest/ExtraTrees 在同一次预测中被执行两遍：一遍生成分类概率，另一遍重新生成 tree-disagreement。

新增隔离的 `OptimizedPairwiseRuntime`，不修改效率 v4 已绑定的 `caeos/pairwise_runtime.py`。它按冻结风险分支按需计算组件，并对服务器全部 `21/21` 个 `ConflictAwareHybridClassifier` 捕获复用一次全局森林前向；其他分类器类型自动回退原实现。真实 cauchy 与 learned 捕获分别在 `6,218`、`7,847` 个无标签输入上通过严格等价门：预测数组完全一致，风险最大绝对差均为 `0.0`，概率最大差不超过 `1.1102230246251565e-16 <= 1e-12`。本地/远端专项测试均 `4/4 PASS`。并发条件下的非正式方向性诊断中，cauchy 分支 batch `1/64/512` 的 P50 为 `249.722/438.444/606.299 ms`，learned 分支为 `288.524/424.727/699.666 ms`；这些数值受正式任务并发影响，只证明快路径值得正式复测，不进入论文效率表。

诊断在 UTC `06:24` 与效率 v4 第四个 CIC-IoT2023/DDoS-ACK-Fragmentation 捕获重叠，而该捕获始于 `06:18`。为避免把资源竞争写入正式证据，已终止该场景捕获，将其 5 个部分文件完整归档至 `runs/strict_v4_final_efficiency_v4_contaminated_20260721T0624Z`，保留前三个已完成场景，并以 PID `1617862` 重新启动恢复脚本。执行器按 expected-files 逐步跳过前三个完整场景，从第四场景干净重跑；污染目录不得参与 summarizer。正式运行时优化必须另冻 v5 协议，在隔离窗口对全部冻结效率场景重复 `5` 次预热、`30` 次测量，并同时通过预测/概率/风险 `1e-12` 等价门后才可形成部署效率结论。

该快路径属于自有算法的工程可部署性优化，不替代准确率创新。准确率候选仍按 `seed195 几何保持适配器 -> 条件确认 -> seed201 反事实冲突门 -> 条件确认 -> v2 最优自有算法选择` 推进；在结果出现前，`CAEOS-Pairwise` 仍是唯一已确认 incumbent。

## 33. ICCV 2025 GSC 第34基线冻结（2026-07-21）

近期方法复核将 Gradient Short-Circuit（GSC）从 `methodology_review_only` 提升为第34个正式候选。ICCV 2025 论文规定：在倒数第二层特征 `F` 上计算预测类 logit 梯度，遮蔽绝对梯度最大的前 `5%` 坐标，并用 `y' = y + J_y(F)(F'-F)` 一阶项得到修正 logits，最后使用修正 energy 判别。表格 MLP 的冻结分类头为线性层，因此一阶更新与重新前向逐元素等价；同时梯度掩码会退化为“同一预测类固定掩码”。实现保留并显式报告该退化，不改变公式或伪造样本自适应性。

新增 `caeos/gsc_posthoc.py`、冻结检查点评估器、14场景确定性选择器、结果前扩展门、汇总器和串行 watcher。公式测试验证线性头精确等价、5%向下取整且至少1维、稳定并列策略、类内固定掩码和完整正向扩展门；本地/远端均 `6/6 PASS`，Bash 静态检查通过。协议在结果 `0/14` 时冻结，protocol SHA 为 `55ade315f13d17cdb9d09e8c24d0a48c3ab52fa1260e31453dfff7b3b9162da9`，扩展门 SHA 为 `8abe15d83a57f3c1005399c1c5857b87edbe7ac9fb04456470a42b2853cbcdaa`。GSC watcher PID `2003725` 等待 GROOD 完成后才运行；后效率链已重启为 PID `2025174` 并新增等待 GSC，顺序调整为 `... -> 自有算法选择 -> GROOD -> GSC -> 污染与最终审计`。

S&I 暂不计作第35基线。其 ICML 2025 论文要求逐层拆分、逐层更新对抗样本并沿对抗样本到真实输入的路径积分归因；官方仓库 HEAD `d8984f0f9325f053e7a7e4b16574842ebab09c34` 使用 ResNet/WRN/BiT 专用 split 网络与多层 hooks。仅对表格 MLP 最终层计算梯度会删除核心方法，因此禁止以简化 GradNorm 类分数冒充 S&I。只有完成 MLP 各隐藏块的逐层拆分、对抗更新、积分路径和官方图像 smoke 对照后，才允许在结果为0时冻结第35协议。

## 34. 自有算法优先队列纠偏（2026-07-21）

再次确认自有算法探索是论文成立的必要条件，公开 SOTA 的作用是建立可信参照系，不能替代独立方法创新。队列审计发现：虽然 GROOD/GSC 已排在最终自有算法选择之后，但 seed195 几何保持适配器仍等待 VOS，而 VOS 又等待 DoH 和 WDiscOOD，导致自有挑战者事实上被多条外部基线阻塞。该依赖与当前目标不一致，已在未产生任何候选结果时纠偏。

新的严格顺序为：`效率 v4 干净恢复 -> seed195 几何保持适配器 -> 条件保留种子确认 -> seed201 反事实冲突门 -> 条件保留种子确认 -> 自有算法 v2 择优审计 -> WDiscOOD -> DoH 外部时序 -> VOS -> GROOD -> GSC -> 后效率声明链`。几何 watcher 现在只等待 `strict_v4_final_efficiency_v4/recovery_complete`；WDiscOOD 同时等待效率完成与 `mal_tls_self_algorithm_selection/audit_complete`；GROOD 同时等待自有选择与 `strict_v4_vos_pilot_seed7/pilot_complete`。三个等待进程已安全重启为 PID `2837968/2837970/2837969`，对应依赖测试远端 `13/13 PASS`，Bash 静态检查通过。

本次纠偏只调整资源顺序，不修改任何冻结模型、风险公式、种子、阈值、数据切分或评价指标。自有候选仍必须同时通过 pilot、保留种子确认、四项未知指标最差 bootstrap 下界、Known F1 非劣、ECE/几何约束以及后续新增数据集外部确认；任何一门失败均不能替换 Pairwise，也禁止结果后拼接候选。北京时间约 `2026-07-21 15:30`，效率恢复已产生 `14` 个 `efficiency_metrics.json` 但尚无 `recovery_complete`；seed195、seed201 和最终选择均为零结果。因此当前仍只能确认 Pairwise 为 incumbent，不能声称新自有算法有效或已经实现全面 SOTA。

## 35. 第三条自有路线：Conflict-Topology Copula（2026-07-21）

现有负结果限定了下一候选的设计空间。LCB tail-aware 在 `2/14` 场景启用，USTC/Tinba 增益明显但 NF-UNSW/Reconnaissance 回退；Mal_TLS 异构编码器虽然四项未知指标均值略正，但只有 `3/6` 场景全指标不回退，ECE 均值下降；保守残差则四项未知指标均值全部为负。因此第三条路线不能继续堆叠编码器或重新加权单变量尾部，而应利用现有 Pairwise 证据包中尚未联合建模的多视图分歧拓扑。

新增 `CAEOS Conflict-Topology Copula (CTC)`：从每个样本提取可靠性加权视图 Jensen-Shannon 分歧、最大视图到共识分歧、成对冲突图 Laplacian 谱半径、冲突-低可靠性耦合、全局概率到视图融合概率分歧五个视图置换不变特征。只将已知验证集按类别确定性拆成拟合/校准两部分（校准比例 `0.4`、种子 `229`），对特征边际作经验高斯 copula 变换，以 Ledoit-Wolf 协方差计算联合 Mahalanobis 非一致性，再用校准子集转换为上尾风险。候选风险固定为 `0.75 * Pairwise risk + 0.25 * topology risk`，分类预测逐元素保持 Pairwise 不变；未知或测试标签不参与 copula 拟合、阈值或权重选择。

实现、评估、矩阵执行、汇总和 watcher 已完成，本地/远端专项及队列测试均 `19/19 PASS`，Bash 与 Python 静态检查通过。首次协议冻结后发现执行器只记录输入 SHA、未在运行时复核；因结果仍为 `0/14`，旧文件以 `protocol_manifest.superseded-missing-input-runtime-check-v1.json` 留档，未运行。补入逐文件 SHA 失败关闭和篡改测试后重新冻结，当前 canonical SHA 为 `d368e18f8529eeb6ec45ea18b620a852403f8269480a0805df2ffef0597cd5c4`，协议文件 SHA 为 `028746b3a27c7dd13cfe6c60ed6f85b990880930811b6f93ad04c04f4f8c47e6`。开发门要求四项总体定向均值全部为正、最差 suite-metric 不低于 `-0.01`、至少 `6/7` 套件全指标不回退、至少 `8/14` 场景四指标均值为正、预测完全相同和 Known F1 差不超过 `1e-12`；阳性后才允许冻结 `233/239/241` 的 full102 确认。

CTC watcher PID `3451408` 等待 Mal_TLS 两条候选的 v2 选择完成，WDiscOOD watcher 已重启为 PID `3451409` 并新增等待 CTC `pilot_complete`。当前严格队列为 `efficiency-v4 -> geometry/confirmation -> counterfactual/confirmation -> self-selection-v2 -> CTC -> WDiscOOD -> DoH -> VOS -> GROOD -> GSC`。UTC `2026-07-21 08:20`，正式效率文件为 `18`，对应 `9/102` 场景完成两种测量口径；CTC、seed195 和 seed201 均为零结果，故第三条路线仍只是预注册候选，不构成效果或 SOTA 结论。

## 36. CTC 保留种子确认分支与队列闭环（2026-07-21）

为落实“自有算法探索不能止于开发集阳性”，已补齐 CTC 的独立确认分支。确认协议只能在 14 场景 pilot 同时满足全部开发门并输出 `freeze_for_reserved_seed_confirmation` 后创建；pilot 阴性时只写入 `not_required`，不消耗保留种子。阳性分支固定使用 `233/239/241`、7 套件、102 场景，共重新训练 `306` 个 Pairwise 参考并生成 `306` 个 CTC 配对报告。每个 Pairwise 源运行必须重新验证风险策略、known-only 选择标志、split fingerprint 和四类必需工件；CTC 实现及执行链由协议 SHA 绑定。

最终确认以场景为独立统计单位，先在每个场景内平均三个种子，再执行 10,000 次 bootstrap、四指标 Wilcoxon 与 Holm 校正。替换 Pairwise 必须同时满足：AUROC/AUPR/FPR95/OSCR 四项有向均值均为正，AUROC/AUPR bootstrap 下界大于 0，四项 Holm 校正后 `p<0.05`，每个 suite 的每项有向均值均不为负，306 次预测数组全部一致，Known macro-F1 绝对差不超过 `1e-12`。即使通过，也只得到“准确率确认，仍待正式效率与新增恶意数据集门”的资格，不能直接写成全面 SOTA。

确认协议生成器、306 运行矩阵、统计汇总器、条件 watcher 和输入泄漏拒绝测试已经部署；本地相关回归 `21/21 PASS`，服务器 CTC 专项 `12/12 PASS`，Bash/Python 静态检查通过。WDiscOOD 的放行条件已从 CTC `pilot_complete` 提升为确认分支 `branch_complete`，旧等待进程已精确停止；新确认 watcher PID `1587732`，新版 WDiscOOD watcher PID `1587738`，锁均有效。UTC `2026-07-21 10:40`，效率 v4 为 `34` 个正式效率文件，即 `17/102` 场景的双口径结果，失败 `0`，尚无 `recovery_complete`；CTC pilot/确认均仍为零结果，Pairwise incumbent 与论文结论边界不变。

## 37. 自有算法必要性与 PRO 第35基线冻结（2026-07-22）

自有算法探索继续保留为主线，外部基线只用于收紧比较边界，不能替代独立创新。当前资格顺序不变：`CAEOS-Pairwise` 是唯一已有独立确认的 incumbent；seed195 几何保持适配器、seed201 反事实冲突门和 CTC 是三条互补挑战路线。三者均仍为零效果结果，只有 pilot 与预留种子确认同时过门，才允许进入最终自有算法择优和新增恶意数据集外部确认。

对 ICML 2025 S&I 官方实现的进一步公式/代码审计表明，其核心是对 ResNet 等网络进行逐层 split，在多次对抗更新中统计非零输入梯度坐标并积分。当前表格 ViewEncoder 是稠密 `Linear-LayerNorm-GELU` 块；直接移植官方“非零梯度占用率”会在一般位置退化为近常量，最终层简化又会删除逐层 split 核心。因此 S&I 继续标记为 `methodology_review_only`，不计作第35基线，也不以名称相似的梯度分数冒充复现。官方审计提交保持为 `d8984f0f9325f053e7a7e4b16574842ebab09c34`。

第35个零结果冻结候选改为 CVPR 2025 Perturbation-Rectified OOD Detection 的 `PRO-MSP-Fixed`。适配严格使用官方 `PROv2_MSP_Postprocessor` 默认值：温度 `1.0`、一步 sign-gradient、步长 `0.003`，在已知训练标准化坐标中沿降低 MSP 的方向更新，不投影，最终风险为原输入与扰动路径最小 MSP 的反向值；分类预测仍来自未扰动冻结 MLP。禁用 APS/OOD 超参数扫描，known-validation 只用于部署阈值，未知/测试标签只计算最终指标。官方代码提交绑定为 `bb22cc2b1c4c928e4bc38e2d7c7db4f8900df295`。

PRO 的7套件、每套件2场景、共 `14` 场景协议在结果 `0/14` 时冻结，protocol SHA 为 `1f9d46cc2a1c52d129c924a1660e3a25948caaa427e86147d440eef2f3175206`，扩展门 SHA 为 `612dfaddfd730c56ec89f34c542017c588cce0cafd932ddcd77ab6236f90cbc2`。核心、协议、汇总和队列测试本地/远端均 `8/8 PASS`，协议以当前实现重新生成时 canonical SHA 不变。只有完整性、拆分、Known F1、四方法排名、相对 MSP 的四项总体/逐套件增益门全部通过，才允许补 full102；PRO watcher PID `3311498` 等待 GSC 完成，后效率 watcher PID `3311499` 已加入 PRO 完成门。

UTC `2026-07-21 22:54` 的服务器快照显示：效率训练块 `21/21` 完成，推理块 `95/102` 完成，已生成 `190/204` 个双口径 `efficiency_metrics.json`；剩余7个场景均在 USTC-TFC2016，executor 仍在运行，尚无 `summary.json` 或 `recovery_complete`。seed195、seed201、CTC、WDiscOOD、VOS、GROOD、GSC和PRO均尚无可判定效果结果。当前结论仍是“Pairwise 为已确认 incumbent，自有挑战者和第31至35外部候选待严格门控”，不能写成已实现全面 SOTA。

## 38. learned-tail 非确定性失败关闭与效率 v5 恢复（2026-07-22）

效率 v4 在 USTC-TFC2016/Miuref 候选捕获处失败关闭。模型预测连续一致，必需组件最大绝对差仅 `3.33e-16 <= 1e-12`，但 `pseudo_unknown_learned_blend` 的二级经验尾仍使用原始离散秩；机器精度级组件扰动跨越相邻经验秩后，同一 runtime 连续两次风险最大差达到 `0.000113199 > 1e-12`。因此 v4 停在训练 `21/21`、推理 `95/102`、正式指标 `190/204`，未生成 summary/完成标志，并整体标记 `valid_for_complete_efficiency_claim=false`。失败时协议、计划、旧 runtime、Miuref 日志和 SHA 清单已保存在 `strict_v4_final_efficiency_v4_failure_20260721T2235Z`。

修复同时覆盖原 runtime 与等价快路径：对 learned blend 的 validation raw score 预排序，按 `1e-12` 邻近簇固定首秩，再用同一稳定经验尾计算查询风险。新增机器精度跨秩回归后，服务器基础/优化 runtime 与恢复协议测试共 `26/26 PASS`。使用 Miuref 原冻结参数在隔离目录重做真实捕获，预测完全一致、连续风险差 `0.0`、组件最大差 `4.44e-16`，证明原失败条件已消除；该 smoke 不进入正式效率聚合。旧/新 runtime SHA 分别为 `e74e5da2f7edc2c7a273f07396cb13d25cfa865147a90d6418a0d3edba4a280d`、`a0f226d1449b5216783207651661a9f64dd9e5a80c2066c59220e381140dc6ae`。

由于实现哈希变化，未直接续写 v4。效率 v5 在正式结果为0时重新冻结 protocol `069c61eeba45ded98f4f7d584b29cf66cda1a22bcb507f475b0abe9f6560cbc1` 和 plan `dd9d3459b3ec28343547c02af653d1969a26422c61863d1fd09484d3247abb05`。复用审计 SHA 为 `cf1d64222f82bc1f5312bee17b6588e9fda85543a4204f8af5272bb53681de99`：只复制公式路径未变且旧等价门通过的 Cauchy 候选捕获及未变的 OpenDetect 捕获，共 `311` 个目录；其中候选 `100`、比较器 `211`。明确跳过 `16` 个 learned-blend 候选捕获和7个未完成场景的21个捕获，禁止复制任何 standalone benchmark 或旧 `efficiency_metrics.json`。因此新实现的 learned 捕获、全部正式计时和全部配对指标都会重新执行。

UTC `2026-07-22 00:30`，v5 已通过连续5次、每次间隔30秒的 GPU 空闲门，executor 正在重跑 NF-UNSW/Fuzzers 的 learned-blend 训练捕获。geometry、WDiscOOD 和后效率等待器已重启并只等待 v5 完成，PID 分别为 `1739794/1739796/1739798`。这一纠偏延后但保护了部署效率结论；自有算法准确率优先级和三条挑战路线不变，Pairwise 仍是 incumbent，尚不能声明全面 SOTA。

UTC `2026-07-22 00:53`，三个新 learned-blend 训练重复均已完成，连续风险差均为 `0.0`、组件最大差均为 `3.33e-16`；正式推理已完成 `3/102` 场景、生成 `6/204` 个双口径指标，executor 仍存活。三场景方向诊断显示原 Pairwise runtime 相对 OpenDetect 的 P50 时延比在 native 模式的 batch `1/64/512` 分别约为 `181.2/340.9/656.0`，CPU 归一化模式约为 `96.3/397.3/410.8`；吞吐比分别只有 `0.0056/0.0030/0.0016` 与 `0.0119/0.0026/0.0026`。样本仅3场景，不能形成总体效率结论，但已证明原 runtime 的部署代价是必须处理的硬约束。v5 继续作为原实现正式基线跑完；已有严格等价 `OptimizedPairwiseRuntime` 后续必须使用独立 v6 三方协议同时比较原版、优化版和 OpenDetect，且不得与当前 v5 或准确率挑战者并发。

## 39. 严格等价快路径 v6 三方协议冻结（2026-07-22）

为避免看到 v5 局部时延后再选择优化口径，v6 在任何 `triad_metrics.json` 出现前冻结。协议覆盖与 v5 完全一致的7套件102场景和 native/CPU归一化两种模式，每场景每模式同时加载 original Pairwise、`OptimizedPairwiseRuntime` 与 OpenDetect；batch 固定为 `1/64/512`、预热5次、正式30次。三方法按 repetition modulo 3 使用 Latin-square 轮换首/中/末位置，消除固定先后顺序偏差。

优化版在每个场景计时前必须对全部输入逐元素通过 prediction 完全一致、probability/risk 最大差 `<=1e-12`；候选与比较器原捕获也必须重复通过各自等价门和输入数组相等门。部署目标在结果前固定为：两种模式、三个 batch 的102场景中位 P99 比均 `<=0.5`，吞吐比均 `>=2.0`；优化产物持久化字节数与原 Pairwise 产物之比必须 `<=1.0`，并在全部204块报告原版、优化版和比较器产物字节数。未达到任一目标只判定快路径不足，不改变 Pairwise 准确率 incumbent，也不允许从局部场景生成速度声明。

首版协议 SHA `2b0f0c20629f61ee9b1444990f7859527408e8a34426f881f3ecb6c49acbb379` 在 optimized 结果仍为 `0/204` 时因缺少显式模型体积门而废止并归档，没有产生可用测量。补齐体积门后重新冻结的当前权威 canonical SHA 为 `ae59745a52eeab39af2b93e9f6bd51dcbba631f11d45dd00e0efe6837e9f8487`。它绑定 original runtime `a0f226d...`、optimized runtime `b1d987c...`、OpenDetect runtime `45b1df1...` 以及 block/matrix/summarizer 全部实现 SHA；再次冻结时 optimized 结果仍为 `0/204`，v5 已有52个指标且明确标记 `used_for_optimized_parameter_selection=false`。本地/远端协议与队列测试均 `9/9 PASS`，Bash/Python 静态检查通过。当前 v6 watcher PID `2424393` 只等待 v5 `recovery_complete` 与 CTC 确认分支 `branch_complete`；WDiscOOD watcher PID `971653` 继续等待 v6 `branch_complete`。UTC `2026-07-22 04:20`，v5 已推进到 `82/204`，并生成126个三方独立 benchmark；v6 仍为0结果且不占用计算资源，v5/v6完成标志均未出现。

## 40. 自有算法优先队列现场复核（2026-07-22）

依赖脚本逐级绑定为：`v5 recovery_complete -> seed195 几何适配器 pilot -> seed195 条件确认 branch_complete -> seed201 反事实冲突门 pilot -> seed201 条件确认 branch_complete -> 自有算法选择 audit_complete -> CTC pilot -> CTC 条件确认 branch_complete -> v6 部署门 -> WDiscOOD`。确认分支在 pilot 未过门时写 `not_required.json` 后仍生成 `branch_complete`，因此负结果会失败关闭但不会永久阻塞后续候选；只有阳性 pilot 才能使用预留种子。

UTC `2026-07-22 04:08` 现场进程显示：seed195 pilot/确认、seed201 pilot/确认、自有算法选择、CTC pilot/确认、v6 与 WDiscOOD watcher 均存活；VOS、GROOD、GSC、PRO watcher 也保持排队。所有自有挑战者的效果完成标志仍不存在，故当前只确认 `CAEOS-Pairwise` 为 incumbent，不把“队列就绪”写成“算法有效”，也不声称全面 SOTA。下一判定点是 v5 完成后 seed195 的12场景开发门；其结果无论阳性或阴性都必须按冻结协议推进条件确认和后续独立候选。
