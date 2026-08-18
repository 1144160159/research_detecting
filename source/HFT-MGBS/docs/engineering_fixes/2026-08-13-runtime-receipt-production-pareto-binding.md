# 2026-08-13 运行时决策收据与生产 Pareto 强绑定

## 问题

生产 Pareto 原先只重哈希统一发布收据与统一审计，但没有直接消费
`capture_runtime_decision` 的收据，也没有从原始运行窗口重算丢包、尾延迟、资源、
关键流覆盖和 DPDK 回退。这样即使上层 JSON 彼此一致，也不能证明运行时门和最终
Pareto 使用的是同一批原始证据。

## 修复

- `decide_xdp_dpdk_runtime.py --raw-runtime-evidence` 生成非发布资格的运行时决策
  收据，绑定 runtime policy、observation 和 raw windows 的文件 SHA-256。
- 最终 selector 重读并重哈希全部文件，按冻结时间重新执行 runtime decision。
- selector 从每个原始窗口重算：最小吞吐、总丢包、nearest-rank P99/P999、CPU、
  GPU、内存、GPU 内存、预算越界、最小关键流覆盖和最大 fallback 恢复时间。
  原始值、observation、候选 metrics 三层必须一致。
- 只有 `keep_xdp`、native AF_XDP zero-copy、三类在线门全通过时，XDP 候选才能
  入选。DPDK 必须同时合格，但仅允许 `dedicated_standby_adapter` 或 maintenance
  回退语义，禁止作为独立生产主后端。
- 冻结算法最优性审计作为独立全局门：selector 重哈希审计文件并要求
  `accepted=true`、`algorithm_only_practical_optimum_proven=true`、证据和成对指标
  完整、winner/practical front 都严格绑定 A09。算法审计不负责、也不要求
  `production_joint_optimum_proven` 或 `final_pareto_ingestion_allowed`；二者由后续联合
  运行证据决定。当前审计为 false，因此当前环境
  保持 fail-closed。

## 当前物理结果

远端 `/home/wangwt/task/datasets/replay/hft_tcp_rss_q2_20260812T165732153923663Z`
的 Q2/TCP 诊断发送与接收均为 15,150,080 包，TX 队列均分，但 RX 队列为
`[15150080, 0]`。P99 11.0035 us、P99.9 151.453 us、零错误且恢复通过，仍因
第二 RX 队列为零而判定 RSS/队列覆盖失败；Q2/Q4 均未解锁。这里只保存远端路径
与证据哈希，不复制数据或伪造本地 receipt。

## 验证

```text
python -m unittest tests.test_capture_runtime_decision tests.test_final_pareto_selector
Ran 36 tests ... OK
```

负向测试覆盖缺失 runtime receipt、全链哈希重新密封后篡改 raw 延迟、DPDK 主后端、
空 RX 队列伪通过、算法审计哈希漂移、伪造 accepted 与 winner/front 不一致。
