# 2026-08-13 当前硬件 2.79 Mpps 独立证据合同与组合器

## 目标与边界

现有 BCM57810/bnx2x 环境已经观测到 TPACKET B2 在单次 capture-only 运行中达到 `2.794217 Mpps`、零包差、P99/P999 `93/126 us`。该结果来自旧 12 Mpps 突破搜索，既不是同一冻结候选的三次重复，也没有解析、特征、推理、资源、关键流和回退证据，因此不能改写为 full pipeline 或生产发布。

本次新增独立的 `current_hardware_2_79` 资格域，不修改任何旧 10/12 Mpps 合同，也不接入 release manifest、unified audit 或 production Pareto。该资格域只允许证明当前硬件在冻结的 64B、2.79 Mpps 短时运行点具有完整候选证据；输出固定 `production_release_accepted=false` 和 `final_pareto_ingestion_allowed=false`。

## 可执行合同

`configs/current_hardware_2_79_release_profile_v1.json` 冻结以下规则：

- backend 只允许 `xdp_skb`、`tpacket_v3`、`dpdk`；必须先提交哈希绑定且恢复闭合的 XDP 实际探针。
- 每个候选必须提交 normal/fallback 各 3 次，共 6 个互异 raw run；每次至少 15 个完整 1 秒窗口，run ID、generator ID 和 raw 内容 SHA 均必须互异。
- 每一个窗口的 offered/received 都必须不低于 2.79 Mpps；不能用全程平均值掩盖低速窗口。
- NIC missed/errors、socket drops、sequence gaps 必须逐项为零并满足包守恒方程。
- capture、parse、feature、inference、resource、quality 和 fallback 全部从 raw 计数、直方图或 ledger 重算；任何层失败都不能成为候选。
- fallback 的三次 trial 必须唯一、严格递增且不重叠，步骤完整，恢复不超过 300 ms，切换及 fallback 捕获均零丢包，primary 和主机均恢复。
- XDP 只有在完整六重复 full-pipeline 合格后才享有优先权。XDP 不可用或 full-pipeline 失败时，TPACKET 与 DPDK 都必须完成同协议评估，再经过硬门、Pareto 和冻结字典序选择。
- 旧 B2 只允许出现在 `legacy_discovery`，且 `counts_toward_qualification` 必须为 false。

## 信任实现

`hft_mgbs/current_hardware_279.py` 对 profile、evidence manifest、XDP probe 和每个 raw run 使用实际文件 SHA-256。所有候选引用被限制在 evidence root 内，拒绝缺失文件、symlink、SHA 漂移、非有限数值、重复身份和任意层级的 `accepted`/`qualified` 自报字段。

组合器从以下原始材料重算：

- 逐窗 offered/received 和四类丢包计数；
- 四组延迟直方图的保守 nearest-rank P99/P999；
- parse/feature/budget/key-flow/inference 计数；
- 每窗归因到捕获主机及推理服务的 CPU、RAM、GPU、显存样本；
- confusion、降序 score buckets、calibration bins 和事件匹配计数；
- fallback 单调时间区间、步骤、恢复时延和切换丢包 ledger。

## TDD 与结果

实现前测试因 `hft_mgbs.current_hardware_279` 不存在而按预期红灯。实现后 9 项测试通过，覆盖：

- 当前 pending 与 legacy B2 永不计数；
- TPACKET 正向、DPDK 低于 2.79 的同协议淘汰；
- XDP 只有完整合格后才优先；
- 单次/两次重复不能伪装为 3×2；
- SHA 漂移和重新密封的自报 acceptance 均被拒绝；
- 平均吞吐不能掩盖单窗低于 2.79；
- 重复 run identity 和重叠 fallback trial 被拒绝；
- 降低 profile 阈值不能创建新的资格域；
- CLI 在无 `PYTHONPATH` 时可直接运行。

当前输入 `configs/current_hardware_2_79_current_evidence_v1.json` 仅保存旧 B2 discovery，正式 candidates 为空。实际 CLI 返回 `2`，机器审计为：

- `audit_complete=true`
- `legacy_discovery_count=1`
- `legacy_qualification_count=0`
- `candidate_evidence_qualified=false`
- `full_pipeline_qualified=false`
- `production_release_accepted=false`
- `final_pareto_ingestion_allowed=false`
- blockers：`xdp_probe`、`selection.non_xdp_comparison_incomplete`

## 后续接线条件

只有物理机生成并回收 XDP probe、TPACKET 六个 raw runs、DPDK 六个 raw runs，且本组合器重新验证通过后，才可另开变更接入 unified candidate-evidence 阶段。接入时仍须重新计算本 profile、manifest、composer 和输出审计的 SHA，不能复制本模块的布尔结果。
