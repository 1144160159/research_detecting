# strict-v4 全面 SOTA 与自有算法优化阶段报告

更新时间：2026-07-19

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
