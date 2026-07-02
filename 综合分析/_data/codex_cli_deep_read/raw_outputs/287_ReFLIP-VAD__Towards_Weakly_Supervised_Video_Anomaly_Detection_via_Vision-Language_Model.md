# [287] ReFLIP-VAD: Towards Weakly Supervised Video Anomaly Detection via Vision-Language Model

## 1. 基本信息

论文：ReFLIP-VAD: Towards Weakly Supervised Video Anomaly Detection via Vision-Language Model  
中文题意：基于视觉-语言模型的弱监督视频异常检测 ReFLIP-VAD  
年份与来源：2024，IEEE Transactions on Circuits and Systems for Video Technology  
DOI：10.1109/TCSVT.2024.3482007  
任务范式：弱监督视频异常检测，只使用视频级标签，输出片段/帧级异常分数。  
正文包状态：本次正文包未截断。  
代码：`source/ReFLIP-VAD`，官方 PyTorch 仓库。

## 2. 中文翻译与核心摘要

这篇论文的核心不是“再做一个 MIL 异常分类器”，而是试图把视觉-语言预训练模型的语义空间引入弱监督视频异常检测。作者认为，传统 WSVAD 多数只用 C3D/I3D/ViT 等视觉特征，再接 MIL 二分类器，因此能判断“是否异常”，但对“异常属于什么语义类别、视觉片段和文本异常标签如何对齐”利用不足。

ReFLIP-VAD 的主线是：用 FLIP/CLIP 类视觉-语言模型抽取视觉和文本表征；用 Glimpse-Emphasize 网络建模全局与局部时序依赖；用分类分支输出粗粒度异常分数；用视频-文本对齐分支输出细粒度类别对齐图；再用 DistilBERT 作为提示编码器生成可学习的重参数化 prompt，减少手工 prompt 对结果的限制。

最终结果：UCF-Crime 上 AUC 89.14%、Ano-AUC 74.72%；XD-Violence 上 AP 86.29%。细粒度定位也优于 Deep-MIL、HL-Net、VadCLIP。

## 3. 论文解决的具体问题

论文面对的是弱监督视频异常检测的三个痛点：

1. 视频只有视频级标签，缺少帧级异常位置，模型必须从一整段视频中找出真正导致标签为异常的片段。
2. 现有方法过度依赖视觉特征和二分类 MIL，能粗略检测异常，但难以解释异常语义，也难以做细粒度异常类别定位。
3. CLIP/FLIP 本来面向图像-文本对齐，直接迁移到视频异常检测时缺少时序建模、异常语义 prompt 设计和弱监督对齐机制。

因此，ReFLIP-VAD 试图同时回答两个问题：视频中哪里异常，以及该异常更像哪个文本异常类别。

## 4. 创新点深度提炼

第一，双分支设计。CLS-Block 负责二分类异常置信度，VTA-Block 负责视频片段与异常文本类别的对齐。这个结构比单一 MIL 分类器更有信息量，因为它把“异常检测”和“异常语义识别”拆成两个互相促进的目标。

第二，引入重参数化可学习 prompt。作者没有只用 “a video of [CLASS]” 这类模板，而是用 DistilBERT prompt encoder 对 prompt embedding 做重参数化，并保留残差连接，使类别文本嵌入更适应异常检测任务。

第三，Glimpse-Emphasize 时序建模。Glimpse 捕获跨片段全局依赖，Emphasize 强调局部/通道相关信息，目标是解决 VLM 静态图像表征缺乏视频动态上下文的问题。

第四，多模态 prompt。分类分支得到的异常注意力会聚合视频视觉特征，形成 anomaly-centric visual prompt，再与文本类别嵌入相加，让文本类别表示带上当前视频的视觉上下文。

第五，MIL-Align。VTA 分支不要求帧级标签，而是从 alignment map 中选择 Top-K 高相似片段，让视频级类别监督约束最代表该类别的片段。

## 5. 科学问题与研究假设

科学问题：视觉-语言模型中学到的开放语义知识，能否在只有视频级标签的条件下提升视频异常检测，尤其是细粒度类别定位？

核心假设：

1. 异常类别文本，如 abuse、arson、explosion，不只是标签 ID，而是有可迁移语义的文本概念。
2. 异常视频中只有少数片段真正与异常类别强相关，因此 Top-K MIL 比全视频平均更合理。
3. 视觉 prompt 能把当前视频的异常上下文注入文本嵌入，从而缓解固定文本 prompt 与具体视频场景之间的语义偏差。
4. 全局时序上下文和局部片段特征都重要：前者帮助理解事件发展，后者帮助捕获短暂异常动作。

## 6. 科学方法与技术路线

方法流程可以概括为：

1. 将视频切为片段，用 FLIP/CLIP 类图像编码器抽取片段视觉特征。
2. 文本侧把 normal 与各异常类别送入文本编码器，不使用 one-hot，而是得到类别语义嵌入。
3. 视觉特征先经 Feature Intensify 和 Glimpse-Emphasize 网络，增强时序表达。
4. CLS-Block 对每个片段输出二分类异常分数，训练时用 Top-K 聚合为视频级预测。
5. VTA-Block 计算片段视觉特征与类别文本嵌入的相似度，形成细粒度 alignment map。
6. DistilBERT 生成重参数化 prompt，视觉异常注意力生成 visual prompt，二者共同改进类别文本嵌入。
7. 总损失包含粗粒度 BCE、细粒度对齐损失和特征/文本分离约束，使正常与异常语义空间拉开。

## 7. 实验设计与实验步骤

数据：UCF-Crime，1900 个真实监控视频、128 小时、13 类异常，1610 训练、290 测试；XD-Violence，4754 个视频、217 小时、6 类暴力异常，3954 训练、800 测试。

预处理：视频按滑窗抽视觉特征，论文设定为 16 帧窗口；UCF-Crime 采样 24 fps，XD-Violence 采样 30 fps；特征长度不足则 padding，过长则采样或分块。

模型/基线：与 Deep-MIL、RTFM、HL-Net、DMU、CLIP-TSA、VadCLIP 等比较；同时报告 CLIP 特征和 FLIP 特征版本。

训练：论文使用 Adam、batch size 128、50 epoch；UCF-Crime 学习率 3e-4，XD-Violence 学习率 5e-4；温度系数 τ=0.07；Top-K 用于弱监督片段选择。

指标：UCF-Crime 用 frame-level AUC 和 Ano-AUC；XD-Violence 用 frame-level AP；细粒度检测用 mAP@IoU 0.1 到 0.5，并报告平均值。

消融/敏感性：验证时序模块、双分支结构、prompt 类型、context length、window length、input length、视觉-语言模型规模、温度系数和损失权重。

结果核查：主表看粗粒度 AUC/AP，细粒度表看 mAP@IoU，消融表看每个模块是否真的贡献增益，类别级图表看在 shoplifting、fighting 等细微异常上的失败边界。

## 8. 关键结果、结论与证据

粗粒度检测：UCF-Crime 上 ReFLIP-VAD-FLIP 达到 AUC 89.14%、Ano-AUC 74.72%，高于 VadCLIP 的 88.02% 和 70.23%；XD-Violence 上 AP 86.29%，高于 VadCLIP 的 84.51%。

细粒度检测：UCF-Crime 平均 mAP 为 9.62%，高于 VadCLIP 的 6.68%；XD-Violence 平均 mAP 为 27.36%，高于 VadCLIP 的 24.70%。绝对值不高，说明细粒度 WSVAD 本身仍很难，但相对提升清晰。

消融证据：无时序建模的 XD-Violence AP 只有 73.31%，完整 GE 达 86.29%；prompt 模板中，`RL-Prompt + [CLASS]` 明显优于裸类别词和手工模板；context length 最优为 24，窗口长度最优约 64，说明 prompt 和时序窗口都存在非单调敏感性。

结论：视觉-语言语义对齐确实能增强弱监督视频异常检测，尤其是异常类别语义定位；但收益依赖 prompt、时序建模和 MIL 选择机制的共同作用。

## 9. 局限性与待解决问题

第一，方法仍依赖预定义异常类别。论文结论也承认，未来需要处理未预定义异常，即开放集或开放词表异常检测。

第二，细粒度 mAP 绝对值仍低。UCF-Crime 平均 mAP 只有 9.62%，说明“识别异常类别并定位时间段”远未解决。

第三，对细微、语义模糊异常不稳定。论文类别分析中 shoplifting、fighting 等类别提升有限，说明简单类别词或 prompt 字典难以覆盖隐蔽异常行为。

第四，代码复现存在风险。当前仓库中顶层 [model.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/model.py:192>) 调用了 `encode_token` 和双参数 `encode_text`，但 [ReFLIP/model.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/ReFLIP/model.py:339>) 中只看到 `encode_image` 与单参数 `encode_text`，接口疑似不一致。另一个风险是 [utils/layers.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/utils/layers.py:176>) 中 `DistanceAdj` 硬编码 `.to('cuda')`，CPU 或非默认 GPU 环境会出问题。

第五，论文实验配置与发布代码默认配置不完全一致。论文写 50 epoch 和较大学习率，代码默认 [ucf_option.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/ucf_option.py:16>)、[xd_option.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/xd_option.py:16>) 是 10 epoch，学习率分别为 2e-5 和 1e-5。

## 10. 与本项目的关系

与网络安全异常检测是弱相关，但思路可迁移。它不能直接处理 QUIC、Tor、DAPT、ToN-IoT 等流量数据；我在仓库中也没有看到这些数据集线索，实际代码围绕 UCF-Crime 和 XD-Violence。

可借鉴的是范式：把网络会话/时间窗当作 video bag，把包序列、流统计、告警上下文当作 segment feature；用视频级/会话级标签训练 MIL；再引入攻击类别文本，如 scan、brute force、DDoS、exfiltration，与序列表征对齐。真正难点是网络侧缺少天然 CLIP/FLIP 这样的强视觉-语言编码器，需要改成时序-文本或表格-文本预训练。

## 11. 代码对照分析

数据预处理： [crop.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/crop.py:8>) 实现 10-crop/flip 特征抽取示例，调用 ReFLIP/CLIP 图像编码器并保存 `.npy`；[make_list_ucf.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/list/make_list_ucf.py:4>) 和 [make_list_xd.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/list/make_list_xd.py:5>) 生成特征路径 CSV，但路径是作者本机硬编码。

数据加载： [utils/dataset.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/utils/dataset.py:7>) 定义 UCFDataset/XDDataset，读取 CSV 中的 `.npy` 特征；[utils/tools.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/utils/tools.py:82>) 负责定长采样、padding 和测试分块。

模型： [model.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/model.py:59>) 是主模型。可见实现包含窗口 Transformer、GCN、距离邻接、DistilBERT prompt、CLS 分类器、视觉 prompt 与文本融合、视觉-文本相似度 logits。它与论文的 Glimpse-Emphasize 公式不完全同名同构，更像发布代码中的工程化时序模块。

训练： [ucf_train.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/ucf_train.py:15>)、[xd_train.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/xd_train.py:15>) 中 `CLASM` 对应 VTA 的 Top-K 多类 MIL，`CLAS2` 对应 CLS 二分类 MIL，`loss3` 对应 normal 文本特征与异常文本特征的分离约束。

评估： [ucf_test.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/ucf_test.py:50>)、[xd_test.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/xd_test.py:50>) 分别计算 CLS 分数 `prob1` 和 VTA 分数 `prob2`，再计算 AUC/AP；[utils/ucf_detectionMAP.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/utils/ucf_detectionMAP.py:125>)、[utils/xd_detectionMAP.py](<F:/泉城实验室/二期/论文/异常检测/source/ReFLIP-VAD/utils/xd_detectionMAP.py:126>) 计算 IoU 阈值下的细粒度 mAP。

## 12. 本篇精华

1. ReFLIP-VAD 的本质是“二分类异常检测 + 文本类别语义对齐”的联合弱监督框架。
2. 论文最有价值的点不是单个 prompt，而是把 prompt、视觉异常注意力、MIL-Align 结合起来。
3. 视觉-语言模型提升最大的位置是 Ano-AUC 和细粒度 mAP，说明语义对齐有助于异常片段和类别的共同定位。
4. Glimpse-Emphasize 消融从 73.31% AP 提到 86.29% AP，证明 VLM 迁移到视频时必须补时序建模。
5. `RL-Prompt + [CLASS]` 明显优于手工模板，说明异常类别词需要任务适配，而不是直接套 CLIP prompt。
6. 细粒度 mAP 仍然偏低，论文更像是在推进方向，而不是彻底解决弱监督细粒度异常定位。
7. 对网络异常检测的启发是：用攻击语义文本约束弱标签序列异常检测，但必须替换掉视频视觉编码器。

## 13. 建议精读路线

先读 Introduction 和 Related Work，抓住作者对传统 WSVAD 与 VLM-based VAD 的批评点。  
再精读 Method 中的 CLS-Block、VTA-Block、Reparameterized Prompt 和 MIL-Align，这是论文真正的机制核心。  
随后读实验主表和消融表，重点看双分支、prompt 类型、时序模块三组消融是否支撑创新点。  
最后对照源码读 `model.py`、`ucf_train.py`、`xd_train.py`、`utils/dataset.py`，并特别核查 ReFLIP 接口与论文公式之间的不一致。