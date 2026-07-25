# strict-v4 全面 SOTA 与自有算法优化阶段报告

更新时间：2026-07-23

## 1. 阶段目标

本阶段不以单一数据集或单次种子排名替代全面结论，而是在统一输入、统一拆分、统一场景推断单元下补齐外部基线，冻结自有算法，再用完全未参与开发的新种子进行确认。核心范围为 7 个数据集、102 个细粒度留一攻击场景、12 个恶意流量大类和 86 个去重原始标签。

7 个核心数据集为 Edge-IIoT、NF-CSE-CIC-IDS2018-v2、USTC-TFC2016、NF-UNSW-NB15-v2、CICIDS2017、CIC-ToN-IoT 和 CICIoT2023。DoHBrw2020 的 3 个恶意隧道细类作为第 8 数据集描述性扩展，不混入 7 数据集确认性主张。

## 2. 基线完整性

OpenDetect 与共享分类器上的 Isolation Forest、One-Class SVM、LOF、PCA reconstruction 已完成全部 102 场景同拆分运行。独立基线报告为 `204/204`，失败数为 0。最终总表通过以下完整性检查：

| 检查 | 结果 |
|---|---:|
| 数据集 | 7 |
| 场景 | 102 |
| 方法 | 22 |
| 独立基线运行检查 | 204 |
| 产物检查 | 1326 |
| 拆分指纹成对检查 | 102 |
| 拆分指纹一致 | 是 |
| 真实未知/测试标签用于拟合或运行时选择 | 否 |

## 3. seed7 完整开发屏幕

| 排名 | 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四指标平均秩 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 领域安全路由 | 0.785848 | 0.777024 | 0.595685 | 0.465323 | 0.635143 | 1.50 |
| 2 | 固定 Rank-Union | 0.785848 | 0.771483 | 0.570017 | 0.428827 | 0.647838 | 2.00 |
| 3 | Pairwise CAEOS | 0.785848 | 0.768855 | 0.586630 | 0.513630 | 0.618404 | 3.75 |
| 4 | OpenDetect | 0.746897 | 0.733439 | 0.525633 | 0.503411 | 0.591630 | 6.00 |

领域安全路由相对 Pairwise CAEOS 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.008169/+0.009055/+0.048307/+0.016739`。四项总体均值和逐套件均非退化，但 AUROC 与 AUPR 的场景块 bootstrap 95% 下界仍分别为 `-0.001792` 和 `-0.001090`。因此 seed7 只用于候选开发和冻结，不能据此写“确认性 SOTA”。

固定套件路由的 252 个合法组合已被穷举。当前路由相对 Pairwise 的最小有向增益为 `+0.008168912`，该假设类的全局最优也只有 `+0.008258312`，额外空间仅 `+0.000089400`。继续更换固定套件映射的收益已经基本耗尽。

## 4. 外部比较器冻结

在完整 22 方法 seed7 总表中，按 AUROC、AUPR、FPR95、OSCR 的平均秩选择唯一最强非 CAEOS 方法，平局按方法名确定。OpenDetect 以平均秩 `6.00` 被冻结为外部确认比较器，确认种子固定为 `137/139/149`，预期 306 个同拆分报告。

外部比较器协议 manifest SHA：`702e4c90d863a94b93ed227178ff212349b14d432f963624126246986599e91d`。该选择在任何新种子 OpenDetect 确认运行前完成，后续不得依据确认结果更换比较器。

## 5. 自有算法候选

### 5.1 领域安全路由

冻结路由为：CICIoT2023、CICIDS2017、NF-CSE 使用 Pairwise；CIC-ToN-IoT、Edge-IIoT 使用 Rank-Cauchy；NF-UNSW 使用 Rank-Union；USTC-TFC2016 使用 Rank-Mean。运行时只读取 `suite_id`，不读取未知类或测试标签。候选 manifest SHA 为 `d7032cc1847e876e9973c0fdb0d035cb32ba75a5d8ea4fab05f70d8685e795b3`。

当前正在种子 `137/139/149` 上执行 102 场景确认。确认协议 SHA 为 `a89fcfc0159f5122be8d3aeb4d622d549a7c306d38adf86298a6a861bd65d74b`。截至北京时间 `2026-07-19 16:18:22`，CAEOS 确认已完成 238/306，失败 0；该计数是运行状态，不是效果结论。

### 5.2 尾部感知连续 Pairwise 排序头

固定套件路由接近上限后，新增 `nested_tail_aware_pairwise_pseudo_unknown_blend`。该方法仅在 known-train/known-validation 的留一已知攻击伪未知任务上构造单调一、二、四次尾部基，联合困难伪未知、困难已知、边界插值和尾部加权成对排序，再以跨任务四指标最小有向均值选择尾部权重与参考风险收缩系数。

开发 pilot 按确定性规则选择每个数据集两个 Pairwise 最困难场景，共 14 场景；测试标签仅用于 pilot 开发判定，不进入训练和运行时选择。14/14 个修复后运行均成功，失败 0，运行时泄漏标志为 0。候选端点相对 Cauchy 模态支持参考的 AUROC/AUPR/FPR95/OSCR 有向均值增益为 `+0.031778/+0.026099/+0.205403/+0.093042`，Known F1 逐位不变。

pilot 的 7 个套件中有 5 个四项完全不退化，最差套件指标为 CICIoT2023 AUPR `-0.049124`，刚高于预注册门槛 `-0.05`；新端点在 3/14 个运行中通过旧式最差折门并成为实际运行端点。自动判定为 `freeze_for_new_seed_confirmation`，但该结果仍使用已开放的 seed7 测试标签作开发筛选，不能进入确认性主表。

首批 Edge-IIoT ransomware/uploading 在训练后写诊断报告时触发旧版平铺候选索引 `KeyError`，没有生成 metrics、scores 或 evidence。失败目录和原协议均已保留；修复只增加嵌套诊断读取器，未改变算法、超参数、场景或种子，并通过 amendment 重新冻结后重跑。

在任何新种子运行前，已冻结 `157/163/167`、完整 102 场景、共 306 次的确认协议，manifest SHA 为 `fd0b17f7cda25aa4be61a83a19fa9466ecd2757aed8bf042ea944e1cbeee8597`。运行时只在 known-only 交叉拟合四指标均值门通过时选择 pilot 已直接评分的尾部端点，否则回退参考风险；24/24 个缓存已生成，截至北京时间 `2026-07-19 16:18:22` 完成 181/306、失败 0。首批 Edge-IIoT Backdoor seed157/163 均实际选择新端点，策略、拆分和泄漏审计通过；四项平均有向增益为 `+0.060321/+0.082487/+0.287769/+0.064606`，只作运行期健康检查，不作提前判定。

## 6. 确认门

领域路由只有同时满足以下条件才升级为最终自有算法：

1. 306 个 CAEOS 与 306 个 MLP 报告完整，失败为 0。
2. 运行时无未知/测试标签泄漏，拆分指纹一致。
3. 四项未知指标总体均值均为正。
4. AUROC、AUPR 场景块 bootstrap 下界严格大于 0。
5. 四项统一 Holm-Wilcoxon `p<0.05`。
6. 所有数据集四项均值非退化，Known F1 非退化。

最终自有算法还必须在相同新种子上通过相对冻结 OpenDetect 的外部确认，才能声明 `confirmed_external_sota_7_datasets_102_scenarios`。DoHBrw2020 只提供描述性扩展，不把声明扩大为 8 数据集确认 SOTA。

尾部感知挑战者的独立确认门更严格：四项总体有向均值、四项场景块 bootstrap 下界和四项 Holm-Wilcoxon 必须全部为正/显著；所有数据集四项均值非退化；Known F1 不变；运行时新端点至少实际触发一次。即使该门通过，也还需在同拆分新种子上与最终领域路由直接比较，才能替换当前主候选。

为防止“先完成者即最终算法”，已在任何锦标赛结果产生前冻结自有算法锦标赛协议，manifest SHA 为 `8db2551480895a1911ce5cd36970463a662c0a44d4823ffb55273746cffce851`。尾部确认失败时保留领域路由/Pairwise；通过时追加 `157/163/167` 上 306 个 Pairwise 同拆分运行，并以四项均值、四项 bootstrap 下界、四项 Holm、逐套件和 Known F1 门决定是否替换。若尾部最终胜出，相对 OpenDetect 的外部确认必须使用全新种子 `173/179/181`，不得复用内部选择种子。

尾部胜出分支的专用外部确认协议也已预先冻结，manifest SHA 为 `cdea80f9bd731b70d2c625a11e6c64f1c44cbfe5c27d4587084c1b565f487ead`：在 `173/179/181` 上分别运行 306 个 Tail-aware 和 306 个 OpenDetect 同拆分任务，仍要求四项均值、四项 bootstrap 下界、四项 Holm、逐套件非退化和 Known F1 非退化全部通过。综合审计已升级为读取锦标赛最终决策和对应种子分支，避免把 seed7 开发表误当成尾部算法确认结果。

## 7. 当前可写与不可写

可写：独立基线 204/204、失败 0；22 方法完整 seed7 屏幕中领域安全路由平均未知指标秩第一；OpenDetect 已按预注册规则冻结为最强非 CAEOS 比较器；领域路由三新种子确认已启动；尾部感知排序头通过 14 场景开发 pilot 并已进入独立三新种子确认。

不可写：领域安全路由已经独立确认；四项指标已全面显著优于全部基线；尾部感知排序头已通过多种子确认、优于领域路由或已成为最终算法；DoH 扩展已经支持 8 数据集全面 SOTA。

## 8. 证据位置

- 完整代码与轻量结果：`source/CAEOS-EMTD`
- 最新实验总览：`source/CAEOS-EMTD/results/experiment_preliminary_summary_latest.md`
- 22 方法总表：`source/CAEOS-EMTD/results/strict_v4_full103_seed7/summary.json`
- 外部比较器协议：`source/CAEOS-EMTD/results/strict_v4_external_confirmation/protocol_manifest.json`
- 尾部感知 pilot 协议及修复记录：`source/CAEOS-EMTD/results/strict_v4_tail_aware_pilot`
- 尾部感知确认协议：`source/CAEOS-EMTD/results/strict_v4_tail_aware_confirmation_protocol_manifest.json`
- 自有算法锦标赛协议：`source/CAEOS-EMTD/results/strict_v4_self_algorithm_tournament_protocol.json`
- 尾部算法专用外部确认协议：`source/CAEOS-EMTD/results/strict_v4_tail_external_confirmation_protocol.json`
- 大规模运行、缓存和逐样本产物：GPU 服务器远端项目目录

## 9. 现代后处理基线补充与最新进度

在原 22 方法总表之后，复用 102 个冻结 MLP 检查点补充 ReAct、DICE 和 SHE。三种方法只用 known-train 拟合后处理器、known-validation 校准阈值，不重训主干，也不使用真实未知或测试标签选模；共完成 306/306 个新增报告，失败 0，102 组 split fingerprint 与源 MLP 逐项一致。协议 manifest SHA 为 `d170433cb2ac9bb19eaf561f4825ee71f44c77d1a5486727945534cf3f2dc8a0`。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四指标平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.746897 | 0.733439 | 0.525633 | 0.503411 | 0.591630 | 6.00 |
| ReAct-Energy | 0.715549 | 0.678694 | 0.474951 | 0.526798 | 0.551987 | 13.00 |
| SHE | 0.721949 | 0.673683 | 0.443406 | 0.523038 | 0.547197 | 15.00 |
| DICE | 0.583394 | 0.618415 | 0.394067 | 0.612370 | 0.451375 | 21.25 |

合并后主表为 25 方法。OpenDetect 仍是唯一最强非 CAEOS 方法，旧外部确认协议继续有效；外部 watcher 已增加后处理矩阵完成标记和比较器决策标记两个硬门，只有决策文件明确选择 `opendetect` 才允许执行旧协议。

截至本次更新，领域安全路由确认完成 143/306，尾部感知确认完成 30/306，二者失败均为 0。详细阶段汇总见 [实验初步总结与后续实验清单](实验初步总结与后续实验清单_2026-07-19.md)。

## 10. 效率证据覆盖与最终测量门

seed7 产物的只读审计显示，自有 Pairwise 核心与 OpenDetect 均覆盖 102/102 场景，但计时语义不可比。前者仅完整记录 `elapsed_seconds`，中位数/均值/P95 为 `232.915/465.284/1829.256 s`；后者仅完整记录 `training_seconds` 与参数量，训练时间中位数/均值/P95 为 `360.749/326.572/577.793 s`，参数量中位数为 `139,815`。推理时间、吞吐、峰值显存及硬件指纹的共同覆盖均为 0/102，所以直接效率比较门为 `FAIL`。

为消除该缺口，已冻结 post-selection 效率协议 `7a3ea3ab5b39fd2c5b40c9601eb704e278713ab9303bd227efc64ae4baf0d94b`。协议不参与准确率选模，只在最终算法及外部比较器确认完成、且确认矩阵不再占用服务器时运行；测量全部 102 场景的批量 1/64/512 推理延迟与吞吐，并在 7 个与效果无关的 SHA 确定性哨兵场景上重复测量特征准备、训练、校准、显存、主存和模型大小。

截至该审计完成时，领域安全路由为 `149/306`，尾部感知为 `40/306`，失败均为 0；后续锦标赛、DoH、外部确认与综合审计尚未越过依赖门。

## 11. GEN 盲态 Pilot 与预算决策

为补齐冻结 softmax 后处理路线，按 GEN 作者公式实现 `gamma=0.1`、`M=min(100, known classes)` 的 generalized entropy 风险，并加入 Shannon entropy 诊断。Pilot 按 coverage SHA 从 7 个套件各抽取 2 个场景，共 14 个；全部 28 份方法报告完成，失败 0，拆分一致。

GEN 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.744728/0.618568/0.499841/0.619851/0.539728`，四指标平均秩 2.25；OpenDetect 为 `0.771531/0.730022/0.588984/0.563472/0.598130`，平均秩 1.00。GEN 相对 MLP Energy 的四指标平均有向增益仅 `+0.002760`，且只有 3/7 套件非负，未通过套件稳健性门，因此停止 102 场景扩展。

Pilot 协议 SHA 为 `bbfe431597ead4cddaf2e6ecc9fa8eaa49a4119dbbc77620854522e82601dbcf`；扩展门 SHA 为 `1da320d78438009322ddf783b9d6da6250d719b0505c2ed2108428b9a81ef0be`。扩展门在已有 9 个文件但尚未读取指标值时冻结，属于开发预算盲态门，不冒充严格运行前预注册。最新主确认进度为 Router `155/306`、Tail-aware `52/306`，失败均为 0。

## 12. seed7 风险覆盖与可信工作点

对 102 个 Pairwise CAEOS/OpenDetect 同拆分场景完成只读风险覆盖分析，协议 SHA 为 `7ebb4fa5aefff0dbdba302a7da7a545076b13e383f1a679325bff72de6ee31c8`。Pairwise CAEOS 的 AURC/EAURC 为 `0.230306/0.095487`，OpenDetect 为 `0.287912/0.142988`，有向改善 `+0.057606/+0.047502`。

在 known-validation 0.95 分位阈值下，Pairwise CAEOS 的已知接受率/未知拒绝率/开放集准确率为 `0.936218/0.413095/0.653447`，OpenDetect 为 `0.948052/0.282366/0.589353`。自有算法降低约 1.18 个百分点的已知接受率，但增加约 13.07 个百分点未知拒绝率和 6.41 个百分点开放集准确率。0.975 工作点仍保持未知拒绝率 `+0.140321`、开放集准确率 `+0.069606` 的优势。

这些曲线仅说明 seed7 Pairwise 风险排序的操作特性，不参与领域路由/尾部算法选择，也不升级确认性 SOTA 声明。最终算法及外部确认完成后，需要在对应新种子分支复算相同指标。

## 13. seed7 核心机制消融

新增 102 场景只读机制消融，冻结协议 SHA 为 `6f3d7cad4c2ef9bbf040abd7ee1f62443a9ed4f7cc0e58e49f4707921a8c011e`。固定参考 `cauchy_modality_support_union` 是两层结构：先分别构造冲突/树分歧的 Cauchy 证据支路和全局距离/各模态 KNN 的 Bonferroni 支撑支路，再对两支路做 Bonferroni 并集。

参考方法相对 `modality_support_union`、`cauchy_modality_support`、`support_union`、`max_modality_knn` 的 AUROC/AUPR/FPR95/OSCR 四指标平均有向增益分别为 `+0.089984/+0.084150/+0.062336/+0.066014`，说明双支路融合是必要机制。相对简单 baseline 和独立 `cauchy_evidence` 的四指标平均分别为 `-0.034857/-0.020144`，主要损失在 FPR95 与 OSCR；这限制了“固定融合全面更优”的声明。

冻结 Pairwise 端点在 14/102 场景选择 `pseudo_unknown_learned_blend`，其余 88 场景回退固定参考。它相对固定参考的四项未知指标平均提升 `0.007598`，但属于 seed7 开发证据。下一步仍按已冻结的新种子领域路由和尾部感知确认决定最终算法，之后才触发外部确认与最终风险覆盖复算。最新进度为 Router `165/306`、Tail-aware `70/306`，失败 0。

## 14. 论文撰写与最终证据边界

截至 `2026-07-19 10:17`，Router 为 `171/306`、Tail-aware 为 `82/306`，失败 0。方法、数据、协议、25 方法开发总表、组件消融和风险覆盖已足以支持正文撰写；最优自有算法、外部确认、DoH 扩展、统一效率和最终综合审计尚未闭环，摘要和结论不得使用“确认性全面 SOTA”。

大体积数据和逐场景产物以 GPU 为权威：原始数据位于 `/opt/data/private/wangwt/ParkAttackKE/datasets`，strict-v4 缓存/运行/汇总分别位于远端项目的 `caches/runs/results`。本地 `source/CAEOS-EMTD/results` 只保留轻量汇总与协议。综合审计已从原 22 方法门升级为强制绑定 `strict_v4_posthoc_ood_seed7/summary.json` 的完整 25 方法门；缺少任一 ReAct/DICE/SHE 报告、拆分不一致、发生标签泄漏或比较器不再是 OpenDetect 都会关闭最终声明。

## 15. KLM 补充基线与扩展决策

新增 OpenOOD KLM 官方公式适配。14 场景严格预结果协议 SHA 为 `09a94c863cd657e765c340037b7f59f7d2930dc99b2a61bf62b9e3cc735375f2`，扩展门 SHA 为 `b93fe56537569a1fbfbd15ae98d23348cccbfd5b914e5f6ac4e027900fd0692f`。KLM 的 AUROC/AUPR/FPR95/OSCR 为 `0.735157/0.574731/0.579268/0.581681`，平均秩 3.00；Energy 为 `0.776583/0.594109/0.426248/0.650151`，平均秩 2.00；OpenDetect 仍为第 1。

KLM 相对 Energy 的四项平均有向增益为 `-0.070574`，只有 2/7 套件非负，四项预算门失败，不扩展完整 102。该结果补齐了架构无关的 KL 模板匹配路线，但不改变当前基线排序或外部确认协议。主确认同期进度为 Router `177/306`、Tail-aware `94/306`，失败 0。

## 16. GradNorm 补充基线与扩展决策

新增 OpenOOD GradNorm 的冻结 MLP 适配，并用 autograd 测试验证解析梯度范数与官方逐样本构造等价。严格预结果协议 SHA 为 `62da1675292dc507c816f2b4ce138b311a03d343befc2f00f4b1b2453e2fbf07`，扩展门 SHA 为 `1dfc24e953509389a1662963a91854bc9167ca06038793b7d32837e69929aa59`。14/14 场景完成，失败 0。

GradNorm 的 AUROC/AUPR/FPR95/OSCR 为 `0.578765/0.446665/0.673105/0.518274`，平均秩 3.00；相对 Energy 四项平均有向增益 `-0.103485`，7/7 套件均负，最差 CICIDS2017 `-0.409938`。扩展门拒绝完整 102 场景，不改变外部比较器和主表。主确认同期为 Router `181/306`、Tail-aware `102/306`，失败 0。

## 17. 在途确认矩阵盲态健康审计

为在不窥视中间测试指标的前提下验证一周运行状态，新增独立健康审计器。它验证 coverage/协议 SHA、102 场景与预注册种子身份、四项必需产物、失败文件、固定风险策略、标签泄漏保护、选中风险报告和 provenance 拆分指纹；审计结果不得参与算法选择或修改。

北京时间 `2026-07-19 16:18:22` 的固定快照为 Router `238/306`、Tail-aware `181/306`，剩余分别 `68/125`，失败均为 0，两个部分矩阵均 PASS。该结论仅证明运行链路和已完成产物健康，最终自有算法仍须等待两个 `306/306` 矩阵完成、冻结锦标赛和独立 OpenDetect 外部确认。证据镜像位于 `source/CAEOS-EMTD/results/strict_v4_running_confirmation_health`。

## 18. ODIN 补充基线与扩展决策

新增固定参数 ODIN 表格 MLP 适配。为满足无未知类调参边界，在结果0时冻结 `T=1000`、标准化输入扰动 `epsilon=0.001`；协议 SHA 为 `7b37efa1712e19985beee1338debcf3b073d81d3a6836bedde973bca548c6da1`，扩展门 SHA 为 `ccbeab8b9cc9ffedfbce7eb1e0d38dc9c7c5237b3e33141bad91baf41b65e0ae`。14/14场景完成，失败0，拆分和Known F1一致。

ODIN的AUROC/AUPR/FPR95/OSCR为 `0.686378/0.474673/0.542374/0.585939`，相对Energy四项平均有向增益 `-0.001087`，平均秩同为2.50；OpenDetect仍为第1。Top-2严格秩和总体增益门失败，不扩展完整102，不改变外部比较器或25方法主表。

## 19. ASH-S 补充基线与扩展决策

新增作者公式 ASH-S@90 的冻结表格 MLP 适配。协议 SHA `45f51342c6f770ed1fe571844355f3f1de7e3375ff043bdb52dc9286816577f6`，扩展门 SHA `3d2b608069cb627b7c4dab2eee7ca4062a0d33ba6132656676c1977f8419d10d`，14/14场景完成、失败0。

ASH-S的Known F1/AUROC/AUPR/FPR95/OSCR为 `0.706656/0.562880/0.405167/0.795492/0.457863`，相对Energy四项平均有向增益 `-0.153814`，Known F1平均差 `-0.050944`，平均秩第3，7/7套件退化。全部效果门失败，不扩展102，不改变外部比较器和主表。

## 20. AdaSCALE 自适应缩放基线与扩展决策

新增 [AdaSCALE](https://arxiv.org/abs/2503.08023) 的冻结 MLP 适配。论文 Algorithm 1 明确以 `k1` 计算最高激活处的扰动位移 `Q`、以 `k2` 计算扰动激活修正项 `C_o`；官方仓库校准函数存在二者反置，而推理函数与论文一致，因此本实现按论文和推理函数冻结。固定 `p_min=60`、`p_max=85`、`k1=1%`、`k2=5%`、`lambda=10`、输入扰动比例 `5%`、`epsilon=0.5`、`T=1`，只用 known-validation 构建 `Q'` 的 ECDF 和拒绝阈值，不使用未知类或测试标签调参。64 维 GELU 嵌入使用 ReLU 计算排序与缩放比，百分比取整至少保留 1 个特征。

协议和扩展门在结果数严格为 0 时冻结，SHA 分别为 `66dcf8e45abb2e4c1ebe336fb01b706ef8387a1f9e83709925c78d1e48853ea8` 和 `5b1e255c1c263062b4534c87717bbfe6e1e393ea7f3294e1e38ea340abde304d`。14/14 场景完成、失败 0、拆分一致。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.784446 | 0.701389 | 0.482337 | 0.583002 | 0.603223 | 1.00 |
| MLP Energy | 0.760068 | 0.650331 | 0.451810 | 0.613100 | 0.570416 | 2.00 |
| MLP SCALE | 0.754443 | 0.586852 | 0.436730 | 0.636833 | 0.522101 | 3.25 |
| AdaSCALE-A | 0.758470 | 0.589646 | 0.433277 | 0.685710 | 0.519808 | 3.75 |

AdaSCALE 相对静态 SCALE 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.002794/-0.003452/-0.048877/-0.002293`，四项平均 `-0.012957`；Known F1 平均差 `+0.004027`、最差场景 `-0.009490`，分类容忍门通过，但排名、指标广度、总体增益和套件稳健性门均失败。只有 CICIoT2023 和 NF-CSE 套件均值为正，最差 CICIDS2017 为 `-0.074897`。因此不扩展完整 102 场景，不改变 25 方法主表、OpenDetect 外部比较器或自有算法确认链。轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_adascale_pilot_seed7`。

## 21. OptFS 最优特征整形基线与扩展决策

新增 [OptFS（ICLR 2024）](https://openreview.net/forum?id=dm8e7gsH0d) 官方默认 `Ours (V)` 适配。算法只使用 known-training 嵌入、冻结分类头和模型预测类别：在全局激活值 `0.1%--99.9%` 分位区间内固定 100 个等宽箱，按预测类 logit contribution 学习分箱权重，令 `theta=1000*I(z)/||I(z)||_2`；推理类别仍来自未整形分类器，OOD 风险为整形后 vanilla confidence 的相反数。该流程不使用未知类或测试标签拟合，且原生支持有正有负的 64 维 GELU 嵌入。官方源码中强制抽取 10000 个训练样本的代码只打印类别改变比例，不进入公式，本适配省略该非算法诊断。

协议和扩展门在结果数严格为 0 时冻结，SHA 分别为 `5a3c84504fb7c82d323e1ef7e04f0f126085ba4a7888e16a7689b9ecdf915af0` 和 `1b036e98cf52a78f255f2064370d1f6781b51117b2790ca938bf7daacecfa8a2`。本地及远端公式/协议测试均为 5/5 PASS；14/14 pilot 场景完成、失败 0、拆分一致。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.783304 | 0.775960 | 0.620716 | 0.453305 | 0.653084 | 1.25 |
| MLP Energy | 0.761651 | 0.764873 | 0.607497 | 0.447847 | 0.635583 | 1.75 |
| OptFS Ours (V) | 0.761651 | 0.726284 | 0.512275 | 0.499294 | 0.617366 | 3.00 |

OptFS 相对 Energy 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `-0.038589/-0.095221/-0.051447/-0.018217`，四项平均 `-0.050869`。未整形预测保证 Known F1 完全一致，但 4/4 未知指标和 7/7 数据套件均退化，最差 CICIoT2023 为 `-0.138037`；排名、指标广度、总体增益和套件稳健性门全部失败。因此不扩展完整 102 场景，不改变 OpenDetect 外部比较器、25 方法主表或自有算法确认链。轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_optfs_pilot_seed7`。

## 22. NNGuide Energy-几何引导基线与扩展决策

新增 [NNGuide（ICCV 2023）](https://openaccess.thecvf.com/content/ICCV2023/papers/Park_Nearest_Neighbor_Guidance_for_Out-of-Distribution_Detection_ICCV_2023_paper.pdf) 官方默认 Energy 适配。按论文与官方代码固定从 known-training 随机抽取 `alpha=1%` 的 L2 归一化嵌入 bank，随机种子 0，`k=10`；bank 向量先乘自身 `logsumexp` Energy confidence，查询 guidance 为 confidence-scaled cosine similarity 的 top-k 均值，最终 ID confidence 为查询 Energy 与 guidance 的乘积。未知类、测试标签和 known-validation 均不参与 bank 或超参数选择，known-validation 只定拒绝阈值。14 个场景的最小官方 bank 为 51，因此没有触发低样本适配。

协议和扩展门在结果数严格为 0 时冻结，SHA 分别为 `5b002198a9316d435f531d9acf52f0ae902d03dbc25f77eb274cee2e0b366dfe` 和 `90fc4f6df8bcde9c279c1e0839b2f0b0bbcc3be57f5912bf9d7dd56f5ea96375`。本地及远端公式/协议测试均为 5/5 PASS；14/14 pilot 场景完成、失败 0、拆分一致。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.781245 | 0.706469 | 0.504451 | 0.547006 | 0.605379 | 1.25 |
| NNGuide-Energy | 0.755270 | 0.662106 | 0.437152 | 0.538943 | 0.558579 | 1.75 |
| MLP Energy | 0.755270 | 0.612044 | 0.408809 | 0.604198 | 0.546615 | 3.00 |

NNGuide 相对 Energy 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.050062/+0.028343/+0.065255/+0.011963`，四项平均 `+0.038906`；Known F1 完全一致，完整性、拆分、Known F1、Top-2、指标广度和总体增益 6 项门均 PASS。跨套件稳健性仍失败：仅 CIC-ToN-IoT、Edge-IIoT、NF-UNSW 3/7 套件为正，NF-CSE 最差 `-0.088656`，低于预注册 `-0.05` 下限。因此按原门禁不扩展完整 102；但该结果首次证明“Energy + ID 流形几何”总体有效，后续自有算法优化应研究只依赖 known-only 信号的域安全启用/回退，而不能按测试套件事后选择。

轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_nnguide_pilot_seed7`。它不改变当前 OpenDetect 外部比较器，也不进入确认性最终主表。

## 23. LINe-IDTune 重要神经元基线与扩展决策

新增 [LINe（CVPR 2023）](https://openaccess.thecvf.com/content/CVPR2023/papers/Ahn_LINe_Out-of-Distribution_Detection_by_Leveraging_Important_Neurons_CVPR_2023_paper.pdf) 公式适配。官方代码按真实训练标签计算冻结线性头的 class-wise 一阶 Taylor 贡献，在原始预测类别上依次执行 activation pruning、weight pruning、上界激活裁剪和 `logsumexp` Energy。冻结线性头下，单样本 Taylor 贡献可精确化简为“嵌入乘真实类分类权重”，无需逐样本反向传播。

原论文对 CIFAR-10/CIFAR-100 的剪枝比例用多个 OOD 测试集平均 FPR95 做消融，并明确要求按模型过参数化程度选择；官方仓库对 CIFAR-10、CIFAR-100、ImageNet 采用不同参数。因此本实验不冒充统一官方默认复现，而命名为 `LINe-IDTune`：只在论文/官方代码出现的 `(p_w,p_a)=(10,10)/(90,90)/(90,10)` 中选择；原始裁剪常数替换为 known-training 嵌入 `0.90/0.95/0.99` 分位数，仅以 known-validation NLL 最小化选择。未知类、测试标签和辅助 OOD 均不参与拟合或参数选择，原始分类器预测保持不变。

协议和扩展门在结果数严格为 0 时冻结，SHA 分别为 `c947c39bf89130f9c766d3703eeff52319be531e2efc2aa036647b665b8dba9a` 和 `e323315609736a4564265445d037cacd87bedf7bafe80eb7538868fc1c73decd`。本地及远端公式/协议测试均为 5/5 PASS；14/14 pilot 场景完成、失败 0、拆分一致。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.791481 | 0.710610 | 0.602572 | 0.565661 | 0.591212 | 1.25 |
| MLP Energy | 0.760686 | 0.679914 | 0.545394 | 0.589621 | 0.580155 | 2.25 |
| LINe-IDTune | 0.760686 | 0.673998 | 0.519235 | 0.550657 | 0.578695 | 2.50 |

LINe-IDTune 相对 Energy 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `-0.005916/-0.026159/+0.038964/-0.001460`，四项平均仅 `+0.001357`。Known F1 完全一致，但只有 FPR95 改善，平均秩、指标广度和套件稳健性门失败；仅 CIC-ToN-IoT 与 NF-UNSW 2/7 套件为正，NF-CSE 最差 `-0.019427`。因此不扩展完整 102。机制结论是重要神经元裁剪可降低尾部误报，却会损伤整体未知排序；后续只能把它视为 known-only 适用性门控的尾部候选组件，不能直接替代主风险。

轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_line_idtune_pilot_seed7`。最新盲态健康快照为 Router `238/306`、Tail-aware `181/306`，失败均为 0；该 pilot 不改变 OpenDetect 外部比较器和确认性主线。

## 24. fDBD 决策边界距离基线与扩展决策

新增 [fDBD（ICML 2024）](https://proceedings.mlr.press/v235/liu24ax.html) 官方实现适配，官方仓库固定到 commit `961621e320bfeb9d7456356945fdcafb8a12868b`。该方法以冻结分类器预测类为基准，累加样本到其余类别线性决策边界的闭式距离，并除以样本嵌入到 known-training 全局均值的距离；只拟合训练均值，无可调超参数、辅助模型或辅助 OOD。known-validation 仅校准拒绝阈值，原始分类预测不变。数值实现只在零范数处使用 `1e-12`，14 个场景均未触发非自身重复权重保护。

协议和扩展门在结果数严格为 0 时冻结，SHA 分别为 `7603f9e6ca93c71a333acdf182d19f0dcab43395a3540500704389e68050110d` 和 `08cf376b0d241d412c7feaf13d18277a7fa681f966427e0a4dba2d4caaa39c2e`。本地及远端公式/协议测试均为 5/5 PASS；14/14 pilot 场景完成、失败 0、拆分一致。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| MLP Energy | 0.756812 | 0.664793 | 0.476054 | 0.594420 | 0.565793 | 1.25 |
| OpenDetect | 0.783009 | 0.655398 | 0.480744 | 0.605731 | 0.560082 | 2.25 |
| fDBD | 0.756812 | 0.644517 | 0.445560 | 0.603536 | 0.563653 | 2.50 |

fDBD 相对 Energy 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `-0.020276/-0.030494/-0.009116/-0.002140`，四项平均 `-0.015506`。Known F1 完全一致，但 Top-2、指标广度、总体增益和套件稳健性门均失败；仅 Edge-IIoT、NF-CSE、USTC-TFC2016 3/7 套件为正，最差 NF-UNSW 为 `-0.058667`。因此不扩展完整 102。该结果表明在当前流量嵌入上，使用单一全局均值归一化决策边界距离不如直接 Energy 稳定，也进一步支持自有算法继续采用类条件、模态条件和尾部条件的局部风险，而不是全局几何标量。

轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_fdbd_pilot_seed7`。最新正式盲态健康快照为 Router `238/306`、Tail-aware `181/306`，失败均为 0；fDBD 不改变 OpenDetect 外部比较器和确认性主线。

## 25. NECO-ID90 主成分投影基线与扩展决策

新增 [NECO（ICLR 2024）](https://proceedings.iclr.cc/paper_files/paper/2024/file/04b84142b99dae8560b517401e6e5275-Paper-Conference.pdf) 官方公式适配，官方 GitLab 固定到 commit `6a55640669f0aad3e23f45ce2f6a8e6400c929ba`。审计发现论文主表按每个 `<模型, ID, OOD>` 组合以 FPR95/AUROC 选择最佳主成分维数，属于测试 OOD 调参，不能进入 strict-v4 无泄漏主表；官方默认 `d=100` 在本项目 64 维嵌入上还会退化为全空间比值 1。故本实验采用论文附录明确给出的通用规则并命名 `NECO-ID90`：只对 known-training 嵌入做 StandardScaler 和 PCA，选择累计解释方差首次达到 90% 的最小维数，风险为主子空间投影范数与完整标准化特征范数之比的相反数。known-validation 只校准拒绝阈值，原始分类预测不变，不使用测试标签、未知类或辅助 OOD 拟合参数。

协议和扩展门在结果数严格为 0 时冻结，SHA 分别为 `05b10bfb3ce4195d58c249accc33a305dbb4a70d4156756bdeec455916a1da9b` 和 `505c5f97d000b4b40efcf7644eba56997c8413fce86e7a8e51f17ec13cd0aa26`。本地及远端公式/协议测试均为 5/5 PASS；14/14 pilot 场景完成、失败 0、拆分一致。14 个场景选择维数为 9--19，均严格小于 64，非退化门通过。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.770719 | 0.683294 | 0.503985 | 0.626929 | 0.578047 | 1.50 |
| MLP Energy | 0.746256 | 0.636243 | 0.485875 | 0.587831 | 0.544774 | 2.25 |
| NECO-ID90 | 0.746256 | 0.660776 | 0.473864 | 0.599999 | 0.545413 | 2.25 |

NECO-ID90 相对 Energy 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.024533/-0.012011/-0.012168/+0.000639`，四项平均仅 `+0.000248`。完整性、拆分、Known F1、非退化维数、指标广度和总体增益门通过，但严格 Top-2 秩与套件稳健性门失败：5/7 套件为正，CIC-ToN-IoT 和 NF-UNSW 分别为 `-0.200560/-0.140302`。因此不扩展完整 102。该混合结果说明 ID 主子空间能改善部分 AUROC，但单一全局主子空间无法稳定控制 AUPR 和尾部误报；它支持在自有算法中保留域安全、类条件和尾部条件门控，而不是直接使用全局 PCA 投影比值。

轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_neco_id90_pilot_seed7`。北京时间 `2026-07-19 16:46:11` 的最新正式盲态健康快照为 Router `240/306`、Tail-aware `202/306`，失败均为 0、健康 PASS；NECO-ID90 不改变 OpenDetect 外部比较器和确认性主线。

## 26. NAC-UE-Fixed 神经元覆盖基线与扩展决策

新增 [NAC（ICLR 2024）](https://proceedings.iclr.cc/paper_files/paper/2024/hash/2b1a955952bc98518a331ad6d8cc524d-Abstract-Conference.html) 的神经元激活覆盖适配，官方仓库固定到 commit `16933b0b17fe451cdcd60f77d95d8746e57da4cc`。官方评估器会在 OOD validation loader 上遍历超参数并以 AUROC 选择最优组合，不能直接进入 strict-v4 无泄漏比较。故本实验明确命名为 `NAC-UE-Fixed`，并在任何流量结果产生前按官方 CIFAR-10/ResNet avgpool 默认冻结：`valid_num=1000`、`M=50`、`O=50`、`alpha=100`、known-training 平衡子集种子 1、测试聚合为平均覆盖。64 维 MLP 最终嵌入作为预分类器 avgpool 类比，神经元状态为 `sigmoid(alpha * o * g_KL)`；其中 uniform-target KL 梯度使用 `(softmax-uniform) @ W` 的解析式，并已与 PyTorch autograd 对齐。覆盖阈值只用 known-training 平衡子集拟合，known-validation 仅校准拒绝阈值，未知类、测试标签和辅助 OOD 均不参与拟合或选参。

14 场景协议与扩展门在结果数为 0 时冻结，SHA 分别为 `dc6b1c1e808e373f07145f4d4e671ced6700ade86321df063bbbf649ebc28b5c` 和 `9dfc7ddf01c8771acc754cca5739b4a62c0b930a6a60b608b858a00bc6bb2610`。14/14 场景完成、失败 0、拆分一致；覆盖平衡子集为 98--1000 个样本，神经元覆盖分数均非退化。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四项平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.777043 | 0.723690 | 0.549098 | 0.512369 | 0.587063 | 1.00 |
| Energy | 0.740311 | 0.670628 | 0.499860 | 0.548813 | 0.561655 | 2.50 |
| NAC-UE-Fixed | 0.740311 | 0.689500 | 0.480847 | 0.611261 | 0.572050 | 2.50 |

NAC-UE-Fixed 相对 Energy 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.018872/-0.019013/-0.062447/+0.010394`，四项平均 `-0.013048`。逐套件平均增益依次为 CIC-IoT `-0.079930`、CIC-ToN-IoT `-0.024829`、CICIDS `+0.004814`、Edge-IIoT `+0.105136`、NF-CSE `+0.189896`、NF-UNSW `-0.140122`、USTC-TFC `-0.146306`。完整性、拆分、Known F1、分数/覆盖非退化和指标广度门通过，但 Top-2、总体增益和套件稳健性门失败，故 `expand_nac_ue_fixed_to_full102=false`。

该结果说明神经元覆盖频率可以提供局部排序信号，但单一全局覆盖统计无法控制跨套件尾部误报，并会牺牲 AUPR。它不直接并入当前自有算法；后续至多作为 known-only 域门控诊断量研究，自有算法仍保持域安全、类条件、模态条件和尾部条件结构。轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_nac_ue_fixed_pilot_seed7`。北京时间 `2026-07-19 17:26:47` 的盲态健康审计为 Router `245/306`、Tail-aware `212/306`、失败均为 0、健康 PASS。

## 27. SIRC-MSP-Fixed Pilot、full102 与 26 方法屏幕

新增 [SIRC（ACCV 2022）](https://openaccess.thecvf.com/content/ACCV2022/html/Xia_Augmenting_Softmax_Information_for_Selective_Classification_with_Out-of-Distribution_Data_ACCV_2022_paper.html) 官方公式适配，官方仓库固定到 commit `0b492695d5bf34942cd8b333d10a998f763c3eff`。SIRC 原任务是含 OOD 的选择性分类（SCOD），与本实验的 OSCR/拒绝工作点直接相关；它保留 MSP 主置信度，并以已知训练嵌入的 L1 范数或负 ViM residual 为辅助置信度。组合风险严格采用官方 `log(1-MSP)+softplus(-b(S2-a))` 等价式，且 `a=mean(S2)-3*std(S2)`、`b=1/std(S2)` 只由 known-training 拟合；known-validation 只校准拒绝阈值，原始分类预测不变。两个官方辅助变体均在结果产生前声明，不使用测试 OOD 选择变体。

14 场景 pilot protocol SHA 为 `652c3f394439fd62a30711da088fa3bc4bd4f56d5973f3904f52043dda03dcbb`，扩展门 SHA 为 `2f62d57c853dad152f747d3b685497023b022a5d5fdece6370f76b747acc1512`，冻结时观测结果为 0。14/14 场景、28 份报告完成，失败 0。SIRC-Residual 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.757017/0.738878/0.540371/0.460899/0.633014`、平均秩 1.50；相对 MSP 四项有向增益为 `+0.035681/+0.054293/+0.044297/+0.019070`，全部扩展门通过。SIRC-L1 为 `0.757017/0.707220/0.486652/0.501730/0.615316`、平均秩 2.75，仅 Top-2 门失败。故只有 Residual 被登记为门通过方法。

full102 协议在结果数为 0 时另行冻结，SHA 为 `400d6eed798d9df494cf40839023ab493ed759f5bf633f2a8e06fb7f7eab7c19`，绑定上述 gate 与 pilot analysis SHA；L1 只作为共享前向的零增量诊断，不进入 26 方法表。102/102 场景、204 份伴随报告完成，失败 0；102 组拆分指纹、源产物绑定和无泄漏检查全部通过。

完整 102 场景上，SIRC-Residual 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.721949/0.638749/0.439290/0.584817/0.549987`，26 方法平均秩 `18.00`。相对 MSP 四项仍全部改善 `+0.042771/+0.050864/+0.026173/+0.020508`，证明 softmax 信息保留组合有效；但相对 OpenDetect 四项全部退化 `-0.094690/-0.086343/-0.081406/-0.041644`。因此 OpenDetect 仍以平均秩 `6.00` 保持最强非 CAEOS 比较器，既有外部确认协议不变。

该结果揭示 14 场景 pilot 对跨套件泛化的乐观偏差：全局 residual 能系统性增强 MSP，却不能替代域条件、类条件和尾部条件风险结构。SIRC 不并入当前自有算法主线；其“主置信度保留 + 辅助信号只在异常区增强”的非线性形式可作为未来域安全门内部的候选融合算子，而不能作为全局统一风险分数。轻量证据位于 `source/CAEOS-EMTD/results/strict_v4_sirc_msp_fixed_pilot_seed7` 与 `source/CAEOS-EMTD/results/strict_v4_sirc_msp_fixed_full102_seed7`。北京时间 `2026-07-19 19:29:00` 盲态健康审计为 Router `256/306`、Tail-aware `220/306`、失败均为 0、健康 PASS。

## 28. DOC-Fixed 必做基线适配与扩展决策

基线缺口复核发现，实验设计将 DOC 标记为必做，但 26 方法表及既有 pilot 队列尚未给出同协议 DOC 结果。本轮按原论文核心机制实现冻结编码器版本：复用同一 strict-v4 MLP 编码器，只在已知训练嵌入上以 one-vs-rest sigmoid BCE 重新拟合线性头；每类阈值固定为 `max(0.5, 1-3*sigma_i)`；连续未知风险为各类 sigmoid 相对类别阈值的最大余量取负。未知测试样本不参与头部训练、Gaussian 阈值拟合或部署阈值校准。公式与协议测试 `6/6` PASS。

14 场景 protocol 与 expansion gate 均在结果数严格为 0 时冻结，SHA 分别为 `097607f752ddb5c2409358704e82a86890925aad638bd7c746c712c1dac75545` 和 `bb9a6bbdb9de8cf90c704c1e007ccd1aad48756deb4c862cc14c5e137eef4e32`。14/14 完成、失败 0、无复用，拆分、优化、阈值范围和无泄漏检查均通过。结果如下：

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四指标平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| OpenDetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 | 1.00 |
| MLP-Energy | 0.734638 | 0.693708 | 0.541199 | 0.473140 | 0.573935 | 2.00 |
| MLP-MSP | 0.734638 | 0.534830 | 0.348210 | 0.633106 | 0.492447 | 3.25 |
| DOC-Fixed | 0.764091 | 0.506392 | 0.394597 | 0.698118 | 0.443588 | 3.75 |

DOC 相对 MSP 的 Known F1 提高 `+0.029452`，AUPR 提高 `+0.046386`，但 AUROC/OSCR/FPR95 有向增益为 `-0.028438/-0.048859/-0.065012`，四指标均值 `-0.023981`。仅 CICIoT2023、CIC-ToN-IoT 和 Edge-IIoT 为正，最差 USTC-TFC2016 为 `-0.216368`；Top-2、指标广度、总体增益和套件稳健性门失败，因此 `expand_doc_fixed_to_full102=false`。该结果补齐了预定 DOC 适配证据，并说明独立 sigmoid 头能改善已知分类，却不能替代 Energy/OpenDetect 的未知排序。证据位于 `source/CAEOS-EMTD/results/strict_v4_doc_fixed_pilot_seed7`。北京时间 `2026-07-19 20:06:54` 盲态健康审计为 Router `260/306`、Tail-aware `224/306`、失败均为 0、健康 PASS。

## 29. Entropy/Prototype 必做 full102 与 28 方法表

新增 Shannon entropy 和独立 Prototype Distance 两个实验设计必做基线。两者复用冻结 MLP 前向，保持原分类预测；Prototype 仅由 known-training 嵌入的类均值拟合，两者均只用 known-validation 定拒绝阈值。协议在结果 0 时冻结，SHA 为 `1cc461ce85b0f43163ad9f73032689ffd4d48808700cd90743bee80666508cf9`。

102 场景、204 报告完成，失败 0；源绑定、拆分指纹、无泄漏和分数非退化检查均为 102/102 PASS。Prototype 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.721949/0.663798/0.447512/0.550775/0.523630`，28 方法平均秩 18.50；Entropy 为 `0.721949/0.621017/0.410697/0.587537/0.542249`，秩 21.50。它们均未超过 OpenDetect 的 `0.746897/0.733439/0.525633/0.503411/0.591630`、秩 6.00，所以比较器不变。

该结果说明简单信息熵和全局类中心几何可改善 MSP，但不能取代跨套件的类条件、模态条件、冲突与尾部建模。领域安全路由仍为 seed7 开发屏幕第一，但全面 SOTA 仍被新种子确认门关闭。北京时间 `2026-07-19 21:45:37` 盲态审计：Router `270/306`、Tail-aware `232/306`、失败 0、PASS。

## 30. 独立训练强基线与综合审计 v5

复核 28 方法表后确认，它已经覆盖共享冻结 MLP 上的经典与现代风险评分，但七数据集 strict-v4 仍缺少同划分、独立训练的 CLOSR、CADE 和 Sieve 证据。为控制算力预算且避免事后挑选，已在任何候选结果产生前冻结 14 场景训练试点：每套件按既有 coverage-SHA 注册表取 2 个场景，共 42 个方法运行；CLOSR/CADE/Sieve 训练预算分别为 100/250/100 epoch。协议 SHA 为 `4a3ffcdf59026f9341dfebf799245bfdd21eb0580d32c4f2320dd8196ee65512`，扩展门 SHA 为 `504f2ef6a0c76fc96cc218a2a2df18765be76f6f5edc28adaa66911ea5b7f0af`。

拟合与 checkpoint/阈值选择只允许已知训练集和已知验证集。每个候选必须同时满足完整性、拆分与无泄漏、Known F1 容忍、四项未知指标 Top-2、指标广度、总体正增益和跨套件稳健性门；任一候选过门，必须扩展至完整 102 场景，未完成前禁止最终外部确认和全面 SOTA 声明。

综合 SOTA 审计已升级到 v5，硬绑定第一组协议、扩展门和最终分析；审计测试和训练试点证据结构测试均 PASS。本阶段结论随后由第 31 节的 v6 审计取代。

## 31. strict-v4 互补主/强基线与综合审计 v6

覆盖审计发现：ARPL、RoNeTC 和 FOSS 虽然在旧 DoH/Mal_TLS/HIKARI 39 任务矩阵中有同协议结果，ARPL/PALM/RoNeTC 也有 6 场景 strict-v4 试点，但它们没有进入当前七数据集 102 场景的冻结基线门。旧任务、旧数据集或未预冻结的小试点不能替代七数据集证据。因此新增第二组互补训练试点：ARPL、PALM、RoNeTC、FOSS，沿用与第一组完全相同的每套件 2 场景注册表，共 14 场景、56 方法运行。

协议与扩展门在结果数严格为 0 时冻结，SHA 为 `1a982b0b4881f98a68f3d7816ddd7079bdfd4f3d477b08ac943855acdb52e38e` / `f311a74c3b74996272b18360bb7badd8442d717f6f7300007050c5eca9a87447`。ARPL/PALM/RoNeTC/FOSS 预算分别为 35/500/100 epoch 和 30 棵 FOSS 隔离树；训练、checkpoint 与阈值仍限定在 known-training/known-validation。任一候选通过七项冻结门，必须补跑 full102。

综合 SOTA 审计升级到 v6，并将第二组试点设为最终外部确认和综合声明的硬依赖；互补协议测试 4/4、综合审计测试 13/13 远端 PASS。北京时间 `2026-07-19 23:35`，Router `280/306`、Tail-aware `240/306`、第一组强基线 `17/42`、第二组 `0/56`，失败均为 0。第二组 watcher PID `2800451`，综合审计 v6 PID `2865237`，最终外部确认 watcher PID `2865238`，锁均存在。

## 32. AEGIS clean-label 适配与综合审计 v7

实验矩阵将 AEGIS-Net/1D-ResNet 列为条件强基线。官方实现使用训练真标签精度选 checkpoint、跨数据集 Darknet 作为 OOD，并在发布版 `predict` 中错误压掉 Conv1d 通道维，不能直接进入 strict-v4。本轮实现 clean-label adapter：保留 1D-ResNet、监督对比、密度原型伪标签纠正和 k=50 归一化特征近邻评分；checkpoint 只按 known-validation Macro-F1 选择，拒识阈值只用 known-validation 95% 分位。该结果只评价干净已知训练下的开放集能力，不冒充原论文标签去噪结论。

模型/损失/伪标签/KNN 单测 3/3 PASS；单轮端到端 GPU 冒烟覆盖训练 `1022`、验证 `276`、测试 `352`、未知 `50`，约 `7,013,920` 参数，拆分指纹、无泄漏证据、`metrics.json` 与 `scores.npz` 全部 PASS。正式 14 场景 protocol/gate 在 `0/14` 时冻结，SHA 为 `6b593c2e2c09de882f692d9a06f01a2e319ea2eabe3bf6962081c90fef9e3dd9` / `54136f2c499c1a9b86340a517d65950108c925f348b9890c14e5d1790b9da413`；协议测试 3/3 PASS。

综合 SOTA 审计升级到 v7，将 AEGIS 试点列为第三组硬依赖；综合测试 15/15 远端 PASS。北京时间 `2026-07-20 00:21`，Router `284/306`、Tail-aware `244/306`、第一组 `36/42`、第二组 `0/56`、AEGIS `0/14`，失败均为 0。AEGIS watcher PID `3982191`，审计 v7/外部确认 PID `4022926/4022927`，锁均存在。

## 33. 第一组独立训练强基线终态与 AEGIS 调度链验证

CLOSR、CADE、Sieve 的冻结试点已 `42/42` 完成、失败 0，14 个场景的拆分指纹和无泄漏证据全部通过。OpenDetect 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.766127/0.800369/0.635266/0.350782/0.637880`，四项未知指标均列第 1。CADE、Sieve、CLOSR 的四指标平均秩分别为 `2.75/2.75/3.50`；相对 OpenDetect 的四指标有向平均增益为 `-0.200113/-0.192966/-0.211599`，Known F1 平均差为 `-0.109370/-0.131317/-0.149684`。三者均未通过 Known F1、Top-2、指标广度、总体增益和跨套件稳健性门，冻结结论为 `expand_to_full102=[]`，不产生 full102 义务。

第一组结束后互补组已自动启动。北京时间 `2026-07-20 00:45`，Router `286/306`、Tail-aware `246/306`、互补组 `3/56`、AEGIS `0/14`，失败均为 0。AEGIS 额外完成命令构造单测，适配器加协议共 `7/7 PASS`；独立矩阵运行器 GPU 冒烟 `1/1` 完成、零失败，manifest 为 `state=complete`，provenance、metrics、scores 和无泄漏选择证据齐全。正式 AEGIS 目录仍保持 `0/14`，冒烟位于隔离目录，不污染冻结试点。

## 34. 训练强基线 full102 自动扩展与综合审计 v8

为关闭“试点过门后只有阻断、没有执行器”的缺口，新增互补组/AEGIS 通用 full102 扩展链。它只在试点 `expand_to_full102` 非空时运行：扩展结果严格为 0 时冻结协议，绑定 coverage SHA、试点协议 SHA、试点分析 canonical SHA 与全部实现 SHA；随后按同一 seed7 划分补跑七套件 102 场景，并要求运行数、失败数、拆分指纹和无泄漏检查全部通过后生成 `full102_expansion_complete`。无人过门时 watcher 记录 `not_required` 后退出。

综合审计升级到 v8。负试点仍要求所有候选决策完整且无扩展；正试点则必须同时验证扩展协议 SHA、试点链绑定、102 场景、`102×候选数` 运行、102 项拆分和无泄漏检查。缺少扩展、证据篡改或无泄漏计数 101/102 均失败关闭；中断续跑会重算期望协议，拒绝实现或试点证据漂移。扩展协议测试 5/5、综合审计测试 18/18，本地和远端共 23/23 PASS；Bash 静态检查 PASS。远端 full102 watcher PID `1725571/1725573`，审计 v8 watcher PID `2075079`，锁均存在。

北京时间 `2026-07-20 01:30`，Router `291/306`、Tail-aware `248/306`、互补组 `19/56`、AEGIS `0/14`，失败均为 0。该改动消除了正向扩展死锁，但不改变当前声明边界：必须等待实际训练、锦标赛、外部确认和 v8 最终审计完成。

## 35. XGBoost 五种子闭集强基线

实验矩阵 C2 要求 XGBoost/LightGBM 至少完成其一。本轮在 GPU 端隔离安装 XGBoost 2.1.4，不修改 `py3.9` 环境；正式协议固定 Mal_TLS2023、23 类、每类最多 500 条、种子 `7/11/19/23/29`、1000 棵树、深度 8、学习率 0.05、subsample/colsample 0.9 和已知验证集 mlogloss early stopping。协议 v3 在 `0/5` 时冻结，SHA 为 `85c6735b51a9ab07c24902c3d05ffe078e5823ad4675c743038b329f6b240c97`，并绑定数据、配置、训练器、协议生成器、运行器和汇总器 SHA。

五个种子全部完成、失败 0；每次训练/验证/测试为 `8050/1725/1725`，完成态审计确认 23 类、有限指标和测试标签未参与拟合或选择。结果如下：

| 指标 | XGBoost 均值±标准差 | 相对 MC7-Stable 的配对均值 |
|---|---:|---:|
| Accuracy | `0.974377±0.002470` | `-0.000812` |
| Macro-F1 | `0.974380±0.002474` | `-0.000766` |
| Weighted-F1 | `0.974380±0.002474` | `-0.000766` |
| ECE | `0.010414±0.001644` | `+0.002623` |
| NLL | `0.079656±0.005722` | `+0.006154` |

ECE/NLL 越低越好，因此后三个配对结果共同表明 MC7-Stable 在分类与校准上总体更优。XGBoost 完成 C2 基线义务，但只属于行分层闭集支撑证据，不进入 strict-v4 开放集 28 方法表，也不改变 OpenDetect 或最终自有算法的选择。北京时间 `2026-07-20 02:38`，开放集主线为 Router CAEOS `298/306`、Tail-aware `254/306`、互补组 `39/56`、AEGIS `0/14`，失败均为 0；全面 SOTA 仍未证实。

## 36. Router 确认计数口径校正

`run_strict_v4_domain_safe_router_confirmation.sh` 的 CAEOS 与 MLP/OpenMax 两个根目录各自要求 `306` 个运行。CAEOS 完成后才启动 MLP/OpenMax，二者齐全后才执行融合、确认和最终选择。因此历史快照中的 Router `x/306` 是 CAEOS 阶段健康计数，不等于端到端总任务只含 306 次。北京时间 `2026-07-20 02:45`，准确状态为 CAEOS `298/306`、MLP/OpenMax `0/306`、Router 完成标记不存在；Tail-aware `254/306`，互补组 `46/56`，AEGIS `0/14`，失败均为 0。此修正不改变已完成实验结果，但会延后 Router 锦标赛的预期完成时间。

## 37. D1-D7 冲突度量专项与自有机制取舍

实验矩阵要求条件冲突与标签不一致、余弦距离、JS、对称 KL、原始 DS 和可靠度条件冲突直接比较。本轮绑定 `runs/strict_v4_full103_pairwise_caeos_seed7` 的 102 个证据包、scores 与 metrics，共 306 项 SHA 完整性检查；最终 v3 protocol SHA 为 `b542de526accc79bbe505a3e90e7bd4d94cbfd211192bba24061f80c4dc10157`，源清单 SHA 为 `6335a5734dc528f3165dc29a3c98c4e2239e40344938044d32e64efb734ea6a1`。未知/测试标签不进入模型、风险或阈值选择，只用于完成后的机制统计。

| 度量 | 平均 Unknown AUROC | 平均秩二列效应 | 与不确定性 Spearman |
|---|---:|---:|---:|
| D1 标签不一致 | 0.625370 | 0.250739 | 0.506808 |
| D2 余弦距离 | 0.642711 | 0.285422 | 0.302313 |
| D3 Jensen-Shannon | 0.629649 | 0.259298 | 0.210086 |
| D4 对称 KL | 0.628075 | 0.256151 | 0.168127 |
| D5 原始 DS | 0.570844 | 0.141688 | -0.154473 |
| D6 条件 DS | 0.714025 | 0.428050 | 0.721814 |
| D7 可靠度条件 DS | 0.722043 | 0.444087 | 0.715196 |

D6-D5 的平均 AUROC 增益为 `+0.143181`，102 场景正增益率 `0.715686`；固定种子 10,000 次 bootstrap 95% CI 为 `[+0.083157,+0.203062]`，单侧配对 Wilcoxon `p=1.4689e-6`，七个套件的均值增益均为正。控制平均模态不确定性后，D6 在 77/102 场景中系数为正且通过度量内 Benjamini-Hochberg FDR，说明条件冲突并非完全由不确定性替代。

D7 相对 D6 平均仅 `+0.008018`，正增益率恰为 `0.50`，未通过稳定增益门。最终机制取舍是：保留 D6 条件归一化作为核心创新和风险候选；可靠度仍用于模态污染与融合折扣，但不单独宣称其普适提高未知检测。D6 最差场景 AUROC 仍仅 `0.032653`，异质性明显，因此最终算法继续使用域安全路由，不能全局固定为单一冲突风险。北京时间 `2026-07-20 03:18`，Router CAEOS `300/306`、MLP/OpenMax `0/306`、Tail `256/306`、互补组 `54/56`、AEGIS `0/14`，失败均为 0。

## 38. 互补强基线终态与 F3 可学习注意力

ARPL/PALM/RoNeTC/FOSS 冻结试点已 `56/56` 完成、失败 0，14 项拆分与无泄漏检查通过。OpenDetect 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.766127/0.800369/0.635266/0.350782/0.637880`，四项未知指标平均秩 `1.00`。FOSS/PALM/RoNeTC/ARPL 平均秩依次为 `3.00/3.50/3.50/4.00`，四者均未通过冻结扩展门；`strict_v4_complementary_training_full102_seed7/not_required` 已落盘，OpenDetect 比较器不变。PALM 的适配器键名 `palm_ssd_plus` 与协议简称不一致，已用严格一对一只读别名修复汇总器并通过 6/6 回归测试，训练产物与冻结门均未修改。

F3 熵条件可学习注意力在 102 个冻结场景上完成，协议 SHA 为 `9e130bf5905b54093f0080091fa2ca050ea67fb7374c99d866f0c479f3489424`，306 项源 SHA 检查通过。它只用已知验证集学习三个模态偏置和一个熵系数。注意力的 Known F1/AUROC/AUPR/FPR95/OSCR/ECE 为 `0.733796/0.706727/0.489718/0.514855/0.614743/0.076775`；相对 CAEOS 可靠度融合的有向增益为 `-0.002256/-0.025996/-0.025438/-0.029996/-0.016353/+0.010352`，未胜出。注意力只改善校准，不进入最终自有算法；现有可靠度融合、D6 条件冲突和域安全路由保持不变。

北京时间 `2026-07-20 04:04`，Router CAEOS 已 `306/306` 并自动进入 MLP/OpenMax `18/306`；Tail-aware `262/306`；AEGIS 已启动并完成 `1/14`，失败总数 0。F3 与互补组缺口已关闭，但全面 SOTA 仍被 Router 第二阶段、Tail、AEGIS、锦标赛、独立外部确认和综合审计阻断。

## 39. F2-F9 共享证据融合算子矩阵

追加 102 场景共享证据的 F2 概率平均、F3 熵条件注意力、F4 EDL Sum、F5 可靠度门、F6 标准 DS 和 F9 CAEOS 最终概率对照。v1 因错误地在 F5 前逐视图预归一化而与存储权威值存在最大 `0.001097` OSCR 漂移，已归档；v2 在零结果重冻，协议 SHA `2b3c137bd7274891718903aa385faed5610dd7b9b22d7df34ef4e90c431a59c6`，306 项源 SHA 及 F3/F5 逐项一致性检查 PASS。

四项未知指标平均秩为 F9 `1.00`、F4/F6 `2.75`、F5 `3.50`、F2 `5.25`、F3 `5.75`。F9 的 Known F1/AUROC/AUPR/FPR95/OSCR/ECE 为 `0.785848/0.739934/0.539348/0.473098/0.641875/0.056823`；相对标准 DS 有向增益为 `+0.053171/+0.007084/+0.018063/+0.000583/+0.011643/+0.561323`。标准 DS/EDL Sum 的排序尚可但 ECE 超过 `0.61`；可靠度门校准较好但整体不及 F9。因此完整路由与冲突机制保持，普通 DS、证据求和和注意力均不替换当前自有算法。

北京时间 `2026-07-20 04:24`，AEGIS `5/14`、Router MLP/OpenMax `72/306`、Tail `264/306`、失败 0。融合基线矩阵已关闭，后续算力继续用于确认链而非新增同质融合变体。

## 40. 综合 SOTA 审计 v9

综合终审新增融合证据硬门：fusion v2/attention v1 协议 SHA、102 场景、306 项源校验、六方法完整性、F3/F5 与独立注意力分析逐项一致、测试真值隔离和污染主张禁用必须全部 PASS。审计 schema 升级为 `strict_v4_comprehensive_sota_audit_v9`；交叉结果篡改测试会失败关闭。

本地和远端测试均 `19/19 PASS`，远端 Bash 静态检查 PASS。旧 v8 watcher 已有序停止，v9 watcher PID `4091654`、锁有效。北京时间 `2026-07-20 04:38`，AEGIS `9/14`、Router MLP/OpenMax `104/306`、Tail `267/306`、失败 0。最终声明仍由全部原硬门与新增融合硬门共同控制。

## 41. AEGIS 训练强基线终态

AEGIS clean-label 冻结试点 `14/14` 完成、失败 0，14 项拆分和无泄漏检查通过。AEGIS 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.768204/0.834617/0.667903/0.346459/0.666426`，四项未知指标平均秩 1.00；OpenDetect 为 `0.766127/0.800369/0.635266/0.350782/0.637880`、平均秩 2.00。AEGIS 四项有向增益为 `+0.034249/+0.032637/+0.004323/+0.028546`，Known F1 平均差 `+0.002077`。

AEGIS 虽通过其余六项门，但套件增益在 CIC-ToN-IoT/USTC-TFC 为 `-0.095161/-0.100566`，只有 4/7 套件非负，冻结套件稳健性门失败。因此 `expand_to_full102=[]`，watcher 已写 `not_required`；不改变 28 方法主表和 OpenDetect 外部比较器。北京时间 `2026-07-20 05:03`，Router MLP/OpenMax `153/306`、Tail `270/306`、失败 0。三组训练强基线现在均已封板，剩余主阻断集中在自有算法确认、锦标赛、外部确认、DoH 和效率审计。

## 42. Router、Tail-aware 与最终自有算法

Router 两阶段均完成 `306/306`、失败 0。相对 Pairwise，其 AUROC/AUPR/FPR95/OSCR 有向平均增益为 `+0.000141/+0.000487/+0.017408/+0.006074`，Known F1 不变；但四指标 bootstrap 正下界、Holm 显著性和全套件非回退未同时满足，冻结替换门 FAIL。

Tail-aware 也完成 102 场景 x 3 新种子共 `306/306`。相对冻结 reference，Known F1 保持 `0.798268`，AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.008555/+0.008218/+0.061314/+0.026340`；AUROC、FPR95、OSCR 的 95% CI 下界为正，但 AUPR 区间为 `[-0.006201,+0.020284]`，且 CIC-IoT2023、CIC-ToN-IoT、NF-UNSW 存在套件回退。Tail 严格确认门和 replacement gate 均 FAIL。

预注册锦标赛因此冻结选择 `caeos_pairwise`，状态为 `frozen_optimal_self_algorithm`，manifest SHA 为 `5300b2a309237aa20dd490ac0ce658d3368896df4ee311d8a2a61484db6aaf26`。这一结论意味着 Router/Tail 的平均改进可以作为失败消融和异质性分析，但不能替换论文主算法，也不能包装为确认性提升。

## 43. Mahalanobis++、DoH 外推与 29 方法表

Mahalanobis++ 完成 `14/14` 冻结试点并通过扩展门，随后完成七套件 `102/102` 全屏幕、失败 0。其 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.721949/0.727044/0.529891/0.485973/0.563717`，四项未知指标平均秩 `7.25`，优于标准 Mahalanobis 的 `8.50`，但未超过 OpenDetect 的 `6.50`。因此主表扩展为 29 方法，OpenDetect 仍是冻结的最强外部比较器。

DoHBrw2020 描述性扩展完成 3 场景 x 3 种子共 `9/9`、失败 0。Pairwise 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.975995/0.907012/0.935702/0.301177/0.883466`，平均秩 `2.00`。该结果仅用于展示跨域可迁移性，不反向参与算法选择，不并入七数据集确认性统计。

## 44. 论文可写性与剩余终审

截至北京时间 `2026-07-20 09:20`，论文的方法、协议、数据集、29 方法开发表、D1-D7 机制、融合消融、训练强基线负结果、Router/Tail 失败确认和 DoH 描述性外推均可开始正式撰写。不可定稿的是摘要中的 SOTA 句、最终确认性主表、端到端效率表和结论中的普适领先表述。

胜出算法 `caeos_pairwise` 对 OpenDetect 的独立外部确认已启动，使用未参与选择的种子 `137/139/149`，目标 `306` 个运行，当前 `28/306`、失败 0。综合审计 v10 watcher PID `3615388` 等待该确认完成，并将 29 方法表、最终算法、无泄漏证据和效率边界作为硬门。只有独立外部确认与 v10 终审通过后，才能决定是否使用“全面 SOTA”；若确认未通过，应以“总体竞争性、机制显著、跨域异质”作为论文主结论。

## 45. ExCeL 30 方法表、综合审计 v11 与效率 v2

新增 ExCeL 强后处理基线，按论文固定 `a=10`、`b=5`、`alpha=0.8`，不使用未知或测试标签调参。协议 manifest SHA 为 `87eeefbca798153993a10e852a7e4d0ae55be1ffa88a00435a98c5982e833d4a`，正式矩阵 `102/102`、失败 0；612 项产物、102 项拆分和无泄漏检查全部 PASS。ExCeL 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.721949/0.700213/0.510958/0.519102/0.552586`，四项未知指标平均秩 `11.50`，未超过 OpenDetect 的 `6.50`。主屏幕由 29 方法扩展为 30 方法，但外部确认协议不变。

综合终审升级为 v11，要求 30 方法 schema、ExCeL 完整覆盖、29 方法结果逐项继承、协议和摘要 SHA 链及 OpenDetect 比较器保持不变；远端 `21/21` 测试和 Bash 静态检查通过，新 watcher PID `3892820`。北京时间 `2026-07-20 10:12`，独立外部确认为 `84/306`、失败 0。

效率方面新增 v2 结果为空协议生成器，绑定冻结 Pairwise、完整外部确认、v1 readiness、七个哈希哨兵和训练实现 SHA。它要求训练、校准与真实测试前向分段计时，并以影子运行验证插桩不改变预测和风险数组；相关 v1/v2 回归 `9/9 PASS`。外部确认完成前该协议拒绝冻结，故效率表仍属于待完成证据。

选后污染确认协议已冻结，manifest SHA `83415875d1f26c8f1c948dac65f498110a5f3a6080e2aba4fd4407aa05eea4f4`。哨兵层覆盖 7 数据集 x 3 模态 x 13 个污染强度条件，共 `273` 次；确认层覆盖 102 场景 x 5 污染家族，共 `510` 次。full102 模态由 coverage SHA 决定，污染强度和优雅退化门在结果前固定，测试标签不用于生成或选择。协议与 runner `7/7 PASS`，但按资源门排在外部确认和独占效率测量之后。

## 46. DCC 动态协方差强基线负结果

按 ICML 2025 DCC 公式新增冻结 MLP 后处理基线。协议在结果 0 时固定每套件两个 SHA 场景、残差维数 `min(50,d-1)`、ridge 和特征值数值保护；训练统计只来自 known-training，known-validation 只校准阈值。manifest SHA 为 `b05efdba3aef7373e5fd54f2b9e38ac5fbbe8c834c10ddf7a843618f083e2e20`，代码与协议测试 `8/8 PASS`。

试点 `14/14`、失败 0，全部 SHA、切分和无泄漏检查通过。DCC 的 Known F1/AUROC/AUPR/FPR95/OSCR 为 `0.762301/0.678972/0.438487/0.619925/0.535440`，四指标平均秩 `4.00`；相对 Mahalanobis++ 的有向均值为 `-0.043900`，只有 USTC 套件非负，总体增益、套件稳健性和 Top-2 门均失败。因此停止在发展筛选，不补跑 full102。该结果说明面向图像特征设计的逐测试样本协方差减法不能直接替代流量任务中的类条件、模态条件与尾部风险结构。

北京时间 `2026-07-20 11:01`，独立 OpenDetect 外部确认为 `114/306`、失败 0；综合审计 v11 继续等待其完成。DCC 不改变当前论文结论边界。

## 47. 效率 v2 部署实现与论文边界

新增 Pairwise 与 OpenDetect 可序列化推理 runtime、训练捕获器和成对效率 runner。Pairwise 两个实际选择分支分别在 221/1,946 个样本上达到预测完全一致和风险差 `0`；OpenDetect 的 CPU 跨设备诊断风险差为 `1.621246337890625e-05`，只证明重放路径可用，不替代 GPU 同设备 `1e-12` 正式影子门。协议生成器已扩展为绑定 10 个实现 SHA，推理固定 seed7、训练哨兵固定 seed191，并强制原生设备结果与同 CPU 归一化结果分开报告。

本地效率协议/runner `9/9`、远端 runtime `7/7`、仪器审计 `3/3`，合计远端 `19/19 PASS`。新增门明确拒绝容差为 `2e-5` 的 CPU 跨设备诊断进入正式 runner。机器审计判定 `instrumentation_code_ready=true`，同时保持 `formal_execution_allowed=false`、`efficiency_claim_allowed=false`。北京时间 `2026-07-20 11:56`，外部确认 `149/306`、失败文件和错误日志为 0；正式效率与污染指标均为 0。论文主体已具备写作依据，但确认性 SOTA、效率优势与污染鲁棒性仍必须等待既定链路完成。

## 48. 效率缓存就绪审计

缓存审计远端 `2/2 PASS`。coverage manifest 指向的 seed7 七套件 CSV/sidecar 已全部通过路径和 SHA 校验，冻结全 102 场景重放输入为 `7/7`；fresh timing seed191 缓存为 `0/7`。因此当前允许在外部确认完成后冻结效率 v2 协议，但不允许开始正式计时。必须先在计时区间外生成并校验 7 套件 seed191 缓存，再执行 seed191 七哨兵三次干净进程训练与 seed7 全 102 场景推理；数据准备耗时不得混入候选或比较器指标。

## 49. seed191 缓存自动化部署

新增独立缓存准备器和外部确认等待器。上游完成后首先调用协议冻结器，绑定两侧训练、runtime、capture、benchmark、paired runner 与 creator 共 10 个实现 SHA，并要求冻结时正式指标数为 0；随后准备器绑定 seed191、七套件既有源路径、最大类样本数、配置文件与 CIC-IoT2023 分组支持规则。`confirmation_complete` 缺失时两者均退出，且代码静态门确认缓存阶段不调用训练器、不产生指标。最后重新运行缓存 readiness，只有 7/7 CSV 与 sidecar 完整且 SHA 可记录时才写 `caches_complete`。协议/审计/脚本测试本地与远端 `6/6 PASS`，Bash 语法检查通过；watcher PID `104970` 已部署但仍在等待，不提前消耗资源。

## 50. OpenDetect 同设备影子等价实现

为消除 CPU/GPU 数值路径差异，OpenDetect capture 现在可以在目标设备上用原始分类器执行独立影子前向，runtime 只与同设备影子做 `1e-12` 正式比较；旧 score archive 只输出诊断差异。paired runner 还会校验等价模式字符串，宽容差或 source-score 模式即使 `passes=true` 也失败关闭。真实 CPU 集成 smoke 在 1,946 样本上预测一致、风险差 `0`，而旧 GPU archive 差异保持 `1.621246337890625e-05`。远端共 `22/22 PASS`；该证据证明仪器可执行，不代表全 102 场景效率结论。北京时间 `2026-07-20 12:28`，外部确认为 `161/306`、失败 0。

## 51. ActSub 第36基线与 S&I 忠实性边界

再次复核 [S&I 官方论文](https://openreview.net/forum?id=b1Bae7TKmw&noteId=rSfz7yghOz) 及固定提交 `d8984f0f9325f053e7a7e4b16574842ebab09c34` 后，确认其核心是 36 个逐层切分点、每点两步对抗更新，以及非零梯度支持的二值化聚合。当前 `ConcatMLPClassifier` 只有两个 `Linear + LayerNorm + GELU` 隐藏块，稠密 GELU 梯度几乎处处非零，直接迁移会使支持占用接近常量；只取最终线性头又遗漏逐层更新。因此 S&I 继续标记 `methodology_review_only`，不计入方法数，也不以简化梯度分数冒充忠实复现。

新增第36个零结果候选 `ActSub-SCALE-Fixed`，依据 [ICCV 2025 ActSub 论文](https://openaccess.thecvf.com/content/ICCV2025/html/Zongur_Activation_Subspaces_for_Out-of-Distribution_Detection_ICCV_2025_paper.html) 与官方代码提交 `5b058e723c814fdfd36ab1b73b18227623faa410`。适配冻结 MLP embedding 和分类头：用分类头 SVD 及 known-training embedding 自动确定 balance index，以官方 ResNet 默认的 percentile `95`、lambda `2`、insignificant top-`10` 计算 SCALE energy、投影余弦与 Eq.10 乘积风险；known-validation 只校准已知接纳阈值，不使用 validation OOD、APS、未知或测试标签调参。

核心、协议、汇总及队列测试本地和远端均 `9/9 PASS`，Python/Bash 静态检查通过。14场景 protocol/gate 在正式指标 `0/14` 时冻结，SHA 分别为 `8d1414123a6a730592ae6949342f6f0c5e5cd65b17078ce53c1364edb312ad44`、`3f1eb8036e00a787548acbde88d72467befa48d4461c83cc445f979acb478639`。ActSub watcher PID `1551185` 等待 PRO 完整分析与分支完成；后处理链 PID `1551184` 已把 ActSub 分析及 `branch_complete` 纳入硬依赖。该冻结只证明协议可复现，不能证明 ActSub 有效。

UTC `2026-07-22 04:54:44`，效率 v5 已生成 `100/204` 个正式指标，执行日志为 0 字节，执行器、恢复包装器及上述等待器均存活，未发现非空错误日志。seed195、seed201、CTC 仍按冻结资格链优先于外部基线执行；在它们的开发门、保留种子确认和最终选择完成前，`CAEOS-Pairwise` 仍是唯一已确认 incumbent，不得声称新自有算法胜出或全面 SOTA。

## 52. CARef/CADRef 第37-38候选与 full102 终审闭环

现有覆盖已包含 NCI、ViM、ReAct、DICE、SHE、ASH、NNGuide、LINe、PRO 和 ActSub，但缺少 CVPR 2025 [CADRef](https://openaccess.thecvf.com/content/CVPR2025/html/Ling_CADRef_Robust_Out-of-Distribution_Detection_via_Class-Aware_Decoupled_Relative_Feature_Leveraging_CVPR_2025_paper.html)。本轮固定[官方代码](https://github.com/LingAndZero/CADRef)提交 `121f74b47ebd71644a1c5a6d856880021268c7fa`，新增共享一次冻结 MLP 前向的第37候选 `CARef` 与第38候选 `CADRef-Energy-Fixed`。类中心严格按 known-training 的模型预测类分组；CARef 使用 Eq.6 归一化 L1 相对误差，CADRef 使用官方默认 Energy 和 Eq.10 `Ep/Energy(x)+En/mean_train_Energy`；known-validation 只校准阈值，未知/测试标签不参与拟合或选择。

首版协议在正式结果 `0/14` 时发现只保证 full102 文件完成、没有绑定 full102 聚合分析，已以 SHA `f31b948cd1d1d6f95ba92747b88c11bd8163edc11e00698fd4502b409bd20a38` 留档作废。补入 `102/102` 场景、零失败、公式完整性、非恒定分数、四方法总表、逐套件增益和 canonical SHA 汇总器后重新冻结；当前 protocol/gate SHA 为 `5ba6b77c9eaf42e86dedb4fd605df841941a3845bccde8e4a0d2d65e355b6094`、`d04405319976b63913d8a281486eeb53add2499fd89045a5ee32f737ea4c7be2`。协议绑定 evaluator、scorer、runner、gate creator、pilot/full summarizer 和 orchestration script 共7项实现 SHA。

远端核心、协议、pilot/full 汇总及队列测试 `10/10 PASS`，Python 编译和 Bash 语法通过。CADRef watcher PID `2395520` 等待 ActSub 的 analysis 与 `branch_complete`；后处理链 PID `2395521` 已把 CADRef analysis/branch 及进程阻断模式纳入硬门。当前正式 CADRef 指标仍为 `0/14`，不能增加已完成方法数或形成效果结论。

UTC `2026-07-22 05:42:56`，效率 v5 为 `124/204`、执行日志0字节，执行器和恢复包装器存活。自有算法仍按 `seed195 -> seed201 -> 选择 -> CTC` 优先推进；CARef/CADRef 只扩展外部 SOTA 参照边界，不参与自有算法择优，也不改变 Pairwise incumbent。

## 53. 统一自有算法选择闭环与第四候选决策

失败集中度复核表明，当前三条挑战者已经覆盖不同、可证伪的机制：seed195 检验表示空间尾部几何，seed201 检验反事实冲突响应，CTC 检验证据冲突联合拓扑。此时再叠加一个全局尾部分数会与 LCB/seed195 高度重合，并扩大开发集选择自由度。因此当前不新增第四候选；这是“先完成三条预注册假设的选择与确认”的阶段决策，不是取消自有算法探索。只有三条均失败且失败证据指向新的、非重合机制时，才重新立项第四候选。

队列审计发现原 `mal_tls_self_algorithm_selection` 只在 seed195 与 seed201 之间选择 Mal_TLS 局部组件，旧 `strict_v4_optimal_self_algorithm` 又只覆盖早期 Tail-aware，导致 CTC 即使通过预留种子确认也无法进入最终全局选择。本轮新增分层统一选择器：全局层仅在冻结 pilot 与 reserved confirmation 均通过时允许 CTC 替代 `CAEOS-Pairwise`，否则保持 Pairwise；局部层继承 canonical Mal_TLS 审计所选的 seed195/seed201 组件。禁止依据结果临时集成或重加权。

结果无关协议已在统一决策 `0` 时冻结，SHA 为 `a122636de37c8485bd805b5a475635fc4a37c00f7a768d42eb87a8528b202698`，并绑定 Pairwise 清单、Mal_TLS selection-v2、CTC pilot 协议以及 creator、selector、watcher 实现。即使 CTC 被选为准确性候选，也只产生 `accuracy_selection`，在 CTC 效率、LSNM2024 和 CICDDoS2019 三道门完成前，`deployment_selection_complete` 必须保持 false。

本地与远端统一选择专项测试均 `6/6 PASS`，Python 编译与三个 Bash watcher 语法通过。UTC `2026-07-22 06:17:24`，v5 已生成 `140/204` 个正式效率指标，主执行器和恢复包装器存活；统一选择、WDiscOOD 和后续声明链 watcher PID 分别为 `3218896/3218897/3218898`，CADRef watcher PID `2395520`。统一决策与三条自有候选正式指标仍均为0，因此当前只能写“探索协议与选择闭环已完成、实验执行中”，不能写新自有算法优于 Pairwise或已实现全面 SOTA。

## 54. Fisher-Rao 第39-41候选与信息几何压力测试

基线缺口复核后新增 ICLR 2026 [Fisher-Rao Sensitivity](https://iclr.cc/virtual/2026/poster/10010515) family。它与现有尾部距离、激活裁剪和相对特征误差不同，直接检验冻结分类器最后一层参数流形的局部信息几何敏感性。单次冻结 MLP 前向共享三个候选：第39个 `FIM-Standard` 使用 Eq.7 `||f||^2(1-||p||^2)`；第40个 `FIM-Tensor` 使用 Eq.9 `U*M`；第41个 `FIM-Additive` 使用 Eq.13，并按 Eq.14-15 在 known-training 上解析平衡方差。特征子空间由 LDA 后正交化得到，概率子空间由 softmax PCA 得到；投影幅值系数符号固定为负、残差系数为正。known-validation 只校准接纳阈值，未知和测试标签不参与拟合或系数选择。

本地与远端核心、协议和队列测试均 `9/9 PASS`，Python 编译及 Bash 语法通过。真实 CIC-IoT2023/Backdoor-Malware 临时冒烟中，三个分数均有限且非恒定；Additive 的 AUROC/FPR95 为 `0.831883/0.373553`。该数值位于 `/tmp`，只证明实现可执行，不属于正式试点，不进入论文比较表。

14场景 protocol/gate 在正式结果 `0/14` 时冻结，SHA 分别为 `fd6756f66d519163c11e9609e075b67f4ce704e49618e60e50a88c08e07c235e`、`14fbc86d20035a566c8f374280bb5d98f83e0a7b99bc593b2be1324c9024b38b`。任一候选通过完整性、Known F1、公式、非恒定分数、Top-2、指标广度、总体增益和套件稳健性门后，才共享扩展 full102 并生成 canonical 聚合分析；否则保留负结果并停止。

Fisher-Rao watcher PID `336594` 串行等待 CADRef，更新后的后处理终审 PID `336592` 已把其 `analysis.json` 与 `branch_complete` 纳入硬依赖。UTC `2026-07-22 06:49:15`，效率 v5 为 `157/204`，Fisher-Rao 正式结果仍为0。该外部基线只收紧 SOTA 参照边界，不参与 seed195/seed201/CTC 的自有算法选择；自有算法探索仍是主线，Pairwise 仍是唯一已确认 incumbent。

## 55. post-30 综合审计 v12 与自有算法证据一致性

终审链复核发现旧 `strict_v4_comprehensive_sota_audit_v11` 在 ExCeL 第30方法阶段已经完成，后续第31-41候选均不在审计输入中；旧 post-chain 还遗漏 WDiscOOD/VOS 两项依赖。因此即使后续候选完成，旧 final readiness 也可能继续消费过时的30方法结论。v11 当前明确给出 `strict_v4_confirmed_external_sota_allowed=false`，且 Pairwise 在开发比较中仍有 FPR95 维度落后 Mahalanobis++；它不能证明全面 SOTA。

本轮新增结果前冻结的 post-30 协议，覆盖 WDiscOOD、VOS、GROOD、GSC、PRO、ActSub、CARef/CADRef 和 Fisher-Rao 共8个家族、11个新增候选。协议在各家族正式 analysis/metrics 均为0时冻结；readiness v3、CTC v2、统一选择 v2 与第四候选失败关闭分支接入后重新冻结的当前 manifest SHA 为 `552855d82c8c0568f9db69c95b1eff6963f5232fbf5b9411ac9aea891b90b2e9`。v12 只有在每个14场景 pilot 完成、analysis 绑定冻结 protocol/gate SHA，且所有阳性分支同时具备102场景、零失败、完整聚合分析与完成标志时，才设置 `post30_baseline_coverage_complete=true`；阳性但缺 full102 必须失败关闭。专项测试本地与远端均通过，Python 编译及 Bash 语法通过。

最终论文 readiness 已升级为 v2，只接受 canonical `strict_v4_comprehensive_sota_audit_v12` 且 post-30 覆盖完整。统一选择若保留 `caeos_pairwise`，可继续使用既有 Pairwise 腐化协议；若 CTC 胜出，旧 Pairwise 腐化链会明确退出，必须为 CTC 另行冻结腐化、外部比较器和效率证据，禁止算法与证据错配。v12 watcher PID `2048375`、新版 post-chain PID `2048376` 已启动，当前分别等待18个先决文件和 v12 审计。UTC `2026-07-22 08:13:47`，效率 v5 已有 `192/204` 个 `efficiency_metrics.json`，seed195、seed201、CTC、统一决策及8个 post-30 家族正式分析仍为0。当前结论继续保持：自有算法探索必要，但 Pairwise 仍是唯一 incumbent；全面 SOTA 尚未建立。

## 56. 效率 v5 正式负方向与 seed195 自有候选决策

效率 v5 已完成102场景双口径共 `204/204` 个正式块，summary SHA 为 `02ae15ed6991377731fcede1cca185b3f324054609ff7de84ac17b1809b4a784`。等价容差、输入一致、训练21块、推理102场景及双口径隔离均 PASS；这里的 `formal_efficiency_claim_allowed=true` 只表示允许报告同硬件测量，不表示效率领先。原始 Pairwise 相对 OpenDetect 的 native P50 时延比95%区间在 batch 1/64/512 分别为 `[177.375,182.719]`、`[305.335,317.318]`、`[523.042,583.076]`，吞吐比区间仅为 `[0.00554,0.00565]`、`[0.00316,0.00337]`、`[0.00185,0.00199]`。训练总时长比区间 `[0.354,0.697]` 有利，但部署产物体积和峰值 RSS 比区间分别为 `[46.435,97.266]`、`[1.704,2.805]`，因此原实现不具备效率 SOTA。

终审发现旧 readiness 即使等待 v6 间接完成，仍只消费 v5 原实现。现升级为 v3：推理优势改为验证 v6 `optimized/OpenDetect` 在 native P50/P95/P99 上界 `<=1`、吞吐下界 `>=1`；同时保留 v5 的训练总时长、部署产物体积和 RSS 硬门，并单列204块等价与优化版相对原版2倍目标。任一失败均不能称多维全面 SOTA。专项测试本地与远端均 `5/5 PASS`，post-chain PID `2662074` 已明确等待 v5、v6、统一选择、8家族和 v12。

seed195 几何保持适配器随后完成12份指标、6个配对家族，失败0。AUROC/AUPR/FPR95/OSCR 平均有向增益为 `+0.005800/+0.023995/+0.001332/+0.007851`，Known Macro-F1 平均增益 `+0.005605`；但只有 `3/6` 家族四指标全不回退，最差场景指标为 `-0.030794`，ECE 平均增益为 `-0.003055`。冻结六门中场景非回退数、最差指标和 ECE 三门失败，决策为 `retain_caeos_pairwise_and_reject_geometry_adapter`。确认分支已写 `not_required` 和 `branch_complete`，不消耗 `197/199/211`；seed201 反事实冲突门已自动启动。

## 57. seed201、CTC 负决策与选择性拓扑第四候选

seed201 反事实冲突门完成12份指标、6个配对家族且失败0。反事实机制确实响应：log attenuation 增益 `+0.867360`、已知验证反事实不确定性增益 `+0.355900`、margin满足率 `0.775050`，Known F1不变，ECE有向增益 `+0.018530`；但实际开放集 AUROC/AUPR/FPR95/OSCR 有向增益为 `-0.004037/-0.011995/-0.013175/-0.003495`，仅1/6家族四指标全不回退，最差指标 `-0.045531`。因此冻结决策为 `retain_caeos_pairwise_and_reject_counterfactual_conflict_gate`，确认分支 `not_required`。Mal_TLS 自有选择审计 SHA `be420fd238e5914640954ec7add19fe14b455b6d721c46870d91f18706a91e4d`，不增加局部组件。

CTC 首次执行在4份部分指标后因已知验证类样本不足4个失败关闭。纠偏只修改 known-only 拆分可行性：单例类仅进入拟合集，支持数不少于2的类至少各留1个拟合和校准样本；旧4份指标值未读取用于改门或选参，旧实现、协议、失败日志和部分产物 SHA 均归档绑定。v2 协议在新结果0时重新冻结为 `04d9b4554c6b76bc40466aea2befe75653e1fb7cba3d19ff894bbb7d786205c9`，随后完成14/14、失败0。

CTC 的 AUROC/AUPR/FPR95/OSCR 总体有向增益为 `+0.015411/+0.006684/+0.160226/+0.079744`，10/14场景四指标均值为正；但只有2/7套件四指标全不回退，最差套件指标为 CIC-ToN-IoT FPR95 `-0.096384`，故拒绝固定 `0.75 Pairwise + 0.25 CTC` 全局混合。统一自有算法选择分析 SHA `2bae7f4a790e39a2499a7063c99ea31a2cb6eae84a43a14b293bb28c9ac76306`，当前选择 `caeos_pairwise`，Mal_TLS组件为空；部署选择继续等待效率和外部数据门。

三条预注册挑战者至此均已失败，但 CTC 的四项总体增益和10/14场景正信号揭示了新的、非重合错误归因：联合拓扑信号有效，固定全局注入造成套件异质回退。因此开放第四路线 `CAEOS Selective Topology Uplift`，不再训练编码器或新增全局混合权重。候选只在 known-validation 联合拓扑风险超过 q95 时执行 `r'=r+0.25(1-r)clip((t-q95)/(1-q95),0,1)`，逐样本保证不降低 Pairwise 风险，预测完全不变。

为避免复用 CTC 开发结果，新的7套件14场景全部从剩余88场景中按固定盐和场景名称 SHA 选择，每套件2个，与原 CTC 14场景零重叠，选择不读取任何指标。协议绑定 CTC v2 负分析、源证据 SHA、alpha `0.25`、激活 q95、拆分种子 `229` 和原严格套件稳定门；在正式结果 `0/14` 时冻结，canonical SHA 为 `d667ec704281a73651278c6ff9c08a14ef7fabf4239e2eea47e291ebb7d5bbee`。服务器编译、Bash语法、风险单调性、场景不重叠和 canonical 校验均通过。

v6 watcher 此前把自身命令误计为活动实验，空闲样本始终非0；已精确排除 watcher 自身并重启。当前 v6 已正式生成 `18/204` 个三方块、错误0。第四候选 pilot/confirmation/branch watcher PID 为 `3085430/3769368/3920585`；确认 watcher 只在 pilot 阳性后冻结 `233/239/241 × 102=306` 运行协议，重新训练 Pairwise 参考，并以场景为推断单位执行10,000次bootstrap、四指标Wilcoxon+Holm和逐套件非负门。branch watcher 只在阴性 pilot 或完整确认后生成 canonical `branch_decision`。WDiscOOD、v12 与 post-chain watcher PID `3425969/3425970/3425971` 均等待该完整分支；第四候选若确认阳性但旧统一选择未切换，终审会失败关闭。这保持“先完成必要自有探索，再扩展外部基线”的资源顺序，同时不把第四候选的协议就绪误写为效果成立。

## 58. v6 负方向预警与张量化 v7 预检

自有算法探索继续保留，但准确性创新与部署实现分轨审计。`CAEOS Selective Topology Uplift` 仍是第四条准确性候选，必须完成冻结14场景及条件306次确认；张量化 v7 只替换冻结 Pairwise 中五个 sklearn 森林的预测执行器，不改变分类器、风险公式、阈值或自有算法身份。二者不能相互替代，也不能用工程加速结果证明检测效果创新。

在 v6 前22/204个三方块上做了不参与调参的只读方向诊断。优化版相对原 Pairwise 的 P50 约为 `0.5408-0.6368`、P99约为 `0.5271-0.7151`、吞吐约为 `1.5492-1.8245`，方向上接近但尚未达到预注册的2倍内部目标；相对同设备 OpenDetect，P50仍约为 `37.33-310.56` 倍、P99约为 `26.04-285.62` 倍，吞吐仅约为 `0.00328-0.02447`。这是未完成快照的诊断，不是正式204场景统计；v6继续运行以形成可报告的正式负结果或最终结论。本轮只读复核时 v6 为 `34/204`、错误0。

根因审计表明 demand-driven v6 仍执行全局 RandomForest、全局 ExtraTrees、三个逐模态 ExtraTrees及逐模态KNN，而 OpenDetect只做小型神经网络前向。服务器现有 PyTorch `2.1.2+cu121`、CUDA可用且为 RTX A6000；不在 v6 期间安装新依赖或修改环境。v7 将已拟合森林展平为只读 tensor traversal，保持 sklearn float32输入遍历与float64阈值/叶概率语义。森林单元测试覆盖 RandomForest、ExtraTrees、维度拒绝，概率最大误差不超过 `1e-12`。

v7采用两阶段失败关闭门，不直接运行full204。七个哨兵由固定盐在v6七套件中各选一个；全输入 prediction 必须逐项一致，probability/risk最大差必须 `<=1e-12`。原生CUDA下固定batch `1/64/512`、3次warmup、10次交替计时；每个batch的七套件中位P99比必须 `<=2.0`、吞吐比必须 `>=0.5`，森林tensor与峰值GPU内存均不得超过8 GiB。仅全部通过才允许在任何完整结果前另冻full204 v7协议；失败则拒绝v7并保留v6系统权衡。预检永远不直接支持正式效率主张。

当前预检包装器为逐项等价审计而保留原 `PairwiseRuntime`，所以它只检验时延、吞吐和GPU内存假设，不改善部署产物体积。已预备独立 compact 状态和原子构建器：仅保存五个森林tensor、融合标量、known-only tail参考及当前端点实际需要的距离/KNN支持，构建前后各做一次完整等价，并记录源/紧凑产物SHA、体积比、构建和重载时间。构建器尚未加载任何正式捕获，也未绑定当前预检协议。即使七哨兵通过，仍必须用该构建器生成不携带原sklearn森林的紧凑状态，并把产物体积、主机RSS与数值等价重新绑定到full204协议；未完成该步骤不得认为v7解决了v5的体积劣势。

条件式 full204 链已预备，但当前不得生成协议。它只有在 preflight analysis 绑定当前SHA、`passes=true`、decision为 `freeze_full204_v7_protocol` 且 `branch_complete` 存在时才放行；同时要求 compact build 和正式效率块均为0，并在冻结时哈希102场景的候选、原生OpenDetect、CPU OpenDetect三组runtime/input/equivalence捕获。随后每个场景先在独立进程原子构建compact，再以新进程分别执行原生/CPU两方法交替计时，最终汇总102场景bootstrap区间。正式门不继承预检的P99 `<=2`、吞吐 `>=0.5` 宽松条件，而要求原生三个batch的P50/P95/P99比bootstrap上界均 `<=1`、吞吐比下界 `>=1`、compact/OpenDetect与compact/original体积比上界均 `<=1`；CPU结果必须完整但只作次级口径。配对进程RSS/GPU峰值只作资源诊断，综合效率结论仍必须合并v5训练时长、体积和RSS证据。

full block、matrix、summarizer和条件watcher均已实现；204块合成通过、延迟/吞吐/体积负例、缺记录、交替顺序、实现SHA和队列依赖共同测试通过。预检阴性时full watcher只写 `not_required + branch_complete`，阳性时才冻结和执行；WDiscOOD新增等待full分支，防止阳性full矩阵与基线竞争机器。最新full watcher PID `2625896`、WDiscOOD PID `2055945`，锁均存在；full协议、compact正式产物和full结果仍为0。

首版预检协议在 `0/7` 结果时冻结为 `081fe703f4d249447f30f712c427aa8e8c7d87dca17401c0e6a33db275d72bd4`。结果前轻量审计发现七哨兵中的 CIC-ToN-IoT/Backdoor 使用 `pseudo_unknown_learned_blend`，其冻结权重包含 `uncertainty/inverse_belief/inverse_margin` 等12个分量，而首版wrapper未显式生成前三项，会造成实现缺项伪阴性。旧协议已留档为 `protocol_manifest.superseded-missing-learned-components-20260722.json`，没有执行或读取任何v7指标。

补齐与现有 demand-driven runtime 相同的三个概率分量后，reference和learned-blend两条端点均通过完整 prediction/probability/risk 等价测试；紧凑状态还通过不保留原runtime/sklearn森林、未用支持裁剪、joblib往返和SHA绑定原子构建门。当前协议仍在 `0/7` 重新冻结，canonical SHA为 `1fc1a515b1d6f0fde24ff37463e1095a57b87ebaa1bb3a042d030843ecf041c6`，七套件与全部性能门不变，wrapper文件SHA复算一致。本地森林、两端点、compact、构建器、preflight/full协议、204块汇总、readiness v4和队列测试合计 `30/30 PASS`；服务器Python编译和Bash等待器语法检查通过，未在v6正式计时期间执行真实远端模型测试。v7 watcher PID `836208` 继续等待 `v6 branch_complete + Selective branch_complete + 连续5次独占空闲`，full/WDiscOOD/post-chain PID为 `2625896/2055945/2625897`。本轮只读复核时v6为 `60/204`、零字节结果0、错误标记0，第61块正在运行。

自有算法选择与效率归因现已硬绑定。full v7 协议冻结时必须同时绑定综合准确率决策和 Selective 分支决策的 SHA；若 Selective Topology 最终具备确认资格或成为统一选择，Pairwise-v7 watcher只生成 `selected_algorithm_runtime_required + branch_complete`，不得把Pairwise效率证据归给新候选。若Pairwise仍为最终算法，v7正式门全部通过才整套选择v7；任何正式门失败均整套回退v6，禁止在v6/v7之间逐指标拼接。readiness v4按该条件分支消费证据，并继续保留v5训练时长和峰值主机RSS门；post-chain PID `2625897` 已等待full分支后才启动污染与终审。因此自有算法探索不会被工程加速替代，也不会被错误实现的效率数据提前锁定。

论文边界因此不变：Pairwise仍是准确性 incumbent；Selective Topology效果未知；v6完整效率结论未知但早期方向明显不利；v7仅为冻结待检验假设。当前证据可以支撑方法、负结果、实验设计和效率瓶颈分析的撰写，不能支撑“全面SOTA”“效率领先”或“v7已解决部署问题”。

## 59. post-30 基线审计协议的 readiness v4 绑定修订

对8家族11候选的活动链做远端逐项核验：WDiscOOD、VOS、GROOD、GSC、PRO-MSP-fixed、ActSub-scale-fixed、CARE/CADRef和Fisher-Rao八个 watcher 均存活；冻结目录覆盖11个候选，阳性 pilot 均要求102场景正式聚合，八家族正式 analysis 当前全部为0。该事实证明的是队列和协议覆盖，不是新增基线已经完成或胜出。

核验同时发现 post-30 v12 协议仍绑定 readiness v3 的旧实现 SHA，而终审代码已升级为 readiness v4。因为八家族正式结果和 v12 审计结果均为0，已在不读取任何指标的前提下执行结果前修订：旧协议 SHA `552855d82c8c0568f9db69c95b1eff6963f5232fbf5b9411ac9aea891b90b2e9` 留档为 `protocol_manifest.superseded-readiness-v3-20260722.json`；新协议显式记录旧 manifest/file SHA、修订原因和修订前 analysis 数0，canonical SHA为 `f35299dc7665c0228c1e49b39e94925f3964b3383b08bd652c0270f980a4cc6f`。

新审计在运行时不再只验证自身 auditor，而是同时验证 auditor、v12 watcher 和 readiness v4 三个文件 SHA；非Pairwise入选时的外部确认缺口原因也改为按实际算法身份生成，避免把 Selective 误写成 CTC。三个远端实际 SHA 与协议逐项一致，Python编译、Bash语法和相关本地/远端测试通过；张量化、readiness与post-30完整相关回归为 `31/31 PASS`。v12 watcher 已用新脚本重启为 PID `3184988`，锁存在且 audit 仍为0。同期 v6 为 `66/204`、错误标记0；Selective pilot/confirmation仍为0，资源顺序未改变。

## 60. LSNM2024/CICDDoS2019 从“准备数据”补齐到“形成论文证据”

对GPU数据扩展链的活动状态复核表明，全量准入 watcher PID `639026` 与标准化准备 watcher PID `1174214` 均正常等待，前者依赖 post-chain，后者依赖准入通过；不存在等待进程丢失。真正缺口是仓库此前只实现了全量扫描、三种子确定性抽样和sidecar，没有任何消费准备产物的冻结评测矩阵、统计汇总或论文就绪更新，因此即使数据生成也不会自动增加论文数据集证据。

现已补齐两阶段失败关闭链。第一阶段在准备结果和评测指标均为0时冻结设计：LSNM2024与CICDDoS2019固定种子 `223/227/229`，对每个保留的非良性攻击家族做逐家族留一未知，双向五元组/会话指纹分组拆分；候选只从canonical post-30准确率审计读取最终自有算法，主比较器固定OpenDetect。Pairwise参数、Selective q95/alpha参数、OpenDetect训练参数和四指标/Known F1统计门均在设计中固定，设计 canonical SHA为 `cdca16e7020ad0e5c4fddb8c4121b3eb703f1a3c0a4b9608bc956b558e8fd0d6`。

第二阶段只在准入及准备完成后读取sidecar标签和组数，要求每个标签至少3个非重叠组、CSV/sidecar/manifest SHA一致，再在正式结果0时生成执行协议。runner随后串行执行入选自有算法与OpenDetect；若入选Selective，先生成同参数Pairwise证据包，再用known-only copula/q95单向抬升，不能复用Pairwise指标。汇总以“数据集×攻击家族”为推断块，先跨3种子聚合，再做10,000次bootstrap、四指标Wilcoxon+Holm、逐数据集非退化和Known F1非劣门；CICDDoS2019声明被限制为DDoS家族外推。最后新增扩展readiness，只有原7数据集确认、post-30覆盖和两个新增数据集确认同时通过才升级准确率声明，且不替代效率与污染门。

远端Python编译、Bash语法和5项新链测试通过；张量化、post-30、readiness与外部数据链完整相关回归为 `36/36 PASS`。external evaluation watcher PID `502086` 已锁定等待，不在v6期间训练；执行协议、正式指标、summary和扩展readiness当前均为0。最新只读快照v6为 `79/204`、错误标记0。因此目前只能声明新增数据评测链已冻结就绪，不能把LSNM2024/CICDDoS2019计入已完成SOTA数据集数量。

## 61. 自有算法探索保留与历史训练器语义回放门

自有算法探索仍是论文创新主线，不能用继续增加外部基线代替。当前第四候选 `CAEOS Selective Topology Uplift` 保持冻结的独立14场景 pilot、条件306次确认和失败关闭分支；在这些结果完成前，`CAEOS-Pairwise` 仍是唯一已确认 incumbent。张量化 v7 只负责部署执行器优化，不能替代准确性探索，也不能作为 Selective Topology 的效果证据。

对新增外部数据评测链继续做实现身份审计时，发现历史 Pairwise 候选清单绑定的训练器 SHA 为 `3b8650655c56c37d08be1085a0e3df99de1bd6ec879678d7a768cd211ef4b1f2`，当前活动训练器 SHA 为 `abf613b43bdab9dd12764cb0b3359ba84fed0d4e9e29e686b86e9823dca458f2`。服务器现有项目根中未找到同名的历史训练器副本，因此不能仅凭当前代码通过单元测试就假定它与历史 Pairwise 证据语义等价。

已增加结果前的两哨兵语义回放门，协议 SHA 为 `e57d72e160f701c452bba68c7c305b485f4fda7c2ebd20f3f40849b96c9fd6a9`。两个互补哨兵固定为 CIC-ToN-IoT/MITM/seed127 的 `pseudo_unknown_learned_blend` 和 CIC-IoT2023/DDoS-ACK-Fragmentation/seed127 的 `cauchy_modality_support_union`。回放必须同时满足：选择风险名称、拆分指纹、测试预测、验证/测试标签逐项一致，报告与验证/测试风险最大绝对差均不超过 `1e-12`。任一哨兵失败都关闭 LSNM2024/CICDDoS2019 正式评测，不允许把新训练结果与历史确认结果混合。

外部数据设计协议经历两次结果前留档：初版 `cdca16e7020ad0e5c4fddb8c4121b3eb703f1a3c0a4b9608bc956b558e8fd0d6` 因未完整绑定实现身份作废；第二版 `3aa7a10675ccd0091007b9d224f83972e3044337fb2d35b5bb5939c48b027f78` 因尚未接入语义回放门作废。当前权威设计 SHA 为 `375fe0b1e1476daa1af6cb07cb448dea8efcaa09d3447f67cd82fea4f5f1f573`，绑定历史候选清单、Selective协议、post-30协议、回放协议以及评测实现文件。只有回放 summary 明确 PASS 后，执行器才允许在正式指标仍为0时冻结具体外部评测协议。

本地与远端完整相关回归均为 `38/38 PASS`，Python编译与Bash语法检查通过；这只证明协议和失败关闭实现就绪。UTC `2026-07-22 13:29` 的权威状态为：语义回放 `0/2`，外部正式指标 `0`，回放summary、回放完成标志和外部执行协议均不存在；新版 watcher PID `1067767` 正等待准备、post-30审计与readiness v4。同期 v6 为 `92/204`、错误0。论文当前可以写自有算法动机、三条负结果、第四候选设计、训练器漂移风险和外部验证协议，但不能写第四候选有效、两个新增数据集确认成功、当前训练器已复现历史Pairwise或已实现全面SOTA。

## 62. post-30 阳性 full102 闭环审计与三家族纠偏

对8家族阳性 pilot 分支逐一做终点证据审计后发现：post-30 v12 虽然会对阳性候选强制检查102份正式指标和聚合分析，但旧 ActSub 分支只运行 full102 并写标志，没有生成 `full_analysis.json`；旧 GSC 完全没有 full102 分支；旧 PRO 虽运行 full102，同样没有聚合分析。若任一家族 pilot 阳性，旧链会在终审阶段失败关闭，无法形成可用于论文的完整 SOTA 对比证据。

上述三家族均在正式结果 `0/14`、full102结果0时纠偏。ActSub 新增独立 full102 汇总器，校验102场景、零失败、拆分一致、公式完整性、非恒定分数、四方法总表、逐套件增益和 canonical SHA；protocol/gate 重冻为 `e06861d598dca122fefd5bc7e7483eafde9dba1c9fc9d180de36188c92a39690` / `26be61c28171271089cabe98bf77ef0a5d221030abf593f28b7f627c779359ae`。GSC 新增条件 full102 执行与聚合，PRO 在既有 full102 后补聚合；两者 protocol/gate 分别重冻为 `2cd8f8b2d7fc8a40072e7af78eb865274934336a976c45321a8684a87136704b` / `4e68e4c68d2410bd6f7d60f92e5e5ccc07bf3d5b78866d32207126df11b93886`，以及 `8c00322ea825ca8de58d88eae37872098bf8ceca6103c2d8567be04d27ad132f` / `7f58166f4ad2645049980a35d1d1261efb1736f9c38f5113f1131726653a28fc`。旧协议和门均以 superseded 文件保留。

ActSub 本地专项 `6/6`、远端完整专项 `10/10` 通过；GSC/PRO 新增 full102 聚合与队列测试本地/远端 `5/5` 通过。post-30 v12 随传递绑定两次结果前修订，当前权威 SHA 为 `4a8031038e3d0a951251a9bf2e6bd88537ff430a8a1057d12b8a406c5191daca`；外部数据设计同步更新为 `7b0c066f24d50e15360b2331acbb0459fdb30bedd1d3cca68c460beee15b9405`，并显式绑定当前 v12。组合回归 `23/23 PASS`，四层 canonical 与交叉绑定检查通过。

该审计还确认 WDiscOOD、VOS 和 GROOD 的活动脚本仍只实现 pilot，尚未具备与 v12 要求相匹配的阳性 full102 执行和聚合闭环；它们是下一批必须修复的已知缺口，不能因 watcher 存活而视为已完成。RAS 2026 是与当前GELU表格MLP兼容的超参数自由后处理候选，但目前仅完成论文适配性审查，尚未冻结协议或计入方法数；FEVER-OOD和DEBO需改变训练目标/结构，不能简化成后处理分数冒充忠实复现。

UTC `2026-07-22 14:32`，V6 为 `121/204`、错误0，ActSub/GSC/PRO正式指标仍均为0，v12审计和外部正式指标仍为0；相关 watcher 全部存活。自有算法探索顺序不变：先完成 V6，再执行 Selective Topology pilot/条件确认和 v7效率分支，之后才串行外部家族。当前仍不能声明全面SOTA或新增三家族效果结论。

## 63. WDiscOOD、VOS、GROOD 阳性 full102 闭环与八家族终点契约

继续按 post-30 v12 的终点契约审计剩余三家族后，确认其旧活动脚本都只能完成14场景 pilot：WDiscOOD 和 VOS 没有独立的102场景源注册协议、正式执行与聚合；GROOD 虽然矩阵执行器支持 full 模式，但旧编排未调用它。首次补齐 GROOD 后又发现其指标和聚合都写入 `results` 且文件名为 `full_analysis.json`，与 v12 冻结的“指标位于 `runs`、聚合位于 `results/.../analysis.json`”契约不一致。该路径问题在结果仍为0时再次修正，避免阳性 pilot 后出现假完成。

现在三条分支均遵循同一失败关闭顺序：pilot 汇总先产生冻结决策；阴性写 `full102_not_required.json`；阳性先冻结独立 full102 协议，再把102份正式指标写入 `runs`、把 canonical 聚合写入 `results`，最后写 `full_complete`。WDiscOOD/VOS 的 pilot 完成标志被延后到条件 full102 分支结束之后，防止 v12 watcher 在正式矩阵尚未完成时抢先审计。WDiscOOD 正式聚合比较 `wdiscood / mlp_mahalanobis / opendetect`；VOS 比较 `vos_energy / mlp_energy / opendetect`；GROOD 比较 `grood / mlp_energy / opendetect`，均校验102场景、零失败、拆分/源SHA、无未知标签拟合和四项有向指标。

三套 pilot 协议均在正式指标为0时重冻并绑定 full102 生成器、执行器、汇总器和编排 SHA：WDiscOOD 为 `3c78dec4d9f0446428d770538eee3373ad2f9edcb9f4e57d669e2598e9c32322`；VOS protocol/gate 为 `86f6514e9635c73c1b5e17b66c3505f4124ff3a180d9001ee59e0b0d51124142` / `318ee0bcca60dd77003403dc8e6ba94df77f5947f1170f0ce055311f8df4b209`；GROOD protocol/gate 为 `f5b2ccec5b9e16306a0e9de912b094dff38e41de9a5e736b69fd63c04cdb0bfb` / `54de31071565bc6d9d8caf96871992d654d8a56e04e090af309caf6f0cef90f9`。使用真实冻结 coverage 和源文件做了不执行指标的构建预演，WDiscOOD 与 VOS 均得到 `102/102` 源注册且 canonical 校验通过。

新增及既有专项远端回归为 `15/15 PASS`，post-30 与外部数据链审计级回归为 `20/20 PASS`，其中新增合成终点测试直接证明 WDiscOOD、VOS、GROOD 的阳性102指标、聚合与marker组合可被最终 `audit_family` 接受；Python编译、Bash语法、活动实现SHA和三层交叉绑定均通过。post-30 v12 随后在零家族分析时修订为 `7cdad1663d334ad7223464a041c502554e2679d9096100ba6eceaef1ffd30b10`，外部数据设计同步修订为 `7215d89e58b1fb3769e57b0ea9f27e2772720558a90a2a39eb5b504690efa05f`；前者逐项绑定当前 WDiscOOD、VOS、GROOD 协议，后者绑定当前 v12。

UTC `2026-07-22 16:23` 的只读快照为：V6 `175/204`、非空错误日志0；WDiscOOD/VOS/GROOD/GSC/PRO/ActSub 的 pilot 与 full 正式指标仍均为0，Selective pilot、v12审计和外部正式指标也均为0，相关 watcher 存活。八家族“阳性后可完成 full102”的结构性缺口现已关闭，但这不等于八家族已完成、更不等于其效果胜出。自有算法探索仍按 `Pairwise incumbent -> Selective Topology 独立 pilot -> 条件保留种子确认` 推进；RAS仍只是待冻结候选。全面SOTA、效率领先和新增数据集外部确认目前均未成立。

## 64. RAS 强基线冻结与自有算法探索分轨

自有算法探索继续作为论文创新主线，不能用增加外部基线替代。当前准确性身份仍是 `CAEOS-Pairwise incumbent -> CAEOS Selective Topology Uplift 独立14场景 pilot -> 阳性后 233/239/241 x 102 条件确认`；RAS 只进入强基线目录，不参与自有算法身份选择，也不能用其结果证明证据冲突机制有效。

RAS 按论文 Eq.7/Eq.8 和官方实现 commit `313d8e09d4e7d513e66fca707adfc2fcd6ecbf08` 做忠实表格 MLP 适配：只用已知训练 embedding 的逐样本升序排序均值形成固定 rank profile，再按每个查询的原激活秩把 profile 散射回原坐标，最后用替换后 logits 的 `logsumexp` 能量评分。官方后处理器的类别预测也来自替换后 logits，因此本实现没有沿用原 MLP 预测冒充忠实复现，而是额外冻结 Known Macro-F1 和预测一致性门；stable mergesort 仅作为并列值的确定性实现策略，不引入 OOD 超参数搜索。

14场景 pilot 由盐 `ras-eccv2026` 在七套件各确定性选择2个场景，选择不读取指标。扩展 full102 必须同时满足：14/14且失败0、三方拆分一致、公式与非恒定分数完整、RAS 相对 MLP Energy 的 Known F1 平均差不低于 `-0.02` 且最差不低于 `-0.10`、平均预测一致性不低于 `0.95`、三方法平均未知指标排名不高于2、四指标至少3项正增益且总体均值为正、至少5/7套件非负且最差套件不低于 `-0.03`。该门只分配开发计算预算；即使阳性，仍须完成102场景正式聚合后才能进入 post-30 审计。

远端 RAS protocol/gate 在正式指标 `0/14` 时冻结为 `c72856ad408c3688ac2a9c63081eb70b38f12c610e69dd60ee13f68392d055f1` / `2c279875d5a7c83cb4baf940fc0c2d6f3943c569b90934e4db1049a833421426`。专项、统一 full102 汇总和 post-30 契约远端测试合计 `19/19 PASS`，Python编译与三个 Bash 脚本语法通过。RAS watcher PID `1105387` 固定等待 Fisher-Rao `branch_complete`，不与当前效率或前序基线竞争资源。

post-30 v12 已在全部九家族正式 analysis 为0时从 `7cdad1663d334ad7223464a041c502554e2679d9096100ba6eceaef1ffd30b10` 结果前修订为 `c4d8df972ccb1242d55587421e3a2da4901a92289b9be3f99a58ec1a0170fc77`，目录口径为9家族、12个post-30候选，即连同原30方法共42方法。外部数据设计同步从 `7215d89e58b1fb3769e57b0ea9f27e2772720558a90a2a39eb5b504690efa05f` 修订为 `123a44fd417cd62ef96c95af5f65617bdcbfc188107b681af65ebd831958b9a0`，并绑定新版v12；两次修订前正式指标均为0。v12 watcher 已重启为 PID `1105386`，状态日志明确等待全部九家族。

UTC `2026-07-22 16:58` 的只读快照为：V6 `192/204`、`error.log/stderr.log/failure.json` 均为0，尚无 `branch_complete`；Selective、RAS、v12审计和外部正式指标仍为0。当前新增的是可审计强基线和完成链，不是效果结论。全面SOTA、RAS胜出、Selective有效、效率领先及两个新增数据集确认均仍未成立。

## 65. V6 正式效率负结果与 Selective Topology 第四候选终态

V6 已在 UTC `2026-07-22 17:21:50` 完成 `102场景 x native/CPU = 204/204` 三方块，失败0，204个全输入 prediction/probability/risk 等价门和204个产物不增门全部通过。正式 summary schema 为 `strict_v4_optimized_efficiency_summary_v1`，canonical SHA `d31c8e6929cf7756d9b8d4f19cf1512de0a5038b074168cfb2b5d4e99856ee1d`。

V6 相对原 Pairwise 确有工程改善，但没有达到冻结的2倍内部目标：batch `1/64/512` 的 P50 中位比分别为 `0.6469/0.6453/0.6072`，P99为 `0.6862/0.6263/0.5841`，吞吐倍数为 `1.5336/1.5563/1.6426`，六个2倍检查为 `0/6 PASS`。更关键的是，相对同设备原生 OpenDetect，P50 中位比仍为 `94.37/180.34/281.66`，P99为 `83.10/140.86/244.26`，吞吐比仅 `0.01049/0.00581/0.00363`。因此 V6 的正式结论是“严格等价且较原实现更快，但远慢于外部比较器”，不能声明推理效率 SOTA。

V6 分支完成后，Selective Topology 首次实际执行在 `12/14` 时因 USTC-TFC2016 的 pairwise conflict 出现 `-9.95e-17/-7.67e-17` 浮点残差而失败。该幅度远小于既有 `EPSILON=1e-12`，其余输入域正常。旧协议 `d667ec704281a73651278c6ff9c08a14ef7fabf4239e2eea47e291ebb7d5bbee`、失败日志和12份部分指标已完整留档；未读取部分指标值用于修订。实现仅允许 `[-1e-12,0)` 的残差并裁剪为0，仍对低于 `-1e-12` 的真实负值失败关闭；新协议首次绑定生成器自身 SHA，并在活动结果0时重冻为 `cb0f3b77a5a2cc2c5d990f7de7282399e9da03e14db17b4f6f319a985b67720a`。

修订后14/14完成并按原冻结门形成负决策。相对 Pairwise 的 AUROC/AUPR/FPR95/OSCR 总体有向增益分别为 `+0.001141/-0.000291/+0.000353/-0.000380`；逐样本风险单调、预测与 Known F1 不变、正场景数 `8/14` 均通过，但只有 `3/7` 套件全指标不回退，最差套件指标为 CICIDS2017 AUPR `-0.020548 < -0.01`，四项总体也未全部为正。验证/测试平均激活率为 `4.65%/14.28%`，说明 known-only q95 在测试分布上仍明显过度激活。最终 decision 为 `retain_caeos_pairwise_and_reject_selective_topology_uplift`，branch manifest SHA `593cbdd64dfe7bd370a4b38127568520c0e9139a12a9628398ff63bc13c43652`，306次确认明确为 `not_required`。

该负结果不取消自有算法探索，反而给出下一候选的约束：不能继续使用仅靠 known-validation 固定 q95 的全局激活规则；新候选需要把分布偏移下的激活率稳定性、CICIDS AUPR保护和逐套件安全回退直接纳入 known-only 机制设计。Pairwise 当前仍是唯一 incumbent；不得根据局部正 AUROC/FPR95 强行替换。

Selective 协议修订后，post-30 v12 在九家族正式 analysis 为0时从 `c4d8df972ccb1242d55587421e3a2da4901a92289b9be3f99a58ec1a0170fc77` 修订为 `9032f5df2011480dc24ecfa57fafc4f1a28a5a8f158799654534c08614aa5081`。v7 首次真实预检又暴露未索引 `cuda` 与实际 `cuda:0` 的对象比较错误；森林维度一致、CPU等价正常，修复只把CUDA设备解析到当前索引，不改变模型或风险。10项本地/远端测试和16样本真实CUDA等价通过，概率最大差 `1.11e-16`、风险差0；v7协议在预检结果0时从 `1fc1a515...41c6` 修订为 `d4263fba04dd5a2dafb11fe24f7eb664230b8798e5ac3501d0b391a1b60ea619`，watcher PID `1556963` 已重启。外部设计因 Selective/post-30 和实现树变更，当前结果前 SHA 为 `c8d21c8dd0fa1b1b234722b677b1c48f2be86779f2121837a40ed704f7818416`；外部正式指标仍为0。

## 66. v7 正式预检负结果与第五自有候选纠偏

v7 张量化执行器已完成冻结的7个哨兵场景。预测数组全部一致，概率最大绝对差和风险最大绝对差均通过，张量森林显存门也通过；但三个 batch 的效率门全部失败。batch `1/64/512` 相对原生 OpenDetect 的 P99 中位比分别为 `32.15/41.59/72.34`，吞吐中位比分别只有 `3.12%/2.28%/1.25%`。正式 decision 为 `reject_tensorized_v7_and_retain_v6_system_tradeoff`，`formal_efficiency_claim_allowed=false`；因此 full204 分支已写 `not_required` 和 `branch_complete`，没有生成或执行正式 full 协议。v7 的负结果只关闭当前张量化执行器路线，不改变 Pairwise 的准确性身份，也不能被解释为自有算法探索无必要。

自有算法第五候选继续立项，但机制必须针对前四条候选暴露的共同失败模式做结构性纠偏。当前不再沿用 Selective Topology 的单一全局 q95 激活，也不按已观察结果放宽 alpha、套件门或最差指标门。下一候选暂定为“known-only 套件自适应可靠度预算门”：仅用已知训练/验证数据估计分层可靠度与允许激活预算，对冲突证据进行有界、可回退的样本级修正；预冻结门必须同时约束验证到测试的激活率漂移代理、CICIDS AUPR保护、逐套件最差回退和 Known F1 非劣。具体公式、数据使用边界和 pilot 场景将在任何新结果产生前单独冻结；在此之前不把该候选计入已完成方法或论文效果表。

基线队列方面，v7 完成后 WDiscOOD watcher 因旧启动副本脚本尾部引号解析错误退出，属于编排故障而非算法结果。活动脚本通过 `bash -n` 后，以原先在 `0/14` 冻结的 protocol `3c78dec4d9f0446428d770538eee3373ad2f9edcb9f4e57d669e2598e9c32322` 重新启动并完成 `14/14`、失败0。WDiscOOD 相对 MLP Mahalanobis 的四指标总体有向均值仅 `+0.000178`，Known F1 最大差0、总体平均未知指标排名第一；但只有 `4/7` 套件均值非负，Edge-IIoT 为 `-0.048630`、NF-UNSW 为 `-0.010753`，未达到冻结的 `5/7` 套件稳健门。因此 decision 为 `expand_to_full102=false`，full102 正确标记为 not-required。Fisher-Rao 和 RAS watcher 仍分别等待 CADRef/Fisher-Rao 上游，尚无可解释效果指标。当前可写的结论是“Pairwise 仍为自有 incumbent，Selective、v7 与 WDiscOOD 扩展门均为正式负结果，自有算法探索进入第五候选设计”，仍不能写全面SOTA、效率领先或新增基线胜出。

## 67. DoH 外部时间验证链解锁与零结果兼容修订

WDiscOOD 结束后发现 DoH temporal watcher 仍等待已废弃的 `runs/strict_v4_wdiscood_pilot_seed7/pilot_complete`，而当前 WDiscOOD 终点契约写入 `results/strict_v4_wdiscood_pilot_seed7/pilot_analysis_complete`。该依赖路径已修正，Bash语法和真实完成标志检查通过。由于原 DoH protocol 绑定修订前 watcher SHA，另在 DoH 正式 `metrics.json=0` 时冻结 dependency revision v2，SHA 为 `79ebc25d4b3c1fd30429c6494557b7f2aaa2925b55f226e56d310910e97a4467`；清单同时绑定原 protocol、新旧 watcher SHA、新旧前置标志和 WDisc 完成证据，并声明数据、拆分、种子、模型、门槛均未改变。

首次 seed223 真实训练随后在仍为0份正式指标时暴露合法混合精度 ISO-8601 时间解析问题：同列同时存在 `2020-...:37` 与 `2020-...:37.xxxxxx`，pandas 的单格式推断在第8000行失败。共享时间分组函数改为 `errors=raise, format=mixed, utc=true`，仍对非法或缺失时间失败关闭，时间顺序和 capture-group 分配不变。包含带/不带微秒混合输入的专项 `2/2 PASS`；input compatibility revision v3 在结果0时冻结为 `59f53efc4a1ac9425c3033164279a4686194885528b1b687218fc66b4e2471c4`，绑定原 protocol、v2修订、新旧 `caeos/data.py` SHA和测试 SHA。

DoH 随后完成 `3 seeds x Pairwise/OpenDetect = 6/6`、失败0，五项平均有向差全部为正：Known Macro-F1 `+0.02136`、OSCR `+0.35575`、AUPR `+0.30310`、AUROC `+0.44164`、FPR95 `+0.43640`，冻结的 `5/5` 非负门通过。该结果只能支持“同一DoH数据集内、按capture时间外推到更晚恶意工具”的 pilot 结论，明确不支持跨数据集、跨组织或全面SOTA。VOS 已按绑定当前脚本 SHA 的 protocol `86f6514e9635c73c1b5e17b66c3505f4124ff3a180d9001ee59e0b0d51124142` 以 PID `1626368` 接棒，正在GPU上训练首场景。

由于 `caeos/data.py` 属于 LSNM2024/CICDDoS2019 外部设计绑定的完整实现树，外部正式指标仍为0时已将旧设计 `c8d21c8d...8416` 留档，并以 `bind_mixed_iso_timestamp_compatibility_before_external_results` 为理由重冻当前设计 SHA `fe3f8dbf24aceba86dd0e65efd906f983598106ce79c1a4ef761e0a21ab7e156`；新设计显式绑定 `caeos/data.py` SHA `6b7d4b98...ebb27`，外部正式指标仍为0。第五自有候选仍须单独结果前冻结，不得复用 DoH 正结果作为候选选择信号。

## 68. 第五至第七自有候选与拓扑后处理路线关闭

在 Selective Topology 的激活率漂移之后，连续冻结并执行三条不重叠的 known-only 候选。三者均保持 Pairwise 分类预测不变，使用独立场景且不按结果放宽套件门。

| 候选 | protocol SHA | 14场景总体有向增益（AUROC/AUPR/FPR95/OSCR） | 稳健性 | 决策 |
|---|---|---|---|---|
| Budgeted Conformal Conflict Uplift | `cc28b0b3...bd81c` | `+0.002057/-0.002173/-0.000169/+0.003105` | 仅 `1/7` 套件全不回退；最大激活差 `0.02187` | 拒绝 |
| Conditional Conformal Conflict Uplift | `b795b8fe...6ea` | `+0.000779/-0.000397/-0.000253/+0.000775` | `2/7` 套件全不回退；最差 `-0.006257` | 拒绝 |
| Dual-Tail Conditional Calibration | `6f2369e7...5561` | `-0.000078/+0.000164/+0.000082/+0.000275` | `2/7` 套件全不回退；最差 `-0.001513` | 拒绝 |

三条新候选与 CTC、Selective 合计覆盖五轮相互排斥的开发场景。结果共同表明拓扑信号局部有效，但固定的后处理抬升、条件尾部预算和双尾校准都不能稳定替换 Pairwise。继续在同一路线调 alpha、q95 或套件门只会增加结果依赖自由度，因此拓扑后处理路线关闭；自有算法探索不关闭，而是转向证据可靠度估计、融合和训练目标。

## 69. 九家族 post-30 基线终态

VOS、GROOD、GSC、PRO、ActSub、CARE/CADRef、Fisher-Rao 和 RAS 均已接续完成；连同 WDiscOOD，九家族全部达到 `14/14`、失败0，并均按冻结门判定不需要 full102。主要结论如下。

| 家族 | 相对本家族 MLP 参考的关键结果 | 终态 |
|---|---|---|
| VOS | VOS 平均未知指标排名2.5，OpenDetect排名1；AUROC `0.6886` 对 `0.8004` | 不扩展 |
| GROOD | GROOD AUROC/AUPR/OSCR `0.6683/0.5272/0.5449`，均低于 OpenDetect | 不扩展；终点 marker 修复清单已绑定旧协议 |
| GSC | 相对 MLP Energy 四指标均值 `-0.04404`，七套件仅2个为正 | 不扩展 |
| PRO-MSP-fixed | 相对 MLP-MSP均值 `+0.001802`，但 FPR95回退且套件门/Top-2失败 | 不扩展 |
| ActSub-scale-fixed | 相对 MLP-MSP均值 `+0.07926`，但 CICIDS2017 `-0.26058`、仅4/7套件为正 | 不扩展 |
| CARE/CADRef | 相对 MLP Energy 均值 `-0.08928/-0.07393` | 均不扩展 |
| Fisher-Rao三式 | Tensor/Standard/Additive均值 `-0.06701/-0.07054/-0.18164` | 均不扩展 |
| RAS-Energy | 相对 MLP Energy均值 `-0.01598`，Known F1均值差 `-0.00154` | 不扩展 |

GSC 与 PRO 在结果前因通用 full102 summarizer 实现 SHA 更新而各自于0指标时重冻；旧 v12 按设计只在这两项协议身份上失败关闭。新增兼容审计逐项验证旧/新 protocol、gate、supersession、analysis 和阴性分支，得到 `post30_baseline_coverage_compatible=true`，manifest SHA `3da67d2d1d01f62d3d5d3d2659daf17bfd7c5c7d8cbcaa72f43f718a3f85e503`。这只证明原30方法加12个 post-30 候选的覆盖链完整，`confirmed_external_sota_allowed` 仍为 false。

## 70. 第八自有候选：类别条件可靠度融合

第八候选 `CAEOS Class-Conditional Reliability Fusion` 不再修改拓扑尾部。它仅用已知验证标签估计每个视图、每个预测类别的经验贝叶斯正确率

`R_vc = (correct_vc + 20 * global_accuracy_v) / (predicted_count_vc + 20)`

并以 `E_q[R_vc] * (0.25 + 0.75 * confidence)` 重算逐样本视图权重。候选只替换冻结 gate 下的 view-fused probability，精确恢复 incumbent 的温度网格；开放集风险固定为 `0.75 * Pairwise risk + 0.25 * (1 - max probability * sample reliability)`。未知/测试标签不参与可靠度、阈值或预测。

前五轮已用70个互斥场景，剩余32个只覆盖4套件。因此本轮在结果0时冻结为“四套件剩余未见场景机制筛选”，protocol SHA `38c086de958eb68efdcfd8e015c3df6efad302d701074795649f808d86bf6e97`；通过后仍必须在 `307/311/313` 新种子、七套件重训确认，不能直接升级论文结论。核心测试 `4/4 PASS`，14/14执行完成。

四项等套件总体有向增益全部为正：AUROC/AUPR/FPR95/OSCR 分别 `+0.012517/+0.008898/+0.091948/+0.033117`，正场景 `10/14`；Known F1平均差仅 `-0.000204`，温度重构最大误差 `3.33e-16`。但 CICIDS2017 与 NF-CSE 回退，只有 `2/4` 套件全不回退，最差套件指标为 `-0.041234`，故冻结决策仍是保留 Pairwise、拒绝当前固定融合。该候选比拓扑后处理更有总体信号，下一轮应研究 known-only 套件安全门或训练期可靠度目标，但必须用新种子，禁止在这14个已观察场景上改0.25权重后重测。

## 71. 外部设计与污染链恢复

自有候选新增 `caeos/*.py` 后，LSNM2024/CICDDoS2019 外部设计实现树再次发生合法变化。外部正式指标仍为0时，当前设计已绑定 post-30 supersession 兼容审计和完整活动源码，重冻 SHA 为 `2e62b71f7644eb5f8228e7dbcb33f7aad27b4cf32ceafb59429fa8294be65b46`；两个新增数据集仍未产生效果指标，不能计入全面SOTA。

选后污染链首次启动在第1个哨兵、0个正式指标时失败：runner 被传入不含 seed7 文件的旧缓存根。恢复没有重生成原始数据，而是建立独立兼容根，逐套件链接 clean Pairwise provenance 指向的 exact seed7 CSV，并绑定七个文件 SHA、失败日志和0指标状态；cache compatibility SHA 为 `46a141a81d971041f8cdc1f4976b7c09b8919c34e79d9991561f5ff70e40c5e1`。旧失败目录已归档，783任务现已恢复运行，完成后原续跑链才会进入比较污染和 final readiness。当前仍不能声明污染鲁棒性、全面SOTA或论文最终就绪。

## 72. 第九自有候选：验证门控的类别条件可靠度融合

固定权重 CCRF 虽然四项等套件总体增益均为正，但在 CICIDS2017 和 NF-CSE 上回退。第九候选 `Validation-Gated Reliability Fusion (VGRF)` 不在这14个已观察场景上调整0.25权重，而是保留同一候选，并仅用已知验证集决定每个场景是否启用；未过门时逐样本概率、风险和阈值输入均精确回退 Pairwise。启用条件同时约束 Known Macro-F1、正确已知样本风险、incumbent错误检测AUROC、错误/正确风险分离度，并要求至少一个错误代理改善达到0.005；未知标签和测试标签不参与门控或预测。

实现、评估器和执行链已通过远端语法检查，核心专项测试 `3/3 PASS`。在成对 reference/candidate 指标均为0时，已冻结训练种子307、七套件各2场景的协议，manifest SHA 为 `af4baac6b46723d3a1a60c63c57d64da45a31d78645dde095a26250f8e8ea589`。14个场景由固定盐哈希选取，与 CCRF 开发场景重叠0，选择不读取指标值，复用 seed7 精确样本缓存但重新训练 reference/candidate；冻结 pilot 门要求四项等套件总体均严格为正、至少6/7套件全指标不回退、最差套件指标不低于-0.005、至少9/14场景为正，并保持 Known F1 和精确回退。

VGRF watcher PID `1846169` 已排队，只在 `strict_v4_postefficiency_claim_chain_v2/chain_complete` 后启动，避免与783项污染矩阵抢占资源。污染矩阵当前只读快照为 `1/783`、失败0，不能据此推断最终趋势。若 seed307 pilot 通过，才冻结 `311/313 x 102` 保留种子确认；即使通过，也仍需外部数据、效率和污染硬门，不能直接升级为SOTA。

新增 VGRF 源码后，LSNM2024/CICDDoS2019 外部正式指标仍为0，因此外部设计再次按结果前修订：旧 SHA `2e62b71f...65b46` 留档，当前 SHA 为 `282dc0448554caa2779656df7d111e1c2a0309e23b1957ddfeffed684ed90665`，修订理由为绑定 VGRF 当前实现。两个新增数据集的效果结果仍为空。

## 73. 污染输出 schema 兼容恢复

缓存兼容恢复完成第1次训练并写出 `metrics.json/provenance.json` 后，旧 runner 在后置验证处退出且未写 `failure.json`。核验表明污染参数并未丢失：`provenance.command` 完整绑定 `feature_shuffle / modality 0 / severity 0.1 / seed 211`，但活动训练器的 `metrics.arguments` 只保留通用训练参数，因此旧 runner 从错误字段读取四个污染参数。这是输出 schema 校验来源不兼容，不是训练参数错误或效果失败。

原 protocol、原 runner 和首份指标均未覆盖。兼容修订在 `metrics=1、validated wrapper=0、failure=0、summary=0` 时冻结，SHA 为 `7e3833d1c76de4b564084a75cb8f59e6937c8f4e1c32bb2c63cec02b311df04d`；它只将四个污染参数的验证来源改为 `provenance.command`，仍要求 risk selection/policy 同时匹配 provenance 与 metrics，并保持任务、缓存、模型、种子、拆分、候选、指标和门槛不变。真实恢复已为首份结果写入 canonical wrapper，并启动第二个强度任务；当前仍为 `1/783`、失败0，不能形成污染效果结论。

## 74. 评价文档复核后的真实异构模态确认

重新按《CAEOS-EMTD评价.pdf》逐项核对后，当前主要缺口不再是通用 OOD 方法数量。原30方法加 post-30 九家族12候选已经覆盖42种方法；继续加入第43个弱适配基线，会进一步放大“排行榜论文”风险。资源优先级保持为：污染鲁棒性、真实异构模态新种子确认、LSNM2024/CICDDoS2019外部数据、唯一算法冻结和最终就绪。主表只保留 MSP/Energy/Mahalanobis/KNN、OpenMax、ARPL、OpenDetect、强树模型和 CAEOS 关键消融；统一表格适配但非官方完整复现的方法进入扩展表并明确适配边界。

Mal_TLS2023 已具备四种真实异构输入：9维 TLS handshake、39维 IP/flow statistics、39维 payload statistics 和30位置 packet sequence，共117维。现有30次开放集多种子证据使用过方法开发种子；异构编码器挑战者的12次试点又因 Qakbot/Scanners 和校准退化被拒绝，不能替代主算法确认。因此新增 `CAEOS-Pairwise vs OpenDetect` 的独立确认，使用未参与既有 Mal_TLS 候选开发的 `317/331/337`，覆盖6个恶意家族留出场景，共 `3 x 6 x 2 = 36` 次模型运行。

协议在 Pairwise/OpenDetect 指标均为0时冻结，manifest SHA 为 `feb260aa331cd3955c26b69c9514c0477b27c644f4b18a2c20dd931a94fb62a7`，专项自检 `7/7 PASS`。两方法必须逐场景逐种子共享完整特征指纹分组，所有组交集为0。主终点为先按种子求家族均值、再对六家族等权的四项开放集有向复合增益；冻结报告包括10000次家族 bootstrap、五指标配对 Wilcoxon/Holm、Known F1、家族复合非回退数和最差家族指标。确认门要求主终点95% CI下界大于0、四项开放集总体全正、至少5/6家族复合非负、最差家族指标不低于-0.05，并限制 Known F1 平均/单场景回退。

该确认等待 VGRF `pilot_complete` 后运行，watcher PID `2268680`，不会与当前污染矩阵并发。污染兼容 runner 已连续形成前三份 canonical wrapper，当前 `3/783`、失败0，正在第4项。即使 Mal_TLS 确认通过，也只支持“单个真实异构加密恶意流量数据集上的新种子确认”，不能替代跨组织、跨协议、污染和外部数据门。

## 75. VGRF 条件确认分支与串行调度修订

VGRF seed307 pilot 若阳性，原先只有协议中的保留种子声明，没有可执行的 full102 分支。现已补齐条件协议生成器、204对输入构造、成对训练/评估、双层 suite/scenario bootstrap 汇总和最终自有算法选择。覆盖构造从权威 coverage 与 seed7 provenance 得到 `311/313 x 102 = 204` 个唯一输入，静态自检 `8/8 PASS`。只有 pilot decision 精确为 `freeze_seed311_313_full102_confirmation` 才在 full 指标0时冻结确认协议；否则写 `not_required` 并保留 Pairwise。

full 门要求四项等套件有向均值全正、主复合增益 bootstrap 95% CI 下界大于0、至少6/7套件全指标不回退、最差套件指标不低于-0.005、至少20个场景启用、至少120/204场景复合增益为正，并保持 Known F1、温度重构和所有 disabled 场景精确回退。通过才选择 VGRF，否则 `caeos_pairwise` 继续作为最优自有算法；禁止逐指标或逐组件拼接。条件分支 watcher PID `2444019`。

调度复核发现 Mal_TLS watcher 初版只等待 VGRF pilot，阳性时会与204项确认并发。初版 Mal_TLS protocol `feb260aa...b62a7` 已在双方0指标时留档；等待条件改为 VGRF `branch_complete` 后，当前权威 protocol 为 `a11a92134649a8c0b9847fd8537d363a550f02902a1efaf1dc60cd6862ea26c7`，自检仍为 `7/7 PASS`，新 watcher PID `2491328`。数据、种子、场景、方法、统计和门均未改变。污染矩阵此时为 `5/783`、失败0。

## 76. 最终自有选择到外部数据的算法一致性

外部 LSNM2024/CICDDoS2019 原设计只允许 `caeos_pairwise` 与已拒绝的 Selective Topology，并从 post-30 accuracy audit 读取旧选择。如果 VGRF full102 胜出，旧 runner 会拒绝该算法或继续评估 Pairwise，无法证明“最终自有算法”的跨数据集表现。外部正式指标仍为0时已修订这一边界。

VGRF 条件分支现在无论 pilot 阴性还是 full102 完成，都会生成 schema `strict_v4_final_self_algorithm_selection_v1` 的 canonical `final_selection.json`：阴性明确选择 Pairwise；阳性只有全部 full 门通过才选择 VGRF。外部 execution protocol 改为读取该 manifest，而不是沿用旧 post-30 选择。当前允许算法为 Pairwise、Selective 和 VGRF；若选择 VGRF，外部 matrix 先按同一外部场景训练 Pairwise base，再从其 evidence package/scores 执行固定 VGRF known-only 门控，并与相同拆分的 OpenDetect 比较。汇总器验证未知/测试标签未参与门控，disabled 场景必须精确回退。

外部设计在0正式指标时由 `282dc044...90665` 修订为 `32c52598a1eb9785b2dfc5381acbc3471879a415c0c82b189aaba7187a0a714e`，专项验证 `6/6 PASS`。新外部 watcher PID `2686731` 显式等待数据准备、post-30审计、基础readiness、VGRF `branch_complete/final_selection.json` 和 Mal_TLS `confirmation_complete`，随后仍执行空闲采样、Pairwise语义回放、结果前 execution protocol 冻结和正式矩阵。污染快照为 `6/783`、失败0；外部正式指标仍为0。

## 77. 污染矩阵四路并行恢复

单任务资源审计显示服务器有80个逻辑CPU、503 GiB内存，串行污染任务约占8个CPU线程和10 GiB内存，GPU空闲。为缩短783任务的墙钟时间，在不改变任务语义的前提下将外层调度从1路提高到4路；每个任务仍固定 `model-jobs=8`、80棵树、seed7、污染seed211、同一缓存、拆分、Pairwise候选、输出路径和验收门，最多请求32个模型线程。

切换时先暂停串行父进程，允许其正在执行的第7个任务自然完成，再结束旧父进程。原始断点为 `metrics=7、validated wrappers=6、failure=0、parallel locks=0`；首批4个并行任务自然完成后，最终并行兼容清单冻结于 `metrics=11、validated wrappers=7、trained pending validation=4、failure=0、parallel locks=0`。协议 SHA 为 `83415875d1f26c8f1c948dac65f498110a5f3a6080e2aba4fd4407aa05eea4f4`，当前并行清单 SHA 为 `4ec663ab41ac5518bab750ecab025d86ce73f857287e85cfa4900d4cb45a32bd`。清单只读取产物数量，不读取指标值，也不允许据此修改算法、阈值或任务。

首次并行预检在新训练启动前暴露包装记录的恢复校验缺陷：写入时 `record_sha256` 未参与计算，但恢复校验误把该字段自身计入哈希。现已统一为移除 `record_sha256` 后校验，并同步修正最终污染汇总器。后续绑定审计又发现第7份包装曾把并行清单 SHA 写入名为 `schema_compatibility_manifest_sha256` 的字段；修订版固定传入 schema SHA `7e3833d1...df04d`，并以一次性修复清单 `d372e78448023d31553e7e8a603846ba7bc47c7e9e192e2d9e0800959152f1cc` 绑定该记录的旧/新文件哈希。11份包装现全部绑定同一 schema，指标与 provenance 哈希未改变。重启后4个独立训练子进程均以 `jobs=8` 运行，活动锁4、失败0。该修订只建立可恢复性和吞吐，不产生污染效果结论；必须等 `783/783` 汇总和后续 Pairwise/OpenDetect 比较污染完成。

## 78. 直接领域基线筛选与BSTS原生复现排队

在42种既有方法基础上，新增基线不再从通用OOD排行榜选择，而是从本地858篇文献库筛选2024--2026年直接处理未知加密恶意流量、开放集加密流量或开放世界NIDS的方法。RoNeTC、FOSS、Sieve和OpenDetect已在现有证据中；ECNet、BSTS-Net、FEC-OSL、MDCG-IDS等属于直接任务候选，其中当前只有ECNet和BSTS-Net具备本地官方代码。

ECNet官方仓库当前 HEAD 为 `667eb8014920cabba4873d18cd6258310bddc118`，本地README、训练器和5个预处理文件与该HEAD逐文件SHA完全一致。论文的CICIDS2018-III原生未知攻击划分为：训练FTP/SSH Patator、GoldenEye/Hulk/Slowloris/SlowHTTPTest和Botnet；测试Web Brute Force/SQL Injection/XSS与DDoS LOIC HTTP/UDP，正常流量按前5天训练、后3天测试，训练数据再取10%验证。GPU服务器已有455 GiB CSE-CIC-IDS2018原始按日抓包和10份ML CSV，覆盖这些日期。但官方代码只硬编码一个正常流量30分钟片段，未提供论文三种重组数据的完整构造脚本，服务器数据又是按日/主机组织而非论文代码使用的30分钟合并pcap。因此当前只能标记为“数据可构造、官方高保真复现未准入”，禁止用自建表格输入冒充ECNet原生复现或直接进入主表。

BSTS-Net官方仓库 HEAD `8eb4eb38f617079d579c55c5037c86ef5eb265a4` 与本地代码、模型定义和 `testData.zip` 逐文件SHA一致；官方ZIP SHA为 `7dd5abc9...e78c`，提供Patator中间特征演示。首版协议 `17f28ef56e469c8910b7a4d453a8162038e9ef1f26a924c1bf60109c5a2ab08d` 虽固定了代码、数据和5个KMeans随机种子，但未绑定精确依赖环境，已在运行记录0时留档作废。当前权威v2协议 SHA 为 `296397e7dfb21cfd1b8d3aab29840ca15dfb71f61b92c17880c982d09cce8a5e`，绑定独立环境 `/opt/data/private/wangwt/envs/bsts-native-1.5.0`、Python 3.9.25、NumPy 1.26.4、SciPy 1.13.1、scikit-learn 1.5.0、joblib 1.4.2、threadpoolctl 3.5.0、PyYAML 6.0.1、四个离线wheel SHA以及runner/summarizer SHA。运行器流式解压并验证3个成员SHA，以 `317/331/337/347/349` 重复官方 `Detect.clusterIPByTpy`，报告Accuracy/Precision/Recall/F1均值、标准差和范围。它只作为原生Patator附录领域基线，不进入七套件Unknown AUROC主表、不参与自有算法选择或外部SOTA门；5/5完成且canonical验证通过后才可把覆盖数从42更新为43。watcher PID `1202388` 等待外部评测完成并连续确认主线空闲后启动。当前BSTS结果仍为0，污染矩阵快照为 `23/783`、失败0。

## 79. 自有算法探索保留与调度状态复核

《CAEOS-EMTD评价.pdf》要求减少低价值基线堆叠，并不意味着取消自有算法探索。论文能否形成方法贡献，最终仍取决于一个冻结、可复现且在独立证据上成立的自有算法。当前 Pairwise 是唯一 incumbent；Selective Topology、Budgeted/Conditional/Dual-Tail Conformal、CCRF 等已观察候选的负结果必须保留，禁止通过删场景、逐指标拼接或在同一14场景上继续调权重把失败候选包装成成功。第九候选 VGRF 使用只读取 known-validation 的可靠度门，seed307 pilot 与 CCRF 开发场景交集为0；只有 pilot 满足冻结门，才执行 seed311/313 的102场景、204对条件确认并整体选择 VGRF，否则精确回退 Pairwise。该链是当前自有算法探索的权威终点，不能被BSTS、ECNet或新增通用OOD基线替代。

2026-07-23 03:24 UTC 远端复核显示，污染矩阵已有27份 `corruption_metrics.json` 通过包装验证，另有4份任务处于训练中，即 `27/783 + 4 running`，失败标记0；并行父进程 PID `3456730` 和4个直接子进程均存活。VGRF pilot/条件确认、Mal_TLS真实异构确认、外部数据评测和BSTS原生附录 watcher PID 分别为 `1846169/2444019/2491328/2686731/1202388`，全部存活且正式结果仍为0。主机80逻辑CPU的一分钟负载约107、可用内存约452 GiB、剩余磁盘约5.3 TiB；当前瓶颈为CPU而非内存或磁盘，污染并发保持4，不再叠加训练。

执行顺序继续冻结为：先完成783项污染矩阵及其汇总，再运行VGRF独立pilot和条件full确认，随后执行Mal_TLS新种子真实异构确认，最后启动LSNM2024/CICDDoS2019外部评测与BSTS附录复现。只有最终自有算法选择、污染鲁棒性、真实异构模态、跨数据集和基础readiness全部形成canonical证据后，才可评估“全面SOTA”是否成立。当前可以撰写方法、协议、负结果、基线边界和阶段实验部分，但仍不得写全面SOTA、最终鲁棒性成立或跨数据集领先。

## 80. 2026直接领域SOTA的协议分轨审计

对 FEC-OSL（TIFS 2026）和 MDCG-IDS（TNSM 2026）完成论文正文、GitHub精确仓库检索和GPU数据覆盖复核。准入清单 `direct_domain_2026_baseline_admission_audit_v1.json` 的 SHA 为 `3a1b1d63d6d0b139cdecb7426b37f051648db4762bd9090ce84865050e59d255`；两篇论文PDF SHA分别为 `00cdd2b9...ca86f` 和 `c12f87b3...8ce7`。论文正文均未声明源码仓库，GitHub repository API 对方法全名、缩写和论文标题片段的4次精确检索结果均为0；该结果只表示当前未发现公开仓库，不等价于证明作者没有私有或后续发布代码。

FEC-OSL原生协议使用 USTC-TFC2016、CIC-IDS2018 和 ISCX-Tor2016，在每个known/unknown比例下把一半未知类作为无标签辅助未知训练数据，另一半作为novel unknown测试数据，终点为known/unknown AUC、known-class F1和unknown clustering AMI。GPU服务器已覆盖三套数据：USTC-TFC2016约4.0 GiB/35文件、CIC-IDS2018原始数据约455 GiB/40文件、ISCX-Tor约20 GiB/4文件，即数据覆盖 `3/3`。但论文没有给出随机种子、各比例具体类别身份和完整预处理实现；其辅助未知暴露与strict-v4的未知类不参与训练契约不同。因此它只能作为独立协议重建候选，不能直接写入strict-v4主表或用表格输入低保真适配。

MDCG-IDS原生协议覆盖 CICIDS2017、UNSW-NB15、ToN-IoT 和5GAD，采用60/20/20拆分：只用良性训练，以良性和已知攻击验证，以未知/OOD攻击测试，报告5次独立运行的AUROC、F1和FPR。GPU已有CICIDS2017原始数据约52 GiB/25文件、UNSW-NB15约101 GiB/91文件和ToN-IoT约3.4 GiB/8文件，但数据根下未发现5GAD，即覆盖 `3/4`。论文依赖从原始抓包重建带IP的flow/session及跨时间、空间粒度张量，却未提供实现和随机种子值，故当前同样只进入协议分轨候选；补齐5GAD和作者级预处理证据后才能启动高保真复现。

这两项审计不会中断已冻结的自有算法与鲁棒性链。基线扩展的下一准入优先级为：等待或发现官方代码 > 补齐原生数据与预处理证据 > 冻结独立协议 > 运行复现；禁止为了增加方法数而在当前CPU满载阶段启动论文重实现。若未来完成复现，其结果也必须按各自辅助未知/良性训练协议单列，不能用不同任务的reported SOTA支持“strict-v4全面SOTA”。

## 81. 5GAD官方数据获取链

MDCG-IDS引用的5GAD已定位到 Idaho National Laboratory 官方 `IdahoLabResearch/5GAD` 仓库。仓库当前main HEAD为 `d6c3643dafb0683ecac2557e1a5ca29c3b5d7ecb`，2026-06-18后归档只读；它包含正常流量、10类5G攻击、PCAPNG和原始数据准备脚本。元数据审计得到273个LFS路径、272个唯一对象；两个FakeAMFDelete路径共享同一OID。工作树最终落盘应为 `35,462,353,124` 字节，去重传输量为 `35,450,181,332` 字节。权威LFS清单 SHA 为 `41c9a865cd03d64ff61863ed55127fff815bb7a2129eaaae893f6107a4ce86a0`。

已在GPU服务器建立 `/opt/data/private/wangwt/ParkAttackKE/datasets/5GAD-2022`，以固定commit、NFS原子目录单实例锁、两路LFS传输、`nice=19`、`ionice=best-effort/7` 启动后台获取。首次使用 `flock` 的进程因NFS返回“No locks available”而在下载前退出，未生成仓库或数据；随后在无活动进程时修订为原子目录锁并重启。当前runner SHA为 `ba8fe2232e5b0c9b056d8fa8c2b76c7d28960c65c373c9aee38db79482c8e4c7`，launcher PID `3271616`；获取协议 SHA 为 `03efdfd28f056321c3f80931f0d9f6dfdfb3d8d37425d3d419ff6970188d5860`。

2026-07-23 03:53 UTC 的首份清单进度为 `101/273` 路径、`88,787,095/35,462,353,124` 落盘字节，仍有172个LFS指针，缺失0、大小异常0。该路径暂只算“官方数据获取中”，不算数据集准入。完成门要求HEAD、清单SHA、273个路径大小和LFS OID SHA全部一致，`download_verification.json` 为passed且完成标记绑定commit。之后仍须审计攻击分组标签，并实现/核验MDCG-IDS所需flow/session/IP重建与60/20/20协议；下载完成本身不能写成MDCG-IDS复现或SOTA结果。

## 82. 5GAD自动准入审计与官方预处理缺陷

为避免把“Git LFS命令退出0”当作数据可用，新增下载完成后的独立准入审计。协议 SHA 为 `8401d897157395181f31b7def0f8b5f32cfb59c6e7d90844569048e1aa4d2395`，审计器/等待器 SHA 分别为 `5e874314...42cea8` 和 `906d77d5...729206`。它等待固定commit完成标记和全量SHA验证后，检查273个LFS路径、三类根目录计数、82个PCAPNG魔数、10个攻击目录，以及每类恰好6个抓包、1个 `Attacks_<name>` 纯攻击抓包和1个 `allcap` 抓包。Normal-1UE/2UE还分别要求7/15个allcap抓包。watcher PID `3788026` 已存活排队，当前正式审计结果0。

官方 `Data_prep.py` SHA `2f73f72c...b8b41` 存在可静态复核的Normal-2UE缺陷：代码执行 `for pcap in datasets`，但循环内调用 `sniff(offline=str(file))`，其中 `file` 是上一阶段Normal-1UE循环遗留变量。因此未修订脚本会重复读取最后一个Normal-1UE文件，而不是逐个读取2UE文件。该脚本本身输出打乱后的payload二分类数组，也不包含MDCG所需IP、flow、session、时序和空间关系；即使修正变量名，也不能作为MDCG-IDS原生预处理。准入报告将数据完整性与 `mdcg_flow_session_preprocessing_ready`、`mdcg_ids_baseline_admitted` 三个状态分开，后两项在本审计中固定为false。

04:07 UTC 下载进度为 `203/273` 个完整路径、`10,760,146,467/35,462,353,124` 个完整文件字节，剩余70个LFS指针，缺失/异常0；数据目录约23 GiB，单下载进程和准入watcher均存活。同期污染矩阵为 `48/783 + 4 running`、失败0，说明低优先级下载没有阻断四路污染训练。

## 83. MDCG-IDS在5GAD上的原生协议可证边界

已从论文Table IV/V视觉复核并冻结5GAD设计协议，SHA 为 `c1317ced542ac11672c78339c6f233d1b08ba7e56678eae9a5d6998be939fd2d`，状态为 `design_only_not_executable`。类别契约为：训练只含Normal；验证ID为Normal、AMFLookingForUDM、GetAllNFs、FakeAMFInsert、randomAMFInsert、CrashNRF和FakeAMFDelete；测试ID复用全部验证类；OOD-1为GetUserData和randomDataDump；OOD-2为automatedRedirectWithTimer和automatedDropWithTimer。

重建契约为5元组flow，10秒inactive timeout、30秒active timeout；TCP session按双向flow和FIN/RST状态切分，UDP/ICMP按共同端点与协议形成单向片段，间隔不超过60秒时合并。时间粒度固定为0.5秒subflow、10秒flow和60秒session。Traffic维覆盖packet size、IAT、TCP window的均值/标准差/最小/最大值，flow包数/字节/持续时间/bytes-per-second，以及session的flow持续时间方差、inter-flow方差、flow数和正反向包/字节比。Temporal维覆盖TCP flag/transport protocol的符号序列、频率、熵和方差；Spatial维覆盖session级flag/protocol集合与host级destination-port/protocol集合。5GAD因TLS缺application protocol，论文对全部数据统一删除该特征。

论文只说明60/20/20、训练仅良性、验证/测试含分层正常与攻击，却未给出将每类记录精确分配到三部分的算法；符号序列/集合的数值编码、五次运行的seed值及作者实现也未公开。因此当前只冻结可证契约和缺口，禁止用自选拆分或编码启动“原生复现”。数据准入、精确采样规则、flow/session实现、五种子结果前冻结和MDCG最优传输模型审计全部完成后，才能进入独立协议基线表。

## 84. 5GAD纯攻击flow重建探针

GPU服务器没有tshark/tcpdump，当前主环境没有Scapy，但py3.9已有 `dpkt 1.9.8` 且支持PCAPNG。为避免自行实现抓包解析器，在10个已经完整物化的官方 `Attacks_<name>.pcapng` 上冻结只读flow探针：协议 SHA `bd508859041572aa0c57f2d6569c1508fc1c2d88f7fb3981e4cca375e93af7c1`，runner SHA `7b82e7ab...bab8d0`。输入逐项绑定LFS OID和大小，方向5元组、10秒inactive和30秒active规则与论文一致；该探针不读取Normal、不生成session、特征张量或模型指标。

10个抓包共39,730包，其中39,424个IP包、306个非IP包，PCAPNG/Ethernet解析异常0；重建得到5,601个方向flow。各攻击flow数为：AMFLookingForUDM 398、CrashNRF 398、FakeAMFDelete 2,296、FakeAMFInsert 397、GetAllNFs 398、GetUserData 398、automatedDropWithTimer 60、automatedRedirectWithTimer 60、randomAMFInsert 799、randomDataDump 397。FakeAMFDelete触发141次active和474次inactive切分；两个定时UDP攻击各触发59次active切分，其余输入未触发超时切分。canonical record SHA 为 `e2d9abe38fb741d1a50a91855dd7286d702ceee8ab139011e2a3d7c8fe696e9a`。

该结果只证明官方纯攻击PCAP可由固定解析器执行论文的5元组flow切分，不能证明23,621 session目标、Normal标签、双向session、Temporal/Spatial编码或MDCG模型正确。04:16 UTC时5GAD目录约33 GiB，仍处于单实例LFS下载且未产生完成标记；自动准入watcher继续等待。同期污染矩阵为 `64/783 + 4 running`、失败0。

## 85. VGRF实现级创新与泄漏审计

自有算法探索继续作为论文方法贡献主线，但当前候选必须按真实机制定位。VGRF不改变训练目标，其贡献位于可信开放集决策层：在known-validation上估计“视图-预测类别”经验贝叶斯可靠度，以预测熵调节视图权重，形成类别条件融合概率；再把样本可靠度转成证据风险，与冻结Pairwise风险按固定0.25比例混合。候选只有同时满足Known Macro-F1、正确样本风险、错误检测AUROC和错误/正确风险间隔门时才启用，否则概率、风险和阈值输入精确回退Pairwise。可支持的论文表述是“验证门控的类别条件可靠度融合与风险校准”，不能表述为新的端到端训练架构。

远端逐文件SHA复核确认，可靠度模块 `f28633c7...8ae06`、门控模块 `8b403cde...48d`、评估器 `4c621462...5301`、矩阵运行器 `196f2e6d...af73` 和汇总器 `ecdd43b8...5b85` 与 canonical protocol `af4baac6...ea589` 的冻结绑定一致。本轮只新增测试，未修改候选公式、参数或门。反事实测试保持证据包和验证输入不变，只置换 `test_labels` 与 `test_unknown`；两次执行的验证门、参考/候选阈值、门状态、验证风险、测试风险和测试预测均逐元素一致，而保存的测试标签/未知标记确实发生变化。GPU py3.9环境直接调用四个测试函数得到 `4/4 PASS`，测试文件SHA为 `f3302a21...d1d6a`；该环境未安装pytest，因此严格记录为“直接函数测试通过”，不是完整pytest套件通过。审计记录 SHA 为 `5cd31f3b93a5cdde31f62bdf78993a90177d4c3d4890124f8ee778e297f1f699`。

该审计把测试标签泄漏风险降为已有可执行反证，但创新性风险仍为中等：VGRF属于post-hoc决策层机制，固定收缩强度和0.25风险混合本身不足以支撑宽泛原创性或全面SOTA。当前状态仍为“候选运行、未准入”。seed307的14个预注册场景必须先整体通过冻结门；只有阳性才允许seed311/313全102场景确认。若pilot阴性，本轮整体拒绝VGRF并保留Pairwise，不在同一决策周期继续新增按结果驱动的候选。若full确认阳性，再执行去类别条件可靠度、去安全门、去风险混合和全局/类别条件可靠度替换消融，并报告启用率、精确回退率、阈值漂移、预测变化率与运行开销。

2026-07-23 04:34 UTC远端快照为污染矩阵 `81/783 + 4 running`、provenance 85、失败0，父进程PID `3456730`及4个直接子进程存活；VGRF pilot watcher PID `1846169` 仍等待污染完成，正式结果为0。5GAD下载PID `3271616` 与准入watcher PID `3788026` 存活，目录约53 GiB、已有82个PCAPNG，仅余4个Normal-2UE LFS指针；但 `download_verification.json`、完成标记和准入 `audit.json` 均未生成，所以仍不得写成数据准入完成或MDCG-IDS复现。

## 86. 5GAD下载完成、准入纠错与MDCG覆盖更新

2026-07-23 04:42 UTC，固定commit `d6c3643...d7ecb` 的5GAD下载和全量验证完成。`download_verification.json` 文件 SHA 为 `acf1a37c...6eb1b`：LFS清单 `41c9a865...e86a0` 的273个路径全部通过逐文件大小和SHA-256验证，物化字节精确为 `35,462,353,124`，失败0，完成标记绑定同一commit。获取进程正常退出，数据本身不再处于“下载中”。

首版独立准入没有直接放行，而是以 `official_source_hash_mismatch` 失败关闭。失败报告文件 SHA `e399b34c...796dc`、canonical记录 `c1f39bbe...fefd`。根因是v1协议把元数据审计副本的三个哈希当成固定commit源码内容SHA；下载后的Git blob与工作树实际内容一致，但与错误期待值不同。v1失败报告和协议 `8401d897...4d2395` 已保留。v2只修正这三个期待值，并同时读取 `git show <commit>:<file>` 与工作树文件进行双重校验，其余commit、LFS、PCAP魔数、目录、标签和官方脚本缺陷门均不变。v2协议/审计器 SHA 为 `7c28edeb...432e2d` / `6782a0bf...7ac98`。

v2正式准入通过：82个PCAPNG魔数有效，10个攻击目录及每类6个抓包、纯攻击/allcap、Normal-1UE 7个和Normal-2UE 15个allcap均满足冻结结构；源码expected/Git blob/worktree三方SHA一致。结果文件/记录 SHA 为 `a0ab7b94...70f74` / `11f63494...6299`，`dataset_integrity_passed=true`。同时，`mdcg_flow_session_preprocessing_ready=false`、`mdcg_ids_baseline_admitted=false` 仍保持，官方Normal-2UE陈旧变量缺陷也继续被检出。

因此MDCG-IDS四套原生数据覆盖由 `3/4` 更新为 `4/4`，直接领域基线审计v2 SHA为 `5e3a0613...5958e`，但可执行基线仍未增加。MDCG预处理协议v2 SHA `7eb7bfe8...92b54` 新增两个作者实现缺口：官方5GAD同时提供allcap、按接口拆分副本和纯攻击子集，论文未公开具体抓包选择/去重规则；Normal-2UE是连续分片，论文也未说明跨文件flow/session状态是否连续。论文报告的23,621 session只作为结构验证目标，禁止在看到模型指标后选择最接近该数量的预处理变体。

04:55 UTC污染矩阵进度为 `86/783 + 4 running`、provenance 90、失败0，剩余磁盘约5.2 TiB。当前继续优先完成污染矩阵；MDCG下一步是结果前冻结抓包选择、跨文件边界和TCP/UDP/ICMP session化实现，再以结构目标验证。它必须单列为论文约束下重建，不能标记为作者官方复现或直接支撑strict-v4全面SOTA。

## 87. MDCG-5GAD抓包选择冻结

完成数据准入后，先冻结输入范围而不运行flow/session或模型。选择规则来自官方README与 `Data_prep.py` 的实际输入：Normal选择Normal-1UE全部7个和Normal-2UE全部15个 `allcap*.pcapng`；每个攻击选择唯一的 `Attacks_<attack>.pcapng` 纯攻击抓包。攻击目录中的allcap和四个单接口副本全部排除，避免同一攻击包被重复计入。最终选中32/82个PCAPNG、`35,341,145,636`字节，排除50个重复语义输入；选择过程不读取论文报告的23,621 session，也不读取任何模型指标。

首次跨平台复现中，选择集合与canonical记录SHA完全一致，但Windows生成文件使用CRLF、GPU使用LF，导致文件字节SHA不一致。v1协议 `991d2ae6...56b4f`、本地文件 `318e3cc2...ecde5`、远端文件 `40ed9383...714a` 和共同canonical记录 `ea857067...42fd9` 均保留，且未写完成标记。v2只把JSON写出固定为UTF-8/LF并记录supersession，选择语义不变。

GPU重新执行v2后与本地文件逐字节一致，协议 SHA `a3a3f6b801fd46ece7377a985357aa7a0358f05fb30866325fa318956055e73f`，生成器 SHA `35341cb8...2e82f`，清单文件/记录 SHA 为 `080d8df7...b616f5` / `1ec8bf6a...1a038d`。当前只可写“抓包输入范围已冻结并跨平台复现”；Normal-2UE跨文件flow连续性、Normal-1UE跨抓包状态、无FIN/RST时的TCP状态机、60/20/20分配和符号编码仍未解决，因此不能写session化、MDCG预处理或基线复现完成。

## 88. MDCG flow/session核心与真实攻击canary

新增纯Python flow/session核心：方向五元组flow按严格大于10秒inactive或30秒active切分；TCP按canonical双向端点聚合并在携带FIN/RST的包后关闭；非TCP按canonical端点和协议聚合，严格超过60秒inactive才关闭。合成边界测试覆盖等于/超过阈值、双向TCP、FIN/RST优先级、UDP反向流、ICMP、乱序失败关闭和跨键时间回跳。本地与GPU py3.9当前核心均为 `9/9 PASS`。

真实canary只使用已冻结的10个纯攻击抓包，不读取Normal、23,621目标或模型指标。v1适配器因Python 3.9不支持未延迟求值的 `PacketRecord | None` 在模块导入阶段失败，抓包读取0；v2只增加延迟注解后启动，但全局时间单调断言在FakeAMFDelete拒绝915个包，结果文件 SHA `7a12422c...239d`，按门失败。

进一步冻结的时间顺序诊断覆盖39,730包：发现144次跨接口全局相邻时间回跳，最大0.238732秒；按旧全局高水位规则会拒绝915包，但方向flow键和canonical session键内部逆序均为0。诊断脚本/结果/记录 SHA 为 `a815c3d9...e771` / `0a02f90f...c5e7e` / `42eae0c8...d421a`，不读取效果指标或论文session目标。由此v3只把全局单调改为flow键和session键分别单调；同键逆序仍失败关闭，timeout和capture scope不变。

v3协议 SHA `120dc2f2...2f56d` 下真实canary通过：39,730总包、39,424 IP包、306非IP包、解析错误0，所有IP包逐个守恒到session；重建7,207个方向flow和5,666个session。结果文件/记录 SHA 为 `e13778fd...db12f` / `4829d047...9ed16`。该结果只准入攻击抓包上的固定解析器和边界实现，不能证明Normal重建、23,621总session、三维特征或MDCG模型。

## 89. MDCG全量session结构门排队

全量协议在Normal结果0、full结果0时冻结。Normal-1UE的7个按时间命名allcap作为一个连续组，Normal-2UE的15个明确顺序分片作为一个连续组；10个攻击组直接复用已绑定canary，不重复选择。全量结构门要求22个Normal抓包全部Ethernet、解析错误0、IP包与session包守恒，并要求Normal与攻击合计session精确等于论文报告的23,621。若不相等，runner写失败报告并整体拒绝，不允许修改抓包组、10/30/60秒比较、FIN/RST或非TCP端点规则后重试。

runner/watcher/protocol SHA 为 `5b1e6474...257d6` / `5bf5de42...1353e` / `7b1995e2...eaf3b`。watcher使用原子目录锁、`nice=19`和 `ionice=best-effort/7`，等待BSTS原生基线完成并连续确认主训练空闲后才扫描约35.34 GB；BSTS又依赖VGRF、Mal_TLS和外部评测，因此不会与当前主线并发。watcher PID `1706756` 已存活等待。2026-07-23 05:34 UTC污染矩阵为 `102/783 + 4 running`、provenance 106、失败0。

即使全量session门通过，也只允许将 `mdcg_flow_session_preprocessing_ready` 推进到结构重建层；Traffic、Temporal、Spatial张量、60/20/20精确拆分、最优传输模型和五种子实验仍须分别冻结和验证，MDCG仍不能进入strict-v4主表或支撑全面SOTA。

## 90. VGRF直接文献新颖性纠偏

自有算法探索继续保留，但VGRF的创新表述需要进一步收窄。对本地850篇可检索全文先执行 `class-conditional reliability`、`validation-gated`、`exact fallback`、`known-validation reliability` 和 `safety gate` 的组合短语筛查，精确命中文件为0；随后对五项最接近方法执行逐机制深读。该筛查只能说明当前本地语料未发现相同组合表述，不能证明更广泛文献中不存在相同方法。

最高重合风险是 RoNeTC（TIFS 2025）：它已经把流拆成三视图，用Dirichlet二阶分类概率形成样本级证据与不确定性，并以Dempster-Shafer规则动态融合不同视图。因此VGRF不得声称“首个可靠多视图融合”“首个不确定性感知开放集流量分类”或“新的证据融合”。ECNet（TIFS 2024）也已包含内容/模式多视图、可学习门控、独立置信分支和低置信未知攻击拒绝；MGN-OSR（Computer Networks 2024）已包含RGB多特征融合、类别特定自编码重构/激活评分、已知样本95%覆盖阈值和线性分数组合。FEC-OSL与MDCG-IDS分别覆盖能量边界加辅助未知训练、跨粒度三维表示加最优传输距离，进一步限定VGRF不能借用端到端训练、未知聚类或跨粒度表示贡献。

当前可辩护的差异单元不是“可靠度融合”本身，而是三项组合：只用known-validation结果估计视图-预测类别经验贝叶斯可靠度；以场景级已知类非退化门决定是否启用；未启用时对Pairwise概率、风险和阈值输入执行精确回退。VGRF仍不改变训练目标，定位保持为post-hoc可信决策层。直接文献审计将新颖性风险由 `medium` 提升为 `medium_high`；当前只能称“候选known-validation门控类别条件可靠度校准层”，不能称已证明原创方法。

这项纠偏不修改已冻结公式、0.25风险混合、门值或seed307场景，也不增加第十候选。若seed307 pilot阴性，按原协议整体拒绝并保留Pairwise；若阳性，仍须seed311/313全102场景确认，之后再做全局/类别条件可靠度、去安全门、去风险混合、去精确回退消融，并报告按套件/类别的启用率和回退率。只有独立确认、污染、真实异构、外部数据和效率证据全部成立后，才允许把该窄化机制写成论文方法贡献。

审计文件为 `vgrf_direct_literature_novelty_audit_v1.json`。2026-07-23 06:12 UTC远端实测污染矩阵为 `122/783`、provenance 126、失败0，父进程及4个直接子进程存活；VGRF pilot/确认、Mal_TLS、外部评测、BSTS和MDCG全量session watcher也全部存活，但均未生成完成标记。当前资源顺序不变，不为文献审计新增GPU训练并发。

## 91. RoNeTC历史作者代码恢复与原生准入边界

VGRF直接文献审计把RoNeTC识别为最高重合风险后，进一步核验其基线证据。论文正文第808行给出的 `https://github.com/xuemanxm/RoNetTC/tree/main` 当前返回404且 `git ls-remote` 为repository not found；GitHub仓库检索定位到迁移后的公开仓库 `xueman-xm/RoNetTC`。其main HEAD为 `af391a4f4f98fb832de416a3d01293d0668d46f9`，当前树只有README。完整历史有33次提交，显示2025-03-03和03-07连续删除数据目录、权重目录和全部Python源码，不能仅按当前HEAD得出“作者从未提供代码”。

删除前最后完整源码提交为 `8f47b9a4fc24aebe1d8a7b9e4c4625b40438bb23`，tree `bcb42184...992e`，共13个文件。已在 `source/RoNetTC-historical-8f47b9a4` 以detached HEAD只读保留，工作树干净；8个Python文件经捆绑Python AST解析 `8/8 PASS`。GPU的GitHub代理失效，故未改网络配置，而是生成完整历史bundle `2e18b7c5...3ed97f`（4,127,395字节）并逐SHA传到 `/opt/data/private/wangwt/ParkAttackKE/baseline_sources`；离线检出的远端HEAD/tree/13文件数与本地一致。源码包含三个MobileViT视图分类器、非负证据/Dirichlet意见、逐视图与联合证据损失、顺序Dempster-Shafer融合和联合不确定性拒识，两份约2.31 MB权重也已绑定SHA。因此现有CAEOS适配的核心机制来源可追溯到作者历史代码，而不再只是论文公式重写。

历史代码仍不能直接形成作者原生复现。默认已知输入 `datasets/tmc_256_16.txt` 不存在，默认未知输入 `datasets/cic_256_16.txt` 只有2字节换行；根目录 `cic.txt` 也只有2个标签均为0的样本。论文使用的UNSW智能设备流量、CIC IoT 2022和MApps三套数据，在权威GPU数据根与既有数据清单中匹配为 `0/3`；全用户目录深扫超时，因此只能写“已知权威位置未发现”，不能证明整台服务器绝对不存在。仓库还缺原始PCAP到三视图文本的完整预处理、六场景类别身份、精确依赖锁和阈值来源记录，原生正式结果保持0。

## 92. CICIoT2022 GPU获取启动与CrossPlatform身份纠偏

用户已在官方页面完成CIC IoT Profiling 2022注册并授权使用浏览器Token。认证目录实际暴露根目录10个文件和 `5-Active` 下24个PCAP、1个Readme，共35个文件；官方Readme称Active实验为30天，但当前页面只列24个PCAP，因此冻结清单只下载实际可见的24个路径，不推测不存在的6个文件。清单 `ciciot2022_gpu_acquisition_manifest_v1.json` SHA为 `ffd50c95...646a8`，固定目标 `/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2022`、单实例、并发1、`nice=19`、I/O优先级7、逐文件结构校验、SHA-256和原子落盘。

站点对非浏览器客户端返回403并重新签发Cookie；本机和GPU普通curl结果一致，因此不能把浏览器Cookie直接视为通用下载凭据。独立环境 `/opt/data/private/wangwt/envs/ciciot2022-download-curl-cffi-0.15.0` 固定 `curl_cffi 0.15.0`，Chrome指纹传输器在GPU成功取回官方Readme 2798字节，SHA为 `aa59d591...73287a`。正式下载器/传输器SHA分别为 `68962654...9368b`、`fad81252...db524`，Token只保存在一个权限0600的 `/dev/shm` 文件并由退出trap清理。PID `403951` 于2026-07-23 08:09 UTC启动；08:14 UTC仍只有1个runner和1个fetcher，`1-Power.tar.gz` 已完成结构校验并原子落盘，大小510,038,785字节，进度为 `1/35`，`2-Idle.tar.gz.part` 已增长到260,840,200字节，错误为空，磁盘剩余约5.2 TiB。同期污染矩阵为 `259/783 + 4 running`、失败0，全部下游watcher存活，未增加训练并发。下载完成后仍须通过35/35结构与哈希门、18个Table-II设备身份映射、三视图预处理和无泄漏canary，当前不得写成RoNeTC原生复现或新增基线结果。

对 `/opt/data/private/wangwt/ParkAttackKE/datasets/CrossPlatform` 的只读审计表明，它不是RoNeTC所用MApps。Android和iOS目录各只有一个413,158,969字节的 `Datasets.tar.gz`，两者SHA完全相同，为 `8be1c35e...f6f9d6`；归档共703,085项，包含625,420个NPY、75,414个PCAP和25个JSONL，顶层同时出现 `CrossPlatform_android`、`CrossPlatform_ios`、`CSTNet-TLS1.3`、`ISCX-Tor-2016`、`ISCXVPN2016` 和 `USTC-TFC-2016`。MAppGraph论文把Cross Platform列为既有外部数据，并另行采集自身Android应用流量；单个重合应用名不能证明同源。身份审计 `crossplatform_mapps_identity_audit_v1.json` SHA为 `b7a935d6...21c3`，结论为高置信 `is_mapps=false`，Dataset-III原生准入仍为false。

阈值协议也必须分轨。论文以已知/未知样本TPR/FPR最大化 `2*TPR-FPR` 选择联合不确定性阈值，但没有给出独立未知验证集；历史代码正式测试使用固定CLI默认值 `0.002`，可选Youden工具会从当前 `y_true` 与测试不确定性计算最优阈值但调用被注释，仓库没有给出 `0.002` 的可复现推导。strict-v4适配因此明确改为只在known-validation风险上取分位数，未知/测试标签仅用于最终指标。这保证无泄漏，但必须标记为“协议修正适配”，不是论文阈值的逐字复现。

现有两层RoNeTC证据继续有效且不重复计方法数：第一层为39项共享侧信道同划分适配，RoNeTC AUROC `0.656010`，同任务CAEOS为 `0.932796`，胜/平/负为 `38/0/1`；第二层为strict-v4独立训练pilot，RoNeTC 14项包含在四方法 `56/56` 中，失败0，Known F1/AUROC/AUPR/FPR95/OSCR为 `0.691196/0.574312/0.357768/0.511269/0.517134`，相对OpenDetect四未知指标有向均值 `-0.196197`，未过full102门。每份远端provenance绑定适配器SHA `33d794dc...0720`，GPU直接运行3个unittest方法均通过；GPU环境未运行pytest，不能写pytest通过。

当前准入结论为：RoNeTC已经是有效的概念基线和适配强基线，但不是作者原生复现。历史源码恢复只关闭代码可审计性缺口，不关闭数据、阈值和原生结果缺口。下一步若推进原生轨，必须先补齐三套精确数据与SHA、六场景类别清单、三视图预处理和兼容环境，并把论文阈值复现与known-validation无泄漏修正分开报告；当前污染/VGRF链运行期间不新增RoNeTC训练。

2026-07-23 06:51 UTC远端复核显示污染矩阵为 `163/783`、provenance 167、失败0，父进程和4个直接子进程存活；VGRF pilot/确认、Mal_TLS、外部评测、BSTS和MDCG watcher也全部存活。污染汇总、VGRF pilot、VGRF最终选择标记均未出现，故当前仍不能形成VGRF效果、最终自有算法或全面SOTA结论。

## 93. CICIoT2022设备身份与RoNeTC三视图输入契约

官方 `Device List.xlsx` 已随CICIoT2022下载落盘，文件为11,616字节，SHA为 `fe81d78d...e1981`，包含40条设备记录。按RoNeTC Table II的18个缩写标签执行不猜测映射，得到15个唯一库存候选和3个歧义标签：`HeimVision *` 同时对应摄像机与Radio/Lamp，`Google Nest *` 同时对应Nest Mini与室内摄像机，`Amazon * Dot` 对应两台不同MAC的Echo Dot。即使15个标签只有唯一候选，也仍需设备级CSV目录和原始PCAP MAC成员关系验证，因此当前完全解析类数为0，`dataset_ii_identity_admitted=false`。

身份协议文件 SHA 为 `45d83047...c8a52f`。GPU端在官方Excel出现后自动重新生成，协议与本地逐字节一致，专项测试 `10/10 PASS`；远端复现记录 SHA 为 `21391ad0...5d94c4`。这只证明库存解析和候选映射可复现，不允许按名称相似度替3个歧义标签选设备，也不允许在18类身份冻结前开始效果导向的流提取或类别拆分。

同时从删除前历史作者代码冻结精确三视图文本边界。每个flow必须是连续3行，顺序固定为 `ip_header / tcp_header / client_payload`；每行16个包时，`byte_num=256` 对应单包 `20/32/204` 字节。仓库根样例 `cic.txt` SHA为 `cbef8ed...3c74ac`，共有2个flow、6行。校验器、测试、契约和样例验证文件 SHA 分别为 `b60ed20d...ce73e`、`af35e8c5...ae1ce`、`04c59b7b...12413`、`1cd0bb3e...2c9a1`，本地和GPU均为 `9/9 PASS`，5个同步文件逐SHA一致。

格式验证通过不等于原始PCAP适配器已准入。历史仓库仍未给出双向flow键规范、timeout、重传/分片、时间戳并列、首包方向归一化、固定20/32字节切片实现、源设备标识和无泄漏group ID。后续必须先用下载完成后的设备目录与PCAP MAC关闭身份门，再结果前冻结这些flow语义，生成小规模canary并通过结构守恒和分组无泄漏检查；禁止把历史随机60/20/余数拆分直接包装成strict-v4无泄漏结果。

2026-07-23 08:43 UTC下载状态已推进到 `11/35`，完成字节 `5,527,634,276`，正在获取 `5-Active/2021_11_03_Active.pcap`，错误为空；PID `403951` 仍为单runner/单fetcher。同期污染矩阵为 `277/783 + 4 running`、provenance 281、活动结果根失败0，父进程PID `3456730`和4个直接子进程存活；VGRF pilot/条件确认、Mal_TLS、外部数据、BSTS和MDCG watcher均存活但无新增正式完成结果。当前最优自有算法仍是Pairwise，VGRF仍是冻结候选，全面SOTA、最终污染鲁棒性和RoNeTC原生复现均未成立。

## 94. RoNeTC Dataset-II源目录与MAC身份实证

在不读取任何模型效果的前提下，新增 `ronetc_ciciot2022_source_directory_contract_v1.json`，把RoNeTC Table II的18个论文标签绑定到CICIoT2022官方Interactions目录及可用的CSV目录前缀。由于3个标签各有两个物理候选，契约共冻结21个候选设备；契约文件 SHA 为 `74477d4b...e3d8`。身份审计器直接流式读取官方 `3-Interactions.tar.gz` 中绑定目录的PCAP Ethernet帧，并以官方设备库存MAC验证成员关系，不按标签字符串或模型指标选择设备。

GPU真实审计覆盖21/21个候选源、413个PCAP成员、71,483,614字节和100,859个Ethernet帧；每个候选目录的官方MAC覆盖率均为 `1.0`，失败0。15/18个论文类因此唯一解析。`HeimVision *`、`Google Nest *`、`Amazon * Dot` 的两个候选目录都被真实PCAP和MAC证据支持，现有数据无法唯一消歧，继续标记为3个歧义类。Ring Base Station虽无对应CSV候选目录，但其Interactions原始PCAP目录和库存MAC已完整通过，因此不构成源身份失败。

审计结果文件 SHA 为 `650844a4...19b`，审计器/测试 SHA 为 `5b41e10d...3ec` / `da2902cc...56c`；合成正负测试在本地和GPU均为 `9/9 PASS`。更新后的RoNeTC原生准入协议 SHA 为 `9f0ff3b2...11d82`，已在GPU端逐SHA验证。其准入结论保持 `dataset_ii_fully_admitted=false`：15个唯一类只允许进入单独命名的结构/适配canary，禁止产生作者原生完整Dataset-II指标；3个歧义类必须取得作者级身份说明，或在结果前预注册全部候选组合的敏感性分析，且不得事后选择最好组合。

2026-07-23 09:13 UTC，CICIoT2022下载为 `19/35`、完成 `11,911,347,121` 字节，正在获取 `5-Active/2021_11_17_Active.pcap`，错误为空；单runner/单fetcher和PID `403951` 均存活。09:14 UTC污染矩阵为 `283/783 + 4 running`、provenance 287、失败0，父进程和4个直接子进程存活，系统负载约 `83.02/82.56/80.61`，数据盘剩余约5.2 TiB；VGRF pilot/确认、Mal_TLS、外部评测、BSTS和MDCG watcher继续等待。该进展补强高保真直接基线的可复现数据边界，但没有新增RoNeTC效果、没有替换Pairwise，也不改变全面SOTA尚未成立的结论。

## 95. RoNeTC身份敏感性与三视图结构canary

对3个仍有双候选的论文类，不再把“等待作者说明”作为唯一推进路径。结果前冻结8种笛卡尔组合，协议 SHA 为 `8a22b933...ba68c`；3类按class id `0/1/15` 的候选顺序生成 `identity_v000` 至 `identity_v111`。8个组合全部是同等敏感性条件，不设主组合，不允许按模型效果选择或只报告最佳组合；未来必须在相同预处理、拆分、种子和超参数下报告逐组合值、最小/中位/最大值及结论符号一致性。协议在本地和GPU均为 `8/8 PASS`，当前完成组合仍为0，且不能据此称作者原生身份复现。

同时对15个唯一身份类执行原始Interactions PCAP到历史RoNeTC三视图文本的结构canary。v1在模型执行前失败关闭：TCP-only门使Home Eye和Netatmo两类flow数为0，且构建器还含GPU Python 3.9不支持的 `Path.write_text(newline=...)`。失败记录 SHA 为 `0297ede0...a879`，没有生成文本、group或模型指标。独立逐类诊断 SHA `ac32a00f...f4cc` 表明两类均无TCP flow；进一步的协议号普查 SHA `ae837939...a2fd` 证明Home Eye含11,803个UDP、21个ICMP帧，Netatmo含10,615个UDP、10个ICMP帧。该事实与已冻结“固定32字节传输层切片、不得把历史 `tcp_header` 名称解释为纯TCP”的输入契约一致。

v2只允许IPv4 TCP与UDP并继续排除ICMP，同时改用Python 3.9兼容原子写出；类、抓包、设备MAC方向锚、抓包级group边界、无跨抓包聚合、flow排序、首16包和 `20/32/204` 固定切片均不变。协议/构建器/测试 SHA 为 `f88f96b7...4772` / `f3ad7f92...b0af` / `18135b3a...acba`，本地和GPU `10/10 PASS`。

GPU真实v2结构canary通过：扫描264个PCAP、84,741个Ethernet帧，15类各取8条，共120条flow；其中TCP 74条、UDP 46条，实际输出包883/195，共52个抓包级group。文本为2,462,808字节，SHA `b2b38614...1d25c`，严格通过120 flow、360行、16包及单包 `20/32/204` 字节的历史格式验证；group清单/构建审计 SHA 为 `1075fd0d...adde` / `137c078d...8d9e`。独立输出验证在本地和GPU逐字节一致，SHA `170cb5df...86b2`，错误0。更新后的总准入协议 SHA 为 `199d615a...e9cf6`。

该结果只把 `dataset_ii_unique_class_structure_canary_admitted` 推进为true。三类身份仍未唯一确定，full flow timeout/重传/分片、完整35文件校验、group-disjoint拆分和六场景模型均未完成，所以 `dataset_ii_fully_admitted=false`、`ronetc_native_baseline_admitted=false`，新增模型效果仍为0。2026-07-23 09:44 UTC下载状态为 `24/35`、完成 `13,371,381,090` 字节；`2021_11_24_Active.pcap.part` 已增长到4,463,618,808字节，runner/fetcher存活且错误为空。污染矩阵为 `289/783 + 4 running`、provenance 293、失败0；VGRF及下游watcher仍在等待。当前最优自有算法继续为Pairwise，全面SOTA仍未成立。

## 96. CICIoT2022独立完成审计与full预处理冻结

下载器本身会在35项完成后逐文件计算SHA并写 `download_verification.json`，但单一实现自证不足以关闭数据准入门。新增独立完成审计协议 `ciciot2022_independent_completion_audit_protocol_v1.json`，SHA为 `f0f99f52...5bf84`。独立审计重新验证固定清单SHA和35个精确路径，要求下载器state/verification/complete三者一致，禁止任何 `.part` 或symlink，并重新计算全部文件SHA；同时完整遍历tar.gz、验证PCAP魔数、XLSX ZIP CRC与内容类型、文本非空。只有全部通过才写 `dataset_acquisition_admitted=true`，仍不自动推进设备身份或RoNeTC模型准入。

审计器/测试/watcher SHA分别为 `4108c5c3...dddd7` / `a6efcad9...d717` / `3f522080...312f`。8项合成测试覆盖正常35项、清单SHA错误、缺完成标记、残留partial、文件哈希变化、非法PCAP、验证路径集缺失和state错误，本地与GPU Python 3.9均为 `8/8 PASS`；Windows缺Linux Bash，故本地Shell语法未运行，GPU `bash -n` 已通过，不能写成双端Bash测试。watcher PID `150686` 已以单实例锁等待，下载完成后使用 `nice=19` 和idle I/O独立执行；启动记录 SHA 为 `4296f024...c80ad`。

论文正文只公开Dataset-II每类500个样本、双向flow首 `l` 包以及已知类60/20/20；未公开CICIoT2022六类实验的源范围、timeout、方向、分片/重传或抓包group。官方CICFlowMeter文档也明确timeout可由使用者任意指定，只给出600秒示例，不能据此反推RoNeTC作者原值。因此新增 `ronetc_ciciot2022_full_preprocessing_split_protocol_v1.json` 时明确标记为strict-v4适配而非作者原生复现，协议 SHA `a126551a...aacc`，本地/GPU均 `8/8 PASS`。

适配源范围在任何full flow或模型指标出现前固定为Power、Idle、Interactions、Scenarios和认证清单实际可见的24个Active PCAP；Attacks因可能把攻击过程线索引入设备身份类而排除，Zigbee/Z-Wave因不满足IPv4 Ethernet三视图输入而排除。范围不得因某类不足500 flow而扩展。flow固定为抓包文件硬边界、设备库存MAC标签、IPv4 TCP/UDP双向五元组；TCP遇FIN/RST关闭，TCP/UDP均严格大于600秒空闲时切分，不设active timeout，不跨抓包延续，时间戳回退失败关闭，TCP重传保留，非首分片排除并计数。

每个身份组合的每类必须至少形成500 flow；否则不得调timeout或扩源。已知Dataset-II场景必须形成精确300/100/100，抓包group不得跨train/validation/test；若无法在group不交叉的条件下满足精确数量，整体失败。未知Dataset-II每类按相同冻结哈希顺序选500并全部进入test。8个身份组合同等执行，未知/测试标签不得参与阈值；作者Youden阈值与known-validation无泄漏修正继续分轨。

2026-07-23 10:02 UTC下载已到 `26/35`、完成 `19,509,767,250` 字节，正在获取 `2021_11_26_Active.pcap`，partial为1,968,349,944字节且增长中，错误为空；下载PID `403951`和独立审计watcher PID `150686`均存活。污染矩阵为 `295/783 + 4 running`、provenance 299、失败0，VGRF pilot/确认仍等待。更新后的总准入协议 SHA 为 `6caf12cf...ec1e`。当前只完成协议冻结，不产生full flow、拆分、RoNeTC指标或自有算法替换结论；Pairwise仍为incumbent，全面SOTA仍未成立。

## 97. RoNeTC full flow与group容量可行性审计链

full协议冻结后继续补齐可执行实现，但避免为8种身份组合重复扫描原始数据。新增可行性审计器先按21个物理候选设备各自的官方MAC提取一次flow，再把固定15类和3类候选映射组合成8个身份variant。每个Ethernet帧必须恰好命中一个候选设备MAC；0命中和多设备命中均排除并计数，避免同一包重复进入两个设备类。源范围继续固定为Power、Idle、Interactions、Scenarios和24个Active PCAP，不读取Attacks、Zigbee或Z-Wave。

解析器只接受classic Ethernet PCAP、IPv4 TCP/UDP和完整首分片；双向key为排序后的IP/port端点加协议。TCP FIN/RST后关闭，TCP/UDP严格大于600秒空闲切分，抓包结束关闭全部活动flow；全局或同flow时间戳回退直接使抓包失败，不重排。输出只包含每物理设备flow数、抓包group容量、协议/关闭原因/排除原因计数和稳定flow摘要SHA，不生成三视图训练文本，不读取模型指标。

协议/auditor/test/watcher SHA为 `3b23fb43...9ada` / `b072fb4a...df78` / `df8fde1f...5358` / `171156c6...0b63`。12项测试覆盖正反方向key一致、双设备MAC排除、UDP接收、ICMP/非首分片排除、600秒严格边界、FIN关闭、时间回退以及协议范围、依赖和三份实现SHA绑定；本地与GPU Python 3.9均为 `12/12 PASS`，GPU `bash -n` 通过。

可行性门要求21个物理候选均至少500 flow且至少3个抓包group，从而保证8种身份组合在计数层都可继续；任一短缺都整体失败，不能扩源或改timeout。精确group-disjoint 300/100/100仍由后续split-manifest builder独立求解，本轮不得把“计数通过”写成“拆分可行”或“full预处理完成”。

为保持自有算法和既有高保真基线链优先，真实扫描watcher PID `1036742` 同时等待两项：CICIoT2022独立35项审计标记，以及MDCG full session重建完成标记。两项未齐时不扫描数据；触发后以 `nice=19`、idle I/O单实例执行。启动记录 SHA 为 `cfae444d...615f`，当前物理候选完成0、身份variant完成0、flow结果0。

2026-07-23 10:19 UTC下载推进到 `27/35`、完成 `24,281,208,828` 字节，正在获取 `2021_12_06_Active.pcap`，partial为304,837,376字节，错误为空；下载/独立完成审计/full flow watcher均存活。污染矩阵为 `300/783 + 4 running`、provenance 304、失败0，VGRF pilot/确认仍等待。总准入协议更新为 `f0775407...f590`。Pairwise仍是当前唯一incumbent，全面SOTA和RoNeTC效果均未成立。

## 98. ECNet原生CICIDS2018数据可行性审计

通用OOD方法覆盖已足够宽后，基线扩展优先转向与本文多视图可信融合主张最接近的直接领域方法ECNet。新增只读准入协议 `ecnet_cicids2018_native_data_feasibility_protocol_v1`，绑定作者仓库commit `667eb8014920cabba4873d18cd6258310bddc118`、6个关键源码SHA和GPU原始目录 `/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cse_cic_ids2018/raw`。协议和真实结果文件SHA分别为 `d1b06c18...c588438`、`bed681d0...78a6a`，结果内部canonical记录SHA为 `e81b2a77...11dff`。

审计器不导入或执行作者预处理脚本，而是用AST静态提取 `type2path`、`type2ip`、当前活动攻击类型和正常窗口，从而避免硬编码路径触发写操作。作者代码中可解析13个攻击类、56个30分钟攻击窗口和9个所需日期；GPU上9个日期的PCAP归档全部存在，另有10个官方CICFlowMeter CSV，因此 `official_source_exact`、`attack_mapping_parse_complete` 和 `raw_archive_date_coverage` 三门通过。审计器及测试已在本地和GPU Python 3.9执行，均为 `12/12 PASS`。

高保真原生执行仍被三门阻断。第一，作者脚本当前只激活 `ddos_loic_udp` 和1个正常窗口，未提供完整全日到30分钟切片程序、`combine_feat`合并器、活动训练入口和论文低置信判恶意推理。第二，场景I/II/III、正常流量时间拆分、10%验证划分、Table I攻击身份和Table II采样数量尚未形成结果前冻结的七份重组工件。第三，GPU未发现 `tshark`、`editcap` 和精确SplitCap工具链。对应结果为 `native_execution_admitted=false`，ECNet新增模型指标仍为0；禁止按论文报告F1反推缺失窗口、采样或阈值。

2026-07-23 10:42 UTC，CICIoT2022仍为 `28/35`、已完成 `25,114,539,234` 字节，`2021_12_07_Active.pcap.part` 已增长到3,823,564,536字节，下载错误为空；污染矩阵推进到 `305/783 + 4 running`、provenance 309、失败0。Pairwise继续作为唯一incumbent，VGRF仍等待污染链，ECNet审计不改变全面SOTA尚未成立的结论。

## 99. ECNet Table I/II精确重组契约

针对前一节“Table I攻击身份和Table II采样数量未形成机器可验证证据”的阻断项，直接回到本地论文PDF第9页、期刊页6879进行可视复核。PDF SHA为 `2fd94696...63190`，固定渲染页为1836×2376像素、SHA `500ffad7...cb3da`。同时纠正前一版协议的来源URL元数据：固定源码的实际Git origin为 `https://github.com/Shining20183/ECNet.git`，不是v1协议误写的组织名；纠正清单SHA为 `1a682758...17d4b`。commit `667eb801...c118`、六个源码SHA、审计门和v1结果均未改变。

Table I表明CICIDS2018论文场景使用12个细类，作者脚本中的第13类 `infiltration` 不属于任何论文场景。场景II的训练类为FTP Patator、GoldenEye、Hulk、Web Brute Force、SQL Injection、Botnet和LOIC HTTP，测试类为SSH Patator、Slowloris、Slowhttptest、XSS和LOIC UDP；两侧不交叉且并集恰为12类。场景III训练类为FTP/SSH Patator、四种DoS和Botnet，测试类为三种Web Attack与两种LOIC；同样不交叉且覆盖同一12类。场景I使用五个粗类别下的相同12类池进行随机训练/测试划分。

Table II精确规模如下。表头是 `Train & Validate`，正文只说明从训练集随机抽10%作验证集，因此不得把这些总数自行拆成逐类训练/验证整数：

| 场景 | Train & Validate Normal | Train & Validate Malicious | Test Normal | Test Malicious |
|---|---:|---:|---:|---:|
| CICIDS2018-I | 630,000 | 157,618 | 270,000 | 67,550 |
| CICIDS2018-II | 600,000 | 159,499 | 300,000 | 65,669 |
| CICIDS2018-III | 600,000 | 202,789 | 300,000 | 32,379 |

契约 `ecnet_table_i_ii_reorganization_contract_v1.json` SHA为 `1330f7ff...8ff4c2`。本地/GPU均 `10/10 PASS`，本地与GPU验证文件SHA分别为 `874da055...b3051` / `af082738...cc14`；去除路径和记录哈希后19个语义字段逐项一致。`table_contract_admitted=true` 只表示论文表格转录、12/1类代码映射和场景分区通过；完整正常30分钟窗口、时区、SplitCap等价session化、Table II降采样顺序、10%验证随机种子、`combine_feat`合并与置信阈值仍未公开，所以 `native_execution_admitted=false`、ECNet效果仍为0。

2026-07-23 10:56 UTC，污染矩阵为 `309/783 + 4 running`、provenance 313、失败0；CICIoT2022仍为 `28/35`，当前 `2021_12_07_Active.pcap.part` 已增长到6,401,590,008字节，下载错误为空。VGRF及其确认分支继续等待，Pairwise仍是唯一incumbent，全面SOTA未成立。

## 100. FEC-OSL论文边界协议与GPU数据可行性

在通用OOD基线已覆盖42种方法、BSTS/MDCG/RoNeTC/ECNet直接基线均有条件执行链后，继续补齐2026年TIFS直接方法FEC-OSL，但不把论文报告曲线复制为本地复现。论文PDF SHA为 `00cdd2b9...ca86f`；开放集比例页和CICIDS2018概念漂移Table II页固定渲染为1224×1584，SHA分别为 `5d638182...f341a` / `ee56387d...cf4d5`。契约 `fec_osl_paper_bounded_protocol_v1.json` SHA为 `c5258826...1be94`。

FEC-OSL与strict-v4不是同一未知类协议。对总未知类数 `Nu`，论文把 `floor(Nu/2)` 个类作为无标签辅助未知直接参与能量边界训练和深度聚类，剩余未知类才作为novel unknown留到测试。USTC-TFC2016使用 `16:4/12:8/8:12/4:16`，CICIDS2018使用 `5:2/4:3/3:4/2:5`，ISCX-Tor使用 `6:2/4:4/2:6`。前两者分别与论文描述的20类和7类一致；ISCX-Tor正文称有16种应用，但全部比例总和均为8，形成论文内部类宇宙矛盾，不能自行选择8类解释后启动实验。

论文可证预处理边界为SplitCap独立双向flow、移除Ethernet头、匿名化IP/端口、首5包、20×20 header矩阵、40×40 payload矩阵、30节点interaction graph和7种节点特征。可证训练配置为Python 3.8.19/PyTorch 1.8.1、SGD、两个学习率 `1e-4/1e-3`、50 epoch、batch 64、温度10、能量边界 `-10/-5`。但论文未给官方代码、各比例known/auxiliary/novel具体类身份、随机种子、精确样本拆分、平衡采样数、SplitCap版本与flow语义、匿名化算法、burst阈值、完整CViT/TAGCN结构、初始聚类算法/类数、动量beta、伪标签和重训周期、Weibull拟合集及无泄漏超参选择。

GPU只读审计确认三套命名数据根 `3/3` 存在：USTC 20个类别候选均有PCAP/归档/目录证据，CICIDS2018十个日期目录及ML目录齐全，ISCX-Tor两份PCAP归档为11,827,793,332和9,418,400,492字节且两份CSV存在。本地/GPU正反向测试均 `12/12 PASS`；验证器/测试 SHA为 `42614b95...47588` / `6530404d...e4318`，GPU结果文件/记录 SHA为 `f73ae07a...9f546` / `4cbf1d32...43f8e`。静态字段与本地结果逐项一致，结论为 `paper_contract_admitted=true`、`gpu_dataset_coverage=3/3`、`native_execution_admitted=false`、`model_metrics_generated=false`。直接领域总账以增量纠正清单 `2dc43668...4e960` 将FEC-OSL由“协议解析待办”更新为“协议已冻结、原生执行不准入”，不覆盖v2审计。FEC-OSL只能作为协议分层附录候选，不能进入strict-v4同协议主表。

2026-07-23 11:15 UTC，污染矩阵为 `314/783 + 4 running`、provenance 318、失败0，父进程与4路训练均存活；CICIoT2022为 `29/35`、已完成32,406,092,744字节，当前 `2021_12_08_Active.pcap.part` 为2,965,619,448字节且继续增长，错误为空。BSTS、MDCG、VGRF及外部评测继续按冻结顺序等待；Pairwise仍是唯一incumbent，全面SOTA未成立。

## 101. M3S-UPD传导式负试点与Trident官方演示纠偏

### 101.1 M3S-UPD冻结身份

M3S-UPD已具备项目内论文公式适配器，但它与strict-v4主协议不是同一推断权限。适配器只用已知训练和已知验证进行训练、检查点与阈值选择，初始标注比例为30%，对剩余已知训练样本迭代伪标注；未知和测试标签不参与拟合或选择。推断阶段却联合使用完整验证或测试特征批进行DBSCAN对齐和多轮传导聚类，所以协议身份固定为 `secondary_transductive`，禁止进入主归纳式表。论文未公开精确网络结构，现有 `MLP-128-64-32` 只能称paper-formula adapter，不能称作者原生实现。

在任何M3S效果出现前冻结7套件各2场景、seed7的14场景协议。协议/扩展门canonical SHA为 `f754ef4e...9603f` / `c6d8efa7...25165`，对应文件SHA为 `130f980b...86cac` / `0c953cda...26d0b`。合同绑定M3S四份既有实现和独立汇总器，默认30 epoch、patience5、10轮训练更新、20轮传导推断；结果生成前为 `0/14`。协议生成、断点恢复、实现变更拒绝、来源覆盖、报告别名及传导身份的远端测试为 `9/9 PASS`，既有M3S核心/适配/矩阵测试为 `46/46 PASS`。

### 101.2 14场景效果与停止决策

低资源runner以单worker、2个BLAS/OpenMP线程、`nice=15` 和I/O优先级7运行，RTX A6000实际分配约354 MiB；14项全部完成，失败0，分割指纹和无未知/测试标签拟合检查均为 `14/14`。分析文件SHA为 `18a5e893...38340`。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR |
|---|---:|---:|---:|---:|---:|
| OpenDetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 |
| M3S-UPD适配器 | 0.681277 | 0.595305 | 0.396238 | 0.601132 | 0.503945 |

相对OpenDetect，M3S-UPD的AUROC/AUPR/OSCR分别下降 `0.205064/0.239028/0.133935`，FPR95恶化 `0.250351`；四项定向平均增益为 `-0.207094`。Known F1平均差为 `-0.084850`，最差场景为 `-0.354422`。七套件中只有Edge-IIoT为正 `+0.075591`，CICIoT2023和CIC-ToN-IoT分别为 `-0.481723/-0.484231`，其余四套件也为负。

八项扩展门中，运行完整、分割/泄漏、传导身份和二方法排名边界通过；Known F1保护、指标广度、总体增益和套件稳健性失败。因此 `expand_to_full102=[]`，不再消耗102场景预算。该结论是当前适配器的有界负证据，不否定M3S-UPD论文；若未来取得作者网络和原始在线更新实现，应重冻独立流式协议，且仍不得与无测试批传导的主表混排。

### 101.3 Trident官方demo准入审计

官方Trident仓库固定在commit `1868ee07...07f3af`，本地仓库通过Git bundle `c76c9a71...d0c4` 离线同步GPU，同一commit和完整历史均通过。仓库仅包含KDDCup99四类demo，README明确示例一次只出现一个新类，同时出现多个新类时的buffer聚类没有提供完整实现。

机器审计确认两处会使官方demo Accuracy失真。第一，`main_process.py:138-140` 把 `gtlabel[:i5]` 与原标签拼接后重新训练，即新类真实标签直接参与增量拟合。第二，160行在Accuracy计算前把每个新类块中的全部拒绝值999替换为 `allIndex[ii]` 的真实类ID，165行才计算Accuracy。该指标路径不能作为无标签未知类发现或开放集分类效果。

审计器和正反向测试在本地/GPU均为 `6/6 PASS`。为消除Windows CRLF与Linux LF差异，文本和CSV统一LF后计算SHA，并同时绑定Git blob OID；两端审计结果文件逐字节一致，SHA为 `8184bedf...9af0`，内部canonical记录为 `649bd16d...9a9ec`。结论为 `official_code_available=true`，但 `official_demo_accuracy_admitted=false`、`native_paper_dataset_result_admitted=false`、`strict_v4_primary_table_admitted=false`，新增模型指标0。

Trident继续作为流式开放世界相关工作和可修复适配候选。只有去除 `gtlabel` 更新、保留真实拒绝/聚类身份、实现无标签同时多新类聚类，并在结果前冻结流式评估协议，才允许执行AE+SPOT修复版；修复版必须单独命名，不能覆盖本次官方demo拒绝记录。

2026-07-23 11:54 UTC，污染矩阵为 `325/783`、失败0，四路训练继续运行；CICIoT2022为 `29/35`、已完成32,406,092,744字节，当前 `2021_12_08_Active.pcap.part` 为11,929,521,912字节并继续增长，剩余5项未开始。M3S-UPD已完成且不扩展，Trident没有准入效果；VGRF及确认链仍等待污染完成。Pairwise仍是唯一已确认incumbent，全面SOTA仍未成立。

## 102. Trident AE+SPOT无预言机负试点与数据获取闭环

### 102.1 v1失败保留与v2超越协议

在官方demo拒绝后，新增独立命名的 `trident_ae_spot_no_oracle` 适配器。它逐已知类加载官方skip-connected AE和SPOT实现，只在known-training训练AE、用known-validation选择检查点并拟合类别阈值；未知/测试标签只用于最终指标，测试样本逐个评分。官方 `gtlabel` 增量更新、拒绝值真值回填和测试批聚类全部禁用，因此可进入归纳式主协议的候选层，但只能称 `primary_inductive_repaired_official_adapter`，不能称作者原生流式复现。

v1协议/门在 `0/14` 冻结为 `3213ec39...c3a5` / `1f073df4...27d0`。真实执行得到3份指标后，在CIC-ToN-IoT `mitm` 场景失败：该场景把 `ddos` 留为已知类，但known-validation只有9条正确类重构损失；设计已预冻结SPOT不可用时回退known-validation 85%分位，v1实现却在进入回退前拒绝少于10条的输入。该失败不是NaN或训练发散。v1的3份指标、provenance、协议和失败日志全部保留，不与后续结果混合。

v2只修正这一实现与预注册策略不一致：空数组、非有限值和负损失继续硬失败；1至9条有限非负损失使用原已冻结85%分位；10条及以上先运行SPOT，SPOT异常或阈值非正时使用相同回退。指标、协议、门和分析schema均升至v2，运行/结果目录改为独立 `strict_v4_trident_ae_spot_pilot_seed7_v2`。新增9样本回退和NaN拒绝测试后，GPU完整依赖环境 `13/13 PASS`，Python编译和Bash语法通过。v2协议/门在新目录 `0/14` 冻结为 `5403c606...c7c20` / `caa88955...a1211`，文件SHA为 `a7310b54...516f` / `e496edf2...8e78`；协议显式绑定v1协议、门、`3/14 + 1 failure`状态和不得混用规则。

### 102.2 14场景效果与停止决策

v2在7套件各2场景、seed7上完成 `14/14`，矩阵失败0。14份指标schema均为v2，`device_used=cuda` 为 `14/14`；未知/测试拟合、联合测试特征聚类、oracle更新和真值回填均为false，逐样本独立评分和主归纳表资格均为true；group overlap检查失败0。独立复算与分析器一致。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR |
|---|---:|---:|---:|---:|---:|
| OpenDetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 |
| Trident AE+SPOT无预言机适配器 | 0.491882 | 0.766952 | 0.640564 | 0.455787 | 0.425789 |

相对OpenDetect，AUROC和OSCR分别下降 `0.033417/0.212092`，FPR95恶化 `0.105006`；只有AUPR增加 `0.005298`，四项有向平均增益为 `-0.086304`。Known F1平均差为 `-0.274245`，最差场景为 `-0.432077`。Edge-IIoT和NF-CSE套件平均增益为 `+0.281902/+0.135249`，但CIC-IoT、CIC-ToN-IoT、CICIDS2017、NF-UNSW和USTC-TFC均为负，其中CIC-ToN-IoT和USTC-TFC为 `-0.352800/-0.431962`。

14个场景全部至少一次使用回退，共141个类别回退，其中6个类别由少于10条验证样本触发；这表明结果不能表述为纯SPOT路线，官方SPOT在类别尾部小样本和不稳定分布上缺乏跨套件可靠性。八项扩展门中运行完整、拆分/泄漏、修复身份和二方法排名边界通过；Known F1保护、指标广度、总体增益和套件稳健性失败。因此 `expand_to_full102=[]`，不消耗102场景预算，不替换Pairwise。分析JSON/Markdown SHA为 `d78c7c35...3371` / `0f4da8e8...9af2`，轻量证据已同步到本地 `output/post30_audit_work/`。

### 102.3 CICIoT2022与PARROT2025边界

CICIoT2022官方35项已全部下载并通过独立完成审计：`verified_files=35`、`verified_bytes=54,912,459,271`、错误0、partial 0、symlink 0，所有tar.gz结构、PCAP魔数、XLSX CRC和文本非空检查通过，`dataset_acquisition_admitted=true`。清单SHA为 `ffd50c95...646a8`，独立审计绑定的download state/verification SHA为 `31126a64...1db` / `e3f644b6...39a1`。但18类设备身份仍有3类歧义，full flow/group扫描还受MDCG前置条件约束，所以 `dataset_identity_fully_admitted=false`、`ronetc_native_baseline_admitted=false`。

PARROT2025_mitmproxy已从Zenodo DOI `10.5281/zenodo.16368932` 下载到GPU `datasets/PARROT2025_mitmproxy/`。ZIP为2,844,079,010字节，MD5 `cbbef965...fa4f`、SHA-256 `a086ce3c...a180`，ZIP全量测试通过；归档含320个PCAP和320个SSL key文本。其80个Android应用均为安装后首次启动/正常交互流量，没有恶意攻击ground truth，因此只可用于移动应用识别、协议演进或正常域外推，不能计入恶意流量数据集数量，也不能直接支撑恶意未知攻击SOTA。

2026-07-23 13:14 UTC，活动污染矩阵为 `345/783`、当前结果根失败0、4路训练存活；历史错误缓存根的单项失败已隔离在 `pre_seed7_cache_compatibility`，不计入当前恢复矩阵。VGRF seed307仍为 `0/14`并等待污染及后效率链，确认分支也未触发。当前最优自有算法仍是CAEOS-Pairwise；Trident和M3S均为有界负基线证据，全面SOTA、最终污染鲁棒性和VGRF效果仍未成立。

### 102.4 污染矩阵中间完整性独立审计

污染矩阵运行时间较长，不能只依赖runner自写wrapper判断前349项可信。新增只读审计器 `audit_strict_v4_postselection_corruption_integrity.py`，不导入效果选择逻辑、不调用训练、不覆盖wrapper或指标，只对审计开始时已存在的wrapper形成固定快照。每项独立检查：任务必须属于冻结783任务宇宙；wrapper canonical记录SHA有效；metrics/provenance/clean anchor文件SHA与wrapper一致；污染类型、模态、强度、seed和Pairwise风险策略与provenance命令一致；输出目录唯一；污染/clean拆分指纹一致；伪未知学习声明无未知或测试标签；Known F1、AUROC、AUPR、FPR95和OSCR均存在且有限。

审计器与测试SHA为 `3321cfb8...0b6e` / `db2ff772...7756`。4项合成回归覆盖正常记录、wrapper哈希篡改、污染命令错配和拆分指纹错配，GPU Python 3.9为 `4/4 PASS`。2026-07-23 13:27 UTC正式快照在 `349/783` 时执行：349个wrapper全部通过、unique task key为349、错误0；执行结束时metrics/provenance为 `349/353`，多出的4份provenance对应活动训练，未被纳入审计。完成任务键集合SHA为 `eccdf419...c6eb`，审计内部记录SHA为 `8008dc73...c010`，文件SHA为 `0f6ec74f...5b70`，轻量副本为 `output/post30_audit_work/postselection_corruption_partial_integrity_audit_349_v1.json`。

该快照只证明已完成349项的来源、参数、拆分、无泄漏和文件完整性，不读取中间效果进行算法、条件或阈值选择，也不替代 `783/783`、最终bootstrap和所有污染家族退化门。同期最近50个完成间隔中位数约98秒；4个长任务持续占用约11至12核且有CPU时间增长，属于运行中而非僵死。VGRF仍按冻结依赖等待，不应通过放宽污染门或跳过后效率链提前启动。

### 102.5 污染完成后的自动收尾链预检

为避免783项长任务完成后才暴露汇总或调度故障，对恢复脚本、污染汇总器、后效率主张链和VGRF watcher进行了只读预检，不生成污染效果、不修改冻结协议。三个Shell脚本均通过语法检查；污染协议/汇总/runner、后效率链和VGRF现有回归共 `14/14 PASS`。污染汇总器要求恰好783个冻结任务，逐项验证wrapper canonical SHA、任务绑定、拆分、无泄漏声明以及metrics/clean文件SHA，任一缺失或错配均在写入 `summary_complete` 前失败；恢复脚本只有在并行runner和汇总器均成功后才启动后效率链。

后效率链的28个前置文件和完成标记当前全部存在，统一选择仍为 `caeos_pairwise`，选择性拓扑分支 `eligible_for_global_selection=false`，冻结污染协议SHA仍为 `83415875...e4f4`。用内存中的合成候选汇总执行协议创建函数，只验证既有源工件而不落盘，306组Pairwise/OpenDetect源记录全部通过seed、方法身份、拆分指纹、无泄漏和文件SHA检查；下游计划规模固定为3个种子、5个污染家族、1,530个配对条件。比较污染目录当前配对结果为0，满足“先冻结协议、后产生结果”的边界。

VGRF watcher锁和进程均存活，仍只等待 `strict_v4_postefficiency_claim_chain_v2/chain_complete`。其seed307协议canonical SHA为 `af4baac6...ea589`，14个试点输入、9个实现文件及CSV/config/provenance SHA全部通过。上述证据只说明从 `783/783` 到污染汇总、比较污染、最终论文就绪审计，再到VGRF试点的自动链可执行且失败关闭；当前污染仍在运行，`summary_complete`、后效率 `chain_complete` 和VGRF效果均未产生，因此不能提前声明污染鲁棒性通过、自有算法升级或全面SOTA。

### 102.6 严格准确率缺口与最终自有算法复确认链

重新读取权威 `strict_v4_comprehensive_sota_audit_v12` 后确认，不能把“28个调度前置产物存在”解释为准确率SOTA已经通过。v12仍记录正式方法数30、`post30_baseline_coverage_complete=false`、`strict_v4_confirmed_external_sota_allowed=false`。其中GSC和PRO的失败属于总协议仍绑定旧哈希：两族分别在正式指标为0时完成协议/门重冻，supersession记录逐项证明old/new protocol、gate、analysis绑定和 `metric_values_used_for_revision=false`；已有兼容审计 `3da67d2d...e503` 因此只允许将post-30基线覆盖视为兼容闭合，不能修复效果门或直接建立外部SOTA。

原Pairwise对OpenDetect的306组、102场景、seed137/139/149确认完整且无泄漏，但严格决策确实失败。Known F1非负、AUROC/AUPR bootstrap下界和四项未知指标总体均值通过；阻断项为FPR95的Holm校正显著性未通过，以及CICIoT2023、CIC-ToN-IoT和NF-UNSW等套件存在指标回退。场景阻塞主端点虽通过，只支持受限的总体优势，不等于冻结的“所有四指标显著且所有套件不回退”SOTA门。后续算法优化必须使用新的独立确认，不能修改旧审计或降低门槛。

为补齐这一逻辑缺口，新增条件式 `strict_v4_selected_external_reconfirmation_seed311_313`。设计在VGRF seed307效果和任何新OpenDetect指标出现前冻结，manifest/file SHA为 `9eeb1b48...c7e65e` / `67dcf83f...b8ea95`，新比较指标数0。只有VGRF先通过seed307试点和seed311/313全102场景确认并成为最终自有算法，才允许在相同seed311/313、7套件102场景上执行204组OpenDetect配对；若VGRF未被选择，则写入 `complete_without_claim_upgrade` 并保持准确率SOTA为false。复确认沿用原严格门：四项Unknown指标总体均值为正、AUROC/AUPR bootstrap下界为正、四项Holm p均小于0.05、所有套件四项均不回退、Known F1不下降。候选源、reference scores/evidence/provenance、OpenDetect三件套、拆分指纹和无泄漏声明均逐项SHA或语义验证。

另冻结 `strict_v4_integrated_comprehensive_sota_v1` 十门终审，manifest/file SHA为 `65a9e04e...81b4d` / `8ead0b83...f7fab`，冻结时集成审计数0。十门同时要求：post-30兼容覆盖、最终算法身份一致、新七套件严格复确认、两外部数据确认、同硬件效率、204块等价、部署门、全部原生效率优势、候选优雅退化、相对OpenDetect比较污染鲁棒性。任一失败均输出 `comprehensive_sota_not_established`，旧v12的false字段保留而不被静默覆盖。新增复确认和集成终审远端测试合计 `8/8 PASS`，Bash语法和Python 3.9编译通过；watcher PID分别为 `3352882/3792034`，各单实例且当前只等待，不占GPU。

2026-07-23 14:45 UTC污染矩阵为 `369/783`、失败0、活动锁4；新复确认指标0，VGRF和集成终审均未产生效果。当前结论仍是Pairwise为incumbent且全面SOTA未成立，但如果VGRF通过，现已具备不复用旧确认种子、不能降门、不能以单维替代的最终准确率与多维终审路径。

### 102.7 TrafficGPT/TrafficLLM准入与PARROT2025外部良性门

TrafficGPT（AINTEC 2024，DOI `10.1145/3674213.3674217`）已有官方代码，但作者随后以TrafficLLM（Computer Networks 274，2026，DOI `10.1016/j.comnet.2025.111847`）扩展为GPT-2和LLaMA-2-7B、七套加密流量数据的期刊版本。因此基线身份以TrafficLLM为准，TrafficGPT只保留为会议前身，禁止把二者重复计为两个正式方法。官方仓库分别固定在commit `9469165f...fdea7` 和 `779e752b...edb2`；完整历史bundle SHA分别为 `16f390ba...bf372` 和 `04dc36b8...f6ff6`，GPU detached checkout的tree为 `b9ee28b8...839e6` 和 `360f6900...b3385`，文件数11/17、工作区均为clean。

源码级数据流审计确认，已发布GPT-2/K-LND实现用已知训练logits计算类中心，并只把known-validation logits/labels传入 `calculate_thresholds`；`open.csv`只用于最终评估，未发现未知或测试标签直接参与阈值拟合。因此该分支保留为 `protocol_adapter_candidate=true`。但原预处理会对DC、DF和USTC合并原train/valid/test后重新切分，随后无 `random_state` 地shuffle，且没有capture/session group门；依赖和GPT-2 revision未锁定，官方评估也只给accuracy和micro/macro F1，缺AUROC、AUPR、FPR95、OSCR、配对多种子统计和同硬件效率。因此 `trafficllm_gpt2_native_main_table_admitted=false`、新增正式方法0、模型指标0；只能在先冻结packet-length/direction适配、group-disjoint拆分和严格指标层后做小型结构canary。

LLaMA分支不能直接排队。固定源码中存在 `Dataset.from_pandas(dataset)` 把CLI字符串当DataFrame、test/open原始pandas对象直接送入DataLoader、以及特征循环首批次无条件 `sys.exit()` 三类硬阻断；模型revision也未固定。故 `trafficllm_llama_native_execution_admitted=false`，必须修复后以独立命名适配器和回归测试重新准入，不能把README命令视为已复现。

机器审计器、测试和结果文件SHA分别为 `1aa290e3...dbaaf`、`a74d7f85...51277`、`1199e7b4...09f5e`；本地Codex Python与GPU Python 3.9均为 `5/5 PASS`。GPU已有USTC-TFC2016、CSTNet-TLS1.3、ISCXVPN2016和ISCX-Tor语义候选数据，但不存在审计器要求的TrafficLLM七套作者精确处理布局；官方Google Drive数据入口从GPU访问超时，所以当前不得声称原生数据就绪。

PARROT2025不作为未知恶意正样本，而新增为“外部良性移动应用域偏移安全门”。320个PCAP只允许在所有模型、特征和阈值冻结后一次性评估，报告良性误报警率、被分配恶意标签比例、单列unknown/reject率，以及相对域内良性流量的风险分布漂移；禁止用PARROT样本或标签校准阈值，也禁止把高拒识率解释为未知攻击检出率。这一设计补的是跨平台良性安全性，不增加恶意大类、细分类或全面SOTA方法数。

PARROT全量结构审计进一步关闭了输入身份缺口。审计器/测试/结果SHA为 `c3a24bab...0812c/8fe76a60...0adbb/7dc3bc2a...d8b8e`，本地与GPU均为 `4/4 PASS`。归档640个文件的canonical inventory SHA为 `21e044d8...25522`；80个应用均恰好4次抓取，320个PCAP与320个SSL key一一对应，缺失、孤立和危险路径均为0。320个PCAP全局头全部有效，统一为Linux cooked v2链路和微秒时间戳。因此 `pcap_feature_extraction_structurally_feasible=true`、`external_benign_safety_evaluation_admitted=true`，但 `training_validation_or_calibration_use_admitted=false`、模型指标仍为0。后续提取器必须显式支持linktype 276，并保持每个PCAP为不可拆分的capture group。

2026-07-23 15:33 UTC，污染矩阵为 `381/783`、当前结果根失败0，主进程继续运行；VGRF、七套件新复确认和十门终审仍在等待。TrafficLLM审计没有改变Pairwise incumbent或全面SOTA未成立的结论，也不打断冻结的污染与自有算法选择链。

### 102.8 外部泄漏门纠偏、PARROT无解密canary与正式安全设计

在外部正式指标仍为0、执行协议和汇总均未生成时，发现 `summarize_gpu_external_evaluation.py` 的泄漏门存在布尔方向错误：协议把 `unknown_or_test_labels_used_for_fit_selection_or_threshold=false` 冻结为禁止事实，汇总器却把同名字段硬置为true并纳入 `all(checks.values())`。虽然逐结果provenance加载器已要求 `unknown_or_test_metrics_used_for_configuration=false`，实际数据流仍是失败关闭的，但旧汇总语义可能同时写出“发生禁止使用”和“验证通过”，不能用于论文终审。

修复后，确认门改为正向谓词 `unknown_or_test_labels_excluded_from_fit_selection_and_threshold=true`；负向事实只在独立 `leakage_audit` 中记录为false。旧负向键一旦出现在确认门中即抛错，所有候选和OpenDetect provenance仍必须逐项显式声明未知/测试指标未参与配置。旧设计 manifest `32c52598...714e` 及文件SHA `38d1fd9d...f0281` 已原样归档；新零指标设计以 `fix_external_leakage_gate_boolean_direction_before_metrics` 为原因绑定前驱，manifest/file SHA为 `528760ae...981c` / `6ceb6fd4...6866`。新汇总器/设计生成器SHA为 `9b864716...562b` / `cce8144c...cd2`。外部与集成终审相关回归 `12/12 PASS`，冻结时 `metrics=0`、执行协议0、summary 0，因此没有结果污染或结果后改门。

PARROT无解密canary使用 `dpkt 1.9.8` 只剥离Linux cooked v2链路头，将IPv4/IPv6载荷封装到全零MAC的Ethernet头，再交给 `NFStream 6.6.0`；`n_dissections=0`、`decode_tunnels=false`，不读取320份SSL key、不解密、不做DPI。首次冻结因把列数手工预估为58而正确失败关闭；现改为逐列绑定 `configs/ustc_tfc2016_nfstream.json`，实际契约为56列，即18个体量、15个时序和23个传输特征。最终canary协议 manifest/file SHA为 `bd6e6546...ec68` / `14126f75...cc83`。

canary按“每应用最小PCAP，再取跨应用最小4个”冻结4个捕获，覆盖Sohanews、Huya Nimo、Mangatoon Comics和WMFall。共读取2,072包，其中2,028个IPv4/IPv6包转换、44个非IP包按协议跳过、解析异常0；生成455条flow。输出列序与56列契约精确一致，4个capture group和4个应用均保留，数值非有限项0，IP/MAC/OUI及应用层识别字段未写入。结果 manifest/file/CSV SHA为 `343fba16...f135` / `fe774f7a...51e2` / `6fc81407...a2a9`。独立复核14项全通过；连同外部和集成终审链，远端相关测试为 `15/15 PASS`。

该canary只证明无解密特征提取可执行，不能写成外部模型安全效果。现有OpenDetect保存 `model.pt`，但自有Pairwise/VGRF主线只保存测试证据、分数和阈值，没有保存对新流重放所需的完整分类器、模态预处理器、全部风险组件与校准器。因此新冻结的正式设计 `parrot2025_external_benign_safety_design_v1` 保持 `execution_admission=false` 和模型指标0，manifest/file SHA为 `333d4f14...7bca1` / `91a8f80f...bcdb0`；独立10项条件复核全通过，合并测试 `17/17 PASS`。

正式设计固定全量80应用、320个不可拆capture group，并选择与PARROT逐列同构的USTC-TFC2016作为源域。10个恶意家族留一场景乘seed311/313形成20个源模型场景，最终自有算法与OpenDetect共40次只读重放。主要报告良性误报警率、拒识率、已接受恶意类分配率、归一化风险分位和相对域内良性风险漂移；capture-block bootstrap为主，应用级结果只作次要描述。成功门预冻结为候选误报警率95%CI上界不超过0.10、相对域内良性增量上界不超过0.05、已接受恶意类分配上界不超过0.05、至少90%应用误报警率不超过0.20、相对OpenDetect误报警差上界不超过0.02。PARROT不得用于训练、验证、校准、特征选择或阈值选择。

正式执行仍有四个硬阻断：最终自有算法选择文件尚未生成；Pairwise/VGRF完整可部署模型包及精确重放尚未实现；全320捕获提取实现尚未冻结；域内良性参考重放尚未冻结。只有在模型和全部实现哈希先于PARROT模型输出写入执行协议后，才允许一次性运行。2026-07-23 16:04 UTC污染矩阵为 `389/783 + 4 running`、当前失败0；VGRF、外部恶意数据确认和十门终审继续等待。Pairwise仍为incumbent，PARROT模型指标仍为0，全面SOTA未成立。

### 102.9 PARROT全量提取协议与2026后续直接基线纠偏

为关闭“全320捕获提取实现尚未冻结”这一阻断，新增 `parrot2025_full_no_decryption_features_v1`。协议在任何full shard、summary和模型指标出现前冻结，manifest/file SHA为 `75325332...40d3` / `cd4a1185...ad0`，并逐项绑定协议生成器、canary提取器、full runner、汇总器和watcher的实现SHA。每个PCAP是不可拆分的独立shard；runner先写临时目录，CSV与canonical manifest全部完成后原子改名。断点续跑只接受manifest自哈希、源member/CRC、56列CSV SHA和协议SHA全部一致的完整shard；局部或被篡改shard失败关闭且不覆盖。最终汇总器独立验证320成员全集、80应用各4捕获、无多余/缺失、列序、元数据、有限值、包计数和全部文件SHA，全部通过后才原子写summary与完成标记。

协议冻结时 `shards=0`、summary 0、完成标记0、模型指标0，12项独立冻结检查全部为true；full/canary/正式安全设计相关远端测试 `8/8 PASS`。watcher PID `3331428` 只等待集成十门终审完成并连续5次观测资源空闲，之后才以 `nice=19`、idle I/O启动提取，不与当前污染、VGRF或外部复确认争用资源。该协议只补结构化特征资产，不能绕过最终模型序列化、域内良性参考和执行准入门。

同时审计两项新发现的2026直接工作。OLPFF（Information Sciences 753, 123646，DOI `10.1016/j.ins.2026.123646`）直接处理开放集长尾加密流量，使用USTC-TFC2016与ISCX-VPN，将原始包转灰度图，以ResNet18和轻量分支进行阶段式多轴融合，用manifold mixup生成伪未知并以预设分数阈值拒识。GPU两套命名数据根均存在，覆盖 `2/2`；GitHub对缩写、全标题、机制短语和DOI的4次精确仓库检索均为0。但当前只有出版社预览和Crossref身份元数据，具体10种设置的类身份、长尾比例、拆分、seed、完整包转图、阈值来源和无测试未知调参证据均未关闭。因此它是高优先级直接基线和独立长尾协议候选，不进入strict-v4主表，不启动低保真实现，不增加正式方法或模型指标。

SSRN预印本 `Open-World Encrypted Traffic Classification Based on Dual Evidence and Topological Persistence`（DOI `10.2139/ssrn.7021419`，2026-06-29）在摘要层已经覆盖侧信道时空序列、空间相似性与能量非置信双证据、EVT类别边界，以及拒识后聚类的拓扑持久性稳定度。它与当前计划在“多证据、类别边界、拓扑相关可信度”上的泛化表述重合风险高，但摘要显示其拓扑位于拒识后的未知簇稳定性，而VGRF是known-validation类别条件可靠性、场景级安全门和Pairwise精确回退。SSRN全文获取被站点自动安全验证阻断，故当前只建立 `abstract_level_novelty_watch`：禁止声称“首个双证据”“首个拓扑可信开放集加密流量方法”，但不据摘要改VGRF公式、不改变已冻结选择链，也不生成比较指标。

两项纠偏的机器审计/测试SHA为 `4b30e61d...1070` / `4ac38258...1157`，本地与GPU均 `5/5 PASS`，正式方法增量0、模型指标增量0。2026-07-23 16:55 UTC污染溯源文件已推进至 `405/783`，4个训练任务继续运行，当前结果根失败0；VGRF、七套件复确认、外部数据评估、十门终审和PARROT full提取均按依赖等待。Pairwise仍为incumbent，全面SOTA未成立。

### 102.10 UT-PAB未知发现协议分层

新增审计UT-PAB（Computer Networks 277, 112062，DOI `10.1016/j.comnet.2026.112062`）。出版社预览给出的协议不是单纯未知拒识：预训练阶段SLT使用已标注known traffic，MixTMM同时从unlabeled traffic学习字节依赖；微调阶段SUP在未标注未知流量内部按语义相似性构造prototype和pseudo-label，SSCT再用自监督对比学习强化未知簇一致性。论文目标是对未知流量进行细粒度聚类/分类，明确在最终评价前整合known与unlabeled unknown数据。

因此UT-PAB与strict-v4存在两层不可混排差异。第一，strict-v4禁止未知类进入训练、验证、选择和阈值，而UT-PAB让未知特征影响伪标签、prototype和微调损失。第二，UT-PAB的端点是多未知簇发现，strict-v4的端点是归纳式known分类加unknown拒识；出版社预览报告的overall accuracy不能替代AUROC、AUPR、FPR95、OSCR、Known F1、配对多种子显著性和逐套件非回退。

GPU已有USTC-TFC2016与ISCX-VPN，数据覆盖 `2/2`。GitHub对方法缩写+领域、全标题和DOI的4次精确仓库检索均为0；全文、作者实现、具体known/unknown类身份、未知暴露比例、包/流与byte token构造、group拆分、seed、prototype更新和完整损失仍缺。增量审计以 `5926c445...c815` 绑定前驱 `4b30e61d...1070`，测试SHA为 `15aa5c1f...9de8`；本地/GPU含前驱组合回归均 `10/10 PASS`。

当前只将UT-PAB加入“半监督未知发现”协议分层附录候选：不启动低保真实现、不进入strict-v4主表、不导入论文accuracy，执行方法总账保持42、模型指标增量0。只有取得全文或作者工件并在效果前冻结精确未知暴露、类别、拆分、预处理、指标、seed和泄漏门，才允许启动独立协议实验。2026-07-23 16:57 UTC污染为 `406/783`、4路训练、失败0，权威自有算法链继续等待。

### 102.11 Pairwise原始特征部署包canary与证据语义纠偏

为关闭“现有测试证据包不能对新流量重放”的实现缺口，新增独立 `PairwiseDeploymentBundle`，不修改已被冻结SHA绑定的 `capture_pairwise_runtime.py` 与 `caeos/pairwise_runtime.py`。部署包保存冻结的模态顺序、逐列特征契约、仅由训练known拟合的median/mean/std、类别映射、良性索引、known-validation选择的拒识阈值及完整Pairwise runtime；原始DataFrame缺列、处理器状态非有限、输出形状错误或输出非有限均失败关闭。旧两文件SHA仍分别为 `8b7cab01...509df/a0f226d1...dc6ae`。

首次v1 canary虽完成精确重放，但证据字段错误写成 `contains_training_rows=false`。Pairwise runtime中的KNN、LOF和类别条件KNN会在拟合状态内保留参考特征向量，因此该说法不准确。v1目录原样保留但被取代，不得用于正式部署主张；机器可读supersession SHA为 `23b445e4...b25e`。v2明确区分：不保存原始输入行；保存拟合后的非参数参考向量和类别条件状态；不保存validation/test标签；工件策略为 `gpu_private_do_not_publish`。这也是部署包不能同步到公开代码仓库的原因。

v2低资源结构canary使用CIC-ToN-IoT `mitm`、seed7、每类最多100、10棵树和单作业。部署工件为1,612,725字节，SHA `c3751015...9928`；冻结79列、3模态、9个known类，特征契约SHA `3e50005b...6c12`，风险为 `cauchy_modality_support_union`，阈值 `0.8688524590163933`。训练器原样运行约33.92秒，其中总拟合约31.90秒；这些时间只描述canary执行，不进入正式效率比较。

捕获阶段验证221条无标签测试输入的closed prediction、risk、rejection和threshold均与源运行逐数组相同，序列化往返也完全一致。独立审计再验证工件、输入、期望输出和等价记录的SHA，重新加载后检查closed prediction、probability、risk、rejection四类输出，连续两次重放完全一致，且拒识严格等于 `risk > threshold`。capture manifest、部署工件和独立审计SHA分别为 `8c766378...8db4/c3751015...9928/4f08ec42...f579`；本地Pairwise相关回归 `22/22 PASS`，GPU为 `27/27 PASS`。canary的 `formal_model_metrics_admitted=0`。

这一步只证明Pairwise原始实现可以被封装为可重放的GPU私有部署工件，尚未关闭PARROT正式执行。canary是CIC-ToN-IoT 79列契约，而PARROT冻结的是与USTC-TFC2016同构的56列契约；最终算法仍未由VGRF选择链确认，也没有10个USTC家族乘seed311/313的20个正式源模型包和域内良性参考。因此PARROT `execution_admission` 继续为false，不得用该canary直接评分320个PCAP，不得把结构重放等价写成外部效果或全面SOTA。2026-07-23 17:13 UTC污染链为 `412/783` provenance、`408` metrics、4个实际训练任务、失败0，summary仍未生成；Pairwise保持incumbent，全面SOTA仍未成立。

### 102.12 USTC-PARROT逐列部署契约canary

在不启动20个正式模型包的前提下，新增一个USTC-TFC2016结构canary验证部署捕获器能否产生PARROT所需的56列接口。试验使用Miuref留一、seed7、每类最多100、10棵树、单作业和capture-grouped拆分；这是低资源接口验证，不是seed311/313正式效果试验。捕获约39.33秒，总拟合约36.57秒，部署包1,228,483字节、SHA `7f04c522...b6cea`。

部署包冻结56列、3模态 `volume/timing/transport`、10个known类，特征schema SHA为 `a0b4a602...c3b6`，源配置SHA为 `36051212...b5ac`。风险仍为 `cauchy_modality_support_union`，known-validation阈值 `0.9101123595505616`。265条无标签重放输入的closed prediction、probability、risk和rejection经源等价、序列化往返、独立重复推理和阈值关系全部通过；capture manifest、独立部署审计SHA分别为 `59e31c99...c387c/4c26ac7d...cdab`。

另新增独立逐列契约审计器，不依赖捕获脚本的结论。它同时读取部署包、`configs/ustc_tfc2016_nfstream.json` 和冻结的PARROT full协议 `75325332...40d3`，验证三个来源的56个列名及顺序完全一致，并核对配置SHA、不可拆capture group、不解密、不DPI、不读SSL key，以及PARROT不得用于训练、验证、校准、阈值/特征选择或生成模型指标。真实审计结果SHA为 `ce45915d...d64cc`，审计器/测试SHA为 `85579c09...385d6/91e54a12...2990`；Pairwise相关本地回归 `24/24 PASS`、GPU `29/29 PASS`。

因此阻断由“Pairwise是否存在56列可调用接口”缩减为正式身份与规模问题，但外部执行仍不准入：最终自有算法尚未完成选择，当前包只覆盖Miuref seed7的低保真状态，缺少10家族乘seed311/313的20个全规模源模型、OpenDetect对应包和域内良性参考；PARROT full shard与summary也仍为0。`formal_model_metrics_admitted=0`、`formal_external_execution_admitted=false`。2026-07-23 17:31 UTC污染链为 `414/783` provenance、`411` metrics、4路训练、失败0，summary未生成；不得把契约通过写成PARROT误报门通过或全面SOTA。

### 102.13 VGRF可部署包装器与稳定尾秩兼容诊断

VGRF的部署状态不能只保存最终风险数组。其推理需要在Pairwise的逐模态概率、全局概率、原逐模态融合概率和gate之上应用known-validation拟合的类条件可靠性矩阵，再由known-validation安全门决定启用VGRF或精确回退Pairwise。因此新增独立 `VGRFDeploymentBundle`，保存Pairwise部署包、类条件可靠性、场景级门决策、VGRF阈值和risk blend；不修改原Pairwise runtime、类条件可靠性公式或VGRF门公式。

首次VGRF构建正确失败关闭：概率、closed prediction和rejection均逐数组一致，但risk不完全相同。根因是训练证据包保存原始不连续经验尾秩，冻结PairwiseRuntime为解决连续运行并列不稳定而使用稳定并列尾秩。首次尝试没有生成可准入工件，失败日志保留。为避免用容差掩盖差异，Pairwise捕获升级为schema v3，额外保存不含标签的processed validation inputs和expected outputs；USTC v2 canary对265条test及177条validation重放均精确通过，manifest/artifact/audit SHA为 `8881eb92...33795/54a26815...5f3eb/96adeca6...100b6`。

VGRF v2使用稳定PairwiseRuntime分别重放known validation与test，在known-validation标签上重新计算同一可靠性矩阵、门和95% higher阈值。构建脚本从scores归档只访问 `validation_labels`，不读取其中test labels/test unknown；部署包不保存validation/test标签，只保存可靠性状态和门的聚合统计。工件1,254,766字节，SHA `d6318d23...6bc47`；capture manifest和独立审计SHA为 `97143f04...27bc3d/aa5f57ee...c94d8`，门启用，部署阈值 `0.7863197403350819`。

源评估器与稳定部署运行时的兼容审计结果为：known-validation门决策相同、test probability逐数组相同、source/deployment阈值完全相同；test risk最大绝对差 `0.026930980331066057`。该风险差没有被声明为数值等价，而被固定为并列尾秩策略诊断，兼容记录SHA `22eb7d20...edc6f`。部署内部以稳定运行时为权威，265条无标签输入的probability、prediction、risk、rejection、序列化往返和重复推理全部精确一致。尝试历史SHA为 `f0d81719...6ff6b`；本地Pairwise/VGRF相关回归为 `25/25 + 8/8 PASS`，GPU为 `30/30 + 8/8 PASS`。

当前只建立“若VGRF最终被选中，则可生成56列可部署工件”的结构证据。它不证明seed307 pilot或seed311/313全102确认通过，也不提供PARROT效果；正式执行仍需等待最终选择文件，并为10个USTC家族乘seed311/313生成20个全规模包后逐一做同类审计。`formal_model_metrics_admitted=0`、`formal_external_execution_admitted=false`。2026-07-23 18:11 UTC污染链 `425/783` provenance、`421` metrics、4路训练、失败0，summary仍未生成；Pairwise仍是incumbent，全面SOTA未成立。

### 102.14 条件式20个USTC正式部署包的结果前冻结

为避免最终自有算法选择完成后临时挑选场景、种子或部署实现，新增条件式正式模型包链。设计在 `final_selection.json`、任何正式包记录和模型工件产生前冻结，覆盖USTC-TFC2016的 `cridex/geodo/htbot/miuref/neris/nsis_ay/shifu/tinba/virut/zeus` 10个留一恶意家族及seed311/313，共20个包。每个包复用冻结seed7来源的同一CSV、配置、场景与训练超参数，只允许改变训练seed、输出目录和风险策略；Pairwise分支强制capture schema v3，VGRF分支还必须绑定full102阳性确认参数并逐场景从known-validation重新构建可靠性状态。

设计协议canonical/file SHA为 `359e0044...1899/67890dd5...a6e8`。独立复核确认状态为 `frozen_before_final_selection_and_package_artifacts`，20个包、10个场景、种子311/313、56列有序PARROT契约，冻结时 `package_records=0`、`deployment_artifacts=0`。runner只有在Pairwise/VGRF最终二选一文件为canonical后才运行；每个包必须依次通过Pairwise独立重放、被选算法独立重放、PARROT逐列契约及工件SHA门，最后才原子写入 `package_record.json`。汇总必须恰好收到20个哈希有效记录，缺一项即失败关闭。

本地和GPU上的正式包/契约新增回归均为 `8/8 PASS`，VGRF部署回归另为 `8/8 PASS`。远端watcher PID `569002` 当前只等待最终选择与连续5次GPU/实验空闲观测，随后才以 `nice=19`、idle I/O串行执行；它不会在现有污染任务运行时启动模型包训练。PARROT原始归档已经位于 `/opt/data/private/wangwt/ParkAttackKE/datasets/PARROT2025_mitmproxy/PARROT2025_mitmproxy.zip`，大小2,844,079,010字节，既有冻结协议记录80个应用、320个PCAP；但full feature shard和summary仍为0。

2026-07-23 18:26 UTC污染链已推进至 `429/783 provenance`、`425` metrics、4路训练、当前结果根失败0；污染summary、后效率chain、VGRF最终选择、20个正式模型包和PARROT full提取均未完成。因此当前最优已确认自有算法仍为Pairwise，VGRF是必要且受控的候选探索；论文可写方法、协议、部署可行性和负结果，仍不得写全面SOTA、最终VGRF胜出或PARROT外部效果成立。

### 102.15 污染矩阵428项完整性复审与剩余任务分布

2026-07-23 18:38 UTC对当前已完成污染前缀重新运行独立只读完整性审计。审计固定开始时的428个wrapper，逐项复算冻结任务成员、record SHA、metrics/provenance/clean anchor SHA、污染命令、拆分指纹、Pairwise风险策略、无泄漏声明及五项有限指标；结果为 `428/428 PASS`、任务键唯一、错误0，审计过程中没有新增wrapper混入。审计记录/file SHA为 `63d21107...6da1/67f73978...f0eb`，审计器SHA仍为 `3321cfb8...0b6e`；`effect_metrics_used_for_selection_or_adjustment=false`，该复审不读取中间效果改变算法、场景或阈值。

新增只读进度汇总器，从冻结783任务宇宙与哈希有效wrapper计算完成、启动未完成和剩余分布，不读取任何效果值。实现SHA为 `ce7457d0...1175`，本地新增测试 `2/2 PASS`，GPU新增及既有污染协议/runner/summary组合 `11/11 PASS`。18:40 UTC真实进度记录/file SHA为 `f7416ed0...c867/035b314f...7135`：完成429项，占54.79%；273个sentinel已全部完成，full102完成156项；剩余354项全部属于full102，当前4个启动未完成任务均为CIC-IoT2023最后场景 `xss` 的四个污染族。

剩余任务未出现污染族缺口：feature shuffle、field missing、Gaussian drift和row missing各71项，modality missing 70项。按套件剩余为CIC-IoT2023 4、CIC-ToN-IoT 45、CICIDS2017 70、Edge-IIoT 70、NF-CSE 70、NF-UNSW 45、USTC-TFC2016 50。四个活动训练器在连续20秒观测中CPU累计时间均显著增加，属于运行中而非僵死；父并行runner和全部下游等待器仍存活。

观测结束时为 `433 provenance/429 metrics + 4 running`、当前结果根失败0。该分布只证明任务覆盖与运行健康，不证明污染退化门通过；必须等待783/783后重新执行全量完整性、bootstrap、套件均值和五污染族退化审计，再允许后效率、VGRF、外部复确认和十门终审继续。Pairwise仍为incumbent，全面SOTA未成立。

### 102.16 TrafficLLM严格适配的数据谱系失败门

现有TrafficLLM原生准入审计曾将GPT-2/K-LND保留为协议适配候选，但候选能否执行仍取决于作者输入和strict-v4捕获组能否同时闭合。对GPU现有 `/datasets/CrossPlatform/Datasets/USTC-TFC-2016` 做新增机器审计后确认：完整、train和test目录的12类身份一致，确定性样本为 `(1,1600)` 的 `uint8` 数组；但TrafficLLM官方commit `779e752b...edb2` 的USTC入口要求 `X_train/y_train/X_valid/y_valid/X_test/y_test.npy` 六个聚合文件，并对每个样本调用字符串 `.replace()` 预处理。

候选目录在根、balanced目录和split目录均不存在上述六个聚合文件，立即可见的CSV/JSON/Parquet组sidecar为0；样本文件名也不含 `CaptureGroup`、capture或 `window_` 标识。其单流数组既不能直接输入官方字符串预处理器，也不能证明与原始PCAP或strict-v4 `PCAP::window`组的一一对应关系。因此不得把CrossPlatform或可能的MApps派生布局称为TrafficLLM作者原生数据，不得按单流随机拆分绕过group-disjoint门，也不得仅凭12类和1600维外形相似启动低保真实现。

审计manifest/file SHA为 `b240b86c...b375/1803c49d...ccdf`，实现/测试SHA为 `c2e8813d...a523/74132a9d...5a4d`；本地和GPU均 `2/2 PASS`，独立canonical哈希复核通过。决策为 `strict_v4_protocol_adapter_execution_admitted=false`、新增模型指标0、正式方法增量0。重新准入至少需要：作者兼容的字符串聚合输入及文件SHA；每个样本到源PCAP/会话的不可变组映射；效果出现前冻结GPT-2模型/tokenizer revision和依赖锁。

该负门执行了“继续补充高保真基线”而没有把方法数量当目标：42方法总账保持不变，TrafficLLM继续作为领域直接但数据谱系未闭合的适配候选。同期污染矩阵已推进至 `454 provenance/450 metrics + 4 running`、当前失败0；Pairwise仍为incumbent，VGRF和全面SOTA结论继续等待权威主链。

### 102.17 VGRF全确认结果链的结果前加固

在seed307试点分析、seed311/313全确认协议和最终选择文件均未产生时，完成VGRF全确认链的静态审计。原链虽然检查试点分析字段和全确认协议SHA，但阳性试点没有在分支入口重新计算；已存在的候选结果也只依赖协议SHA复用；最终汇总未逐项复验候选身份、冻结参数、输入文件SHA、无测试标签泄漏和任务全集。这些缺口不会改变尚未产生的结果，但若不在结果前修复，可能让篡改或陈旧结果进入最终算法选择。

修订后的确认协议生成器必须从冻结的seed307输入和实现确定性重算pilot analysis，并要求与磁盘分析逐字段相同、所有pilot门为真且决策明确为进入full confirmation。全确认runner对新生成和断点复用的参考训练及候选统一执行独立验证；汇总器再次验证参考训练task/command/provenance、CSV/config/训练器SHA，候选schema、canonical protocol、冻结参数、evidence/scores SHA、gate一致性、禁用时对Pairwise的精确回退、无测试标签/测试未知使用、有限指标，以及恰好204个唯一任务、7个套件、seed311/313全集。任何一项不满足均失败关闭；只有204项和全部预冻结效果门同时通过，才整体选择VGRF，否则整体保留Pairwise，不允许按套件挑选。

新增验证模块、协议生成器、runner、汇总器、分支脚本和回归测试SHA分别为 `059b6808...c2f5/c89a67d1...d0ce/d8b8758b...31c3/00a4e6bd...4fa8/31cad9b0...4e5a/8a2a6c5d...a484`，本地与GPU逐文件一致。新增加固回归两端均 `6/6 PASS`；GPU既有确认分支 `8/8 PASS`、VGRF核心 `3/3 PASS`，Shell语法检查通过。seed307冻结实现和活动等待脚本没有修改；watcher PID `2444019` 仍只等待上游完成。

2026-07-23 19:28 UTC只读复核为 `490 provenance/486 metrics + 4 running`。污染summary、VGRF试点analysis、全确认protocol及最终selection均不存在，因此本次工作只加固未来证据链，正式方法指标增量0。当前最优已确认自有算法仍为Pairwise；VGRF保持必要候选，但不得声明VGRF胜出、七套件复确认通过或全面SOTA成立。

### 102.18 最终readiness的post-30兼容性死锁修复

对污染完成后的完整调度链做静态复核时发现，原 `audit_strict_v4_final_paper_readiness.py` 仍硬性要求综合SOTA v12中的 `post30_baseline_coverage_complete=true`。权威v12审计有意保留该旧字段为false，GSC与PRO的结果前协议重冻只通过独立 `supersession_compatibility_v1.json` 修复身份绑定。因此原post-efficiency链即使完成全部污染、效率和比较实验，也会在最终readiness入口失败；`chain_complete`不会产生，seed307 VGRF试点及全部后续链会永久等待。

修复不修改v12审计、旧readiness审计器或正在运行的污染恢复脚本，而新增独立 `strict_v4_final_readiness_post30_compat_protocol_v1`。协议在readiness输出和chain marker均为0时冻结，要求compatibility的old audit file/manifest与现行v12逐项一致，`post30_baseline_coverage_compatible`、7个未受影响分支及GSC/PRO两个superseded分支全部通过。compatibility只能把基线覆盖身份门判真；七套件准确率、同硬件效率、204块等价、部署门、候选退化和相对OpenDetect污染门继续读取原效果证据，任何一项失败都不能被替代。

真实协议canonical SHA为 `1c4126b7...9d96b`；新审计器、协议生成器、watcher和测试SHA分别为 `05d28048...945f/53bab86e...5963/ebba5eca...b8df/b28d1d55...3eeb`，本地与GPU一致。两端新增回归均 `3/3 PASS`，GPU Shell语法通过。watcher PID `3485890` 当前只等待既有efficiency v5、optimized v6、tensorized分支、污染summary和比较污染summary；完成后生成兼容的readiness v4并写入原chain marker，不启动或重复任何训练。

本次复核同时暴露下一项集成门：现有base readiness的效率证据属于Pairwise；如果最终VGRF胜出，集成终审不得直接继承Pairwise效率门。后续integrated audit v2必须要求“最终算法与效率证据算法一致”，VGRF分支需补204块同硬件等价、延迟/吞吐、训练开销和工件体积证据。该门尚未完成，因此即使旧integrated v1未来产生阳性文件，也不能单独授权全面SOTA。当前新增模型指标0，主结论不变。

### 102.19 Integrated SOTA v2的最终算法系统证据一致性

原integrated v1虽然核对最终选择与七套件复确认、外部数据所写算法一致，但六个系统门直接继承base readiness。base readiness由Pairwise的效率、204块等价、部署、候选污染和Pairwise-vs-OpenDetect比较污染产生；若VGRF最终胜出，v1可能把Pairwise系统证据错误归给VGRF并形成假阳性综合结论。该问题与效果高低无关，是最终算法身份和证据对象不一致。

新增 `strict_v4_integrated_comprehensive_sota_design_v2` 在最终选择、外部结果和集成审计均为0时冻结，并明确supersede v1最终主张。Pairwise路径只允许消费 `base.selected_algorithm=caeos_pairwise` 的系统门，禁止额外summary替换。VGRF路径必须提供canonical `strict_v4_vgrf_selected_system_confirmation_summary_v1`，算法身份为VGRF、validation全通过、204个全输入等价块、1530个相对OpenDetect比较污染条件，以及同硬件效率、部署、优雅退化和比较鲁棒性六门全部为真；缺summary、计数不符或任一门失败均不能生成全面SOTA阳性。

对1530计数的源码复核确认其语义为306个候选/OpenDetect同拆分源对乘5个确认污染族；306源对来自102场景乘3个冻结源种子，并先在场景内聚合种子。它不能由seed311/313的204项VGRF准确率确认直接替代。未来VGRF system协议仍需在任何系统结果前冻结第三源种子、精确模型/拆分/工件SHA、污染条件及同硬件计时实现；当前只冻结集成消费契约，没有生成这些效果。

integrated v2 design canonical SHA为 `0bdc581a...bb16`；auditor/creator/watcher/test SHA为 `c82265c8...c661/d7131ad7...bc57/cbaf086c...8a14/2bdb94b9...1951`，本地与GPU新增回归均 `4/4 PASS`，GPU Shell语法通过。watcher PID `3543948` 当前等待兼容readiness、最终选择、外部数据和复确认；若Pairwise胜出则使用Pairwise base，若VGRF胜出则继续等待VGRF专属system summary。integrated v1即使先产生文件也不再授权最终论文主张。

### 102.20 VGRF专属system分支的结果前设计与准备

为避免VGRF胜出后再按结果选择系统实验规模，新增conditional `strict_v4_vgrf_selected_system_confirmation_design_v1`。设计绑定102场景coverage、integrated v2、Pairwise正式效率v5、已冻结污染协议和seed307 VGRF pilot。准确率选择与系统效率固定使用seed311/313，因此运行时等价规模为102场景乘2种子等于204块；比较鲁棒性再加入结果前确定的第三源种子317，规则为“严格大于313的最小素数”，不是按效果选择。因此比较源对为102乘3等于306，沿用五个full102污染族后恰为1530项。

同硬件效率沿用既有正式协议的batch `1/64/512`、5次预热、30次计时，并交替VGRF/OpenDetect顺序。必须计完整forward与risk transform，禁止只计 `scores.npz` 后处理；204块逐一验证probability、prediction、stable risk和rejection，原经验尾秩差继续只作诊断。训练/校准效率使用既有每套件一个coverage-SHA sentinel、seed311/313共14对，报告训练、校准、总拟合、GPU/RSS和部署工件体积。任何延迟、吞吐、训练成本或工件CI门失败均报告负结果，禁止按指标混合运行时。

比较污染严格复用现有五族、固定severity、coverage-SHA模态规则和corruption seed211。306个VGRF/OpenDetect同拆分源对乘5族形成1530项，先在场景内平均3种子，再做20,000次bootstrap及每族6指标Holm校正；六指标为Known Macro-F1、AUROC、AUPR、FPR95、OSCR和ECE。准确率确认204项不能替代这1530项，Pairwise污染结果也不能改名为VGRF结果。

system design canonical/file SHA为 `080196a0...abf7/dde16d26...b8b4`，creator/test SHA为 `51804d09...bfaf/186317a0...0a65`，双端 `4/4 PASS`。另冻结preparation canonical/file SHA `311a8b13...8abc/331a989e...4e3e`，绑定validator/creator/watcher/design creator SHA `b53bbfcf...67d9/5102188b...36ee/c743a137...c45a/51804d09...bfaf`，双端 `6/6 PASS`、GPU Shell通过。

条件watcher PID `3707385` 当前只等待最终选择：Pairwise胜出则写canonical `not_required` 并完成；VGRF胜出则先写design/selection/confirmation绑定的 `execution_required`，只有收到204/1530计数、无泄漏、禁止拼接且六门结构完整的summary后才写branch marker。结构完整的负效果允许完成分支，但 `all_system_gates_pass=false`，不能授权全面SOTA。当前summary、execution-required、not-required和branch marker均为0；仍需实现preparation列出的execution protocol、seed317源runner、双运行时capture、同硬件benchmark、比较污染runner和system summarizer，故本节不是效果完成声明。

### 102.21 VGRF系统执行面的306源计划、部署捕获与污染runner

在最终选择和VGRF系统指标均未产生时，完成execution protocol creator。它只在canonical VGRF最终选择及full102确认通过后准入，同时要求selected external reconfirmation已经完成且结构验证通过；外部复确认的效果可以为负，负值会原样写入claim boundary并继续作为集成SOTA失败门，不再因负效果造成system分支死锁。creator逐项复验204个VGRF/Pairwise冻结源的metrics、scores、evidence、provenance及输入绑定，并绑定204个OpenDetect的metrics、scores、provenance和 `model.pt`。第三种子317按102个场景预登记CSV/config/unknown class、Pairwise来源provenance、seed311 OpenDetect命令模板及输出根，形成恰好306个唯一身份；任何缺失、重复、SHA漂移、泄漏声明或冻结前结果都会失败关闭。creator/test SHA为 `a8ba3f29...f027/50a89d20...5350`，本地与GPU为 `8/8 PASS`。

静态审查同时发现原seed311/313 VGRF runner直接调用Pairwise训练脚本，却没有先写验证器必需的 `provenance.json`，因此未来首个新参考训练完成后会确定性失败。修复后runner在训练前使用统一 provenance API同时冻结task、完整command、输入和代码身份，断点恢复也必须逐字段一致；seed317 runner采用同一机制，只替换seed、输出目录和已冻结risk policy。修复后的full runner与seed317 runner SHA为 `0a4f2b4a...be06/7d611c9a...75b6`，GPU相关VGRF组合回归 `18/18 PASS`，未启动新增训练。

新增OpenDetect部署对象、捕获器和独立审计器，SHA为 `7cc32f6a...b688/d9c267d2...00c8/31dcb8a2...4901`。部署对象从真实 `model.pt` 恢复完整OpenDetect前向和 `negative max class-conditional KL logit` 风险变换，绑定同拆分的无标签多视图输入、known-validation阈值、模型/config SHA；源prediction、risk和rejection必须在1e-12边界内一致，probability执行序列化往返和重复推理精确审计。GPU合成模型真实捕获与独立审计 `1/1 PASS`，不是仅对 `scores.npz` 做后处理。

306组部署捕获runner对每个源在隔离目录中确定性重训并捕获Pairwise schema v3、构建VGRF v2、恢复OpenDetect部署对象，三者分别独立审计；Pairwise重训的probability/prediction/risk/rejection还必须与冻结源逐数组相同，VGRF重建的prediction/risk/rejection必须与冻结源相同。捕获runner SHA为 `9213218b...e04e`，GPU捕获辅助回归 `3/3 PASS`。204块同机推理runner SHA为 `ed862f29...5d28`，固定batch 1/64/512、5次预热、30次计时并逐重复交替方法顺序，完整计入forward、risk和rejection，双端纯逻辑回归 `3/3 PASS`。

比较污染evaluator/runner SHA为 `ca8f604d...f5b0/75c1f059...8e71`，严格复用coverage SHA决定的模态、五个冻结家族、severity和seed211。每个306源对重建同一确定性拆分，要求捕获test数组与重建数组完全一致，再对VGRF/OpenDetect施加相同污染并只用test标签计算最终Known F1、AUROC、AUPR、FPR95、OSCR和ECE退化；总条件固定1530。两端新增逻辑回归 `3/3 PASS`，GPU execution/corruption组合 `11/11 PASS`。

当前这些是可执行实现，不是正式效果：execution protocol文件仍需等待最终选择与204个OpenDetect复确认源，seed317、306部署包、204基准块和1530污染结果均为0。还缺7套件sentinel×2种子×3 clean-process的VGRF/OpenDetect训练/校准效率runner、最终system summarizer及watcher自动串联，不能写六个system gate通过。2026-07-23 20:40:54 UTC污染链为 `514/783 metrics`、`518 provenance`、4路训练、失败0；Pairwise仍为当前incumbent，VGRF仍是受控候选，全面SOTA未成立。

### 102.22 VGRF专属训练效率、系统汇总与自动执行链闭合

补齐7套件sentinel、seed311/313、每对3个独立clean-process的训练/校准效率runner，总规模固定为14对、42块。每块重新执行Pairwise训练和VGRF known-validation校准，并在独立目录重新执行OpenDetect训练；报告特征准备、训练、校准、总拟合、峰值GPU显存、峰值主机RSS和序列化部署工件7项成本。Pairwise部署捕获新增Linux进程峰值RSS，VGRF端把Pairwise训练与后续VGRF构建子进程的峰值取最大并写入独立资源计时manifest，避免只计主训练而漏掉校准构建。训练runner/test SHA为 `5569b22f...f471/b9da8093...6ed2`，Pairwise部署捕获SHA更新为 `bc982eb8...7e2e`。

同机benchmark现在为每个204块写入canonical manifest SHA，断点续跑同时验证protocol和块自身SHA；矩阵启动前冻结硬件记录并要求GPU独占，runner SHA更新为 `1bbda97f...09de`。306捕获runner把VGRF源经验尾秩风险差严格限定为诊断，只要求源closed prediction、门决策和probability一致，同时继续要求稳定部署内部probability、prediction、risk、rejection四输出精确重放，SHA更新为 `9336c07b...b623`。这两项修订取代102.21中的旧capture/benchmark SHA，不改变算法公式或冻结效果门。

新增system summarizer `be287f7d...a392`，逐项复核306捕获、42训练、204同机运行时和1530比较污染产物及其SHA。训练门以14对各3次中位数做20,000次配对bootstrap，7项成本比上界均不得超过1；运行时门要求各batch延迟比上界不超过1、吞吐比下界不低于1、工件比上界不超过1，并要求训练与运行时硬件身份完全一致。比较污染先在102场景内平均3种子，再对六指标执行bootstrap、Wilcoxon及Holm，要求总体均值为正、置信下界为正、校正显著且每个套件均值非负。汇总器只生成同一VGRF身份的六门canonical summary，任一负门原样保留并阻止全面SOTA，不做套件、指标或运行时拼接；summarizer/test SHA为 `be287f7d...a392/ba2b7b78...1913`。

execution creator同时绑定既有污染protocol及其中冻结的优雅退化阈值，creator/test SHA更新为 `a3f8ca41...25f8/3923e426...560f`。自动脚本SHA `6242cadf...bff4` 固定执行顺序为seed317源补齐、306部署捕获、42训练效率、204同机基准、1530比较污染、system汇总；只有最终选择为VGRF且全部来源就绪后才冻结execution protocol，并在连续5次GPU及实验进程空闲后以 `nice -n 15`、idle I/O串行运行。Pairwise胜出时直接退出而不运行VGRF系统实验。watcher顺序/门测试SHA为 `81589772...dc1e`，本地和GPU均 `4/4 PASS`；远端相关实现组合回归另为 `29/29 PASS`、Shell语法通过，关键文件本地/GPU SHA一致。远端独立watcher PID为 `580542`，当前状态是等待最终算法选择，未启动新增训练。

2026-07-23 21:06:59 UTC只读快照为污染 `526/783 metrics`、`530/783 provenance`、4路训练、当前失败0，最终选择仍不存在。因此本节闭合的是结果前执行能力，不是效果结论：execution protocol、seed317正式结果、306部署包、42效率块、204基准块、1530比较污染项和system summary仍均为0；Pairwise继续作为incumbent，VGRF是否替换、六个system gate及全面SOTA仍必须等待真实结果。

### 102.23 TAO-Net 2026直接领域基线的代码与协议准入审计

2026文献刷新发现TAO-Net是当前总账尚未单列、且与开放世界加密流量直接相关的压力测试基线。论文已发表于Neurocomputing 679 (2026) 133170，DOI为 `10.1016/j.neucom.2026.133170`；[arXiv全文](https://arxiv.org/abs/2512.15753)与[作者仓库](https://github.com/WaIdo/TAO-NET)均可核验。作者代码固定到commit `a1574f38741772ac79628131f9fbef8a7c78374a`，168个tracked文件、工作树干净；论文PDF为6,613,141字节，SHA `9aea18ac...ef491`。由于Windows/Linux换行不同，首版协议误用工作树原始字节SHA，远端首次审计在README身份门失败并停止；在任何模型指标产生前将旧协议 `77622490...cb2a4` 原样归档，新协议改用跨平台Git blob内容SHA，并显式记录supersession。

论文协议与strict-v4并不相同。TAO-Net在CHNAPP、ISCXVPN和ISCXTor上分别使用4/2、9/4、8/4个ID/OOD类；训练集只有ID，但validation和test都按7:3混入ID/OOD。Strict prompt还把OOD候选标签集合直接提供给生成分支，最终报告Macro Precision、Macro F1、Micro F1和Recall。论文写明hybrid参数为 `alpha=0.6`、`delta=0.75`；而公开代码默认 `threshold-method=youden`，先用test标签划分ID/OOD，再把同一test的两组分数同时用于阈值搜索和最终评估。该默认实现的测试阈值泄漏不能进入strict-v4；论文固定delta也不能在缺失配置时由我们自行推断其来源。

公开仓库README明确说明最终实验配置、预处理数据校验manifest和部署脚本尚未发布。机器审计进一步确认Stage-1只实现CHNAPP别名 `Tinghuaall`，并把 `processed_valid.json` 合并到训练；三套Stage-1 processed split、三套PacRep train/valid/test以及三份BERT预训练权重共15个引用工件全部缺失，即 `0/15`。GPU存在ISCXVPN和ISCXTor原始归档候选，逐冻结文件大小复核为 `2/3`；CHNAPP根不存在。CrossPlatform下虽有VPN/Tor派生JSONL，但作者仓库没有对应dataset/checksum manifest，禁止把其命名相似性当作TAO-Net原生数据，因此精确论文预处理覆盖仍为 `0/3`。

第二版Git-blob协议虽修复跨平台SHA，但把“原生复现”和“strict-v4主表比较”错误绑定为同一组门；它及对应审计均在模型指标为0时归档，file/canonical SHA分别为 `cfce7379...20db4/1b7b4ed2...e657c` 和 `f8828560...712e6/2662d68d...73a9d`。当前权威协议将两组门禁分离：原生执行只检查官方身份、阈值身份、发布配置、执行工件和三套精确预处理数据；strict-v4主表再独立检查任务、指标、未知暴露、候选标签可见性和无测试标签选阈值。当前协议file/canonical SHA为 `fe426d49...7095a/e70c7e5d...41fd2`，远端审计file/canonical SHA为 `f81c5449...7ad1/1b744bec...c98e`；creator/auditor/test SHA为 `11ffddfc...0d93/347247c4...d3e0/ceb458dc...0473`，本地与GPU均 `6/6 PASS`。离线Git bundle为2,288,217字节、SHA `364bbc3f...c0fa1`，远端checkout的HEAD/origin/tracked/status均独立复核。最终判定为 `paper_contract_admitted=true`、`official_source_snapshot_admitted=true`、`native_execution_admitted=false`、`strict_v4_main_table_admitted=false`、`appendix_protocol_candidate=true`、`model_metrics_generated=false`、方法数增量0。TAO-Net可以在相关工作和协议分层附录中作为2026直接SOTA压力测试，但当前不得写成本地复现，也不得用论文96%级指标与strict-v4五指标直接排序。

2026-07-23 23:54:10 UTC污染链已推进至 `683/783 metrics`、`687/783 provenance`、4路训练、失败0；最终算法选择、branch-complete标记和VGRF system summary仍不存在，PID `580542`存活并继续等待。TAO-Net审计不抢占GPU、不改变Pairwise incumbent，也不改变“全面SOTA尚未成立”的边界。

### 102.24 k-LND直接领域基线的无泄漏适配与零结果冻结

k-LND来自Computer Networks 236 (2023) 109991，DOI为 `10.1016/j.comnet.2023.109991`；论文提出在深度分类器logit空间执行的k-LND1/2/3，并在AWF、DF、DC、SETA和IoT五套加密流量数据上评估。官方仓库固定到commit `673320b86dcaf72dcdeae5159b3b8ce91ac5e19c`，219个tracked文件、工作树干净；论文PDF与离线Git bundle SHA分别为 `dd64018f...e52a/3cac6a8d...ed9e`。官方五个关键notebook使用canonical Git blob内容SHA绑定，消除了Windows CRLF和Linux LF造成的身份漂移。

适配严格遵循论文方法定义而非复制单个notebook的偶然差异。每个已知类中心只由正确分类的known-training logit均值构建；原生距离阈值只来自正确分类的known-validation。k-LND1使用预测类距离，k-LND2使用其他类相对预测类的距离差之和，k-LND3使用预测类距离与其他类距离和的比值。Strict-v4统一规定风险越大越未知，因此k-LND2取 `risk=-D2`；其90%高尾风险阈值等价于官方大类notebook的10%低尾D2规则。DC notebook对三种距离均采用0.9索引等实现不一致不被带入适配器，公式和方向均在协议中显式冻结。

执行层冻结既有strict-v4 MLP，不重新训练网络，只在其known-training/known-validation logit上拟合k-LND；unknown/test不参与中心、原生阈值、部署阈值、邻居数或场景选择。由于strict-v4已知类规模有限，邻居固定为全部其他已知类，不做OOD调k。覆盖SHA与官方commit在效果前确定每套件2个场景，共7套件、14场景；三种k-LND同时运行，候选选择固定为四未知指标平均秩最低，精确并列按字典序。试点扩展门还要求14/14完整、42份报告、零失败、拆分一致、正确分类train/validation支持、风险非退化、相对MLP Energy至少2/4指标改善、四指标有向均值为正、Known F1容差、至少4/7套件非负且最差不低于-0.05，以及六方法平均秩不高于3。试点test标签只服务显式标注为development-only的预算门，正式部署阈值仍只用known-validation 95%接受率。

首次远端协议冻结在任何结果产生前因官方notebook工作树字节SHA跨平台不一致而失败关闭，`pre/post metrics=0`，没有生成可被误用的协议。修复为Git blob内容SHA后，核心与协议/汇总回归本地、GPU均为 `12/12 PASS`。当前权威protocol canonical/file SHA为 `a3f0572b...611e/b36099b2...e631`，扩展门canonical/file SHA为 `a6b73331...a5a2/0933aeb7...39b6`；冻结前后试点结果均为 `0/14`，因此正式方法总账仍为42，尚无k-LND效果结论。

低优先级watcher SHA为 `16adc130...920c`，GPU PID `3218770`。它只在现有污染链达到 `783 metrics + 783 provenance`、失败0且权威污染summary生成，并连续5次观察到GPU和实验进程空闲后，以CPU、`nice=19`、idle I/O、单worker运行14场景；结束后只生成分析，不自动启动full102。2026-07-24 00:40:12 UTC只读快照为污染 `735/783 metrics`、`739/783 provenance`、4路训练、失败0；k-LND仍为0指标，VGRF最终选择与branch-complete仍不存在。当前结论仍是Pairwise为incumbent，k-LND是新增的高保真直接领域基线候选，全面SOTA和最终自有算法均未成立。

### 102.25 OpenCBD直接领域论文契约与不可低保真适配边界

42方法总账虽然已足够覆盖通用OOD广度，但相关工作仍缺少对OpenCBD这一直接加密未知流量方法的明确定位。OpenCBD发表于Wireless Communications and Mobile Computing 2022，文章号1746373，DOI `10.1155/2022/1746373`。出版社开放全文确认其使用ISCXVPN2016，固定8个known类和5个互斥unknown类，每类1,000个样本；每个样本从10个连续包构建payload序列，并用虚拟包表示超过1秒的包间隔。CBD编码器由CNN、Transformer/BERT和dense模块组成，先用排除13个实验类的未标注流量自监督预训练，再做个体known-class训练和多编码器集成训练，损失为交叉熵与II-loss组合。

其开放集阈值数据边界值得保留：只在known-training上计算异常距离，排序后把最大1%距离视为异常边界，论文没有把unknown/test描述为阈值拟合输入。因此OpenCBD属于真正的直接领域known-only阈值基线，不应被通用OpenMax或一个表格CNN名称替代。但原文只报告known/unknown二分类及known多分类的Accuracy、Precision、Recall和F1，不提供strict-v4的Known Macro-F1、AUROC、AUPR、FPR95、OSCR统一契约。

2026-07-24按全标题、OpenCBD缩写、DOI和架构短语检索，未找到作者身份可核验的公开代码；论文也没有发布commit、依赖锁、固定seed、机器可读8/5类表、归档checksum、完整模型配置或capture/session组映射。GPU已有 `/datasets/cic/iscx_vpn_nonvpn_2016/raw/PCAPs` 的5个官方原始ZIP候选，合计26,217,052,748字节；这只证明数据候选存在，不能证明论文13类采样、连续10包构造、预训练排除集、拆分和模型状态可复现。CrossPlatform下的派生数组同样没有OpenCBD manifest，禁止冒充作者预处理。

更关键的是，OpenCBD消费payload字节序列，而strict-v4主表主动采用无payload流级统计特征。直接把现有表格送入CNN/Transformer会改变研究问题和模型，不是高保真OpenCBD。因此当前判定为 `paper_contract_admitted=true`、`gpu_raw_dataset_candidate_present=true`、`official_source_snapshot_admitted=false`、`native_execution_admitted=false`、`strict_v4_main_table_admitted=false`、`appendix_protocol_candidate=true`、模型指标0、正式方法增量0。该补充增强相关工作覆盖，但不启动低保真实现，不改变Pairwise incumbent或全面SOTA边界。

同期对OLPFF做2026-07-24刷新：出版社全文预览仍确认USTC-TFC2016/ISCX-VPN、10种开放集长尾设置、ResNet18+轻量分支+SMAF、manifold mixup伪未知和预设阈值，但精确代码检索仍无作者仓库。OLPFF继续保持高优先级直接候选和独立长尾协议，不因摘要中的“SOTA”措辞进入主表。00:52:55 UTC污染链为 `745/783 metrics`、`749/783 provenance`、4路训练、失败0；k-LND仍为0结果并等待权威污染summary。

### 102.26 VGRF终选与同算法系统链的环境一致性复核

在污染链接近完成时重新执行VGRF关键静态回归，首先暴露本地源码镜像缺少 `caeos/budgeted_conformal_uplift.py`。该模块在GPU权威项目中存在，SHA为 `4b679e32...fd3`，且已被结果前integrated设计的实现身份绑定；现已从GPU只读同步到本地，相同SHA复核通过。该问题只影响本地测试导入，不影响远端运行或冻结算法。

随后本地Python报 `run_strict_v4_vgrf_selected_system_capture.py` 第54行语法错误，但文件与GPU SHA均为 `9336c07b...b623`。根因不是镜像漂移：本地 `D:\soft\Anaconda3` 实际为Python 3.7.6，目标GPU环境虽路径名为py3.9且实际版本为3.9.23；括号化多上下文管理器在目标环境可解析。本机Python 3.12.13对capture及补齐模块的 `py_compile` 均通过，因此禁止为兼容错误的3.7测试解释器改动已冻结3.9实现。

GPU目标环境以低CPU/I/O优先级重新执行：validation gate核心 `3/3`、test-label/test-unknown扰动不改变选择 `1/1`、VGRF全确认加固 `6/6`、selected-system设计/准备/协议/seed317/捕获/训练效率/基准/污染/汇总/watcher组合 `41/41`、integrated comprehensive SOTA v2 `4/4`，合计 `55/55 PASS`。进一步从selected-system watcher提取execution protocol实际绑定的24个实现文件，逐文件比较本地与GPU SHA，结果 `24/24`完全一致。覆盖点包括known-validation-only门、204项整体选择、Pairwise精确回退、最终算法身份、306源捕获、42训练块、204同机块、1530比较污染定义和六系统门；测试与SHA通过证明执行链当前无静态断裂，但不替代尚未产生的真实效果。

2026-07-24 01:06:50 UTC污染链已推进至 `759/783 metrics`、`763/783 provenance`、4路训练、失败0；权威污染summary、VGRF最终选择和k-LND试点效果仍为0。当前最优已确认自有算法继续是Pairwise，VGRF只有在真实seed307和seed311/313门整体通过后才允许替换，全面SOTA仍未成立。

### 102.27 污染矩阵763项无效果进度与剩余任务审计

在不读取任何效果指标的前提下，对冻结783任务宇宙重新生成进度快照。汇总器逐项验证 `corruption_metrics.json` 的schema、record SHA、validation门、unknown/test标签未用于污染生成/拟合/选择，并拒绝冻结宇宙外或重复任务。2026-07-24 01:11 UTC结果为 `763/783` 完成，完成率 `97.4457%`；全部763个wrapper哈希有效、任务均属于冻结宇宙，`effect_metrics_read=false`。record/file SHA分别为 `9a5899af...0a42/e05c7407...9b9d`，本地与GPU文件SHA一致。

273个sentinel已全部完成，full102为 `490` 项完成、20项剩余。剩余任务全部属于USTC-TFC2016，没有其他套件或sentinel缺口；五个污染族feature shuffle、field missing、Gaussian drift、modality missing和row missing各剩4项。剩余任务键集合SHA为 `8e1e6679...19e`，因此后续完成状态可按同一冻结集合独立复验，不能用目录文件数替代任务身份。

快照时4项已启动未完成，均为USTC-TFC2016 `shifu`：feature shuffle模态2、field missing模态0、modality missing模态2、row missing模态1。对4个训练进程间隔20秒读取累计CPU时间，分别增加226、262、243和256秒，状态在 `R/S` 间正常切换且各自约占11至12个CPU核，不是僵死或空等待。其余16项尚未启动，将由冻结4-worker runner继续调度。

该审计只证明覆盖、身份和运行健康，不读取AUROC、AUPR、FPR95、OSCR、Known F1或ECE，因此不能提前判断污染门正负。必须等待783/783及权威summary后，重新审计五污染族、七套件、置信区间和相对OpenDetect退化结论；k-LND watcher也继续等待该summary，不手工越过门。Pairwise、VGRF和全面SOTA主张边界不变。

### 102.28 单套件污染门与综合SOTA v3的结果前纠偏

复核原污染汇总器发现，现有确认门按每个污染家族汇总全部102个场景的均值，因此某一数据套件的严重退化可能被其他套件抵消。原协议虽然报告Known Macro-F1、AUROC、AUPR、FPR95、OSCR和ECE六项指标，但冻结的 `maximum_mean_degradation` 只包含前五项，没有ECE阈值。已有结果接近完成时不得凭效果补设ECE阈值，也不得把“报告六项”误写成“六项均被阈值验收”。

为此在权威污染summary、suite audit、integrated v2 audit和integrated v3 audit均为0时，冻结补充协议 `strict_v4_postselection_corruption_suite_gate_protocol_v1`。它原样继承既有五个污染家族、七套件、102个场景和五个冻结阈值，形成 `5 × 7 × 5 = 175` 个逐家族逐套件阈值门；另要求 `5 × 7 = 35` 个ECE套件均值存在、有限并与权威summary一致，但明确保持描述性，不作事后阈值判断。审计器在summary完成后独立读取510个full102 canonical wrapper，逐项复核任务身份、无泄漏声明、metrics/clean SHA，重算全部套件均值并以 `1e-12` 绝对容差对照权威summary；任一聚合家族门或任一175项套件门失败，均必须报告负结果。

suite protocol canonical/file SHA为 `74bbb277...600b/8e828bd7...8586`；creator/auditor/watcher/test SHA为 `636d945f...8eb/69acd300...c77/0f144668...23d/0b989d85...0d1`。同时冻结综合SOTA v3设计，canonical/file SHA为 `336d858c...e6187/d8062b58...fb4d`；它明确supersede v2最终主张，只有integrated v2的算法一致性、外部数据、效率和selected-system证据通过，且Pairwise anchor聚合污染门与新增175项套件门全部通过，才允许 `comprehensive_sota_confirmed=true`。Pairwise套件门不能替代VGRF selected-system证据，ECE也不能升级为确认指标。v3 creator/auditor/watcher/test SHA为 `fc356cc3...071/2a338c1a...cc9d/57e040af...8f2/170e94aa...861`。

本地Python 3.12与GPU Python 3.9回归均为 `8/8 PASS`，8个部署文件逐SHA `8/8`一致。suite gate与v3 watcher PID分别为 `102009/102010`，均以低优先级等待既有权威输出，不修改783任务。2026-07-24 01:32:10 UTC，污染产物已达到 `783/783 metrics` 与 `783/783 provenance`，但权威summary及suite/v2/v3 audit仍全部不存在。因此当前只可确认实验覆盖完成，不能提前声称污染门通过、最终自有算法确定或全面SOTA成立。

### 102.29 污染确认正式负结果与自有算法纠偏方向

权威污染summary实际写入 `results/strict_v4_postselection_corruption_confirmation/`，而协议保存在 `results/strict_v4_postselection_corruption_seed7/`。初版suite watcher误把两者视为同一目录，因而只等待且未改写任何结果；路径修正后，独立审计在首个wrapper的自指记录哈希上失败关闭。runner写入 `record_sha256` 时对尚未包含该字段的对象求哈希，因此审计也必须先排除该字段再重算。该修复发生在权威summary之后、suite audit之前，明确记录为schema compatibility而非结果前协议；不改变任务、文件SHA、指标提取、退化方向、五个阈值或175项门。

兼容记录canonical/file SHA为 `854e5c43...a526/596c9b8a...76da`，绑定旧/新auditor SHA `69acd300...ac77/7b4c276e...55f7` 及权威summary manifest/file SHA `1ebaefe1...5941/0e61cc2e...dad6`。修正后的creator/auditor/watcher/test SHA为 `7e23d0de...af78/7b4c276e...55f7/3a7478b7...46b3/0c6d0cf0...3232`；本地与GPU组合回归增至 `9/9 PASS`。正式suite audit canonical/file SHA为 `b9e7c79a...376f/cff280b6...97b`，510/510 full102 wrapper、175/175阈值检查和35/35描述性ECE值均完成独立重算，validation通过，但最终 `passes=false`。

聚合家族结果如下。feature shuffle的F1/AUROC/AUPR/FPR95/OSCR平均退化为 `0.093898/0.075358/0.136948/0.107304/0.096566`，通过；row missing为 `0.071171/0.076751/0.135174/0.098679/0.091011`，通过。field missing的AUPR/FPR95退化 `0.171785/0.227936` 超门；Gaussian drift五指标退化 `0.126073/0.160326/0.197788/0.292375/0.192502` 全部失败；modality missing为 `0.302915/0.193723/0.194777/0.233317/0.323625`，五项全部失败。三者使原聚合门本身已是正式负结果。

逐套件175项中79项失败：按家族为feature shuffle 7、field missing 17、Gaussian drift 24、modality missing 27、row missing 4；按套件为CICIDS2017 20、Edge-IIoT 18、NF-CSE 14、USTC-TFC2016 13、CIC-ToN-IoT 8、NF-UNSW 4、CIC-IoT2023 2；按指标为Known Macro-F1 18、OSCR 17、AUPR 17、AUROC 14、FPR95 13。最严重的是CICIDS2017 modality missing：OSCR退化 `0.572511`、Known Macro-F1退化 `0.475385`；USTC-TFC2016和NF-UNSW modality missing的Known Macro-F1也分别退化 `0.464129/0.415727`。feature shuffle和row missing虽然聚合通过，仍有7和4个单套件门失败，直接验证了“总均值掩盖局部失败”的纠偏必要性。

论文现在可以写“完成783次预冻结污染确认并得到正式负结果”，不能写“鲁棒性SOTA”或“优雅退化门通过”。Pairwise仍是当前准确性incumbent，但不是鲁棒性完备的最终算法；integrated v3因suite gate失败将保持 `comprehensive_sota_confirmed=false`，即使后续v2其他门通过也不能升级。下一轮自有算法应优先处理可观测缺失模式下的模态安全回退和训练时结构化缺失增强，同时覆盖Gaussian drift与field missing；本次seed7污染结果只能转为开发诊断，任何新候选必须用未触碰的新训练种子、污染种子和预冻结整套七套件门重新确认，禁止在这510项上调参后把同一结果重复包装成确认。

### 102.30 Pairwise–OpenDetect比较污染零结果字段修复与恢复

原最终链在冻结比较污染v1协议后，于第一个 `cic_iot2023/backdoor_malware/seed137` 源对完成Pairwise和OpenDetect runtime capture，但evaluator在写入任何 `paired_corruption.json` 前失败。错误为 `MultiViewFlowDataset` 没有 `unknown` 属性；数据类自始至终公开的是 `is_unknown`。v1失败日志SHA `fb69492b...bd15` 已复制到协议目录保留，失败时配对结果严格为 `0/306`，因此可以做不涉及效果的字段契约修复。

比较污染v2协议只把 `bundle.test.unknown` 改为 `bundle.test.is_unknown`，并重新绑定evaluator、runner和summarizer；306个源、种子137/139/149、五污染族、severity、coverage-SHA模态规则、corruption seed211、六指标、20,000次bootstrap、Holm校正和全部suite非负门均未改变。v2 canonical/file SHA为 `ef9461fd...d8cf/96af30d4...9629`；revision creator/evaluator/runner/summarizer/chain/test SHA为 `120406fd...c83f/7e8b9c51...af32/54eaa3e2...0f1b/27e9c02e...5446/c40e95ba...4013/c6212574...fa6c`，7个文件本地/GPU逐SHA一致。本地旧Python环境及GPU目标环境比较污染回归均为 `8/8 PASS`，GPU Shell语法通过。

恢复主链PID为 `261507`。首个block复用已经通过等价门的两套capture，只重新执行evaluator，现已生成5个固定污染条件，候选/比较器输入数组逐元素相同，unknown/test标签未用于拟合、选择或污染生成；block canonical/file SHA为 `fad472f9...42a7/ce8cb24a...671f`。截至2026-07-24 02:48 UTC，`backdoor_malware`三种子和 `browser_hijacking/seed137` 已完成，当前进度为 `4/306` source pair、`20/1530` condition。该进度只证明v2恢复闭环，不允许陈述Pairwise相对OpenDetect更稳健；必须等待306/306、场景内三种子平均、六指标bootstrap与Holm门全部完成。

### 102.31 缺失感知自有算法的三条开发诊断与停止边界

正式污染负结果产生后，先对已有 `missing_aware_cauchy_modality_support_union` 风险做三种不增加训练的开发性回放。第一种raw missing-aware在保存的缺失掩码出现时直接使用缺失感知风险：510项中套件阈值失败由79降至49，modality missing五指标退化降为 `0.108841/0.117735/0.107822/0.101758/0.145826`，row missing降为0项失败；但clean输入最大指标差达到 `0.399763`，modality missing的Known F1仍超过0.10门，且Gaussian drift仍失败24项。analysis canonical/file SHA为 `d774a9a9...c4d0/08008d45...58c`，只能证明缺失感知证据具有开发价值，不能替换incumbent。

第二种conservative fallback只在冻结known-only选择风险等于Cauchy基风险时按场景启用，510项中440项激活，clean输入精确不变，失败数由79降至55；但modality missing退化仍为 `0.134415/0.130292/0.118097/0.117665/0.168828`，Known F1和OSCR继续失败。analysis canonical/file SHA为 `2334409f...0a9/ba949089...bbe`。第三种RC-MAF用known-validation分位映射把缺失风险校准到选择风险量纲，只对保存的无标签缺失掩码逐样本切换；无缺失样本和clean Known F1精确不变，但总失败只由79降至75，modality missing的FPR95/OSCR退化扩大到 `0.306134/0.283387`，field/row missing的尾部误报也恶化。analysis canonical/file SHA为 `97746d50...0d0/d52d3be7...b19`。

三条结果共同否定了“在冻结seed7输出上再做风险映射即可修复鲁棒性”的路线。raw版本改善最大但破坏clean语义；保守版本保护clean却仍有系统性缺失退化；秩校准版本保持逐样本clean等价但不能控制尾部风险。因此立即停止继续利用这510项结果搜索权重、阈值、分位或按套件回退。本轮结果只作为机制诊断，不作确认。下一候选必须在结果前冻结，使用全新训练种子和全新污染种子，并把训练期结构化模态/字段/行缺失与Gaussian drift增强、known-only校准、clean回退及七套件175项门同时写入协议。

### 102.32 k-LND冻结试点负结果与基线收缩

k-LND等待器在污染783/783及权威summary完成后按协议运行14个冻结场景、三种变体共42份报告，失败0；拆分、known-only拟合、正确分类支持、分数非退化和Known F1容差均通过。预注册排序选择 `klnd3`，其Known F1/AUROC/AUPR/FPR95/OSCR为 `0.756102/0.590787/0.480836/0.626373/0.490938`，四项未知指标平均秩为4.25。相对MLP Energy的AUROC/AUPR/FPR95/OSCR有向增益为 `-0.056762/-0.029822/-0.055891/-0.070014`，四指标均值为 `-0.053122`；7套件中只有CIC-IoT2023、CICIDS2017和USTC-TFC2016为正，NF-CSE最差为 `-0.191220`。

因此 `top_half_rank`、`metric_breadth`、`overall_gain` 和 `suite_robustness` 四门均失败，正式决策为 `expand_selected_klnd_to_full102=false`。k-LND完成了一条直接领域强基线的可证伪义务，但不进入full102和正式可排序主表，方法总账仍为42。轻量结果已镜像到 `source/CAEOS-EMTD/results/strict_v4_klnd_pilot_seed7/`；`analysis.json` 文件SHA为 `5df588f2...1804`。该负结果进一步说明单一logit类中心距离不足以替代多模态证据冲突与缺失机制，不改变Pairwise准确性incumbent身份，也不恢复全面SOTA主张。

### 102.33 MDR-CAEOS新鲜种子设计与零结果预冻结

基于三条缺失回退负诊断，新增 `MDR-CAEOS` 候选，但不修改已被冻结协议绑定的 `train_hybrid_open_set.py` 和Pairwise runtime。算法保留干净Pairwise为主路径，另训练一个只使用known-training的结构化增强全局分类器；独立视图专家仍在clean训练上拟合。增强固定覆盖modality/field/row missing、同known类内feature shuffle和Gaussian drift，训练样本子集比例为0.25；总增强权重只允许在预登记 `[0.125, 0.25, 0.5]` 中由14场景的known-validation clean容差与污染minimax Macro-F1整体选择，不能按test、unknown或套件效果选择。

推断健康门只使用三种无标签信号：validation校准的缺失掩码、最大局部冲突、clean与robust概率的Jensen-Shannon分歧；后两者阈值固定为known-validation 0.99分位。门未激活时prediction和risk逐样本精确等于Pairwise；激活时采用增强路径prediction，missing-aware或增强风险先通过known-validation经验分位映射回clean Pairwise风险量纲，拒识阈值继续取clean Pairwise known-validation。该结构同时避免raw fallback破坏clean语义和RC-MAF的跨量纲尾部误报问题，但目前只是可证伪假设。

设计在候选 `evaluation.json=0` 时冻结。pilot训练/污染种子为 `331/337`，14场景由coverage SHA每套件确定2个，6条件共84项；只有clean Known F1均值/最差退化不超过 `0.01/0.03`、pilot套件失败不超过50、modality/Gaussian失败均减少且任何家族指标相对Pairwise不额外退化超过0.02，才允许扩展。保留确认训练种子 `347/349/353`、污染种子 `359/367/373`，全102场景共1836项，最终仍要求聚合门和175项套件门全过。

设计canonical/file SHA为 `a8d9e9b5...1638/572c9b90...2019`；增强、融合、训练包装器、评估器和设计生成器SHA为 `ce92ed8a...b3eb/1c9f46b2...7f1e/b0fe1296...b781/3b0295ab...7bc9/0ddb170a...e4f6`，本地与GPU一致。目标py3.9静态编译通过，数组、健康门、冻结边界及真实小型sklearn拟合共 `6/6 PASS`。当前 `execution_admitted=false`，尚缺pilot执行协议、可恢复runner、独立汇总审计和资源等待器，且正式结果仍为0；因此本节只证明新候选已停止事后调参并完成结果前设计，不能写MDR-CAEOS有效或优于Pairwise。

### 102.34 MDR-CAEOS v2零结果修订、完整试点链与等待执行

102.33的v1设计冻结后、任何候选捕获或评估产生前，运行时实现复核发现训练包装器原先把配置分类器定义在 `main()` 内，导致正式捕获工件无法稳定反序列化；同时v1尚未绑定全局权重选择、84条件评估、汇总和独立审计实现。该问题若留到训练后再修会破坏结果前身份，因此在远端 `capture_manifest=0`、`evaluation.json=0` 时生成v2。v2只把分类器提升为可导入模块级类型并绑定完整执行面，算法公式、14场景、权重网格、训练/污染种子、pilot门和保留确认门均未改变；v1原样保留为被取代的设计证据，不再作为执行依据。

v2执行链先对14场景和3个增强权重生成42份runtime捕获。每份捕获分别训练clean Pairwise与robust路径，因此准确预算为84次模型拟合；只有全部42份known-validation profile齐全后，才在clean F1均值不低于 `-0.01`、最差不低于 `-0.03` 的候选中按跨场景污染minimax F1整体选择单一权重，未知类和test标签不进入拟合、权重选择、健康门或路由。选中runtime在clean及五污染家族上复用，不重新训练，形成 `14 × 6 = 84` 份评估，而不是按三个权重重复生成252份test评估。汇总器独立重算候选与Pairwise的175项套件阈值、clean退化、modality/Gaussian失败缩减及家族额外退化；审计器再复核实现SHA、42捕获、84评估、canonical summary和无泄漏边界。阴性pilot也必须写完整summary/audit和 `full_confirmation_not_admitted`，不得静默丢弃；阳性只允许后续另建1836项确认协议，不自动启动full102。

v2 design canonical/file SHA为 `9e53a1b4...3f0/e7427662...1274`，pilot execution protocol canonical/file SHA为 `8c9afb81...562/28231313...e89f`。独立复核确认14个来源场景、42捕获、84拟合、84评估，冻结时capture/evaluation/selection/summary/audit均为0，`unknown_or_test_labels_for_fit_selection_or_routing=false`，13个协议绑定实现的本地/GPU SHA不一致数为0。结构化增强、融合、运行时、训练包装器、捕获、评估、选择、runner、汇总和审计的关键SHA依次为 `ce92ed8a/1c9f46b2/ec28abab/71abdf25/18db5e93/fc173479/bae9b438/c03c5a63/a0246eb5/6ae18491`；协议创建器和watcher为 `0a296474/37c2f553`。目标环境静态编译、shell语法和组合回归最终为 `12/12 PASS`，其中v2零结果拒绝路径、可序列化分类器、42捕获选择、84评估汇总和确定性污染均有直接测试。

GPU等待器PID为 `1091078`，锁目录存在，状态为 `waiting for comparative corruption summary`；它只有在既有Pairwise–OpenDetect比较汇总完成且连续5次观察到GPU和实验进程空闲后，才以 `nice=19`、idle I/O、单外层worker启动可恢复pilot。2026-07-24 03:18 UTC，MDR正式捕获/评估仍为 `0/0`，比较污染为 `7/306` 源对、`35/1530` 条件，PID `261507` 正常存活。当前新增证据证明的是执行协议完整、身份冻结和无资源争抢，不是MDR效果；Pairwise仍仅为准确性incumbent，绝对污染门失败尚未修复，全面SOTA仍未成立。

### 102.35 MEDAF通用SOTA基线的源码固定与无泄漏准入边界

为补充2024后通用开放集SOTA，新增审计AAAI 2024 MEDAF（Exploring Diverse Representations for Open Set Recognition，DOI `10.1609/aaai.v38i6.28385`）。官方仓库固定到commit `5d5328333af1f0857b9de20e94063ca8e6353d16`，16个tracked文件、工作树干净；988,683字节离线Git bundle SHA为 `6c026975...78c4`，已同步到GPU `/opt/data/private/wangwt/ParkAttackKE/third_party_sources/MEDAF-5d532833`。源码完整实现三个专家分支、attention diversity loss、样本自适应gate和gated MSP；默认 `score_wgts=[1,0,0]`、gate分支、`gate_temp=100`、`logit_temp=100`。

官方训练函数本身只读取training loader，但默认评估不满足strict-v4：`core/test.py`把known-test与unknown-test共同写入open标签并计算ROC，再选取TPR最接近0.95的阈值计算Macro-F1；`osr_main.py`还在每个epoch读取known-test和unknown-test。源码没有known-validation loader，不报告FPR95、OSCR和ECE。其AUROC/AUPR是阈值无关报告，但默认F1阈值不能进入无未知暴露主表。进一步地，官方专家多样性作用于2D卷积空间attention map；直接把56/79列表格特征reshape成图像会改变输入语义，不能称原生MEDAF。

首次审计在模型结果0时错误绑定工作树字节SHA，Windows CRLF和Linux LF分别产生不同canonical `24ad940f...a34cb/4874bfe1...ca8e1`，两端失败工件原样保留。v2改用canonical Git blob内容SHA，方法与准入门不变；最终audit canonical/file为 `1a0ec766...a2f6/1cb49716...3042`，两端双一致。auditor/test SHA为 `4193859b...2595/a2f1b290...bf40`，本地/GPU `2/2 PASS`。

当前判定为 `official_source_snapshot_admitted=true`、`native_medaf_strict_v4_execution_admitted=false`、`named_tabular_adapter_candidate=true`、正式方法增量0、模型指标0。后续若执行，必须明确命名 `MEDAF-Tabular adapter`，在零结果时冻结表格/多视图attention定义，保留三专家、diversity、gate和gated MSP，只用known-training拟合与known-validation选阈值/超参，训练期间不读test，并补齐六指标和跨套件pilot扩展门。该候选不插队当前Pairwise比较或MDR；2026-07-24 03:52 UTC比较链为 `10/306` 源对，MDR捕获仍为0，Pairwise准确性incumbent与全面SOTA未成立边界不变。

### 102.36 MEDAF-Tabular核心实现与零结果设计冻结

在102.35的原生执行负门之后，仅以明确命名的 `MEDAF-Tabular adapter` 实现可证伪适配，不把56/79列表格reshape为伪图像。共享表格编码器对应官方共享前层；三个独立专家分别生成embedding和分类logit，并用目标类分类权重乘专家embedding构造类条件激活图。多样性项严格复用官方源码的L2归一化、按位置中心化、ReLU及三个专家对余弦求和。独立gate拥有自己的编码器，以温度100生成样本权重，并只融合detach后的专家logit，确保gate交叉熵不反向更新专家。总损失固定为 `0.7 × 三专家CE之和 + 1.0 × gate CE + 0.01 × diversity`；开放集风险固定为温度100的gated softmax之 `1-MSP`。

训练器固定150 epoch、SGD学习率0.1、momentum 0.9、weight decay `1e-5`、epoch130衰减和最终epoch checkpoint。训练函数签名没有validation/test输入，只能读取known-training；训练结束后才用known-validation的0.95接受率分位确定阈值，test标签只用于最终Known Macro-F1、AUROC、AUPR、FPR95、OSCR和ECE。目标Py3.9/Torch对三专家形状、gate概率、官方损失、gate/专家梯度隔离、三对CAM余弦求和及一轮known-only CPU训练smoke为 `5/5 PASS`，设计的确定性、42报告预算和零结果拒绝为 `3/3 PASS`。

设计在GPU适配 `metrics.json=0` 时冻结。场景选择不读效果，而以coverage manifest SHA、官方commit、suite、scenario的SHA256排序每套件取2个，共14场景；training seed固定为383。pilot在同一拆分上比较MEDAF-Tabular、MLP Energy和OpenDetect，共42报告。扩展门同时要求42/42、零失败、拆分与无泄漏全过、风险/gate非退化、至少2/4未知指标相对Energy改善、四指标平均有向增益为正、平均秩不高于2、相对OpenDetect的Known F1均值退化不超过0.03、至少4/7套件相对Energy非负且最差不低于-0.05。任何一门失败都不扩full102。

design canonical/file SHA为 `e8c83252...05db/9dfd9104...92bf`；model/trainer/design creator SHA为 `398aa95b...5a01/ae9f007c...b71e/c90b1198...cde4`，4个设计绑定实现的本地/GPU SHA差异0。当前 `pilot_execution_admitted=false`、`full102 execution_admitted=false`、正式结果和方法增量均为0；仍缺42报告执行协议、可恢复runner、canonical汇总/独立审计和排在现有队列之后的watcher。2026-07-24 04:00 UTC，比较链推进至 `11/306`，MDR仍为0捕获；本节证明适配定义与泄漏边界闭合，不证明MEDAF-Tabular有效。

### 102.37 MEDAF-Tabular零结果执行协议与MDR后置队列

在102.36的 `metrics.json=0`、summary/audit=0边界下补齐正式pilot执行面。协议逐场景绑定Pairwise确认源的seed137 CSV/config与source split、fresh MLP和OpenDetect provenance SHA；三方法均在同一源CSV上用新训练seed383重新拆分和训练。MEDAF固定150 epoch最终checkpoint；MLP Energy只选择fresh MLP score suite中的Energy报告；OpenDetect复用已固定的100 epoch、prototype reset和known-validation checkpoint/阈值协议。三者不得复用旧seed137效果，也不得在unknown/test上选择超参、checkpoint、阈值或路由。

可恢复runner只接受canonical protocol/design和绑定实现SHA。每个 `suite/scenario/method` 成功后写入独立run manifest，绑定完整命令、metrics SHA、拆分指纹、known-only选择门及MEDAF风险/gate诊断；未完成任务可重跑，已完成任务必须逐哈希复核。canonical汇总器要求14场景×3方法=42份唯一报告、零未解决failure、每场景三拆分指纹相同、无unknown/test选择、14个MEDAF风险与gate均非退化；随后独立计算AUROC/AUPR/FPR95/OSCR相对MLP Energy的有向增益、三方法平均秩、相对OpenDetect的Known F1退化和7套件增益。独立审计器从磁盘重新读取42份metrics与MEDAF scores，精确重算summary并复核11个执行实现SHA；汇总结果无权放宽102.36的任何扩展门。

execution protocol canonical/file SHA为 `b1ee2001...bc25/40b6f62c...6225`；protocol creator/runner/summarizer/auditor/watcher/test SHA为 `24b46505/eb166ae2/7645441a/9f56d172/f65b9c59/e4b71134`，watcher与chain test纳入后共13个协议绑定实现，本地与GPU逐文件差异0。目标GPU环境把新增4项链测试与既有MEDAF admission/core/design 10项合并为 `14/14 PASS`；本地缓存Python缺pytest、旧Anaconda因损坏的zipfile/pkg_resources不能启动pytest，故本地只记静态编译通过，不把本地pytest误报为通过。

低优先级watcher PID为 `2021310`，锁目录存在，状态为 `waiting for comparative corruption and MDR pilot completion`。它必须先看到Pairwise–OpenDetect比较summary/marker和MDR canonical summary/audit/pilot marker，再连续5次确认GPU及相关实验进程空闲，之后才以 `nice=19`、idle I/O、单外层worker串行执行42报告；阳性也只写 `full102_design_required`，不得自动运行full102。2026-07-24 04:47 UTC，比较链为 `15/306` 源对、当前进程健康，MDR捕获/评估和MEDAF报告仍均为0。当前新增证据只把pilot从“设计未授权”推进为“协议授权但排队等待”，没有任何MEDAF效果，也不改变Pairwise仅为准确性incumbent、全面SOTA未成立的结论。

### 102.38 OpenPN直接基线准入审计与队列实时状态

补充审计2026年Journal of Computer Security论文OpenPN（DOI `10.1177/0926227X251414058`）。出版社、DBLP和OpenAlex一致确认论文身份为34卷3期、193-210页、2026-02-10首次在线；但出版社页面为restricted access，OpenAlex记录 `is_oa=false`、`oa_status=closed`、无开放PDF及仓储全文。按DOI、完整标题和 `OpenPN "unknown attack"` 执行的GitHub repository API查询均为0，公开网页精确检索也未验证作者实现；GitHub code search因未认证返回401，故未被计作通过。这里的失败关闭结论只表示“截至本轮未验证到作者代码”，不把负检索夸大为代码不存在。

出版社摘要可直接确认论文整体框架分层：第一层OpenPN分类已知流量并识别未知流量；后续由专家验证未知候选，使用密度型k-reciprocal nearest-neighbor聚类优化，并把确认为新攻击的类别用于持续学习。因此完整框架不满足strict-v4静态零未知暴露协议；第一层OpenPN仍可保留为条件候选，但在全文或作者代码可用前，模型、损失、阈值、三套数据集身份、类别表、拆分、种子及unknown/test选择边界均不可重建。禁止据摘要自造表格适配并称为OpenPN复现，不启动GPU训练，不增加方法数或模型指标。

证据manifest canonical/file为 `0f85e55e...b77fa/87efb3c7...5946d`，audit canonical/file为 `a5a0248a...3505/9245cd2b...141a`，auditor/test SHA为 `a8603341...3d31c/774525c9...2b971`。新增测试包含真实仓库evidence重算与存档audit对象完全相等门，本地和GPU均 `6/6 PASS`；最终 `native_execution_admitted=false`、`strict_v4_main_table_admitted=false`、`baseline_count_increment=0`。

2026-07-24 05:42 UTC远端实时核验显示Pairwise-OpenDetect比较链PID `261602`存活，已完成 `19/306` 源对、`95/1530` 污染条件、38个模型捕获，failure文件0，权威summary仍未生成。MDR捕获/评估和MEDAF metrics/summary/audit继续为0并按依赖等待。OpenPN负准入没有占用训练资源；当前自有算法顺序仍是先完成比较链，再执行MDR新鲜种子pilot，最后执行MEDAF-Tabular。Pairwise仍只是准确性incumbent，其绝对污染门失败未被修复，全面SOTA及最终自有算法结论均未成立。

### 102.39 CNN-RPL直接DDoS基线全文、代码与数据准入审计

补充审计IEEE Access 2024 CNN-RPL（DOI `10.1109/ACCESS.2024.3388149`）。DBLP与IEEE身份一致为12卷56461-56476页；官方PDF/抽取文本SHA为 `fb3816fc...5421/742a6879...bfc5`。全文图表确认7个Conv1D、3次MaxPool、卷积后PReLU、二维deep feature、6类输出与18,872参数；训练为100 epoch、学习率0.003、batch512、Adam、MultiStepLR及10个固定种子。损失为 `Lc + lambda*Lo`，拒识函数使用二维特征到类中心的指数距离。

原生协议数据候选已经齐全。GPU CICIDS2017路径 `/datasets/cic/cic_cicids2017/raw` 包含Wednesday/Friday PCAP和MachineLearningCSV；CICDDoS2019路径 `/datasets/cic/CICDDoS2019` 包含论文使用的LDAP、MSSQL、DNS、NetBIOS、NTP、UDP、SNMP、SSDP、SYN CSV，原始源覆盖为 `2/2`。但论文没有发布输入特征顺序、缩放/插补/过滤、完整pooling stride/padding、MultiStepLR milestones/gamma或processed manifest；源文件齐全不能证明论文Table 2的处理后数量身份闭合。

GitHub repository API三组查询为 `0/1/0`。唯一同名仓库固定commit `a4c352624707a76bf8ad921b6e9210b67b513238`，仓库作者不在论文作者表；实际代码仅使用Passive Aggressive、Random Forest和Decision Tree，缺PyTorch、Conv1D与reciprocal-point loss，README反而把CNN/RNN列为future enhancements，因此已明确排除为作者实现。该正搜索结果不能静默忽略，也不能因标题相同冒充原论文代码。

strict-v4关键失败门来自选择边界：论文固定 `lambda=0.3`、阈值0.7，并明确说明这些参数“为优化未知识别而选择”且可按不同分布调整，却未记录独立known-only validation。论文也只报告Accuracy/Precision/Recall/F1，没有AUROC/AUPR/FPR95/OSCR/ECE及capture-group拆分。故 `native_execution_admitted=false`、`strict_v4_main_table_admitted=false`，但 `native_external_protocol_data_ready=true`；CNN-RPL进入直接领域相关工作和原生外部协议条件候选，不启动低保真训练。既有ARPL adapter只是方法族适配，禁止改名为CNN-RPL复现或重复增加方法数。

机器证据evidence/audit canonical为 `a5075195...3194/933429d4...2c72`，auditor/test SHA为 `b58c9ce2...0a32/654d9dc5...7236`，本地/GPU真实工件重算均为 `8/8 PASS`，7个同步工件逐SHA一致。2026-07-24 06:23 UTC，比较链PID `261602`健康，已完成22/306源对、110/1530条件，45个capture表示第23个源对候选捕获正在进行，failure 0、summary 0；MDR PID `1091078`与MEDAF PID `2021310`继续依赖等待。CNN-RPL审计没有抢占GPU，当前顺序和结论不变：Pairwise仅为准确性incumbent，先完成相对比较，再以新鲜种子检验MDR，全面SOTA和最终自有算法仍未成立。

### 102.40 SINFlow 2025直接未知DDoS基线准入审计

补充审计CMC 2025 SINFlow（DOI `10.32604/cmc.2025.061001`）。官方PDF/抽取文本SHA为 `c52d6709...ef7e/e20dc94d...6c83`。论文管线先以autoencoder编码流级特征，再以DNN做benign/malicious二分类，最后用Gaussianizing Iterative Slicing估计编码训练分布，以log-density识别未知。已冻结的训练参数包括Adam、LR 0.005、weight decay 0.003、batch512、随机70:30拆分及16个种子；阈值取训练密度第1百分位，报告值为-23.30。

论文级复现条件未闭合。正文没有给出AE层宽、潜维度、激活函数、dropout率、DNN层结构、训练epoch或GIS迭代数、切片数、KDE/whitening/停止条件；训练次数又分别写成10次、16种子和20次。预处理虽描述删除missing/NaN、INF置1e10、负值置0、`log10(X+1)/10`及缩放到 `[0,1]`，但没有说明缩放器是否只在training拟合。阈值规则原则上只需known-training，但正文允许按数据集经验调整且没有发布选择trace，故不能确认zero-unknown exposure。

2025 IDS作者实现未验证；四组GitHub repository查询均为0，负检索不等于不存在。论文引用的2021 SINF底层官方仓库固定commit `450ee7bf...a58`，提供通用GIS/SIG引擎但不含CIC数据、AE/DNN、论文预处理或增量管线，不能冒充2025实现。GPU原始源候选覆盖2/2，但直接读取ZIP表头发现CICIDS2017 Wednesday为79列、CICDDoS2019示例为88列、共享78列；论文声称80个输入特征却未发布跨数据集映射或processed manifest。

效果口径也必须分层。静态未知模块只报告ODR，CICIDS2017-Friday为1.42%，CICDDoS2019约11.24%-86.69%；摘要0.9999 F1来自专家标注被标记未知样本并执行增量学习之后，禁止写成静态zero-shot SOTA。机器evidence/audit canonical为 `783454e4...f82f/698f398b...f892`，auditor/test SHA为 `f1f4c45e...7ed5/d1990b7b...1fd8`，本地/GPU均10/10 PASS，8个同步工件逐SHA一致。最终为 `native_execution_admitted=false`、`strict_v4_main_table_admitted=false`、`native_external_protocol_data_ready=true`、模型指标0、正式方法增量0。

2026-07-24 07:01 UTC比较链PID `261602`健康，已形成26/306源对、130/1530条件与52个capture，failure 0、summary 0；当前正在 `CICIoT2023 / DDoS-RSTFINFLOOD / seed149` 的candidate capture。MDR与MEDAF继续等待，不因文献审计抢占计算资源。当前仍只能称Pairwise为准确性incumbent，全面SOTA和最终自有算法未成立。

### 102.41 Pairwise-OpenDetect比较链的无语义变更并行加速

07:03 UTC资源复核确认GPU服务器有80核、503 GiB内存且约481 GiB可用，A6000空闲；原比较runner却只串行执行一个source pair，活动capture约占4核和7.6 GiB。运行约5小时仅完成26/306，成为MDR、MEDAF与最终自有算法选择的确定性阻塞。比较污染不是效率benchmark，结果身份由冻结v2 protocol、trainer/runtime/capture/evaluator和block canonical约束，调度顺序不进入任何指标或统计公式，因此新增只改变任务领取顺序的外部加速器。

加速器每次复核原7个实现SHA，从source registry末端反向领取任务，启动和逐任务均检查连续串行前沿及最小安全间隔；每项使用独立原子claim，发现未claim部分目录即失败。候选命令只替换output dir，其他参数仍来自冻结provenance；OpenDetect继续CPU same-device shadow和 `1e-12` 门；最终仍由原v2 evaluator写出，且必须通过原block schema、protocol SHA、source/split身份、五污染族、输入相等和无未知拟合门。加速器不写execution-complete、不生成summary，不改变最终统计。

两任务试点固定indices 305/304，即USTC Zeus seeds149/139，距串行前沿超过270项。约3分钟均完成，block canonical为 `02f179fd...199d/63758ccc...b936`，失败0；pilot manifest/summary canonical为 `6962f398...5304/893c6412...5b4`。随后启动 `reverse64_w10_20260724T0715Z`，manifest canonical/file为 `a3917d94...e74c/f0a2bc9f...fad5`，只覆盖indices303..64共240项，启动前沿27、gap32，已完成304/305不重复领取。

10个活动worker使1分钟load升至112.89/80核，因此没有继续盲目扩并发，而是暂停6个本轮capture、保留进程和claim，把有效并发降为4；load随后降到28.14且结果继续增长。自动恢复守护器只在四个活动槽耗尽队列、父进程仅剩6个stop子进程时核验PID/PPID/state并恢复，monitor PID `4151738`。accelerator/test SHA为 `d7bd83eb...dfa3/870d2bc6...913`，monitor/test SHA为 `9c06b8e5...9d79/e94648f8...7336`；本地新增测试 `7/7+3/3 PASS`，GPU合并原比较回归 `18/18 PASS`。

07:39 UTC，原block门已确认总计48/306 source pairs、240/1530 conditions、96个capture，连续串行前沿28；反向链新增20块，failure 0，active summary、总summary和resume record均为0。MDR/MEDAF继续等待。该进展只缩短结果形成时间，不是效果增益；Pairwise仍仅为准确性incumbent，全面SOTA与最终自有算法未成立。

### 102.42 MDR-CAEOS三新种子确认链与MEDAF后置纠偏

MDR v2虽已在结果0时声明保留训练种子 `347/349/353` 和配对污染种子 `359/367/373`，但阳性pilot之后仍只有“需要full102设计”的标记，没有协议、执行器、汇总器、独立审计或最终选择。这会使最关键的自有算法探索停在14场景development-only结果，不能支撑“最优自有算法”结论。当前补齐的条件分支不修改13个已被活动pilot protocol绑定的实现；只有pilot summary canonical、独立audit PASS、阳性扩展决策和确认结果计数全0同时成立时，才允许冻结full protocol。

确认宇宙固定为7套件102场景、三个全新训练/污染种子对，生成306个clean/robust双路径捕获、612次模型拟合和clean加五污染族共1,836份评估。pilot只确定一个全局augmentation weight，确认阶段禁止重新选权重、套件、污染、阈值或路由。每个捕获绑定seed137来源provenance、CSV/config SHA和fresh training seed；每个评估绑定runtime/input SHA、污染模态、severity与corruption seed。runner按任务目录可恢复，发现未完成的部分capture即失败关闭；正式运行固定4个外层worker、每训练8 jobs，并只在连续5次资源空闲后启动。

最终门完整重放5族×7套件×5指标的175项阈值、25项等套件聚合族阈值、clean Known F1均值/最差非劣、inactive probability/prediction/risk精确Pairwise回退和unknown/test零选择。另先在每个场景内平均三个保留种子，再以套件内重采样、套件等权聚合执行10,000次bootstrap，主复合退化优势95%下界必须严格大于0。全部通过才整体选择 `mdr_caeos_v1`；任一失败整体保留 `caeos_pairwise`，禁止按套件、指标或组件拼接。即使MDR胜出，selection仍显式保持 `comprehensive_sota_confirmed=false`，继续等待外部数据、效率、部署与系统门。

protocol/evaluator/runner/summarizer/auditor/watcher SHA分别为 `fa2e7ffe/52de34fe/ed148e78/791815c7/c8b16d8f/ffaa3dbc`；MEDAF恢复器SHA为 `b64cee40`。9个新增实现/测试文件本地与GPU逐SHA一致，本地Python3.12静态编译通过；GPU目标Py3.9的MDR新旧组合回归 `15/15 PASS`，确认与恢复子集另为 `6/6 PASS`，仅有既有numexpr/bottleneck版本警告。

为避免MEDAF在MDR pilot结束瞬间与自有算法确认争抢资源，MDR确认watcher PID为 `3578270`；尚未训练的MEDAF watcher PID `2021310` 已暂停，恢复monitor PID `3602612` 只在MDR `branch_complete` 后核验PID、命令和stop状态再SIGCONT。该动作只改变队列顺序，不修改MEDAF算法或其冻结protocol。08:51 UTC比较链已达137/306 pairs、685/1530 conditions、274 captures、failure 0；MDR pilot/确认和MEDAF效果仍全为0。当前新增的是完整可证伪的自有算法确认能力，不是MDR有效、最终算法已确定或全面SOTA成立。

### 102.43 MDR胜出后的证据不可继承边界与全面SOTA分层

现有integrated v2/v3只识别Pairwise或VGRF，并且旧v3绑定的Pairwise绝对污染门已经正式失败。因此，MDR即使通过保留种子full102确认，也不能把旧外部数据、效率、部署或系统结果改名继承，更不能靠增加一个算法白名单升级全面SOTA。为避免看到MDR效果后再选择门槛，新增 `strict_v4_mdr_postselection_evidence_design_v1`，在MDR pilot、确认、外部、系统、PARROT和综合审计结果均未产生时冻结。

设计直接绑定MDR v2的保留宇宙：102场景、训练种子 `347/349/353`、污染种子 `359/367/373`、clean加五污染族和1,836项确认评估。后选择阶段必须重新训练MDR并完成两套恶意外部数据LSNM2024/CICDDoS2019、种子 `223/227/229`、OpenDetect主比较器的正式确认；Pairwise/VGRF外部结果不可继承。系统证据要求306个MDR runtime序列化往返、prediction精确一致、risk/probability最大绝对误差不超过 `1e-12`，并在同一硬件、独占资源、批量1/64/512、5次预热和30次计时下完整报告延迟、吞吐、GPU/主机内存、工件大小与拟合耗时。PARROT2025仍只用于320捕获/80应用的无解密外部良性安全回放，不得用于训练、选择、校准或阈值，也不得替代恶意外部数据。

论文结论被固定为两个不可混淆的层级。只有MDR full102、两套新鲜恶意外部数据、MDR自身系统可部署性和PARROT良性安全全部通过，才允许讨论“准确率/鲁棒性/外部泛化SOTA且可部署”；只有在此基础上，MDR对嵌入Pairwise参考和OpenDetect的延迟、吞吐、工件与拟合成本严格效率优势也全部成立，才允许“多维全面SOTA”。若效率不优，必须报告权衡并保持多维全面SOTA为false，禁止按数据集、指标或组件拼接。

GPU权威设计canonical/file SHA为 `c589a060...be1ce1/997b32ac...365f`，creator/test SHA为 `3d7b06b2...c560/39fec7b5...92bcb`，GPU测试 `4/4 PASS`；冻结时external metrics、system blocks、PARROT metrics和integrated audits均为0。09:14 UTC比较链实际文件名复核为 `paired_corruption.json`，进度163/306 pairs、815/1530 conditions、326 captures、failure 0，权威summary仍未生成；MDR与MEDAF效果继续为0。该冻结只补齐结论边界和后续实验合同，不证明MDR胜出或全面SOTA成立。

### 102.44 MDR恶意外部子设计、协议生成与可恢复执行骨架

在总合同四类输出仍为0时，进一步冻结 `strict_v4_mdr_external_malicious_design_v1`。它固定LSNM2024与CICDDoS2019、训练种子 `223/227/229`、fingerprint-grouped拆分、逐攻击家族留一、OpenDetect冻结策略和原两数据集统计门。MDR增强权重只能从阳性full102 canonical确认协议读取一次，禁止在外部数据上重选；每个场景的augmentation/validation-profile seed由外部design manifest、数据集、未知家族、训练种子和用途字符串的SHA-256前31位确定，不读取任何效果。design canonical/file SHA为 `28ab654f...4bd00/adfca454...1407`，creator/test为 `fe5220a1...0a6e/d1bb86ca...15c`，冻结正式指标计数0。

协议生成器只在final selection v2选择 `mdr_caeos_v1`、MDR full102 summary通过、独立audit通过、两套外部准备summary完整且全部实现SHA存在时才允许创建；它逐CSV/sidecar绑定文件SHA、标签与每类至少三组门，并将场景增强种子写入执行清单。protocol creator/test SHA为 `a181d502...af3e/871f7b84...6c8f`，当前因上游尚未阳性而未生成正式protocol，这是预期阻断而非失败。

运行时评估器读取MDR capture artifact和evaluation inputs，复核算法、weight、seed、split fingerprint及runtime证据；candidate与嵌入Pairwise都在同一test上计算六指标，test标签只用于最终指标。inactive prediction/risk/probability任一不与Pairwise逐元素一致即失败关闭。evaluator/test SHA为 `5e5afec3...2523/ef54da3e...a733`。可恢复runner对每场景依次执行fresh clean/robust MDR capture、MDR评估和OpenDetect；完整工件可跳过，空目录可继续，任何部分capture或metrics目录拒绝静默覆盖。runner/test SHA为 `9d8640de...3347/5e038867...8add`。

五组新增模块GPU合并回归为 `19/19 PASS`，仅有既有numexpr/bottleneck警告。当前尚缺外部summarizer、独立auditor与条件watcher，因此执行链还未准入，也没有外部效果。09:57 UTC比较链189/306 pairs、945/1530 conditions、378 captures、failure0，summary仍无；MDR pilot、确认、外部和MEDAF效果均为0，全面SOTA仍未成立。

### 102.45 MDR恶意外部分支闭环与条件排队

外部summarizer已按原两数据集冻结统计口径补齐。它先在每个“数据集×未知攻击家族”块内平均 `223/227/229` 三种子，再用攻击家族块执行10,000次bootstrap；AUROC/AUPR/OSCR按candidate减OpenDetect，FPR95按OpenDetect减candidate。四指标同时要求总体均值严格为正、bootstrap 95%下界严格为正、单侧Wilcoxon经Holm校正后小于0.05，并保留两数据集四指标非负和Known F1总体/逐数据集容差。summarizer/test SHA为 `72018d43...62b1/0ba02b1f...fb89`。

独立auditor从磁盘重新读取全部metrics/provenance并精确重算summary。其 `passes` 只表示协议绑定、场景覆盖、零failure和精确重算完整；科学效果另记为 `external_effect_gate_passes`。因此完整的正式负结果允许 `passes=true` 且 `external_effect_gate_passes=false`，审计不得覆盖或升级负效果。auditor/test SHA为 `ae43c7d9...aff9/3bf184ae...58e9`。

静态复核发现full confirmation把 `training_sample_fraction` 与 `health_quantile` 放在 `confirmation` 子对象，新external protocol creator原先按顶层读取。该问题在MDR、external metrics均为0时修正并新增嵌套字段测试；修正后creator/test SHA为 `ce652214...a449/8a7a33db...82ef`。随后GPU端对外部分支8组测试合并回归 `33/33 PASS`，目标Bash语法通过；未来protocol所需13个实现文件已逐SHA解析齐全。

条件watcher SHA为 `0ccb86a4...377a`，测试SHA为 `e10c1346...99b0`，GPU PID `1032116`。若MDR保留种子确认最终选择Pairwise，它写canonical not-required和 `comprehensive_sota_confirmed=false` 后结束；只有选择MDR、full confirmation summary/audit通过、外部准备完成且连续5次资源空闲，才冻结正式protocol并依次运行MDR/OpenDetect矩阵、汇总和独立审计。11:28 UTC比较链252/306 pairs、1260/1530 conditions、508 captures、failure0，权威summary仍无；MDR、MDR外部和MEDAF效果仍为0。外部分支代码闭环不等于外部效果成立或全面SOTA成立。

### 102.46 恶意流量检测为何必须评估良性流量

这里的“良性检测”不是另建一个与恶意检测无关的分类任务，也不是用PARROT标签训练良性分类器。部署系统对每条流量都必须在“告警、拒识、继续放行”之间决策；只测恶意样本能得到检出率，却无法知道系统会把多少正常业务误报为恶意。误报率的分母正是良性流量，因此没有良性样本就不能估计FPR、每应用误报集中度、运维干预率或阈值跨域稳定性，也不能论证系统可部署。

开放集加密流量的风险更明显。新应用、版本升级、CDN切换、移动端网络变化和加密协议演进都可能产生训练域外但完全良性的流量；模型若把“未见过”简单等同于“恶意”，未知攻击召回可能上升，但实际SOC会被大量正常告警淹没。故PARROT2025在本项目中的唯一角色是“跨域良性流量误报安全性评估”：禁止训练、选择、校准和阈值调整，只测冻结系统在320个捕获、80个应用上的false alert、known-attack assignment、reject与operational intervention。它不能替代LSNM2024/CICDDoS2019恶意外部确认，也不能支持恶意准确率或PARROT SOTA声明。

### 102.47 MDR系统部署与PARROT良性安全链闭环

MDR selected-system分支已实现306个保留确认runtime、102个场景块、批量1/64/512、5次预热、30次计时、同进程交替顺序和嵌入Pairwise精确序列化往返。汇总先平均每场景三个MDR训练种子，再执行10,000次场景块bootstrap；部署等价门与严格效率优势门分开，效率失败只阻断多维全面SOTA。GPU定向测试 `21/21 PASS`，条件watcher PID `2630913` 等待canonical MDR分支。

PARROT链新增独立MDR原始特征部署包，未改动已由pilot protocol绑定的共享MDR runtime与capture脚本；原冻结SHA已复核保持不变。安全设计固定30个USTC模型对、320捕获、80应用、56个无解密特征，候选与OpenDetect在同一处理后输入上比较；主统计先在capture内平均30模型，再对320个capture做10,000次块bootstrap，应用级80×4仅作次级汇总。完整protocol/evaluator/runner/summarizer/auditor/watcher已通过GPU `25/25 PASS`，watcher PID `3711611` 等待MDR选择、PARROT特征、恶意外部与系统分支。当前仅证明未来评估合同完整，正式PARROT指标仍为0。

### 102.48 MDR–OpenDetect效率补充与综合SOTA预结果审计

后选择总合同要求MDR同时严格优于嵌入Pairwise和OpenDetect，原selected-system链只覆盖前者。为关闭该缺口，在任何MDR效率输出产生前冻结 `strict_v4_mdr_opendetect_efficiency_design_v1`，canonical SHA为 `be497cbc...62e7`。设计固定306个MDR确认capture、102个OpenDetect seed137 runtime、102场景×3个MDR训练种子、批量1/64/512、5次预热、30次计时、同进程同输入、交替顺序及10,000次场景块bootstrap；OpenDetect seed137复用只允许支持运行效率，不得支持效果结论。

实现审计发现OpenDetect源指标真实字段是 `training_seconds`，不是设计文字中的 `elapsed_seconds`，故协议绑定真实字段与metrics文件SHA，不伪造字段。更重要的是，MDR的clean+robust训练墙钟下界不能单独证明总构建成本更低。由于306个确认任务尚未启动，确认runner已在不改共享MDR runtime/capture的前提下增加外层 `time.perf_counter` 证据，记录包含训练、校准、validation profile和序列化的完整capture subprocess墙钟；严格fit gate使用该保守实测总耗时，下界仅保留为诊断。效率链的protocol/benchmark/runner/summary/audit/watcher与确认计时证据已通过GPU定向回归，合并测试先为 `12/12 PASS`，加入综合审计后为 `17/17 PASS`；效率watcher PID `218013` 等待selected-system完成。

综合审计另在结果前冻结 `strict_v4_mdr_integrated_comprehensive_sota_protocol_v1`，canonical SHA为 `e9b093ea...ffe7`，watcher PID `340799`。它逐分支验证protocol/summary/audit canonical链与实现SHA，并输出两级不可拼接结论：一级要求MDR full102确认、LSNM2024/CICDDoS2019恶意外部、部署等价和PARROT良性误报安全全部通过；二级在一级基础上再要求相对Pairwise与OpenDetect的全部延迟、吞吐、工件和完整构建耗时门通过。审计完整性 `passes` 与科学门结果分离，任何负门都原样保留；SOTA范围只限冻结的strict-v4比较器、数据集与指标宇宙，禁止扩写为普适SOTA。

截至本次快照，Pairwise–OpenDetect主链为 `288/306` 配对结果，两侧runtime capture也均为 `288/306`；权威summary尚未生成，MDR确认protocol仍不存在。故当前可以写入论文的是实验设计、泄漏控制、基线准入审计、Pairwise绝对污染正式负结果和MDR可证伪验证路线；不能写MDR已优于基线、PARROT安全门已通过、最终自有算法已确定或全面SOTA成立。

### 102.49 MDR证据复用的精确部署优化链

静态调用审计发现，原始MDR一次推理中clean路径先执行Pairwise预测、再重复提取模型证据，共2次模型证据前向；robust路径还会为missing-aware risk再次提取组件，共3次，合计5次。新增 `MDREvidenceReuseRuntime` 在不修改已冻结共享MDR runtime、capture或训练器的前提下，保留clean/robust第一次前向得到的概率、局部冲突和robust风险组件，使每条路径各只执行1次模型证据前向，合计由5次降为2次。该适配器不改变健康门、风险公式、阈值、预测、污染生成或模型状态。

零正式结果设计已固定306个MDR保留种子capture、102个三种子场景块及clean加五污染族共1,836个等价条件，design canonical为 `18ba07b9...988c`。离散输出必须逐数组精确一致，概率、风险和全部诊断量最大绝对误差不超过 `1e-12`，且要求序列化往返等价。效率测量在同进程、同输入、单线程环境下交替比较原始MDR、证据复用MDR和嵌入Pairwise，固定batch 1/64/512、5次预热、30次计时，再按102个三种子场景块执行10,000次bootstrap。

正式protocol creator、evaluator、可恢复runner、summarizer、独立auditor、条件watcher及测试SHA分别为 `46edde9b/66188953/1d8a1368/6ca70f90/62c71953/acf7033e/05eb2c57`，本地与GPU逐SHA一致。runner只接受watcher完成五次空闲复核后传入的外部 `MDR_EXCLUSIVE_MACHINE_GATE=passed`，禁止自行签发该标记。目标GPU回归为 `10/10 PASS`，Bash语法通过；watcher PID `853649` 当前只等待canonical MDR最终选择和selected-system完整性，不抢占主链。若MDR未入选则写canonical not-required；若入选，则只有306捕获、1,836条件、序列化和独立审计全部通过才允许部署替换。

三类门严格分离：`deployment_substitution_gate` 只证明效果等价且可以替换；`latency_improvement_over_original_gate` 另以全部延迟CI上界不高于1、吞吐CI下界不低于1判断是否确实提速；相对Pairwise结果仅为补充诊断，不能覆盖已冻结selected-system效率门。该优化按构造不减少双模型训练/完整capture成本，也不移除双模型工件状态，不能单独支持SOTA或挽救失败的效率门。

2026-07-24 15:32 UTC复核时，Pairwise–OpenDetect主链已形成 `291/306` 个配对结果，主runner PID `261602` 仍存活，权威summary与MDR confirmation protocol仍未生成。因此当前新增的是可审计的部署优化能力，不是MDR效果阳性、最终自有算法已确定或全面SOTA成立。

### 102.50 Pairwise–OpenDetect相对污染正式负结果与独立审计

主比较链最终完成306个runtime capture pair、102个场景、三种子场景内平均及1,530个污染条件，权威summary canonical为 `eae661c7...5618`。五个污染族的严格门全部失败，因此 `comparative_robustness_gate=false`。这与Pairwise此前相对自身clean anchor的绝对污染负结果方向一致，并进一步证明不能用“比OpenDetect退化更少”挽救Pairwise鲁棒性声明。

结果存在稳定的指标分裂：Pairwise在五族Known Macro-F1均值上分别相对OpenDetect提高 `+0.016197/+0.048385/+0.014268/+0.059404/+0.013596`（feature shuffle、field missing、Gaussian drift、modality missing、row missing），但主要未知检测与校准指标整体变差。例如AUROC均值优势依次为 `-0.022407/-0.071702/-0.082669/-0.083474/-0.040251`，AUPR为 `-0.043827/-0.089733/-0.087325/-0.085467/-0.069701`，OSCR为 `-0.004391/-0.030276/-0.051316/-0.050431/-0.016146`，ECE优势也全部为负。五族的均值、bootstrap下界、Holm显著性和逐套件非负门均未全部通过，禁止只抽取Known F1或个别套件写成相对胜出。

为缩短最后12项串行长尾，新增独立final-gap协调器。它先确认PID `261602` 为STOP、保留其正在写的index66，固定indices67..77、4 workers，不改protocol、训练器、capture、evaluator或统计；11/11原block canonical通过、失败0，run manifest/summary canonical为 `1a5ad088...a185a/66e48888...f2311`，随后自动恢复原runner并由原runner生成权威summary。accelerator/coordinator/test SHA为 `dc699830/88131ca0/9f63710f`，GPU与原加速器组合 `12/12 PASS`。

新增独立审计器重新读取306个block，绑定全部block文件SHA，重算1,530条件、三种子场景平均、10,000次bootstrap、单侧Wilcoxon-Holm、7套件均值和五族总门，并核验10个冻结实现SHA。全部完整性检查为true，`passes=true`，但科学效果保持 `comparative_robustness_gate_passes=false`；audit canonical为 `511887e4...36cb`，审计器/test SHA为 `d3afdb4f/50b9eb97`，GPU与原比较测试合并 `9/9 PASS`。审计PASS只证明负结果可信，绝不把负效果升级为SOTA。

### 102.51 MDR pilot实际启动、等待死锁纠偏与捕获加速

主比较summary形成后，MDR pilot watcher原应进入五次空闲检查，但旧冻结脚本的 `pgrep` 模式把VGRF和MDR confirmation的纯等待脚本误当成实际训练，导致idle样本永久为0。由于pilot protocol绑定旧watcher SHA且正式capture仍为0，没有事后改写该冻结脚本；而是停止三个零结果纯等待进程，使原watcher于16:56 UTC取得连续五次空闲并按原protocol启动。未来MDR confirmation protocol尚未冻结，因此其同类匹配已提前改为排除全部 `wait_and_` 进程；修正后watcher/test SHA为 `e2147b96/b33ff330`，GPU `4/4 PASS`。

MDR pilot现执行14场景×3增强权重共42个clean/robust双模型capture，随后只由权威runner选择一个known-validation权重并执行84项clean加五污染族评估。单个双模型capture约占6至7核、约21 GiB，原runner完全串行会形成新的数小时长尾。新增capture协调器只在权威runner为STOP且其当前子capture已自然完成后运行，跳过该部分目录，以4 workers执行其余冻结命令；每项仍使用protocol绑定的clean/robust trainer、seed331/337、sample fraction、health quantile、CSV/config和运行时SHA。全部42项完成后自动恢复原runner，由原runner逐项复核、选择权重、评估、汇总和独立审计。

捕获加速器/coordinator/test SHA为 `8b529c43/7bcc686b/4e2ce0d7`，目标GPU与MDR confirmation测试合并 `8/8 PASS`，Bash语法通过。当前协调器PID `2698500` 正等待首个权威capture自然结束；MDR capture、weight selection、evaluation、summary和audit正式结果仍为0。因此Pairwise已形成可信相对负结果，但MDR是否能成为最终自有算法仍待pilot和保留种子确认，全面SOTA继续为false。

### 102.52 MDR pilot v1序列化失败、零结果修订与v2重启

首个v1捕获完成clean/robust训练后，在写入 `mdr_runtime.joblib` 时确定失败：动态 `runpy` 名称 `strict_v4_mdr_nested_capture_module` 不可导入，导致 `ConfiguredStructuredRobustClassifier` 不能被joblib定位。权威 `execution.log` SHA为 `cf5f569d...d8c0`，旧protocol文件SHA为 `28231313...e89f`；停止加速会话并让权威runner收割失败后，相关pilot/capture/accelerator进程全部退出。独立计数确认旧根目录完整 `capture_manifest=0`、`evaluation=0`，只保留5个不具正式资格的部分权重目录，禁止复用或覆盖。

修订不改MDR公式、数据拆分、种子、权重网格、选择规则或科学门。新增 `capture_mdr_caeos_runtime_v2.py` 以文件stem作为正式可导入模块名，在执行trainer前注册到 `sys.modules`，并用真实 `ConfiguredStructuredRobustClassifier` 完成joblib dump/load回归；同时新增v2 protocol、runner、accelerator、watcher和独立auditor。目标GPU对原MDR执行、v2回归和捕获加速组合测试为 `12/12 PASS`，仅有既有numexpr/bottleneck版本警告。关键SHA为capture `fd1eb96e...f111`、protocol creator `1ad5f3dd...4cd`、runner `9fbc6847...fc57`、accelerator `12b9cdd9...c4c6`、auditor `ededc0ef...2613`、watcher `9afcbeb4...ab3e`、test `eff94e75...d6fa`。

v2 protocol在全新run/result根目录零正式输出时冻结，manifest/file SHA为 `f8a9191b...e422/9ee00839...18b1`，绑定16个实现及旧失败日志SHA，并显式声明旧完整capture为0、算法公式未改、必须使用新根目录。连续5次GPU/实验空闲观测于17:52 UTC通过，v2 runner PID `3183760` 和首个capture PID `3183887` 启动；协调器PID `3204019` 已STOP runner但保留当前capture继续运行，待首个真实manifest通过序列化与往返校验后才以4 workers补齐剩余任务。截至本快照，v2完整capture和效果指标仍为0，故不能声称修复已被端到端产物确认，更不能声称MDR阳性、最终自有算法确定或全面SOTA成立。

### 102.53 MDR v2确认链兼容与2026-07-25基线刷新

静态依赖审计发现，原保留种子confirmation creator只接受pilot protocol/audit v1；即使v2试点阳性，也会在生成306捕获、1,836评估协议之前被schema门拒绝。新增 `create_strict_v4_mdr_caeos_confirmation_protocol_v2.py` 仅在单次调用内适配pilot protocol v2与pilot audit v2，仍调用原confirmation creator生成既有 `strict_v4_mdr_caeos_confirmation_protocol_v1`，不改102场景、训练种子 `347/349/353`、污染种子 `359/367/373`、单一pilot权重或任何统计门。首次实现因导入时全局替换校验函数污染v1历史测试，合并回归3项失败；已改为 `try/finally` 调用级替换并恢复，v1/v2合并最终 `8/8 PASS`，确认子集 `6/6 PASS`，目标Bash语法通过。

确认v2输入watcher最初写入 `_v2` 结果根，但恶意外部、部署、PARROT与综合审计监听原权威confirmation根。只读复核证明两根的protocol、capture、evaluation、summary、audit、selection均为0后，watcher在零结果边界改为写原权威根，并使用独立 `watcher_state_v2/lock_v2` 保存调度证据；算法与效果门未变。旧v1等待器和短暂存在的旧根v2等待器均在核验PID/命令后停止，当前唯一权威confirmation watcher PID为 `3409896`。creator/watcher/test SHA分别为 `f09856a9...5dc6/970bda2e...df7b/6da4a8e5...df34`，确认正式输出仍为0。

出版社记录同步刷新2025--2026直接领域方法。OLPFF（Information Sciences 753, 123646）、TAO-Net（Neurocomputing 679, 133170）、M3S-UPD和EFC/MGN-OSR均已在本项目分流、审计或pilot中；ETC-IMC（JISA 99, 104433）解决少标注自监督分类，未给出与本论文一致的静态开放集未知攻击拒识协议。刷新没有产生能同时满足作者实现、输入同构、known-only选择和严格五指标的新主表比较器，故正式方法总账保持42，禁止为数量增加第43个低保真适配器。资源继续优先给MDR、保留种子确认、LSNM2024/CICDDoS2019恶意外部、PARROT良性安全和部署效率。

### 102.54 MDR v2首个真实capture通过与v3调度修订

首个v2任务 `cic_iot2023/dos_tcp_flood/weight_0p125` 在约34分钟后形成正式capture manifest。独立调用原runner的 `validate_capture` 复核通过：manifest文件SHA为 `899f82d1...e0ebf`，schema/state为 `strict_v4_mdr_caeos_runtime_capture_v1/complete`；runtime SHA `e79c31a7...ab5c`、evaluation inputs SHA `8e136450...bb7e` 均匹配，prediction序列化前后逐元素一致，risk/probability最大绝对误差均为0，known-validation profile为15项。由此v1 `runpy` 动态模块不可pickle故障已经被真实训练后的端到端产物关闭，不再只是单元测试推断；该结果仅证明运行时捕获有效，不包含pilot测试效果。

首capture结束后，v2协调器尝试启动4路加速，但原加速器的snapshot门硬编码 `run_strict_v4_mdr_caeos_pilot.py`，拒绝实际 `run_strict_v4_mdr_caeos_pilot_v2.py`，错误为 `unexpected MDR pilot runner command`；trap按设计恢复权威runner，后者开始第二个串行capture。失败日志SHA为 `833658a0...7438`，没有并行目录、evaluation或效果结果。因pilot v2协议已经绑定16个实现，未修改任何冻结文件，而是新增v3调度层，仅把runner身份门改为准确的v2文件名，任务矩阵、capture命令、算法、超参、数据、拆分、选择和科学门全部复用。

独立加速修订manifest在1个完整capture、0 evaluation/selection/summary/audit时冻结，canonical/file SHA为 `5772c66b...4540/fbaa560e...a8d1`，绑定首capture SHA、v2失败日志和6个调度实现，并明确 `effect_metrics_read=false`。accelerator/amendment creator/coordinator/test SHA为 `5ac0c72e/63e7c73d/817ca651/bec14193`，GPU与旧执行/加速组合回归 `8/8 PASS`，Bash语法通过。v3协调器PID `3736669` 已STOP runner PID `3183760`，保留第二capture PID `3604543` 自然完成；完成后才会从冻结protocol选择剩余空任务并启动4 workers。截至本快照，完整capture为1、pilot效果输出仍全0，MDR效果与全面SOTA未定。

### 102.55 MDR v3四路捕获正式启动

第二个串行capture在约36分钟后同样形成完整manifest，完整capture总数达到2。v3协调器于2026-07-24 18:59:32 UTC通过runner STOP、无活动直接子进程、pilot v2 protocol SHA和acceleration amendment canonical门，创建并行run `capture_accel_v3_20260724T185932Z`。run manifest canonical/file SHA为 `b3372bf9...f646/846f89fd...b0d7`，绑定pilot protocol `f8a9191b...e422`、design `9e53a1b4...f63f`、4 workers，并在效果评估前精确冻结剩余indices `2..41`共40项。

四个worker PID `4024811/4024812/4024813/4024814` 均使用protocol绑定的 `capture_mdr_caeos_runtime_v2.py`、clean/robust trainer、seed331/337、三权重、原CSV/config和known-only health profile；启动后failure为0、完整capture仍为2。全部40项完成后协调器自动恢复权威runner，runner将逐manifest复核42项、仅凭全部known-validation profile选择单一全局weight，再执行14场景×clean加五污染族共84项测试评估、汇总和独立审计。当前只是调度与端到端捕获成立，尚无MDR效果或full102准入结论。

### 102.56 MDR v3首批四路完成与线程池轮换

首批4个并行任务在共享负载下约47--49分钟完成，完整capture从2增至6，parallel failure保持0。原runner的 `validate_capture` 对4个新增manifest逐一重新验证task identity、weight、runtime artifact SHA、evaluation inputs SHA与roundtrip；文件SHA分别为 `4e0a8e10...9544`、`bd1a9e41...5b0a`、`804defc3...9711`、`f6f0a79f...1047`。四者prediction序列化前后均逐元素相等，risk/probability最大绝对误差均为0。

线程池已自动轮换到 `cic_ton_iot/password` 三权重和 `cic_ton_iot/injection/weight_0p125`，新worker PID为 `1446664/1455020/1527027/1535836`。这证明v3修订不仅能创建run manifest，也能完成、校验、释放任务并继续调度下一批。当前capture进度 `6/42`、evaluation/selection/summary/audit仍为0；未读取known-validation数值、未中途调整worker、权重或门，MDR效果继续未知。

### 102.57 MDR v3第二批完成与浮点roundtrip口径

第二批4项完成后capture进度增至 `10/42`，failure保持0，线程池继续轮换到CIC-ToN-IoT injection与CICIDS2017 ssh_patator。新增manifest SHA为 `54f541b7...b6d8`、`9acb2732...77bf`、`1992e674...f5c0`、`8eb15af5...232a`，原runner `validate_capture` 对task、weight、artifact/input SHA和roundtrip均判为true。

前两项probability往返误差为0，后两项为 `5.551115123125783e-17` 与 `2.220446049250313e-16`；四项prediction均逐元素相等，risk误差均为0，`roundtrip.passes=true`。这是浮点序列化的机器精度舍入且远低于冻结容差，不是capture失败；同时纠正表述边界：正式要求是离散输出精确和连续输出容差内等价，不能把前一批观察到的0误差扩写为所有runtime必须概率字节级0。当前evaluation/selection/summary/audit仍为0。

### 102.58 MDR v3第三批部分完成与良性安全口径

2026-07-25只读复核时，完整capture由10增至12，parallel failure保持0，4个worker继续运行；权威runner PID `3183760` 仍处于协调器预期的暂停状态，v3协调器PID `3736669`存活。新增两项为 `cic_ton_iot/injection` 的weight `0.25/0.5`，manifest文件SHA分别为 `f7e2ea15...b88f1` 和 `bab7add6...6bfb`。独立调用原runner `validate_capture` 对两项均返回true，确认task/weight、runtime artifact SHA、evaluation input SHA和冻结roundtrip门完整。附加诊断字段查询发生SSH超时，因此本报告不推断具体连续量误差；正式通过结论只按validator已有证据记录。

远端evaluation目录仍为0，结果根只有 `execution.log`、`idle_observations.log`、`watcher_state.log` 和 `watcher_stdout.log`，尚无weight selection、summary或audit。故当前仍不能比较MDR与Pairwise/OpenDetect效果。

同时明确恶意检测的良性安全边界：完整开放世界评价需覆盖已知良性、未知良性、已知恶意和未知恶意。PARROT2025只作为320个capture、80个应用的外部未知良性误报测试，禁止参与训练、选参、校准或阈值拟合；即使其false-alert、known-attack assignment、相对OpenDetect误报差和应用覆盖门全部通过，也只能支持“跨域良性误报安全非劣”，不能替代LSNM2024/CICDDoS2019恶意外部泛化或授权全面SOTA。

### 102.59 CLOSR正式出版身份与MalRAG基线分流

2026-07-25最新文献复核确认，TNSM 2026论文 *A Novel Contrastive Loss for Zero-Day Network Intrusion Detection* 提出的开放集扩展就是CLOSR，DOI为 `10.1109/TNSM.2026.3652529`，作者仓库同时公开CLAD/CLOSR训练、评估与Lycos2017协议。官方HEAD为 `79da4d1f...40f8`；本地 `source/CLOSR` 的README、requirements、`train_closr.py`、`eval_closr.py` 和 `losses/closr_loss.py` 与当前上游五项逐SHA一致。项目既有三数据集39任务、官方200轮、known-only协议适配因此获得更强的正式出版身份，但不能以新论文标题再计为第43种方法，也不改变其未通过full102扩展门的既有结果。

MalRAG（arXiv:2511.14129）则是值得写入相关工作的2025开放集恶意流量路线：它对IDS已标记的可疑流构建payload、包长和到达间隔多视图知识库，经检索/剪枝后调用冻结LLM，评价已知与新颖恶意流量precision、recall和normalized accuracy。该人口不含全流量未知良性，输入依赖payload与序列，推理成本也与本项目流级表格方法不同；当前公开记录未验证作者代码。故只登记为异构独立协议候选，不做低保真代理、不增加正式方法数。42方法广度保持充分，新增计算继续优先MDR、恶意外部、PARROT和效率。

### 102.60 MDR进度15/42与capture补充完整性审计

CICIDS2017 `ssh_patator` 三个增强权重全部完成后，MDR pilot capture由12增至15，parallel failure保持0。三个manifest文件SHA分别为 `9d1bdfcf...91cdd`、`8295b438...36660`、`5cf9d766...6a477`；协调器已自动轮换到CICIDS2017 `web_bruteforce` 三权重和Edge-IIoT `uploading`，4个worker持续运行。evaluation、weight selection、summary和audit仍为0。

为避免最终效果audit只重算84项指标而缺少独立runtime工件总账，新增只读补充审计器 `audit_mdr_caeos_capture_integrity.py`。它独立核验v2 protocol/design canonical、protocol绑定实现SHA、42项期望身份、manifest schema/state、runtime artifact与evaluation input文件SHA、roundtrip、known-validation profile元数据及零unknown/test训练选择；实现明确不读取profile中的效果值和任何evaluation/test指标。审计器/test SHA为 `653fa320...0af0b/06128627...1e290`，本地语法通过、GPU目标环境 `2/2 PASS`。

首次快照位于 `results/strict_v4_mdr_caeos_capture_integrity_v1/snapshot_20260724T202901Z.json`，canonical SHA为 `eac5003b...b487`。它对已观察15项给出 `observed_integrity_passes=true`、invalid 0；同时记录missing 27、state `partial_capture_snapshot`、总 `passes=false`。这种分离防止把部分工件完整误写成矩阵完成。该补充审计不改变原protocol、算法、权重选择或效果门；42项齐全后还需重新生成完整快照，且即使完整性通过也不能单独支持MDR效果。

### 102.61 MDR第16项与自动最终capture审计

下一项 `cicids2017/web_bruteforce/weight_0p125` 已形成完整manifest，文件SHA为 `bf31e22b...53c0`，capture总数达到16，parallel failure仍为0、4个worker继续运行，evaluation与正式selection/summary/audit仍为0。重新执行补充审计得到 `snapshot_20260724T203343Z.json`，canonical SHA `7f887136...d478`；16项全部通过身份、实现、artifact/input SHA、roundtrip与泄漏元数据检查，invalid 0，但missing 26，所以总passes保持false。

新增 `scripts/wait_and_audit_mdr_caeos_capture_integrity.sh` 关闭人工漏跑最终审计的调度缺口。脚本SHA为 `3ca9c17b...200df`，远端逐SHA一致、Bash语法PASS，watcher PID `2912864`。它只轮询manifest数量；少于42时等待，多于42时失败，恰为42时调用独立审计器写临时文件，只有canonical正确、observed count为42且passes为true才原子移动为 `final_integrity.json` 并写匹配SHA的completion marker。已有final输出也必须重新验证，禁止覆盖或仅凭文件存在跳过。该watcher不读取任何效果、不干预原runner，也不授权MDR扩展。
