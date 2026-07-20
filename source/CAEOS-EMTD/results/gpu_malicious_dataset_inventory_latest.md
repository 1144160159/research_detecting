# GPU 恶意流量数据集扩展库存

更新时间：2026-07-18

## 已完成可重放审计

| 数据集 | 规模 | 恶意场景 | 分组证据 | 协议层级 | 结论 |
|---|---:|---:|---|---|---|
| DoHBrw2020 | 16,000 流 | 3 | benign/dns2tcp/dnscat2/iodine 分别 20/96/570/467 个 CaptureId | strict capture-group | 立即进入严格扩展 |
| HIKARI2021 | 555,278 流 | 4 | 四个攻击类各只有 1 个 SourceGroup | fingerprint-isolated | 单列扩展，不混入严格主表 |

DoHBrw2020 加入后，严格采集组协议由 7 数据集、102 场景扩展到 **8 数据集、105 场景**。再计入 HIKARI2021 指纹隔离层后，总覆盖为 **9 数据集、109 场景**。审计 manifest SHA 为 `7fdf073bdccb342227c9af4cec2f6b31614f3045c5305cab0a2f293a93709557`。

## GPU 服务器候选库存

| 优先级 | 数据集 | 服务器状态 | 当前障碍 | 下一步 |
|---|---|---|---|---|
| P0 | CICAPT-IIoT2024 | 约 12 GB；另有 5.1 GB 原始公开包、24 个 PCAP、两阶段网络 CSV、MITRE 攻击时间表 | CSV 尚未绑定 PCAP/时间窗为 CaptureGroup；标签需按战术或技术归一 | 基于 PCAP 文件和攻击时间表构造 capture-aware 流表，审计每类组数 |
| P1 | CIC-BoT-IoT | 8.5 GB；主 CSV 7.4 GB，含 `Label` 与 `Attack` | 单一大 CSV，尚无冻结采集组字段 | 审计 Timestamp、源端和攻击会话，禁止直接随机拆分 |
| P1 | CICDDoS2019 | 25 GB；PCAP 与 CSV 目前为压缩包 | 尚未解包，攻击类别与采集日/文件组关系未审计 | 只解包元数据和必要 CSV，按采集文件建立组 |
| P1 | LSNM2024 | 2.4 GB；15 个恶意目录和 1 个 benign 文件 | 多数攻击仅 1 个 CSV，benign 也只有 1 个文件，不能直接证明跨采集泛化 | 检查原始时间段/PCAP能否形成每类至少 3 组 |
| P2 | Mal_TLS2023 | 82 MB；已有配置和 6 个恶意场景 | 配置无采集组字段 | 只能进入 fingerprint-isolated 层，除非补充原始采集身份 |
| P2 | CICDarknet2020 | 70 MB 单 CSV | 存在重复 `Label` 表头，Tor/Non-Tor 与应用类别不等同于良/恶性标签 | 先重建语义明确的标签协议，不直接登记为恶意检测数据集 |

## 纳入门

1. 必须同时存在明确 benign 和恶意细类标签。
2. 严格主表要求每个纳入标签至少 3 个独立采集组，且 train/validation/test 组不重叠。
3. 只有指纹隔离能力的数据集必须单列，不与 strict capture-group 结果合并排名。
4. 数据目录存在、CSV 可读或论文声称含攻击都不等于完成纳入；必须生成缓存 SHA、标签计数、组计数和拆分 fingerprint。
