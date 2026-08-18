# 2026-08-13 新高速 NIC 到货即执行验收链

## 状态

- 工具链：已实现并完成本地负向测试。
- 新高速 NIC 实机：未到位，当前状态只能是 `hardware_pending`。
- 生产资格：`false`。
- 最终 Pareto 输入：`false`。

本记录只说明验收工具已就绪，不代表任何新 NIC、native XDP、AF_XDP
zero-copy 或 DPDK 多队列已通过实机验收。

## 修复原因

现有 `capture_hardware_upgrade_gate_v1.json` 给出了采购后的能力要求，但没有一条
独立、可复算、默认无 PF 变更的到货验收链。若只读取网卡型号、`ethtool -i` 或
PMD 文档，容易把“可能支持”误写成“本机已通过”。此外，现有 bnx2x runner 属于
当前 BCM57810 的诊断链，不能被复用成新硬件合格证明。

## 新增内容

1. `configs/new_nic_acceptance_contract_v1.json`
   - 冻结 PCIe 当前协商宽度/速率、NUMA 本地性、管理面隔离、驱动/固件/DDP、
     native XDP、forced AF_XDP zero-copy、DPDK RSS/TSS、多队列和独立发生器门。
   - 排除当前 `0000:cb:00.0/1` BCM57810 和 `0000:e3:00.0--3`
     BCM5719 管理适配器，防止既有硬件冒充到货候选。
   - 默认只读；PF/XDP/DPDK 状态变更需要三个精确环境授权、变更单和 hash 冻结
     helper manifest。
2. `configs/schemas/new_nic_inventory_v1.schema.json` 与
   `configs/schemas/new_nic_preflight_result_v1.schema.json`
   - 固定原始 inventory 和判定结果结构。
   - 结果 schema 明确 `production_qualified=false` 和
     `final_pareto_ingestion_allowed=false`；这条链只允许硬件预验收，不越权替代
     R0--R4/Pareto 门。
3. `hft_mgbs/new_nic_acceptance.py`
   - 从原始 inventory 和能力探针 receipt 重新计算判定。
   - receipt 必须绑定 capture host、PCI 地址、独立 run ID、时间顺序、receipt 和
     probe binary SHA-256；receipt 内容 hash 会重算，probe binary hash 必须与冻结
     helper manifest 一致，并验证恢复声明。
   - XDP/DPDK 每队原始包计数都会重算总量、活动队列与份额；至少 8 队分别占
     5%，拒绝 `[N,1,1,...]` 形式的伪多队列。
   - before/after 指纹覆盖管理面、默认路由、candidate kernel driver、master、IP。
4. `scripts/preflight_new_nic.py`
   - 自动发现排除旧 PCI/管理面后的物理接口，或按显式接口集合采集。
   - 只执行 sysfs、`ip`、`ethtool`、`lspci`、`bpftool feature probe` 查询。
   - 支持离线 inventory 重放；所有输出原子写入。
5. `scripts/run_new_nic_acceptance.sh`
   - 默认仅运行 inventory/preflight，当前没有新 NIC 时以退出码 20 输出
     `hardware_pending`。
   - 只有 `capability_probe_pending` 才能进入显式授权分支。
   - runner 自身不嵌入厂商 PF 命令；仅调用 hash 冻结的 XDP/DPDK/恢复 helper。
   - 授权分支要求变更记录提供独立可信 manifest SHA-256；随后把 helper、runner、
     validator、module 和合同复制进证据目录，复哈希并只执行冻结副本，关闭
     hash-check 到 exec 的 TOCTOU 窗口。
   - 原始合同路径先与可信 manifest 完成身份核验，随后才把合同和执行入口切换到
     证据目录内的冻结副本；该顺序避免把冻结副本误与原路径比较而触发授权分支
     `exit 74`，并由静态顺序负向测试锁定。
   - 信号或失败统一进入恢复，恢复 helper 与 before/after 指纹任一未通过即退出
     97，不能将失败包装成成功；恢复 helper 有 TERM/KILL 超时，清理期间忽略第二
     信号并继续封存证据。
   - 恢复指纹覆盖 XDP attach、driver/driver_override、MTU、txqlen、offloads、
     channels/rings/coalesce、RSS/RETA、IRQ affinity、全部 NUMA HugePage、DPDK
     runtime prefix、管理面和默认路由。

## 状态语义

| 状态 | 含义 | 可否声称通过 |
|---|---|---|
| `hardware_pending` | 没有检测到非旧 BCM57810 的候选口 | 否 |
| `invalid_inventory` | inventory envelope/JSON 不可信 | 否 |
| `preflight_failed` | PCIe、NUMA、管理面、版本、队列或发生器硬门失败 | 否 |
| `capability_probe_pending` | 只读 inventory 合格，但缺 native-ZC/DPDK 实测 receipt | 否 |
| `self_consistent_capability_receipts_only` | inventory 与本地冻结 helper receipt 内容自洽 | 仅本地自洽，不是外部认证；仍非硬件/生产资格 |

能力 receipt 的自哈希只证明内容未在本地链内漂移，不能证明其外部真实性。完整
硬件资格仍需由批准的变更记录提供可信 manifest SHA-256 根，并在 R0--R4/最终
Pareto 门中绑定独立原始计数。此工具不会输出 `production_qualified=true`。

## 到货后命令

先执行默认只读模式，不设置任何授权环境变量：

```bash
cd /home/wangwt/phase_2/code/HFT-MGBS
HFT_NEW_NIC_INTERFACES=ens10f0 \
HFT_NEW_NIC_WORKER_CPUS=48,49,50,51,52,53,54,55 \
HFT_NEW_NIC_STACK_ATTESTATION=/approved/path/stack-attestation.json \
HFT_NEW_NIC_GENERATOR_ATTESTATION=/approved/path/generator-attestation.json \
bash scripts/run_new_nic_acceptance.sh
```

输出目录固定在 `/home/wangwt/task/datasets/replay/hft_new_nic_acceptance_*`，本地
仓库不存 inventory、probe receipt 或结果数据。只有只读结果为
`capability_probe_pending`，且已有人批准维护窗口、变更单、具体 helper 后，才允许
设置合同中的授权变量运行能力分支。

## 测试

本地命令：

```text
python -m unittest tests.test_new_nic_acceptance -v
```

结果：物理机 28/28 通过（含动态 runner）；最终同步后物理机联合定向回归
55/55 通过；本地 27/27 可执行测试通过、1 项 Linux 动态测试因 Windows 平台
跳过。最终默认只读预检证据目录为
`/home/wangwt/task/datasets/replay/hft_new_nic_acceptance_20260813T002425014098848Z_BrmFie`，
退出码为 20，`status=hardware_pending`、`candidate_ports=0`、
`mutations_performed=false`；`evidence.sha256` 2/2 通过，清单 SHA-256 为
`ad58c9687524e2be9b163f0634cfd36ad9a576d3783a81f9a3fb92e33c05615d`。
负向覆盖：无新硬件、旧
BCM57810/BCM5719（含 PCI 重枚举）冒充、双口共享 serial、PCIe 降速、NUMA
跨节点、管理口/IP/默认路由污染、driver/firmware/DDP 不匹配、同机/同卡发生器、
generic XDP/copy fallback、DPDK 单活动队列/缺 TSS、receipt host/run 身份漂移、
恢复漂移、非法 envelope、重复 JSON key、NaN/Infinity、损坏 JSON、极端队列
偏斜、畸形数值类型、自引用证据清单，以及 runner 授权/冻结副本/恢复顺序。

## 未完成项

- 新 NIC 到货后尚未在 10.0.5.8 生成正式只读 inventory。
- 尚未提供本机实际 driver/firmware/DDP compatibility attestation。
- 尚未生成 forced AF_XDP zero-copy 和 DPDK RSS/TSS 多队列 receipt。
- 尚未执行独立发生器 15 Mpps headroom、R0--R4、24/72 小时稳定性。
