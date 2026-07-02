# [661] Encrypted Traffic Classification Based on Two-Phase Feature Fusion

## 1. 基本信息

- 论文题名：Encrypted Traffic Classification Based on Two-Phase Feature Fusion
- 作者：Xiaobin Tan, Chaoming Huang, Hao Wang, Shuangwu Chen, Quan Zheng
- 年份：2026
- 来源：IEEE Transactions on Cognitive Communications and Networking
- DOI：10.1109/TCCN.2026.3683889
- 主题归类：加密流量分类、应用识别、内容类型识别、TLS 流量侧信道分析
- 核心方法：2P2F，两阶段特征融合，即 TLS 握手阶段特征 + 安全数据传输阶段特征，再用注意力机制融合。

## 2. 中文翻译与核心摘要

这篇论文的核心观点是：加密流量不应该被当成一个同质的整体处理。TLS/SSL 流量天然分为两个阶段：握手阶段和安全数据传输阶段。前者虽然不包含明文业务内容，但存在可观测的协议协商元数据；后者负载被加密，但 TCP 段长度序列仍保留内容类型相关的统计侧信道。

作者提出 2P2F 方法：在握手阶段，从 Client Hello 和 Server Hello 的 TLS 扩展字段中提取原始扩展信息，转成 16×28 灰度图，用 CNN 提取应用相关特征；在安全数据传输阶段，提取前 32 个 TCP data segment 长度，用 Transformer 建模序列模式，提取内容相关特征；最后用注意力机制融合两类特征，完成应用类型、内容类型以及应用-内容联合分类。

论文的实际贡献不在于单独发明 CNN、Transformer 或注意力机制，而在于把 TLS 协议生命周期拆成两个语义阶段，并让模型结构与阶段可见信息匹配。这使得方法比直接把整条流丢给一个通用模型更有解释性。

## 3. 论文解决的具体问题

论文面对的是加密流量分类中的细粒度识别问题，目标是在不解密、不查看应用负载的前提下，对 TLS/SSL 会话级流量进行分类。

它不仅识别“来自哪个应用”，例如 Baidu、Bilibili、TouTiao，也识别“传输什么内容类型”，例如 image、audio、radio、live video、video；更进一步，识别二者组合，例如 “Baidu-video” 或 “Bilibili-live video”。

作者认为既有方法的问题主要有三类：

1. 传统端口和 DPI 方法在加密流量上失效。
2. 传统机器学习依赖人工特征，泛化性和维护成本较差。
3. 深度学习方法虽然能自动提取特征，但常把整条加密流看成一个整体，忽略 TLS 协议自身的阶段差异。

因此，本文要解决的不是单纯“提高准确率”，而是回答一个更具体的问题：TLS 流量不同阶段暴露的信息是否具有不同分类价值，能否用阶段专属模型提取并融合这些互补特征，从而提升加密流量细粒度分类效果？

## 4. 创新点深度提炼

第一，论文把加密流量分类问题重新组织为协议阶段建模问题。多数工作按 packet、flow、payload/header 或统计特征建模，而本文按 TLS 工作流程划分为握手阶段和安全传输阶段。这一划分更贴近协议语义。

第二，握手阶段不直接用人工统计特征，而是使用 TLS 扩展字段的原始字节表示。作者认为扩展字段包含客户端和服务器协商细节，例如扩展项、密码套件、协议能力等，这些信息与应用生态、客户端实现、服务器部署有关，因此适合应用类型识别。

第三，传输阶段放弃不可读的加密负载内容，转向 TCP 段长度序列。论文特别指出，IP 层分片会破坏原始 TCP segment 长度信息，因此需要从 TLS/record 解析和 TCP 重组角度恢复更接近传输语义的长度序列，而不是简单使用 IP packet length。

第四，模型结构与特征性质对应：CNN 处理固定二维化的扩展字段图像，Transformer 处理长度序列，注意力机制处理跨阶段融合。这种设计的解释性优于把所有特征拼接后交给一个黑盒分类器。

第五，论文不仅做了主实验，还做了长度混淆鲁棒性实验。传输阶段长度被随机 padding 或 256-byte block padding 后，transmission-only 模型显著下降，但融合模型仍能依靠握手阶段保持较好性能。这一实验强化了“两阶段互补”的论点。

## 5. 科学问题与研究假设

本文隐含的科学问题可以概括为：

1. TLS 握手阶段的可见元数据是否足以表达应用类型差异？
2. 安全传输阶段的 TCP segment length sequence 是否足以表达内容类型差异？
3. 两个阶段的特征是否互补，而不是冗余？
4. 注意力融合是否优于简单拼接、独立分类后组合或单阶段建模？
5. 在长度侧信道被扰动时，握手阶段是否能为整体模型提供鲁棒性补偿？

对应的研究假设是：

- H1：TLS 扩展字段中存在应用相关模式，适合应用类型分类。
- H2：加密后的内容虽然不可见，但不同内容类型会留下不同长度序列模式。
- H3：应用识别和内容识别依赖不同阶段的信息，单阶段特征无法达到最优。
- H4：注意力机制能够动态调节两阶段特征贡献，因此优于简单结果拼接。
- H5：当传输阶段长度特征被 padding 削弱时，握手阶段特征可以缓解性能退化。

## 6. 科学方法与技术路线

2P2F 的技术路线可以拆成四层。

第一层是流量预处理。原始 pcap 按五元组切分 session flow，并根据 TLS 协议类型区分握手阶段和安全数据传输阶段。实验中还使用 SplitCap 按 TCP/UDP 划分流量，并选取访问特定网站时最大的 SSL/TLS session flow 作为分类对象，以降低背景流量干扰。

第二层是两阶段特征抽取。握手阶段抽取 Client Hello 和 Server Hello 中的 TLS extension field，转成十六进制，再形成 16×28 灰度图。Server Name 字段可能被伪造，因此被置零。传输阶段抽取安全数据传输阶段前 32 个 TCP data segment length，形成长度序列。

第三层是阶段内特征精炼。握手扩展字段图像交给 CNN，利用局部结构捕捉协议字段分布模式。TCP 段长度序列交给 Transformer，利用自注意力建模序列中不同位置之间的依赖关系。

第四层是跨阶段融合。论文用 CNN 输出作为 query/key 来源，用 Transformer 输出作为 value 来源，计算 attention fused feature，再输入分类器得到最终标签。这个设计意味着融合模块更偏向让握手侧特征决定“关注什么”，再从传输侧特征中取值补充内容模式。

## 7. 实验设计与实验步骤

可复核流程如下。

1. 数据  
   使用三个数据集：自建 2P2F Website Dataset、CIC IoT 2022、mobile app dataset。自建数据集来自 CENI-HeFei 平台，包含 Bilibili、TouTiao、Himalaya、Netease cloud、Baidu 五类应用，内容类型包括 image、audio、radio、live video、video，总规模约 175.8GB。训练测试比例为 8:2。

2. 预处理  
   从 pcap 出发，先用 SplitCap 按传输层协议划分 TCP/UDP；再按五元组切分 session flow；针对一次网站访问产生的多个 session flow，选择最大的 SSL/TLS session flow；用 Scapy 解析 TLS packet 的 handshake layer 和 record layer 类型，划分握手阶段与安全传输阶段；对被 IP 分片影响的流量进行合并，恢复 TCP segment length。

3. 特征构造  
   握手阶段：抽取 Client Hello 和 Server Hello 的 TLS 扩展字段，server name 内容置零，转十六进制并映射为 16×28 灰度图。  
   传输阶段：抽取安全数据传输阶段前 32 个 TCP data segment length，作为序列特征。  
   明确排除 IP 地址和包到达间隔等易受 CDN、负载均衡、网络状态影响的特征。

4. 模型与基线  
   2P2F 使用 CNN + Transformer + attention fusion。  
   对比方法包括 CCIT、FS-Net、FlowPrint、DE-GNN。  
   变体包括 2P2F-handshake、2P2F-transmission、2P2F-assoc、2P2F-fuse 等。

5. 训练  
   CNN 和 Transformer 分别对两阶段特征进行离线预训练或训练，融合模型再进行最终分类。环境为 PyTorch 2.0、CUDA 11.8、Ubuntu 16.04，硬件包括 Intel CPU、NVIDIA GPU。

6. 指标  
   使用 accuracy、precision、recall、F1-score 等指标。核心报告关注 F1，因为联合应用-内容分类存在多类别细粒度混淆，F1 更能反映整体分类质量。

7. 消融与敏感性  
   消融实验比较 handshake-only、transmission-only、feature fusion。  
   特征有效性实验比较 TLS 扩展字段、TCP segment length sequence 以及其他候选特征。  
   鲁棒性实验模拟 random padding 和 256-byte block padding，观察长度混淆对模型的影响。  
   时间开销实验比较 2P2F 与 DE-GNN 的预处理、特征提取和推理耗时。

8. 结果核查  
   通过主表结果验证 2P2F-fuse 是否优于单阶段模型和外部基线；通过混淆矩阵检查具体类别误分是否集中在语义相近类别；通过 padding 实验检查模型是否过度依赖长度侧信道；通过时间开销检查方法是否具备在线部署可能。

## 8. 关键结果、结论与证据

最关键的结果是：在 2P2F Website 数据集上，handshake-only 的 F1 约为 0.82，transmission-only 的 F1 约为 0.90，而完整 2P2F-fuse 达到约 0.96。这说明两阶段特征不是简单重复，而是存在互补。

应用类型分类中，握手扩展字段比传输阶段长度序列更有效。这符合直觉：TLS 扩展字段体现客户端、服务端、协议协商栈和应用部署差异，更接近“是谁”的问题。

内容类型分类中，TCP segment length sequence 更有效。这也符合网络侧信道分析逻辑：视频、音频、图片、文本等内容在分块大小和传输节奏上会留下不同形态，即使内容本身被加密。

应用-内容联合分类中，注意力融合优于简单组合。论文中 2P2F-fuse 在多任务细粒度识别上优于直接把应用分类和内容分类结果拼起来，也优于概率相加式组合。

混淆矩阵显示，误分主要发生在语义或传输形态相近的类别之间，例如 Bilibili radio 与 Bilibili live、Baidu image 与 Baidu video。这类误差说明模型确实在捕捉应用和内容模式，但边界类别仍受内容形态相似性影响。

鲁棒性实验中，block padding 会使 transmission-only F1 从约 0.90 降到约 0.59，但 2P2F-fuse 仍保持约 0.88。这个结果很重要，因为它说明融合模型不是完全依赖长度侧信道；当传输阶段被扰动，握手阶段仍能承担一部分识别任务。

时间开销方面，2P2F 平均每条流预处理和特征提取约 4.82 ms，模型推理约 0.91 ms，总体明显低于 DE-GNN。相比需要构建 Traffic Interaction Graph 的 GNN 方法，2P2F 的工程复杂度和在线成本更低。

## 9. 局限性与待解决问题

第一，方法仍然依赖可见 TLS 握手元数据和长度侧信道。随着 Encrypted Client Hello、QUIC、HTTP/3、padding、traffic shaping 的普及，握手和长度特征的可见性或稳定性可能下降。

第二，论文虽然做了 padding 鲁棒性实验，但主要是受控模拟。真实网络中的混淆机制可能更复杂，例如自适应 padding、批量发送、代理转发、CDN 策略变化、浏览器版本变化、移动网络波动等。

第三，自建数据集虽然规模较大，但应用和内容类别仍有限。五个应用、若干内容类型不足以证明方法在开放世界流量中的泛化能力。真实部署还会遇到未知应用、未知内容类型和长尾类别。

第四，选择“最大 SSL/TLS session flow”可以降低背景流量干扰，但也可能引入实验偏置。实际页面加载通常包含多个第三方域名、广告、CDN、API 请求和并行连接，最大流不一定总是最能代表用户访问行为。

第五，论文把 server name 字段置零以避免伪造或直接泄漏标签，这是合理处理；但 TLS 扩展字段中仍可能包含与特定客户端/服务器实现高度相关的环境指纹。模型学到的可能部分是采集环境、浏览器栈或服务器部署特征，而不完全是应用本质特征。

第六，正文包未截断，本次理解基于完整提供正文。但若用于正式复现或引用，仍建议回到 PDF 核查表格中的具体数值、CNN/Transformer 参数表细节和图中混淆矩阵数值。

## 10. 与本项目的关系

这篇论文与“异常检测”和“AI 安全跨域检测”项目关系较强，原因在于它提供了一种可解释的加密流量表征思路。

对异常检测来说，2P2F 的价值不只是分类应用或内容，而是提供了一套“协议阶段分治”的特征工程框架。握手阶段可用于识别客户端/服务端协商异常、伪装应用、异常 TLS 指纹；传输阶段长度序列可用于识别内容行为异常、隧道流量、恶意 C2 通信、异常数据外传。

对加密恶意流量检测来说，2P2F 可以改造成二分类或多分类恶意检测框架：握手分支学习 TLS 指纹，传输分支学习通信行为，融合层判断是否偏离正常应用-内容模式。

对本项目综述写作来说，这篇论文适合作为“从单流整体建模到协议阶段感知建模”的代表工作。它比一般 CNN/RNN/Transformer 流量分类论文更适合作为方法论案例。

## 11. 代码对照分析

本地信息显示该论文“已有代码状态：未发现；无”，因此不能把论文方法对应到真实源码文件。下面只能给出复现时应有的代码结构与运行线索，而不是对已存在代码的断言。

如果复现 2P2F，代码通常应分为四部分：

- 数据预处理：可能对应 `preprocess.py`、`split_flows.py`、`tls_parser.py`  
  负责读取 pcap，按五元组切分 session flow，调用 SplitCap 或等价逻辑，使用 Scapy 解析 TLS handshake/record 类型，区分握手阶段和传输阶段。

- 特征提取：可能对应 `extract_handshake.py`、`extract_sequence.py`、`dataset.py`  
  握手侧生成 16×28 extension-field grayscale image；传输侧提取前 32 个 TCP segment length；同时完成 padding、截断、归一化和标签构建。

- 模型定义：可能对应 `models/cnn.py`、`models/transformer.py`、`models/fusion.py`  
  CNN 对应握手扩展字段图像；Transformer 对应长度序列；fusion 模块实现 Q/K/V attention，并接分类头。

- 训练评估：可能对应 `train.py`、`evaluate.py`、`metrics.py`、`ablation.py`、`robustness_padding.py`  
  负责 8:2 划分，训练 2P2F-fuse 和各消融版本，计算 accuracy、precision、recall、F1，绘制混淆矩阵，并执行 random padding、block padding 鲁棒性测试。

运行依赖大概率包括 Python、PyTorch、CUDA、Scapy、SplitCap 或等效流切分工具。论文环境是 PyTorch 2.0、CUDA 11.8、Ubuntu 16.04。

## 12. 本篇精华

1. 2P2F 的核心不是“又用了 CNN 和 Transformer”，而是按 TLS 协议流程把加密流量拆成握手阶段和安全传输阶段，并分别建模。

2. 握手阶段的 TLS extension field 更适合识别应用类型，因为它携带协议协商、客户端能力和服务端配置痕迹。

3. 安全传输阶段的 TCP segment length sequence 更适合识别内容类型，因为不同内容会留下不同长度分布和序列模式。

4. IP packet length 不如 TCP segment length 可靠，因为 IP 分片会损失原始传输语义；论文强调要合并分片并恢复 TCP 段长度。

5. 注意力融合使应用相关特征和内容相关特征互补，2P2F-fuse 明显优于 handshake-only 和 transmission-only。

6. padding 实验是论文较有价值的补充：长度侧信道被削弱时，单传输分支大幅下降，而融合模型仍可依靠握手特征维持性能。

7. 方法的主要风险是上下文过拟合：模型可能学习到浏览器、TLS 栈、CDN、采集环境或服务器部署特征，而不完全是应用/内容本质。

8. 对异常检测项目而言，这篇论文可借鉴为“协议语义阶段 + 行为侧信道 + 融合判别”的加密流量建模范式。

## 13. 建议精读路线

第一遍读 Introduction 和 Preliminaries，重点抓住作者为什么反对“把整条加密流当作同质序列”。这一点是全文方法论基础。

第二遍读 Section IV，画出 2P2F 数据流：pcap → session flow → handshake extension image / TCP segment length sequence → CNN / Transformer → attention fusion → classifier。

第三遍精读 Feature Extraction，尤其是 server name 置零、排除 inter-arrival time、排除 IP 地址、恢复 TCP segment length 这些工程选择。这些细节决定方法是否真正可复现。

第四遍读实验部分，按“主结果、单阶段消融、特征有效性、联合分类、padding 鲁棒性、时间开销”六组实验整理证据链。

第五遍带着批判问题重读：如果换成 QUIC/HTTP3、ECH、强 padding、跨浏览器、跨时间、跨网络环境，2P2F 还能保留多少性能？这部分适合写进综述中的局限与未来方向。