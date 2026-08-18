# 2026-08-13 新高速 NIC R0 自动实验链

## 状态边界

- 独立合同、复算器、composer、两阶段 runner 与合成负向测试：已实现。
- 当前 10.0.5.8：没有到货的新高速 NIC，只允许得到 `hardware_pending`。
- native AF_XDP、DPDK、12 Mpps 与故障切换实机结果：尚未执行，不能声称通过。
- `r0_qualified` 只代表本合同的 R0 实验完成；`production_qualified` 和
  `final_pareto_ingestion_allowed` 永远为 `false`。
- 本修复没有修改现有 bnx2x runner、统一发布审计或生产 Pareto 选择器。

## 修复原因

到货验收链只验证 PCIe/NUMA/管理面隔离、驱动固件、native XDP/forced
zero-copy、DPDK RSS/TSS 与至少八队能力。它没有形成完整 R0 工作负载：XDP 主路
三次、DPDK 回退三次、连续流量下三次故障切换、逐窗资源与关键流、P99/P999 以及
恢复前后状态。因此，到货门通过也不能推出 12 Mpps 工程目标通过。

## 新增文件

1. `configs/new_nic_r0_campaign_contract_v1.json`
   - 固定 64 B、至少 12 Mpps、至少 15 s、XDP/DPDK 各恰好三次。
   - native AF_XDP 必须是 driver/native attach 和 forced zero-copy；DPDK 必须有
     RSS、TSS、RETA 与至少八个 RX/TX queue。
   - 每队包计数从原始整数重算，至少八队各占总量 5%，拒绝单队极端偏斜。
   - 每次都要求零发生器错误、零丢包、零重复、零乱序；累计直方图末桶必须等于
     unique packet 数，并重算 P99/P999。
   - 延迟只允许硬件时间戳/PTP 关联或发生器 marker 单调时钟关联，时钟误差不超过
     5 us，所有 unique packet 都必须有延迟样本。
   - 每次至少 15 个资源样本，间隔和首尾覆盖都不超过 2 s；逐窗检查 CPU、内存、
     RSS 与 HugePage。
   - 关键流分母必须来自独立发生器 marker manifest，覆盖率至少 99%，预算跳过为零。
   - 三次 forced XDP primary stop 都从 monotonic ns 重算恢复时间，要求不超过
     300 ms，且切换窗零丢包、零重复、零乱序。
   - 禁止在运行时对同一 PF 改绑驱动；只接受预置第二 PF、预置 VF/SF 或无需运行时
     PF 改绑的 bifurcated PMD。
2. `hft_mgbs/new_nic_r0.py`
   - 对合同、campaign、六次运行、三次 fallback、资源、发生器和恢复 receipt 做
     严格类型校验与原始指标复算。
   - 每个 receipt 的内容 SHA-256 会去掉 `receipt_sha256` 后重新计算；producer
     SHA-256 必须与最终可信 artifact manifest 中对应 helper 的实际 hash 相同。
   - 发生器窗口与资源窗口是各自独立的 hash-bound receipt，不能由 capture runner
     嵌套一个未认证布尔量代替。
   - fallback 的发生器连续性由独立 generator receipt 的 requested/sent/error、
     fault 前/中/后正包量和最大 inter-packet gap 重算；`generator_continuous=true`
     本身不能通过该门。XDP 的 driver/bind flags、zero-copy/copy 原始包量，以及 DPDK
     RETA、RSS 类型和 RX/TX 每队原始包量同样会重算，不能由能力布尔量代替。
   - 恢复快照必须区分 `before`/`after`，并覆盖管理面、XDP attach、PCI driver 与
     override、MTU/txqlen、offload/channel/ring/coalesce、RSS/RETA、IRQ affinity、
     全 NUMA HugePage 和 DPDK runtime prefix；所有域 canonical hash 必须一致。
3. `scripts/compose_new_nic_r0_acceptance.py`
   - 拒绝重复 JSON key、NaN/Infinity、绝对路径、目录穿越、符号链接、重复 role/path
     和 artifact hash 漂移。
   - 正式模式只接受外部提供的完整 artifact-manifest SHA-256，并复核运行中的
     composer 与 imported evaluator 就是 manifest 中冻结的字节。
   - 原子写出 fail-closed 结果；畸形数值不会产生无输出的 Python traceback。
4. `scripts/run_new_nic_r0_campaign.sh`
   - `PENDING` 是默认路径，只写 `hardware_pending` 证据，退出码 20，不检查或改变 PF。
   - `EXECUTE` 需要精确授权串、维护窗口、变更单、外部 helper-manifest SHA-256，
     以及外部根绑定且已达到 `self_consistent_capability_receipts_only` 的到货验收证据。
   - 所有可执行 helper、runner、合同、composer 和 evaluator 都复制到本次唯一目录，
     复哈希后只执行冻结副本；运行全程持有独占锁。
   - `campaign_executor` 固定接收 12 Mpps、15 s、三次 XDP、三次 DPDK、三次 fallback
     参数。runner 从冻结到货证据复制 inventory/preflight，执行后再次校验，禁止
     executor 覆盖到货结论。
   - 信号和异常进入有 TERM/KILL timeout 的恢复；清理期间忽略第二信号。若恢复仍
     失败，写入持久 `RECOVERY_REQUIRED` 并退出 97。`RECOVER` 阶段可在 SSH 断线或
     进程意外终止后只使用原冻结 restore helper 继续恢复。
   - `EXECUTE` 完成恢复后生成候选 manifest，由冻结的 `trust_root_recorder` 写到
     显式指定且位于整个 evidence root 之外的新路径；runner 不提供同盘默认回执。
     返回 21 后，`COMPOSE` 必须再次提供 helper 根、外部 evidence
     根和外部 receipt，三者逐字节一致才会复算 R0。这避免一次进程自己生成证据又
     自己声称其可信。
5. `tests/test_new_nic_r0.py`
   - 用完整合成原始 receipt 验证唯一的 R0 正例，并覆盖低于 12 Mpps、窗口不足、
     丢包、P99、时钟来源、资源越界/采样缺口、关键流、generic/copy XDP、DPDK
     畸形队列类型、队列偏斜、慢切换、切换丢包、恢复漂移、同机发生器、同 PF
     runtime rebind、receipt 篡改和外部 manifest 篡改等负例。

## runner helper 接口

runner 不内嵌任何厂商 PF 命令。到货后必须另外提供并冻结以下硬件相关实现：

| role | 最小职责 |
|---|---|
| `xdp_runner` | native attach、`XDP_ZEROCOPY` 强制 bind、八队收包、原始 NIC/XSK/序列计数与延迟直方图 |
| `dpdk_runner` | 预置回退面、RSS/TSS/RETA、八队收包与同一计数结构 |
| `generator_runner` | 独立主机/独立 NIC 持续发送，输出 requested/sent/error 和 marker identity receipt |
| `resource_sampler` | 在每个运行窗采集主机 CPU/内存、进程 RSS、全 NUMA HugePage |
| `fallback_orchestrator` | 在发生器不停流时强停 XDP primary，记录 fault/首个 DPDK packet 单调时间与过渡序列 |
| `restore_helper` | `snapshot-before`、`restore`、`snapshot-after` 三模式，恢复全部合同状态域 |
| `campaign_executor` | 只编排冻结 helper，输出 `campaign.json`、六个 run receipt 和三个 fallback receipt |
| `trust_root_recorder` | 把候选 manifest hash 写入 campaign 目录外的批准存储；不得只是普通可覆写的同目录文件 |

`campaign_executor` 和以上 runner/helper 的代码尚未因具体新 NIC 型号确定而实现；它们
是当前唯一剩余的软件适配层。合同、复算器和 orchestration 不依赖厂商。

## 状态和退出码

| 状态/退出码 | 含义 |
|---|---|
| `hardware_pending` / 20 | 默认只读占位，无 R0 实机证据、零变更 |
| `evidence_pending` / 21 | 硬件阶段已恢复并封存，等待以外部根执行 COMPOSE |
| `r0_qualified` / 0 | 所有原始门和外部 provenance 均通过，仅 R0 |
| `r0_rejected` / 22 | 原始指标、重复次数、拓扑、切换或恢复任一失败 |
| 74--75 | 授权、helper provenance 或到货证据根失败，禁止开始变更 |
| 97 | 恢复失败，必须保留 `RECOVERY_REQUIRED` 并执行 RECOVER |

## 到货后的顺序

1. 先用 `run_new_nic_acceptance.sh` 完成只读 inventory 和授权 capability receipt，
   独立记录该目录 `evidence.sha256` 的 SHA-256。
2. 实现与新 NIC 驱动/PMD 对应的八个 helper，制作 role/path/SHA-256 helper manifest，
   在批准的变更记录中保存 manifest SHA-256。
3. 设置 `HFT_NEW_NIC_R0_PHASE=EXECUTE` 及精确授权、到货证据根后运行；返回 21 是预期
   的两阶段边界，不是 R0 通过。
4. 由批准的 `trust_root_recorder` 在 campaign 外保存 evidence manifest SHA-256，再用
   `HFT_NEW_NIC_R0_PHASE=COMPOSE` 和该外部 receipt 复算。
5. 只有 COMPOSE 返回 0 才能称 R0 通过；仍需后续 R1--R4 和生产 Pareto 门。

## 测试与未完成项

本地合成测试命令：

```text
python -m unittest discover -s tests -p test_new_nic_r0.py -v
bash -n scripts/run_new_nic_r0_campaign.sh
```

最终本地 33 项可执行测试通过，1 项 Linux 动态 runner 测试在 Windows 跳过；
10.0.5.8 上 34/34 全部通过（Linux 动态项实际执行）。物理机默认命令
`env -i HOME=/root PATH=... bash scripts/run_new_nic_r0_campaign.sh` 返回 20，证据目录为
`/home/wangwt/task/datasets/replay/hft_new_nic_r0_20260813T022841514083544Z_oySJ7i`；
audit 与 runner state 均为 `hardware_pending`、`mutations_performed=false`，
`evidence.sha256` 2/2 校验通过，清单 SHA-256 为
`5717be463e2bf8cb4f27820fe5097578924ff32ab5aa6ab26ef3c6871525e4e3`。
这些结果只验证默认零变更路径和合成复算器，不能描述为新 NIC 实机 R0。

新硬件到货前仍缺：实际接口/PF/VF 拓扑、驱动/固件/DDP 定版，独立发生器与 PTP
时基，八个硬件 helper，以及由这些实现产生的正式 arrival/R0 evidence roots。
