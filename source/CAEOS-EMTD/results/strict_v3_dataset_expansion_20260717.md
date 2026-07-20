# Strict-v3 恶意流量数据扩展检查点

更新时间：2026-07-17（阶段检查点）

## 1. GPU 服务器数据盘点

| 数据集 | 服务器占用 | 当前形态 | 接入优先级 |
|---|---:|---|---:|
| NF-UNSW-NB15-v2 | 454 MB | 单个 NetFlow v2 CSV，共 2,390,275 流 | P0 |
| CIC-IDS2017 | 52 GB | PCAP、TrafficLabelling CSV、MachineLearning CSV | P0 |
| CIC-ToN-IoT | 3.4 GB | 单个 CICFlowMeter CSV | P1 |
| CIC-BoT-IoT | 8.5 GB | 单个 CICFlowMeter CSV | P1 |
| CICDDoS2019 | 25 GB | CSV/PCAP 压缩包 | P1 |
| CICAPT-IIoT2024 | 5.1 GB | 两阶段 PCAP 与拆分 PCAP | P1 |
| CICIoT2023 | 565 GB | 702 个文件，以 PCAP 为主 | P2 |

## 2. NF-UNSW-NB15-v2

原始数据包含 Benign 和 9 个攻击类别。旧矩阵只定义 Analysis、Backdoor、DoS、Exploits、Generic、Reconnaissance 6 个留一攻击场景，现已补入 Fuzzers、Shellcode、Worms，形成 9 个场景。

指纹审计显示，seed 7、每类上限 5000 的随机切分中，测试集 5409 条流有 3519 条与训练集共享特征指纹。因此 strict-v3 固定使用：

1. 未知类先隔离；
2. 只在已知类中删除跨标签同指纹组；
3. 按特征指纹分组切分；
4. 记录完整 split fingerprint。

9 个留一场景均已完成真实 split 冒烟，train/validation/test 指纹重叠均为 0。Worms 只有 164 条，保留但应报告置信区间和样本量敏感性。

## 3. CIC-IDS2017

TrafficLabelling 原始 CSV 共扫描 3,119,345 行。WebAttacks 文件末尾含 288,602 条空标签拼接记录，已在标签统一阶段剔除；有效流为 2,830,743 条，14 个攻击标签均完整出现。

清洗后的严格源缓存使用 73 个非 IP 数值流特征、`Capture_ID` 和标签无关 `Flow_Group`。流组定义为：捕获文件、无向端点端口对、协议、精确时间戳、持续时间、双向包数和字节数的 SHA-256。当前源缓存 SHA-256：

`0e23470358d0d1188d7775669db57629750ae64f882f556729038a8bd7492074`

seed 7、每类上限 5000 的分层缓存共 49,193 条流，SHA-256：

`bb5ced6383b461e0ba85d58de10828733eb35bedf6427d3fc836eef061286a62`

14 个留一场景已逐一通过：

- 已知类跨标签特征指纹冲突行：0；
- train/validation/test 流组交叉：全部为 0；
- 每个已知类均覆盖三个 split；
- 14/14 场景可构建。

主统计包含 11 个样本量不低于 500 的攻击场景。Heartbleed（11）、Infiltration（36）、Web Attack - Sql Injection（21）固定标记为 `low_support_sensitivity`，单独报告，不进入未加说明的主均值。

## 4. 扩展后的实验规模

strict-v2 保持 3 数据集、38 场景不变。strict-v3 第一批新增：

- NF-UNSW-NB15-v2：9 场景；
- CIC-IDS2017：11 个主场景 + 3 个低支持敏感性场景。

第一批扩展后共有 5 个数据集、61 个留一攻击场景，其中主统计场景 58 个，低支持敏感性场景 3 个。

seed `7/11/19/23/37` 的 NF-UNSW-NB15-v2 和 CIC-IDS2017 固定缓存已经全部生成，共 10 个缓存。缓存审计逐项核对实际 CSV SHA-256、sidecar SHA-256、种子、每类上限、实际行数和类别计数，结果为 10/10 通过、失败 0。审计记录见 `results/strict_v3/cache_audit_5seed.json`。

下一阶段不直接启动 61 场景乘 20 基线的完整矩阵。先在两个新增数据集上运行 CAEOS、共享 MLP 风险和 strict-v2 最强基线的代表场景试验，确认特征模态、训练稳定性和统计量级后，再决定完整扩展范围。
