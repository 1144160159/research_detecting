# CAEOS-EMTD评价意见吸收与纠偏记录

## 1. 评价来源与结论边界

- 评价文件：`CAEOS-EMTD评价-20260727.pdf`
- 文件SHA256：`601a1da85be521d8e610f3d9b2e2ff44a3304862365d6e5736b41e8da7fdbdcb`
- 评价范围：公开仓库快照、中文方案文档、`source/CAEOS-EMTD`代码与轻量结果。
- 当前纠偏原则：合理意见立即落地；已被当前实现覆盖的意见补足证据；与当前机器权威状态冲突的判断予以更正；不因评价内容绕过冻结协议或提前选择算法。

评价对研究方向、未知隔离、分组切分、支持/冲突双路径和协议驱动实验体系的正面判断成立。评价指出的公开可复现性问题也成立：本地配置虽为完整JSON，但根目录原有的广泛Git LFS规则会使公开快照只显示指针。

## 2. 需要更正的评价判断

### 2.1 Pairwise不是已经终选的论文最终算法

评价第1、3、7--8页将`CAEOS-Pairwise v1.4.4-paper-freeze`解释为当前最终冻结主算法。该判断基于较早公开快照，与2026-07-27机器权威状态不一致。

当前准确口径为：

1. Pairwise是冻结的稳定参照实现和`provisional incumbent`。
2. KRC、条件RRC和PUG终选链仍未结束，Pairwise不能被表述为已终选算法。
3. 最新KRC原子证据为124/306 capture、744/1836 evaluation、41个完整三种子场景；KRC仍无终态。
4. 全面SOTA机器总账仍有8项科学阻断，`goal_achieved=false`。

因此，评价中基于39任务旧适配结果给出的`0.932796`等数字只能作为历史同协议证据，不能替代当前strict-v4全面SOTA审计，也不能授权把Pairwise写成最终算法。

### 2.2 “配置内容不存在”应改为“公开传输方式有缺陷”

评价第1、4、7、10页指出`configs/*.json`和`requirements.txt`为LFS指针。纠偏核查发现：

- 当前工作区的`mal_tls2023.json`、`hikari2021.json`等配置内容完整；
- 但根目录`.gitattributes`原来同时用`source/**/*.json`、`*.json`和`*.txt`进行宽泛LFS跟踪；
- 因而公开快照出现指针是一个真实的发布工程缺陷，而不是配置设计本身缺失。

本次已在所有宽泛规则之后增加显式文本例外，`git check-attr`确认配置、依赖锁和复现协议的`filter/diff/merge`均为`unset`、`text=set`。

## 3. 已吸收并完成的意见

| 优先级 | 评价意见 | 处理结果 | 当前证据 |
|---|---|---|---|
| P0 | 公开真实配置 | 已完成发布规则纠偏 | `.gitattributes`对`configs/*.json`显式取消LFS |
| P0 | 锁定环境 | 已完成 | `requirements-lock-gpu-cu121.txt`和GPU环境快照 |
| P0 | 两数据集最小复现 | 已实现可执行包，正式结果待运行 | Mal_TLS/Tor、HIKARI/Probing，support/cauchy/nested固定剖面 |
| P1 | 聚焦支持/冲突/验证驱动嵌套路径 | 已吸收 | 新协议不再把大量开发候选并列为论文贡献 |
| P1 | 固定两数据集主线剖面 | 已完成协议和运行器 | smoke为6项，paper为18项，输出逐文件SHA |
| P2 | evidence package部署验证 | 当前已具备，不重复实现 | `verify_evidence_package.py`、部署bundle和selected-system审计链 |

最小复现包位于`source/CAEOS-EMTD/reproducibility/`。`smoke`模式仅验证执行和工件完整性，明确标记`scientific_evidence=false`；`paper`模式固定3个全新种子，输出源码、配置、输入、命令和结果工件哈希。数据CSV仍保留在GPU服务器，不纳入代码仓库。

## 4. 有条件吸收的意见

### 4.1 拆分`train_hybrid_open_set.py`

评价第7、10页关于2876行总控脚本维护风险的判断合理。当前不直接重写正在产生strict-v4权威证据的训练入口，避免改变在途KRC/PUG证据的实现身份。模块化按以下顺序执行：

1. 终选链结束前只增加只读注册表、复现入口和测试，不改变冻结训练语义。
2. 终选后拆分`risk_components`、`risk_selection`和`deployment_package`。
3. 新旧入口必须在冻结输入上逐数组、逐指标和逐工件哈希等价后，才能切换论文默认入口。

这属于已接受但受实验完整性门约束的工程纠偏，不应描述为已全部完成。

### 4.2 Mondrian/类条件conformal支持风险

评价第9--10页建议强化支持风险。该方向与现有方法兼容，但不是尚未实现的新点：

- 当前训练器已经包含`mondrian_support_union`与`mondrian_class_support_union`；
- strict-v4扩展风险筛选已纳入相关支持风险；
- 冻结确认没有通过联合安全门，候选状态为`rejected`或`frozen_unconfirmed`；
- 现有结果显示单纯支持路径在最差套件/留一场景上不稳定。

因此，本次将Mondrian路径保留为负向消融和后续校准研究，不提升为当前自有算法，也不因评价意见重新使用已见测试结果调参。

## 5. 基线纠偏

基线不继续无边界扩张，而分成两层：

| 层级 | 方法 | 用途 |
|---|---|---|
| 经典精简主表 | MSP、Energy、OpenMax、kNN、ViM、Mahalanobis++、OpenDetect | 覆盖置信度、能量、距离、统计与强适配方法；维持冻结7项 |
| 域近邻重点表 | OpenDetect、RoNeTC、ARPL、CADE | 回答恶意流量/多视图/安全漂移领域的直接竞争关系 |

现有39任务域近邻矩阵已经包含OpenDetect、RoNeTC、CADE和CLOSR。其数字是旧版同协议适配结果，不是对方论文原始结果，也不是当前strict-v4五指标全面SOTA结论。后续优先补强RoNeTC和OpenDetect的严格协议证据，ARPL/CADE作为次级域近邻对照；经典7项不因结果强弱事后更换。

## 6. 纠偏后的实验优先级

1. 继续完成KRC 306项、条件RRC和PUG fresh跨套件终选，不读取部分结果做算法选择。
2. 终选后执行selected-system外部恶意、PARROT未知良性安全和同硬件效率三条证据链。
3. 在资源空闲且不干扰终选链时，运行两数据集三路径paper profile，报告AUROC、AUPR、OSCR、FPR95和Known Macro-F1。
4. 补充`temporal_capture_grouped`/跨采集验证，优先验证未来未知与部署漂移。
5. 轻量embedding只做受控插拔消融，不替换冻结树模型主线，不启动大型主干搜索。

## 7. 当前结论

评价已促成真实的可复现性修复和更集中的实验叙事，但没有改变科学结论：Pairwise仍是暂定参照，最优自有算法尚未终选，全面SOTA尚未成立。论文当前可以撰写问题定义、方法框架、无泄漏协议、基线设计和已完成实验事实；最终算法名、全面SOTA结论、外部部署安全和效率结论仍必须等待对应机器门完成。

## 8. 域近邻意见的落实状态

评价后的进一步盘点确认：当前完整102场景开发结果包含OpenDetect，但不包含RoNeTC、ARPL或CADE；旧39任务域近邻数字不能直接补入strict-v4主表。因此采取“少而有说服力”的分层修正：

1. 经典主表维持冻结7项，不扩张。
2. strict-v4域近邻主证据只新增RoNeTC，并与现有OpenDetect组成两方法重点表。
3. ARPL和CADE保留为旧39任务次级参考，明确不授权strict-v4主张。

RoNeTC的7套件102场景、seed 7、同缓存/拆分协议已经在结果为0时冻结，协议canonical为`8ec67d1e...9b50`；独立审计`passed=true`、canonical为`02f22fec...3917`。冻结时102项`metrics/scores/provenance`均不存在，训练未启动。目标机器审计已把它列为第9项阻断，状态为`frozen_zero_result_not_executed`。这项落实吸收了“领域直接竞争证据不足”的合理意见，同时避免把协议准备误述为实验效果。

## 9. RoNeTC证据链的二次纠偏

进一步审查发现，第8节协议虽能启动102项训练，但没有预注册逐场景汇总、独立结果复算和完成标志；中间重冻结版又引用不存在的postselection cache-dir，并会使NF-UNSW从full103的5000上限回退到1500。由于正式结果仍为0，现已在不接触任何RoNeTC效果的条件下完成缓存纠偏和最终重冻结。当前权威canonical为`38807dd2...e656`，协议审计canonical为`8fe711a6...1c96`；第8节`8ec67d1e...9b50`及中间版`5629e2e8...9467`仅作历史记录。

新协议绑定OpenDetect baseline manifest、6个实现文件、3个源证据文件、7组CSV/sidecar SHA、102个任务以及summary/audit/completion四类后处理输出。独立结果审计要求重读原始工件并复算总体、逐套件和胜平负，完成标志同时绑定protocol、summary和audit的canonical/file SHA。GPU联合测试`23/23 PASS`，但所有RoNeTC正式结果仍为0。该补强真正吸收了评价关于可复核性和域近邻竞争证据不足的意见，同时继续维持“协议完整不等于效果完成”的边界。

## 10. 纠偏后的最新运行复核

KRC运行没有因本轮协议和文档纠偏被中断。最新原子快照为140/306 capture、840/1836 evaluation、46个完整三种子场景；独立known-only bottleneck审计`passes=true`，跨套件汇总状态为`valid_partial_diagnostic`，25个完整场景具RRC诊断资格。CICIDS2017已完成五个三种子场景且源安全均通过，但CIC-ToN-IoT的源安全失败仍存在，说明评价所强调的可靠性边界不能用总体均值掩盖。

目标总账canonical/file为`38b59393...565b/d5edf973...4adf`，仍有9项阻断且`goal_achieved=false`。因此本次“吸收合理意见并改正”的完成范围是：纠正结论口径、补齐复现边界、精简并分层基线、冻结RoNeTC严格证据链、保留自有算法探索及其终选门；不是宣告最优自有算法已经产生，也不是宣告全面SOTA已经成立。

## 11. 评价意见驱动的终局编排与运行恢复纠偏

评价强调“工程完整性不能替代科学结论”和“公开结果必须可复核”。沿此边界继续审计发现，旧KRC downstream watcher在KRC阳性时会立即运行KRC专属external、PARROT和效率链，而此时RRC/PUG及必要的双阳性直接锦标赛尚未结束。这会把暂定候选错误地固化为部署算法。现已将该watcher缩减为只生成canonical终态决策和handoff；最终下游统一由selected-system watcher在canonical final activation出现后运行。PUG跨套件watcher同时独立等待pilot，RRC watcher继续按KRC阴性条件接力。该改动直接吸收了评价关于结论边界和证据链完整性的合理意见。

部署过程中也暴露出评价所指的可复现性风险：统一运行时依赖未按闭包原子安装，新`pairwise_runtime.py`短暂先于包含`PUG_RISK_NAME`的依赖落盘，使KRC capture导入失败。事故没有改变冻结protocol或算法语义，但留下154个日志半成品目录。纠偏没有删除这些目录，而是通过新脚本逐目录验证唯一日志、缺失manifest和精确ImportError后，整体迁入带时间戳的隔离区，并保存路径、大小和SHA清单。隔离后原树为152个完整capture、0个半成品，清单SHA为`eb0343cf...dd7/2a5452f7...e8a`。

使用同一冻结protocol恢复后，KRC已越过异常点并发布156/306 capture、936/1836 evaluation的原子快照；52个三种子场景完整，31个具RRC诊断资格，九项不变量和独立known-only audit均通过。progress、bottleneck、diagnostic canonical分别为`41095b5e...9bdfad`、`03ea28c2...7ade8`和`19a11c34...390f`。最新目标总账`57b0c0bd...81f6/f432f3fb...ff35`仍列9项阻断，故本轮纠偏只能表述为“终局编排正确、运行已可审计恢复”，不能表述为KRC阳性、最优自有算法已产生或全面SOTA成立。

尚未吸收完的工程项也明确入账：若上游KRC/RRC与PUG均阳性，直接锦标赛已有冻结设计，但7项执行实现尚缺。该缺口不会影响当前KRC继续运行，却会在未来双阳性时阻断最终算法选择，必须在读取双阳性效果之前补齐；否则“寻找最优自有算法”仍不能闭环。

## 12. 双阳性直接锦标赛工程缺口闭合

第11节记录的是修正前的真实缺口。该缺口现已在没有读取任何双阳性终局效果、直接锦标赛正式输出仍为0的条件下闭合：

1. 激活器只接受canonical目标总账中的KRC/RRC上游终态阳性、PUG跨套件终态阳性和未完成终选三者同时成立；当前条件不满足时只返回pending。
2. 执行协议固定7套件102场景、seeds `809/811/821`、306个同CSV/配置/seed/split的fresh incumbent--PUG配对任务，以及clean、模态完全缺失和高斯漂移三条件共918次评价。
3. incumbent允许KRC或条件RRC。RRC必须由三个fresh seed的known-only证书重新物化；PUG必须按冻结cross-suite控制重新拟合，不复用已见测试结果选择参数。
4. 逐任务评价要求标签、unknown mask、全部视图数组和64位split fingerprint完全一致；同一份损坏数组同时送入两种算法。
5. 汇总按条件、种子、场景、套件逐级聚合并对7套件等权，使用固定seed的10,000次套件/场景区组bootstrap；Known Macro-F1保护、四项未知指标均值、指标广度、套件广度、最差套件和三个条件门均为冻结硬门。
6. 独立审计从306份原始任务记录重读并复算918项评价，验证实现SHA闭包、protocol/summary/audit/file SHA和最终选择一致性。挑战者未过门时合法终态是保留incumbent，而不是把实验写成失败或强制选择PUG。
7. 持久watcher只在双阳性激活后等待所有冲突实验进程为0、load1不超过逻辑CPU数25%、GPU计算PID为0，连续3次通过才以4个外层worker启动；`--once`模式禁止启动。

GPU主项目与目标审计联合回归为`21/21 PASS`，设计冻结、selected-system激活和下游watcher回归为`18/18 PASS`，累计`39/39 PASS`。真实一次性检查状态为`waiting_for_dual_positive_activation`、`launch_admitted=false`；持久watcher PID为`1185946`。冻结设计canonical/file仍为`258605ec...84b/7d313c2f...b0f`，未因实现补齐而重选阈值、seed、套件或指标。

北京时间2026-07-27 21:41的机器总账canonical/file为`83df01c4...bda3/6607da60...f392`，设计冻结与7项实现完整均为true，但KRC正式审计快照仍为`164/306`、PUG fresh 18任务尚无终态，故直接锦标赛当前状态是`not_required`而非已执行。总账仍有9项阻断、`goal_achieved=false`。本节只证明未来双阳性时终选链不会断裂，不证明PUG、KRC或RRC已经获胜，也不授权“最优自有算法已产生”或“全面SOTA已成立”。

## 13. 长跑恢复与RoNeTC自动执行的失败关闭纠偏

评价提出的“复现实验需披露运行状态与失败条件”进一步暴露了两个不能靠人工口头接续的缺口。

第一，KRC恢复协调器主线程在检查`cicids2017/portscan/seed659`时遇到“partial capture requires quarantine”，但该目录随后由仍在运行的旧worker完整写出manifest。这说明故障是协调器与未完全排空worker之间的读取竞态，不是该任务的数据或算法效果失败。主线程已无法继续消费后续future结果或生成终态，但`ThreadPoolExecutor`中预提交的任务仍会由4个线程继续取出并自然排空。新增`watch_strict_v4_krc_coordinator_recovery.py`不删除、不移动也不读取活动中的部分工件：旧协调器或worker仍存在时只计数manifest；全部退出后才调用冻结的原始capture validator逐项检查306任务。若发现非空非法目录，它写入`manual_partial_capture_intervention_required`并停止；只有0个非法目录且连续3轮空闲，才按原protocol、run root、result root和4 workers精确重启。代码/测试SHA为`cc1a232...cf23a/a56e0f6d...1e7a`，定向测试`4/4 PASS`，持久PID为`3744868`。北京时间22:21状态为旧协调器1、worker 4、完整manifest诊断计数219、缺87，仍是`waiting_for_existing_krc_processes_to_drain`。该219不得替代正式原子审计，论文进度仍写`progress_164.json`。

第二，RoNeTC虽然已有权威零结果协议、逐场景汇总和独立审计，但没有持久条件执行器。首次新增的watcher把它排在selected-system统一下游终态之后；进一步核对综合审计发现，该顺序会使activation永久绑定“RoNeTC未完成”的旧目标快照，而综合审计又要求activation时只剩external、PARROT和效率三项阻断，因此即使后续RoNeTC完成也无法通过。现已修正为“最终自有算法终选后、selected-system激活前”运行。watcher重新验证protocol canonical `38807dd2...e656`、协议文件SHA `cb7085c8...c186`、协议审计canonical `8fe711a6...1c96`及102个任务身份；无provenance却存在metrics/scores的目录会失败关闭，有匹配provenance的中断任务才允许原runner恢复。它还要求冲突进程为0、load1不超过逻辑CPU数25%、GPU计算PID可观测且为0，连续3轮通过后才依次执行训练、summary、独立audit、completion和总目标审计刷新。

修正后watcher/激活器SHA为`a28caa25...bc73/3da2b448...28e9`。selected-system激活器现在只有在经典7项完整、RoNeTC终态、最优自有算法终选、文档快照有效、选择后经典五指标和两类污染门均通过，且blocker集合精确等于external/PARROT/效率三项时才写入不可逆activation；其余合法未完成状态返回pending。GPU联合回归覆盖RoNeTC、activation、selected watcher、综合审计和目标总账并通过。真实检查确认102项metrics/scores/provenance均为0、非法半成品为0，新持久PID `2291917`状态为`waiting_for_final_self_algorithm_selection`，没有启动训练。

第三，目标总账原先用`project_root.parent.parent/方向分析/...`验证文档。这在Windows源工作区成立，在GPU目录布局下必然不存在，使`documentation_updated`永久为false。新增文档快照生成器固定复制README、核心矩阵、阶段报告和本评价记录四份文件，逐文件绑定相对路径、字节数和SHA，并生成canonical manifest；GPU审计只接受四文件实际快照与manifest逐项一致，拒绝绝对路径、`..`和文件篡改。生成器/总账SHA为`1bf2bee5...d309/dd5e2568...2dce`，首版快照canonical/file为`eced263b...fdd0/c49e58f8...632f`，GPU总账已验证`documentation_updated=true`。该修复只证明指定文档字节已经同步，不是效果证据；目标总账仍为9项科学阻断、`goal_achieved=false`。

## 14. 最终候选激活前的经典基线与污染重证

进一步检查9项阻断的算法身份发现，现有“对经典7项严格五指标”“五族绝对污染”和“相对OpenDetect污染”三份审计都固定锚定Pairwise。如果最终算法是KRC、RRC或PUG，沿用这些证据会把Pairwise的失败归给最终候选，或反过来把Pairwise的局部成功冒充最终候选成功。评价提出的“基线和鲁棒性证据必须与方法主张一致”因此不能只靠修改文字解决，必须做终选后的算法无关重证。

结果产生前已经冻结`strict_v4_selected_system_preconfirmation_design_v1`。它复用KRC协议的7套件102场景和seeds647/653/659任务宇宙，要求306个最终候选fresh捕获和306个fresh OpenDetect捕获；同一clean训练任务产生MSP、Energy、OpenMax、kNN、ViM、Mahalanobis++六份报告，OpenDetect单独fresh训练。五个污染家族固定为modality missing、field missing、row missing、feature shuffle和Gaussian drift，固定severity、模态选择规则与原协议一致；每个306任务形成5条candidate--OpenDetect配对记录，共1530条。聚合顺序固定为种子、场景、套件并对7套件等权，10,000次bootstrap只作冻结统计门。

design canonical/file为`193dfe33...838a/690b372e...d51a`；独立设计audit canonical/file为`097b97e7...7b60/30f8cc4e...132c`且`passed=true`。creator、preactivation writer、auditor和测试SHA分别为`9905a00a...7471/700022ac...07a0/1e7a752e...a337/1113db05...435e`。Windows和GPU从同一输入独立重建后canonical和文件SHA逐字节相同，GPU与目标总账联合定向测试`30/30 PASS`。真实预激活入口返回`pending_final_self_algorithm_selection`，未写activation；正式protocol、306/306捕获、1530记录、summary、effect audit和completion均为0。总账明确记录design frozen、terminal false和剩余实现0/6，因此本节只锁定了未来比较方法，没有减少当前9项阻断。

## 15. KRC真实终态与“有选择的SOTA”口径纠偏

KRC已从长跑进度转为正式阴性终态：306个capture和1836项evaluation完整，独立audit逐文件复算。四个未知指标总体有向均值和bootstrap下界为正，但只在2个primary套件形成足够激活覆盖，未达到冻结的跨套件最低门；feature-shuffle复合增益还出现`-0.000109`的小幅负值。合法选择是保留Pairwise并进入RRC，而不是删除覆盖门后宣布KRC获胜。该结果同时说明评价中关于“不能用总体平均掩盖适用边界”的意见是合理的。

进一步澄清旧audit字段`decision_matches_summary=false`：其代码定义不是“summary与audit内容相等”，而是“独立audit所有门通过且KRC效果阳性”。补充审计canonical `2ae1c380...b881`验证13项结构检查全过、唯一效果失败项为启用套件覆盖、Pairwise选择遵守冻结规则，`no_summary_audit_selection_inconsistency=true`。因此该false是预期的科学阴性标志，不是证据链冲突；RRC回退仍是唯一合法控制流。

RRC首次执行因OpenBLAS线程池越界段错误，当前用四类数值库单线程和outer worker1恢复。2026-07-28 10:33的可核验证据为base/runtime `12/249、10/249`，certificate/evaluation `0/83、0/1494`；11:00已推进为`12/249、12/249、4/83、72/1494`。规范快照继续验证到base `14/249`，其余计数不变，四类invalid/pending均0；持久观察器PID `3618677`每300秒刷新，真实state canonical为`1cae7a19...c1b`，逐文件绑定SHA并明确不聚合、不断言部分效果。这证明4个场景完成证书与六条件评价，但没有正式summary/audit。因此评价纠偏后的实时汇报采用“文件计数+进程状态+失败原因+规范快照”，不从部分工件提前推断效果。PUG暂存则通过哈希门拒绝旧依赖，重建13文件闭包和canonical协议后才重新进入资源等待，未与RRC抢占资源。

评价原文对“全面SOTA”的质疑也被吸收为结果前声明阶梯，而不是结果后改口径。最高层继续要求经典7项五指标、绝对污染和相对污染三门全部通过；窄口径一固定为7套件AUROC/AUPR/FPR95对经典7项的统计优势并保护Known Macro-F1；窄口径二固定为五族绝对鲁棒门与相对OpenDetect门同时通过。GPU测试证明五指标门失败时，只有预注册窄口径自身全部条件满足才会产生窄口径授权字段，且`comprehensive_sota_authorized`保持false。该纠偏允许论文形成有边界的强结论，同时禁止把局部优势扩写成全面SOTA。
