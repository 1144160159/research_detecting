# DPDK 证据空数组与错误退出码修复

## 现象

2026-08-12 正式 Q1 在数据面运行和主机恢复均完成后，证据封存阶段报错：

`missing_files：未绑定的变量`

对应目录为：

`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T073500338872332Z`

该目录中的原始运行结果、资源验收和恢复账本均已生成，但未形成完整哈希清单与最终 acceptance，故该次运行不得作为发布验收结果。更严重的是 SSH 命令返回 0，说明清理函数内部的 Bash 致命错误没有通过最终退出码 fail-closed。

## 根因

runner 启用了 `set -u`。在当前 Bash 语义下，仅声明但从未赋值的空数组仍可能被视为未绑定变量。当没有缺失文件时，`missing_files` 没有发生追加赋值，随后 `${#missing_files[@]}` 触发致命错误。

同时 `finalize` 一开始移除了 EXIT trap。若证据构建阶段发生 nounset 等 shell 级致命错误，清理函数无法执行其最终状态合成，外层观察到的退出码可能错误地为 0。

## 修复

- `required_files`、`present_files`、`missing_files`、`empty_files` 和 `snapshot_suffixes` 全部显式初始化为 `()`；
- `finalize` 进入后将 EXIT trap 替换为非递归应急保护：任何未预期的清理期致命错误固定返回 99；
- 显式捕获 `build_evidence` 返回码，非零时返回 17；
- 正常完成状态合成后才移除应急 EXIT trap；
- 新增合同测试，固定上述数组初始化和清理期错误码语义。

## 独立恢复核验

故障发生后独立检查确认：ens8f0/ens8f1 均已绑定 `bnx2x`，UP/LOWER_UP、10Gb/s、carrier yes；node0/node1 的 2 MiB HugePage 均为 0；无 HFT DPDK 进程，且 UIO 模块未残留。该恢复事实不改变本次证据封存失败、不得验收的结论。

## 性能数据边界

该故障目录中的数据面观测可用于诊断，但不能作为发布验收：15 个完整窗口的 TX/RX 最低速率约为 1.009920/1.009925 Mpps，收发 15,150,080 包且数据面计数无丢包，P99/P999 约为 20.92/80.55 微秒，RSS 40,492 KiB，进程平均 CPU 约 0.97 核。必须用修复后且哈希重新冻结的 runner 重跑，才能形成可信 acceptance。
