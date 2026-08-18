# MEDAF baseline admission audit

更新时间：2026-07-24

## 结论

MEDAF（AAAI 2024）是代码完整的通用开放集多专家基线，但官方实现不能原样进入 strict-v4。官方源码快照和训练机制可以固定；默认 F1 阈值消费 known-test 与 unknown-test 标签，训练期间每个 epoch 都读取两套 test；2D 卷积空间注意力也不等于当前有序流级表格/多视图输入。后续只有以 `MEDAF-Tabular adapter` 明确命名并在零结果时冻结无泄漏协议，才允许进入小型 pilot。

## 官方身份

- 论文：Exploring Diverse Representations for Open Set Recognition
- 会议：AAAI 2024
- DOI：`10.1609/aaai.v38i6.28385`
- 论文页面：https://ojs.aaai.org/index.php/AAAI/article/view/28385
- 官方仓库：https://github.com/Vanixxz/MEDAF
- 固定 commit：`5d5328333af1f0857b9de20e94063ca8e6353d16`
- tracked 文件：16
- 离线 Git bundle：988,683 字节
- bundle SHA256：`6c0269753ef038f4cef5777ac18543bb145cabb43056b58898209554045378c4`
- GPU checkout：`/opt/data/private/wangwt/ParkAttackKE/third_party_sources/MEDAF-5d532833`

本地和 GPU checkout 的 HEAD 一致、工作树干净。首版审计错误使用工作树字节 SHA，Windows CRLF 与 Linux LF 造成 canonical 分歧；两端失败工件均保留。v2 改为 canonical Git blob 内容 SHA，方法、准入门和模型结果均未改变。

## 源码契约

官方核心包含三个专家分支、attention diversity loss、样本自适应 gate 和 gated MSP 分数。默认配置为 `score_wgts=[1,0,0]`、`branch_opt=-1`、`gate_temp=100`、`lgs_temp=100`。训练函数本身只读取 training loader。

但 `core/test.py` 把 known-test 和 unknown-test 组合成 `open_labels`，调用 `roc_curve(open_labels, prob)`，再选择 `TPR` 最接近 0.95 的阈值计算 Macro-F1。`osr_main.py` 每个 epoch 调用该 evaluation。源码没有 known-validation loader；还不报告 strict-v4 所需的 FPR95、OSCR 和 ECE。AUROC/AUPR 本身是阈值无关报告，但默认 Macro-F1 不能作为 strict-v4 无泄漏结果。

## 适配前置条件

1. 明确命名为 `MEDAF-Tabular adapter`，不得称作者原生复现。
2. 在任何效果产生前冻结表格/多视图 attention map 定义。
3. 保留三专家、diversity loss、自适应 gate 和 gated MSP 核心。
4. 模型只拟合 known-training，拆分保持 group-disjoint。
5. 阈值与所有适配超参数只使用 known-validation。
6. 训练与选择阶段不得读取 known-test 或 unknown-test。
7. 报告 Known Macro-F1、AUROC、AUPR、FPR95、OSCR 与 ECE。
8. 先预注册跨套件小型 pilot 和扩展门，不直接运行 full102。

## 证据

- v2 audit canonical：`1a0ec766026dcbc86a6d1987c870076a3f31208460a1e56736982ea557aba2f6`
- v2 audit file：`1cb49716180f1b5535531928524aaee5a63c107dbd6f2f88641039bca32d3042`
- auditor SHA：`4193859ba47ead48145f9fa102ebd5b2117a4fd86b3b97f34c824a9853db2595`
- test SHA：`a2f1b2906ed4446bbb3c9055501195c52151bd9e275288a1c8d2ad8642dbbf40`
- 本地/GPU测试：`2/2 PASS`
- 冻结时模型结果：0
- `native_medaf_strict_v4_execution_admitted=false`
- `named_tabular_adapter_candidate=true`
- 正式方法增量：0

## MEDAF-Tabular结果前设计

在任何适配结果产生前，已实现表格核心与known-only训练器并冻结设计。共享表格编码器对应官方共享前层，三个独立专家使用“目标类分类权重乘专家嵌入”构造类条件激活图；多样性项严格复用官方的归一化、中心化、ReLU及三对余弦求和。独立gate使用自己的编码器，并只融合detach后的专家logit。训练损失固定为 `0.7 × 三专家CE之和 + 1.0 × gate CE + 0.01 × diversity`；gate与logit温度均为100。训练固定150 epoch、SGD 0.1、momentum 0.9、weight decay `1e-5`、epoch130衰减，不做checkpoint选择。

训练循环函数签名只包含model、known-training loader、device与固定优化参数，不能传入validation/test。known-validation只在训练结束后确定95%已知接受率阈值，known-test与unknown-test只服务最终六指标。目标环境的结构、梯度隔离、官方损失、CAM多样性、概率风险和known-only一轮CPU smoke共 `5/5 PASS`；设计/零结果/确定性场景选择测试 `3/3 PASS`。

设计以coverage manifest、官方commit、suite和scenario的SHA256排序为每套件选择2个场景，共14场景；固定training seed383。pilot同时要求同拆分 `MEDAF-Tabular / MLP Energy / OpenDetect` 三方法，共42报告。扩展门要求零失败、拆分一致、无泄漏、风险与gate非退化、至少2/4未知指标优于Energy、四指标平均有向增益为正、平均秩不高于2、相对OpenDetect的Known F1均值退化不超过0.03、至少4/7套件相对Energy非负且最差不低于-0.05。

- design canonical：`e8c83252483abd0f2b99090e347e4373e349b23478ab5ab0558693d0ab2305db`
- design file：`9dfd9104ef0323f0cd662c64dd245f8066b63e465ce98420fed05258604192bf`
- model/trainer/design creator SHA：`398aa95b...5a01/ae9f007c...b71e/c90b1198...cde4`
- 冻结时适配结果：0
- `pilot_execution_admitted=false`
- `full102 execution_admitted=false`

当前仍缺42报告执行协议、可恢复同拆分runner、canonical汇总/独立审计和排在现有Pairwise/MDR队列之后的资源watcher。设计冻结不等于MEDAF-Tabular有效，也不增加正式方法数。

## MEDAF-Tabular零结果执行链

上述缺口已在任何MEDAF结果产生前关闭。正式协议绑定14个冻结场景的seed137来源CSV/config及Pairwise、MLP、OpenDetect provenance，但执行时三方法统一用fresh seed383重新拆分和训练。MEDAF固定150 epoch最终checkpoint；MLP只选择fresh score suite的Energy报告；OpenDetect使用固定100 epoch配置。每个任务以 `suite/scenario/method` 写canonical run manifest，绑定完整命令、metrics SHA、split fingerprint、known-only选择门和MEDAF风险/gate诊断。

汇总器只接受42份唯一报告、零未解决失败、每场景三方法拆分一致、无unknown/test选择且MEDAF风险/gate 14/14非退化；随后按预冻结门计算四项未知指标相对Energy的有向增益、三方法平均秩、相对OpenDetect的Known F1退化和7套件增益。审计器独立重读42份metrics及MEDAF scores，精确重算summary并复核协议绑定实现SHA。

- execution protocol canonical：`b1ee20011392d31e80766114145ffc0a2f5ce52e6fcb9ca62b76d31728a8bc25`
- execution protocol file：`40b6f62ca0b81fbc7d260e33bec5a7da3b70e3cf573a5995ff522624b2626225`
- creator/runner/summarizer/auditor SHA：`24b46505...f1e46/eb166ae2...980f/7645441a...f28d/9f56d172...fa43`
- watcher/test SHA：`f65b9c59...9819/e4b71134...e9a`
- 协议绑定实现：13个（含watcher与chain test）
- 本地/GPU新增文件SHA差异：0
- GPU合并回归：`14/14 PASS`
- watcher PID：`2021310`
- 资源顺序：Pairwise比较summary → MDR pilot → 连续5次空闲 → MEDAF
- 当前MEDAF metrics/summary/audit：`0/0/0`
- `pilot_execution_admitted=true`（仅协议层）
- `full102 execution_admitted=false`

该执行链只授权排队运行，不证明适配有效。阳性pilot也只能写下一阶段设计需求，不能自动启动full102；阴性pilot必须保留canonical summary/audit并停止扩展。
