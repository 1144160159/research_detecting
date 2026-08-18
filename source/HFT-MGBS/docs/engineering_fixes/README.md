# HFT-MGBS 工程修复留存索引

- `2026-08-13-two-stage-candidate-pareto-release-gate.md`：把统一候选证据资格与最终生产 Pareto 发布拆为两个可达、哈希绑定且 fail-closed 的阶段；只有实际 Champion 才能获得最终发布。

本目录记录 HFT-MGBS 内部的每项工程修复。每条记录必须包含问题现象、根因、修改范围、验证证据、性能影响、回退条件与遗留风险；只读上游 `traffic-analysis-platform/rust` 不允许修改。

- `2026-08-13-new-high-speed-nic-arrival-acceptance.md`：冻结默认只读 inventory/preflight、显式授权能力探针和 fail-closed 恢复合同；当前无新 NIC 时只输出 `hardware_pending`。

- `2026-07-30-physical-diagnostic-gro-reconciliation.md`：物理双口诊断证据隔离与 GRO 计数对齐。
- `2026-07-30-xdp-umem-multiqueue.md`：XDP 优先路径的 UMEM 清理与多队列适配。
- `2026-07-30-ebpf-evidence-reproducibility.md`：固定 eBPF 构建上下文并把源文件纳入运行证据。
- `2026-07-30-joint-resource-evidence-binding.md`：XDP 物理运行与 GPU 节点资源的同场时间绑定。
- `2026-07-30-xdp-runtime-capture-fallback.md`：XDP poll 故障后的同进程 AF_PACKET 回退、恢复和清理。
- `2026-07-30-release-schema-current-state.md`：消除 ens8、XDP 与发布/进度文档之间的旧状态漂移。
- `2026-07-30-xdp-receive-batch-control.md`：把固定 XDP receive/refill 批量改为有界可审计候选，并按硬门限受控筛选。
- `2026-07-30-xdp-multiqueue-idle-poll.md`：修复 8 个 XSK RX 队列空闲时只监听单一 fd 的就绪遗漏。
- `2026-07-30-xdp-fill-ring-priming.md`：分离初始 fill 深度与 receive batch，启动时完整预填 2,048 个 ring slot。
- `2026-07-30-xdp-hot-path-allocation-tracking.md`：消除 descriptor/refill 逐批分配，并用稠密位图替代逐包帧哈希。
- `2026-07-30-xdp-borrowed-capture-probe.md`：新增 UMEM 借用式 capture-only 探针，隔离原始接收与完整流水线成本。
- `2026-07-30-fastpath-sync-path-correction.md`：记录首次定向 SCP 的目录误投、精确清理与防复发规则。
- `2026-07-30-xdp-per-queue-workers.md`：把 8 个 XSK RX queue 拆为 NUMA 本地一队列一线程，并保留可恢复所有权。
- `2026-07-30-synthetic-multithread-injector.md`：用 NUMA 本地 8 线程预构建 64B 包替换单线程 PCAP 发生器的吞吐瓶颈。
- `2026-07-30-packet-tx-ring-generator.md`：在 5 Mpps 发生器触顶后切换到内存映射 `PACKET_TX_RING` 并保留失败证据。
- `2026-07-30-bnx2x-tx-coalescing-control.md`：对发送口 TX 中断节流做两个有界候选并保证异常退出自动恢复。
- `2026-07-30-af-xdp-tx-generator.md`：新增每队列独占 UMEM 的 AF_XDP COPY-mode 发送候选，分离 AF_PACKET 上限。
- `2026-07-30-dpdk-bnx2x-bootstrap-preflight.md`：隔离构建固定 DPDK 版本并对双 PF 解绑风险做只读预检。
- `2026-07-30-rust-dpdk-r0-fastpath.md`：新增与原 crate 隔离的 Rust DPDK 双口 R0 发生/抓包快路径。
- `2026-07-30-dpdk-disruptive-validation-rollback.md`：对双 PF DPDK 验证加入显式授权、全状态快照和失败自动回绑。
- `2026-07-30-dpdk-doc-sync-path-correction.md`：记录 DPDK 实验文档误投、精确删除和分目录重同步。
- `2026-07-31-dpdk-static-pmd-world-writable-path.md`：把 bnx2x PMD 静态链接进 Rust 二进制，消除 world-writable 祖先目录导致的动态插件安全拒绝。
- `2026-07-31-dpdk-dual-port-startup-hugepage-cleanup.md`：修复直连双口的顺序启动死锁，并用 RAII 与运行前缀定向清理保证大页完整回退。
- `2026-07-31-dpdk-perf-evidence-path-correction.md`：纠正 perf 自匹配与旧证据目录误投，精确清理无样本文件并加固运行目录选择。
- `2026-07-31-dpdk-rust-multiqueue-rss.md`：把单队列 Rust DPDK 扩展为每队列独占线程与硬件 RSS/TSS，按 Q2/Q4 受控扩展。
- `2026-07-31-dpdk-realtime-worker-isolation.md`：为物理机并发负载下的 DPDK 收发线程增加默认关闭、有界且可回退的实时调度隔离。
- `2026-07-31-dpdk-bnx2x-rss-capability-advertisement.md`：修复 DPDK 25.11.2 bnx2x 已实现 UDP RSS 但未向 ethdev 上报能力导致的双队列初始化拒绝。
- `2026-07-31-rust-clippy-current-toolchain.md`：修复当前 Rust 工具链发现的 HFT XDP 无效 link-id forget、复杂返回类型和冗余转换。
- `2026-07-31-dpdk-runtime-prefix-cleanup.md`：把 `/var/run/dpdk` 的本次 EAL fbarray 元数据目录纳入定向回退与零残留硬门。
- `2026-07-31-gpu-ssh-port-25150.md`：统一切换 GPU 同步入口与部署配置到
  25150，并在新旧主机指纹不一致时保持 fail-closed。
- `2026-07-31-dpdk-runner-release-fail-closed.md`：把双 PF runner 拆分为
  数据面、资源、恢复和证据四层发布门，并保留远端编译/实机回归未完成边界。
- `2026-08-01-gpu-ssh-port-25696-service-recovery.md`：切换 GPU SSH 入口到
  25696，并记录容器重启后的 50051 服务恢复、协议健康检查与未形成分体链路边界。
- `2026-08-12-dpdk-release-lifecycle-sealing.md`：补齐 worker 异常生命周期、全 NUMA
  HugePage、接口基线、信号恢复、运行超时与派生验收回执的 fail-closed 发布门。
- `2026-08-12-dpdk-q1-cpu-remap.md`：记录生产物理机 CPU 空闲门阻断、NUMA1 稳定性采样
  与同一 Q1 的有界资源映射收敛。
- `2026-08-12-dpdk-evidence-empty-array-exit-code.md`：修复完整证据路径中的 Bash 空数组
  nounset 与清理期错误退出码假成功。
- `2026-08-12-tpacket-qm-irq-breakthrough-runner.md`：固定八队列流映射与 IRQ/worker
  亲和，形成可恢复的 TPACKET/QM 突破运行器。
- `2026-08-12-unified-release-audit-and-bottleneck-attribution.md`：分离审计完成与生产
  发布语义，绑定最新 DPDK/TPACKET/硬件门证据，并用 fail-closed 规则归因抓包瓶颈。
- `2026-08-12-dpdk-hotpath64-observability.md`：为双 PF DPDK 的 64B 包准备和空轮询
  降本，并拆分 TX/RX、descriptor 与 mempool 计数以定位 10 Mpps 阻塞点。
- `2026-08-12-xdp-primary-dpdk-runtime-decision.md`：以 strict native/zero-copy
  能力、DPDK 容量和逐窗关键流覆盖建立非变更型运行时决策，禁止 generic XDP 冒充
  native，把同 PF DPDK 改绑留在维护窗口，并强制 Native AF_XDP 使用
  `XDP_ZEROCOPY` bind flag。
- `2026-08-12-dpdk-testpmd-capacity-runner.md`：用双进程 testpmd 隔离 Rust 与
  bnx2x 数据面容量，封存严格对齐速率窗、错误计数和完整主机恢复证据。
- `2026-08-12-bnx2x-asymmetric-queue-contract-rejection.md`：按 stock bnx2x 的
  `TXQ <= RXQ` 与对称 fast-path 约束，在任何 PF 变更前拒绝失效的 TXQ4/RXQ1
  testpmd 合同。
- `2026-08-12-unified-r0-trust-chain-hardening.md`：冻结 XDP 优先与 DPDK 回退
  证明，重算 12 Mpps 原始 R0 指标，并封闭重复身份、证据哈希、恢复账本及阶段
  自报发布漏洞。
- `2026-08-12-r1-r4-stage-receipt-recomputation.md`：从密封原始计数重算 R1--R4
  的吞吐、丢包、尾延迟、质量、资源、关键流、回退和长稳，并把 20 项联合指标
  接入统一审计。
- `2026-08-12-production-pareto-selector.md`：在全部生产硬门之后对受控联合候选执行
  多指标 Pareto 选择，禁止单指标冠军与未密封候选入围。
- `2026-08-12-dpdk-stock-tcp-rss-diagnostic-profile.md`：在不修改 stock bnx2x PMD
  的前提下，以默认关闭的合法 IPv4/TCP 多五元组和 Ethernet padding 时间戳，
  有界验证 PMD 内部 TCP RSS/indirection 路径。
- `2026-08-12-dpdk-stock-tcp-rss-q2-diagnostic-runner.md`：以独立冻结合同、完整双 PF
  恢复闭环和原始指标重算，执行 stock TCP RSS 对称 Q2 一次性诊断；Q2 失败即停且
  永不直接解锁 Q4。
- `2026-08-13-stage-evidence-content-provenance-and-fallback-uniqueness.md`：为 R1--R4
  receipt 增加五类内容 manifest/schema/provenance 重算，并只用唯一、严格递增且
  不重叠的完整 fault trial 计算回退次数。
- `2026-08-13-algorithm-optimality-fail-closed-audit.md`：从 normal/fallback 原始指标重算
  受控候选的硬门和 Pareto 前沿，分离 finalist winner、全搜索最优与生产联合最优。
- `2026-08-13-runtime-receipt-production-pareto-binding.md`：把 runtime decision 收据、原始
  窗口重算和算法最优性审计接入生产联合 Pareto，当前 BCM57810 保持 fail-closed。
- `2026-08-13-gpu-ssh-contract-25696-timeout120.md`：同步脚本与测试统一使用 GPU 端口
  25696、120 秒连接门及 ClearAllForwardings，避免旧 25150 断言和 15 秒假超时。
- `2026-08-13-new-high-speed-nic-arrival-acceptance.md`：为新高速 NIC 建立默认只读、
  外部 hash 根约束且完整恢复的到货能力验收链；当前无新卡，保持
  `hardware_pending`。
- `2026-08-13-new-nic-r0-campaign-harness.md`：在到货门之后冻结 native AF_XDP
  优先、DPDK 回退、12 Mpps×15 s×3、丢包/P99/资源/关键流/恢复的独立两阶段 R0
  实验链；不改统一发布审计或生产 Pareto。
- `2026-08-13-bounded-algorithm-qualification-campaign.md`：冻结 A01--A10、normal/
  fallback、三种子共 60 单元的统一算法资格 campaign，并记录本机锁、输入 exact-set、
  稳定读取与 finalizer 精确 run-ID 修复。
- `2026-08-14-ustc-tfc2016-campaign-input-restore.md`：从固定公开提交恢复合同所需的
  18 个 USTC PCAP，封存来源/目标哈希及 27 项正式输入冻结预演，且不把恢复动作冒充
  算法资格结果。
- `2026-08-14-algorithm-campaign-shared-release-gate.md`：让 unified 与 Pareto 共用算法
  campaign 门；当前摘要 receipt 一律不能替代 60 单元 raw replay，保持 fail-closed。
- `2026-08-14-unified-dual-backend-stage-wiring.md`：把新 NIC R0 的 native XDP primary
  与 DPDK fallback 双角色绑定接入统一 stage 审计；无新硬件/未批准 trust profile 时
  仍保持 pending。
