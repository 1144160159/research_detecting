# CAEOS-EMTD 恶意流量数据集标签处理清单（2026-08-08）

## 判定口径

- **严格流级完成**：标签索引状态为 `ready`，且 `formal_gate_passed=true`、准入门为 `strict_flow_label`。
- **条件准入完成**：标签索引状态为 `ready`，但依赖全捕获成员标签或源质量修正规则；可进入当前工程，论文中必须单独披露证据强度。
- **未完成**：只有原始数据、官方 CSV、前缀检查、流身份重建或候选适配，不计为标签处理完成。
- 覆盖率低于 1 不等于标签错误率；`effective_coverage_fraction=1` 表示保留流均已获得正式标签，未覆盖流按批准规则排除并记录原因与比例。

远端权威清单：`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5/_control/label_index_manifest.json`

远端文件 SHA-256：`8f1aae7a62e1b201b34ea1c190c0b54e6e18df936f3fb584f3105c72474919fc`

## 严格流级完成（5 个）

| 数据集 | 官方标签记录数 | 原始覆盖率 | 有效覆盖率 | 状态 |
|---|---:|---:|---:|---|
| Edge-IIoTset | 7,597,160 | 99.5924% | 100% | `ready / strict_flow_label` |
| CICIDS2017 | 2,830,743 | 76.3482% | 100% | `ready / strict_flow_label` |
| CIC-BoT-IoT | 73,367,604 | 99.9243% | 100% | `ready / strict_flow_label` |
| CIC-ToN-IoT | 22,338,152 | 56.4248% | 100% | `ready / strict_flow_label` |
| CICDDoS2019 | 70,427,637 | 31.2741% | 100% | `ready / strict_flow_label` |

## 条件准入完成（3 个）

| 数据集 | 标签记录数 | 准入依据 | 有效覆盖率 | 论文披露要求 |
|---|---:|---|---:|---|
| CICIoT2023 | 309 | `full_capture_member_inventory` | 100% | 捕获成员级标签，不表述为严格流级标签 |
| CICIoT2022 | 1,152 | `full_capture_member_inventory` | 100% | 归档成员/README 标签，不表述为严格流级标签 |
| DoHBrw2020 | 1,167,136 | `source_quality_adjusted_flow_label` | 100% | 披露重复 CSV 优先级和源质量修正规则 |

因此，当前工程可用的标签处理完成数据集共 **8 个**，其中严格流级完成 **5 个**、条件准入完成 **3 个**。

## 已入队但标签未完成

### CICIDS2018

- 原始资产：10 个官方 PCAP 归档，共 477,321,665,202 字节；10 份官方日级流 CSV 和 10 份日志归档均存在。
- 前置处理：10/10 PCAP 归档已完成流身份重建，生成 4,456 份逐捕获 `Flow.csv`。
- 当前状态：`waiting_for_exact_official_label_join`。
- 阻塞原因：官方日级 CSV 缺少源/目的 IP 和源端口，必须将重建的流身份与官方标签做唯一连接；禁止按整天或仅按攻击时间窗口粗赋标签。
- 调度状态：已经加入四路特征队列，位于 CICIDS2017 之后；只有标签清单、源清单和数据目录三重准入通过后才会启动。

## 尚未完成标签索引

| 数据集 | 当前状态/缺口 |
|---|---|
| ISCX Tor/Non-Tor 2017 | 需要完成无时间戳歧义适配 |
| ISCX VPN/Non-VPN 2016 | 当前未发现可用的本地流标签 CSV 或日志 |
| PARROT2025 | 需要完成 PCAP 与标签配对覆盖审计 |
| CrossPlatform Android/iOS | 需要完成去重和配对覆盖审计 |
| 5GAD-2022 | 旧队列状态为等待资源，未形成当前权威标签索引 |
| UNSW-NB15 | 旧队列状态为 queued，未形成当前权威标签索引 |
