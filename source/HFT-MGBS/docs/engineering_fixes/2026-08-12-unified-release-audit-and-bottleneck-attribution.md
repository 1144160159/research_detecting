# 统一发布审计与瓶颈归因修复

## 问题

原有 `audit_release_candidate.py` 的 `accepted=true` 表示离线 RC 配置自洽，
同时又强制 `final_pareto_eligible=false`；`audit_remote_release.py` 的运行时、资源、
接口和 live-preflight 参数多数可省略。8 月 12 日新增的 DPDK 1/12 Mpps、TPACKET
B1/B2 和硬件迁移门也没有进入同一发布判定。因此下游若只读取 `accepted`，可能把
“审计程序成功、仍不可发布”误读成生产合格。

吞吐分析还有一个独立问题：TPACKET 的 2.794 Mpps 零丢包只能说明接收端跟上了
本次发生器，不能外推为 12 Mpps；DPDK 12 Mpps 请求在单队列上停于约 2.57 Mpps，
也不能仅凭速率将网卡、PMD 和 Rust 构包成本混成一个笼统结论。

## 修改

- 新增 `configs/release_manifest_v2.json`，绑定算法搜索、旧 RC、抓包搜索、10 Mpps
  目标、硬件门、TPACKET 搜索和 DPDK 1/12 Mpps 冻结配置的 SHA-256。
- manifest 同时绑定四份物理 acceptance 及其完整证据清单。历史失败观测必须被审计，
  但 `counts_toward_r0=false`，以后不能阻止三份新的正式 R0 通过证据进入可行集。
- 新增 `scripts/audit_unified_release.py`：
  - `audit_complete` 只表示审计已完整执行；
  - `production_release_accepted` 才是生产发布结论；
  - 配置、回执、完整清单、现役 runtime identity、资源、关键流、回退和 R1--R4
    均为 fail-closed；
  - 关键流总数为 0、NaN/Infinity、布尔伪装数值、哈希漂移、缺证据和输入自行声明
    `final_pareto=true` 均不能通过；
  - 最终 `accepted`、`final_pareto_eligible` 与
    `final_pareto_ingestion_allowed` 只由审计器计算。
- 新增 `configs/capture_bottleneck_decision_v1.json` 和
  `scripts/analyze_capture_bottleneck.py`，对路径和可选期望 SHA 做绑定，区分：
  `generator_limited`、`capture_limited`、`single_queue_path_limited` 和
  `target_unproven`。分析器拒绝未恢复主机、非有限数值、计数矛盾和未封存 DPDK
  回执，并始终禁止把 capture-only 结果升级为完整流水线资格。

## 验证

- 本地与物理机相同的相关回归均为 `43/43` 通过；两项 Python 脚本完成
  `py_compile`，JSON 解析和 `git diff --check` 通过。
- 物理机直接读取封存证据执行瓶颈分析，3 个观测全部通过路径、SHA、计数和恢复门：
  - TPACKET B1/B2：`generator_limited=true`；
  - DPDK 12 Mpps Q1：`single_queue_path_limited=true`；
  - `capture_limited=false`、`target_unproven=true`、
    `extrapolation_performed=false`。
- 分析输出：
  `/home/wangwt/task/datasets/replay/hft_capture_bottleneck_analysis_v1_20260812.json`，
  SHA-256 `2a63f2576cf66865dbf711b5a1964d4cd54f047c0cb4c94f95afcb5742567ddd`。
- 统一审计已核验四份物理 acceptance、四份完整清单、8 份本地配置以及主机恢复；
  当前输出中 `offline_algorithm_candidate_accepted=true`、
  `host_restoration_qualified=true`，但 `physical_r0_qualified=false`、
  `runtime_identity_current=false`、R1--R4 均 false，故
  `production_release_accepted=false`。
- 审计输出：
  `/home/wangwt/task/datasets/replay/hft_unified_release_audit_v1_20260812.json`，
  SHA-256 `d6bb2afec89320c07853060856706a2346ccced2e7324971c5c7b4efed38b013`。

## 性能影响与回退

两个新工具只读取 JSON/清单并计算哈希，不进入 Rust 数据面，没有运行时包处理开销。
若 schema 需要演进，应新增版本而不是放宽 v2 的必填证据；删除新入口即可回退到旧审计，
但旧 `accepted` 不能被解释为生产发布资格。

## 遗留风险

- GPU 25696 本轮只确认 50051 由 Python PID 1888 监听；SSH 随后间歇超时，现役
  manifest、PID 命令行、模型/代码身份和 NDJSON health 未能同时核验，因此运行时身份
  必须保持未验证。
- 当前三份瓶颈观测都低于 12 Mpps。它们能排除“在已提供负载下捕获侧丢包”，不能排除
  Rust/PMD 在真正 12 Mpps 输入下成为瓶颈。
- 下一有效突破不是继续扩展 worker/burst 微参数，而是用不共享当前适配器包处理预算的
  独立发生器，以及支持强制 native AF_XDP zero-copy 和成熟 RSS/TSS 的网卡完成三次 R0。
