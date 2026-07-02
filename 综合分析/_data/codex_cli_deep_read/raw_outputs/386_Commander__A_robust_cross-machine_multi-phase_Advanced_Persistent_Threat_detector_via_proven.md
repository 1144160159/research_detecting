# [386] Commander: A robust cross-machine multi-phase Advanced Persistent Threat detector via provenance analytics

## 1. 基本信息

- 题名：Commander: A robust cross-machine multi-phase Advanced Persistent Threat detector via provenance analytics
- 作者：Qi Liu, Kaibin Bao, Veit Hagenmeyer
- 年份/来源：2025，Journal of Information Security and Applications
- DOI：10.1016/j.jisa.2025.104057
- 主题关键词：APT 检测、数据溯源分析、数字取证、Active Directory、工业组织安全
- 方法定位：启发式 provenance-based IDS，不是典型 GNN 图学习论文。它使用图作为因果追踪和攻击重构载体，核心贡献在跨机器、跨阶段、跨 IT/OT 域的溯源链路恢复。

## 2. 中文翻译与核心摘要

这篇论文提出 Commander，一个面向工业组织的跨机器、多阶段 APT 检测系统。它的出发点是：传统 IDS 和多数 PIDS 只能在单机、短链条或简化 APT 场景中工作，而真实 APT 常通过持久化、横向移动、会话劫持、端口转发等方式把攻击链拆散，导致溯源图断裂或依赖爆炸。

Commander 的核心思路不是单纯提高规则数量，而是把“身份驱动攻击”的认证异常作为入口，再结合持久化检测、会话劫持检测、端口转发检测，修正跨会话与跨机器追踪中的断点。之后它用 logon session ID 把同一身份在多台机器上的活动串起来，最终生成按威胁分数排序的攻击图。

论文的重点场景是工业组织：企业 IT 域与 OT/ICS 域通过网关相连，攻击者从 IT 域进入后，经网关抵达工程站和现场控制器。作者还为 Siemens SIPROTEC 和 Hitachi Energy RTU500 控制器开发了解析器与 ICS TTP 规则，使 Commander 能把工业控制器上的操作归因到企业侧真实攻击身份。

## 3. 论文解决的具体问题

论文要解决的问题很具体：现有 PIDS 难以检测“跨机器 + 多阶段 + 工业域”的真实 APT。

第一，持久化会把攻击链拆成 setup 和 execution 两段，常常位于不同 logon session 中。没有持久化语义的 PIDS 会把两段看成无关图，导致攻击链断裂。

第二，横向移动导致跨机器追踪。若只按网络连接连图，会产生严重依赖爆炸；若按登录事件连图，又容易被身份盗用、端口转发误导。

第三，Hades 已经解决了一部分跨机器追踪问题，但仍会被三类常见技术绕过：持久化、会话劫持、端口转发。Commander 可以看作对 Hades 的鲁棒化扩展。

第四，工业组织中还存在跨 IT/OT 域和现场控制器归因问题。控制器日志粒度粗，且没有通用 OS 的 logon session 概念，普通主机溯源方法不能直接套用。

## 4. 创新点深度提炼

1. 把跨机器 APT 检测推进到“跨机器 + 多阶段”。此前 Cpd 解决持久化导致的多阶段问题，Hades 解决 AD 环境跨机器问题，Commander 将二者合并，并补上会话劫持与端口转发两类绕过场景。

2. 提出面向 Hades 的逃逸分析。论文不是泛泛说“攻击者会规避检测”，而是明确指出三种会破坏 logon session-based tracing 的技术：persistence 造成跨 session 断链，session hijacking 造成劫持 session 与被劫持 session 无法归并，port forwarding 造成源 IP 被代理机替换。

3. 三阶段架构较清晰：预检测、全网追踪、攻击图排序。预检测模块提供“修补追踪”的先验关系，第二阶段利用这些关系恢复完整攻击链，第三阶段用 TTP 丰富度、跨域、ICS 行为等进行威胁评分。

4. 将工业控制器纳入 provenance 追踪。论文没有把 ICS 只当成普通资产，而是承认控制器日志模型不同，并用“工程站 logon session 到控制器命令”的归因方式连接 IT/OT 攻击链。

5. 实验数据选择有针对性。AVIATOR-Oilrig 和 AVIATOR-Sandworm 是基于 MITRE emulation plan 扩展到 ICS 的数据集，能覆盖传统 DARPA 数据集中缺失的持久化、横向移动、工业控制器攻击步骤。

## 5. 科学问题与研究假设

核心科学问题是：在攻击者使用身份盗用、持久化、会话劫持和端口转发的情况下，能否仍然用系统日志和认证日志恢复同一攻击者跨机器、跨阶段的因果链？

论文隐含了几条关键假设：

- OS、固件和日志框架完整性可信。攻击者没有成功篡改关键日志。
- Windows/AD 环境中的 logon session ID 足以作为划分用户活动、权限上下文和横向移动链条的重要锚点。
- 真实 APT 在初始访问后通常呈现稳定模式：AD discovery、credential access、lateral movement、privilege escalation，并可能扩展到 persistence、session hijacking、port forwarding、ICS TTP。
- 攻击图中 TTP 的多样性、频次和跨域/跨现场资产行为可以作为威胁评分依据。
- 工业控制器虽然日志粒度粗，但若能定位来自工程站的登录/命令窗口，仍可把控制器行为归因到上游攻击身份。

## 6. 科学方法与技术路线

Commander 的技术路线可以概括为“先找身份异常，再修补跨 session 断点，最后重构并排序攻击图”。

第一阶段是预检测，四个模块并行运行：

- 认证异常检测：基于 Hades，检查 AD 认证与登录事件，发现 Pass-the-Hash、Golden-Ticket 等身份驱动异常。
- 持久化检测：集成 Cpd，识别 persistence setup 与 persistence execution，并输出成对 logon session。
- 会话劫持检测：寻找几乎同时发生的被劫持用户 logon 与劫持用户 logoff，再检查劫持方 session 是否存在提权到高完整性/系统权限。
- 端口转发检测：识别 plink、ssh、netsh 等端口转发进程和命令行参数，再把代理机上的转发端口与目标机登录事件关联，恢复真实源 session 与目标 session。

第二阶段是全网追踪。Commander 从认证异常中的主机、用户、session ID 出发，判断远程访问类型，必要时进行 session ID reassignment 和 session linking。随后做单机内前向/后向追踪，并在每一步检查是否命中持久化、会话劫持、端口转发 session pair。跨机器时依赖认证/登录事件，跨 IT/OT 域时检查网关服务器，进入工程站后再追踪到现场控制器。

第三阶段是攻击图评分。Commander 将图中事件匹配 AD TTP 规则和 ICS TTP 规则，根据每条横向移动边周围的技术频次、战术多样性、域管凭据、攻击类型关键性、跨域、端口转发、ICS 控制器行为等累计威胁分数。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：选用 AVIATOR 的两个 ICS 扩展子集。AVIATOR-Oilrig 包含 10 台目标主机，真实攻击为 Pass-the-Hash，数据 566 GB、约 3.6 亿事件；AVIATOR-Sandworm 包含 8 台目标主机，真实攻击为 Golden-Ticket，数据 610 GB、约 4.79 亿事件。

2. 预处理：收集 Windows Security、Sysmon、Linux Auditd、域控认证日志、各主机登录日志，以及 Siemens SIPROTEC / Hitachi Energy RTU500 控制器日志。日志进入 Elasticsearch，Commander 用 EQL 查询相关事件。

3. 模型/基线：Commander 与 Elastic detection rules、Sigma rules、Google Chronicle rules、一个匿名商业 AD 攻击检测器 Cad 对比。论文也讨论 Hades、Cpd、KAIROS、FLASH 等 PIDS，但直接实验对比受限于代码和数据差异。

4. 训练：Commander 不是学习型模型，无训练过程；其检测依赖规则、启发式和 logon session-based tracing。

5. 指标：统计 FP、FN，并合并两个数据集计算 precision、recall、F1。还测量每个攻击图从触发到输出威胁分数的响应时间。

6. 消融/敏感性：论文没有做标准机器学习式消融，但通过 Hades 的三类逃逸案例说明：若缺少持久化、会话劫持、端口转发检测，追踪会提前终止或错误归因。威胁阈值敏感性通过 CDF 展示：阈值下降会保留 TP，但 FP 上升。

7. 结果核查：检查 Commander 生成的攻击图是否覆盖 Oilrig 和 Sandworm 扩展计划中的关键横向移动、持久化、网关、工程站、现场控制器步骤，并与 Cad 的粗粒度图进行质量对比。

## 8. 关键结果、结论与证据

检测准确性上，Commander 在两个数据集上 FP=0、FN=0。合并结果 precision=1.0，recall=1.0，F1=1.0。对比来看，Elastic、Chronicle、Sigma 的误报较多或漏报明显；Cad precision 高但漏掉 Oilrig 的 Pass-the-Hash，recall 为 0.667。

威胁评分上，两个真实攻击图都获得最高分。论文强调 Commander 的目标不是让规则永远无误报，而是把最值得调查的图排在最前面。若阈值设为最高真实攻击分数，两个数据集 FP 均为 0；若阈值降低 50%，Oilrig FP rate 为 1.9%，Sandworm 为 3.4%。

响应时间上，瓶颈主要来自第一阶段的持久化检测。Oilrig 上完整输出每个攻击图约 103-128 秒，Sandworm 上约 586-627 秒。第二、三阶段本身较快：Oilrig 多数图额外耗时低于 18 秒，Sandworm 多数低于 20 秒。

攻击图质量上，Commander 能重构 Oilrig 中从 Workstation_1 到 Exchange Server、Data Server、Gateway Server、Engineering Workstation、Siemens 控制器的链路，并识别持久化、会话劫持、端口转发等连接断点。Sandworm 中也能从 OT 域 Golden-Ticket 异常回溯到 Gateway Server、Workstation_1，并继续追踪到工程站和 Hitachi RTU500 控制器。

## 9. 局限性与待解决问题

论文承认 Sandworm 攻击图并不完全。攻击者在 IT 域有三个初始访问点，但 Commander 只能从 OT 域异常回溯到 Workstation_1，无法把 Workstation_2、IT Domain Controller、Linux Server 上的攻击活动全部归并，因为数据中没有攻击者机器日志，无法从外部源头因果连接多个初始访问。

Linux 侧也是短板。Linux 有 logon session 概念，但 Auditd、CamFlow 等常用工具不会把 logon session ID 写入系统事件，导致 Commander 暂时无法在 Linux 上做与 Windows 同等粒度的 session-based tracing。

系统强依赖日志完整性。如果攻击者能删除、篡改或绕过关键日志，Commander 会失效。论文提到 Windows Protected Event Logging、Sysmon protected process、Auditd immutable configuration 等防护，但这仍是依赖前提。

部署代价也不低。详细系统日志会带来存储、查询、隐私和计算资源问题。实时部署时，Elasticsearch 查询频率、图更新频率和 SOC 资源之间需要权衡。

本次正文包信息显示未截断，因此不需要因正文缺失额外保留结论；但仍建议回到 PDF 核对图 7、图 12、图 13 的细节，因为攻击图中的节点文字在纯文本中无法完整呈现。

## 10. 与本项目的关系

若本项目关注“异常检测、图学习、知识图谱与威胁情报”，这篇论文的相关性在于：它不是把图学习作为主算法，而是展示了安全语义驱动的 provenance graph 如何服务 APT 检测和取证。

对综述写作有三点价值：

- 可作为“规则/启发式 PIDS 在复杂 APT 中仍有优势”的代表，与 KAIROS、FLASH 等 GNN PIDS 对比。
- 可作为“图学习方法的不足案例”：若模型不能理解持久化的 setup/execution 双阶段语义，仅靠图表示学习可能难以泛化。
- 可作为“工业 APT 检测”的桥接文献：从企业 AD 攻击链延伸到 OT 网关、工程站、现场控制器，适合放在 IT/OT 跨域威胁检测章节。

## 11. 代码对照分析

元数据说明未发现该论文对应的本地开源代码，因此不能给出真实代码目录、源码文件名或运行命令。下面只能依据论文 Implementation 部分给出实现线索级对照。

可能的数据预处理对应模块：

- 日志接入：Winlogbeat、Auditbeat 将 Windows Security、Sysmon、Auditd 日志送入 Elasticsearch。
- 控制器解析：应有 Siemens SIPROTEC 和 Hitachi Energy RTU500 日志 parser。
- 查询层：通过 Elasticsearch EQL 检索认证、登录、进程、文件、注册表、网络连接等事件。

可能的检测模块：

- `authentication anomaly detector`：处理 AD 认证与登录事件，输出异常类型、涉及主机、用户、session ID。
- `cyber persistence detector`：对应 Cpd，包含 persistence setup rules、execution rules、alignment、false positive reduction。
- `session hijacking detector`：处理 logon/logoff 事件与提权证据，输出 hijacking/hijacked session pair。
- `port forwarding detector`：解析 plink/ssh/netsh 等进程命令行、端口开放、代理登录事件，输出 source/destination session pair。

可能的图与评分模块：

- 图构建：论文明确使用 Python NetworkX 按需创建 provenance graph。
- 可视化：使用 PyVis 输出交互图。
- 追踪：实现 backward/forward tracing、session reassignment、session linking、cross-domain tracing、cross-field tracing。
- 评分：实现 `CalculateScore` 与 `SumScore`，依据 AD TTP、ICS TTP、跨域、端口转发、域管凭据、控制器行为累计分数。

## 12. 本篇精华

- Commander 的关键不在“更多规则”，而在用专门检测器修补 provenance tracing 中会被 APT 技术打断的因果边。
- 论文把 Hades 的弱点讲得很清楚：持久化、会话劫持、端口转发都会让 logon session-based cross-machine tracing 断链或错链。
- 持久化被建模为 setup/execution 双阶段，这是理解多阶段 APT 图断裂问题的核心。
- logon session ID 是全篇最关键的工程锚点：它既分隔不同身份活动，也帮助识别权限提升和远程访问上下文。
- Commander 对工业场景的贡献在于跨 IT/OT 域追踪，以及把工程站 session 与现场控制器 TTP 操作关联起来。
- 评估显示真实攻击图威胁分数显著高于良性图，说明“完整因果链 + TTP 密度”比单点告警更适合 SOC 排序。
- 该系统的最大现实风险是日志完整性、日志成本和 Linux session 信息缺失。
- 对图学习研究的启示是：APT 检测不能只依赖结构异常，必须把攻击技术语义和身份上下文编码进图构建过程。

## 13. 建议精读路线

1. 先读 Introduction 和 Threat Model，明确论文不解决初始访问检测，也不处理日志被篡改后的场景。

2. 精读 Section 4 的三个 motivating examples。这部分是理解 Commander 必要性的核心，尤其要画出 persistence、session hijacking、port forwarding 如何让 Hades 断链。

3. 再读 Algorithm 1-3。重点看四个预检测器如何把“潜在断边”变成 session pair，供第二阶段追踪使用。

4. 读 Section 6.2 的 Oilrig 攻击图解释。它是全篇最好的系统运行样例，能看出 IT 域、网关、OT 域、工程站、控制器如何串联。

5. 读 Section 8 的实验表格和响应时间。注意 Commander 的高准确率建立在 AVIATOR 两个扩展场景上，样本规模不是大量攻击类型泛化测试。

6. 最后读 Limitations。尤其关注多初始访问无法归并、Linux session ID 缺失、日志完整性与实时部署成本，这些都是后续研究可以切入的真实问题。