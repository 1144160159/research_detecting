# [795] SAGA: Synthetic Audit Log Generation for APT Campaigns

## 1. 基本信息

- 论文：SAGA: Synthetic Audit Log Generation for APT Campaigns
- 作者：Yi-Ting Huang 等
- 来源：IEEE Transactions on Dependable and Secure Computing
- DOI：10.1109/TDSC.2025.3640696
- 年份：在线发表为 2025 年 12 月 5 日，正文卷期版本为 2026 年 3/4 月
- 主题：APT 活动的合成审计日志生成、MITRE ATT&CK 技术标签、主机溯源检测、技术狩猎、APT campaign detection
- 本地代码状态：未发现该论文对应代码包

## 2. 中文翻译与核心摘要

这篇论文提出 SAGA，即面向 APT 活动的合成审计日志生成框架。它要解决的不是一个检测模型本身，而是 APT 检测研究中更基础的数据问题：真实主机审计日志难收集、难共享、难标注，尤其缺少事件级、技术级、阶段级标签，导致机器学习方法难以训练，也难以公平评测。

SAGA 的核心思路是：先用 CALDERA 等红队模拟平台执行 MITRE ATT&CK 技术，采集 Procmon 审计日志；再把具体攻击实例抽象成攻击模式模板，模板中记录攻击阶段、技术编号、前置条件、产物、事件序列和实体描述符；最后将这些模板重新实例化，并与正常用户行为日志混合，生成可配置时长、可配置 APT campaign 数量、可细粒度标注的合成审计日志。

论文的重点贡献在于把“APT 攻击生命周期”与“底层系统审计事件”连接起来：一边保留进程、文件、注册表、网络 socket 等事件级细节，一边给出 MITRE ATT&CK Technique、攻击阶段、ability、威胁组织等高层标签。作者进一步用 AirTag、Unicorn、KAIROS、Sigma rules、SFM 等方法验证这些合成日志可用于入侵检测、技术狩猎和 APT 活动归因。

## 3. 论文解决的具体问题

论文针对的是主机侧 APT 检测研究中的数据瓶颈。

第一，真实 APT 日志稀缺。APT 攻击持续时间长、行为隐蔽，真实企业环境中的审计日志通常涉及隐私和商业数据，难以公开共享。

第二，已有公开数据集标签粒度不足。DARPA TC、OpTC、LANL 等数据集虽然常被使用，但很多只给出攻击时间段或场景级描述，没有把恶意行为精确映射到具体事件、进程、文件或 MITRE ATT&CK 技术。

第三，检测方法之间难以客观比较。事件级方法、图级方法、时间窗口级方法使用不同输入粒度和评价方式，如果没有细粒度标签，很难判断误报、漏报究竟发生在哪些攻击技术或生命周期阶段。

第四，机器学习模型缺少可控训练数据。APT 技术组合、攻击持续时间、多 campaign 并发、正常行为背景噪声都会影响模型表现。真实数据无法任意改变这些变量，而 SAGA 试图提供一个可控实验平台。

## 4. 创新点深度提炼

SAGA 的第一点创新是把红队模拟产生的具体日志转化为可复用攻击模板。论文不是简单录制一次攻击日志，而是把具体文件名、进程名、网络地址等实体抽象为类别和描述符，例如 `File.phishing`、`Process.browser`、`Network.c2`。这样同一个 ATT&CK 技术可以生成多个变体，避免数据只记住一次攻击的表面 artifact。

第二，SAGA 使用前置条件和产物约束来组织 APT 链条。一个技术模板会声明它需要什么资源，以及执行后产生什么资源。例如初始钓鱼附件产生恶意文件，后续用户执行技术再消费这个文件。这使生成日志不只是随机拼接技术，而是有攻击语义和因果连续性。

第三，论文把 APT 生命周期形式化为可生成流程。它用类似上下文无关文法的方式描述 benign audit log、malicious audit log、lifecycle stage、Technique instantiation 的组合关系，使攻击链可以按阶段推进，也可以随机生成或由专家指定。

第四，SAGA 提供事件级细粒度标签。每条恶意事件可标注攻击阶段、Technique、ability、相关实体和操作属性。这比只给“某时间段发生攻击”的数据集更适合训练技术狩猎模型和评估检测器。

第五，论文不只提出生成框架，还用多类下游任务验证可用性：APT 入侵检测、Technique hunting、APT campaign attribution，以及在 DARPA TC E3 Fivedirection 上测试对未见攻击格式的迁移能力。

## 5. 科学问题与研究假设

论文隐含的核心科学问题是：合成审计日志能否在保留攻击语义和系统行为结构的情况下，为 APT 检测模型提供有效训练与评估环境？

它的主要研究假设包括：

1. 红队模拟平台执行的 ATT&CK 技术可以作为真实 APT 行为的近似来源。
2. 将具体攻击日志抽象为模板，再替换 artifact，可以生成多样但仍语义合理的攻击事件。
3. 通过生命周期阶段、前置条件和产物约束，可以合成比随机事件拼接更真实的 APT campaign。
4. 细粒度标签能够支持更复杂的评估任务，例如技术狩猎和 campaign attribution。
5. 用 SAGA 合成数据训练的模型，至少能在部分未见数据集上识别相似攻击技术。

这些假设并非全部被完全证明。论文更多是在经验层面展示“有用性”，而不是严格证明合成日志与真实企业日志具有同分布关系。

## 6. 科学方法与技术路线

SAGA 的技术路线可以概括为四步。

第一步，攻击采集与标注。作者使用 CALDERA 执行 169 个 abilities，这些 ability 对应 MITRE ATT&CK 技术实现。Procmon 采集 Windows 系统审计日志，CALDERA 报告提供 PID、命令和 Technique ID。作者再基于专家规则、前向/后向追踪和代码交叉审查，为相关日志事件打上技术标签。

第二步，攻击模板抽象。具体攻击事件序列被抽象成模板。模板包含攻击身份，即 lifecycle stage 和 Technique；攻击模式，即事件序列和实体描述符；前置条件；执行产物。抽象的关键在于把具体 artifact 替换为类别-描述符结构，例如文件、网络、命令行、进程、注册表、系统实体等。

第三步，APT campaign 生成。SAGA 根据 Mandiant adversary lifecycle 选择攻击阶段：Initial Compromise、Establish Foothold、Internal Reconnaissance、Escalate Privileges、Move Laterally、Maintain Presence、Complete Mission。阶段可以按专家指定生成，也可以随机生成。每个阶段选择满足前置条件的攻击模板，并实例化为具体事件。

第四步，审计日志混合。SAGA 将正常行为日志和恶意 campaign 日志按时间组合。正常行为包括浏览网页、看 YouTube、下载和编译 GitHub 代码、写邮件、运行 Python、玩游戏、阅读新闻、写 Word 文档等。恶意日志可设置持续时间、间隔、插入位置和多个 campaign 并存。

## 7. 实验设计与实验步骤

可复核流程如下。

1. 数据准备：采集正常 Windows 用户行为日志；使用 CALDERA 执行 169 个 ATT&CK abilities，生成恶意审计日志；使用 VX-Underground 和 VirusTotal 收集真实恶意样本 artifact，再用 Faker 生成用户名、PID 等随机实体。

2. 预处理与标注：根据 CALDERA 报告中的 PID、命令和 Technique ID 构建进程家族树；用专家规则筛选真正与攻击有关的事件；为恶意事件标注 7 个攻击阶段、80 个 Techniques、169 个 abilities，并采用 BIO2 标注方案。

3. 模板构建：将具体攻击事件抽象成 attack pattern template，记录 stage、Technique、event sequence、prerequisite、outcome、entity descriptor。

4. 数据集生成：生成三类 campaign：8 个基于威胁情报报告的已知 APT campaign，记为 C 组；20 个随机生成 campaign，记为 G 组；10 个由 3 个 campaign 组合而成的复合场景，记为 M 组。每类再生成 15 分钟、1 小时、1 天三种持续时间。

5. 模型与基线：APT intrusion detection 使用 AirTag、Unicorn、KAIROS；Technique hunting 使用 Sigma rules 和 SFM；APT campaign attribution 使用 SFM 的技术图匹配能力。

6. 训练设置：Technique hunting 训练集包含 16,900 个 attack patterns，按 8:1:1 划分训练、验证、测试。神经网络实验使用 PyTorch 1.13.1、Python 3.10、A100 GPU。

7. 指标：入侵检测、技术狩猎使用 precision、recall、F1、accuracy；campaign attribution 使用 Top-K 排名。

8. 消融与敏感性观察：论文没有传统意义上的严格消融，但比较了技术数量、campaign 复杂度、单/多 campaign、持续时间变化对检测性能的影响。

9. 结果核查：作者观察到 C 组通常比 G 组更容易检测，单 campaign 比复合 campaign 更容易检测，短时日志比长时日志更容易检测。这说明 SAGA 能够通过控制变量制造不同难度的评测场景。

## 8. 关键结果、结论与证据

第一个关键结论是：SAGA 能生成规模较大且可配置的审计日志。15 分钟日志平均约 91 万事件，1 小时约 118 万事件，1 天约 1426 万事件，说明日志规模接近真实主机审计数据的高噪声环境。

第二，现有 APT 检测方法在 SAGA 上表现差异明显。Unicorn 作为图级方法整体表现较好；AirTag 作为事件级异常检测方法在复杂场景下误报和漏报较多；KAIROS 的时间窗口粒度使其召回较高但精度偏低。论文借此强调：评价粒度会显著影响检测结论，事件级标签使不同粒度方法都能被分析。

第三，技术多样性会拉低检测性能。随机生成 G 组包含更多、更广的 Techniques，因此检测结果低于基于情报构造的 C 组。这说明检测器对未覆盖或少见攻击技术仍然脆弱。

第四，多 campaign 复合场景更难。M 组模拟多个 APT 同时作用于同一主机，攻击行为和正常行为交错更复杂，检测性能随之下降。

第五，细粒度 Technique 标签确实能支持技术狩猎。SFM 能从合成数据中学习攻击模式；Sigma rules 依赖人工规则，效率高但覆盖有限，对 T1055.002、T1491 等没有规则覆盖的技术会漏检。

第六，SAGA 训练出的模型对未见数据有一定迁移能力。在 DARPA TC E3 Fivedirection 案例中，SFM 能识别钓鱼附件下载、恶意文件执行等行为，但对 PowerShell 连接 C2 与 payload 下载之间的完整技术边界识别不全。

## 9. 局限性与待解决问题

本次正文包未截断，因此当前理解基于完整提供正文；但论文提到大量补充材料表格，例如 Table S1 到 S9，本次正文只包含其引用和部分主文结果，若要复现实验细节仍需回到 PDF 附件或 supplementary material 核查。

论文最大的局限是合成数据与真实数据之间仍有分布差异。SAGA 的攻击真实性依赖 CALDERA ability 的质量；如果模拟器实现过于规整，模型可能学到模拟器特征，而不是真实攻击本质。

第二，artifact 替换可能造成泄漏。即使使用 VX-Underground、VirusTotal 和 Faker 增强多样性，如果某些文件名、路径、命令模式与标签高度绑定，模型可能依赖浅层 artifact，而不是因果行为结构。

第三，正常行为合成性仍不足。论文列举了多种正常活动，但真实企业主机存在长期软件更新、后台服务、EDR、自定义业务系统、多用户操作等复杂噪声，SAGA 当前主要在 Windows 单主机环境下验证。

第四，SAGA 当前覆盖 80 个 Techniques、169 个 abilities，仍远少于 ATT&CK 全量技术生态。APT 行为快速演化，新技术、新工具链和新规避策略需要持续补充模板。

第五，论文强调“usefulness study”，并未证明 SAGA 数据能替代真实数据。更稳妥的定位是：SAGA 适合做可控评测、预训练、压力测试和标签补充，而不是直接代表真实环境检测效果。

## 10. 与本项目的关系

该论文与“异常检测”项目高度相关，但它不是单纯的恶意流量检测论文，而是主机审计日志与 APT 溯源检测方向。

对本项目有三点启发。第一，如果项目缺少高质量标签，可以考虑“红队模拟 + 模板抽象 + 合成插入”的数据构造路线。第二，异常检测不能只评估二分类效果，还应关注攻击技术、攻击阶段、事件因果链等解释层标签。第三，模型评估需要区分事件级、窗口级、图级粒度，否则不同方法的 precision/recall 不可直接比较。

如果本项目关注网络流量，SAGA 的直接可用性有限；但其思想可迁移到网络侧：把攻击步骤抽象为 TTP 模板，把 IOC、域名、IP、端口、payload 特征参数化，再与正常流量背景混合，生成可控攻击场景。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法进行逐文件源码核对。论文只明确给出公开数据集地址和使用到的外部工具/基线，包括 CALDERA、Procmon、VirusTotal、VX-Underground、Faker、AirTag、Unicorn、KAIROS、Sigma rules、SFM。

如果按论文方法还原代码结构，关键模块大概率应包括：

- 数据采集：负责启动 CALDERA ability、收集 CALDERA report、调用 Procmon 采集 Windows 审计日志。
- 标注模块：根据 PID、进程树、命令行、文件路径、网络连接等规则，将恶意事件映射到 Technique ID。
- 模板抽象：把具体实体替换为 `Category.Descriptor`，生成 attack pattern template，并记录 prerequisite 与 outcome。
- artifact 池构建：从 VirusTotal 行为报告和 Faker 生成候选文件名、路径、用户名、进程 ID、注册表路径等。
- campaign 生成：根据生命周期文法选择阶段和模板，检查前置条件，实例化攻击事件。
- 日志合成：将 benign audit log 和 malicious audit log 按时间轴混合，维护 timestamp、PID、父子进程和共享 artifact 关系。
- 评估适配：把 SAGA 日志转换为 AirTag、Unicorn、KAIROS、Sigma、SFM 所需输入格式，并计算不同粒度指标。

需要注意，论文的代码修改只说“为兼容合成日志结构做了适配”，没有给出修改细节。若后续找到数据集或仓库，应优先核查模板格式、标签 schema、Procmon 字段映射和 baseline 适配脚本。

## 12. 本篇精华

1. SAGA 的核心贡献不是新检测器，而是为 APT 检测提供可配置、细粒度标注的合成审计日志生成框架。

2. 它将 MITRE ATT&CK 技术、APT 生命周期和 Windows 审计事件三层语义打通，使事件级检测和 campaign 级归因可以共用同一数据基础。

3. 攻击模板由具体 CALDERA 执行日志抽象而来，包含 Technique、stage、event sequence、prerequisite、outcome，是生成合理攻击链的关键。

4. SAGA 通过真实恶意 artifact 与 Faker 随机实体替换增强多样性，但仍面临 synthetic artifact leakage 和真实分布差异问题。

5. 实验表明，攻击技术更多、持续时间更长、多 campaign 混合时，现有检测器性能明显下降，说明 SAGA 可用于构造难度可控的压力测试集。

6. Sigma rules 覆盖有限，SFM 能学习合成攻击模式，说明细粒度合成标签对学习型 Technique hunting 有实际价值。

7. 在 DARPA TC E3 未见场景上的案例显示，SAGA 训练模型能识别部分相似攻击技术，但对跨格式、跨事件序列变体仍不稳定。

8. 这篇论文最适合被引用在“APT 检测数据集不足”“合成日志生成”“主机溯源检测评测”三个综述段落中。

## 13. 建议精读路线

建议先读 Introduction 和 Background，抓住作者为什么认为现有 APT 数据集不够用，尤其关注 realism、scenario coverage、detailed labeling、flexibility、diversity 这几个需求。

第二步精读 Section III。重点看 attack pattern template、prerequisite/outcome、context-free grammar 和 Algorithm 2，这是 SAGA 真正的方法核心。

第三步读 Section IV 的实验设计，不要只看表格分数，而要理解不同检测粒度如何影响结果。AirTag、Unicorn、KAIROS 的差异正好体现事件级、图级、窗口级评价不可简单横比。

第四步读 Technique hunting 和 unseen case study。这部分最能说明细粒度标签的意义，也暴露合成数据泛化的边界。

最后读 Discussion，把它作为论文自我约束来理解：SAGA 适合生成可控、带标签、可复现实验场景，但不能被简单等同于真实企业环境。

<!-- codex-cli-deep-read: complete -->
