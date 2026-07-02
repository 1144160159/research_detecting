# [696] Hardware-Aware Neural Architecture Search for Encrypted Traffic Classification on Resource-Constrained Devices

## 1. 基本信息
题名可译为：面向资源受限设备的加密流量分类硬件感知神经架构搜索。

作者来自意大利热那亚大学 SEALab，发表于 2026 年 `IEEE Transactions on Network and Service Management`，DOI 为 `10.1109/TNSM.2026.3666676`。论文主任务是加密流量分类，重点不是云端高精度模型，而是能在 STM32 级 MCU 上部署的会话级轻量模型。

正文包本地可见且未截断。代码元数据中 `source\ProtectIT` 标记为 failed，但实际本地存在 `source\ProtectIT_Unige`，包含预处理和 NAS 核心代码。

## 2. 中文翻译与核心摘要
这篇论文的核心意思是：在加密流量占主导、DPI 与端口识别失效的环境下，边缘/IoT 设备也需要做实时流量识别，但已有深度模型大多只追求准确率，参数量、FLOPs、RAM 峰值激活都不适合微控制器部署。

作者用硬件感知 NAS 搜索一个 1D CNN，会话输入为固定长度原始字节序列。最终模型在 ISCX VPN-nonVPN 主任务上达到 `96.60%` accuracy、`96.63%` F1，同时只有 `88.26K` 参数、`10.08M` FLOPs、`20.12K` 最大中间张量。它牺牲了少量准确率，换来数量级的资源下降，并通过多任务、跨数据集、预处理策略、会话长度缩减、INT8 量化和 STM32 实测证明可部署性。

## 3. 论文解决的具体问题
论文解决的是一个很具体的工程科学问题：如何在不解密、不依赖手工统计特征的情况下，把会话级加密流量分类模型压到 MCU 可承受的 Flash、RAM 和计算预算内。

传统方法的问题是三层叠加：加密让 DPI 失效，端口号不可靠；经典 ML 依赖人工统计特征，迁移和维护成本高；深度模型虽然能吃原始字节，但模型和激活张量太大，无法在 Nucleo-F401RE 这类 512KB Flash、96KB RAM 的设备上运行。

作者选择会话级而不是包级，是因为会话能保留双向通信行为；选择 1D CNN 而不是 LSTM/Transformer，是因为卷积的局部连接和权值共享更符合 MCU 计算约束。

## 4. 创新点深度提炼
第一，论文把硬件约束前置到架构搜索，而不是训练好大模型后再压缩。搜索时同时限制参数量、FLOPs 和最大中间张量，这三个量分别对应 Flash、计算延迟/能耗和 RAM 峰值。

第二，搜索对象是会话级加密流量原始字节分类模型。它不是统计特征模型，也不是图像化后套大 CNN，而是在 784 字节会话向量上搜索 1D CNN block 组合。

第三，论文没有只报一个 accuracy，而是系统分析了头部字段预处理和会话长度。24 种 header-level 策略说明了隐私保护和准确率之间的实际冲突，196 到 784 字节长度实验说明了早期会话字节的信息密度。

第四，作者做了真正的嵌入式闭环：Float32 搜索、INT8 PTQ/QAT、STM32Cube.AI 转换、Cortex-M4/M7 延迟与能耗实测。这一点比很多“轻量化”论文更接近部署。

## 5. 科学问题与研究假设
科学问题可以表述为：加密流量的可判别结构是否主要存在于会话早期字节、包头结构和时序排列中，并且能否用受硬件约束的 1D CNN 提取出来。

论文隐含了几个假设：会话级原始字节包含足够的应用/类别指纹；硬件约束纳入 NAS 后，比人工设计或事后压缩更容易得到可部署模型；适度删除或匿名化敏感头部字段不会摧毁分类性能；缩短会话长度能显著降低 FLOPs 和张量峰值，但存在过度截断的拐点；在 ISCX 上找到的结构具有跨数据集迁移能力。

## 6. 科学方法与技术路线
技术路线是：PCAP 原始流量先按双向五元组抽取 session，过滤无载荷控制包和 DNS，处理 MAC/IP/端口/UDP padding，再截断或补零到固定长度，字节归一化到 `[0,1]`。

模型搜索空间由多个 1D CNN block 组成，每个 block 可变 filters、kernel、stride、padding、pooling 类型、pool size、dropout。末端使用 Global Average Pooling 和 Dense softmax。NAS 采用演化搜索：从父架构出发，每代生成若干子架构，对 block 做添加、删除或参数变异，先过硬件约束，再训练并按验证准确率选下一代父架构。

硬件约束设为 `120K` 参数、`22K` 最大 tensor、`11M` FLOPs，对应 Nucleo-F401RE 的 Flash/RAM/频率边界。最终再对同一架构做多任务重训、跨数据集测试、预处理消融、输入长度消融、INT8 量化和 MCU 实测。

## 7. 实验设计与实验步骤
可复核流程如下：

1. 数据：主数据集为 ISCX VPN-nonVPN，约 30GB、11 类；外部泛化用 USTC-TFC2016，约 4GB、20 类，以及 QUIC NetFlow，约 120GB、5 类。主任务包括 VPN-NonVPN、VPN-Diff、VPN-Type、NonVPN-Type、Traffic-Cat、App-ID。

2. 预处理：用 Scapy 读取 PCAP，按双向 session 聚合，去除无效控制包和 DNS；执行 MAC 移除/置零/匿名化、IP 匿名化/置零、端口置零、UDP padding 等策略；统一到 784 字节，并测试 676、576、484、400、324、256、196 字节。

3. 模型/基线：候选模型是硬件约束下的 1D CNN；对比对象包括 session、packet、flow、hybrid 输入的 SOTA 模型，比较 accuracy、F1、参数量、FLOPs、最大 tensor。

4. 训练：NAS 在 ISCX 的 VPN-NonVPN 上执行，20% 训练数据作验证，最多 100 epoch，初始学习率 `1e-3`，batch size `128`，plateau 降学习率，early stopping，3 次 multi-start。搜索为 100 代、每代 10 个可行子模型、每个子模型 2 次随机变异、最大深度 5。

5. 指标：分类指标为 accuracy、F1，部分代码也计算 weighted precision/recall；硬件指标为参数量、FLOPs、最大中间张量、Flash/RAM 估计、MCU 延迟和能耗。

6. 消融/敏感性：24 种头部预处理策略，8 种输入长度，Float32/PTQ/QAT 三种量化配置，Cortex-M4 与 Cortex-M7 两类 MCU。

7. 结果核查：同一架构需同时满足主任务精度、外部数据集泛化、硬件阈值、量化后精度保持、真实 MCU 延迟能耗这五组证据。

## 8. 关键结果、结论与证据
主任务 VPN-NonVPN 上，模型达到 `96.60%` accuracy 和 `96.63%` F1，但只有 `88.26K` 参数、`10.08M` FLOPs、`20.12K` 最大 tensor。相对部分 SOTA，参数最多降 `444x`，FLOPs 最多降 `312x`，tensor 最多降 `15x`。

多任务结果显示它不是只适配一个标签空间：VPN-Diff 为 `99.86%`，VPN-Type 为 `99.14%`，NonVPN-Type 为 `94.04%`，Traffic-Cat 为 `96.74%`，App-ID 为 `94.18%` accuracy、`94.42%` F1。

泛化结果也强：USTC-TFC2016 达到 `99.73%` accuracy/F1，QUIC NetFlow 达到 `99.98%` accuracy/F1。预处理方面，NAS 使用的 Strategy 2 约 `96.59%`，最激进的 Strategy 24 降到 `89.08%`，说明过度置零会破坏结构信息。长度方面，784 到 196 字节使 FLOPs 从 `10.08M` 降到 `2.24M`，最大 tensor 从 `20.12K` 降到 `4.90K`，多数策略只损失约 1 到 2 个百分点。

部署方面，QAT 后 INT8 基本贴近 Float32，差距约 `0.1%` 到 `0.3%`。784 字节输入时，Cortex-M4 为 `115.4 ms`、`28.85 mJ`，Cortex-M7 为 `31.43 ms`、`7.86 mJ`；324/484 字节被论文认为是更好的准确率、延迟、能耗折中点。

## 9. 局限性与待解决问题
这不是异常检测论文，而是监督式加密流量分类论文。它对本项目有方法价值，但不能直接解决未知攻击、开放集检测、概念漂移或告警解释问题。

部署实验只评估 MCU 侧推理，session 聚合、PCAP 捕获、缓冲和预处理假设由上游网关完成，这部分开销没有纳入端到端实时性。硬件约束主要用参数量、FLOPs、最大 tensor 近似，内存访问、DMA、缓存、调度开销没有在 NAS 目标中直接建模。

正文包未截断，但文本抽取中的部分表格行，尤其 Table V 的逐层架构细节，没有完整保留下来；若要复现实验报告中的精确层序列，仍需回到 PDF 复核表格。作者未来工作也承认还需要联邦学习、运行时自适应、异常/入侵检测扩展、量化感知约束和对抗/分布漂移鲁棒性。

## 10. 与本项目的关系
对“异常检测”项目来说，这篇论文最有价值的不是某个分类准确率，而是它给出了一套边缘侧安全模型设计范式：从数据长度、头部隐私、模型结构、硬件预算到 MCU 实测形成闭环。

可以借鉴的方向包括：把异常检测模型的搜索目标从 accuracy/AUC 扩展为 accuracy、FLOPs、峰值激活、延迟、能耗联合约束；把 session 前若干字节作为轻量前端筛查信号；在网关侧做聚合，在 MCU 或低功耗边缘节点做快速分类/告警前置。

需要注意边界：它的标签空间是已知应用/类别，不是未知异常；ISCX 也偏老，可能存在数据集指纹。若迁移到本项目，应补上开放集评估、跨时间采集、攻击家族外推、误报成本和在线漂移监测。

## 11. 代码对照分析
本地实际代码在 `source\ProtectIT_Unige`。目录与论文主流程基本对应：`preprocessing` 对应 PCAP 到 IDX 会话样本，`nas_optimization` 对应 HW-NAS 搜索、模型训练和硬件指标计算。

关键文件对应关系如下：

| 论文环节 | 本地文件 | 观察 |
|---|---|---|
| PCAP 会话抽取与标签 | `preprocessing\session_preprocessing.py` | `label_mapping` 对 ISCX/USTC/QUIC 留有映射；`create_session_key` 构造双向 session key；`extract_sessions` 做聚合、去重、截断/补零到 784。 |
| Header 预处理 | `preprocessing\session_preprocessing.py` | `extract_packet_data` 支持 MAC remove/anonymize/zero、IP anonymize/remove/zero、端口置零、UDP padding，对应论文 Table IX。 |
| IDX 数据加载 | `nas_optimization\Library_load_and_split_data.py` | `read_idx3/read_idx1` 读取 MNIST 风格 IDX，`preprocess_data` 归一化并 reshape 到 `(samples, 784, 1)`。 |
| NAS 入口 | `nas_optimization\B01_NAS.py` | 设置 `num_classes=11`、`120000` 参数、`11000000` FLOPs、`22000` max tensor、100 代、10 子代、2 次变异，和论文设置一致。 |
| CNN block | `nas_optimization\Library_Block.py` | Conv1D、BatchNorm、Activation、Max/Average Pooling、Dropout，基本对应论文搜索空间。 |
| 演化搜索 | `nas_optimization\Library_NAS.py` | `run_NAS`、`new_generation`、`mutate_network_and_control` 实现父代到子代的添加/删除/修改和硬件筛选。 |
| 模型与硬件指标 | `nas_optimization\Library_Net.py` | 固定输入 `(784,1)`，GAP 后接 Dense；`hw_measures` 用 `keras_flops` 算 FLOPs，并用 `4 * params/tensor` 估计 Flash/RAM。 |
| 指标 | `nas_optimization\Library_compute_stats.py` | 计算 accuracy、weighted precision、weighted recall、weighted F1。 |

复现时要特别注意：`Library_load_and_split_data.py` 仍是 `/path/to/your/...` 占位路径，而且在模块导入阶段就调用加载函数，不改会直接失败；`session_preprocessing.py` 的 `idx3_path/idx1_path` 赋值缩进在 `if not pcap_files` 的返回之后，实际有 PCAP 时可能未定义；代码包没有包含论文中量化、STM32Cube.AI、所有表格重训和会话长度批量实验脚本。因此它覆盖“预处理 + NAS 核心”，但不是完整一键复现实验包。

## 12. 本篇精华
- 论文真正的贡献是把加密流量分类从“高精度深度模型”推进到“MCU 可运行的会话级模型”。
- 参数量、FLOPs、最大 tensor 三个约束分别锚定 Flash、计算/能耗、RAM，是做边缘安全模型时很实用的三元指标。
- 1D CNN 在会话原始字节上足够有效，没必要默认使用 LSTM、Transformer 或复杂混合模型。
- 会话早期字节信息密度很高，输入缩到 324/484 字节仍可保持较好 INT8 精度并明显降低延迟能耗。
- 头部字段不是简单“删得越干净越好”，过度置零会损伤结构指纹；UDP padding 能缓解 TCP/UDP 结构差异带来的性能损失。
- ISCX 上搜索到的架构在 USTC 和 QUIC 上仍有效，说明搜索得到的可能是通用轻量结构，而非单数据集大模型。
- 代码展示了方法骨架，但复现实验前必须修路径、修预处理输出路径缩进，并自行补齐量化部署脚本。

## 13. 建议精读路线
先读 Introduction 和 Related Work，抓住作者批评对象：不是加密流量分类没人做，而是可部署硬件约束没人系统做。

第二步读 Methodology 中的预处理、约束优化公式和搜索空间，重点看为什么选择 session-level、1D CNN、参数/FLOPs/tensor 三约束。

第三步读 Experimental Setup，把 ISCX 主任务、外部 USTC/QUIC、STM32F746G 与 Nucleo-F401RE 的硬件阈值记清楚。

第四步读 Results，不必纠结每个 SOTA 名称，重点看“精度损失多少、资源省多少、是否满足 MCU”。最后读 Section VII 和 VIII，因为预处理、长度、量化和 MCU 实测才是这篇论文最能服务后续边缘异常检测研究的部分。

<!-- codex-cli-deep-read: complete -->
