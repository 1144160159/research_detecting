# [557] TeRed: Normal Behavior-Based Efficient Provenance Graph Reduction for Large-Scale Attack Forensics

## 1. 基本信息

题名可译为：**TeRed：基于正常行为的大规模攻击取证高效溯源图归约方法**。

- 年份：2025
- 期刊：IEEE Transactions on Information Forensics and Security, Vol. 20
- DOI：10.1109/TIFS.2025.3601381
- 主题：溯源图压缩/归约、APT 检测、攻击取证、正常行为模板、频繁子图挖掘
- 代码：`source\TeRed`
- 相关性判断：对“大规模系统审计日志/溯源图上的异常检测与攻击调查”强相关，不是单纯检测模型论文，而是检测前的数据可用性保障方法。

## 2. 中文翻译与核心摘要

TeRed 的核心思想是：**不要直接猜哪些行为异常，而是先学习正常行为长什么样，只压缩被高置信度匹配为正常行为的图区域**。论文针对系统审计日志生成的超大规模 provenance graph，提出用软件单元测试生成干净、细粒度的正常行为图，再通过 gSpan 挖掘稳定模板；在线或离线归约时，用子图同构匹配找到正常行为区域，并用较小结构替代，同时保留区域外的因果可达性。

它的目标不是最大压缩率，而是“压缩后仍能直接用于攻击检测和取证”。论文强调现有高压缩率方法会误删攻击证据或破坏图结构，例如文中引用 SDPR 可达到 92.45% 归约，但会让 DeepLog precision 从 52.94% 降到 4.88%、recall 从 87.10% 降到 14.29%。TeRed 试图把压缩对象限定为正常行为模板匹配区域，从机制上降低误删异常证据的概率。

## 3. 论文解决的具体问题

论文解决的是 **APT/系统入侵场景下，溯源图太大但又不能粗暴删边删点** 的矛盾。

系统级审计每天每主机可产生 GB 级事件，长期潜伏攻击要求保留较长历史，导致 provenance graph 存储、查询、人工调查和检测模型输入都变得沉重。已有方法的问题在于：

- lossless compression 不丢信息，但使用前往往要解压，不适合直接检测与追踪。
- lossy reduction 能减小数据，但高压缩率常常破坏频率分布、因果依赖或攻击路径。
- 攻击检测依赖异常行为和低频行为，误删攻击边/节点会造成漏报。
- 攻击调查依赖前向/后向追踪，破坏图连通性会截断攻击链或产生错误依赖。

TeRed 把问题重新表述为：**如何在只删除正常行为冗余结构的前提下，保留异常证据与外部因果可达性？**

## 4. 创新点深度提炼

第一，论文把“正常行为模板”引入 provenance graph reduction。它不从待压缩大图中泛化“看似冗余”的结构，而是从可控的正常单元测试中学习行为模式，再到真实大图中匹配。

第二，单元测试被用作正常行为数据源。这个选择很关键：单元测试天然对应单一功能点，攻击污染概率低，且可随软件版本更新持续运行，适合构建可维护的模板库。

第三，模板学习不是直接拿一次执行图当模板，而是多次执行同一测试用例，用频繁子图挖掘去掉 PID、偶发交互、环境噪声等不稳定部分。

第四，归约时使用子图同构，而不是模糊相似度匹配。论文方法要求节点类型、边系统调用等属性一致，意图是避免把攻击子图误判为正常模板。

第五，归约策略关注取证可达性。被匹配区域被替换为模板语义节点/边，外部前驱重连到应用节点，外部后继重连到新节点，以保留区域外前向和后向追踪能力。

第六，论文讨论了可逆归约：模板保存内部结构，额外表保存被删属性和内外连接，可按需局部恢复。Lab 1 中属性恢复表约占原数据 27.71%，依赖恢复表约占 0.56%。

## 5. 科学问题与研究假设

核心科学问题可以概括为三组：

- 正常行为是否能被稳定学习：同一正常功能多次执行后，是否存在能代表该行为的公共 provenance 子图？
- 只归约正常行为是否能保护检测有效性：若只压缩模板匹配区域，是否能避免破坏异常检测所需的攻击证据和频率线索？
- 模板替换是否能保留调查可用性：压缩后，攻击相关实体之间的前驱/后继关系是否仍可通过图追踪得到一致结果？

论文依赖的假设也比较强：

- 模板学习阶段主机没有被攻击者污染。
- 内核级审计完整、准确，日志未被篡改。
- 不考虑硬件攻击、侧信道、隐蔽信道、内核级攻击等审计不可见行为。
- 单元测试库覆盖了足够多的正常行为；覆盖不足时，归约率下降，但不应伤害检测和取证。

## 6. 科学方法与技术路线

TeRed 分为三阶段。

模板学习阶段：执行正常单元测试，每个测试用例多次运行，收集系统事件并构造 provenance graph。图中节点是 process/file/socket/host 等实体，边是 read/write/clone/exec 等事件，带时间戳、事件类型和源/目标实体。

模板挖掘阶段：对同一行为的多次执行图做频繁子图挖掘。论文采用 gSpan 思路，以支持度阈值筛掉偶发噪声，保留跨多次执行稳定出现的公共结构。实验中模板在执行次数增加后趋于稳定，8 次时所有测试行为都能准确提取，最终选择 n=10。

模板匹配阶段：对待归约图和模板库逐一做子图同构匹配。论文使用 VF2，并给应用节点加入应用名属性作为初始匹配约束，减少无效匹配。匹配不仅看拓扑，也要求节点类型和边系统调用一致。

模板归约阶段：把匹配到的正常行为区域替换为更小结构。单模板区域被归约为应用节点、新模板语义节点及其连接边；外部前驱接到应用节点，外部后继接到新节点。论文还讨论了多模板不重叠、同应用重叠、不同应用重叠三种情况。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：使用 DARPA Transparent Computing Engagement 3 的 Trace 和 Theia；另构造三组 Vulhub 场景：CVE-2019-9193 PostgreSQL 任意代码执行、CVE-2016-4971 Wget 重定向任意文件写、CVE-2014-6271 Bash Shellshock。
2. 预处理：采集 sysdig/审计事件，解析为 provenance graph JSON；节点至少含 `id/type`，边至少含 `source/target/ts/syscall`。
3. 模板学习：对 Wget、Bash、Nginx 等程序正常测试用例多次执行；同一行为形成一组图；用 gSpan 挖掘频繁子图模板。
4. 模板验证：用前 n 次执行挖模板，再用额外 5 次执行图验证模板是否都是子图；观察执行次数对模板稳定性的影响。
5. 归约模型与基线：比较 TeRed、CPR、PCAR、FDPR、SDPR、LogApprox、LogGC、NodeMerge。
6. 下游检测：在原图与归约图上运行 Unicorn、ProvDetector、DeepLog，指标采用 F1-score，并调参到较优性能。
7. 攻击调查核查：在 Lab1-Lab3 中选择攻击相关实体集和 POI，对原图与归约图分别做前向/后向追踪，比对 predecessor/successor 划分是否一致。
8. 消融/敏感性：模板库比例从 10% 到 100% 增加，每档随机选择模板 10 次取均值，观察模板数量与归约率关系。
9. 结果核查：重点不是只看 reduction ratio，而是同时看攻击检测 F1 是否下降、攻击实体可达性是否变化、归约是否误删攻击相关信息。

## 8. 关键结果、结论与证据

模板提取方面，论文报告 Wget、Bash、Nginx 的测试用例都能提取出代表行为的模板；执行次数越多，模板越稳定，8 次时全部测试行为准确提取，实际选择 10 次运行。

归约率方面，TeRed 在五个数据集上保持高归约率，整体不低于多数已有方法。SDPR 在五个数据集中的四个归约率最好，TeRed 在 Lab 2 最好；但 SDPR 等高归约率方法会严重损害检测，TeRed 的优势在于压缩率和检测可用性同时成立。

检测方面，TeRed 在五个数据集、三种检测器 Unicorn/ProvDetector/DeepLog 上没有负面影响；部分场景中检测还更好，论文解释为正常可疑路径被压缩后攻击行为更突出。

攻击调查方面，Lab1-Lab3 的前驱/后继追踪结果在归约前后保持一致，说明 TeRed 没有破坏攻击相关实体之间的关键依赖可达性。

可扩展性方面，模板比例越高，归约率越高，说明 TeRed 对软件更新的适配路径是持续扩展测试用例和模板库。

## 9. 局限性与待解决问题

正文包标注未截断，本次理解不受正文截断影响。但提供的纯文本中表格行数据没有完整保留，且论文提到的 Appendix A/B 属于补充材料，正文包未给出攻击复现实操和测试用例明细；精确表格数值仍需回 PDF/补充材料复核。

方法层面的限制包括：

- 依赖完整可信审计日志，真实环境中日志丢失、采集配置错误、内核攻击会削弱模板学习或匹配。
- 单元测试覆盖决定模板库覆盖，覆盖不足时归约率下降。
- 如果攻击行为刻意复用正常程序路径或嵌入正常模板区域，边界处语义细节可能不足。
- VF2 子图同构和 gSpan 在模板库大、图规模大时仍有扩展性压力。
- 论文承认攻击路径穿过归约区域时，路径细节会出现轻微缺口，虽然关键攻击事件仍保留。
- 代码实现与论文方法有差距，不能直接把开源仓库视为论文完整工业级实现。

## 10. 与本项目的关系

如果本项目关注异常检测、恶意流量/攻击检测、威胁溯源或图学习，TeRed 的价值在于提供了一个**检测前的数据减负层**。它不是替代 DeepLog、Unicorn、ProvDetector 这类检测器，而是降低 provenance graph 的存储与分析成本，同时尽量不破坏检测输入。

对你的方向尤其有用的点是：正常行为模板库可以视为一种“主机行为知识库”；模板匹配后的压缩节点保留行为语义，可与攻击图谱、威胁情报实体、ATT&CK 技术标签结合。若项目中有流量侧数据，也可以借鉴其思想：先学习高置信正常交互模式，再只压缩正常模式，避免把罕见攻击行为当冗余删掉。

## 11. 代码对照分析

仓库主入口是 [main.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/main.py:12)，设计上调用 `mine_subgraph()` 学模板，再调用 `reduce_by_template()` 归约。但当前 [main.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/main.py:8) 导入 `DATA_TO_COMPRESS`，而 [settings.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/settings.py:1) 实际定义的是 `DATA_TO_REDUCE`；[reduce_by_template.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/reduce_by_template.py:11) 导入 `COMPRESSED_FOLDER`，但配置文件是 `REDUCED_FOLDER`。因此 README 的 `python main.py` 需要先修正变量名才能直接跑。

模板学习对应 [graph_mining.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/gspan_mining/graph_mining.py:45)。它先由 [data_processing.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/gspan_mining/data_processing.py:43) 把 JSON 图转为 gSpan 输入，节点标签拼接 `pname/path&type`，边标签使用 `syscall`；再用 `-s 5 -d True` 运行 gSpan，见 [graph_mining.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/gspan_mining/graph_mining.py:48)。本地 `test_data/cve-2016-4971-small` 有 10 个正常 JSON，和论文 n=10 的思路相符。

归约对应 [reduce_by_template.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/reduce_by_template.py:43) 和 [graph_match_and_replace.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/graph_match_and_replace.py:15)。源码用 NetworkX `GraphMatcher` 做匹配，见 [graph_match_and_replace.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/graph_match_and_replace.py:67)。但活跃代码没有启用 `node_match/edge_match`，相关属性匹配只在注释中，且使用 `nx.Graph()` 而非有向图；替换也更像把匹配区域折叠为一个 `Compressed_wget_...` 节点，见 [graph_match_and_replace.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/reduction_set/graph_match_and_replace.py:86)，没有完整实现论文的“两节点一边”和重叠区域规则。

数据构图线索在 [sysdig_log2graph.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/collector_set/sysdig_log2graph.py:123)，它解析 clone、read、write、exec/open 等系统调用，并构造 `nx.DiGraph()`，见 [sysdig_log2graph.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/collector_set/sysdig_log2graph.py:638)。

下游检测代码分三块：DeepLog 在 [deeplog/main.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/deeplog/main.py:75) 读取归约结果，[preprocess.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/deeplog/preprocess.py:133) 做 Spell 模板解析，[predict.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/deeplog/predict.py:103) 计算 F1。ProvDetector 在 [provdetector.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/provdetector/provdetector.py:28) 入口，流程是图构建、路径表示、embedding、LOF，见同文件 54、55、75、80 行。Unicorn 适配在 [unicorn/parse.py](F:/泉城实验室/二期/论文/异常检测/source/TeRed/unicorn/parse.py:34)，把 JSON 切成 10% base 和 stream，再由 [preprocess.sh](F:/泉城实验室/二期/论文/异常检测/source/TeRed/unicorn/preprocess.sh:14) 调用二进制生成 sketch。

## 12. 本篇精华

- TeRed 的关键不是“压得最多”，而是把归约对象限定为高置信正常行为，优先保证检测和取证可用。
- 单元测试是本文最有启发的设计：它把正常行为采集从不可控生产日志转移到可重复、可更新、可覆盖的软件测试流程。
- gSpan 负责从多次执行中抽取稳定公共子图，本质上是在 provenance graph 层面消除 PID、偶发 I/O、环境交互噪声。
- VF2 子图同构加属性约束是安全边界；如果实现时不做节点/边属性匹配，会明显偏离论文设计。
- 归约后的图必须保留区域外前驱/后继可达性，否则攻击调查会被截断。
- 实验结论强调 TeRed 是唯一兼顾高归约率和三类检测器 F1 不下降的方法。
- 模板库越大归约率越高，但这也意味着工程上要维护持续测试与模板更新流水线。
- 公开代码能帮助理解流程，但核心归约实现比论文描述简化，复现实验前必须修正配置变量和匹配语义。

## 13. 建议精读路线

1. 先读 Introduction 和 Background，抓住两个约束：不能误删异常、不能破坏因果图结构。
2. 再读 Threat Model，明确 TeRed 不解决日志被篡改、采集缺失、内核级攻击等问题。
3. 重点精读 Design B/C/D：模板学习、模板匹配、模板归约，这是论文真正的方法核心。
4. 读 Evaluation 时不要只看 reduction ratio，要同步看检测 F1 和 tracing 一致性。
5. Discussion 的 reversible reduction 和 scalability 值得单独整理，可作为后续系统设计启发。
6. 最后对照代码读 `reduction_set`，特别注意公开实现与论文算法描述的差距。