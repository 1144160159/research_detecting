# DPDK testpmd 双 PF 独立容量诊断

## 目的

现有 HFT Rust DPDK 单队列在 12 Mpps 请求下 TX/RX 同步停在约 2.57 Mpps，
但该闭环同时包含 mbuf 分配、64 B 模板复制、时间戳写入和 bnx2x PMD，不能只凭
该结果区分“合成发生器开销”与“PMD/硬件单队列上限”。本修复增加独立的
DPDK `testpmd` RX-only/TX-only 容量诊断；它只回答当前两个 PF 能否由成熟 DPDK
数据面提供 10 Mpps，不升级 HFT R0 或最终流水线资格。

## 实现

- `scripts/run_dpdk_testpmd_capacity.sh` 复用现有 runner 的 fail-closed 约束：
  独占锁、接口/PCl 身份、地址/路由/策略/XDP/活动 DPDK、全 NUMA HugePage、
  ethtool/qdisc 基线均在解绑前检查；HUP/INT/TERM 和超时后先停止两个进程，
  再回绑 bnx2x，恢复 ring/coalesce/GRO/LRO/MTU/txqlen/UP、HugePage、UIO 与
  EAL runtime 前缀，并逐项生成恢复账本。
- RX 和 TX 实例分别使用 main lcore 与 forwarding lcore。Q1 固定
  `RX main/worker=45/46`、`TX main/worker=50/51`；Q4 使用 NUMA node 1 上两个
  main 与各四个 worker。所有核及 SMT sibling 在解绑前执行五次空闲门检查。
- RX 先启动，TX 延迟两秒开始；RX 在 TX 结束后继续排空两秒。两个实例均以
  writer 每秒显式执行 `show port stats all` 采集速率（不依赖交互模式下无效的
  `--stats-period`），并在停止后显式执行最终 `show port stats all` 与
  `show port xstats all`。
- 两个实例先通过 ready marker 汇合，再启动 RX，TX 在 RX start marker 后精确
  延迟两秒；汇总时 RX 额外跳过两个 lead 窗口，使最终使用的 12 个 RX/TX 窗口
  对应同一重叠时段。活动进程门按 `/proc/PID/exe` 与精确 `comm` 判定，避免
  runner 文件名中的 `testpmd` 误匹配自身。
- Q1/Q4 均固定 `burst=256`、`mbcache=512`、`total-num-mbufs=32768` 和
  `record-burst-stats`；Q4 TX 另启用 `txonly-multi-flow`，避免默认单流让 RSS
  全落同一接收队列后误判四队列容量。两个实例各限定 `socket-mem=0,256`，总量
  不超过冻结的 node 1 HugePage 预算。
- `scripts/summarize_dpdk_testpmd_capacity.py` 对 RX 先丢弃两个 lead 窗口，再对
  RX/TX 同时丢弃前两个 warm-up 窗口，仅使用
  后续前 12 个完整窗口，要求 TX/RX 最低均不低于 10 Mpps、xstats 存在且错误类
  计数为零；最终标准统计中的 `RX-missed/RX-errors/RX-nombuf/TX-errors` 也必须
  存在且为零。输出始终设置 `r0_capture_only_qualified=false`、
  `full_pipeline_qualified=false` 和 `final_pareto_ingestion_allowed=false`。
- 所有日志、最终 stats/xstats、前后快照、恢复账本、派生结果与完整 SHA-256
  清单保存在 `/home/wangwt/task/datasets/replay/hft_dpdk_testpmd_capacity_*`。

## 有界执行与停止规则

1. 先执行 Q1 15 秒三次；任一轮恢复或证据封存失败立即停止。
2. 若 Q1 三轮均低于 10 Mpps，则当前 bnx2x 单队列 PMD/硬件容量已被独立确认，
   不再把 Rust 微参数调整当作 10 Mpps 方案。
3. Q4 仅为实验诊断。stock bnx2x PMD 若拒绝四队列，或 xstats/队列覆盖不完整，
   立即停止，不启用历史实验 RSS 补丁、不改变 DPDK build manifest。
4. 即使 testpmd 三轮达到 10 Mpps，也只解锁“优化 HFT 发生器热路径”的 M1；
   HFT 自身仍须重新执行 12 Mpps R0 三次硬门。

## 回退边界

脚本无法捕获 SIGKILL、掉电或内核崩溃，因此每轮之后仍需在第二个 SSH 命令中独立
复核双 PF 为 bnx2x、UP/10GbE/carrier、全部 HugePage 为 0、UIO/testpmd/EAL
前缀为零。任一项异常时不得开始下一轮。

runner 内部恢复门还会复核 driver override、NUMA HugePage 与 hugetlbfs/UIO 模块
原状态、MTU/txqlen/UP、地址/路由/策略路由/XDP、ethtool/qdisc 哈希和运行前缀。

首次 Q1 尝试在任何主机变更前由合同门退出：原 jq 在 worker 数组上下文中读取
`.queue_count`，触发 `Cannot index array with string "queue_count"`。现已用根对象的
`$queues` 绑定修复，并增加 `HFT_PREFLIGHT_ONLY=YES` 的非变更预检模式；它只有在
合同、接口/PCI、CPU/SMT 及全部主机前置门均通过后才返回，且明确记录
`mutation_started=false`。Q1/Q4 必须先通过该模式再允许解绑。

首次非变更 CPU 门发现 CPU 54 在一个采样窗达到 28%，因此没有降低 5% 阈值，
而是对 node 1 全部物理核及 sibling 进行五次 1 秒扫描，并把 Q1 重冻为
45/46/50/51；该轮对应 sibling 101/102/106/107 的最大利用率均不超过 1%。

Q1 单轮实测的 12 个重叠窗口为 RX 最低 2.569691 Mpps、TX 最低
2.569706 Mpps，标准错误计数与 xstats 错误计数全零；恢复账本 13/13 通过。
该结果与 HFT 旧闭环约 2.57 Mpps 重合，因此仅解锁一次 Q4 结构诊断，不再重复
无信息增益的 Q1。Q4 的 CPU 36 sibling 92 在全核扫描中略超 5%，已替换为 45。
Q4 首次非变更预检又发现 CPU 48/52 分别突发到 19.6%/87.5%，PF 未变更；两核
已由同 NUMA 扫描低于 3% 的 39/41 替换，继续执行相同 5% 门，不接受降门槛。
第二次预检显示后台负载迁移至 38/39/41/42，故再次对全 node 1 扫描，并只选取
跨多次扫描均稳定的 29/30/37/40/44/45/46/49/53/54。若该组仍未通过 5% 门，
本次 Q4 停止，不迁移或终止宿主机现有服务。

该 10 核对称 Q4 仍因宿主负载迁移被预检拦截。结合既有证据中 bnx2x RX queue1
始终为零，继续分配四个 RX worker 没有工程意义；最终结构诊断改为 TXQ4/RXQ1：
TX 以多流驱动四个发送队列，RX 保持唯一已证明可收包的队列。它分别报告发生器
扩展能力与单队列接收上限，不把 TX 达标误写为捕获达标。
非对称预检仅 TX main CPU 29 在一个采样窗被占用 53%，其余物理核与 sibling
均低于 3.1%；只将该 main lcore 替换为多轮扫描稳定的 CPU 49 后重试。

2026-08-12T13:47Z 的再次非变更预检中，仅 CPU49 在首个 1 秒窗突发到
21.21%，其余冻结核及 sibling 均不超过 4.91%；脚本在 PF 解绑前退出，双 PF
仍为 bnx2x 且接口保持 UP。随后对 node1 的 28--55 物理核及 sibling 做最后一次
五窗只读扫描，形成远端证据
`/home/wangwt/task/datasets/replay/q4_cpu_idle_scan_20260812T1350Z.json`。据此新增
CPU-only 冻结合同 `dpdk_testpmd_capacity_q4_10mpps_v2.json`：RX 45/46，TX
main 51、workers 30/31/32/37；这些物理核及 sibling 在该扫描中的最大利用率均
不超过 3.97%。V2 是最后一次有界 Q4 重试；若同一 5% 门仍失败，则停止，不再
迁移业务、不降低阈值，也不继续搜索 CPU 组合。

V2 非变更预检证据位于
`/home/wangwt/task/datasets/replay/hft_dpdk_testpmd_capacity_20260812T135350462128488Z`。
结果 `passed=false`：CPU45 的 sibling CPU101 在三个窗口达到
32.99%/88.17%/87.64%，CPU46 的 sibling CPU102 最高 6.06%；因此按上述停止规则
终止 Q4。`mutations_performed=false`，之后独立 SSH 复核两个 PF 均绑定 bnx2x、
node0/node1 2 MiB HugePage 均为 0、ens8f0/ens8f1 均为 UP/LOWER_UP。
