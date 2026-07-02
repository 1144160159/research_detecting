# [583] A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats

## 1. 基本信息

- 题名：A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats
- 作者：Raffaele Carillo, Francesco Cerasuolo, Giampaolo Bovenzi, Domenico Ciuonzo, Antonio Pescape
- 年份：2026
- 来源：IEEE Transactions on Network and Service Management
- DOI：10.1109/TNSM.2026.3675031
- 主题：IoT 网络入侵检测、联邦学习、类别增量学习、0-day 攻击、早期检测
- 本文定位：把 Federated Learning 与 Class Incremental Learning 结合到 IoT NIDS 中，研究在非 IID、客户端攻击类别不重叠、每个客户端只出现一个新攻击类的严苛条件下，NIDS 如何持续学习新威胁并尽量不遗忘旧威胁。
- 正文状态：本次正文包未截断。
- 代码状态：未发现该论文对应的本地开源代码包。

## 2. 中文翻译与核心摘要

这篇论文关注一个很现实的问题：IoT 网络中的攻击类型不断变化，不同边缘节点或组织看到的攻击也可能不同；传统 AI-NIDS 如果要学习新攻击，往往需要集中数据并重新训练，这既有隐私风险，也有计算和存储成本。

作者提出 FCIL，即 Federated Class Incremental Learning，用于网络入侵检测。它希望同时满足三点：第一，不集中原始流量数据，通过联邦学习在多个客户端协同训练；第二，模型能够增量吸收新攻击类别，而不是每次从头训练；第三，检测尽可能早发生，只使用双向流前 10 个包的包级特征。

实验使用 TON IoT、IoT-NID、Edge-IIoTset 三个 IoT 数据集，比较了多种 CIL 方法和 FL 聚合算法。核心发现是：MEMENTO+ 与 FedProx 的组合总体最强；加入 TCP Flags 和 TTL 等扩展特征能明显提升表现；FCIL 在小规模客户端场景下可优于集中式 CIL，但仍落后于集中全量从头训练；客户端数量增加后，模型更能保留旧知识，却更难吸收新攻击；跨数据集部署时性能明显下降，说明网络环境迁移仍是关键难题。

## 3. 论文解决的具体问题

本文不是单纯做“入侵检测分类器”，而是在解决一个组合难题：

1. IoT 攻击持续演化，新攻击类会不断出现，NIDS 不能只识别固定闭集。
2. 不同客户端、边缘节点或组织掌握的数据不同，攻击类可能只在某个客户端局部出现。
3. 原始网络流量难以集中共享，尤其涉及用户行为、设备指纹和组织内部网络结构。
4. 增量学习容易遗忘旧攻击，联邦学习又会因为非 IID 数据导致全局模型偏移。
5. 实际 NIDS 需要早期检测，不能等完整流结束后再依赖全流统计特征。

因此，论文真正处理的是：在隐私受限、数据分散、攻击类异步出现、类别极度非 IID 的 IoT 环境中，如何构建一个能持续更新的多类 NIDS。

## 4. 创新点深度提炼

第一，问题设定比常见 FL-NIDS 更严苛。多数联邦入侵检测默认攻击类别固定，或者各客户端类别有重叠；本文设置为每个客户端引入一个不同的新攻击类，客户端之间新类不重叠，更接近“某个组织先遭遇某种 0-day”的实际场景。

第二，论文把 CIL 和 FL 的交叉问题具体化到早期检测 NIDS。输入不是完整流统计，而是双向流前 10 个包的 PL、IAT、DIR、WIN、FLG、TTL 等包级序列特征，强调尽早响应。

第三，系统比较了 CIL 策略与 FL 聚合算法的交互。作者不是只提出一个模型，而是比较 FT-Mem、iCaRL+、BiC、BiC+、MEMENTO、MEMENTO+ 与 FedAvg、FedProx、FedDyn 的组合，说明 CIL 技术在联邦非 IID 环境下会出现不同于集中式场景的行为。

第四，论文引入两种联邦偏置校正方式：一种对所有新类共享 bias correction 层，另一种为每个客户端的新类维护个性化 bias correction 层，即 BiC+ / MEMENTO+ 思路。这是为了解决联邦增量学习中“新类来自不同客户端”造成的类别偏置。

第五，实验不只看总体 F1，还分解旧类、新类、全部类，并使用低 FPR 区间 pAUC 评估二分类检测能力，符合 NIDS 对低误报的实际要求。

## 5. 科学问题与研究假设

科学问题可以概括为：当新攻击类别分散出现在不同客户端，且客户端数据高度非 IID 时，联邦增量学习能否训练出一个既记得旧攻击、又能识别新攻击的 IoT NIDS？

论文隐含的研究假设包括：

- CIL 的 rehearsal、knowledge distillation、bias correction 等机制可以缓解旧类遗忘。
- FL 的 FedProx、FedDyn 等正则化聚合方法比 FedAvg 更适合非 IID 攻击分布。
- 包级早期特征足以支撑 IoT 入侵检测，尤其前 10 个包已包含较强攻击指纹。
- TCP Flags 与 TTL 能为恶意流量识别提供额外信息。
- 客户端数量增加会提升场景复杂度，使新类吸收更困难，但联邦训练可能增强旧知识保留和跨网络鲁棒性。

## 6. 科学方法与技术路线

技术路线分为四层。

第一层是数据表示。论文以 biflow 为流量对象，取前 10 个包，每个包提取若干字段，形成 packets × fields 的矩阵输入。基础特征为 PL、IAT、DIR、WIN；扩展特征增加 FLG 和 TTL。

第二层是基础 NIDS 模型。主模型为 2D-CNN，约 540k 参数，由卷积、池化、归一化和 Dense 分类头组成；另用 CNN-LSTM HYBRID 架构测试方法是否依赖特定网络结构。

第三层是类别增量学习。初始模型先学旧类 Kold，增量阶段每个客户端引入新类 Knew。方法包括 FT-Mem、iCaRL+、BiC、BiC+、MEMENTO、MEMENTO+。其中 MEMENTO 系列结合记忆样本、蒸馏、数据增强、输出平滑和偏置校正。

第四层是联邦协同。每个客户端本地训练若干 epoch 后上传模型，服务器用 FedAvg、FedProx 或 FedDyn 聚合，再广播全局模型。FedProx 通过近端项抑制客户端漂移，FedDyn 通过动态正则修正局部目标与全局目标的不一致。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 TON IoT、IoT-NID、Edge-IIoTset 三个 IoT/IIoT 数据集，覆盖 DoS/DDoS、信息收集、MITM、注入、恶意软件等攻击类别。

2. 标签标准化  
   将不同数据集中的攻击名称重标注为统一格式，如 `dos-*`、`infog-*`、`mitm-*`、`inject-*`、`malwr-*`，以便跨数据集比较。

3. 采样与不平衡处理  
   对多数类随机下采样，使每类 biflow 数量约在 10k 到 100k 范围内，但仍保留较强长尾不平衡。

4. 特征构造  
   每个 biflow 取前 10 个包。基础特征：PL、IAT、DIR、WIN；扩展特征：再加入 FLG、TTL。短流用 zero-padding。

5. 场景设置  
   S1 为少客户端场景，2 个客户端，每个客户端出现一个不同新攻击类。S2 为多客户端场景，5 个客户端，每个客户端出现一个不同新攻击类。旧类包含 benign，新类只包含 attack。

6. 模型与基线  
   主模型为 2D-CNN，补充 HYBRID 架构。上界基线包括 Scratch，即集中全量从头训练；Centralized CIL，即集中式增量学习。

7. 训练设置  
   总本地训练 200 epoch，patience 为 20，初始学习率 0.1，学习率衰减因子 3，最小学习率 1e-4。每个旧类记忆 25 个 biflow。同步轮数 R 取 4、10、20、40、100、200。

8. 联邦算法  
   比较 FedAvg、FedProx、FedDyn。重点观察它们与 BiC+、MEMENTO+ 等 CIL 方法的组合效果。

9. 指标  
   多类任务使用 macro F1，并分别报告 old、new、all。二分类检测使用 pAUC，限制 FPR 在 0 到 1%，更贴近 NIDS 低误报需求。

10. 消融与敏感性  
   比较基础特征与扩展特征；比较不同同步轮数 R；比较 2 客户端与 5 客户端；比较 IID 新类分布与非 IID 新类分布；比较 2D-CNN 与 HYBRID。

11. 结果核查  
   通过 Drop-Scratch 和 Drop-CIL 衡量 FCIL 相对上界的性能差距；通过 ROC 和混淆矩阵检查低误报检测、新类学习和跨数据集泛化偏置。

## 8. 关键结果、结论与证据

最重要的结论是：FCIL 可行，但新攻击学习仍是瓶颈。

在 TON IoT 的 S1 场景中，基础特征下 FT-Mem 在高同步轮数可达到约 65% F1all；但引入扩展特征后，多数方法旧类和整体表现明显提升，说明 FLG 与 TTL 对 IoT 攻击识别有价值。

FedProx 在低同步轮数下明显优于 FedAvg，尤其适合 MEMENTO+ 和 BiC+；FedDyn 在同步轮数较高时表现更强，但低 R 下较弱。整体上，MEMENTO+ + FedProx 是最稳定的优选组合。

与上界相比，FCIL 在 S1 中对 TON IoT 和 Edge-IIoTset 可优于集中式 CIL，但仍落后于 Scratch，AC 任务差距可到约 8%。IoT-NID 上集中式 CIL 反而略强，说明数据集特性会影响联邦增量学习优势。

在 S2 中，客户端数量增加后，FCIL 更能保留旧知识，但学习新攻击更困难。对 Edge-IIoTset，AC 任务中新类性能相对 CIL 的下降可达 13%，说明“每个客户端一个新类”的场景会放大类别偏移和聚合冲突。

跨数据集部署时性能显著下降。源数据集和目标数据集相同时，bMD 的 pAUCAll 通常 ≥ 92%；跨数据集时最高约 75%，不少组合低于 60%。这说明 IoT NIDS 的跨网络泛化仍远未解决。

Few-shot 实验显示，当每个新攻击类只有 15 到 200 个样本时，FCIL 对旧类影响较小，新类表现有时接近甚至超过全量样本设置。这可能与样本选择、噪声、类内差异有关，也提示少样本增量更新并非完全不可行。

## 9. 局限性与待解决问题

第一，FCIL 仍明显落后于集中全量 Scratch。也就是说，它解决了隐私和持续更新问题，但以性能为代价。

第二，新攻击类学习仍不稳定，尤其在客户端数量增加、类别不重叠时，模型更容易保守地保留旧知识，而难以充分吸收新类。

第三，跨网络泛化能力不足。不同 IoT 数据集之间设备、流量模式、攻击实现和采集环境差异很大，导致部署到新网络后检测和分类性能明显下滑。

第四，隐私保护还不充分。论文使用 FL 避免共享原始数据，但没有深入处理梯度泄露、模型反演、成员推断、恶意客户端投毒等问题。

第五，通信与资源开销只做了复杂度层面的说明，没有充分实验验证在 NB-IoT、LTE-M、边缘网关等真实部署条件下的延迟、带宽和能耗。

第六，本文主要是类别增量学习，还没有系统处理 domain-incremental learning。现实中更常见的是同一攻击在不同网络域表现变化，而不只是新增类别。

第七，本次正文包未截断，因此理解不受正文缺页影响；但由于未发现代码包，无法核验实现细节与论文描述是否完全一致。

## 10. 与本项目的关系

该论文与“入侵检测与网络异常检测”高度相关，尤其适合支撑以下研究方向：

- 分布式 NIDS：多个组织、边缘节点或网关不共享原始流量，通过模型更新协同学习。
- 持续学习型异常检测：攻击类随时间增长，模型需要增量更新。
- IoT/IIoT 安全：设备异构、攻击面大、网络环境差异强。
- 隐私保护检测：避免集中上传敏感流量。
- 早期检测：仅使用前几个包做判断，适合快速阻断或预警。

对本项目的启发是：如果目标是构建实用型异常检测系统，不能只追求单一数据集上的闭集分类效果，而要评估新类学习、旧类遗忘、跨域泛化、低 FPR 检测、少样本更新和分布式协同。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法逐文件对应源码实现。

根据论文描述，如果复现代码存在，预计目录会包括以下模块：

- 数据预处理：负责读取 TON IoT、IoT-NID、Edge-IIoTset，生成 biflow，抽取前 10 个包的 PL、IAT、DIR、WIN、FLG、TTL，并执行统一重标注与下采样。
- 数据划分：负责构造 S1、S2 场景，划分 Kold/Knew，将不同新攻击类分配给不同客户端，生成 10 个 seed 的 train/test split。
- 模型定义：应包含 2D-CNN 和 HYBRID CNN-LSTM，分类头需要支持增量扩展。
- CIL 方法：应实现 FT-Mem、iCaRL+、BiC、BiC+、MEMENTO、MEMENTO+，包括 exemplar memory、herding、KD loss、bias correction、MEMENTO 的 IAT 增强与 smoothing。
- 联邦训练：应包含 server/client 抽象，实现 FedAvg、FedProx、FedDyn，以及每 R 轮同步、客户端本地训练和全局模型广播。
- 评估脚本：应计算 F1old/F1new/F1all、pAUCold/pAUCnew/pAUCall、Drop-Scratch、Drop-CIL，并输出 ROC、混淆矩阵和同步轮数敏感性图。
- 运行线索：论文说明其扩展自 FACIL 框架，使用 NumPy、Pandas、PyTorch、Matplotlib、Seaborn；若复现，应优先检查是否有基于 FACIL 改造的 `server`、`client`、`approach`、`datasets`、`networks`、`eval` 目录。

## 12. 本篇精华

- 本文最有价值的不是提出一个新分类器，而是定义了更真实的 FCIL-NIDS 场景：新攻击类分散出现在不同客户端，且客户端之间新类不重叠。
- MEMENTO+ + FedProx 是总体最优组合；FedProx 在低同步轮数下对非 IID 客户端漂移更稳。
- TCP Flags 与 TTL 对 IoT 入侵检测有明显增益，说明包头行为特征在早期检测中仍很关键。
- FCIL 在少客户端场景可超过集中式 CIL，但仍达不到集中全量 Scratch，上限差距不可忽视。
- 客户端越多，新类吸收越困难；FCIL 更擅长保留旧知识，而不是无损学习新攻击。
- 跨数据集泛化是最大现实短板，训练网络和部署网络不同会导致 pAUC 和 AC 性能显著下降。
- Few-shot 新攻击学习结果并不悲观，少量新攻击样本在部分场景中已能接近全量设置。
- 对真实部署而言，后续必须补上安全联邦、防投毒、通信压缩、个性化模型和域增量学习。

## 13. 建议精读路线

建议按以下顺序精读：

1. 先读 Introduction 和 Literature Gap，明确本文比普通 FL-NIDS 或 CIL-NIDS 难在哪里。
2. 再读 Methodology III-C，重点理解每个客户端引入不同新类时，FCIL 的目标函数和偏置校正如何变化。
3. 接着读 Experimental Setup，尤其是输入特征、S1/S2 场景、Scratch 与 centralized CIL 两个上界。
4. 精读 Table III、Fig. 4、Table IV，理解特征扩展、同步轮数和 FL 聚合算法的交互。
5. 精读 Table V，这是全文结论核心，可直接提炼 FCIL 与 Scratch/CIL 的差距。
6. 最后读跨数据集和 few-shot 部分，因为这两节最接近真实 NIDS 部署问题，也最能暴露未来研究空间。

<!-- codex-cli-deep-read: complete -->
