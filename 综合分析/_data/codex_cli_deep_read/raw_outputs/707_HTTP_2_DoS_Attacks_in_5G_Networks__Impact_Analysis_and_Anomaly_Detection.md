# [707] HTTP/2 DoS Attacks in 5G Networks: Impact Analysis and Anomaly Detection

## 1. 基本信息
- 论文：HTTP/2 DoS Attacks in 5G Networks: Impact Analysis and Anomaly Detection
- 作者：Nathalie Wehbe、Hyame Assem Alameddine、Chadi Assi
- 来源：IEEE Transactions on Mobile Computing，Vol. 25, No. 7，July 2026
- DOI：10.1109/TMC.2026.3657143
- 主题定位：5G SBA 控制面安全、HTTP/2 DoS、恶意流量与入侵异常检测
- 本地材料：正文包完整，未标记截断；未发现该论文对应的本地开源代码包。

## 2. 中文翻译与核心摘要
题名可译为：**5G 网络中的 HTTP/2 拒绝服务攻击：影响分析与异常检测**。

这篇论文的核心不是提出一种全新的 HTTP/2 攻击，而是把已经在 Web 环境中被认识的 HTTP/2 DoS 攻击放进 5G SBA 控制面里，验证它们是否真的会破坏 NF 间信令，并进一步构造面向异常检测的数据集。作者用 free5GC 和 UERANSIM 搭建符合 3GPP 流程的 5G 核心网实验环境，模拟 6 类 HTTP/2 攻击：两类 stream multiplexing attack、rapid reset、三类 slow-rate attack。论文最有价值的地方在于说明：在 5G SBA 中，攻击影响并不局限于被打的 NF，AMF、SMF、UDR、PCF 等 NF 之间的过程依赖会放大异常，形成连锁退化甚至 DoS。

检测部分采用 Wireshark 抓包、CICFlowMeter 提取 84 个流特征、方差阈值筛出 54 个高变化特征，再比较 AE、LSTM-AE、Isolation Forest。平均 F1 分别为 LSTM-AE 92.24%、AE 83.28%、IF 84.34%。结论是：仅靠消息计数不足以发现慢速 HTTP/2 操纵，带时间建模能力的 LSTM-AE 更适合 5G SBA 中跨流程、跨 NF 的异常检测。

## 3. 论文解决的具体问题
论文针对的是一个很具体的空白：5G SBA 已经把 HTTP/2 作为 NF 间 SBI 信令协议，但已有 HTTP/2 DoS 研究大多在 Web 服务器语境下，已有 5G 安全研究又多聚焦 jamming、MITM、切片隔离、传统 DoS 或非 HTTP/2 协议。

作者要回答三件事：
1. Web 中的 HTTP/2 DoS 技术迁移到 5G SBA 后，是否仍然有效？
2. 它们攻击某个 NF 时，会不会通过 5G procedure 依赖影响其他 NF？
3. 仅用流量级特征，能否建立对 HTTP/2-5G 特定攻击有效的异常检测基准？

这不是泛泛的“5G 安全检测”，而是把 HTTP/2 的帧、流、多路复用、窗口和 SETTINGS 行为，与 AMF/SMF/UDR/PCF 的服务调用流程绑定起来分析。

## 4. 创新点深度提炼
- **攻击语境创新**：攻击本身不是新攻击，但论文把 SMA、rapid reset、slow-rate 三组 HTTP/2 攻击放入 5G SBA NF-to-NF 信令中，讨论 NFc/NFp 双向角色、3GPP API、UE 状态和过程依赖。
- **实验环境更接近 5G 控制面**：使用 free5GC docker-compose 3.4.0 和 UERANSIM，Ubuntu 20.04、8 vCPU、64GB RAM，模拟 UE 注册、注销、Uplink、Downlink、PDU session release、UDR Management 等流程。
- **攻击影响分析不是只看目标服务宕机**：论文观察 CPU、NF 间消息量、攻击开始后控制面流程卡点，指出 AMF-SMF 等核心交互会成为放大器。
- **数据集贡献明确**：构造包含正常和 6 类 HTTP/2 攻击的 5G SBA flow-based 数据集，并声称公开发布；这是论文服务后续研究的主要资产。
- **检测基准务实**：没有堆复杂模型，而是用 AE、LSTM-AE、IF 三种无监督模型给出可比较基线，强调 zero-day 和真实标签缺乏场景。

## 5. 科学问题与研究假设
科学问题可以概括为：**HTTP/2 协议层资源消耗型异常，是否会在 5G SBA 的服务化控制面中表现为可观测、可学习、可检测的跨 NF 流量异常？**

主要假设包括：
- 攻击者可通过容器逃逸、虚拟化漏洞、切片隔离失败或配置错误，控制某个 NFc 或 NFp。
- 被攻陷 NF 仍可通过 TLS 认证，并持有或重新获取 OAuth2.0 token，因此看起来像合法 NF。
- 攻击者掌握部分 UE 信息，如 SUPI/IMSI，可触发与 UE 状态相关的服务过程。
- HTTP/2 的 SETTINGS、RST_STREAM、stream multiplexing、flow control 等机制在 5G SBA 中仍可能被滥用。
- 即使不解析明文 payload，流级统计特征也能捕获足够的异常行为。

## 6. 科学方法与技术路线
技术路线是“协议攻击建模 -> 5G 流程嵌入 -> 实验观测 -> 数据集构建 -> 无监督检测”。

攻击建模部分覆盖 6 个变体：
- Attack 1.1：SMA-Request/Response，恶意 SMF 通过 Namf_Communication_N1N2MessageTransfer 对 AMF 发起多请求。
- Attack 1.2：SMA-Subscribe/Notify，恶意 SMF 利用 notify URI 和 DISCONNECTED UE 触发 AMF 反向通知，压垮 AMF/SMF。
- Attack 2：Rapid Reset，恶意 PCF 对 UDR 发送请求后立即 RST_STREAM；实验假设补丁存在，但 UDR 将并发流配置提高到 1000。
- Attack 3.1：Slow Rate-Setting，不确认 SETTINGS，拖住连接资源。
- Attack 3.2：Slow Rate-Connection Preface，发送 HTTP/2 connection preface 后不继续 GET/POST。
- Attack 3.3：Slow Rate-Window Size，将 SETTINGS_INITIAL_WINDOW_SIZE 设为 0 且不发送 WINDOW_UPDATE。

检测方法上，AE 依赖重构误差，IF 依赖高维空间中的异常隔离，LSTM-AE 进一步利用 5G 信令序列的时间依赖。

## 7. 实验设计与实验步骤
可复核流程如下：

1. **数据环境**：搭建 free5GC + UERANSIM，NF 以容器运行；模拟 100 个 UE，两小时正常流量。
2. **正常流量生成**：UE 到达服从 Poisson 过程；10 分钟负载序列为 `[1,2,3,5,6,7,8,9,7,5,3,0.5]`；每个 UE 从注册开始，再按 3GPP 逻辑依赖随机进入后续流程。
3. **攻击注入**：前 60 分钟保持正常，负载接近峰值时启动攻击；攻击利用 30 个合法 UE 的 IMSI；默认 SETTINGS_MAX_CONCURRENT_STREAMS 为 200，rapid reset 场景中设为 1000。
4. **攻击规模**：SMA-Request/Response 使用 55,954 条 HTTP/2 连接、单连接最多 907 请求；SMA-Subscribe/Notify 使用 54,188 条连接、单连接最多 841 请求；rapid reset 约 263,251 条连接、单连接最多 2306 请求/RST；三类 slow-rate 分别约 3,947、5,733、3,815 条连接。
5. **抓包与预处理**：Wireshark 保存 PCAP；CICFlowMeter 生成 84 个 flow-based 特征；归一化后用 VarianceThreshold 保留 54 个高方差特征。
6. **模型/基线**：训练 AE、LSTM-AE、Isolation Forest 三个无监督模型。
7. **训练与测试**：训练集 100,000 行，其中 20% 做验证；每个攻击文件测试时抽取 30,000 条 benign flow 和 10,000 条 attack flow。
8. **指标**：主指标为 F1-score；LSTM-AE 进一步用 ROC-AUC，AUC 范围为 0.87 到 0.97。
9. **消融/敏感性**：论文没有严格做系统消融，但通过 6 类攻击、不同 HTTP/2 机制、不同 NF 组合和不同模型比较，间接展示了攻击类型和时间依赖建模的重要性。
10. **结果核查**：同时检查 NF CPU、NF 间消息量、网络是否宕机、F1/AUC；特别强调慢速攻击中“消息总量低”不等于“风险低”。

## 8. 关键结果、结论与证据
- 正常流量下，各 NF CPU 基本低于 25%，AMF、SMF、UDR 较高，符合它们处理大量控制面请求的角色。
- SMA 类攻击破坏性最强。Attack 1.1 启动约 44 分钟后 AMF 失败；Attack 1.2 会让 AMF 和 SMF 同时承受请求与通知压力。
- Rapid reset 即使在补丁存在时，如果 SETTINGS_MAX_CONCURRENT_STREAMS 配置偏大，也会造成 UDR 和 PCF 高 CPU，论文观察到 UDR/PCF 长时间接近 80%，后续出现 160% CPU 峰值。
- Slow-rate 攻击更隐蔽。Connection Preface 变体的 CPU 行为接近正常流量，说明只看 CPU 或 NF 间消息数会漏掉此类攻击。
- 检测结果中，LSTM-AE 平均 F1 为 92.24%，明显优于 AE 的 83.28% 和 IF 的 84.34%。这支持论文判断：5G SBA 的信令异常具有时序依赖，LSTM-AE 比普通重构模型更合适。

## 9. 局限性与待解决问题
- 实验基于 free5GC/UERANSIM 和单 VM 容器化部署，能反映 5G SBA 逻辑，但与运营商多节点、多厂商、硬件加速、真实切片编排环境仍有差距。
- 攻击者模型较强：假设 NF 已被攻陷、认证授权可用、UE 标识可获得。论文关注“攻陷后如何利用 HTTP/2 放大破坏”，不是解决初始入侵问题。
- 数据集虽然有价值，但攻击流量由实验室脚本生成，真实攻击者可能采用更低速、更混合、更规避的策略。
- 特征主要是 CICFlowMeter 流级特征，HTTP/2 帧级语义、5G API 序列、NF 拓扑图结构还没有充分融合。
- 论文没有完整展开模型结构消融、阈值敏感性、跨部署泛化、跨版本 free5GC 泛化和在线误报成本。
- 正文包未标记截断；但提供的纯文本中部分表格单元格没有完整展开，若要复现实验超参数和逐攻击 F1 明细，仍需回到 PDF 表格核对。

## 10. 与本项目的关系
这篇论文与“恶意流量、暗网与攻击检测、入侵检测与网络异常检测”强相关，尤其适合作为 5G/云原生核心网异常检测方向的支撑文献。它提供了三个可借鉴点：一是从协议机制出发定义攻击，而不是只拿公开 IDS 数据集跑模型；二是把异常放回业务过程依赖中解释；三是用流特征作为可部署检测的第一层基线。

如果本项目面向多源异构安全数据融合，这篇论文可作为“网络流量 + NF 资源 + 5G 控制面流程”的典型案例。后续可以把其 flow-based 特征扩展为时序图：节点是 NF，边是 SBI 调用，边属性是 HTTP/2 流/帧/窗口/重置行为。

## 11. 代码对照分析
本地未发现该论文对应的开源代码包，也未发现以 707、DOI、HTTP/2、free5GC、UERANSIM、5GShield 命名的源码目录。现有 `source` 下包含许多其他项目代码，但没有能直接对应本文实验的目录。

若作者代码存在，按论文方法应至少包含这些模块：
- **测试床编排**：free5GC docker-compose、UERANSIM UE/RAN 配置、NF IP/端口和 SBI 配置。
- **正常流量生成**：Poisson 到达、100 UE、10 分钟负载序列、3GPP procedure 依赖调度。
- **攻击脚本**：SMA 请求生成、Subscribe/Notify notify URI 构造、RST_STREAM 发送、SETTINGS/WINDOW_SIZE/connection preface 操纵。
- **抓包与特征处理**：PCAP 保存、CICFlowMeter 调用、CSV 合并、标签生成、归一化、VarianceThreshold。
- **模型训练评估**：AE、LSTM-AE、IF 的训练、验证、阈值选择、F1/ROC-AUC 计算。
- **影响分析**：容器 CPU 采样、NF 间消息统计、按攻击时间窗口绘图。

## 12. 本篇精华
- 5G SBA 采用 HTTP/2 后，Web 协议层 DoS 不再只是 Web 问题，会变成核心网控制面可用性问题。
- 攻击一个 NF 可能拖垮一条 5G procedure 链路，AMF-SMF、PCF-UDR 等交互会放大单点异常。
- SMA 是破坏性最强的攻击族，slow-rate 是最隐蔽的攻击族，rapid reset 对配置错误高度敏感。
- SETTINGS_MAX_CONCURRENT_STREAMS 是安全和性能之间的关键旋钮，固定值策略不够，需要自适应配置。
- 只统计 NF 间消息量不足以检测慢速 HTTP/2 攻击，因为某些攻击消息少但连接资源占用高。
- CICFlowMeter 流特征可作为 5G HTTP/2 异常检测基线，但未来应引入帧级、时序级和协议语义特征。
- LSTM-AE 的优势来自对 5G 信令时序依赖的建模，平均 F1 92.24%，优于 AE 和 IF。
- 论文最大贡献是“攻击影响实证 + 数据集基准”，不是单纯模型创新。

## 13. 建议精读路线
先读 Section IV，弄清 6 类 HTTP/2 攻击如何映射到 NFc/NFp、UE 状态和 3GPP API。再读 Section V-VI，把正常流程、攻击注入时间、连接规模、CPU 和消息量变化对应起来。随后读 Section VII-VIII，关注 PCAP 到 flow feature、54 个特征选择、AE/LSTM-AE/IF 比较。最后读 Section IX-X，把本文与 5GShield、5Greplay、Web HTTP/2 DoS 研究的差异整理成综述段落。