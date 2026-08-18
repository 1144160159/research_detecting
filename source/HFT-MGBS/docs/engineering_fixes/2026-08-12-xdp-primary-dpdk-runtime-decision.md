# XDP 优先、DPDK 回退运行时决策合同

## 审计结论

现有 Rust 运行时只实现了 `xdp-skb -> af-packet-ts`：XDP 启动或轮询报错后，
清理主后端并启动 AF_PACKET 时间戳后端。它没有依据可复现的 native XDP、强制
AF_XDP zero-copy、DPDK RSS/多队列容量证据选择后端，也不能在不中断数据面的前提下
把当前同一 PF 从内核驱动改绑给 DPDK。

当前 BCM57810/bnx2x 的 strict native XDP 探测已返回 `EOPNOTSUPP`，现有
`xdp-skb` 是 generic XDP + AF_XDP copy。即使其低负载诊断通过，也不能在任何运行时
字段中提升为 native、zero-copy 或生产合格后端。当前 DPDK bnx2x 的正式容量也只有
约 2.57 Mpps，且没有成熟多 RX RSS 证据，因此按本合同当前机器应返回 fail-closed，
不会制造一个可自动切换的 10 Mpps 后端。

## 新增独立合同

- `configs/xdp_dpdk_runtime_policy_v1.json` 固定后端优先级为
  `native_af_xdp_zerocopy -> dpdk`；generic `xdp-skb` 仅保留诊断身份，不进入生产
  优先级。
- `hft_mgbs/capture_runtime_decision.py` 只消费不可变能力与在线窗口观测并生成决策，
  不 attach XDP、不绑定 PCI、不写 sysfs，也不启动数据面。
- `rust/hft-capture/src/capture_runtime_decision.rs` 在物理机 Rust 侧实现相同纯决策；
  `src/bin/capture_runtime_decision.rs` 只读取 policy/observation、写回执并按合同退出，
  不包含 `Command`、PF bind、sysfs 或 XDP attach 操作。
- `scripts/decide_xdp_dpdk_runtime.py` 提供 JSON 输入/输出入口；合同或 JSON 异常时输出
  `stop_fail_closed` 并以退出码 2 结束。脚本会把自身解析出的项目根目录加入模块搜索
  路径，因此可从项目根直接执行，不要求 editable install 或外部设置 `PYTHONPATH`。
- 未修改 unified release audit、Pareto selector 或远端主机；Rust 抓包侧仅收紧下面记录的
  native AF_XDP 强制零拷贝 bind flag 和运行身份字符串。

## 能力门

XDP 主后端必须同时证明：driver/native attach 成功、强制 `XDP_ZEROCOPY` bind 成功、
copy mode 为 false、至少 4 个 RX 队列、能力探测后主机恢复，以及接口不承载管理面。
任一字段缺失、陈旧或语义不一致即不可选。

DPDK 回退必须同时证明：PMD 探测、独立容量门至少 12 Mpps、至少 4 个 RX 队列、RSS
与每个要求队列的收包覆盖、零错误计数、恢复闭环、待机预检、不可变二进制 SHA-256
和管理面隔离。`capacity_qualified=true` 不能替代实际最低 RX Mpps、队列覆盖和错误计数。

## 在线门与关键流语义

连续 3 个不重叠窗口必须逐窗满足：有实际收包、drop/poll error/invalid/ring-full/
fill-empty 均为 0、kernel-to-feature P99/P999 不超过 10/50 ms，活动队列数足够。
计数与浮点比率必须严格一致，NaN/Infinity 拒绝。

每个窗口还独立硬门 CPU 占整机不超过 0.85、内存占比不超过 0.85、预算超限次数为
0，以及已发生的捕获回退恢复时间不超过 300 ms。这些属于运行安全门；任一超限均
直接停止，不触发 DPDK 切换，避免把资源、预算或恢复 SLA 问题误归因为 XDP 故障。

关键流按 `remote_scored_or_local_fallback_completed` 计算，逐窗要求覆盖率至少 0.99。
分母为 0 时覆盖率必须为 `null` 且该窗口不合格，不能把“未观测到关键流”记为 1.0。
关键流覆盖失败不是抓包后端故障信号：若捕获门正常而覆盖失败，运行时停止并报警，
不得借切换 DPDK 掩盖调度、推理或本地回退缺口。

## 切换安全边界

只有已有独立待机适配器、且流量静默、状态快照、目标预检和回滚准备四项都通过，
外部执行器又明确授权时，决策才返回 `switch_to_dpdk`。当前双 PF 同属 BCM57810，
同 PF 或同适配器全 PF 改绑必须返回 `request_maintenance_dpdk_fallback`，不能在线自动执行。

本模块返回 `transition_permitted` 只表示合同允许外部恢复型执行器进入下一步；它本身从不
执行变更，也不构成发布资格、Pareto 证据或 10 Mpps 证明。

## 当前 BCM57810 冻结快照

`configs/current_bcm57810_runtime_snapshot_v1.json` 绑定当前已验证事实：bnx2x 只通过
generic/copy XDP 诊断，native attach 为 `EOPNOTSUPP`；DPDK Q1 最低 RX 为
2.569691 Mpps、仅 1 个 RX 队列、无成熟 RSS，而且拓扑要求同一适配器全部 PF 改绑。

对应 `configs/current_bcm57810_runtime_decision_v1.json` 的实际决策为
`action=stop_fail_closed`、`selected_backend=null`、`transition_permitted=false`、
`production_backend_available=false`。generic XDP 和当前 Q1 DPDK 均只列在
`diagnostic_only_backends`，没有被选为生产后端；快照变陈旧时仍会 fail-closed。

CLI 退出码同时属于合同：`0` 只用于保持已经合格的 XDP/DPDK，或已满足全部 handoff
条件且 `transition_permitted=true` 的明确切换；`10` 表示输入有效但结论为停止、准备、
维护窗口或没有生产后端；`2` 表示 JSON/合同错误。外部 wrapper 不得只把“成功解析”
当成数据面 GO。

## Native AF_XDP 强制零拷贝修复

此前 `HftXdpMode::Native.bind_flags()` 返回 0；这只能请求 AF_XDP 协商，不能证明 bind
未退回 copy mode。现改为使用只读上游 `probe_agent::capture::xdp_sys::XDP_ZEROCOPY`，
并把 native 运行报告明确命名为 `native_af_xdp_forced_zerocopy`。generic `Skb` 仍固定
`XDP_COPY`。单元合同同时禁止 Native flags 为 0 或 `XDP_COPY`。当前 bnx2x 会在严格
native/zero-copy 能力门更早失败，这是预期的 fail-closed，而不是静默降级。

## Python/Rust 一致性边界

`tests/fixtures/capture_runtime_current_golden_v1.json` 是两种实现共享的当前 BCM57810
golden：固定 `now_utc` 下都必须返回无生产后端、generic XDP/DPDK 均不合格、
同适配器全 PF 拓扑、`stop_fail_closed` 和退出码 10。Python 测试执行 Python 决策
并逐字段核对；Rust 模块通过 `include_str!` 读取同一 policy、snapshot 和 golden 做
serde 单测。Rust CLI 也提供 `--now-utc`，仅用于证据回放和 golden 测试；生产省略时
读取系统时钟。

## 验证

合同测试覆盖：合格 native/zero-copy XDP 保持、generic XDP 防冒充、独立 DPDK
回退、同 PF 维护门、关键流失败禁止换后端、空分母、计数一致性、非有限数、观测新鲜度、
handoff 缺项和篡改语义守卫。另有真实 subprocess 回归：清除 `PYTHONPATH`，以项目根
为工作目录直接执行脚本并解析输出，防止只在测试导入环境中可用。

本地 Windows 工作区未安装 `cargo/rustc/rustfmt`，因此先执行 Python 决策/CLI 18 项
与 Rust 源码合同 4 项，共 22/22。随后将 HFT-MGBS 自有文件同步到 10.0.5.8，使用
Rust 1.93.0 完成真实构建验证（未修改只读上游 `traffic-analysis-platform/rust`）：

- `cargo fmt --all -- --check` 通过；
- `cargo test --all-targets` 共 17 项通过；
- `cargo clippy --all-targets --no-deps -- -D warnings` 对 HFT 自有目标通过；只读上游
  `probe-agent` 仍输出 14 个既有 warning，但不在本次可修改范围内，也未被表述为已修；
- `cargo build --release --bins` 通过；纯决策器 SHA-256 为
  `39ea4b32c298b6e0064882040e128b9e5d4b90606d7af21867444144288456f5`，
  `hft-capture` SHA-256 为
  `8f8eae438723345e44fd6565c00981931c0fcf8ae8261d89bc1c603fc2010f43`；
- release 决策器对共享 BCM57810 golden 实跑返回 `stop_fail_closed`、无生产后端、
  generic XDP/DPDK 仅诊断，退出码 10。

第一次严格 Clippy 门发现 HFT 测试夹具先 `Default` 再字段赋值；已改为结构体初始化，
复跑通过。这一代码修复与真实工具链验证均留存在本文件，满足 HFT-MGBS 修复留档要求。
