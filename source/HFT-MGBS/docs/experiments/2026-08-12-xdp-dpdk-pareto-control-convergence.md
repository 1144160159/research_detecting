# XDP/DPDK 与生产 Pareto 控制闭环收敛

## 本轮结果

当前环境没有达到 10 Mpps，也没有生产 Champion。独立 testpmd Q1 的 12 个重叠窗
最低 TX/RX 为 2.569706/2.569691 Mpps；TPACKET/QM8 的最好已知 offered 为
2.794217 Mpps。当前 BCM57810/bnx2x 不支持 strict native XDP，AF_XDP 只能 generic/
copy；DPDK 只有单接收队列的已验证能力。因此当前可行集为空，禁止用 generic XDP、
2.57 Mpps DPDK 或离线 A09 质量替代生产 10 Mpps 资格。

## 数据面与运行时决策

Rust `HftXdpMode::Native` 已从协商 flags=0 改为强制 `XDP_ZEROCOPY`，generic/SKB
仍强制 `XDP_COPY`。新增 Python 与纯 Rust 非变更决策器，冻结 XDP native zero-copy
优先、独立待机 DPDK 回退以及同 PF/同适配器全 PF 必须进入维护窗口的边界。连续在线
窗口逐窗检查丢包、P99/P999、CPU/内存、预算、关键流覆盖和回退恢复；关键流或资源门
失败直接停止，不能借切换后端掩盖。

物理机 Rust 1.93 验证：`cargo fmt --check`、HFT 自有 Clippy 严格门、release build
通过，`cargo test --all-targets` 17/17 通过。release 纯决策器 SHA-256 为
`39ea4b32c298b6e0064882040e128b9e5d4b90606d7af21867444144288456f5`，
抓包程序为 `8f8eae438723345e44fd6565c00981931c0fcf8ae8261d89bc1c603fc2010f43`。
共享 BCM57810 golden 实跑输出 `stop_fail_closed`、无生产后端、退出码 10。

## 最后一次 Q4 有界诊断

Q4 仅用于判断 TX 四队列是否扩展，RX 仍为单队列，不属于 R0。V1 非变更预检因
CPU49 突发至 21.21% 停止；对 NUMA node1 全核及 sibling 做 5 秒扫描后冻结 CPU-only
V2（RX 45/46，TX 51/30/31/32/37）。V2 仍因 sibling CPU101 峰值 88.17%、CPU102
峰值 6.06% 超过 5% 门而停止。证据目录：

`/home/wangwt/task/datasets/replay/hft_dpdk_testpmd_capacity_20260812T135350462128488Z`

两次均在 PF 解绑前停止。独立 SSH 复核双 PF 为 bnx2x、ens8f0/ens8f1 为
UP/LOWER_UP、node0/node1 2 MiB HugePage=0。按冻结规则不再换核、不迁移业务、不降门。

## 可信发布与联合 Pareto

统一审计现在从哈希绑定的 R0 原始 result 重算 12 Mpps/64B/15 窗/零丢包/尾延迟/
多队列，并要求三次独立 run 和发生器身份。R1--R4 使用独立原始回执合同重算解析、
基础特征、预算、A09 质量、资源归属、关键流、回退及 24/72 小时连续性；每份回执的
代码、输入、阶段配置、runtime、模型和抓包二进制均需被同目录完整清单实际重哈希，
并绑定已通过 R0 的 backend/hardware 与实时 runtime manifest。

只有五阶段全通过才生成 20 项 `derived_production_pareto_metrics`。最终选择器限制 2--10
个联合候选、算法最多 10 个；当前只允许冻结 practical-front 的 A09 进入生产候选，
但必须与完整数据面/资源/恢复证据成对。单项最高准确率或吞吐不能产生 Champion。

当前三条实际命令均按 fail-closed 结束：

- runtime decision：exit 10，`selected_backend=null`；
- unified release audit：exit 2，R0/R1--R4/full pipeline/release 全 false；
- production Pareto：exit 10，front 为空、Champion 为 null。

## 下一工程动作

1. 在不停止现有业务的维护窗口重新满足 Q4 CPU/SMT 5% 门，最多执行一轮 TXQ4/RXQ1
   诊断；它无论结果如何都不升级为 R0。
2. 真正 10 Mpps 路径需要支持 native XDP/AF_XDP zero-copy 与成熟多队列 RSS 的新
   捕获 NIC，以及不共享当前适配器/CPU 预算的独立 10/25GbE 发生器。
3. 新硬件按 1/5/10/12 Mpps 梯度执行；10/12 Mpps 各 15 秒三次，任一丢包、时延、
   资源、关键流或恢复门失败即停止。
4. R0 三次通过后，正式 runner 才按阶段合同生成 R1--R4 密封 raw receipts；24h 通过
   后再运行 72h，最后才允许生产联合 Pareto 选择。

