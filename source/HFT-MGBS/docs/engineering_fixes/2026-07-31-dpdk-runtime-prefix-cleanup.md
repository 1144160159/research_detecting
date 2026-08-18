# DPDK EAL 运行前缀定向清理

## 问题现象

双 PF DPDK 测试结束后，网卡、驱动、链路、hugepage 和
`/dev/hugepages/${run_id}map_*` 均已恢复，但 `/var/run/dpdk` 下仍保留 14 个
本轮 `hft_r0_dpdk_*` 目录。每个目录包含 11 个 EAL `fbarray_*`/配置元数据
文件。没有 HFT DPDK 进程继续占用这些目录。

这不影响已经核验的收发结果，但不满足“运行前缀零残留”的严格回退约束，
因此不得把“大页映射零残留”扩大表述为“全部运行前缀零残留”。

## 根因

`rte_eal_cleanup()` 与 `--huge-unlink=always` 已释放端口和大页映射，但
DPDK 25.11.2 没有删除 root 运行时目录中的 EAL fbarray 元数据。原回退脚本
只定向删除 `/dev/hugepages/${run_id}map_*`，没有检查
`/var/run/dpdk/${run_id}`。

## 修改范围

- `scripts/run_dpdk_bnx2x_validation.sh`
  - 把 `pgrep` 纳入前置依赖；
  - 回退时先确认不存在命令行含当前 `--file-prefix ${run_id}` 的
    `hft-dpdk.bin` 进程；
  - 只允许删除严格匹配
    `/var/run/dpdk/hft_r0_dpdk_<UTC纳秒时间戳>` 的当前运行目录；
  - 删除后再次核验路径不存在，失败则回退状态返回非零；
  - 最终主机恢复硬门同时检查 EAL 运行目录，并在 manifest 记录
    `dpdk_runtime_prefix_removed=true`。

未修改只读上游
`/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 已执行恢复与验证

- 修改前确认没有 `hft-dpdk.bin` 进程。
- 逐目录检查 14 个遗留目录均位于 `/var/run/dpdk` 第一层，且名称只匹配
  本轮 HFT UTC 运行前缀。
- 只清理上述 HFT 目录；未删除其他 DPDK 前缀。
- 清理后要求：
  - `/var/run/dpdk/hft_r0_dpdk_*` 为 0；
  - `ens8f0/ens8f1` 均为 bnx2x、UP/LOWER_UP、10GbE；
  - hugepages 为 0；
  - HFT DPDK 进程为 0。
- 脚本 `bash -n` 已通过；物理机未安装 `shellcheck`，因此没有宣称该门
  已通过。

本修复发生在实验结束后的回退与证据完整性层，不改变已冻结的吞吐、
丢包、P99/P999 或队列覆盖数据。

## 回退条件

若检测到同一 `run_id` 的进程仍存活、运行前缀不满足严格正则、删除失败或
删除后目录仍存在，则不继续扩大删除范围，直接把主机恢复判定为失败并以
退出码 15 关闭。

## 遗留风险

该修复未通过再次解绑双 PF 的破坏性运行验证；当前仅执行静态验证和既有
残留的受限清理。下一次经批准的 DPDK 运行必须同时用 manifest 与独立
`find /var/run/dpdk -name "${run_id}"` 复核自动清理。当前实验仍是
capture-only R0，`final_pareto_eligible=false`。
