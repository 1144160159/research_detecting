# [083] Generating Network Intrusion Detection Dataset Based on Real and Encrypted Synthetic Attack Traffic

## 1. 基本信息

- 编号：083
- 题名：Generating Network Intrusion Detection Dataset Based on Real and Encrypted Synthetic Attack Traffic
- 年份：2021
- 来源：Applied Sciences
- DOI：10.3390/app11177868
- 主题归属：入侵检测与网络异常检测
- 数据集名称：HIKARI-2021
- 核心对象：真实背景流量、HTTPS/TLS 加密合成攻击流量、NIDS 评测数据集构建方法
- 代码状态：本地未发现该论文对应开源代码包；论文声称公开了数据集与生成过程，数据位于 Zenodo。

## 2. 中文翻译与核心摘要

这篇论文的核心不是提出一个新的检测模型，而是提出一个更贴近当前网络环境的入侵检测数据集构建方法，并发布 HIKARI-2021 数据集。作者认为，很多经典 IDS 数据集已经不适合今天的评测：要么年代久远，要么缺少真实背景流量，要么没有可靠 ground truth，要么没有 payload，要么没有体现加密流量已经成为主流的现实。

HIKARI-2021 的设计思路是：在真实生产网络中采集背景流量，同时在受控攻击者网络中生成 HTTPS/TLS 加密的良性访问和攻击流量，然后通过 Zeek 提取 86 个流特征，并对每条 flow 打上二分类标签和细粒度流量类别标签。攻击类型主要包括 CMS 登录暴力破解、XML-RPC 暴力破解、CMS 漏洞探测，以及在背景流量中额外发现的 XMRIGCC 加密货币挖矿流量。

论文真正想解决的是 IDS 数据集的“可信评测基础”问题：如何让数据集既有真实网络背景，又有可解释的攻击生成过程、可复核标签、完整 pcap、加密流量特征和可复现生成流程。

## 3. 论文解决的具体问题

论文针对的是网络入侵检测数据集长期存在的几个具体痛点。

第一，现有数据集老化严重。KDD99、NSL-KDD 等仍被大量使用，但其攻击类型、网络协议、业务形态与今天的真实网络相差很远。用这些数据集评估现代 IDS，容易得到虚高或无现实意义的性能。

第二，很多数据集没有充分体现加密流量。现实中的 Web 访问和攻击大量通过 HTTPS/TLS 传输，而许多 IDS 数据集仍主要面向明文协议或只提供粗粒度 NetFlow 信息。对于加密攻击流量，payload 内容不可直接解析，检测必须更多依赖流统计、时序、TLS 会话行为和方向性特征。

第三，ground truth 与标签可靠性不足。真实流量难以人工确认是否恶意，纯合成流量又不够真实。论文试图折中：背景流量来自真实网络，攻击和良性用户行为由脚本控制生成，因此攻击流量的源、目的、端口、协议、时间窗口可以追溯，标签依据更明确。

第四，数据集构建方法缺少过程公开。很多论文只发布最终 CSV 或特征表，不说明如何捕获、匿名化、注入攻击、提取特征和打标签。作者把数据集要求分为内容要求和过程要求，强调未来研究者应能按同样流程重新生成或扩展数据集。

## 4. 创新点深度提炼

1. 把“加密攻击流量”放在数据集设计中心  
   HIKARI-2021 聚焦通过 HTTPS/TLS 1.2 投递的应用层攻击，而不是仅把加密流量作为普通背景现象。这一点对现代 NIDS 更关键，因为攻击者常利用加密信道绕过基于内容特征的检测。

2. 同时提出内容要求与过程要求  
   论文不是只发布数据，而是先归纳数据集应满足的要求：完整捕获、payload、匿名化、ground truth、可更新、标签、加密信息，以及生成方法。这使它更像一套数据集构建规范，而不只是一个静态 benchmark。

3. 真实背景流量与可控合成攻击结合  
   背景流量来自真实 victim network，攻击和良性访问来自受控 attacker network。这样既保留真实网络的复杂性，又避免攻击标签完全依赖事后猜测。

4. 通过浏览器自动化模拟良性 HTTPS 用户行为  
   良性流量不是简单访问固定 URL，而是用 Selenium 驱动 Chrome/Firefox headless 浏览器，模拟注册、登录、发文、登出、随机点击等行为。这比单纯 curl 请求更接近 Web 用户交互。

5. 攻击目标选择现实常见 CMS  
   论文选择 WordPress、Joomla、Drupal 作为 victim 服务，因为它们市场占有率高、历史 CVE 多，暴力破解和漏洞探测具有现实意义。

6. 标签设计兼顾二分类和细粒度类别  
   数据集中既有 `Label`：Benign/Attack，又有 `traffic_category`：Background、Benign、Bruteforce、Bruteforce-XML、Probing、XMRIGCC CryptoMiner。这对二分类、攻击类型识别和类别不平衡研究都更方便。

## 5. 科学问题与研究假设

这篇论文背后的科学问题可以概括为：

能否构建一个既包含真实网络背景、又包含可验证加密攻击流量的 IDS 数据集，使其比旧数据集更适合作为现代 NIDS 评测基础？

论文隐含了几条研究假设。

第一，IDS 数据集质量会显著影响模型评价可信度。若数据集缺少真实背景、加密流量或可靠标签，则模型性能不能代表真实部署效果。

第二，即使攻击通过 HTTPS/TLS 传输，仍可以从流级统计特征中观察到可分类信号。作者用 KNN、MLP、SVM、RF 的基础实验验证这一点，结果多个模型取得接近 0.99 的 F1。

第三，真实背景流量加合成攻击是一种比纯仿真更实用的折中方案。真实流量提供复杂背景，合成攻击提供标签确定性。

第四，数据集不仅要“可用”，还要“可再生成”。网络环境、攻击工具和协议都会变化，因此公开生成方法比只公开静态 CSV 更有长期价值。

## 6. 科学方法与技术路线

论文的方法路线可以分为六层。

第一层是需求建模。作者系统比较 KDD99、MAWILab、CAIDA、SimpleWeb、NSL-KDD、IMPACT、UMass、Kyoto、IRSC、UNSW-NB15、UGR’16、CICIDS-2017 等数据集，从完整捕获、payload、匿名化、ground truth、标签、加密流量、可生成性等角度找缺口。

第二层是网络环境搭建。攻击者网络与受害者网络分离。攻击者机器运行 CentOS 7/8，使用 Bash 和 Python 3.8.8；受害者网络部署三台 CMS 服务器：Joomla、Drupal、WordPress，运行在 Debian 系统上，并使用默认主题和插件。

第三层是流量生成。背景流量来自 victim network 的真实采集；良性合成流量由 Selenium 模拟浏览器用户行为；攻击流量包括浏览器暴力破解、XML-RPC 暴力破解和 CMS 漏洞探测。

第四层是流量捕获与匿名化。作者使用 tcpdump 进行 full packet capture。对真实背景流量中的敏感部分进行匿名化，IP 地址匿名化采用 Crypto-PAn 思路，同时处理 payload 以保护隐私。合成良性和攻击流量则保留完整捕获。

第五层是特征提取。作者使用 Zeek 提取流级特征，特征设计大体继承 CICIDS-2017 的 80 余个统计特征，并加入 Zeek 相关字段，如 `uid`、`originh`、`originp`、`responh`、`responp`、`traffic_category`、`Label`。

第六层是标签与基础评测。标签以 flow 为单位，依据五元组、协议、生成日期和场景规则确定。随后使用 KNN、MLP、SVM、RF 做基础性能检验，指标包括 Accuracy、Balanced Accuracy、Precision、Recall、F1。

## 7. 实验设计与实验步骤

数据：  
采集时间为 2021 年 3 月 28 日至 5 月 4 日之间的非连续时段，每次采集 3 到 5 小时，总计约 39 小时。数据包含真实背景流量、Selenium 生成的 HTTPS 良性流量、HTTPS 暴力破解、HTTPS XML-RPC 暴力破解、CMS 探测流量，以及从背景流量中识别出的 XMRIGCC CryptoMiner。

预处理：  
使用 tcpdump 捕获 pcap。对背景流量进行隐私保护处理，重点匿名化 IP 和 payload；合成攻击与合成良性流量保留 payload。之后使用 Zeek 从 pcap 中提取 flow 特征，生成 CSV 和 pkl 形式的 flowmeter 文件。

模型/基线：  
论文没有提出新模型，只用四个传统机器学习模型做 sanity check：KNN、MLP、SVM、Random Forest。这些模型的作用是验证数据集中攻击与良性流量是否存在可学习区分信号，而不是证明某个检测算法最优。

训练：  
论文正文没有详细给出训练/测试划分、超参数、归一化、随机种子等细节。从可复核角度，复现实验时应明确：按 flow 级样本划分训练集和测试集，避免同一攻击会话的高度相似 flow 泄漏到两侧；对数值特征做标准化或归一化；移除明显会造成标签泄漏的字段后再训练，如源/目的 IP、生成日期或直接类别字段。

指标：  
论文报告 Accuracy、Balanced Accuracy、Precision、Recall、F1。Balanced Accuracy 是必要的，因为数据类别明显不平衡：Background 和 Benign 远多于攻击类别。

消融/敏感性：  
论文没有系统消融实验。合理的复核方案应补充几组敏感性实验：去除 IP/端口字段后性能是否仍高；仅使用加密会话特征时性能如何；按时间切分训练/测试时是否下降；按攻击类型留一测试能否泛化；背景流量中未标注异常对误报率有多大影响。

结果核查：  
复核时不能只看 0.99 F1。应检查混淆矩阵、每类召回率、攻击类别间混淆、训练测试划分是否泄漏场景信息、`traffic_category` 是否被误用作输入特征、以及模型是否主要学习到了源 IP、目的端口、日期等采集工况特征。

## 8. 关键结果、结论与证据

数据规模上，HIKARI-2021 包含 555,278 条 flow。其中 Background 170,151 条，Benign 347,431 条，Bruteforce 5,884 条，Bruteforce-XML 5,145 条，Probing 23,388 条，XMRIGCC CryptoMiner 3,279 条。加密会话数量方面，Benign 有 116,309 条，Background 有 36,782 条，三类合成攻击均为加密流量，XMRIGCC CryptoMiner 没有加密会话记录。

特征层面，数据集包含 86 个字段，覆盖包数、方向性包数、速率、header size、TCP flag、payload 长度统计、IAT、active/idle 时间、初始窗口大小等。论文指出多数特征分布高度偏斜，95 分位数远小于最大值，这意味着建模时需要考虑异常值、重尾分布和标准化策略。

基础模型结果显示，KNN 的 F1 为 0.88，MLP、SVM、RF 均约为 0.99。这说明 HIKARI-2021 中的攻击与良性流量在流级统计特征上确实存在明显可分性。不过，这也提示潜在问题：如果划分方式不严格，模型可能学习到采集场景或生成脚本特征，而不是真正的攻击行为本质。

与其他数据集相比，HIKARI-2021 的突出证据是：它比 KDD99 更现代；比仅 NetFlow 的数据集保留更多 pcap 信息；比许多真实流量数据集有更明确标签；比 CICIDS-2017 更强调 HTTPS/TLS 应用层攻击；并提供生成流程作为未来扩展基础。

## 9. 局限性与待解决问题

第一，攻击类型覆盖有限。论文选择了暴力破解、XML-RPC 暴力破解、漏洞探测和被动发现的加密挖矿流量，但没有覆盖 SQL 注入、XSS、Webshell 上传、命令执行、横向移动、C2 通信、DDoS、低慢速攻击等更广泛场景。

第二，合成攻击可能带有脚本指纹。即使用 Selenium 模拟浏览器行为，攻击和良性流量仍可能存在工具、时间间隔、源网络、目标路径上的固定模式。模型高分未必意味着能泛化到真实攻击者。

第三，标签依赖五元组、日期和生成规则，存在标签泄漏风险。若研究者直接把 IP、端口、时间相关字段纳入训练，模型可能学到“哪个机器/哪个时段是攻击”，而不是学到攻击行为。

第四，背景流量无法绝对保证干净。作者通过 Zeek 规则发现了 XMRIGCC CryptoMiner，并将其作为攻击类加入，但真实背景中是否仍有未发现恶意流量，论文不能完全证明。

第五，基础评测不够深入。论文只报告四个模型的总体指标，缺少严格的跨时间、跨攻击、跨目标 CMS、去泄漏字段、类别级性能和误报分析。

第六，匿名化与 payload 可用性存在张力。背景流量为保护隐私进行了匿名化和 payload 处理，这虽然必要，但也限制了后续基于内容、TLS 指纹或应用语义的深入分析。

第七，本文正文包未截断，本次理解基于完整提供的正文内容；但由于本地未发现代码包，代码级复核仍无法完成。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”项目高度相关，尤其适合作为数据集与基准构建类文献使用。

对异常检测研究来说，HIKARI-2021 的价值不在于模型，而在于数据生成逻辑。它提醒我们：异常检测实验不能只追求高准确率，还必须审查数据是否真实、标签是否可靠、攻击是否现代、加密流量是否覆盖、训练测试是否存在场景泄漏。

对本项目的数据集建设有直接借鉴意义：可以采用“真实背景流量 + 可控攻击注入 + 完整 pcap + flow 特征 + 二级标签”的组织方式；同时把数据集构建文档化，使后续研究者能够增量生成新攻击、新协议、新时间段的数据。

对综述写作也有价值。HIKARI-2021 可以放在 CICIDS-2017、UNSW-NB15、UGR’16 之后，作为强调加密 Web 攻击和过程可复现的新一代 NIDS 数据集代表。

## 11. 代码对照分析

本地代码包状态为“未发现；无”，因此无法逐文件核对实现。论文中提到公开了生成过程和脚本，但当前材料只包含正文，不包含源码目录。

根据论文方法，如果拿到完整代码或 Zenodo 附件，关键源码大概率可按以下线索定位：

- 数据捕获：查找与 `tcpdump`、`pcap`、capture、interface、background 相关的 Bash 或 Python 脚本。
- 背景流量匿名化：查找 Crypto-PAn、anonymize、payload removal、IP anonymization 相关实现。
- 良性流量生成：查找 Selenium、Chrome、Firefox、headless、random click、signup、signin、post、logout、Alexa list 等关键词。
- 暴力破解攻击：查找 brute force、login、credential、password list、common credentials、CMS admin login 相关脚本。
- XML-RPC 攻击：查找 `xmlrpc`、WordPress XML-RPC endpoint、credential guessing 等关键词。
- 漏洞探测：查找 droopescan、joomscan、Drupal、Joomla、WordPress scanner wrapper。
- 特征提取：查找 Zeek、Bro、conn.log、flowmeter、CSV、pkl、feature extraction 相关代码。
- 标签生成：查找 label、traffic_category、five-tuple、source IP、destination IP、port、protocol、scenario date 等规则脚本。
- 训练评估：查找 KNN、MLP、SVM、RandomForest、Accuracy、Balanced Accuracy、Precision、Recall、F1，可能使用 scikit-learn。

需要特别注意：如果复现实验，不能把 `traffic_category`、`Label`、明显场景标识字段作为输入特征；`originh`、`originp`、`responh`、`responp` 也应单独做去除实验，判断模型是否依赖采集环境而非攻击行为。

## 12. 本篇精华

1. HIKARI-2021 的核心贡献是数据集与生成规范，不是检测模型。
2. 论文把现代 IDS 数据集的关键缺口明确指向加密流量、ground truth、完整 pcap、匿名化和可复现生成过程。
3. 数据集采用真实背景流量与受控合成 HTTPS 攻击结合的方式，兼顾现实复杂性和标签可控性。
4. 攻击场景围绕 WordPress、Joomla、Drupal 的暴力破解、XML-RPC 暴力破解和漏洞探测，贴近常见 Web 攻击面。
5. Zeek 提取 86 个流级特征，支持在 payload 不可见或受限时基于统计行为检测加密攻击。
6. 基础模型达到很高 F1，但这既是可分性的证据，也是标签泄漏和场景过拟合需要复核的信号。
7. 对后续研究最有价值的不是直接刷分，而是用它研究加密流量检测、数据集构建规范、特征泄漏、跨时间泛化和真实背景误报。

## 13. 建议精读路线

1. 先读 Introduction，抓住作者对旧 IDS 数据集的批评：过时、缺少加密流量、标签和过程不透明。
2. 再读 Section 3，重点理解内容要求和过程要求，这是论文的方法论核心。
3. 精读 Section 4，画出 HIKARI-2021 的生成流程：网络拓扑、背景流量、良性流量、攻击流量、场景、预处理、标签。
4. 对照 Table 2 和 Table 3，理解类别分布、加密会话数量和 86 个特征的含义。
5. 阅读性能分析时保持怀疑，重点看哪些字段可能造成泄漏，而不是只记住 0.99 的结果。
6. 最后读结论和未来工作，提炼它对你自己项目的启发：如何构造可复核、可扩展、面向加密攻击的异常检测数据集。