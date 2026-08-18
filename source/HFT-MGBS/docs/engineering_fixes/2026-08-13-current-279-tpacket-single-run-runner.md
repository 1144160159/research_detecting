# 当前硬件 2.79 Mpps TPACKET 单轮全流水线 runner

日期：2026-08-13  
范围：仅新增物理机单轮诊断 runner、冻结配置、静态/负向合同测试和本文档；未修改
Rust、`current_hardware_279`、unified 或 Pareto 逻辑，也未在物理网卡执行。

## 问题与边界

历史 B2 结果只是 TPACKET 捕获观测，不能证明“捕获—解析—流表—多粒度特征—预算调度—
Python 推理”闭环。新增 runner 只产生一轮原始证据，任何成功退出均保持
`runtime_identity_verified=false`、`full_pipeline_qualified=false` 和
`final_pareto_ingestion_allowed=false`，后续必须由独立验收器判断。

本轮固定 ens8f0 捕获、ens8f1 回放、64 B、每队列 144 个确定性 UDP 流、8 队列、
clone 64、burst 8、rx-usecs 24、active timeout 1 s、batch 8。首轮为 HASH；本次唯一候选变量
只将 fanout 切换为 QM，traffic v2 保持不变。捕获持续
21 s；GPU reverse ready 后的 13 s start delay 用于跨越完整 irqbalance 周期，随后发生器
持续 19 s，目标是留下至少 15 个完整的一秒窗。
QM 需要专用 CLI 授权，但授权参数本身不是亲和性证明；仍未授权 unready GPU diagnostic。

## 安全与可追溯修复

runner 在任何主机变更前要求变更、恢复、irqbalance 有界 stop/start 三个精确授权值和变更单号，
并用独占 `flock` 防并发。
runner、配置、正式二进制各自要求外部 SHA-256 信任根，复制到证据目录后再校验；正式二进制
SHA 同时固定为
`499b0b8e9abc14877d85fa0009489ffdf2e7f8d9527986e6cd1993008c2589fe`。该值来自正式目录的 UDP
worker-local flow-state 候选 `--locked` 构建；隔离构建因绝对构建路径不同产生另一哈希，未用于
实机合同。该构建来自正式 Rust 源修复、GPU runtime identity、QM 证据、hotpath-v1 及 UDP
worker-local 状态的统一构建链；`cargo fmt -- --check`、`cargo check --tests --locked`、
`cargo test --release --locked`（47 passed、0 failed、3 ignored）与 release build 已通过；
`Cargo.lock` SHA 保持 `a6ba...` 不变。

预检精确检查 root、两个不同 PCI PF、bnx2x、NUMA 1、link/carrier、无 IP、8 combined
channels、各 8 个队列 IRQ、pktgen 未加载、50052 未占用及同名流水线进程不存在。CPU 门记录
28--54 及全部 SMT sibling 的 5 组一秒原始样本；证据必须完整，
每核五秒平均 busy 不得超过 0.85，且任一样本达到 0.98 即阻断。该门容忍低系统负载下线程
瞬时迁移，不会为测试停止或迁移业务。发生变更前会再次检查竞争进程、50052、pktgen 和冻结
哈希，缩小 TOCTOU 窗口。

首次真实预检发现 irqbalance 已持续运行约七个月，16 个队列 IRQ 当时集中在 CPU 51/107。
runner 保存 irqbalance 的 active/enabled state、完整 systemd show、配置、MainPID、可执行文件、
`/proc/<pid>/stat` start ticks 和 cmdline。
首次 live run 进一步证明 irqbalance 会在约 10 秒主动迁移 affinity。其 R1 原始计数为：pktgen
发送 52,982,307 包，pipeline 接收 50,503,894 包，差额 2,478,413；ens8f0
`rx_discards` 增量也恰为 2,478,413，且主要集中在硬件队列 1/3/5/7。因此 R1 明确失败，
不能作为 2.79 Mpps 闭环证据。

完成的 normal-r1b 证据目录为
`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T060428Z_normal_r1b`。
18 个完整窗口最低 2.788163 Mpps；pktgen 共发送 52,892,869，pipeline 收到 52,881,290，差额
11,579 与 ens8f0 `rx_discards` 增量精确一致，socket/internal drop 均为 0。八个 capture worker
各约占一个 CPU 的 99.5%，说明 HASH 软件散列路径已达到 worker CPU 瓶颈。关键流 2,051/2,051
完成评分，GPU 302 batches，但 batch RTT P99 为 55.139 ms。历史 B2 QM8 的最低窗口为
2.790743 Mpps 且零丢包，因此下一候选严格只切换 HASH→QM。

Rust runner 不再将 `--allow-qm-with-verified-flow-affinity` 记录成已验证事实。每个 worker 只在
低频 closed-flow 路径记录 `flow_id` 的确定性双 FNV-1a 64-bit 哈希及重开次数；包级热路径不做
该记录。main 合并八个 worker 的所有闭流哈希，重算每个 flow 的 worker owner，输出
`qm_flow_affinity_evidence`：闭流覆盖数、distinct hash、同 worker 重开、每 worker 计数、证据
溢出和跨 worker collision。QM raw observation 必须同时满足证据非空、覆盖全部 `flows_closed`、
未溢出且 collision=0；否则 JSON 仍落盘但进程非零退出，runner 也独立复核这些字段。因此
allow flag 只能授权测试，不能自证 flow affinity。
由于删除了误导性的 `qm_flow_affinity_asserted` 并加入运行时证据结构，raw pipeline JSON schema
从 1 升为 2，runner 要求精确版本 2，避免旧消费者静默误读。

normal-r1b 的 2,051 个闭流强烈指向 traffic v2 的设计错误：八个 pktgen 设备复用相同的
目的地址 `.1`--`.144`、UDP 53 及其余五元组字段，全局实际上约 144 个 flow，而非
8×144；active timeout 1 s 下约 14 次关闭/重开得到约 2,016，与实测 2,051 一致。这仍是基于
配置与总数的推断，不冒充旧 binary 未记录的运行时 distinct-flow 证明。本次为保持
QM 单变量不修改 traffic。若 QM 证据中的 `distinct_flow_hashes` 约为 144，将成为直接运行时
实证。下一独立 traffic-v3 才会为每个 TX queue 分配唯一 UDP source 或不重叠地址区间，使
全局达到 1,152 flow/s，并严格回读八个 Params；在 traffic-v3 实跑前不得声称每窗 1,000 样本。

## QM 实跑与 hotpath-v1

正式 QM v2 实跑给出真实亲和性证据：`runtime_verified=true`，1,160 个 distinct flow，八队列
接近 8×145，跨 worker collision 为 0。该轮 52,943,873 packets/21 s，18 个完整窗最低
2.783028 Mpps，NIC 丢包 11,665 且全部集中在 queue 3；八个 worker thread CPU 均约 99%，
GPU P99 为 16.637 ms。当前瓶颈因此在 CPU36--43 的 Rust 每包热路径。

该轮记为 `qm_probe_r1`，恢复台账全部通过，但因 NIC discard 非零且最低完整窗低于 2.79 Mpps，
不计合格 repeat。随后 `qm_hotpath_r2` 在相同 traffic v2 下得到 18 个完整窗最低 2.791237 Mpps，
NIC discard 降至 3,970 且全部位于 queue 1，GPU P99 16.961 ms，2,032 个闭流全部 scored，QM
collision=0，恢复台账全部通过。该轮虽然越过吞吐门，仍因 discard 非零且流密度不足，不计合格
repeat。

`hotpath_v1` 采用两项紧密、语义保持的低风险优化。第一，UDP 的 `tcp_flags==0` 立即返回，
非零 TCP flags 只遍历置位 bit；对全部 256 个 u8 flag 值及正反方向执行穷举等价测试，确保
flag count、FIN 和 RST 语义与原固定 8-bit loop 一致。第二，worker 不再为每个 packet 对
`BTreeMap<epoch_second,count>` 执行 entry 查找；单调时间戳正常路径只更新当前秒标量，跨秒
才写一次 map，乱序秒显式 fallback 并累计 `epoch_out_of_order_packets`。测试覆盖单调百万包
及乱序输入，与原逐包 BTreeMap 结果相同。

同时新增低频 expiry 观测，不改变 active/idle timeout：每次原有约一秒 scan 记录
`expire_scan_calls`、`expire_scan_closed_total`、event-time delta min/max，退出时记录
`flush_closed`。这些字段用于解释 QM v2 的 1,160 distinct、868 reopen、2,028 closed 为何接近
一次重开。停止门为：任何特征语义/epoch count 差异、official `--locked` 测试失败，或后续
正式单变量实跑仍有 NIC discard/最低完整窗低于 2.79 Mpps，均不得认定 hotpath-v1 达标。
隔离 release 微基准各执行 20,000,000 次：UDP zero-flag 分支相对旧固定 loop 为 4.299×，
epoch scalar accumulator 相对逐包 BTreeMap 为 1.901×。这些只是局部代码段的方向性结果，不能
换算成整条流水线吞吐，正式 PF 单变量实跑仍是唯一达标判据。

第三个单变量候选只把 UDP 流状态移入 QM 已证明单 owner 的 worker-local `HashMap`，去掉每包
`PartitionedFlowTable` 的 DashMap/原子访问和 `extras` 双表；非 UDP 保持通用途径。固定与随机
UDP 序列、active/idle expiry、flush、双向 canonical key、payload/IAT/TOS/UDP flags fixture 均以
旧路径为 oracle，对 `RAW_FEATURE_ORDER` 38 维逐元素 bitwise 等价。隔离 2,000,000 包、145 flow
微基准为 3.129×，但只代表 CPU 降本潜力。第三轮只能定位为 UDP fastpath capacity diagnostic：
即使 NIC discard 为 0，traffic v2 已知约 2,032 closed/18 windows，runner 的聚合流密度硬门
`flows_closed >= full_windows * 1000` 仍会 fail closed。因此该轮预期不计 repeat，不得为了通过而
改门或同时修改 traffic；后续必须用独立 traffic-v3 提供不重叠的每队列五元组。

第一次采用动态 ban 的正式尝试在发包前以 RC83 失败，证据目录为
`hft_current_279_tpacket_20260813T054055Z_normal_r1`：发送 settings 后仅等待 0.2 s，setup 仍返回
`SLEEP 10 BANNED 00000000`，精确集合门拒绝继续；cleanup 成功恢复空集合，ledger/restoration
全部通过，因此该轮没有发包。进一步核对 openEuler `irqbalance-1.8.0-9.oe2203sp2` 及上游
1.8.0 源码表明，socket handler 将动态列表替换后设置 `need_rescan=1`；定时 scan 在重建路径内
执行 `sleep_approx(sleep_interval)`，与 socket handler 共用 GLib main loop，所以即时 setup
不能作为同步 acknowledgement。更重要的是，现场用不存在的 IRQ 进行协议探针时，daemon 在
下一个约 10 s 扫描周期退出（`ExecMainStatus=13`），证明该版本的动态 ban 对本 runner 不具备
安全兼容性。runner 因此完全移除 socket、`SCM_CREDENTIALS`、硬编码 PID socket 和动态 ban
路径；延长轮询不能修复这个安全问题。

新路径仅在第三个显式授权值存在时允许有界 service 事务。所有预检及最后 TOCTOU 门通过后，
runner 再次核对原 active PID/start ticks，使用 `timeout 15 systemctl stop irqbalance`，并要求
状态严格为 inactive、MainPID=0 且原进程消失，之后才固定双口同 queue IRQ 到 CPU 28--35。
100 ms monitor 持续检查 affinity，并每秒确认 irqbalance 没有意外重新 active；任何漂移都先
停 pktgen、终止冻结 capture 后非零退出。runner 不使用 `restart`，也不直接 signal/kill daemon。

cleanup 先停发生器及所有子进程，在 irqbalance 停止期间恢复原 affinity、ring、coalesce 和
pktgen module；启动前再次封存并比对 unit 配置，随后才执行有界
`timeout 15 systemctl start irqbalance`。恢复门要求 service
active、MainPID 非零、新 PID/start ticks 身份不同于旧进程，并且 `/proc/<pid>/exe` 与冻结的
原 executable 一致，enabled 状态也必须与初始值相同；结果写入 restoration ledger。若 stop
命令失败但原身份仍 active，cleanup
不会重复 start。初始 inactive 分支全程保持 inactive。任一服务状态或身份门失败都会将最终
退出码提升为 97。

为避开现场已观测的 IRQ CPU 51/107，pktgen CPU 改为 44--50、52，scheduler 改为 53，
generator control 改为 54；CPU 预检相应覆盖 28--54 及全部 SMT siblings，仍执行 5×1 秒门。

## 确定性多流 traffic v2 与硬件丢包门

原 8 固定流只能产生约 8 closed flows/s，不能满足流级每窗至少 1,000 样本的目标。
`deterministic_multiflow_v2` 在每个 TX queue 设置 `flows 144`、`flowlen 36`、
`flag FLOW_SEQ`、144 个连续目的地址及固定 UDP 目的端口 53；Linux 5.10 源码将
`daddr_max` 定义为 exclusive，因此 `.1`--`.144` 使用 `.145` 作上界。保留 clone_skb 64 和 burst 8。
Linux 内核 pktgen 文档明确将 `flows`、`flowlen`、`FLOW_SEQ`、`clone_skb` 和 `burst` 列为
设备参数，并说明 clone_skb/burst 的共享 skb 行为：
https://docs.kernel.org/networking/pktgen.html 。runner 在发流前保存八个 `/proc/net/pktgen`
完整回读并严格核验 Params；完成后仍以后验 `flows_closed / full_epoch_windows >= 1000`
作为聚合诊断门。该聚合门不等于逐窗证明，所以 raw runner 的资格字段继续保持 false。

此外，runner 从 ens8f0 的前后 `ethtool -S` 中唯一解析总 `rx_discards` 和八个队列计数，
生成 `nic_rx_discards_gate.json`。总增量及每队列增量都必须为 0；该门独立于 packet-socket
drops，即使 socket drops 为 0，只要 NIC `rx_discards` 非零，本轮仍非零退出。

状态快照覆盖 interface、address、driver、link、ring、coalesce、features、channels、XDP、
qdisc（含统计）、IRQ affinity 和 pktgen。采集二进制通过 `setsid` 建立独立 PGID；runner 只有
在 `/proc` 证明 exe 是冻结二进制、PGID 等于 PID，且 argv 同时绑定本证据目录中的 output 和
ready 文件后，才允许向该进程组发信号。退出或第一信号触发清理后忽略后续信号，先停止
pktgen，再对发生器、timer、采集进程组和监控进程依次执行有界 TERM、5 s 后 KILL、2 s
复核，之后才 best-effort 恢复 IRQ、ring、coalesce 和 pktgen module。

每个恢复动作及 before/after 比对均写入 `restoration_ledger.tsv`。发生过变更且任一恢复或
核验失败时，最终退出码强制为 97；证据生成 `evidence.sha256` 并立即执行 `sha256sum -c`，
检查结果保存为 `evidence.sha256.check`。

## 使用与验证

同步到物理机后，先运行只读语法和合同测试：

```bash
bash -n /home/wangwt/phase_2/code/HFT-MGBS/scripts/run_current_hardware_279_tpacket_diagnostic.sh
cd /home/wangwt/phase_2/code/HFT-MGBS
PYTHONPATH=. python3 -m unittest tests.test_current_hardware_279_tpacket_runner_contract -v
```

执行人必须在同步后重新计算 runner/config SHA，并与审阅后的值核对。正式单轮命令形式为：

```bash
export HFT_CURRENT_279_MUTATION_AUTHORIZATION=I_AUTHORIZE_CURRENT_279_TPACKET_MUTATION
export HFT_CURRENT_279_RESTORATION_AUTHORIZATION=I_AUTHORIZE_CURRENT_279_TPACKET_RESTORATION
export HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION=I_AUTHORIZE_IRQBALANCE_STOP_START_FOR_CURRENT_279
export HFT_CURRENT_279_CHANGE_TICKET=HFT-279-DIAG-001
export HFT_CURRENT_279_RUNNER_SHA256=<reviewed-runner-sha256>
export HFT_CURRENT_279_CONFIG_SHA256=<reviewed-config-sha256>
export HFT_CURRENT_279_BINARY_SHA256=499b0b8e9abc14877d85fa0009489ffdf2e7f8d9527986e6cd1993008c2589fe
/home/wangwt/phase_2/code/HFT-MGBS/scripts/run_current_hardware_279_tpacket_diagnostic.sh \
  /home/wangwt/task/datasets/replay/hft_current_279_tpacket_$(date -u +%Y%m%dT%H%M%SZ)
```

本地验证结果：新增合同测试 13 项通过；其中真实 bash 负测仅在 POSIX 环境运行，Windows
unittest 会显式 skip。另用 Cygwin Bash 4.4 独立执行 `bash -n` 通过，并验证无授权退出码为
74。物理机仍必须再次执行 `bash -n`，因为本次任务明确不进行远端网卡运行。
