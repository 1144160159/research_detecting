# [109] KRYSTAL: Knowledge graph-based framework for tactical attack discovery in audit data

## 1. 基本信息
- 论文：KRYSTAL: Knowledge graph-based framework for tactical attack discovery in audit data
- 年份/来源：2022，Computers & Security 121，Article 102828
- DOI：10.1016/j.cose.2022.102828
- 主题：系统审计日志、溯源图、知识图谱、RDF/OWL、SPARQL、攻击图重构、MITRE ATT&CK 映射
- 代码：`source/Krystal`，Java/Maven 原型，入口为 [Main.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/Main.java:26)
- 正文包状态：未截断，本次理解可基于完整正文包完成。

## 2. 中文翻译与核心摘要
题名可译为：**KRYSTAL：面向审计数据中战术级攻击发现的知识图谱框架**。

这篇论文不是提出一个新的异常分数模型，而是解决溯源图攻击检测领域更基础的工程与科学问题：已有方法通常是封闭原型、私有图结构、规则写死在代码里，导致攻击图难复现、难扩展、难与威胁情报联动。KRYSTAL 的核心主张是：把系统审计日志统一提升为 RDF/OWL 知识图谱，用标准本体表达进程、文件、Socket、用户、主机和系统调用关系，再在同一张图上组合标签传播、衰减/恢复、策略告警、Sigma 规则、SPARQL 图查询和 ATT&CK 战术技术映射。

其结果是一个“低层事件证据 -> 溯源攻击片段 -> 高层 TTP 解释”的框架。实验表明，RDF 溯源图虽然比 MORSE 等专用结构慢，但仍可达到约 15.6K 到 37.8K events/s 的处理速度；压缩后 HDT 图很小；攻击图重构通常在秒级以内；Sigma 规则还能补出标签传播漏掉的持久化、压缩打包等行为。

## 3. 论文解决的具体问题
论文瞄准的是**审计日志中复杂攻击链的可解释发现与重构**，具体包括三层困难：

第一，低层溯源图难解释。审计事件能连出进程读写文件、发送网络包、执行程序等因果链，但安全分析员真正需要的是“这是初始访问、执行、防御规避还是数据外传”。没有 ATT&CK、CVE、资产、漏洞和规则上下文，低层图只是大量节点和边。

第二，已有方法难组合。SLEUTH/MORSE 偏标签传播，HOLMES/RapSheet 偏 TTP 或 EDR 规则，POIROT/AIQL/SAQL 偏查询匹配，但它们各自使用自定义数据模型和规则实现，难以复用检测规则、攻击图、威胁知识和实验结果。

第三，攻击发现需要同时兼顾鲁棒性和可扩展性。单一检测机制容易漏报或误报；论文假设更好的方向是统一底座上组合多种技术，而不是再做一个封闭的专用检测器。

## 4. 创新点深度提炼
1. **把系统级溯源图标准化为 RDF/OWL 知识图谱**：KRYSTAL 本体把 Process、File、Socket、User、Host、Executable、IPAddress 及 `writes`、`isReadBy`、`sends`、`isExecutedBy` 等关系显式建模，避免每篇论文一个私有图结构。

2. **用语义推理补全图结构**：通过 `rdfs:domain/range`、`rdfs:subPropertyOf`、`owl:inverseOf`，可自动推断节点类型、通用溯源边 `provRel` 和反向关系，使后续 SPARQL 查询不必硬编码所有底层事件变体。

3. **检测机制模块化**：同一张知识图谱上可以跑标签传播、衰减/恢复、策略告警、Sigma 签名、SPARQL 图查询。论文的价值不在某个单点检测算法，而在把这些机制放入一个可组合框架。

4. **攻击图重构与 TTP 映射一体化**：Backward-forward chaining 先反向寻找可能根因，再正向构造攻击链；同时通过 ATT&CK-KG/SEPSES CSKG 把告警映射到技术和战术，提升解释层次。

5. **RDF 图压缩和查询可行性验证**：用 HDT 压缩 RDF 溯源图，证明标准语义图不是只能做小规模演示，在 DARPA TC 多平台数据上仍能承载攻击重构。

## 5. 科学问题与研究假设
核心科学问题是：**标准知识图谱表示能否在不显著牺牲性能的前提下，支撑多源审计日志中的攻击发现、攻击链重构和高层战术解释？**

论文隐含了几条研究假设：

- 统一 RDF/OWL 数据模型能降低检测技术之间的耦合，使不同检测方法可在同一图上组合。
- 多种检测机制互补会比单一机制更鲁棒，尤其是标签传播与 Sigma/图查询结合后能覆盖更多攻击步骤。
- 语义推理和 SPARQL property path 足以表达溯源分析中的因果追踪与攻击图重构。
- 外部威胁知识链接能把低层审计证据提升为可读的 ATT&CK 技术/战术链。
- 标准图模型的性能损失可以通过事件过滤、重复三元组合并、HDT 压缩和阈值过滤控制在可接受范围内。

## 6. 科学方法与技术路线
KRYSTAL 的技术路线是三段式。

第一段是**溯源图构建**：从 Linux auditd、FreeBSD DTrace、Windows ETW 等审计日志中解析出进程、文件、Socket、主机、用户及其交互关系，映射为 RDF 三元组。代码中对应 [JsonRDFReader.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/JsonRDFReader.java:35) 的逐行读取与多平台 parser 分派，以及 [LogMapper.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/parser/LogMapper.java:71) 的 RDF 关系拼装。

第二段是**威胁检测与告警**：标签传播维护完整性、机密性、主体标签；衰减与恢复控制长链传播导致的依赖爆炸；策略规则识别文件执行、权限改变、文件破坏、数据泄露、侦察等事件；Sigma 规则用于补充基于 IoC/行为签名的检测。

第三段是**攻击图与场景重构**：反向从告警沿 `provRel` 找根因并加权，正向沿低完整性节点构造攻击子图；图查询用于匹配已知攻击模式；SPARQL federation 用于链接 ATT&CK 技术、战术和其他背景知识。

## 7. 实验设计与实验步骤
1. **数据**：使用 DARPA Transparent Computing 第三阶段数据，覆盖 Cadets、Theia、FiveDirections 三类平台场景，包括 FreeBSD Nginx backdoor、Ubuntu Firefox backdoor、Windows Firefox backdoor。总量超过 53GB JSON 审计日志、约 7 天行为。

2. **预处理**：按事件类型过滤审计日志，抽取 subject、object、路径、IP/端口、时间戳、主机、用户等字段；构造 Process/File/Socket 等 RDF 节点；对机密目录如 `/etc/passwd`、`/etc/shadow`、`/documents/` 初始化低机密性/低完整性标签；用 OWL/RDFS 推理补全类型和通用 `provRel`。

3. **模型/基线**：KRYSTAL 不是训练式模型，而是框架性方法。对照对象主要是 SLEUTH/MORSE 的标签传播思想、HOLMES/RapSheet 的战术级分析、POIROT/AIQL/SAQL 的图查询路线，以及 MORSE 的吞吐性能。

4. **训练**：无机器学习训练过程。实验变量主要是规则、标签阈值和传播参数，例如完整性/机密性低于 0.5 视为可疑，`ab=0.2`、`ae=0.1` 控制 attenuation，`period=0.25`、`tb=0.75`、`te=0.45` 控制 decay。

5. **指标**：图规模压缩率、构图与告警吞吐、forward chaining 时间、graph querying 时间、传播式告警数量、Sigma 告警正确/错误数量、是否覆盖 ground truth 攻击步骤。

6. **消融/敏感性**：论文没有系统做参数敏感性曲线，但比较了传播式告警与 Sigma 告警的互补性；讨论了 attenuation/decay 对依赖爆炸的控制；也比较了 KRYSTAL 与 MORSE 在吞吐上的差距。

7. **结果核查**：通过 DARPA ground truth 与五个攻击场景图核查攻击链是否被重构；表 4-7 分别给出 RDF/HDT 图大小、运行时间、传播式告警和 Sigma 告警数量。

## 8. 关键结果、结论与证据
图压缩效果明显：Theia 18.7GB JSON 变为 280MB RDF、16MB HDT；Cadets 两组 19GB JSON 变为约 400MB RDF、17MB HDT；FiveDirections 16GB JSON 变为 25MB RDF、0.9MB HDT。这说明审计日志转成语义溯源图后，经过事件选择和重复合并，规模是可控的。

处理性能可用但不是最快：KRYSTAL 构图与告警约 15.6K 到 37.8K events/s，低于 MORSE 的约 100K events/s。论文的解释是 RDF lifting、Jena 推理、SPARQL 查询带来开销，但换来了互操作性、规则复用和背景知识链接。

攻击图重构很快：forward chaining 约 0.79 到 1.99 秒，graph querying 均低于 0.5 秒。作者认为在这些攻击场景里 property path 没有触发理论上的严重复杂度问题，因为路径较短，且低完整性过滤缩小了搜索空间。

检测互补性成立：传播式策略覆盖了 ground truth 中的高层攻击活动；Sigma 规则在 Linux/FreeBSD 场景中没有错误告警，并发现了 bash_profile 修改、数据压缩等传播式方法漏掉的行为。Windows 场景中 Sigma 触发 1162 个正确告警，但也有 261 个无法关联真实攻击的错误告警，说明规则质量和平台噪声仍是问题。

## 9. 局限性与待解决问题
1. **在线重构尚未真正验证**：论文说构图接近在线，但攻击图重构主要按离线/取证场景评估。真实流式环境还要解决窗口、延迟、时间同步、多条攻击链并行维护等问题。

2. **仍依赖预定义规则和先验目录**：低标签初始化、敏感目录、Sigma 规则、图查询模式都需要人工知识。未知攻击可通过标签传播部分缓解，但不是纯异常检测。

3. **SPARQL 门槛和性能风险**：SPARQL 表达力强，但安全分析员未必熟悉；property path 在复杂大图上有潜在指数级风险，论文实验中的路径较短不能完全代表生产环境。

4. **评估场景有限**：DARPA TC 是经典数据集，但仍是红蓝对抗构造场景；多租户生产主机、云原生环境、容器、横向移动、多主机联动没有充分验证。

5. **源码与论文描述存在落差**：论文强调 RML 声明式映射，但代码包中我看到的是 Java parser 与 `LogMapper` 直接拼 RDF；Sigma 也主要以已翻译的 TTL 规则加载，未看到完整 YAML-to-SPARQL 转换器。复现实验时需要注意这可能是论文原型的简化发布版本。

6. **配置和平台命名有不一致处**：论文称 Cadets 是 FreeBSD、Theia 是 Ubuntu；代码配置注释和 parser 命名中 `ubuntu14`、`freebsd` 的对应关系较混乱，README 示例用 Cadets 却启动 `ubuntu14` parser，需要结合样例数据实际核对。

## 10. 与本项目的关系
对“异常检测”项目而言，KRYSTAL 的相关性是**中等偏有用**，更适合作为异常检测系统的解释与上下文层，而不是直接替代统计/深度异常检测模型。

它能提供三类价值：第一，把主机审计日志变成可查询的溯源知识图谱，为图学习或 GNN 提供结构化输入；第二，把低层异常告警映射到攻击链和 ATT&CK TTP，增强可解释性；第三，可把恶意流量、暗网情报、IoC、CVE/CWE/CAPEC 等作为外部知识接入图中，支持跨源关联。

但它不是网络流量分类器，也不是面向暗网文本或流量特征的异常检测算法。若本项目关注恶意流量/暗网攻击检测，KRYSTAL 更适合做“主机行为证据 + 网络连接实体 + 威胁情报”的关联框架。

## 11. 代码对照分析
代码结构与论文三段架构基本对应：

- 配置与入口：[config.yaml](F:/泉城实验室/二期/论文/异常检测/source/Krystal/config.yaml:3) 定义输入目录、GraphDB endpoint、ontology、标签传播、attenuation/decay、Sigma 规则目录和敏感目录；[Main.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/Main.java:26) 读取配置并调用 `JsonRDFReader.readJson`。
- 数据预处理/构图：[JsonRDFReader.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/JsonRDFReader.java:35) 逐行读 JSON，按 `os-platform` 分派到 [LogParserFreeBSD.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/parser/LogParserFreeBSD.java:42)、[LogParserUbuntu12.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/parser/LogParserUbuntu12.java:49)、[LogParserUbuntu14.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/parser/LogParserUbuntu14.java:43)、[LogParserWin.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/parser/LogParserWin.java:45)。
- RDF 映射：[LogMapper.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/parser/LogMapper.java:71) 负责 `writeMap/readMap/executeMap/sendMap/receiveMap`，并初始化进程、文件、网络标签。
- 本体与推理：[log-ontology.ttl](F:/泉城实验室/二期/论文/异常检测/source/Krystal/experiment/ontology/log-ontology.ttl:47) 定义 `provRel` 及各类系统调用关系；[JsonRDFReader.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/JsonRDFReader.java:167) 使用 Jena OWL Micro Reasoner 生成 `InfModel`。
- 标签传播：[PropagationRule.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/PropagationRule.java:48) 实现 read/write/receive/send/exec/fork 标签传播；attenuation 在同文件约 377 行和 419 行；decay 在约 708 行。
- 策略告警：[AlertRule.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/AlertRule.java:71) 包含 reconnaissance、exec、data leak、corrupt file、change permission 等 SPARQL CONSTRUCT 告警逻辑。
- Sigma 规则：[AlertRule.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/AlertRule.java:265) 从 `experiment/rule` 和 `experiment/rule_win` 读取已翻译的规则 TTL，执行其中 `sigma:hasDetection` 查询。
- 攻击重构：[AttackConstruction.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/AttackConstruction.java:34) 做告警加权和根因查找；[forwardAnalysis.sparql](F:/泉城实验室/二期/论文/异常检测/source/Krystal/experiment/query/forwardAnalysis.sparql:1) 给出前向构图与 ATT&CK 链接查询示例。
- 存储与压缩：[Utility.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/helper/Utility.java:56) 支持 HDT 生成，[GraphDBStorage.java](F:/泉城实验室/二期/论文/异常检测/source/Krystal/src/main/java/sepses/krystal/helper/GraphDBStorage.java:22) 通过 `curl` 写入 GraphDB。

## 12. 本篇精华
- KRYSTAL 的真正贡献是“统一语义底座”，不是单个新检测算法。
- RDF/OWL 让溯源图、告警规则、ATT&CK 技术战术和外部 CTI 可以在同一查询体系里联动。
- 标签传播擅长未知因果扩散，Sigma 擅长已知行为签名，二者组合确实补强检测覆盖。
- `provRel` 是攻击重构的关键抽象：具体读写执行关系被提升为统一可遍历的因果边。
- HDT 结果说明大规模审计日志转 RDF 后并非不可用，压缩图可小两个数量级以上。
- 性能代价真实存在：KRYSTAL 比 MORSE 慢，但换来可复用、可解释、可扩展。
- 论文对“异常检测 + 知识图谱 + 威胁情报”的结合很有启发，但对在线、多主机、参数敏感性和生产误报仍验证不足。

## 13. 建议精读路线
1. 先读 Introduction 的 motivating example，抓住 `/tmp/XIM`、`/etc/passwd`、外联 HTTP 这一条低层攻击链如何需要高层解释。
2. 再读 Requirements，重点看 R1-R4：上下文化、复用扩展、威胁情报链接、跨平台互操作。
3. 精读 Section 5 的 ontology 和 inference，这是理解 `provRel`、类型推理、反向关系的基础。
4. 精读 Section 6 的 tag propagation、Sigma、backward-forward chaining、SPARQL federation。
5. 对照 Tables 4-7 看实验是否支撑作者主张，尤其注意性能低于 MORSE 但攻击重构较快。
6. 最后读 Discussion，重点看作者承认的在线重构、未知攻击、SPARQL 门槛和分布式扩展问题。
7. 若要跑代码，建议按 `config.yaml -> Main -> JsonRDFReader -> LogParser/LogMapper -> PropagationRule/AlertRule -> AttackConstruction/forwardAnalysis.sparql` 的顺序读源码。

<!-- codex-cli-deep-read: complete -->
