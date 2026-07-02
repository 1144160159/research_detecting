# [053] Detection of DoH Tunnels using Time-series Classification of Encrypted Traffic

## 1. 基本信息
- 题名：Detection of DoH Tunnels using Time-series Classification of Encrypted Traffic
- 中文题名：基于加密流量时间序列分类的 DoH 隧道检测
- 年份/会议：2020，IEEE DASC/PiCom/CBDCom/CyberSciTech
- DOI：10.1109/dasc-picom-cbdcom-cyberscitech49142.2020.00026
- 研究对象：DNS over HTTPS 场景下的 DNS 隧道流量检测
- 数据集：作者构建并公开 CIRA-CIC-DoHBrw-2020
- 本地代码状态：未发现该论文对应的 DoHlyzer/DoHMeter 原始代码包；本地仅发现相邻项目中复用 DoHBrw 数据的 `.npy` 样本与训练代码。

## 2. 中文翻译与核心摘要
这篇论文关注一个很具体但重要的问题：DoH 本意是保护 DNS 查询隐私，但它把 DNS 查询封装进 HTTPS/TLS 后，也让传统依赖 DNS 明文、域名长度、TXT 记录、查询频率等特征的 DNS 隧道检测方法失效。作者提出两层检测框架：第一层区分 DoH 与普通 HTTPS，第二层在 DoH 内部区分 benign DoH 与 malicious DoH，即 DoH 隧道。

论文的核心不是破解加密内容，而是证明即使载荷不可见，流量的包大小、方向、时序和连续同向包聚合后的“clump”序列仍然保留了足够的行为模式。统计特征分类器可以取得很高准确率，但需要等待完整流；时间序列 LSTM 利用前几个 clump 就能在约 1 秒内完成判别，更适合在线检测。

## 3. 论文解决的具体问题
传统 DNS 隧道检测依赖 DNS 层可见性，例如子域名熵、查询频率、记录类型、请求响应关系等。DoH 将 DNS 放入 HTTPS 后，网络侧只看到 TCP/443 TLS 流，DNS 内容、查询次数甚至 HTTP/2 多路复用下的请求粒度都被隐藏。

因此本文解决的是：在不解密 HTTPS、看不到 DNS 明文的情况下，能否仅凭加密流量的时序形态识别 DoH，并进一步识别 DoH 隧道。这个问题比普通 DNS tunnel detection 更难，因为检测器面对的是“看起来都像 HTTPS”的流量。

## 4. 创新点深度提炼
1. 两层分类思想清晰：先做 DoH/non-DoH 过滤，再对 DoH 做 benign/malicious characterization，避免直接在所有 HTTPS 流中寻找隧道导致类别边界混乱。
2. 构建了 CIRA-CIC-DoHBrw-2020，包含普通 HTTPS、良性 DoH 浏览流量、DoH 隧道流量，并覆盖 Google Chrome、Firefox、AdGuard、Cloudflare、Google DNS、Quad9 以及 Iodine、DNS2TCP、DNScat2 等工具。
3. 提出 packet clump 表示：把同一方向、时间间隔未超过阈值的连续包合并为一个 clump，用 `size、pktCount、direction、duration、interarrival` 表示，试图恢复被 TLS 分段/IP 分片打散的应用层行为节奏。
4. 将检测延迟作为核心指标之一。统计特征效果高但依赖完整流，LSTM clump 序列能用少量早期流量实现在线检测。
5. 论文实际把 DoH 隧道检测从“DNS 内容分析”转向“加密流行为建模”，这对后续加密恶意流量、C2 隐蔽信道、跨域异常检测都有借鉴价值。

## 5. 科学问题与研究假设
核心科学问题是：DoH 加密是否彻底抹除了 DNS 隧道与正常 DoH 在网络侧的可分性？

作者隐含了几个假设。第一，虽然载荷不可见，但包长、方向、到达间隔、请求响应节奏仍携带应用行为指纹。第二，DoH 隧道为了传输数据，会产生与正常网页 DNS 解析不同的连续交互模式。第三，这种差异在流的早期就可见，不必等待完整连接结束。第四，公共 DoH resolver 与常见 DNS 隧道工具生成的实验流量足以代表一类真实攻击行为。

## 6. 科学方法与技术路线
技术路线是“采集 HTTPS 流量 -> 五元组建流 -> 标签构造 -> 特征抽取 -> 两层二分类”。

预处理阶段按 `<src IP, dst IP, src port, dst port, protocol>` 识别流。由于 TCP 和目的端口 443 对各类样本相同，标签主要依赖目的 IP、生成工具和采集场景：浏览器访问 Alexa Top 10k 产生 non-DoH HTTPS 与 benign DoH；DNS 隧道工具经 DoH proxy 封装后产生 malicious DoH。

特征分两类。统计特征包括发送/接收字节数及速率、包长统计、包时间统计、请求响应时间差统计，共 28 个。时间序列特征则过滤掉无载荷 ACK 和过小包，只保留 TLS application data 相关包，进一步构造 clump 序列，并用滑动窗口长度 `λ` 生成固定长度片段。分类器方面，统计特征使用 RF、C4.5、SVM、NB、DNN、2D CNN；时间序列使用含 LSTM 层的深度网络。

## 7. 实验设计与实验步骤
1. 数据：采集三类 HTTPS 流量：普通 HTTPS、良性 DoH、恶意 DoH 隧道。浏览器侧使用 Firefox/Chrome 访问 Alexa Top 10k；DoH resolver 包括 AdGuard、Cloudflare、Google、Quad9；隧道工具包括 Iodine、DNS2TCP、DNScat2。
2. 预处理：用五元组切分 flow；清理少量 NaN flow；按 80%/20% 划分训练与测试；统计特征由 DoHMeter 抽取，时间序列由 DoHlyzer/Scapy 思路读取 pcap 或在线嗅探。
3. 模型/基线：统计特征基线包括 RF、C4.5、SVM、NB、DNN、2D CNN；时间序列模型为 LSTM。两层均为二分类：Layer 1 是 DoH vs non-DoH，Layer 2 是 benign DoH vs malicious DoH。
4. 训练：对完整 flow 训练统计分类器；对 clump segment 训练 LSTM，并改变 `λ=1...10` 观察精度和检测延迟。
5. 指标：Precision、Recall、F1-score，同时记录 flow duration 或 clump sequence duration，用于评估在线检测时延。
6. 消融/敏感性：主要敏感变量是 clump 数 `λ`。Layer 1 从 1 到 6 个 clump 精度明显上升；Layer 2 在 3 个 clump 左右已经接近稳定高精度。
7. 结果核查：重点核查高精度是否来自完整流等待过长，作者用 duration 分布说明 LSTM 在 Layer 1 约 6 个 clump、Layer 2 约 3 个 clump 时可在 1 秒内检测。

## 8. 关键结果、结论与证据
统计特征下，Layer 1 的 RF/C4.5 precision、recall、F1 均为 0.993；Layer 2 的 RF/C4.5 三项指标均为 0.999。SVM 和 NB 明显较弱，DNN/2D CNN 介于中间或接近树模型。

但完整流统计特征有延迟问题：Layer 1 平均 flow duration 为 20.393 秒，Layer 2 平均为 53.924 秒。对在线防御来说，这意味着检测结果可能来得太晚。

时间序列 LSTM 解决的是“早判别”。Layer 1 在 `λ=6` 时 precision/recall/F1 均达到 0.993，平均片段时长 0.574 秒；Layer 2 在 `λ=3` 时 precision/recall/F1 均约 0.991，平均片段时长 0.502 秒。作者进一步根据 duration 分布认为两层检测均可控制在约 1 秒内。

## 9. 局限性与待解决问题
正文包标记未截断，本次理解不受正文缺失影响。

主要局限在数据外推性。恶意样本由实验环境中的 Iodine、DNS2TCP、DNScat2 生成，不能覆盖所有 DoH 滥用方式；论文也明确说 malicious label 在这里特指 DoH tunneling，而不是所有恶意 DoH。标签构造依赖受控环境、目的 IP 和工具场景，真实企业网络中 CDN、代理、浏览器实现、DoH relay、ECH/HTTP/3 等变化可能改变流量形态。

另一个问题是缺少跨网络、跨时间、跨 resolver、跨客户端版本的泛化验证。论文展示了 `λ` 对性能和延迟的影响，但对 clump timeout、HTTP/2 多路复用强度、低速隧道、攻击者主动填充/限速规避等没有充分展开。统计模型和 LSTM 高分也需要在更复杂背景流量下复核误报率。

## 10. 与本项目的关系
这篇论文与“加密流量分类与应用识别”“恶意流量/暗网/攻击检测”“跨域异常检测”强相关。它提供了一个很好的研究范式：不依赖解密和 DPI，而是从加密流的时间结构中构造可解释的行为单元。

对本项目最有价值的是 clump 思路。相比直接使用 packet 序列，clump 把连续同向包聚合，既降低维度，又更接近应用交互节奏。若本项目关注异常检测，可以把 clump 序列作为统一输入表示，再做监督分类、半监督异常检测或跨域泛化实验。

## 11. 代码对照分析
未发现本文对应的本地 DoHlyzer/DoHMeter 原始源码包，因此不能做逐文件复现级对照。论文中提到的代码角色大致应为：DoH Data Collector 负责 DoH 隧道场景配置、SSH 控制、tcpdump 采集；DoHMeter 负责从 pcap 建 flow 并抽取 28 个统计特征；DoHlyzer 负责基于 Scapy 读取 pcap/在线嗅探、生成 DoH flow、做 clump/time-series 分析。

本地发现的 [README.md](<F:/泉城实验室/二期/论文/异常检测/source/MAML-Training-ETC/README.md:1>) 属于另一篇 “Training Robust Classifiers for Classifying Encrypted Traffic under Dynamic Network Conditions”，不是本文源码。它包含 DoHBrw 样本数据线索：`DoHBrw-ALL` 下有 `X_AdGuard_*、X_CloudFlare_*、X_Google_*、X_Quad9_*` 和对应 `y_*.npy`。相关读取逻辑在 [dataset.py](<F:/泉城实验室/二期/论文/异常检测/source/MAML-Training-ETC/dataset.py:101>)，训练入口在 [train.py](<F:/泉城实验室/二期/论文/异常检测/source/MAML-Training-ETC/train.py:28>)，模型包括 [base_models.py](<F:/泉城实验室/二期/论文/异常检测/source/MAML-Training-ETC/base_models.py:73>) 的 DFNet 和 [base_models.py](<F:/泉城实验室/二期/论文/异常检测/source/MAML-Training-ETC/base_models.py:203>) 的 DFTransformer。该代码更像后续加密流量鲁棒分类实验，不包含本文的 clump 生成、DoHMeter 统计特征、两层 DoH 隧道检测 LSTM 主流程。

## 12. 本篇精华
- DoH 隧道检测的难点不是“DNS 隧道”本身，而是 DoH 把 DNS 层证据藏进 HTTPS 后，传统 DNS 明文特征失效。
- 两层检测比单阶段多类分类更符合防御流程：先识别 DoH，再判断 DoH 是否承载隧道。
- packet clump 是本文最值得复用的表示：用同向连续包聚合恢复加密流中的交互节奏。
- 完整流统计特征能给出很高分数，但平均要等几十秒；在线安全场景更看重早期 clump 序列。
- LSTM 在 Layer 1 用 6 个 clump、Layer 2 用 3 个 clump 就能达到约 0.99 F1，说明 DoH 隧道早期行为差异明显。
- CIRA-CIC-DoHBrw-2020 是后续 DoH 检测、加密流量分类、跨域鲁棒性研究的重要基准。
- 论文结论强，但泛化仍需谨慎：实验隧道工具、resolver、网络环境和攻击策略都较受控。

## 13. 建议精读路线
先读 Section III-B 的 clump 定义和 Algorithm 1，这是方法核心。然后读 Section IV，弄清 benign DoH、malicious DoH、non-DoH 的采集边界，否则容易误解标签含义。接着对照 Table III/IV 和 Table V/VI，比较“完整流统计特征高准确但慢”与“clump LSTM 稍早判别且仍高准确”的差异。最后读结论和 future scope，重点思考本项目能否沿着 DoH proxy、DoH server、跨网络环境和规避攻击继续扩展。

<!-- codex-cli-deep-read: complete -->
