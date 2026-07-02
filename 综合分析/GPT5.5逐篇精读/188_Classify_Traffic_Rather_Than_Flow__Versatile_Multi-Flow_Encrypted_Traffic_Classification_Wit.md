# [188] Classify Traffic Rather Than Flow: Versatile Multi-Flow Encrypted Traffic Classification With Flow Clustering

## 1. 基本信息

- 题名：Classify Traffic Rather Than Flow: Versatile Multi-Flow Encrypted Traffic Classification With Flow Clustering
- 作者：Zihan Chen, Guang Cheng, Zijun Wei, Dandan Niu, Nan Fu
- 来源：IEEE Transactions on Network and Service Management
- DOI：10.1109/TNSM.2023.3322861
- 在线发表：2023-10-09；正式卷期：Vol. 21, No. 2, April 2024
- 主题：加密流量分类、应用识别、多流分类、流聚类、开放世界流量分析
- 数据集：ISCX VPN-nonVPN、CERNET-Access-2022、CERNET-Access-2023-Aug
- 代码状态：本地未发现该论文对应开源代码包

## 2. 中文翻译与核心摘要

论文标题可译为：**“分类流量而不是分类单条流：基于流聚类的通用多流加密流量分类方法”**。

这篇论文的核心判断很明确：现有加密流量分类通常把**单条 flow** 当作分类单元，但真实应用访问并不是这样产生流量的。一次网页访问、一次 App 打开、一次业务交互，往往会同时或连续产生多条 TCP/UDP 流。这些流共同服务于同一次访问，因此它们之间存在时间、资源、业务语义上的关联。

作者认为，继续逐条 flow 分类会带来四类问题：重复计算、结果冲突、低置信度小流误判、外链/共享服务造成的类别混淆。因此论文提出：应把一次访问产生的多条流组织成 **flow bunch**，再面向 flow bunch 做分类。

技术路线分两层：

1. 先用 **TSHC-SW**，即带滑动窗口的时间序列层次聚类，把原始加密 flow 聚成 flow bunch。
2. 再提出五种多流分类 schema：SF、EF、d-CV、HF、d-CT，在精度、速度、覆盖率之间按需求取舍。

论文最重要的结论是：**多流分类不是简单扩大输入，而是把分类对象从“孤立流”改为“访问级流量单元”**。在实验中，流聚类达到约 95% ARI 和 98% purity；多流分类在部分模式下可超过 99% F1，同时减少约 79% 预测时间，并提高约 5% 样本覆盖率。

## 3. 论文解决的具体问题

论文解决的是加密流量分类从实验室单流分类走向真实网络部署时的关键错位问题。

传统 ETC 方法通常做的是：

- 输入：一条 flow 或 flow 内包序列；
- 特征：包长序列、到达时间序列、统计特征、TLS 残留明文等；
- 输出：该 flow 属于哪个应用或服务。

但真实网络管理需要知道的是：

- 当前用户正在访问哪个应用；
- 某次访问整体是否属于某个业务；
- 是否需要对这个应用级访问进行 QoS、审计、拦截或安全分析。

单条 flow 并不等价于一次应用访问。一次访问可能包含 HTML 主资源、图片、脚本、CDN、API 请求、广告、第三方登录、视频片段、心跳连接等多种流。若逐条分类，会出现：

- **重复分类**：几十条流都指向同一个应用，浪费推理资源。
- **结果不一致**：核心流判成应用 A，广告/外链流判成应用 B。
- **小流信息不足**：短流或握手流无法提供足够包长序列。
- **开放世界干扰**：未知应用、相似应用、共享 CDN、通用 443 端口会造成混淆。
- **管理不可用**：网络侧拿到一堆 flow 标签，却不能稳定还原用户一次访问的应用意图。

因此论文真正解决的问题是：**如何在不知道真实访问边界的情况下，把加密流量恢复成访问级 flow bunch，并基于多条相关流进行更实用的应用分类。**

## 4. 创新点深度提炼

第一，论文把 ETC 的分类单元从 flow 推进到 access / flow bunch。  
这不是简单把多个 flow 拼起来，而是重新定义了分类对象：一次应用访问产生的多条流才是更贴近网络管理需求的单位。

第二，提出了 flow bunch 概念。  
flow bunch 是围绕单个设备一次访问形成的 flow 集合。它介于单 flow 和 session 之间，比 session 更有业务语义，比单 flow 更稳定。

第三，提出 TSHC-SW 流聚类算法。  
作者没有假设知道访问次数，也没有假设每次访问包含多少流，而是利用流开始时间 `pkt_ts_first` 和结束时间 `pkt_ts_last`，在滑动窗口内做凝聚层次聚类。这个设计适合开放世界，因为它不需要预设簇数。

第四，明确区分了 in-flow relationship 和 inter-flow relationship。  
单流方法只能利用 flow 内包长序列的马尔可夫关系；多流方法额外利用同一次访问中不同 flow 之间的关联。作者用条件熵的表述说明，多一个相关特征空间可降低分类不确定性。

第五，提出五种需求导向 schema。  
SF 追求速度，EF 追求充分投票，d-CV 在速度和准确性之间折中，HF 是纯多流输入，d-CT 进一步扩展候选多流输入。论文不是只给一个模型，而是给一个部署选择空间。

第六，提出 SCR 指标。  
Sample Covering Rate 衡量某个 schema 在真实流量中有多少 flow bunch 能满足输入条件。这个指标很关键，因为开放世界中不能只看分类准确率，还要看多少样本被模型“跳过”。

## 5. 科学问题与研究假设

论文背后的科学问题可以概括为三个：

1. **一次应用访问产生的多条加密 flow 是否具有可利用的关联结构？**
2. **在没有访问边界标签的真实流量中，能否仅靠网络侧可见特征恢复 flow bunch？**
3. **利用 flow bunch 是否能同时提升分类准确率、推理效率和开放世界可用性？**

对应研究假设是：

- H1：同一次访问产生的 flow 在时间上具有突发性和集中性，因此可通过时间特征聚类。
- H2：多条 flow 的包长序列包含 inter-flow relationship，可补充单条 flow 内部特征不足。
- H3：访问级分类比单流分类更符合网络管理任务，能减少重复推理和冲突标签。
- H4：不同部署环境对速度、精度、覆盖率的要求不同，因此多流分类应提供多种 schema，而不是单一模型。
- H5：即使分类器不变，仅改变输入组织方式和预测 schema，也能带来显著收益。

## 6. 科学方法与技术路线

论文方法由三部分组成。

第一部分是应用数据传输模式分析。  
作者指出，一次应用访问会产生两类多流关系：

- continuation mode：前一条流结束后，后续流继续产生；
- concurrent mode：多条流同时服务同一次访问。

这说明单 flow 不是最小业务语义单元，access 才更接近真实应用行为。

第二部分是流聚类。  
因为真实网络中无法直接知道哪些 flow 属于同一次访问，作者先构造 flow bunch。候选聚类特征包括端口、时间、包数量、包长度等 15 个统计特征。实验后发现 `pkt_ts_first` 和 `pkt_ts_last` 最有效。最终采用 TSHC-SW：

- 按流开始时间进入滑动窗口；
- 窗口内使用开始/结束时间作为特征；
- 采用凝聚层次聚类；
- 用距离阈值控制合并；
- 输出若干 flow bunch。

第三部分是多流分类 schema。  
五种 schema 的含义如下：

- **SF**：从 flow bunch 中选一条代表性 flow 分类，通常选 first-flow，速度最快。
- **EF**：对 bunch 中每条 flow 分类，再投票，精度可能提升但代价很高。
- **d-CV**：选 d 条候选 flow 分类并投票，是 SF 与 EF 的折中。
- **HF**：从多个 flow 中各取固定长度包长序列，拼成一个总长度不变的多流输入，是纯多流分类。
- **d-CT**：选 d 条候选 flow，每条保留类似单流长度的包长序列，再组合分类，输入更大，利用信息更多，但覆盖率下降。

## 7. 实验设计与实验步骤

可复核流程如下。

**数据**

1. 使用 ISCX VPN-nonVPN 验证单流分类器基本有效性。
2. 使用 CERNET-Access-2022 做主要多流分类实验。
   - 真实 CERNET 环境采集；
   - 时间跨度为 2022 年 5 月至 11 月；
   - 设备包括 Windows PC、Linux workstation、Android 手机；
   - 同时具备 access 标签和 application 标签。
3. 使用 CERNET-Access-2023-Aug 做更多应用数量下的聚类鲁棒性测试。
   - 100 个应用；
   - 700 次访问；
   - 主要用于聚类验证。

**预处理**

1. 从原始包形成 flow。
2. 记录每条 flow 的起始时间、结束时间、包长序列等特征。
3. 对分类输入，按 schema 截取或组合包长序列。
4. 对不满足输入长度要求的样本，计算是否被覆盖，形成 SCR。
5. 开放世界设置中，选 6 个应用作为已知分类目标，另 2 个相似应用作为背景干扰：
   - 已知：Douban、Sohu、NetEase、Bilibili、JD、Sina；
   - 背景：Youku、Hupu。

**模型/基线**

单流分类基线包括：

- 传统机器学习：C4.5、SVM、kNN；
- 集成学习：XGBoost、Random Forest；
- 深度学习：CNN、Deep Packet、FS-Net、LS-LSTM。

后续重点比较：

- C4.5；
- RF；
- FS-Net；
- LS-LSTM。

**训练**

1. 单流训练对应 SF、EF、d-CV。
2. 多流训练对应 HF。
3. d-candidate 多流训练对应 d-CT。
4. 训练/测试按论文设置采用 80% / 20% 样本比例。
5. 深度学习环境：Python 3.8.8、PyTorch 1.8.1、CUDA 11.1、GTX 3090。

**指标**

分类指标：

- Precision；
- Recall；
- F1-score；
- prediction time；
- training time；
- model size；
- SCR。

聚类指标：

- Purity；
- Rand Index；
- Adjusted Rand Index；
- Adjusted Mutual Information Coefficient。

**消融/敏感性**

1. 聚类窗口大小：60 秒到 420 秒，步长 30 秒。
2. 聚类距离阈值：4、3.5、3、2.5、2、1、0.5、0.1、0.05、0.01。
3. 聚类算法对照：TSHC-SW vs DBSCAN。
4. flow 选择策略：
   - first；
   - random；
   - top。
5. d-CV / d-CT 中 d 从 2 到 5。
6. HF 中 each size θ 选择 10 和 25。

**结果核查**

1. 聚类最佳参数约为 window size = 330 秒，distance threshold = 1。
2. TSHC-SW 明显优于 DBSCAN，达到约 95% ARI 和 98% purity。
3. 聚类吞吐量约 49,081 flows/s。
4. SF 显著节省预测时间，但精度提升有限。
5. EF 精度有时提升，但预测时间代价过大。
6. d-CV 随 d 增大 F1 提升趋缓，覆盖率下降。
7. HF 在 F1、速度、SCR 上整体最均衡，是论文最推荐的 schema。
8. d-CT 精度强，但 SCR 较低，更适合重流量、长流业务。

## 8. 关键结果、结论与证据

第一，时间特征足以较好构造 flow bunch。  
15 个候选统计特征中，流起始时间和结束时间最有判别价值。这说明一次访问产生的多流确实具有时间突发性。

第二，TSHC-SW 聚类效果较强。  
论文报告流聚类达到约 95% ARI 和 98% purity。这个结果是多流分类成立的基础，因为如果 bunch 构造错误，多流分类会把不同应用的流混在一起。

第三，单流强分类器仍然有价值，但对象错了。  
LS-LSTM、FS-Net 等模型在单流分类上表现不错，但论文指出这并不能解决真实网络中重复标签、冲突标签和低覆盖的问题。

第四，SF 的主要价值是速度。  
SF 用 first-flow 代表整个 flow bunch，可以大幅减少预测次数。它牺牲少量或不显著的分类效果，换来明显推理加速，适合在线高吞吐场景。

第五，EF 并不是理想方案。  
虽然 EF 对每条 flow 分类再投票，理论上信息更多，但实际代价很大，尤其 RF 和深度模型会出现预测时间暴涨。并且低显著性 flow 的投票可能拖累结果。

第六，HF 是论文最核心的多流分类方案。  
HF 把多个 flow 的包长片段拼接成固定长度输入，在不改变输入总长度的情况下引入 inter-flow relationship。实验显示 HF 在分类效果、预测时间和 SCR 上都优于传统单流方法。

第七，SCR 是开放世界部署中的关键指标。  
很多分类论文只报告被模型接收样本上的 F1，但真实网络中被跳过的样本也是失败。HF 因为每条 flow 所需包数减少，反而能覆盖更多 flow bunch；d-CT 和 d-CV 随 d 增大，SCR 下降。

第八，first-flow 通常优于 random-flow。  
论文解释为应用实现中核心资源往往先加载，例如 HTML、主 API 或核心业务资源，因此早期 flow 更有应用代表性。

## 9. 局限性与待解决问题

第一，方法高度依赖访问级时间突发性。  
如果应用访问非常稀疏、后台流长期存在、用户并发访问多个应用，TSHC-SW 可能把不同访问混合或把同一访问拆散。

第二，NAT、多设备共 IP 场景未被充分解决。  
论文说明不重点处理 NAT 后多个网络实体识别问题，而是引用已有研究。真实运营商网络中，这仍是部署前必须处理的问题。

第三，非对称采样和丢包场景下 HF 可能退化。  
HF 要求 flow bunch 中有足够多可用 flow。如果采样流量、镜像点不完整、上下行不对称，multi-flow 输入可能不稳定。

第四，d-CT 虽然精度高，但 SCR 低。  
它适合视频等长流应用，不一定适合短交互、小流密集的应用分类。

第五，图结构特征尚未纳入。  
作者在结论中明确提到没有引入图特征。考虑到多 flow 天然可形成时间图、主机图、域名/IP 资源图，这是后续很自然的扩展方向。

第六，公开数据集虽有价值，但类别和环境仍有限。  
CERNET 环境真实，但是否能泛化到移动运营商、企业网、家庭宽带、跨境链路、QUIC/HTTP3 高比例场景，需要进一步验证。

第七，论文主要面向应用分类，不直接解决异常检测。  
它提供了更合适的流量组织单元，但异常定义、未知类别发现、概念漂移检测仍需额外方法。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，原因不在于它直接提出异常检测模型，而在于它改变了加密流量分析的基本粒度。

对异常检测而言，单 flow 级检测常常会遇到同样问题：

- 单条 flow 信息不足；
- 攻击或异常行为跨多条连接展开；
- CDN、外链、共享服务造成误报；
- 单 flow 告警难以还原用户行为上下文。

论文提出的 flow bunch 可以作为异常检测中的更高层样本单元。也就是说，本项目可以借鉴：

- 用访问级 flow bunch 替代孤立 flow；
- 用 inter-flow relationship 建模访问行为；
- 用 SCR 衡量模型在真实流量中的覆盖能力；
- 用 TSHC-SW 或改进版聚类构造无标签访问边界；
- 在 bunch 层做应用识别、异常检测、未知行为发现或跨域迁移。

对“其他 AI 安全与跨域异常检测”方向，本文尤其有启发：跨域问题常来自采集环境、用户行为、链路条件和应用版本变化。多流聚合后，样本语义更稳定，可能比单 flow 特征更抗域偏移。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法逐文件核对作者实现。不过根据论文方法，若复现或实现，代码结构应大致对应以下模块。

**数据预处理**

可能包含：

- pcap 读取；
- flow 构造；
- 五元组划分；
- 包长序列提取；
- `pkt_ts_first` / `pkt_ts_last` 提取；
- access 标签和 application 标签对齐；
- 过滤不满足输入长度的 flow 或 bunch。

核心逻辑应对应论文中的 CERNET-Access 数据构造和 flow feature extraction。

**流聚类**

应实现 TSHC-SW：

- 按时间排序 flow；
- 按 sliding window 切分；
- 在窗口内使用 `[pkt_ts_first, pkt_ts_last]`；
- 凝聚层次聚类；
- 根据 distance threshold 合并；
- 输出 flow bunch；
- 计算 purity、RI、ARI、AMIC。

如果用 Python 复现，可能依赖 `sklearn.cluster.AgglomerativeClustering` 和 `sklearn.metrics`。

**模型**

单流分类器应包含：

- C4.5 或决策树；
- SVM；
- kNN；
- XGBoost；
- Random Forest；
- CNN；
- Deep Packet；
- FS-Net；
- LS-LSTM。

论文真正用于后续重点比较的是 C4.5、RF、FS-Net、LS-LSTM。

**训练 schema**

应有三个训练入口：

- single-flow training：供 SF、EF、d-CV 使用；
- multi-flow training：供 HF 使用；
- d-candidate flow training：供 d-CT 使用。

**评估**

应包含：

- 单流 baseline 评估；
- SF / EF / d-CV / HF / d-CT 评估；
- first / random / top 选择策略；
- d、θ 敏感性实验；
- SCR 计算；
- prediction time、training time、model size 统计；
- 聚类 purity 对最终分类 F1 的修正或约束分析。

如果本项目要复现，建议优先实现最小闭环：pcap-to-flow、TSHC-SW、HF schema、一个 RF baseline、一个 LSTM/GRU 深度模型、SCR 评估。

## 12. 本篇精华

1. ETC 的核心问题不只是“选什么模型”，而是“分类单位是否符合真实网络语义”；单 flow 分类在部署层面天然不足。
2. 一次应用访问产生多条 flow，这些 flow 之间存在 inter-flow relationship，可作为加密流量分类的重要信息来源。
3. flow bunch 是本文的关键抽象：它把网络侧不可见的访问行为转化为可聚类、可分类的样本单元。
4. TSHC-SW 用流起止时间和滑动窗口恢复 flow bunch，不需要预设访问数量，适合开放世界流量。
5. HF schema 是最值得关注的方案：固定总输入长度，但从多条 flow 中抽取包长片段，兼顾准确率、速度和覆盖率。
6. SCR 是真实部署不可忽略的指标；只看 F1 会高估模型，因为被输入条件排除的样本同样影响系统可用性。
7. first-flow 通常比 random-flow 更有代表性，说明应用核心资源加载顺序本身泄露了分类信息。
8. 这篇论文对异常检测的启发是：很多异常不是单连接现象，而是访问级、多连接、上下文相关的行为模式。

## 13. 建议精读路线

1. 先读 Introduction，重点抓住作者批判单 flow ETC 的四个问题。
2. 再读 Section III-A，理解一次访问为什么会产生 continuation 和 concurrent 两种多流模式。
3. 精读 Section III-B，重点理解 in-flow relationship 与 inter-flow relationship 的区别。
4. 精读 Section IV-A，弄清楚 TSHC-SW 如何用滑动窗口和层次聚类构造 flow bunch。
5. 精读 Section IV-B，对照五种 schema 画出输入输出关系，尤其区分 d-CV 和 d-CT。
6. 读实验时先看聚类参数敏感性，再看五种 schema 的 F1、prediction time 和 SCR。
7. 最后回到 Discussion，重点理解作者对 first-flow、HF、SCR、聚类成本的部署解释。

<!-- codex-cli-deep-read: complete -->
