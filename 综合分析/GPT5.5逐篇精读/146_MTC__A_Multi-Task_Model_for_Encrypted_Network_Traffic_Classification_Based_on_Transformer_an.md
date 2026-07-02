# [146] MTC: A Multi-Task Model for Encrypted Network Traffic Classification Based on Transformer and 1D-CNN

## 1. 基本信息

- 编号：146
- 题名：MTC: A Multi-Task Model for Encrypted Network Traffic Classification Based on Transformer and 1D-CNN
- 年份：2023
- DOI：10.32604/iasc.2023.036701
- 来源：Intelligent Automation & Soft Computing
- 主题归类：加密流量分类与应用识别
- 二级关联：其他AI安全与跨域异常检测
- 本地正文：`综合分析_data/full_text_cache_plain/146.txt`
- PDF：`paper/10.32604_iasc.2023.036701.pdf`
- 代码状态：未发现该论文对应的本地开源代码

## 2. 中文翻译与核心摘要

这篇论文提出 MTC，一个面向加密网络流量分类的多任务模型。它把 Transformer 与 1D-CNN 并联起来，通过特征融合模块让两条分支互相补短：Transformer 负责捕获较长距离的字节序列依赖，1D-CNN 负责提取局部细节模式。模型同时处理应用识别、流量类别刻画以及辅助类别任务，试图降低分别训练多个模型带来的管理和训练成本。

核心思想不是简单堆叠 Transformer 和 CNN，而是让两类特征在中间层交互：CNN 分支产生的局部特征送入 Transformer 分支，Transformer 分支产生的全局相关信息送入 CNN 分支。作者认为，加密流量虽然 payload 不可直接解析，但其字节分布、包头结构残留、长度和局部模式仍然含有可学习信号；多任务学习还能利用不同标签粒度之间的关系提升表示质量。

实验主要在 ISCX VPN-nonVPN 上进行，并用 CICIDS2017 验证泛化。MTC 在 ISCX 上取得应用识别 F1 98.25%、召回 98.30%，流量类型刻画 F1 97.94%、召回 97.54%；在 CICIDS2017 上，攻击类型分类和恶意流量识别也达到 99% 以上指标。

## 3. 论文解决的具体问题

论文针对的是加密网络流量分类中的两个实际问题。

第一，已有方法通常把“应用识别”和“流量类型刻画”分开做。前者识别 FTP、Facebook、Skype、YouTube 等具体应用，后者识别 Chat、Email、Streaming、VoIP 等粗粒度流量类别。分开建模会增加训练、部署和网络管理复杂度，也没有利用两个任务之间天然存在的标签关联。

第二，单独使用 CNN 或 Transformer 都有结构性短板。1D-CNN 对局部字节模式敏感，但卷积感受野有限，对长序列中的远距离依赖捕获不足；Transformer 擅长建模全局依赖，但在短序列和局部细节上未必优于卷积。加密流量分类既需要捕捉局部协议/载荷残留模式，也需要把较长范围的字节关系纳入表示，因此单一架构不够理想。

第三，真实流量数据类别不均衡明显。ISCX VPN-nonVPN 中不同应用样本量差异较大，CICIDS2017 中 Infiltration 等攻击类别极少。论文希望模型在不均衡和少样本类别上仍保持较好性能。

## 4. 创新点深度提炼

1. **并联式 Transformer + 1D-CNN 结构**  
   论文没有采用串联结构，而是用两条分支同时处理同一输入。这样设计的含义是：两类归纳偏置并行保留，不让其中一种表示被另一种过早压缩。

2. **中间层双向特征融合**  
   MTC 的关键在 feature fusion block。Transformer 输出经过插值上采样、CNN 输出经过平均池化下采样，再通过 1×1 卷积调整维度，使两条分支能够交换信息。这个设计对应论文的核心假设：局部模式和长距离依赖不是替代关系，而是互补关系。

3. **多任务学习绑定不同粒度标签**  
   在 ISCX 上，模型同时输出 17 类应用标签、12 类流量类型标签、6 类辅助粗粒度标签。辅助任务把 VPN 与非 VPN 合并，只保留 Chat、Email、File Transfer、Streaming、Torrent、VoIP 六类。这相当于用更稳定的粗粒度语义约束表示空间，帮助复杂任务学习。

4. **长序列与短序列双场景验证**  
   ISCX 使用 1500 字节 packet 序列，CICIDS2017 使用 49 维特征序列。作者用这两个数据源验证：长序列上 Transformer 相对 CNN 更有优势，短序列上 CNN 更强，而 MTC 在两者上都能取得最好或接近最好的结果。

5. **对辅助任务、损失权重、encoder 层数、dropout 的敏感性分析**  
   论文不仅给最终结果，还讨论了 encoder 重复次数、任务损失权重、CNN dropout、epoch 数对性能的影响，这对复现和理解模型有效性比较重要。

## 5. 科学问题与研究假设

核心科学问题可以概括为：

加密流量无法直接读取明文语义时，是否可以通过结合局部字节模式与全局序列依赖，获得比单一深度模型更稳健的流量表示？

论文的主要研究假设有三条：

1. **局部细节假设**：即便流量被加密，packet 字节序列中仍存在局部统计模式、头部结构和长度相关模式，1D-CNN 能有效捕捉这些短程特征。

2. **长距离依赖假设**：长达 1500 字节的 packet 序列中存在跨位置相关性，Transformer 的自注意力机制能够补充 CNN 感受野不足的问题。

3. **多任务互助假设**：应用识别、流量类型刻画和辅助粗粒度分类不是独立任务，粗粒度任务可作为正则化信号，改善细粒度分类和类别不均衡条件下的泛化。

## 6. 科学方法与技术路线

技术路线可以拆成四层。

第一层是输入构造。ISCX VPN-nonVPN 采用单 packet 作为输入，统一为 1500 字节序列，并进行归一化；CICIDS2017 使用清洗后的 49 维数值特征。

第二层是双分支表征。Transformer 分支把 1500 字节变成 30 个 50 维 token，使用多头注意力和前馈层建模全局关系；1D-CNN 分支使用 bottleneck 结构，包括 1×1、1×3、1×1 卷积和残差连接，提取局部模式并控制参数量。

第三层是特征融合。第二、三层 block 中进行双向融合：CNN 特征经过池化和 1×1 卷积送入 Transformer，Transformer 特征经过插值和 1×1 卷积送入 CNN。第一层不融合，因为还没有可交换的中间表征。

第四层是多任务输出。ISCX 上 Transformer 分支用于 17 类应用识别，CNN 分支用于 12 类流量刻画和 6 类辅助任务；CICIDS2017 上 Transformer 分支用于 6 类攻击类型分类，CNN 分支用于恶意/良性二分类。最终损失是各任务交叉熵的加权平均。

## 7. 实验设计与实验步骤

**数据**

- ISCX VPN-nonVPN：原始 14 类流量，去除 Browsing 和 VPN-Browsing 后，重构为 12 类流量类型、17 类应用、6 类辅助标签。
- CICIDS2017：包含良性流量和多类攻击流量，用于验证模型在短特征序列和攻击检测任务上的泛化能力。
- 数据划分：训练集、验证集、测试集比例为 64%、16%、20%。

**预处理**

- ISCX：
  - 删除 Ethernet header。
  - 将 IP header 中的 IP 地址置为 `0.0.0.0`，降低地址泄漏导致的过拟合。
  - TCP header 截为 20 字节，UDP header 补齐到 20 字节。
  - 删除 DNS、ACK、SYN、FIN 等主要服务/握手包。
  - packet 末尾补零到 1500 字节。
  - 字节值除以 255 归一化。
  - 对 17 类应用进行随机采样，每类最多 50,000 个样本，缓解类别不均衡。

- CICIDS2017：
  - 从 78 个特征中删除 10 个差异较小特征和 17 个冗余特征。
  - 清理 NaN 等异常值。
  - 使用分位数变换归一化到 0 到 1。
  - 移除极少数的 Infiltration 类。
  - 使用 RandomUnderSampler 和 SMOTE 进行重采样，最终攻击分类保留 6 类。

**模型/基线**

- 主模型：MTC，Transformer 与 1D-CNN 并联，并通过 feature fusion block 双向融合。
- 基线 1：Multi-task Transformer，基于 MTT 思路，只使用 Transformer。
- 基线 2：Multi-task 1D-CNN，基于 Deep Packet 思路，只使用 1D-CNN。
- 额外对比：Deep Packet、PERT、TSCRNN、LUCID、DBN、CNN-LSTM 等已有方法。

**训练**

- 框架：PyTorch 1.10。
- GPU：NVIDIA RTX 3090 24GB。
- Python：3.7。
- ISCX 训练参数：
  - epoch：100。
  - batch size：128。
  - optimizer：Adam。
  - 初始学习率：0.001。
  - 学习率调度：ReduceLROnPlateau，factor 0.1，patience 10。
  - weight decay：0.0001。
  - early stopping patience：20。
  - 激活函数：ReLU。
- ISCX 损失权重：App:Tra:Aux = 6:2:1。
- CICIDS2017 损失权重：Attack:Mal = 2:1。

**指标**

- Precision、Recall、F1。
- 论文重点报告平均 F1 与平均 Recall。

**消融/敏感性**

- Transformer 第二、三层 encoder 重复次数：比较 `(5,5)`、`(5,6)`、`(6,5)`、`(6,6)`，最终选 `(5,6)`。
- 损失权重：比较 `3:2:1` 到 `7:2:1`，最终选 `6:2:1`。
- CNN dropout：比较 0.05、0.07、0.09，最终选 0.07。
- epoch：比较 50、80、100、120，最终选 100。
- 辅助任务消融：MTC-2task 去掉 6 类辅助任务，性能明显下降。

**结果核查**

复核时应重点检查三点：第一，是否严格删除 Browsing/VPN-Browsing；第二，packet 级采样是否造成训练测试泄漏，例如同一 flow/session 的包是否跨集合；第三，CICIDS2017 使用 SMOTE 后是否只在训练集上做重采样，避免测试集分布被污染。

## 8. 关键结果、结论与证据

在 ISCX VPN-nonVPN 上，MTC 的应用识别 F1 为 98.25%、召回 98.30%；流量刻画 F1 为 97.94%、召回 97.54%；辅助任务 F1 为 97.97%、召回 97.81%。相比 Multi-task Transformer，应用识别 F1 提升 0.98%，流量刻画 F1 提升 2.04%；相比 Multi-task 1D-CNN，流量刻画 F1 提升尤其明显，达到 8.58%。

在 CICIDS2017 上，MTC 的攻击类型分类 F1 为 99.47%、召回 99.66%；恶意流量识别 F1 为 99.71%、召回 99.75%。这说明模型不仅适用于 VPN/非 VPN 加密流量应用分类，也能迁移到入侵检测式任务。

辅助任务的作用很明显。去掉 Aux 后，App 任务 F1 从 98.25% 降到 95.60%，Tra 任务 F1 从 97.94% 降到 92.46%。这说明粗粒度标签不是附属装饰，而是在多任务共享表示中提供了有效约束。

论文最有价值的证据是长短序列对比：ISCX 的 1500 字节长序列上 Transformer 优于 1D-CNN；CICIDS2017 的 49 维短序列上 1D-CNN 几乎追平或超过 Transformer；MTC 在两类场景中均保持最佳。这支持了作者关于局部和全局特征互补的判断。

## 9. 局限性与待解决问题

第一，训练时间较长。作者也承认 MTC 在 ISCX 长序列上训练成本偏高，主要原因可能是 encoder 层数较多、输入长度较长，以及并联双分支带来的额外计算。

第二，解释性不足。论文证明了融合有效，但没有解释模型到底学到了哪些局部模式、哪些长距离依赖，也没有通过注意力可视化、特征归因或错误案例分析说明模型依据。

第三，packet 级输入存在信息损失。单包输入降低了预处理成本，但应用行为往往体现在 flow/session 级时间序列中。对于短包、控制包、加密隧道中高度相似的应用，单包方法可能不如 flow/session 方法稳定。

第四，数据划分方式需要复核。论文只说明按 64/16/20 划分，没有详细说明是否按 flow/session 隔离。如果同一会话中的 packet 同时出现在训练集和测试集，可能导致指标偏高。

第五，类别重采样策略可能影响真实部署表现。ISCX 每类最多采 50,000，CICIDS2017 使用欠采样和 SMOTE，这有利于训练和评价平衡分类能力，但与真实网络中的长尾分布仍有差距。

第六，CICIDS2017 的输入形态与 ISCX 差异很大。前者是人工提取的 49 维特征，后者是原始字节序列；这能说明模型有泛化潜力，但也使两个实验之间的机制解释不完全一致。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，尤其适合作为“加密流量分类与跨域异常检测”的方法参考。

对本项目最有启发的是三点。第一，多任务学习可以把不同粒度标签统一起来，例如“是否异常”“攻击家族”“应用类型”“协议行为类别”可共享底层表示。第二，Transformer + CNN 的互补结构适合处理既有局部模式又有全局依赖的网络数据。第三，辅助任务可以作为一种结构化正则化方法，在标注不足或类别不均衡时提升主任务稳定性。

如果本项目关注异常检测而不只是分类，可以借鉴 MTC 的共享编码器思路：用 CNN 分支捕获局部包/特征模式，用 Transformer 分支捕获跨字段或跨时间依赖，再同时预测异常二分类、攻击类型、多粒度行为标签，甚至加入自监督重构或对比学习任务。

## 11. 代码对照分析

本地未发现该论文对应的开源代码，因此无法逐文件对应真实源码实现。不过根据论文方法，若复现 MTC，代码目录大概率应拆成以下几类：

- 数据预处理：
  - ISCX packet 清洗：删除 Ethernet header、IP 置零、TCP/UDP header 标准化、过滤 DNS/ACK/SYN/FIN、padding 到 1500、除以 255。
  - CICIDS2017 特征清洗：删除冗余/低差异特征、NaN 清理、分位数归一化、RandomUnderSampler、SMOTE。
  - 标签生成：17 类 App、12 类 Tra、6 类 Aux；CICIDS2017 的 Attack 与 Mal 标签。

- 模型文件：
  - `TransformerBlock`：embedding、multi-head attention、feed-forward、residual、normalization、dropout。
  - `CNNBlock`：1×1、1×3、1×1 bottleneck 卷积、残差连接、dropout。
  - `FeatureFusionBlock`：1×1 卷积、average pooling、interpolation、normalization。
  - `MTC`：三层双分支结构、第二/三层融合、多任务输出头。

- 训练文件：
  - 多任务 loss 加权：ISCX 为 `6:2:1`，CICIDS2017 为 `2:1`。
  - Adam、ReduceLROnPlateau、early stopping、weight decay。
  - 保存验证集最佳模型。

- 评估文件：
  - 按任务输出 macro/average F1 与 Recall。
  - 分类别 F1/Recall 曲线或表格。
  - MTC、Multi-task Transformer、Multi-task 1D-CNN、MTC-2task 的统一评测入口。

复现时最容易出错的是数据处理而不是模型搭建，尤其是 packet 过滤、采样平衡、标签映射和训练/测试隔离。

## 12. 本篇精华

1. MTC 的核心不是“Transformer 加 CNN”，而是让两者在中间层双向交换特征，用 CNN 补 Transformer 的局部细节，用 Transformer 补 CNN 的长程依赖。

2. 多任务学习在本文中有实质贡献；去掉 6 类辅助任务后，应用识别和流量刻画均明显下降，说明粗粒度标签能改善共享表示。

3. ISCX 上 1500 字节原始 packet 输入验证了长序列场景，CICIDS2017 上 49 维特征输入验证了短序列场景，MTC 同时适配两者。

4. 论文的强结论来自结构互补证据：长序列上 Transformer 更强，短序列上 1D-CNN 更强，而 MTC 在两者上整体最优。

5. 数据预处理对结果影响极大，包括 IP 置零、header 标准化、服务包过滤、padding、归一化和类别平衡。

6. 该方法适合扩展到异常检测中的多粒度任务，例如恶意/良性、攻击类型、应用类型、流量行为类别联合建模。

7. 主要风险在于训练成本、解释性不足，以及 packet 级随机划分可能带来的潜在数据泄漏问题。

## 13. 建议精读路线

1. 先读 Introduction 和 Related Works，抓住作者为什么认为 Transformer 与 1D-CNN 互补，以及多任务学习为什么适合加密流量分类。

2. 再精读 Section 3.2 的预处理。该部分决定实验是否可复现，尤其要注意 ISCX 的 packet 级处理和 CICIDS2017 的重采样方式。

3. 重点读 Section 3.3 的结构图和三个模块：Transformer Block、1D-CNN Block、Feature Fusion Block。理解第二、三层才发生融合这一细节。

4. 接着读 Table 4 和 Section 4.4，比较 MTC、Transformer、1D-CNN、MTC-2task 的差异，不要只看最高指标，要看不同任务上的提升幅度。

5. 最后读 Discussion，尤其是损失权重、encoder 层数、dropout 和辅助任务消融。这部分最能帮助后续复现和改造模型。

<!-- codex-cli-deep-read: complete -->
