# [695] HADES: Detecting and Investigating Active Directory Attacks via Whole Network Provenance Analytics

## 1. 基本信息

- 题名：HADES: Detecting and Investigating Active Directory Attacks via Whole Network Provenance Analytics
- 中文题名：HADES：基于全网溯源分析检测与调查 Active Directory 攻击
- 作者：Qi Liu, Kaibin Bao, Wajih Ul Hassan, Veit Hagenmeyer
- 年份：论文在线发表为 2025 年，期刊卷期为 IEEE TDSC, Vol. 23, No. 1, Jan./Feb. 2026
- DOI：10.1109/TDSC.2025.3611866
- 来源：IEEE Transactions on Dependable and Secure Computing
- PDF：`paper/10.1109_TDSC.2025.3611866.pdf`
- 正文包：`综合分析_data/full_text_cache_plain/695.txt`
- 正文完整性：本次正文包未截断
- 代码状态：未发现该论文对应的本地开源代码

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：现代企业中大量攻击已经转向身份驱动，攻击者拿到凭据后围绕 Active Directory 横向移动、权限提升和凭据窃取；传统 IDS 看到的只是零散事件，现有溯源 IDS 又大多只能在单机内部追踪，无法准确回答“攻击者到底从哪台机器到哪台机器、在哪些登录会话里做了什么”。

HADES 的思路不是单纯把 AD 攻击当作分类问题，而是把它拆成两个阶段：

第一阶段只看认证与登录日志，识别 AD 认证流程中的不完整或异常序列。例如 TGT 请求、TGS 请求、成功登录之间的缺失关系，可以对应 AS-REP Roasting、Kerberoasting、Pass-the-Ticket、Golden-Ticket、Pass-the-Hash 等攻击迹象。这个阶段轻量、快，但会产生较多误报。

第二阶段才进入论文真正的贡献：基于登录会话 ID 做全网级溯源。HADES 不把两台机器之间的任意网络连接都视为因果边，也不简单把一次登录视为跨机因果边，而是利用 Windows 的 logon session ID、logon GUID、认证日志、登录日志和系统日志，把攻击行为约束到具体登录会话中，再在会话内做前向和后向追踪。这样可以显著降低依赖爆炸，输出跨主机攻击图，并为每张图计算威胁分数。

一句话概括：HADES 的价值在于把 AD 攻击检测从“发现某个可疑事件”推进到“重建攻击者跨机器、跨会话的因果链条”。

## 3. 论文解决的具体问题

论文解决的是企业 AD 环境中身份驱动攻击的检测与调查问题，重点不是恶意软件本身，而是攻击者利用合法凭据、合法协议和 LOLBins 完成横向移动。

具体问题包括：

1. 传统 IDS 对 AD 攻击不敏感。  
   APT 攻击者常使用 `net`、`netstat`、`setspn`、RDP、SMB、WinRM、WMI、PsExec 等合法工具或系统机制，行为低噪声、低频率，单事件规则很容易漏报或误报。

2. 现有 PIDS 难以跨机器追踪。  
   传统 provenance-based IDS 能把进程、文件、socket 等事件拼成因果图，但多数局限于单机。AD 攻击的关键恰恰是跨主机横向移动。

3. 朴素跨机连接会导致依赖爆炸。  
   如果两台机器有网络连接就连边，会把大量正常业务流量纳入攻击图。如果只根据登录事件连边，也无法区分真实用户和窃取凭据后的攻击者。

4. AD 认证异常本身不足以可靠判定攻击。  
   例如缓存 TGT、网络中断、合法 `runas`、正常 NTLM 访问都可能呈现类似攻击的认证异常。单靠认证日志会带来高误报。

5. SOC 需要可解释调查结果。  
   论文强调检测系统不应只给一个告警，而应输出能支撑响应的攻击图：涉及哪些用户、主机、登录会话、凭据访问、横向移动和权限提升。

## 4. 创新点深度提炼

第一，提出面向 AD 攻击的认证异常模型。  
作者不是简单堆规则，而是从 Kerberos/NTLM 的正常认证流程出发，观察攻击会造成哪些步骤缺失或异常。例如 Kerberoasting 会出现 TGS 请求后没有真实服务访问，Pass-the-Ticket 会缺少对应 TGT 请求，Golden-Ticket 使用伪造 TGT 请求服务票据。这种建模比硬编码 IP、hash 或命令行片段更稳定。

第二，提出 logon session-based execution partitioning。  
这是论文最重要的概念。HADES 把登录会话作为跨机溯源的基本因果单元，而不是进程、主机或网络连接。Windows 中每个成功登录会生成 logon session ID，系统活动会带有该会话上下文。利用这一点，HADES 可以把同一台主机上的多用户、多会话活动切开，避免把正常管理员、普通用户和攻击者行为混在一起。

第三，实现更准确的跨机器因果追踪。  
论文明确区分 correlation-based edge 和 causality-based edge。网络连接或登录事件只是相关性；真正的因果边应连接“发起远程访问的源登录会话”和“被创建的目标登录会话”。这是 HADES 优于 TRACE 类方法的关键。

第四，处理 Windows 登录机制中的复杂细节。  
作者发现不同远程访问方式会产生不同数量的登录事件和会话 ID，且 RDP、PowerShell Remoting、内部 Web 请求等场景会出现系统活动被记录到已有会话或 `System` 会话下的问题。因此设计了远程访问类型推断、会话 ID 重分配、会话链接三个模块。这部分是论文工程含金量最高的地方。

第五，把攻击图排序纳入检测闭环。  
HADES 不只输出图，还根据 AD 攻击的固定模式打分：AD discovery、credential access、lateral movement、privilege escalation。其中凭据访问和横向移动被视为核心证据，访问 `lsass.exe` 的凭据窃取更高危，涉及域管理员或 Golden-Ticket 的图优先级更高。

## 5. 科学问题与研究假设

核心科学问题可以概括为：

在企业 AD 环境中，能否利用登录会话这一系统语义，把跨主机的身份驱动攻击从海量正常认证、登录和系统事件中准确还原出来？

论文隐含了几个关键假设：

1. AD 攻击会造成认证流程异常。  
   攻击者使用窃取票据、hash、服务账号或伪造票据时，认证与登录事件序列会偏离标准 Kerberos/NTLM 流程。

2. 攻击者完成有效入侵通常需要横向移动。  
   HADES 只在第一阶段发现潜在横向移动后才触发全网溯源，因此它默认“只做 AD discovery 或 credential access 但未横向移动”的早期攻击优先级较低。

3. 登录会话能近似表达身份层面的因果边界。  
   一个远程登录会话由源机器上的某个登录会话触发，目标机器上的系统活动应归属于该目标会话。这个假设是 HADES 全网追踪成立的基础。

4. 日志可信。  
   和大多数 PIDS 一样，HADES 假设 OS、固件和日志框架未被攻击者破坏，Sysmon、Windows Security logs、认证日志和登录日志可信。

5. AD 攻击模式相对稳定。  
   论文把 AD 攻击抽象为 discovery、credential access、lateral movement、privilege escalation 的刚性链条，并用这个模式做威胁打分。

## 6. 科学方法与技术路线

HADES 的技术路线是“两阶段检测 + 会话级全网溯源 + 威胁排序”。

第一阶段：认证与登录异常检测。

输入是域控上的认证日志和各主机上的登录日志，重点事件包括：

- Event ID 4768：Kerberos TGT 请求
- Event ID 4769：Kerberos TGS 请求
- Event ID 4624：成功登录
- Event ID 4625：失败登录，主要用于边界判断
- logon GUID：连接认证事件与登录事件的关键字段

HADES 对每个认证或登录事件做前后向关联，检查是否存在标准流程中的缺失步骤，并标记可能攻击类型。

第二阶段：登录会话级溯源。

输入扩展为认证日志、登录日志、Windows Security logs 和 Sysmon logs。核心步骤是：

1. 根据第一阶段告警定位涉及的用户、主机、logon GUID 和 logon session ID。
2. 在访问目标主机上推断远程访问类型，如 RDP、SSH、WinRM、WMI、RPC、PsExec、SMB、内部 Web 请求。
3. 判断是否需要 logon session ID reassignment。
4. 链接同一真实身份触发的多个相关登录会话。
5. 在会话内部做系统级前向和后向溯源。
6. 查找由当前会话发起的进一步远程登录，形成跨机器前向追踪。
7. 查找当前会话来自哪台机器的哪个会话，形成跨机器后向追踪。
8. 输出低层次全网 provenance attack graph。

第三阶段：威胁分数计算。

HADES 统计每条跨机边之前是否出现 AD discovery、credential access、访问 `lsass.exe` 的凭据访问、privilege escalation，并结合攻击类型严重性、是否涉及域管理员账号，计算整张攻击图的威胁分数。

## 7. 实验设计与实验步骤

可复核流程如下。

数据：

- 公共数据集层面，DARPA E3/E5 不适合评估 AD 攻击，OpTC 缺少域控认证日志，因此不能完整运行 HADES。
- 作者基于 MITRE Adversary Emulation Plans 严格实现了三个攻击场景：
  - APT29
  - Oilrig
  - WizardSpider
- 这些数据后来合并发布为 AVIATOR dataset。

预处理：

1. 在域控收集认证日志。
2. 在各 domain-joined host 收集登录日志。
3. 使用 Windows Security logs 和 Sysmon logs 收集系统活动。
4. 通过 Winlogbeat 将日志送入 Elasticsearch。
5. 使用 EQL 查询日志事件。
6. 利用 logon GUID 关联认证事件和登录事件。
7. 利用 logon session ID 给系统活动分区。
8. 丢弃大部分预定义系统会话 ID 下的取证无关活动，但保留与登录创建、远程访问相关的系统活动。

模型与基线：

- HADES Stage 1：认证异常检测模型。
- HADES Stage 2：登录会话级全网溯源与威胁打分。
- 开源规则基线：
  - Elastic detection rules
  - Sigma rules
  - Google Chronicle detection rules
- 商业基线：
  - 一个未具名商业 AD attack detector，论文称为 CAD。

训练：

- HADES 不是传统机器学习模型，没有复杂训练过程。
- 认证异常模型来自 AD 攻击流程分析。
- 威胁打分中的权重是人工设定：discovery、privilege escalation、credential access、涉及 `lsass.exe` 的 credential access 分别有不同指数权重。
- Criticality 也由人工设定，例如 Golden-Ticket 高于 Silver-Ticket，Kerberoasting 高于一般用户凭据攻击。

指标：

- False positives
- False negatives
- 对真实攻击的检测能力
- 攻击图完整性和可解释性
- 响应时间
- Stage 1 到 Stage 2 的误报削减效果

消融与敏感性：

- 论文没有做严格意义上的模型消融，但给出了 Stage 1 与 Stage 2 的对比。
- Stage 1 仅靠认证异常，能捕获攻击但误报多。
- Stage 2 加入会话级溯源和威胁打分后，平均误报降低约 99%。
- 威胁分数阈值使用真实攻击 threat score threshold 展示结果，这一点在复现实验时需要特别核查，避免阈值选择过于依赖已知标签。
- 权重和 Criticality 是主观设定，实际部署需要组织根据资产重要性和风险偏好调参。

结果核查：

1. 检查每个数据集中的真实攻击是否被 Stage 1 捕获。
2. 检查 Stage 2 输出的攻击图是否包含攻击者横向移动链路。
3. 对照 MITRE emulation plan 核查图中的 AD discovery、credential access、lateral movement、privilege escalation 是否完整。
4. 比较 SIEM 规则的误报和漏报。
5. 比较 CAD 是否输出告警及攻击图。
6. 核查响应时间：Stage 1 毫秒级，Stage 2 单个高层告警最多约 45 秒。

## 8. 关键结果、结论与证据

最重要的结果是：HADES 相比开源 SIEM 规则平均减少约 98% 误报；相比自己的 Stage 1，Stage 2 通过会话级溯源和威胁打分平均减少约 99% 误报。

与开源 SIEM 规则相比：

- Sigma 检出率高，但误报多，部分原因是规则库中存在大量重复或相似规则。
- Elastic 误报相对较少，但漏掉 APT29 和 WizardSpider 中的攻击。
- Chronicle 误报低，但在三个数据集上均漏掉真实攻击。
- HADES 同时保持较好检出和低误报，原因是它不是只看孤立事件，而是要求事件在因果图中呈现 AD 攻击链条。

与商业 CAD 相比：

- CAD 没有产生误报，但漏报严重。
- CAD 对 Pass-the-Hash 的检测存在已知问题。
- CAD 不收集足够系统日志，尤其缺少主机内部 credential access 的可见性。
- CAD 输出的攻击图不完整，无法展示攻击者在主机内部执行的恶意系统活动。

案例证据：

- Oilrig / Pass-the-Hash：HADES 能从 Workstation_1 的 C2 活动追踪到 Exchange Server，再到 Data Server，并揭示 AD discovery、credential access、横向移动和访问关键数据的过程。
- APT29 / Golden-Ticket：HADES 能还原从初始主机到 Domain Controller 的凭据访问，再到伪造票据访问 Workstation_2 的链条。
- 响应时间：Stage 1 在每个认证/登录告警上小于 35 ms；Stage 2 对高层告警生成带威胁分数的低层攻击图最多约 45 s。

关键结论是：AD 攻击检测不能停留在认证异常或孤立规则上，必须把身份、登录会话、主机系统活动和跨机因果链统一起来。

## 9. 局限性与待解决问题

本次正文包未截断，因此理解不受正文缺失影响。

论文自身承认的主要局限包括：

1. 可能被会话劫持规避。  
   如果攻击者在一台机器上拥有足够权限，可以劫持已有登录会话。仅靠普通系统日志可能无法建立“劫持会话”和“被劫持会话”的因果连接，导致攻击图提前终止或错误。

2. 依赖日志完整性。  
   如果攻击者能篡改、删除或阻止日志生成，HADES 会失效。这是所有日志驱动检测系统的共性弱点。

3. 尚未在真实生产环境充分部署。  
   论文实验基于 MITRE emulation plans，虽然场景较真实，但仍不是长期生产网络。

4. 隐私问题突出。  
   HADES 结合登录日志和系统活动后，可以揭示员工在何时、哪台机器上做了什么。这对真实企业可能带来合规、信任和滥权风险。作者提出未来需要日志匿名化、数据脱敏、噪声注入等隐私保护机制。

5. 适用范围限定在 AD 和 domain-joined hosts。  
   BYOD、本地账号、非域环境、基于漏洞利用的横向移动不在 HADES 的主要检测范围内。

6. 早期攻击检测能力有限。  
   HADES 是 on-demand PIDS，只有 Stage 1 发现潜在横向移动后才触发 Stage 2。如果攻击者只做 AD discovery 和 credential access，尚未横向移动，HADES 可能不会触发完整调查。

7. 权重设计主观。  
   threat score 中 tactic 权重和 Criticality 值没有通过统计学习或大规模企业数据验证，实际部署需要重新校准。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，但它的价值不在于提出一个复杂图神经网络模型，而在于给出了异常检测系统落地时更关键的东西：异常定义、因果边界和调查输出。

对本项目的启发主要有三点：

第一，异常检测对象应从“单事件异常”转向“因果链异常”。  
AD 攻击中的很多单点行为都是正常的：RDP、SMB、TGS 请求、`net` 命令、访问共享目录。真正异常的是这些行为在同一身份、同一会话、跨主机链路中的组合。

第二，图学习或知识图谱方法需要先解决边的语义。  
如果图中的跨机边只是网络连接，图学习模型会学习大量伪相关。HADES 的 logon session-based tracing 提醒我们：构图质量比模型复杂度更基础。

第三，威胁情报可以作为图排序依据，而不是只作为规则匹配条件。  
论文把 MITRE ATT&CK 中的 tactic/technique 用于攻击图打分，适合与知识图谱、攻击链建模、威胁狩猎结合。

对于“恶意流量、暗网与攻击检测”方向，HADES 的直接覆盖是企业内网身份攻击，不是外部恶意流量分类。但它可作为横向移动检测、内网威胁狩猎、APT 调查和安全运营告警降噪的核心参考。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法逐文件对应论文实现。不过正文给出了比较明确的实现线索。

论文实现原型：

- 语言：Python
- 部署环境：Ubuntu 22.04, 256 GB RAM, 32-core CPU
- 日志来源：Windows Security logs, Sysmon logs, 域控认证日志, 主机登录日志
- 日志管道：Winlogbeat → Elasticsearch
- 查询语言：EQL
- 规则来源：MITRE ATT&CK、Elastic、Sigma、Chronicle

如果复现或补写代码，目录大概率应拆成以下模块：

- 数据接入与解析：负责读取 Elasticsearch 中的 4768、4769、4624、4625、Sysmon、Windows Security 事件。
- 认证异常检测：实现 TGT、TGS、logon GUID、成功登录之间的前后向匹配，对应论文 Stage 1。
- 远程访问类型推断：根据认证、登录和系统事件判断 RDP、SSH、WinRM、WMI、RPC、PsExec、SMB、Web request。
- 会话 ID 重分配：处理 RDP reconnect、PowerShell Remoting、内部 Web 请求中系统活动被记录到旧会话或 `0x3e7` 的情况。
- 会话链接：连接用户会话、系统服务会话、UAC 产生的高低权限会话。
- provenance tracing：在登录会话内做进程、文件、网络、凭据访问的前向/后向追踪，并递归跨主机扩展。
- ATT&CK 技术识别：识别 AD discovery、credential access、访问 `lsass.exe`、privilege escalation。
- 威胁打分：实现论文中的两级分数公式。
- 图输出与可视化：生成类似 Fig. 3、Fig. 10 的攻击图。
- 评估脚本：运行 Elastic/Sigma/Chronicle 规则、统计 TP/FP/FN、响应时间和威胁分数分布。

需要注意的是，论文方法高度依赖 Windows 日志字段语义。若没有作者代码，复现难点不会在 Python 框架，而在日志字段清洗、不同远程访问类型的事件模式、会话重分配规则和跨机 logon GUID 对齐。

## 12. 本篇精华

1. HADES 的核心贡献不是“检测 AD 攻击”，而是提出用登录会话作为全网 provenance tracing 的因果边界。

2. AD 攻击检测的难点在于攻击者使用合法凭据、合法协议和 LOLBins，单事件规则天然容易陷入高误报或高漏报。

3. 认证异常适合作为轻量触发器，但不足以直接判定攻击；真正降低误报的是后续会话级攻击图重建。

4. 跨机溯源不能简单基于网络连接或登录事件连边，否则会产生严重依赖爆炸；必须找到源登录会话到目标登录会话的因果关系。

5. Windows 的 logon session ID、logon GUID、Event ID 4768/4769/4624 是 HADES 的关键数据基础。

6. 论文最有工程价值的部分是远程访问类型推断、会话 ID 重分配和会话链接，因为这些处理了真实 Windows 日志中的复杂性。

7. HADES 用 AD 攻击的固定链条模式给攻击图打分：discovery、credential access、lateral movement、privilege escalation，其中凭据访问和横向移动是核心证据。

8. 这篇论文对图学习类异常检测的提醒很重要：先构造语义正确的因果图，再谈图模型；错误边会让后续模型放大噪声。

## 13. 建议精读路线

建议按以下顺序读：

1. 先读 Introduction 和 Threat Model。  
   把问题边界读清楚：HADES 面向 identity-based lateral movement，不覆盖所有入侵类型。

2. 精读 Fig. 4、Fig. 5 和 Authentication Anomaly Detection。  
   这是理解 Stage 1 的基础，重点看标准 Kerberos 流程如何被不同 AD 攻击打断。

3. 重点精读 Logon Session-Based Execution Partitioning and Tracing。  
   这是论文主贡献。建议对照 Fig. 6、Fig. 7 理解网络连接、登录事件、登录会话三种跨机追踪粒度的差异。

4. 细读 Remote Access Type Inference、Logon Session ID Reassignment、Logon Session Linking。  
   这三节决定方法能否落地，是复现时最容易踩坑的地方。

5. 再读 Threat Score Assignment。  
   注意它不是学习模型，而是基于 AD 攻击链认知设计的排序函数。

6. 最后读 Evaluation 和 Limitations。  
   重点看 HADES 与 SIEM/CAD 的差异、Stage 1 到 Stage 2 的误报下降，以及生产部署中的日志完整性和隐私问题。

<!-- codex-cli-deep-read: complete -->
