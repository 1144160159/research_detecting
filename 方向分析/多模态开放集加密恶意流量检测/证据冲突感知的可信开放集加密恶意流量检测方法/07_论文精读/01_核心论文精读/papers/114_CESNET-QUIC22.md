# 114 CESNET-QUIC22：一个月骨干链路 QUIC 流量数据集

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / Value / Objective | 第 2 至 4 节 | 已覆盖 |
| Data Description | 第 5 至 8 节 | 已覆盖 |
| Experimental Design | 第 9 至 14 节 | 已覆盖 |
| Ethics / Availability | 第 15 节 | 已覆盖 |

## 1. 文献身份

- 标题：CESNET-QUIC22: A Large One-Month QUIC Network Traffic Dataset From Backbone Lines。
- 作者：Jan Luxemburk、Karel Hynek、Tomáš Čejka、Andrej Lukačovič、Pavel Šiška。
- 期刊：Data in Brief，46，2023，108888。
- DOI：10.1016/j.dib.2023.108888。
- 数据 DOI：10.5281/zenodo.7409923 / record 7409923；版本记录文中还列 10.5281/zenodo.7409924。
- 许可：CC BY 4.0。
- 定位：大规模良性 QUIC 服务分类、背景 OOD、时间漂移和预训练数据；不是恶意流量检测数据集。

## 2. 摘要缩译

QUIC 将可靠传输、安全握手与 HTTP/3 结合，握手可见性低于传统 TLS/TCP，因而需要真实大规模数据。CESNET-QUIC22 来自连接约 500 家机构、服务约 50 万用户的 CESNET2 网络。

数据以 enriched bidirectional flows 的压缩 CSV 发布，包含 packet metadata sequences、flow statistics、QUIC version、SNI、少量 user agent 和服务标签。采集跨度一个月，总计约 1.53 亿保存 flows。

## 3. 数据价值

原始观测来自 100 Gbps backbone links，约 27 TB 实际网络流量；发布数据解压约 89 GB。其价值包括：

- 真实浏览器、操作系统、移动设备与用户行为。
- QUIC service、traffic category、client device classification。
- 三个 background 类支持 web-service OOD/open-world 研究。
- 四周时间跨度支持 temporal drift。
- 可作为 malicious QUIC 研究中的真实 benign traffic。

最后一点不能反向理解为数据含恶意流量；论文没有攻击采集或攻击 ground truth。

## 4. 规模与标签

- 采集：2022-10-31 至 2022-11-27。
- 四周保存 flows：32.6M、42.6M、33.7M、44.1M，总计约 153M。
- 选定 service classes：102。
- Background：Google Background、Facebook Background、Default Background 三类。
- 服务大类：17 categories。
- 选定服务覆盖 CESNET2 QUIC traffic volume 约 84%。

这里的 102/17 是应用服务细粒度/粗粒度标签，不是恶意攻击细类/大类。

## 5. Packet Metadata Sequence

每个 flow 保存前 30 个 packet 的：

- UDP transport header 之后的 payload size。
- Direction，client→server 为 +1，server→client 为 −1。
- Inter-packet time。

同时派生 PPI_LEN、PPI_DURATION、PPI_ROUNDTRIPS。Roundtrip 由 direction change 次数近似。

“Payload size”只是 UDP payload 长度，不是 payload byte content。PPI 最多 30 包，不能宣称为全流完整 sequence。

## 6. Flow Statistics 与 Histogram

整条 bidirectional flow 保存：

- 双向 bytes 与 packets。
- Flow duration。
- 双向 packet-size histogram。
- 双向 inter-packet-time histogram。
- Idle、active-timeout、other end reason。

Histogram 使用 8 个对数 bins：0–15、16–31、32–63、64–127、128–255、256–511、512–1024、>1024，单位分别为 byte 或 millisecond。

PPI sequence 只覆盖前 30 包，而 flow statistics/histograms 覆盖完整导出 flow record，二者时间覆盖不同。

## 7. QUIC Handshake 与身份字段

QUIC Initial Packet 中提取：

- QUIC_SNI。
- QUIC_VERSION。
- QUIC_USER_AGENT，只有约 0.2% flows 有值，但仍约 342K samples。

SNI 用于构建 service label，因此任何 service-classification 模型都必须删除 QUIC_SNI，通常也需删除 server IP/ASN；否则输入直接暴露标签规则。

User agent missingness 不是随机的，使用时应报告有效覆盖率，不能把缺失当普通类别而忽略 selection bias。

## 8. 文件结构

数据按周组织为压缩 CSV，一行一个 flow。每个 flow data file 配套 JSON，记录：

- observed/seen flows。
- 属于 service 的 flows。
- 动态采样后 saved flows。
- per-service counts 与 sampling ratio。

另有 week-level 与 dataset-level stats JSON，以及 feature distributions、QUIC version、user agent 统计。配套 counts 可恢复原始服务比例，是评估真实先验与采样先验差异的关键。

## 9. 采集架构

五个 monitoring points 位于 Prague、Brno、Ostrava，通过 passive optical TAP 接入一个或多个 100 Gbps peering links。各 probe 用 NTP 对齐到同一 time server。

ipfixprobe 负责 flow export；IPFIXcol2 收集；NEMEA 做流式过滤和处理。该链路比从 PCAP 自行重放更接近生产 flow monitoring，但数据不发布 PCAP，无法重新提取 payload bytes 或不同 packet limit。

## 10. 服务选择与标签生成

优先选择高流量且多样的 services。SNI→service mapping 来自：

- 官方 firewall/whitelist documentation。
- Netify Application Lookup。
- 对观测 SNI 的人工分析。

同一 provider 的服务还可合并为 provider group。标签规则透明度较高，但 SNI mapping 可能随 CDN、shared domain 和时间变化产生 label noise。

## 11. Background 与 Open World

未进入 102 selected services 的流量拆为：

- 未选 Google services。
- 未选 Facebook/Meta services。
- 其余 QUIC services。

这提供了 service-level OOD 测试，但不是 security unknown：background 大多是正常应用。若 CAEOS 使用它，只能评估“良性 OOD 不应被误报为恶意”和跨协议/跨域 robustness。

Background 还可能含未识别恶意流，但没有 threat-intelligence ground truth，因此不能当作 confirmed malicious unknown。

## 12. Flow Export Timeout

- Active timeout：5 min。
- Inactive/idle timeout：65 s。

长 connection 会被切为多个 flow records；这会使同一连接跨记录高度相关。训练/测试若随机按 row 拆分，会发生 connection/service/time leakage。

严格实验应按时间周、匿名 client prefix、server/service 或可恢复 connection group 设计 split，而不是随机行拆分。

## 13. 过滤规则

只保留：

- Destination port 443/UDP。
- QUIC SNI 非空。
- 两个方向至少各一个 packet。

被排除的 unidirectional flows 可能来自 scanning、connection error 或 asymmetric routing。该过滤使数据更适合服务分类，却系统性删除了一部分安全异常，进一步说明它不是攻击检测全流量数据。

## 14. 动态采样

为缓解类别极不平衡，按 service prevalence 动态采样：

- Top 5% services：1:15。
- Bottom 60%：不采样。
- 中间 35%：约 1:2 至 1:9。
- 三个 background：1:15。
- Sampling ratio 每 5 min 更新。

发布分布是 softened imbalance，不等于真实 backbone prior。比较 classifier 时应同时报告 released-balanced 结果与按 JSON 恢复原始 prior 的加权结果。

## 15. 匿名化与伦理

Client IP 用 Crypto-PAn prefix-preserving anonymization，保留 subnet structure；server IP 保留，因为被视为公开信息；MAC 和其他可识别字段删除。

Prefix-preserving IP 仍可能成为 institution/client-group shortcut。正式模型应默认排除 IP、port、ASN、SNI、absolute time，除非研究目标就是网络运营实体识别。

# 第二部分：独立技术分析

## A. 一句话结论

CESNET-QUIC22 不应进入 CAEOS “含恶意流量主数据集”清单；它最适合用作大规模良性 QUIC 预训练、良性 OOD/FAR 压力测试和时间漂移数据，并为 sequence＋statistics 双视图提供标准化字段。

## B. 两条交付线

### 工程线

若纳入基础 CSV，只建立 `benign_external_quic` 支线：保留 PPI、flow statistics、service/category/background、week 与 sampling weight；删除模型可见的 SNI/IP/ASN/port/absolute timestamp，记录 PPI 截断和 timeout split。

### 论文线

把它列为外部良性域验证，而不是恶意检测训练/测试数据。报告“模型是否把新 QUIC 正常服务误报为 malicious/unknown”，重点指标是 Benign FAR、Known/Benign Acceptance 和 calibration shift。

## C. 数据协议审计

- Labels：SNI mapping 的 service/category，不是攻击标签。
- Malicious ground truth：无。
- OOD：三个未选 service background，属于 service OOD。
- Input leakage：SNI、server IP/ASN 与标签高度直接相关。
- Split：论文只发布数据，不规定安全 ML split；随机 row split 风险高。
- Sampling：动态 class-dependent，发布先验被改变。
- Protocol：`D0-benign-QUIC-service-and-background-OOD/P3-SNI-IP-time-shortcut-random-row-split-and-dynamic-sampling-risk`。

## D. 是否构成三模态

原数据可稳定形成两个非重复视图：

1. Packet sequence：size＋direction＋IAT，前 30 包。
2. Flow statistics：全 flow counters＋histograms。

QUIC handshake/version 可作为第三 context view，但 SNI 是标签源，user agent 仅 0.2% 覆盖，不能构成普适第三模态。没有 payload bytes，也没有 PCAP 可重新提取字节载荷。

因此对 CAEOS 来说它最多是“双视图良性 QUIC”，不是完整三模态恶意数据集。

## E. 三层指标适用性

| 层级 | 数据可支持 | CAEOS 用法 | 判定 |
|---|---|---|---|
| 已知识别 | 102 service / 17 category | 不对应恶意 family Macro-F1 | 任务不同 |
| 未知检测 | 3 background service classes | 良性 OOD/FAR 压力测试 | 有条件适用 |
| 联合开放集 | 已知服务＋background | 可做 service OSR，不是恶意 OSR | 不可直比 |
| 校准 | 长期大量良性流 | temporal/domain calibration shift | 适用 |

## F. 95%/5% 安全门

该数据最直接检验的是安全门的反面风险：当外部良性 QUIC 到来时，模型是否误报恶意。应报告：

> Benign FAR = 被判为 malicious 的 CESNET flows ÷ 全部 CESNET flows。

目标可设 FAR≤5%，但不能用 CESNET 服务分类 accuracy 替代。若把 background 当 unknown rejection，必须同时说明拒识“正常新服务”在安全运营中的代价。

## G. 采纳与排除

### 采纳

- PPI size/direction/IAT schema。
- 全流 histogram/statistics schema。
- Week-based temporal split。
- Sampling weight 恢复真实 prior。
- 外部良性 FAR 与 calibration drift。

### 有条件采纳

- QUIC version 可作 context，但需检查版本与周/服务 shortcut。
- Anonymous prefix 可用于 group split，不能作为输入。
- Background 可做 service OOD，不得标作恶意 unknown。

### 排除

- SNI、server IP、ASN、port、absolute time 作为分类输入。
- 随机 row split。
- 把 UDP payload size 写成 payload bytes。
- 把 PPI 前 30 包写成完整流 packet sequence。
- 把数据列入恶意流量数据集数量统计。

## H. CAEOS 可执行实验

1. `E-QUIC-01`：CESNET 四周 week-based benign FAR。
2. `E-QUIC-02`：CIC/ToN/BoT 训练后外部 QUIC zero-shot calibration。
3. `E-QUIC-03`：sequence-only、statistics-only、双视图融合。
4. `E-QUIC-04`：移除 SNI/IP/ASN/time 的 shortcut audit。
5. `E-QUIC-05`：released prior vs sampling-weight restored prior。
6. `E-QUIC-06`：service background rejection 与恶意误报分解。
7. `E-QUIC-07`：PPI truncation 5/10/20/30 packets，不能外推超过 30。
8. `E-QUIC-08`：week-to-week ECE/Brier/NLL 与 risk drift。

## I. 可引用与不可引用主张

### 可引用

- 数据来自一个月 100 Gbps backbone QUIC 流量，总计约 153M flows。
- 发布 102 service labels、17 categories 和 3 background classes。
- PPI 保存前 30 包的 size/direction/IAT。
- Flow statistics/histograms 覆盖完整导出 flow record。
- SNI→service mapping 生成标签。
- 数据按 service 动态采样并提供 seen/saved counts。

### 不可引用

- CESNET-QUIC22 含官方标注恶意流量。
- Background 是未知攻击。
- 数据含 payload bytes 或 PCAP。
- 三个 handshake 字段构成无泄漏第三模态。
- 随机流拆分适合该数据。
- 发布类别比例代表真实 backbone prior。

## J. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至期刊/DOI/数据 DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`D0-benign-QUIC-service-and-background-OOD/P3-SNI-IP-time-shortcut-random-row-split-and-dynamic-sampling-risk`
- G5 方法/数据门：通过
- G6 结果门：数据论文无模型主结果；规模、字段、标签、采样已核读
- G7 对比门：通过至数据用途边界
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
