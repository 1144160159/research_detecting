# DPDK 静态 PMD 修复：拒绝不安全动态插件路径

## 问题现象

经批准执行双 PF DPDK 1 Mpps R0 时，两个 PF 已成功进入受控测试窗口，
但 EAL 在数据面启动前退出：

```text
EAL: Error, directory path /home/wangwt is world-writable and insecure
EAL: Cannot init plugins
Error: rte_eal_init failed with -1
```

失败证据位于：

`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T011908239452444Z`

本次运行 `dpdk_exit_status=1`、`restoration_verified=true`。退出后
`ens8f0/ens8f1` 均已恢复为 10GbE `UP,LOWER_UP` 和 `bnx2x`，NUMA 1
大页恢复为 0，`uio_pci_generic` 已卸载。

## 根因

旧实现通过 EAL `-d` 参数从
`/home/wangwt/phase_2/code/HFT-MGBS/.deps/.../librte_net_bnx2x.so`
动态加载 PMD。DPDK 对动态插件路径的祖先目录执行安全检查，而
`/home/wangwt` 为 world-writable，因此 EAL 在初始化插件前按安全策略
拒绝继续。

这不是 1 Mpps 性能失败；数据面尚未开始，不能产生吞吐结论。

## 修改范围

- `rust/hft-dpdk/build.rs`
  - 对 `libdpdk.pc` 强制启用静态链接。
  - 不再让 Cargo 分拆并重排 `pkg-config` 的链接元数据；把
    `pkg-config --static --libs libdpdk` 原始顺序写入 linker response
    file，保留 `--whole-archive` 对 PCI bus、mempool 和 bnx2x 驱动
    构造器的强制装入语义。
- `rust/hft-dpdk/src/main.rs`
  - 删除 `--pmd-path` 参数和 EAL `-d` 动态插件参数。
- `scripts/build_hft_dpdk.sh`
  - 删除 DPDK 共享库运行路径依赖。
  - 把 Clippy `-D warnings` 纳入设置了固定 `PKG_CONFIG_PATH` 的唯一构建
    入口，避免脱离入口调用产生伪环境失败。
  - 增加 `ldd` 硬门，发现任何 `librte_*` 动态依赖即拒绝发布。
  - 增加 `nm` 硬门，二进制缺少 `rte_pci_bus` 或
    `bnx2x_logtype_driver` 即拒绝发布。
- `scripts/run_dpdk_bnx2x_validation.sh`
  - 删除动态 PMD 参数和 `LD_LIBRARY_PATH` 注入。
  - 删除前置文件检查中遗留的 `PMD_PATH` 引用；该引用曾在解绑前由
    `set -u` 以“未绑定的变量”拒绝运行，未改变网卡状态。

没有修改 `/home/wangwt` 权限，没有把文件安装到 HFT-MGBS 之外，也没有
修改只读上游 `traffic-analysis-platform/rust`。

## 验证要求

1. `cargo fmt --check`、单元测试和 release 构建通过。
2. `ldd hft-dpdk` 不包含任何 `librte_*`。
3. `nm hft-dpdk` 同时包含 `rte_pci_bus` 和
   `bnx2x_logtype_driver`。
4. 脚本通过 `bash -n`，且源码不再包含 `PMD_PATH` 或 `--pmd-path`。
5. 未授权门继续以退出码 13 拒绝执行。
6. 重新执行 1 Mpps，确认 EAL 能发现两个静态注册的 bnx2x 端口。
7. 无论成功或失败，恢复后两个接口、驱动、链路、队列、ring、
   coalescing、offload、大页和 UIO 状态均须通过回退核验。

## 性能影响与回退

静态链接只改变 PMD 装载方式，不改变 burst、CPU 绑定或收发算法。若静态
PMD不能被 EAL 枚举，停止测试并回退本提交，不允许通过放宽目录权限或绕过
DPDK 安全检查继续。

## 遗留风险

该修复仅消除动态插件路径安全阻断。1/5/10/12 Mpps、丢包、P99/P999 和
资源门仍须实测；`final_pareto_eligible` 保持 `false`。
