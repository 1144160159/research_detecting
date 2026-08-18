# 修复：DPDK bnx2x 隔离构建与只读预检

## 现状

- `ens8f0/ens8f1` 分别映射到 `0000:cb:00.0/0000:cb:00.1`，属于同一 BCM57810 适配器。
- 固件为 `mbi 7.15.42 / bc 7.15.23`，高于 DPDK bnx2x PMD 文档要求的 7.13.11。
- 系统没有 IOMMU group，启动参数没有 `intel_iommu=on`。
- PF 没有 `sriov_totalvfs/sriov_numvfs`，不能用当前内核状态下的 VF 隔离路径。
- `uio_pci_generic` 内核模块存在，但尚未加载。
- DPDK、Meson、Ninja 未安装；开发依赖 numactl/libpcap/OpenSSL/zlib 已存在。
- bnx2x PMD 不支持 RSS；未启用 SR-IOV 时，官方要求同一适配器的全部 PF 一起从 Linux 驱动解绑。

## 实现

- `bootstrap_dpdk_bnx2x.sh` 在 HFT-MGBS 的 `.deps` 内下载、校验、构建并安装固定版本 DPDK 25.11.2，不污染系统 Python 或全局库。
- 官方发布页 MD5 `a017927310a8a545b6bad8ade8a70c85` 作为下载门禁；构建后另存 SHA-256 与路径 manifest。
- `preflight_dpdk_bnx2x.py` 只读采集接口、PCI、固件、NUMA、链路、SR-IOV、IOMMU、UIO 与 DPDK 构建状态，明确输出 `mutations_performed=false`。
- 预检分别输出 `ready_for_disruptive_validation` 与 `ready_for_non_disruptive_validation`：无 SR-IOV 是整卡解绑约束而不是 DPDK 构建阻断项，且整卡路径始终要求显式批准。
- DPDK Rust crate 与现有 `hft-capture` 分离，确保没有 DPDK 的环境仍能执行原有 8 个 Rust 测试和 release 构建。

## 后台入口修复

首次 detached 启动日志显示 SCP 后脚本没有可执行位，`nohup "$0"` 立即以 Permission denied 退出，未产生安装结果。入口改为 `nohup bash "$0"`，不依赖目标文件 mode；PID/log 路径固定在 `.deps`，重复启动会检查存活 PID。

## 变更门禁

预检与构建不解绑接口。加载 UIO、分配 hugepages、关闭两口并解绑 `bnx2x`、绑定 UIO 均属于后续有中断风险的验证阶段，必须先固化恢复命令和用户批准。
