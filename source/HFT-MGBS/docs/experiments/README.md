# HFT-MGBS 实验留存索引

> 2026-08-13 语义校正：`current_environment_unified_release_audit_v2.json` 仅证明候选证据/全流水线并控制 Pareto ingestion，不执行最终选择；`current_environment_production_pareto_audit_v1.json` 才是唯一可产生 Champion 与 `production_release_accepted=true` 的阶段。当前两者仍 fail-closed。

本目录记录受控候选、冻结变量、硬门限、原始证据路径、选择/拒绝原因和后续
动作。实验报告不能把 diagnostic-only 结果升级为生产资格。

- `2026-07-30-xdp-load-boundary.md`：在已知 0.01 Mpps 通过、0.05 Mpps
  失败的区间内，用 0.02/0.03/0.04 Mpps 三个候选确定当前 XDP 诊断上界。
- `2026-07-30-ten-mpps-r0-scaling.md`：记录 Rust R0 从 XDP、受控发生器到
  DPDK Q1/Q2 的逐级扩展、停止规则和当前硬件/驱动上界。
- `2026-07-31-dpdk-dual-pf-authorized-repeat.md`：记录明确授权后的 DPDK 双
  PF Q1/B128/1 Mpps 重复通过，以及 5 Mpps 在 PF 解绑前被 CPU/SMT
  空闲门阻断的完整证据。
- `2026-07-31-gpu-service-25150-reactivation.md`：记录密钥认证恢复、50051
  服务健康、50052 尚未成链、源码漂移和审计计数污染边界。
- `2026-08-12-dpdk-q1-release-accepted.md`：记录 release gate v2 修复后的
  Q1/1 Mpps 正式 acceptance、证据哈希、完整恢复及仅限 R0 capture-only 的边界。
- `2026-08-12-tpacket-v3-finite-search.md`：记录 TPACKET_V3 实现、1 Mpps
  零丢包/时延矛盾、pktgen 2.784 Mpps 上探和当前硬件无最终 Pareto 的停止结论。
- `2026-08-12-throughput-breakthrough-and-hardware-gate.md`：记录 QM8/IRQ 对齐后的
  2.794 Mpps 零丢包结果、DPDK 12 Mpps 失败及新硬件验收门。
- `2026-08-12-unified-audit-and-bottleneck-analysis.md`：用三份哈希绑定观测区分发生器
  受限与单队列路径受限，并给出统一生产发布门的当前 fail-closed 结论。
- `2026-08-12-current-environment-10mpps-execution.md`：记录独立 testpmd Q1
  2.5697 Mpps 上限、Q4 资源门停止、Rust 热路径 1 Mpps 运行验收以及达到
  10 Mpps 所需的硬件/多队列部署基线。
- `2026-08-12-xdp-dpdk-pareto-control-convergence.md`：汇总 strict XDP/DPDK
  决策、Rust 真实编译、最后一次 Q4 预检、R1--R4 原始重算及当前空 Pareto 前沿。
- `2026-08-13-stock-tcp-rss-q2-execution.md`：记录 stock bnx2x 隐式 TCP RSS
  对称 Q2 数据面、P0 加固、三次 CPU/SMT 门前阻断及第四次实际诊断；TCP 多流仍为
  RX `[15,150,080, 0]`，由此冻结当前网卡多队列分支并转入换卡验收。
- `2026-08-13-unified-algorithm-optimality-gate.md`：统一发布审计直接重算并哈希绑定
  受控算法搜索；当前全 10 候选证据不完整，因此算法、发布和最终 Pareto 均保持拒绝。
- `2026-08-13-algorithm-evidence-access-three-route.md`：记录从本机、物理机中继和本地/
  物理镜像三路只读回收 A01--A10 证据的实际结果；GPU 25696 拒绝、内网 22 身份未受信，
  未绕过主机校验，十候选证据仍按 fail-closed 处理。
- `2026-08-13-algorithm-evidence-access-three-route.json`：上述三路访问的机器可读回执，
  明确 `retrieved_candidate_evidence_count=0`，防止把路径引用当作已取得证据。
- `current_algorithm_optimality_audit_v1.json`：机器可读的 10 候选最优性审计；仅 A09/A10
  有成对三重复指标，A09 为 finalist practical winner，但全搜索最优性为 false。
- `current_environment_production_pareto_audit_v1.json`：由生产联合 Pareto CLI
  对当前环境两项 fail-closed 候选实际生成的机器可读审计；当前前沿为空且无
  Champion，不能作为生产最优声明。
- `current_environment_unified_release_audit_v2.json`：统一审计 CLI 的当前机器可读
  结果；R0、R1--R4、20 项派生指标、全流水线与生产发布均保持 false。
