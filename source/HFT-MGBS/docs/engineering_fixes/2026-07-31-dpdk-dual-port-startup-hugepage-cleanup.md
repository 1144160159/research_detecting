# DPDK 双口启动顺序与大页回退加固

## 问题现象

静态 PMD 注册修复后，1 Mpps R0 已进入真实 DPDK 初始化，但在数据面前
退出：

```text
Error: DPDK port 0 is not 10GbE UP (speed=10000, up=0)
```

证据目录：

`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T013014001227273Z`

自动回绑已恢复两个 PF、bnx2x、10GbE 链路、队列、ring、coalescing 和
offload，但本次 EAL 前缀的 77 个映射文件仍占用 77 个 2 MiB 大页，因此
严格回退核验以退出码 15 正确拒绝成功结论。

## 根因

1. Rust 依次执行“初始化端口 0、等待端口 0 链路、初始化端口 1”。两个
   测试口直接相连，端口 1 未启动时端口 0 无法进入 UP，形成启动顺序
   依赖。
2. `main -> Result` 的早退路径没有执行端口关闭和
   `rte_eal_cleanup()`；EAL 大页映射文件因此残留。
3. 外层回退脚本在删除本次映射文件之前尝试把大页数恢复为 0，内核只能
   回收未占用大页，严格状态核验因此失败。

## 已执行恢复

- 确认 EAL PID `3121726` 已退出。
- 确认 `/dev/hugepages` 中不存在其他前缀文件。
- 仅删除 `hft-3121726map_*`，未删除其他路径或文件。
- NUMA 1 的 2 MiB 大页已恢复为 0。
- `ens8f0/ens8f1` 均为 `UP,LOWER_UP`、10GbE、bnx2x；UIO 未加载。
- `/dev/hugepages` 是系统 `dev-hugepages.mount` 静态挂载，保持 active，
  未擅自卸载。

## 代码修复

- 两个 DPDK 端口全部完成 configure/queue/start 后，再统一等待两口
  10GbE UP。
- 新增 Rust `EalGuard` 和 `PortGuard`；任意 `?` 早退都会先逆序关闭已
  启动端口，再执行 EAL cleanup。
- 把 TX 热路径的 8 个静态参数收敛为 `TxConfig`，通过 Clippy
  `too_many_arguments` 硬门，同时避免后续参数顺序错配。
- 新增受限 `--file-prefix`，只接受 1..=64 个 ASCII 字母、数字、`-`、
  `_`；运行脚本传入证据 `run_id`。
- EAL 增加 `--huge-unlink=always`。
- 回退脚本只删除当前 `run_id` 的 `${run_id}map_*`，然后恢复大页数。
- manifest 新增 `hugetlb_mounted_before`，最终核验同时检查挂载状态。

## 验证门

1. Rust 单元测试增加前缀路径注入拒绝测试。
2. `cargo fmt --check`、测试、Clippy 和 release 构建必须通过。
3. 失败注入或正常退出后，本次前缀大页文件必须为 0。
4. 大页数、hugetlbfs 挂载状态、UIO、驱动、链路和网卡参数必须与测试前
   一致。
5. 重新从冻结的 1 Mpps 开始；未通过时不得升级 5/10/12 Mpps。

## 遗留风险

本次失败发生在数据面启动前，不能作为吞吐证据。修复后仍需验证 bnx2x
PMD 端口启动、实际收发、P99/P999 和零丢包硬门；
`final_pareto_eligible=false`。
