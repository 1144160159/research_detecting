# 修复：stock bnx2x TCP RSS Q2 一次性诊断 runner

## 问题与边界

既有发布 runner 冻结为 UDP/Q1 release gate，不能为验证 stock `bnx2x` 的隐式 TCP RSS
而改变。新的诊断分支只回答一个问题：在双 PF 均配置 RXQ2/TXQ2 时，合法 IPv4/TCP
多流能否让两个软件 RX queue 与两个软件 TX queue 在 1 Mpps、15 秒窗口中均有包。
它不形成 R0 发布资格，不进入最终 Pareto，也不直接解锁 Q4。

## 实现

- `scripts/run_dpdk_tcp_rss_diagnostic.sh` 从成熟双 PF runner 继承完整的接口占用检查、
  CPU 空闲门、NUMA HugePage 所有权、信号处理、PF 回绑和逐项状态恢复闭环，但使用独立
  合同、独立 evidence 目录和独立 validator；旧 runner 未修改。
- 冻结双端口对称 `RXQ2/TXQ2`、`ipv4_tcp_multiflow` / Rust
  `tcp-rss-diagnostic`、256 五元组、64 B、burst 128、1 Mpps、15 秒。这里的
  `64 B` 是 DPDK `pkt_len`，不含线上的 4 B FCS；线速预算必须另计前导码与 IFG。
- runner 在 PF 变更前验证 stock build manifest 必须精确包含
  `experimental_bnx2x_rss=NO`，并将 manifest 内的 `bnx2x_ethdev_sha256` 与实际
  `drivers/net/bnx2x/bnx2x_ethdev.c` 重新计算值绑定。
- 合同的 `binary_freeze_pending=true` 时仅允许 `HFT_DPDK_PREFLIGHT_ONLY=YES`；
  真正 PF 运行必须先回填并验证 binary SHA-256。预检不要求破坏性授权且不改变 PF。
- validator 从原始结果重新检查两 RX/两 TX 队列非零、包守恒、逐秒速率窗口、错误计数、
  运行时长、P99/P999、延迟样本、CPU/PCI/参数/时间戳偏移和主机恢复，不信任 Rust
  `data_plane_qualified` 单一布尔值。

## 2026-08-13 P0 终审修复

- runner 在 CPU 与 DPDK 预检结束后、`mutation_started=1` 之前重新执行 exact
  DPDK executable/runtime ownership 门，并重算 source 与 `run_dir` 内合同、binary、runner、
  validator、两项 preflight 脚本、stock manifest、ethdev 的哈希或逐字一致性。结果写入
  `pre_mutation_gate.json`，validator 将该 receipt 作为硬门重新绑定。
- `setsid` 的目标 PGID 固定为其 leader PID，只接受 `ps` 观察值等于 PID，绝不采用可能仍
  属于 SSH shell 的其他 PGID。恢复时只有在组内进程 argv 精确包含
  `--file-prefix <run_id>` 后才发送负 PGID 信号；否则仅逐 PID 终止经同一 argv 证明的进程。
  `child_pid`/`child_pgid` 一直保留到 EXIT 恢复结束。
- PF 回绑和接口恢复改成 best-effort：单个 sysfs/ethtool/ip 步骤失败会累计失败状态，
  但不再阻断另一 PF、接口、runtime、HugePage 与模块恢复。
- 恢复不再只信任 runner 的 `restoration_verified` 布尔值。validator 解析
  `restoration_ledger.json`，要求 13 个有序、唯一且状态全为 0 的步骤，并交叉检查 runner
  claim；缺步、重排、重复或任一失败均禁止解锁 Q2/5M。
- 每个 RX/TX 软件队列的最小占比与合同统一为 `0.40`，并补边界测试（40% 通过，少 1 包
  失败）。validator 同时绑定 binary pending 状态、原始退出码、两项 preflight 脚本哈希
  与完整参数/端口内容。
- 速率证据要求 15 个共享单调时钟完整 1 秒窗口、TX/RX 窗口数一致、TX 总量与报告平均值
  一致，并交叉核对 DPDK `capture.ipackets == received_packets`、
  `replay.opackets == offered_packets`。Rust 的 RX elapsed 包含约 200 ms drain，所以
  `reported achieved_rx_mpps` 只保留为审计字段，不以其低于 1 Mpps 误杀；RX 正式门由 15
  个完整窗口最小值、包守恒和 `received/(合同15秒)` 总量重算共同决定。

## 分阶段语义

通过时仅设置 `diagnostic_passed=true` 和 `q2_5m_unlocked=true`，允许后续另建
Q2/5 Mpps 冻结合同；`q4_unlocked` 永远为 `false`。Q2 失败时
`q2_failure_stops_branch=true`，不得尝试 Q4。资源发布门本轮未执行，acceptance 明示
`resource_gate_evaluated=false`。

## 当前冻结状态

配置 `configs/dpdk_stock_tcp_rss_q2_diagnostic_v1.json` 冻结 runner、validator、两项
preflight、DPDK build manifest、ethdev 源码与远端已独立核验的 Rust binary SHA-256。
任何脚本更新后必须重新计算 runner/validator 哈希并更新合同，随后仍须先通过非变更预检。

第一次修复版预检在 2026-08-13 被原 48/53 核的 11.11%/31.31% 动态负载拦截，
`mutations_performed=false`。随后的 NUMA1 全核 5x1 秒只读扫描选择 main=45、
RX=46/47、TX=48/49；这五个物理核及其 SMT sibling 的本次峰值均不超过 1.99%。
候选 ID 因此升为 `V2_CPU_ADAPT`，5% 门限未降低，实际动作前仍会重新采样。
V2 随后仅因 CPU49 的 sibling 105 在最后一秒瞬时达到 60% 再次被安全拦截，仍未
发生 PF 变更。最后一次 V3 适配从同一次全核扫描中选择 main=31、RX=32/34、
TX=35/37；各物理核及 sibling 的扫描峰值为 0.99%–2.97%。V3 之后不再轮换核心；
正式 runner 自身的 5x1 秒门若失败，本维护窗口立即停止。

## 验证

- 本地 Python：`python -m unittest tests.test_dpdk_tcp_rss_diagnostic_runner -v` 共 14 项通过。
- 本地 Python `py_compile` 与 JSON 解析通过。
- 本机没有可用 Linux Bash（`bash.exe` 指向未安装的 WSL），因此本轮未声称本地
  `bash -n` 通过；同步前后必须在 10.0.5.8 再执行 `bash -n`。
- 未运行远端 PF 数据面；因此不存在 Q2 性能通过结论。

## 回滚与风险

删除新增 runner/config/validator/tests/doc 即可回滚；既有 release Q1 runner、validator 与
composer 均未修改。实机风险仍是双 PF 短时中断，必须满足显式授权、CPU 前置门和完整
恢复校验；任何恢复失败优先返回失败，不能用诊断结果覆盖。
