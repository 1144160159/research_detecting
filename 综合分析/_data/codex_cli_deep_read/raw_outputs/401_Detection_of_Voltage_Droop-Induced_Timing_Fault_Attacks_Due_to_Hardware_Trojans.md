# [401] Detection of Voltage Droop-Induced Timing Fault Attacks Due to Hardware Trojans

## 1. 基本信息

- 论文题名：Detection of Voltage Droop-Induced Timing Fault Attacks Due to Hardware Trojans
- 作者：Jonti Talukdar, Akshay Vyas, Krishnendu Chakrabarty
- 年份：2024
- 期刊：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems
- DOI：10.1109/TCAD.2024.3418395
- 主题定位：异构集成 chiplet 中由硬件木马诱发的 PDN 电压跌落、时序故障攻击与运行时异常检测
- 本地代码状态：未发现该论文对应的本地开源代码

## 2. 中文翻译与核心摘要

这篇论文研究的是一种非常具体但危险的硬件安全问题：在 2.5D/3D 异构集成系统中，攻击者可以在不可信 chiplet、第三方 IP、代工或封测环节中植入小面积、高开关活动的硬件木马，例如环形振荡器 RO 或 glitch-based power wasting circuit。当这些木马被触发时，会在片上电源分配网络 PDN 中制造额外电流突变，从而引起电压跌落。电压跌落会放大关键路径延迟，最终可能造成运行时的时序违例和功能错误。

论文的核心不是传统意义上的“网络流量异常检测”，而是硬件层面的时间序列异常检测：它先构建 RTL-to-GDSII 到 Voltus/Tempus 的 EDA 分析流程，评估 RO 木马对 chiplet PDN 的电压跌落影响，再用动态 workload 下的电压跌落时间序列训练卷积自编码器，检测木马触发导致的异常电压跌落模式。

一句话概括：论文把“硬件木马造成的 PDN 电压扰动”建模为一种可量化、可排序、可检测的运行时异常，并给出从版图、功耗、电压跌落、时序降额到机器学习检测的端到端框架。

## 3. 论文解决的具体问题

论文瞄准的问题是：现有 chiplet 安全方案多关注总线访问、内存隔离、NoC 协议、secure interposer 或 root-of-trust，却不足以覆盖通过电源网络发起的运行时故障攻击。

具体来说，它解决了三层问题：

1. 攻击可行性问题  
   小面积 RO 或 glitch 木马是否能在 chiplet 内制造足够明显的 PDN 电压跌落，并进一步影响正常功能路径的时序？

2. 易受攻击路径识别问题  
   给定一个 chiplet 设计、版图、PDN 和运行 workload，哪些功能路径最容易因为电压跌落出现 timing fault？仅看静态 slack 不够，因为路径是否危险还取决于路径经过的物理位置是否处在 voltage droop hotspot。

3. 运行时检测问题  
   如果木马只在功能运行期间随机触发，能否从电压跌落时间序列中识别异常？论文选择卷积自编码器，因为它可学习“正常 workload 下的 Vdroop 分布”，再用重构误差识别偏离正常模式的时间窗口。

## 4. 创新点深度提炼

第一，论文把 chiplet 安全攻击面从逻辑/协议层扩展到了 PDN 物理侧信道层。  
已有 root-of-trust 或 secure NoC 方案主要防止恶意 chiplet 访问非法地址、篡改共享内存或窃取互连数据，但无法阻止一个本地木马通过电源网络影响旁边或同一 chiplet 的功能逻辑。

第二，论文给出 RO 木马插入、版图实现、电压跌落仿真和时序降额的完整 EDA 流程。  
它不是只停留在抽象模型，而是使用 Synopsys Design Compiler、Cadence Innovus、Voltus、Tempus 和 ASAP 7nm 标准单元库，把 RTL 设计变成带 PDN 的版图，再做 post-layout 电压和时序分析。

第三，论文把“路径时序脆弱性”从纯 timing slack 扩展为 slack + 物理电压跌落的联合问题。  
一个路径原本不一定是最差 slack，但如果其单元经过高 Vdroop 区域，RO 激活后也可能成为更危险的路径。因此论文提出基于 instance-level Vdroop 的 timing deration 排名方法。

第四，论文把硬件木马检测转化为时间序列异常检测。  
卷积自编码器只用未攻击状态下的电压跌落序列训练，然后用重构误差阈值识别异常。这适合硬件安全场景，因为攻击样本通常稀缺，而正常运行数据更容易获得。

第五，论文没有只验证 RO 木马，还补充了 glitch-based power wasting Trojan。  
这增强了结论泛化性：检测框架捕捉的不是 RO 的特定结构，而是木马触发后造成的异常 PDN 动态行为。

## 5. 科学问题与研究假设

核心科学问题可以概括为：

- 在异构集成 chiplet 中，局部恶意开关活动能否通过 PDN 扩散为可导致时序错误的系统级扰动？
- 电压跌落对路径延迟的影响能否通过 post-layout、instance-level 分析可靠量化？
- 正常 workload 下的电压跌落时间序列是否具有可学习的稳定分布？
- 木马触发造成的异常 Vdroop 是否会在自编码器重构误差空间中与正常样本形成足够分离？

论文依赖几个重要假设：

- 供应链中存在不可信 COTS IP、foundry 或 OSAT，攻击者可通过 ECO 或版图级修改插入小型木马。
- RO 或 glitch 木马与功能逻辑共享 PDN，因此其电流突变会影响正常逻辑的供电。
- 功能 workload 可通过 Verilog testbench 和 VCD 近似真实运行场景。
- 正常与异常 Vdroop 时间序列分布存在差异，且这种差异大于工艺噪声、负载变化和正常 workload 波动带来的混淆。

## 6. 科学方法与技术路线

论文技术路线分成两条主线。

第一条是 presilicon 安全评估：

1. 从 FIR、IIR、3DES、MD5、JPEG 等 benchmark IP 出发。
2. 使用 Synopsys DC 综合 gate-level netlist。
3. 使用 Cadence Innovus 完成 floorplan、micro-bump assignment、place-and-route、PDN 插入。
4. 在布局中插入 RO-based Trojan。
5. 使用 Cadence Voltus 做静态或动态 voltage droop 分析。
6. 使用 Cadence Tempus 提取关键路径 timing report。
7. 对路径上每个 cell instance 结合其 worst-case Vdroop 计算 timing deration。
8. 得到最容易发生 voltage droop-induced timing failure 的路径排名。

第二条是运行时异常检测：

1. 从动态 workload 中采集 Vdroop 时间序列。
2. 用无木马激活的正常数据训练卷积自编码器。
3. 将序列按滑动窗口切成长度 16 的样本。
4. 用训练集最大重构误差作为异常阈值。
5. 引入连续历史窗口约束，减少单点误报。
6. 在不同 Trojan 数量、不同 workload、不同 IP 上评估 accuracy、false positive 和 test escape。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 CEP 和 OpenCores 中的 FIR、IIR、3DES、MD5、JPEG IP。论文列出这些 chiplet 的标准单元数、pin 数、版图尺寸和面积，其中 JPEG 最大，3DES 最小。

2. 预处理  
   对每个 IP 构建功能 workload。论文定义 busy、bursty 和 mixed 三类模式。busy 表示连续输入事务；bursty 表示功能输入中穿插低开关活动阶段；mixed 则混合 busy 和 bursty，用于更一般的运行场景。动态功耗分析使用 Verilog testbench 生成 VCD。

3. 模型/基线  
   安全评估部分的“模型”是 EDA 物理分析链：Innovus + Voltus + Tempus。异常检测部分使用卷积自编码器，没有依赖有监督攻击分类器。

4. 训练  
   自编码器只在正常 Vdroop 时间序列上训练。每个 IP、每种 workload 各训练一个模型。训练序列长度为 500，窗口大小为 16，stride 为 1，训练 150 epoch，学习率 0.001。

5. 指标  
   timing 安全评估看 100 条 worst timing paths 的平均延迟退化、标准差和 timing violation 数量。异常检测看 accuracy、false positive 和 test escape。

6. 消融/敏感性  
   论文改变 RO Trojan 数量，从少量到 30 个，观察 Vdroop 和 timing degradation 的增长趋势。还比较 RO-based Trojan 与 glitch-based Trojan，并分析 3、5、7、15 个 Trojan 时正常/异常重构误差分布的分离情况。

7. 结果核查  
   关键核查点包括：Vdroop 是否随 Trojan 数量增加而上升；路径延迟退化是否随 Vdroop 增大；是否出现 timing violation；自编码器阈值是否能把正常与异常重构误差分开；低 Trojan 数量时 false positive 是否增加。

## 8. 关键结果、结论与证据

论文最重要的结论是：少量 RO 木马就可能造成可观的时序退化。文中指出，单个 RO Trojan 可在关键路径上引入约 0.5% 到 0.8% 的平均退化；当 Trojan 数量增加到 3 或 5 时，退化接近 1.5%；部分 IP 在 5 个 Trojan 左右开始出现 timing violation。

第二，Vdroop 与物理位置高度相关。FIR case study 显示，离 PG pin 更远的区域电压跌落更严重，热点区域可能成为时序故障高风险区域。

第三，路径脆弱性不能只看原始 slack。某些路径本来未必是最关键路径，但如果路径中的 cell 落在高 Vdroop 区域，攻击触发后会变得更危险。

第四，卷积自编码器能有效检测电压跌落异常。训练集重构误差阈值在 FIR、3DES 等 IP 上能较好分开正常和异常样本；多个测试场景下误报和漏检均较低。对 glitch-based Trojan 的实验也显示，在 5 和 7 个 Trojan 场景下检测效果较强。

第五，PG pin 增强是一种可行缓解方向。论文展示 FIR chiplet 中增加 PG pin 后，worst-case Vdroop 更低且分布更均匀，说明 PDN 设计本身可以作为安全加固手段。

## 9. 局限性与待解决问题

这篇论文的局限主要在四方面。

第一，实验仍主要是 presilicon EDA 仿真，缺少真实硅片测量验证。Voltus/Tempus 分析可信度高，但实际芯片中的工艺波动、封装寄生、电源噪声、温度变化和老化效应可能改变异常分布。

第二，威胁模型偏强。论文假设攻击者能在 chiplet 内插入 RO 或 glitch 木马并控制触发条件，这在不可信供应链场景合理，但不同供应链阶段的实际可操作性仍需更细粒度讨论。

第三，异常检测依赖传感与采样假设。论文说明从 timing critical paths 相关标准单元采样 Vdroop，但实际部署中需要片上传感器、采样带宽、位置选择、读出开销和安全可信采集链路。

第四，低 Trojan 数量下正常与异常分布尾部重叠更明显。论文自己也指出 3 个 Trojan 场景下 false positive 更高，这意味着检测阈值和历史窗口策略需要结合具体安全代价调参。

第五，跨 chiplet 和 active interposer 的共享 PDN 攻击仍是未来工作。论文主要关注同一 chiplet 内的恶意修改，对多 chiplet 耦合、interposer Trojan、跨域电源扰动传播还没有充分展开。

本次正文包标注为未截断，因此上述理解基于完整提供文本；若后续用于正式综述或复现实验，仍建议回到 PDF 核对图表、表格数值和版面细节。

## 10. 与本项目的关系

虽然已有粗分类写作“恶意流量、暗网与攻击检测”，但这篇论文更准确的归属应是硬件安全、供应链安全、运行时异常检测和侧信道故障攻击检测。

它与异常检测项目的关系很强，原因在于它提供了一个非网络域的异常检测范式：不是检测包流量、日志或行为序列，而是检测芯片 PDN 的物理时间序列。其思路对本项目有三点借鉴价值：

- 异常并不一定表现为语义层事件，也可能表现为底层资源扰动。
- 自编码器适合“正常样本多、攻击样本少”的安全检测场景。
- 检测模型需要和威胁机理绑定，不能只看算法指标；本论文把 Vdroop、timing deration 和 timing violation 连接起来，增强了异常检测结果的物理解释性。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此不能给出源码级逐文件对应关系。

但若未来获得代码或复现实验，目录大概率应与论文流程对应为以下几类：

- 数据预处理  
  可能包含 benchmark RTL、Verilog testbench、workload stimulus 生成脚本、VCD 生成流程。对应论文 Section V-C 的 busy、bursty、mixed workload 构造。

- 版图与 PDN 构建  
  可能包含 Synopsys DC 综合脚本、Cadence Innovus floorplan/place-route/PDN insertion 脚本、ASAP7 library 配置。对应 Section IV。

- Trojan 插入  
  可能包含 RO netlist、glitch Trojan netlist、ECO 插入脚本、enable/reset 连接逻辑。对应 Section III 和 Section VII-A。

- 电压跌落与时序分析  
  可能包含 Cadence Voltus rail analysis 脚本、Tempus timing report 解析脚本、instance-level Vdroop 与 timing path 映射脚本。对应 Section V-A/V-B。

- 异常检测模型  
  可能包含 Python/PyTorch 或 TensorFlow 的 convolutional autoencoder、滑动窗口构造、训练阈值计算、false positive/test escape 统计。对应 Section VI。

由于没有代码包，本文的可复现障碍主要不是算法本身，而是商业 EDA 工具链、ASAP7 PDK 配置、benchmark RTL 和 Voltus/Tempus 报告格式的可获得性。

## 12. 本篇精华

- 这篇论文的核心贡献是把 chiplet 硬件木马攻击从逻辑篡改扩展到 PDN 电压跌落诱发的运行时时序故障。
- RO 木马面积小、开关活动强、容易伪装成正常片上传感/监控结构，是异构集成供应链中的现实威胁。
- 电压跌落风险不是纯逻辑问题，而是 workload、物理位置、PDN 结构和 timing slack 的耦合问题。
- 论文提出的路径排序方法很有价值：用 instance-level Vdroop 对关键路径做 timing deration，从而找出最脆弱路径。
- 自编码器检测有效的原因在于正常 Vdroop 序列可形成稳定分布，木马触发后的重构误差明显偏离。
- 低强度攻击更难检测，正常/异常分布尾部重叠会带来误报或漏检，这是部署时必须处理的问题。
- PG pin 增强说明安全防护不一定只靠检测模型，也可以通过 PDN 物理设计降低攻击可行性。
- 对异常检测综述而言，这篇文章是“物理层时间序列异常检测 + 可解释攻击机理”的好案例。

## 13. 建议精读路线

建议按以下顺序读：

1. 先读 Introduction 和 Threat Model，明确论文为什么认为 bus-level RoT 不足以覆盖 PDN 攻击。
2. 再读 Section III，理解 RO 木马如何制造 Vdroop，以及路径延迟为何会随供电下降而增加。
3. 精读 Section IV 和 Fig. 5/Fig. 6，掌握 RTL-to-GDSII、PDN 插入、Voltus 分析的完整流程。
4. 重点读 Section V，尤其是 timing deration 和 path ranking，这是论文最有硬件安全特色的部分。
5. 再读 Section VI，关注自编码器的输入窗口、阈值选择和历史窗口抑制误报策略。
6. 最后读 Discussion，特别是 glitch Trojan 泛化实验和 PG pin mitigation，这部分决定论文方法能否从“检测”走向“防护”。