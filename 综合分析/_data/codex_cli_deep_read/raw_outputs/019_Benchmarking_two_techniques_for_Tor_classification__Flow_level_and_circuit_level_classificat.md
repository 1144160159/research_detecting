# [019] Benchmarking two techniques for Tor classification: Flow level and circuit level classification

## 1. 基本信息

- 题名：Benchmarking two techniques for Tor classification: Flow level and circuit level classification
- 作者：Khalid Shahbar, A. Nur Zincir-Heywood
- 年份：2014
- 会议：2014 IEEE Symposium on Computational Intelligence in Cyber Security, CICS
- DOI：10.1109/cicybs.2014.7013368
- PDF：`paper/10.1109_cicybs.2014.7013368.pdf`
- 主题定位：Tor 加密流量中的用户活动分类，对比“电路级”和“流级”两种观测粒度。
- 本地代码状态：未发现对应开源代码或论文复现实验代码。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：在不解密 Tor 加密内容的前提下，仅凭流量元数据，能够把 Tor 用户正在进行的活动识别到什么程度。

作者比较了两类方法。第一类是电路级分类，需要在 Tor 中继节点内部获取 circuit 和 cell 的统计信息，例如电路生命周期、上下行 cell 数量、cell 到达时间、上下行比例、EWMA 等。第二类是流级分类，只观察用户与入口中继之间的 TCP 流，使用 Tranalyzer2 和 Tcptrace 导出的流统计特征，不需要控制 Tor 中继内部逻辑。

论文的关键结论是：流级分类在准确率上可以接近甚至达到电路级分类，同时部署条件更宽松。电路级方法需要访问或修改 Tor relay，现实中可用性有限；流级方法只需要能抓取用户到入口节点之间的加密 TCP 通信，因此可在用户端、入口节点或 ISP 侧完成。

## 3. 论文解决的具体问题

论文解决的不是“能否解密 Tor 内容”，而是“即使内容加密，通信行为是否仍泄露应用类型”。

具体任务是三分类：

- Browsing：网页浏览
- Streaming：视频流媒体
- BitTorrent：P2P 下载

作者关注两个观测层次：

- Tor 内部电路层：基于 circuit/cell 的行为统计判断活动类型。
- 外部网络流层：基于 TCP flow 的统计特征判断活动类型。

这对应一个重要安全问题：匿名通信系统隐藏了用户身份和内容，但是否隐藏了用户行为类型。论文的答案是：没有完全隐藏，至少在实验条件下，应用类别可以被高精度识别。

## 4. 创新点深度提炼

第一，论文把 Tor 活动识别从“必须进入 Tor 内部”扩展到“只看外部 TCP 流”。前人工作主要利用 circuit/cell 级信息，攻击或分析者需要控制 relay 或访问 relay 内部状态。本文证明，只使用用户和入口节点之间的 TCP 流统计，也能取得很高分类准确率。

第二，论文扩展了电路级特征集。作者认为仅看电路传输总量不够，因为同样的数据量在不同生命周期下含义不同。因此加入了：

- 单位生命周期内的 cell 数量
- 上行 cell 数量
- 下行与上行 cell 比例
- cell 序列的 EWMA

这些特征直接针对三类应用的通信模式差异：网页浏览短促突发、视频流更平滑持续、BitTorrent 上下行更活跃且电路更长。

第三，论文做了方法可用性的基准对比。它不是只追求最高准确率，而是把“准确率”和“部署条件”一起比较。电路级方法准确但难部署，流级方法更灵活，适合在不修改 Tor 的条件下做流量分析。

第四，论文显式处理了隐私约束。作者只标注自己控制的客户端流量，并用 IP 区分三类实验客户端，同时避免记录其他真实 Tor 用户的 circuit/cell 信息。这一点说明 Tor 流量研究的数据构建本身就是难点。

## 5. 科学问题与研究假设

科学问题可以概括为：

- Tor 的加密 cell 是否仍保留可被机器学习利用的行为指纹？
- 电路级统计与流级统计在识别用户活动时，性能差距有多大？
- 不访问 Tor relay 内部状态，仅依靠 TCP flow 特征是否足够完成活动分类？

论文隐含的研究假设包括：

- 不同应用类型在时间、方向、流量规模和持续时间上存在稳定差异。
- 这些差异不会因为 Tor 的加密和固定 cell 机制而完全消失。
- 机器学习分类器可以从 circuit/cell 或 TCP flow 的统计特征中学习到这些模式。
- 流级特征虽然更粗，但包含足够多的行为侧信道信息。

## 6. 科学方法与技术路线

论文采用监督学习路线。

整体技术流程是：

1. 搭建 Tor 实验环境，设置三个客户端分别生成网页浏览、视频流和 BitTorrent 流量。
2. 将三个客户端配置为使用作者控制的 Tor 入口节点。
3. 对电路级方法，修改 Tor 源码，记录来自实验客户端的 circuit 和 cell 信息。
4. 对流级方法，在入口节点抓取客户端到 relay 的 PCAP。
5. 用 Tranalyzer2 和 Tcptrace 从 PCAP 导出 TCP flow 统计特征。
6. 去除 IP、端口、MAC、非 TCP 协议相关属性以及 payload 相关信息，避免分类器直接利用身份字段或内容字段。
7. 使用 Weka 中的 Naive Bayes、Bayes Net、C4.5、Random Forest 进行分类。
8. 用 accuracy 和 F-measure 评估分类结果，并对比前人电路级结果。

技术路线的核心是“加密内容不可见，但元数据可学习”。论文没有引入复杂模型，而是用传统机器学习和手工统计特征证明问题本身存在。

## 7. 实验设计与实验步骤

可复核流程如下。

数据：

- 三个实验客户端分别生成 Browsing、Streaming、BitTorrent。
- 所有客户端都被配置为使用作者控制的 Tor entry node。
- 流级数据抓取持续 10 小时，共得到约 4.2 GB PCAP。
- 电路级数据来自修改后的 Tor 日志，包括 circuit 创建/销毁时间、cell 到达时间、方向、类别和 circuit ID。

预处理：

- Browsing 和 Streaming 由 iMacro 自动生成。
- Browsing：随机搜索词，打开搜索结果，在页面内随机点击链接，并随机停留。
- Streaming：随机搜索视频并播放，停留时间比普通浏览更长。
- BitTorrent：使用 Deluge 生成 P2P 流量。
- 电路级数据按 circuit 聚合 cell 统计。
- 流级数据通过 Tranalyzer2 和 Tcptrace 导出 flow 特征。
- 删除源/目的 IP、端口、MAC、非 TCP 属性和 payload 信息。

模型/基线：

- Naive Bayes
- Bayes Net
- C4.5
- Random Forest
- 对比基线是 Alsabah 等人在 2012 年基于 Tor circuit/cell 的分类方法，最佳离线准确率约 91%。

训练：

- 使用 Weka 默认参数。
- 两种验证方式：
  - 70% 训练、30% 测试切分
  - 10-fold cross-validation
- 数据分布包含两类设置：
  - 电路级：60% Browsing、20% Streaming、20% BitTorrent
  - 流级：一组均衡三分类，一组按前人设置下采样为 60/20/20

指标：

- Accuracy
- Precision
- Recall
- F-measure
- 分类别报告 Browsing、Streaming、BitTorrent 的 F-measure。

消融/敏感性：

- 论文没有做严格的逐特征消融。
- 但通过讨论说明新增特征的作用：生命周期、上行 cell、上下行比例能缓解 Browsing 与 BitTorrent、Browsing 与 Streaming 的混淆。
- 对流级方法，比较了不同 flow exporter：Tranalyzer2 与 Tcptrace。
- 对分类器敏感性，比较了四种传统监督模型。

结果核查：

- 电路级分类在 70/30 split 下，C4.5 达到 100%；10-fold 下 Random Forest 约 94.9%。
- 均衡流级数据中，Tranalyzer2 + Bayes Net 在 split 下 100%，cross-validation 下 99.2%。
- 下采样为 60/20/20 后，Tranalyzer2 + Bayes Net 在 split 和 cross-validation 下均达到 100%。
- Tcptrace 在下采样设置下明显弱于 Tranalyzer2，尤其 Streaming 和 BitTorrent 的 F-measure 下降较多。

## 8. 关键结果、结论与证据

最重要的结果是：流级分类并不明显弱于电路级分类。

电路级结果：

- C4.5 在 70/30 split 下达到 100% accuracy。
- Random Forest 在 10-fold cross-validation 下约 94.9%。
- 相比前人 91% 的电路级离线分类结果，作者报告有约 9% 提升。

流级结果：

- 均衡类别设置下，Tranalyzer2 特征明显强，Bayes Net 的 10-fold accuracy 为 99.2%。
- 下采样为 60/20/20 后，Tranalyzer2 + Bayes Net 达到 100%。
- Tcptrace 也能分类，但在下采样设置下表现不稳定，说明 flow exporter 的特征质量对结果影响很大。

论文结论可以拆成三层：

- 安全结论：Tor 加密不能完全隐藏用户活动类型。
- 方法结论：基于 flow 的外部统计特征足以完成高精度活动分类。
- 工程结论：流级方法比电路级方法更容易部署，因为不需要修改或控制 Tor relay。

## 9. 局限性与待解决问题

第一，数据规模和场景有限。实验只覆盖三类活动：浏览、流媒体和 BitTorrent。真实 Tor 使用包含登录、聊天、文件传输、暗网访问、API 请求、混合会话等更复杂行为，三分类结果不能直接外推到开放世界多类别识别。

第二，实验环境有明显控制条件。三个客户端被配置为使用作者自己的入口节点，且应用类型与客户端 IP 绑定。虽然作者删除 IP 作为训练特征，但数据生成方式仍可能带来环境偏差。

第三，缺少跨时间、跨网络、跨 Tor 版本验证。论文没有证明模型在不同日期、不同 relay、不同拥塞条件、不同 Tor 客户端版本下仍稳定。

第四，没有严格特征消融。作者解释了新增电路级特征为何有用，但没有逐项去除特征验证每个特征的独立贡献。

第五，在线分类仍未完成。论文最后明确把 online classification 作为未来工作；现有结果主要是离线分类，不能直接说明实时检测性能。

第六，可能存在数据泄漏风险需要复核。尤其是 100% accuracy 的结果，在小规模受控实验中需要检查切分方式是否按 flow/circuit 随机切分，而非按时间或会话切分。若同一长会话被拆分到训练集和测试集，性能可能偏乐观。

## 10. 与本项目的关系

这篇论文与“加密流量分类与应用识别”直接相关，对异常检测项目的价值主要在三个方面。

第一，它提供了加密流量场景下的经典特征工程思路。即使 payload 不可见，仍可利用持续时间、方向、上下行比例、速率变化、EWMA、flow 统计等元数据建模。

第二，它提醒异常检测任务必须注意观测位置。电路级特征强但依赖系统内部权限；流级特征弱一些但部署更现实。对于实际网络安全项目，流级方法通常更接近可落地方案。

第三，它适合作为“基准与方法论”类参考。论文没有提出复杂模型，但清楚展示了数据采集、特征构造、分类器比较和可部署性分析，对构建本项目的实验章节有参考价值。

但它与现代异常检测仍有距离：类别少、模型传统、缺少开放集检测、概念漂移分析和跨域泛化验证。因此更适合作为综述中“早期 Tor 流量分类基准研究”，而不是作为当前最先进方法。

## 11. 代码对照分析

本地未发现该论文对应开源代码，因此无法进行逐文件源码对照。根据论文方法，如果复现实验，代码或脚本通常会对应以下模块：

- 数据生成：iMacro 脚本负责网页浏览和视频流自动化，Deluge 负责 BitTorrent。
- Tor 修改：需要修改 Tor 源码，在入口 relay 侧记录 circuit 创建/销毁、cell 到达时间、方向、class、circuit ID。
- 抓包：使用 tcpdump 或 Wireshark 在入口节点抓取实验客户端到 relay 的 PCAP。
- 流特征导出：Tranalyzer2 和 Tcptrace 对 PCAP 生成 flow-level CSV/text 特征。
- 特征清洗：删除 IP、端口、MAC、非 TCP 特征和 payload 相关字段。
- 数据标注：根据实验客户端 IP 映射 Browsing、Streaming、BitTorrent 标签，但不把 IP 输入分类器。
- 模型训练评估：Weka 中运行 Naive Bayes、Bayes Net、C4.5、Random Forest，并输出 accuracy 和 F-measure。

如果后续补充代码包，最关键应检查四类文件：Tor logging patch、PCAP-to-flow 脚本、特征筛选脚本、Weka 训练配置或 ARFF 数据生成脚本。

## 12. 本篇精华

- Tor 隐藏内容和身份路径，但应用行为仍会通过流量统计泄露。
- 电路级分类准确，但需要访问 Tor relay 内部 circuit/cell 信息，现实部署门槛高。
- 流级分类只依赖用户到入口节点之间的 TCP flow，部署位置更灵活，仍可取得接近 100% 的受控实验准确率。
- Browsing、Streaming、BitTorrent 的主要差异体现在生命周期、上下行 cell 数量、上下行比例和速率衰减模式。
- Tranalyzer2 的 flow 特征在本文实验中明显优于 Tcptrace，说明流导出工具本身会影响分类性能。
- 100% accuracy 不能简单理解为真实世界中 Tor 活动完全可识别，仍需警惕受控数据、随机切分和类别有限带来的乐观偏差。
- 这篇论文适合作为加密流量分类的早期基准研究，用于说明“payload-free traffic analysis”的可行性和部署权衡。

## 13. 建议精读路线

建议先读 Introduction 和 Classification for Tor，抓住论文的两个层次：circuit level 与 flow level。重点理解两者的观测权限差异，这是本文最有价值的比较点。

第二步读 Tor Background 中对 circuit、cell、上下行行为的解释，并结合 Figure 2、Figure 3、Figure 4 理解三类应用的速率曲线差异。

第三步精读 Experiments，特别是数据采集方式、客户端自动化、Tor 源码修改、PCAP 抓取和特征删除规则。这部分决定实验可信度。

第四步读 Results and Discussion，不只看最高准确率，还要比较 Tranalyzer2 与 Tcptrace、split 与 cross-validation、均衡分布与 60/20/20 分布之间的差异。

最后复核局限：数据是否会话级独立切分、是否存在同源环境偏差、三分类是否足以代表真实 Tor 使用。这些问题比单个 100% 数字更值得在综述或科研汇报中展开。