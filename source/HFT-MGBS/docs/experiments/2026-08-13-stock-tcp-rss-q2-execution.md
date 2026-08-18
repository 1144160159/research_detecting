# stock bnx2x TCP RSS Q2 执行记录

## 结论

2026-08-13 已完成 Rust 数据面、独立安全 runner、validator、冻结配置、负向测试及
远端构建验证。前三次命令均在 CPU/SMT 空闲门被拦截；第四次只读门的 10 个相关
逻辑核最高利用率为 4.04%，随后实际完成 Q2/1 Mpps、15 秒数据面诊断。

诊断发送和接收均为 15,150,080 包，包差为 0，TX 软件队列为
`[7,575,040, 7,575,040]`，但 RX 软件队列为 `[15,150,080, 0]`。因此 256 个合法
IPv4/TCP 五元组仍全部落到 RX queue 0，冻结的每队至少 40% 覆盖门失败。该结果拒绝
stock bnx2x 隐式 TCP RSS 假设，并按 `q2_failure_stops_branch=true` 永久停止当前
网卡的 Q2/5 Mpps 与 Q4/10 Mpps 分支；不能解锁 R0、全流水线或 Pareto。

## 已实现和冻结的诊断

- 双 PF 均为对称 RXQ2/TXQ2；禁止 bnx2x 源码明确拒绝的 TXQ4/RXQ1。
- 使用 stock DPDK 25.11.2、`mq_mode=NONE`、`rss_hf=0`，由 PMD 内部 IPv4/TCP
  路径接受 256 个合法 TCP 五元组；本轮只诊断该隐式路径，不把它当作已支持能力。
- 64 B 为 DPDK `pkt_len`，不含线上 FCS；时间戳位于 54--61 字节 padding，IPv4/TCP
  校验和和实际双 PF MAC 已由 Rust 测试验证。
- 每个 TX/RX 软件队列必须占各自总量至少 40%，并要求 15 个完整共享 1 秒窗口、包守恒、
  NIC `ipackets/opackets` 一致、零错误、P99/P999、原始退出码和 13 步恢复账本全通过。
- runner 在变更前二次检查精确进程/runtime 所有权并重算冻结件；恢复链为 best-effort，
  任一步失败不会阻止其余 PF、接口、HugePage 和模块恢复，但最终验收必失败。

最终代码身份：

- Rust binary：`7137c47ea22cfec124b57c51c1476c121b21b124978cabf850d7526ce2f6f19b`；
- runner：`d2b03e655833276d2450fc717ddc434726e6a07a06167dee4ba795c1b0ce3ef4`；
- validator：`759a21c023c6c876ea88e68e106048a02108324f1604cbaec7adc5b15db0829e`；
- V3 CPU 自适应合同：`9e0631f1e1c6ca14c419387076a8819c661fdf045f01500396a1f905c5acc722`；
- stock build manifest：`29436d1b20abeb70ea0758470086cacc436245e127ffc16824105bab134e5143`；
- stock `bnx2x_ethdev.c`：`5a62456b7f20f6995bfb9dab4d014a43e793f1d4d75b0d7075eae7f32e56d1bb`。

远端 `bash -n`、14 项 Q2 runner 负向测试、Rust `cargo fmt/test/clippy/build` 均通过。

## 三次非变更阻断与一次实际执行

所有证据均位于物理机 `/home/wangwt/task/datasets/replay`：

1. `hft_tcp_rss_q2_preflight_blocked_20260812T163748335120234Z`：原组合的
   CPU48/53 峰值为 11.11%/31.31%；
2. `hft_tcp_rss_q2_preflight_blocked_20260812T164119353049946Z`：V2 的 CPU49
   sibling 105 最后一秒达到 60%；
3. `hft_tcp_rss_q2_preflight_blocked_20260812T164412828342779Z`：正式授权命令的
   V3 中 CPU31 sibling 87 达 61.22%，CPU37 sibling 93 达 62.77%。

三份 manifest 均为 `mutations_performed=false`，完整清单校验通过。最终独立复核：
`0000:cb:00.0/.1` 均绑定 bnx2x，`ens8f0/ens8f1` 均 UP/LOWER_UP、10Gb/s Full，
node0/node1 的 2 MiB HugePage 均为 0，且无 HFT/DPDK 数据面进程。

第四次执行证据目录：
`/home/wangwt/task/datasets/replay/hft_tcp_rss_q2_20260812T165732153923663Z`。
关键结果如下：

- 15 个完整共享 1 秒窗口的 TX/RX 最低速率均为 1.00992 Mpps；
- `offered_packets=received_packets=15,150,080`，NIC 错误和丢包计数均为 0；
- P99 为 11.0035 us，P999 为 151.4530 us；
- TX 队列各占 50%，RX queue 1 占 0%，`diagnostic_passed=false`；
- 13 项恢复账本全部为 0，双 PF 回绑 bnx2x、接口恢复 UP/LOWER_UP、两 NUMA
  节点 HugePage 恢复为 0；
- 完整证据清单执行 `sha256sum -c` 通过。

关键证据 SHA-256：

- `acceptance.json`：`732fbc815fa5099b93be6608d2875b67f2353a69b5fe5caeadcabb1918824448`；
- `result.json`：`54f6df71b49e1f21c4552416d3782b01a20e9fa0cf547308917063d6ebecf354`；
- `restoration_ledger.json`：`3cf1ca90777d036fe2a3b803fc3dee7b9d06e411ffd3934ed56447a2cd05db59`；
- `evidence_sha256_complete.txt`：`e63fe68bab32e4500e557c50c0b2bde8ef092775fb75fa19fc7ccde6d7eeb2ff`。

## 达到 10 Mpps 的执行决策

当前 BCM57810/bnx2x 分支已经完成最后一个有信息增益的多队列假设检验并失败，不能再通过
维护窗口、CPU 绑核、burst、UDP/TCP 模板或 PMD 参数扫描达到 10 Mpps。下一步唯一保留的
工程路径是安装支持 native XDP、forced AF_XDP zero-copy、成熟 RSS/TSS 和逐队列计数的
现代 10/25GbE 以上 NIC，并使用独立 10/25GbE 发生器执行 12 Mpps、15 秒、三次零丢包门。

当前可重复实测上界仍为 testpmd Q1 约 2.5697 Mpps 和 TPACKET 发生器约
2.7942 Mpps；10 Mpps 未达到。
