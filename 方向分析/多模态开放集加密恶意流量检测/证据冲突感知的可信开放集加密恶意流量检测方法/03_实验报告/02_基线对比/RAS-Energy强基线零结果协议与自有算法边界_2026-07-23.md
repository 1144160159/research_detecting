# RAS-Energy 强基线零结果协议与自有算法边界

## 1. 补齐目的

RAS 是 post-30 目录中的第九个强基线家族，用于检验“按 ID 激活秩参考替换特征后再做能量检测”是否优于冻结 MLP Energy 和 OpenDetect。它不属于 CAEOS 自有算法，不改变 `CAEOS-Pairwise` incumbent 或 `CAEOS Selective Topology Uplift` 第四候选的身份与确认顺序。

论文来源为 <https://arxiv.org/abs/2604.08572>，官方实现为 <https://github.com/gigug/RAS>，冻结参考 commit 为 `313d8e09d4e7d513e66fca707adfc2fcd6ecbf08`。本适配没有复制未知标签选择或 OOD 超参数搜索。

## 2. 忠实适配

对每个冻结表格 MLP 场景，仅从已知训练集收集最终 embedding。设第 `i` 个训练样本的升序激活向量为 `sort(h_i)`，固定参考 profile 为

`m = mean_i sort(h_i)`。

对查询 embedding `h`，先取得其稳定升序索引，再把 `m` 的各秩值散射回对应原坐标，得到 `h_RAS`。分类 logits 与开放集分数均从 `h_RAS` 重新计算：

`z_RAS = W h_RAS + b`，`score_ID = logsumexp(z_RAS)`。

部署拒绝阈值只使用已知验证集。未知类和测试标签不进入 profile、阈值、参数或场景选择。stable ascending mergesort 只固定并列激活的确定性次序，不引入可调超参数。

官方后处理器使用替换后 logits 产生类别预测，所以本适配也使用 `argmax(z_RAS)`。因此不能套用“后处理不改变 Known F1”的假设，必须同时审计闭集预测退化。

## 3. Pilot 与扩展门

pilot 使用 coverage manifest SHA、套件名和盐 `ras-eccv2026` 做确定性索引，在七套件各选2个场景，共14场景；选择过程不读取任何指标。比较方法固定为 `RAS-Energy / MLP-Energy / OpenDetect`。

只有以下检查全部通过才允许运行 full102：

1. 14/14 指标完整、失败0，三方 split fingerprint 一致。
2. Eq.7/Eq.8、官方 commit、known-training profile、known-validation threshold、shifted-logit prediction 和无 OOD sweep 均通过实现校验。
3. 验证和测试 RAS 分数在全部14场景中非恒定。
4. RAS 相对 MLP Energy 的 Known Macro-F1 平均差不低于 `-0.02`，最差场景差不低于 `-0.10`。
5. shifted-logit 与原 MLP 测试预测平均一致性不低于 `0.95`。
6. 三方法四项未知指标平均排名不高于2；相对 MLP Energy 至少3/4指标平均正增益，四指标有向均值严格为正。
7. 至少5/7套件四指标均值非负，最差套件不低于 `-0.03`。

该门只决定是否投入102场景开发预算，不是确认性 SOTA 结论。阳性后还必须生成独立 full 协议、102份指标、`full_analysis.json` 和 `full_complete`；阴性保留完整负结果并停止扩展。

## 4. 冻结与运行状态

远端项目根为 `/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717`。RAS pilot 目录为 `results/strict_v4_ras_energy_pilot_seed7`，full目录为 `results/strict_v4_ras_energy_full102_seed7`。

protocol/gate 在正式指标0时冻结为：

- protocol: `c72856ad408c3688ac2a9c63081eb70b38f12c610e69dd60ee13f68392d055f1`
- gate: `2c279875d5a7c83cb4baf940fc0c2d6f3943c569b90934e4db1049a833421426`

实现 SHA、protocol/gate、post-30 family spec 和外部设计四层交叉绑定通过；远端相关测试 `19/19 PASS`。RAS watcher PID `1105387` 等待 Fisher-Rao 完整分支，不提前占用资源。UTC `2026-07-22 16:58` 时 pilot/full 指标仍为 `0/0`。

## 5. 结论边界

当前可以写入论文的是 RAS 的理论来源、忠实适配、无泄漏协议和预冻结扩展门。当前不能写 RAS 优于 MLP Energy、RAS 优于 OpenDetect、RAS 已完成102场景、RAS 支持自有创新，或整个方法已经全面 SOTA。

自有算法探索继续独立推进：`CAEOS-Pairwise` 保持 incumbent；Selective Topology 只有在14场景 pilot 与三保留种子 full102 确认均通过后，才有资格改变统一算法选择。外部强基线数量不能替代这一创新证据。
