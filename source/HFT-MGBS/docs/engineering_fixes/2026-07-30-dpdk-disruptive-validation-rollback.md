# 修复：DPDK 双 PF 中断式验证与自动回退

## 风险

BCM57810 未启用 SR-IOV 时，DPDK bnx2x PMD 要求同一适配器的两个 PF 一起脱离 Linux `bnx2x`。这会让 `ens8f0/ens8f1` 在验证期间从 Linux 网络栈消失。

## 保护

- 必须显式设置 `HFT_ALLOW_DISRUPTIVE_DPDK=YES`，否则退出 13。
- 变更前要求两口无地址、无路由、无残留 XDP，且都由 `bnx2x` 驱动。
- 保存 queue、ring、coalescing、GRO/LRO、hugepage、模块与接口完整快照。
- 仅在 NUMA 1 临时分配 512 个 2 MiB hugepage。
- 任何错误、中断或正常退出均执行 trap：两个 PCI 从 UIO 解绑、回绑 `bnx2x`，恢复 queue/ring/coalescing/offload、hugepage、模块与链路 UP。
- 运行结束再次核验两个 PCI 驱动和 TX coalescing；恢复失败使用独立退出码 15，不得把实验结果视为有效。
- 二进制、Rust/C 源、构建 manifest、预检、运行配置、前后快照与哈希全部保存在远端 replay 证据目录。

## 冻结阶梯

先运行 1 Mpps，只有全部硬门禁通过才进入 5 Mpps；之后依次 10、12 Mpps。默认 burst 256。任一级失败即停止升级并保留证据，不以单一吞吐覆盖丢包、P99/P999 或回退失败。

## 当前状态

脚本与配置已实现但尚未执行。双 PF 解绑仍等待显式批准；`final_pareto_ingestion_allowed=false`。
