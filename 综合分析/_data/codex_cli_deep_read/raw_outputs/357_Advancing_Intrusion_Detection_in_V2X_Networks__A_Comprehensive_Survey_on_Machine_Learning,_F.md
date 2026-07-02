# [357] Advancing Intrusion Detection in V2X Networks: A Comprehensive Survey on Machine Learning, Federated Learning, and Edge AI for V2X Security

## 1. 基本信息

- **中文题名**：推进 V2X 网络入侵检测：面向 V2X 安全的机器学习、联邦学习与边缘 AI 综合综述
- **作者**：Shimaa A. Abdel Hakeem, HyungWon Kim
- **年份 / 来源**：2025，IEEE Transactions on Intelligent Transportation Systems，Vol. 26, No. 8，pp. 11137-11205
- **DOI**：10.1109/TITS.2025.3558849
- **论文类型**：综述论文，不是单一算法或系统论文
- **主题定位**：V2X / CAV / IoV 场景下的入侵检测、误行为检测、对抗鲁棒性、联邦学习、边缘 AI、数据集与真实部署
- **代码状态**：未发现该论文对应的本地开源代码；本地检索到的若干泛 V2X 仓库与题名/DOI无直接对应关系。

## 2. 中文翻译与核心摘要

这篇论文的核心不是提出一个新的 IDS 模型，而是把 V2X 入侵检测从“算法准确率比较”提升到“可部署安全体系”的层面来梳理。作者认为，V2X 网络具有高移动性、低时延、安全关键、分布式、多通信协议并存等特征，传统集中式 IDS 和普通 ML-IDS 在这里会遇到隐私泄露、通信开销、算力不足、误报率高、对抗攻击脆弱、真实部署不稳定等问题。

论文围绕三条主线展开：第一，系统梳理 V2X 传统攻击、AI 驱动攻击、误行为检测与 ML/DL IDS 方法；第二，重点评估数据集和基准，指出 VeReMi、ROAD、CICIDS2017、ToN-IoT、UNSW-NB15 等各有覆盖盲区，单一数据集无法支撑 V2X 零日攻击评估；第三，讨论联邦学习、边缘 AI、分布式传感器融合、区块链、后量子密码和 XAI 如何支撑下一代 V2X IDS 的隐私保护、实时性和可信部署。

## 3. 论文解决的具体问题

论文要解决的具体问题可以概括为：**如何在真实 V2X 网络中构建既准确、低误报、低时延，又隐私保护、可扩展、能抵抗对抗攻击的 IDS/MDS。**

更具体地说：

- **传统误行为检测不够用**：RSSI、到达角、物理一致性、规则检查、协作信任等方法依赖诚实多数、环境理想、传感器可信或固定规则，面对合谋、位置偏移、Sybil、传感器操纵和动态交通时容易失效。
- **集中式 ML-IDS 不适合大规模 V2X**：车辆持续上传原始数据会带来隐私风险、带宽压力、云端时延和单点故障。
- **现有数据集不支撑真实泛化**：V2X 专用数据集覆盖车载误行为但网络攻击类型不足；通用 IDS 数据集攻击丰富但缺少 BSM、GPS、CAN、V2V/V2I 语义。
- **高准确率不等于可部署**：很多模型在仿真中接近 99% 准确率，但没有验证 NLOS、天气、城市遮挡、节点高密度、硬件算力、OTA 更新和通信拥塞。
- **AI IDS 本身会被攻击**：FGSM、PGD、策略渗透、数据投毒、标签翻转、模型反演、梯度泄漏等会破坏检测模型或 FL 聚合过程。

## 4. 创新点深度提炼

这篇综述的创新主要体现在“综述视角的扩展”，而不是某个算法公式。

1. **把 V2X IDS 综述从算法清单推进到部署约束分析**  
   作者不只列 SVM、RF、CNN、LSTM、GAN、Transformer，而是持续追问这些方法在车辆、RSU、MEC、云之间如何部署，延迟、能耗、通信开销和可扩展性是否可接受。

2. **把数据集作为核心科学问题处理**  
   论文详细区分 V2X 专用数据集与通用网络 IDS 数据集，指出 VeReMi 适合误行为检测但攻击类型窄，CICIDS2017/ToN-IoT/UNSW-NB15 攻击丰富但缺少 V2X 语义，因此提出“真实车联网数据 + 合成对抗攻击”的混合数据集方向。

3. **把对抗机器学习纳入 V2X IDS 主线**  
   论文讨论数据投毒、逃逸攻击、模型提取、FGSM、PGD、PIA、标签翻转、策略诱导等威胁，强调 AI-IDS 不是安全终点，而是新的攻击面。

4. **系统讨论 FL + Edge AI 的隐私保护 IDS 架构**  
   论文将 FedAvg、FedSGD、FedProx、层次化 FL、同态加密、差分隐私、安全多方计算、边缘推理放在同一框架下分析，适合 V2X 这种数据不能集中、又要求实时响应的场景。

5. **补入传感器融合、噪声和误报率问题**  
   论文特别强调 FAR、噪声、传感器漂移、结构化缺失、对抗扰动会直接影响 V2X 安全决策，提出分布式传感器融合、观察器冗余、去噪自编码器、动态阈值等方向。

6. **连接区块链与后量子密码**  
   区块链用于可信日志、身份、模型更新完整性；后量子密码和 QKD 用于未来 6G-V2X/FL 聚合安全。这个部分偏前瞻，但给出了长期安全路线。

## 5. 科学问题与研究假设

**科学问题**可以抽象为：

- 在高移动、低时延、资源受限、数据分散的 V2X 网络中，IDS 如何同时满足检测性能、隐私保护和实时部署？
- 如何构造能代表真实 V2X 攻击面的数据集，尤其覆盖零日攻击、AI 对抗攻击和跨协议攻击？
- 如何降低 anomaly-based IDS 的误报率，使其不会在真实交通波动中频繁误触发？
- 联邦学习是否能在不共享原始车载数据的条件下达到接近集中式训练的检测性能？
- 边缘 AI、传感器融合、区块链和后量子密码是否能组合成可落地的 V2X 安全体系？

**隐含研究假设**包括：

- ML/DL 模型比规则和签名方法更适合检测动态、未知和多样化 V2X 攻击。
- FL 能显著降低隐私风险和通信开销，但会带来模型聚合安全、非 IID 数据和通信同步问题。
- Edge AI 能降低检测时延，但必须依赖轻量模型、剪枝、量化或模型压缩。
- 单一数据集无法证明 IDS 的真实鲁棒性，跨数据集、真实测试床和混合攻击数据是必要条件。
- 对抗训练、鲁棒聚合、XAI 和多源传感器融合是降低误报和提升可信度的关键补充。

## 6. 科学方法与技术路线

论文采用结构化综述方法：先定义研究目标，再检索和筛选文献，最后按攻击、检测方法、数据集、架构、部署约束和未来方向建立分类体系。

技术路线大致如下：

1. **系统文献综述**：从 Google Scholar、Scopus、IEEE Xplore、SpringerLink、ACM Digital Library 等来源收集 300+ 篇相关论文，筛选出约 150 篇重点研究。
2. **V2X 基础建模**：梳理 V2V、V2I、V2N、V2P，IEEE 802.11p、LTE-V2X、5G/6G-V2X、IEEE 1609.x，以及 BSM、SPaT、MAP、EVA 等消息类型。
3. **攻击面分类**：覆盖 OBD、ECU、CAN、传感器、V2V/V2I 通信；攻击包括 DoS/DDoS、Sybil、Replay、Spoofing、Jamming、Eavesdropping、False Information、Timing、Privacy 等。
4. **IDS 分类**：按检测方法分为签名、异常、ML；按部署位置分为 HIDS、NIDS、Hybrid IDS；按架构分为集中式、分布式；按作用域分为 V2V/V2I/V2X IDS。
5. **ML/DL 方法分类**：监督、无监督、强化学习、深度学习、GAN、Autoencoder、LSTM、CNN、Transformer、FL、Edge AI。
6. **数据集评估**：从攻击覆盖、真实/仿真来源、特征粒度、是否适合 ML、是否支持零日攻击等维度比较数据集。
7. **真实部署分析**：将仿真结果与真实 OBU、Raspberry Pi、Jetson、MEC、RSU 等边缘部署案例对照，分析延迟、能耗、通信开销、误报和鲁棒性。

## 7. 实验设计与实验步骤

这篇论文自身是综述，不是单一实验论文；但它给出了一套可复核的 V2X IDS 评估流程，可按下面方式复现实验或设计新实验。

1. **数据**  
   选择 V2X 专用数据集与通用 IDS 数据集组合。V2X 侧包括 VeReMi、ROAD、VDDD、VDOS-LRS、VDoS、CAN-Intrusion、Car-Hacking、BurST-ADMA、真实 MK5 OBU flooding 数据等；通用侧包括 NSL-KDD、KDD Cup 99、CICIDS2017/2018、ToN-IoT、UNSW-NB15、X-IIoTID。

2. **预处理**  
   对 BSM/CAN/pcap/传感器日志做统一解析，抽取车辆 ID、位置、速度、加速度、时间戳、消息类型、流量统计、CAN ID、包间隔等特征；进行缺失处理、归一化、类别不平衡处理，如 SMOTE 或 class-weighted loss；可使用 PCA、LDA、Chi-square、Autoencoder 做特征选择或降维。

3. **模型 / 基线**  
   基线应包含传统合理性检查、签名 IDS、LR、SVM、KNN、Decision Tree、Random Forest、XGBoost、LightGBM；深度模型包含 CNN、LSTM、CNN-LSTM、Autoencoder、VAE、GAN、Transformer；分布式方案包含 FedAvg、FedSGD、FedProx、Hierarchical FL、Edge AI 推理。

4. **训练**  
   集中式训练用于上限对照；边缘训练在 RSU/MEC/车载设备上评估推理延迟；FL 训练由车辆或 RSU 本地更新模型，再由边缘或云端聚合。需要记录本地轮数、聚合轮数、客户端数量、非 IID 划分方式、通信量和掉线情况。

5. **指标**  
   不应只报 accuracy。必须同时报告 precision、recall、F1、AUC、TPR、TNR、FPR、FNR、FAR、per-attack detection rate、latency、communication overhead、energy cost、model size、training time 和 edge inference time。

6. **消融 / 敏感性**  
   检查集中式 vs FL vs Edge；仿真数据 vs 真实数据；单数据集 vs 混合数据集；有无 SMOTE；有无特征选择；不同攻击密度、车辆密度、噪声强度、非 IID 程度；FGSM/PGD/PIA/poisoning 下的鲁棒性；剪枝/量化后精度与延迟变化。

7. **结果核查**  
   高准确率必须用混淆矩阵、每类攻击指标、跨数据集测试、真实测试床或至少真实轨迹驱动仿真验证。特别要查是否存在数据泄漏、类别极不平衡导致的虚高准确率、同一场景训练测试重复、只检测单一攻击而泛化不足等问题。

## 8. 关键结果、结论与证据

论文汇总出的关键结论较清晰：

- **传统检测有价值但边界明显**：例如基于 RSSI 的物理层合理性检查在升级版 VeReMi 上达到约 95.91% precision、83.73% detection rate，但这类方法仍容易受位置欺骗、合谋和环境变化影响。
- **ML/DL IDS 在仿真中表现强，但泛化需谨慎**：多项工作报告 95%-99% 级检测效果，如 AE+LSTM-RNN 在合成 AVN 攻击中检测率约 95%、FAR 约 3%；stacked LSTM 在 AIoT-SoL 上 accuracy 约 99.8%。
- **FL 是 V2X IDS 的核心方向**：Korba 等 FL-based IDS 在 VDoS 场景中报告 accuracy/F1 约 99.99%、FPR 约 0.01%，并指出少量 CAV 参与训练即可接近集中式性能且缩短训练时间约 30%。
- **边缘部署能明显降低时延**：混合 edge-cloud 架构报告约 30% latency reduction、约 10% accuracy improvement，边缘响应约 22 ms，相比云端约 58 ms。
- **轻量化是可部署关键**：FED-IoV 将流量转图像并用 MobileNet-Tiny，在 CAN-Intrusion 和 CICIDS2017 上分别约 98.51% 和 97.74% accuracy，Raspberry Pi 4 上预测延迟低于 10 ms。
- **真实测试床正在补齐仿真缺口**：MK5 OBU flooding 数据集显示真实 V2V 条件下仍可取得较高 F1，但也暴露真实流量波动比仿真更复杂。
- **对抗鲁棒性不可忽略**：论文总结 adversarial training 可显著提升逃逸攻击鲁棒性，结论部分给出最高约 30% 的提升幅度，但真实 V2X 对抗数据仍不足。
- **未来 IDS 应是组合架构**：单一 ML 模型不够，作者倾向于 FL + Edge AI + Hybrid IDS + Sensor Fusion + Blockchain/PQC + XAI 的多层体系。

## 9. 局限性与待解决问题

- **综述不是统一实验基准**：论文比较了大量研究，但这些结果来自不同数据集、不同划分、不同攻击模型和不同硬件环境，数值不能直接横向排名。
- **数据集问题仍是最大瓶颈**：VeReMi、ROAD 等更贴近 V2X，但攻击覆盖有限；CICIDS2017、ToN-IoT、UNSW-NB15 攻击丰富但 V2X 语义不足；KDD/NSL-KDD 对现代 V2X 的代表性较弱。
- **真实部署验证不足**：大量工作仍依赖 NS-3、OMNeT++、Veins、SUMO、MOSAIC 等仿真环境，对城市遮挡、NLOS、天气、电磁干扰、车辆密度和硬件限制考虑不够。
- **FL 本身引入新攻击面**：模型投毒、Sybil 客户端、模型反演、成员推断、梯度泄漏、非 IID 数据和客户端掉线都可能破坏 FL-IDS。
- **区块链和后量子密码存在性能债务**：它们能增强完整性和长期安全，但会增加计算、通信、能耗和工程复杂度，尤其在车载设备上需要严肃评估。
- **误报率仍未彻底解决**：真实交通中的异常驾驶、传感器噪声、通信波动可能被误判为攻击，导致安全系统不可信。
- **正文截断说明**：本次消息中发送的正文包被截断。虽然本地 `full_text_cache_plain/357.txt` 能补读后续章节到结论和参考文献，但正式引用表格、图编号和精确数值时，仍需回到 PDF 复核被截断部分及原始排版。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”项目强相关，尤其适合作为综述和实验设计依据。

- 对**异常检测综述**：可直接提供 V2X/IoT/边缘安全场景下的攻击分类、IDS 分类、数据集分类和部署挑战。
- 对**开放集/零日检测**：论文反复强调现有数据集对 zero-day 覆盖不足，支持后续构造“已知攻击训练、未知攻击测试”的开放集协议。
- 对**多源异构融合**：V2X 场景天然包含 CAN、BSM、GPS、LiDAR、Radar、Camera、RSU、网络流量，适合借鉴为多模态异常检测问题。
- 对**联邦/边缘检测**：如果项目关注隐私保护或分布式部署，本篇可作为 FL-IDS、Edge AI、MEC/RSU 架构设计的入口文献。
- 对**实验规范**：它提醒不能只报 accuracy，而要把 FAR、FPR、latency、communication overhead、energy 和 cross-dataset generalization 纳入评估。

## 11. 代码对照分析

本地未发现这篇论文的官方代码包。检索索引中出现的若干 `V2X` 仓库只是名称泛匹配，README 与论文题名、DOI、作者和方法无直接对应关系，不能视为论文代码。

因此没有可对应的源码文件可以确认属于本文的：

- **数据预处理文件**：未发现。
- **模型定义文件**：未发现。
- **训练入口文件**：未发现。
- **联邦学习 / 边缘部署实现**：未发现。
- **评估脚本或复现实验配置**：未发现。

如果后续要按本文路线搭建复现工程，合理目录应包括：`datasets/` 处理 VeReMi、ROAD、CAN、CICIDS、ToN-IoT；`models/` 放 SVM/RF/XGBoost、AE、LSTM、CNN-LSTM、GAN；`fl/` 放 FedAvg/FedProx/HFL 聚合；`edge/` 放 Raspberry Pi/Jetson/RSU 推理脚本；`attacks/` 放 FGSM、PGD、poisoning、Sybil、DoS 生成；`eval/` 统一计算 FAR、F1、AUC、latency、communication overhead。

## 12. 本篇精华

- V2X IDS 的难点不是“能不能训练一个高准确率分类器”，而是能否在高移动、低时延、隐私受限、算力受限环境中稳定运行。
- 数据集是 V2X IDS 的根问题：V2X 专用数据集缺少广泛网络攻击，通用 IDS 数据集缺少车联网语义，混合数据集是必要方向。
- FL + Edge AI 是作者认为最现实的下一代 V2X IDS 架构，但必须解决非 IID、聚合安全、通信开销和边缘能耗。
- 误报率 FAR 在安全关键交通场景中比普通网络 IDS 更敏感，高误报会造成不必要制动、告警疲劳和系统失信。
- 对抗攻击已经从“攻击车辆网络”扩展为“攻击检测模型本身”，包括逃逸、投毒、策略诱导、模型反演和梯度泄漏。
- 真实部署必须核查延迟、带宽、算力、能耗、OTA 安全、legacy vehicle 兼容和 NLOS/天气/城市遮挡等因素。
- 未来可信 V2X IDS 更可能是组合系统：混合 IDS + 分布式传感器融合 + FL + Edge AI + XAI + 区块链/后量子密码。

## 13. 建议精读路线

1. 先读 Abstract、Introduction 和 I.B/I.C，抓住作者认为前人综述遗漏的点：数据集、对抗攻击、FL/Edge、真实部署、计算复杂度。
2. 再读 IV-VI，建立 V2X 通信模式、组件、传统攻击和 AI-based attack 的威胁模型。
3. 精读 VII-VIII，整理 IDS 分类和 ML/DL 技术谱系，可直接转成综述中的方法分类表。
4. 重点读 IX，这是对本项目最有价值的部分：数据集适用性、零日攻击覆盖不足、混合数据集建议。
5. 精读 X 和 XII，关注 FL/Edge AI 架构、真实部署、通信开销、边缘硬件、仿真与现实差距。
6. 最后读 XIII-XIV，把 future directions 提炼成自己的研究问题：真实 V2X 数据集、开放集攻击、低误报边缘检测、鲁棒 FL、可解释 IDS。