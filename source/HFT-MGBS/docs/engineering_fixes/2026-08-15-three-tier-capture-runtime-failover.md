# 三层捕获运行时切换

## 结论

新 NIC 生产线仍采用 `native_af_xdp_zerocopy` 主路径和 `dpdk` 生产备用路径。
现有 BCM57810 双口不再被当作生产候选，而是版本化为
`current_tpacket_v3_bcm57810` 降级服务连续性兜底。控制面支持双向切换和失败回滚，
但任何切入 BCM57810 的回执都固定：

- `degraded_mode=true`；
- `production_sla_qualified=false`；
- `release_qualification=false`；
- `final_pareto_ingestion_allowed=false`。

因此，兜底可维持服务，不会把当前硬件过去的诊断结果冒充新生产线资格。

## 优先级与触发边界

固定优先级为：

1. `native_af_xdp_zerocopy`；
2. `dpdk`；
3. `current_tpacket_v3_bcm57810`。

只有捕获后端故障可以触发切换。关键流覆盖失败或运行时资源/预算安全失败必须
`stop_fail_closed`，不得通过切换捕获后端掩盖。BCM57810 的代码门槛冻结为至少
2.60 Mpps、8 个活动接收队列、零丢包、恢复验证、管理面隔离和二进制 SHA 绑定；
这些门必须来自切换当时的 live preflight，而不是由静态配置自报通过。

自动切换还要求外部控制面同时给出：

- `traffic_quiesced`；
- `state_snapshot_verified`；
- `target_preflight_passed`；
- `rollback_ready`；
- 精确授权 `I_AUTHORIZE_CAPTURE_RUNTIME_FAILOVER_V2`；
- SHA-256 固定的执行计划及每个可执行文件/依赖文件身份。

同 PF 或同适配器全部 PF 重绑定仍属于维护窗口操作，不能自动执行。

## 代码边界

- `hft_mgbs/capture_runtime_failover.py`：v2 非变更决策器和密封决策回执。
- `hft_mgbs/capture_runtime_failover_executor.py`：快照、目标健康检查、启动、停源、
  后验快照和回滚。
- `scripts/decide_capture_runtime_failover.py`：决策 CLI。
- `scripts/execute_capture_runtime_failover.py`：显式授权执行 CLI。
- `configs/capture_runtime_failover_policy_v2.json`：三层冻结策略。
- `configs/current_bcm57810_failover_observation_v2.json`：当前现场的 fail-closed
  模板；它故意不把历史诊断直接标为 live ready。

现有 `xdp_dpdk_runtime_policy_v1.json`、Python v1 决策器和 Rust 共享 golden 均不改，
避免改变已冻结的 XDP/DPDK 证据语义。v2 控制器以外部进程操作方式切换三个数据面，
因此不要求在一个 Rust 二进制中同时链接 AF_XDP、DPDK 和 TPACKET。

## 调用顺序

先由监控/预检生成新的 observation，再只做决策：

```bash
python3 scripts/decide_capture_runtime_failover.py \
  --policy configs/capture_runtime_failover_policy_v2.json \
  --observation /sealed/live-observation.json \
  --now-utc 2026-08-15T00:00:05Z \
  --seal-receipt \
  --output /sealed/decision-receipt.json
```

只有 `transition_permitted=true` 时，控制面才可使用外部钉住的执行计划：

```bash
python3 scripts/execute_capture_runtime_failover.py \
  --policy configs/capture_runtime_failover_policy_v2.json \
  --observation /sealed/live-observation.json \
  --decision-receipt /sealed/decision-receipt.json \
  --execution-plan /approved/failover-plan.json \
  --trusted-plan-sha256 "$TRUSTED_PLAN_SHA256" \
  --authorization I_AUTHORIZE_CAPTURE_RUNTIME_FAILOVER_V2 \
  --work-dir /run/hft-mgbs/failover-run \
  --output /sealed/execution-receipt.json
```

执行器要求执行计划包含三个后端的 health/start/stop、snapshot 和 rollback 共 11 个
精确操作。目标启动后先复验健康，再停止源后端；任一后验失败即运行 rollback，并用
快照证明恢复到原后端。

## 当前状态

代码切换能力已就绪；真实切换仍保持 `live_transition_qualified=false`。原因是生产新
NIC 尚未到位，而且当前 BCM57810 还需要在正式启用前生成一份新鲜的 live preflight
和执行计划。这个边界不妨碍代码先部署，也不允许提前声称生产 SLA 已验证。
