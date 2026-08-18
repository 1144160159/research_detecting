# DPDK bnx2x RSS 能力上报修复

## 问题与证据

双队列候选 `hft_r0_dpdk_20260731T022745794651819Z` 在端口配置阶段失败：

```text
ETHDEV: Ethdev port_id=0 invalid rss_hf: 0x20, valid value: 0x0
Error: initialize DPDK port 0 failed: -22
```

该轮未进入发包阶段，自动恢复验证通过。DPDK 25.11.2 bnx2x 源码存在内部能力
与 ethdev 能力上报不一致：

- `bnx2x_dev_infos_get()` 上报多 RX/TX 队列，但未设置
  `flow_type_rss_offloads`，所以 ethdev 通用校验把合法集合视为 0。
- 同一 PMD 的 probe 路径显式读取
  `RTE_ETH_RSS_NONFRAG_IPV4_UDP` 并设置 `sc->udp_rss`。
- RSS 初始化路径会建立多队列 indirection table，并在 `sc->udp_rss` 为真时
  启用 IPv4/IPv6 UDP RSS。

因此失败发生在 ethdev 通用校验层，不是硬件队列数量不足。

首次能力上报修复后的 Q2 运行
`hft_r0_dpdk_20260731T024226277475329Z` 成功启动双队列，但两个 RX 队列包数为
`[38886459, 0]`。冻结发生器包含 256 个变化的 UDP 五元组，因此不是单流哈希
集中。进一步核对发现 PMD 在 PCI probe 阶段读取 `dev_conf.rss_hf`；此时应用尚未
调用 `rte_eth_dev_configure()`，所以 `sc->udp_rss` 实际保持 0。该时序错误使 UDP
未进入 RSS，即使后续配置已通过。

## 修复

- 在 HFT-MGBS 中保存最小兼容补丁
  `patches/dpdk-25.11.2/0001-bnx2x-advertise-ipv4-udp-rss.patch`。
- 补丁只补报 PMD 已经显式消费的
  `RTE_ETH_RSS_NONFRAG_IPV4_UDP`，不扩大到未经当前代码路径证明的能力。
- 第二个最小补丁把 `sc->udp_rss` 赋值移动到 `bnx2x_dev_configure()`，
  使其读取应用已经提交的配置。
- DPDK bootstrap 按文件名顺序幂等应用补丁集；若任一补丁既不能应用也不是已应用状态，
  立即失败。
- build manifest 固化补丁 SHA-256 和修补后 `bnx2x_ethdev.c` SHA-256。
- Rust `build.rs` 跟踪 DPDK build manifest 和 `librte_net_bnx2x.a`；外部静态依赖
  更新后强制重新执行链接，避免 Cargo 复用旧二进制。
- 发生器从 DPDK 读取双 PF 的运行时 MAC，以接收 PF MAC 为目的地址、发送 PF MAC
  为源地址生成普通单播测试帧；报告 schema 4 固化两端 MAC。这样 RSS 覆盖验证不再
  混入“未知目的 MAC 的混杂接收路径”这一硬件分类变量。
- 不修改只读的 `traffic-analysis-platform/rust`。

## 验证与回退

1. 重建 DPDK 25.11.2，确认 manifest 包含补丁和源文件哈希。
2. 重建静态 Rust DPDK 二进制并通过格式、测试、Clippy、release 和符号门禁。
3. 先运行冻结的 Q2/1 Mpps RSS 覆盖冒烟；两个 RX 队列都必须收到包。
4. 只有冒烟全门通过，才允许重新评估 Q2/5 Mpps；Q4 继续停止。
5. 任一丢包、时延、吞吐、RSS 覆盖或恢复门失败即停止。

回退时删除/禁用该兼容补丁并从原始已校验归档重新构建。该修复只解决能力上报
矛盾，不豁免任何运行硬门，也不使 capture-only R0 获得全链路 Pareto 资格。

## 最终判定与默认回退

配置时序修复后的首次 Q2/1 Mpps 冒烟
`hft_r0_dpdk_20260731T024920052633840Z` 仍为
`rx_queue_packets=[15150080,0]`，且 P99/P999 为 129.21/814.19 us。
改为双 PF 实际 MAC 后的最后一次冒烟
`hft_r0_dpdk_20260731T025306882795396Z` 仍为
`rx_queue_packets=[15150080,0]`，P99/P999 为 130.18/827.27 us。
两轮均零丢包、总收发一致且恢复验证通过，但 RSS 覆盖和时延硬门失败。

因此 BCM57810 + DPDK 25.11.2 bnx2x 多 RX 候选在本机被拒绝；不再运行 Q2/5 或
Q4。补丁文件和失败证据保留供复核，但 bootstrap 默认
`HFT_ENABLE_EXPERIMENTAL_BNX2X_RSS=NO`，会按逆序撤销实验补丁并构建原始已校验
DPDK。只有显式设置 `YES` 才会重现实验分支；该分支不得进入生产或 Pareto 候选集。

首次默认回退已成功把两个补丁按逆序撤销，但 bootstrap 中遗留的旧循环尾部语句使
构建在 Meson 前返回状态 1。源树核验已恢复原始状态；删除该不可达残留后重新执行
完整构建，不把首次返回状态 1 记为回退完成。
