# [300] Self-Supervised Masked Convolutional Transformer Block for Anomaly Detection

## 1. 基本信息

- 编号：300
- 题名：Self-Supervised Masked Convolutional Transformer Block for Anomaly Detection
- 作者：Neelu Madan、Nicolae-Cătălin Ristea、Radu Tudor Ionescu 等
- 年份：2023 在线发表，TPAMI 2024 年 1 月卷期刊出
- 来源：IEEE Transactions on Pattern Analysis and Machine Intelligence
- DOI：10.1109/TPAMI.2023.3322604
- 任务类型：一类异常检测、重建式异常检测、自监督掩码建模
- 主要应用域：工业缺陷、医学影像、RGB 监控视频、热成像视频
- 与本项目相关性：弱相关。它不是网络流量或入侵检测论文，但其“只用正常样本学习、异常样本重建困难、以重建误差做异常分数”的思想可迁移到网络异常检测。

## 2. 中文翻译与核心摘要

这篇论文提出了一个可嵌入其他异常检测模型的神经网络模块：SSMCTB，即自监督掩码卷积 Transformer 块。它的核心做法不是在输入图像或视频上整体遮挡一块区域再让整个模型恢复，而是把“遮挡中心区域并用上下文恢复”的任务封装到一个卷积式基础模块中。该模块可以插入 CNN 或 Transformer 架构的中间层，让网络在特征层面学习正常模式的上下文结构。

SSMCTB 包含两个关键组件：一是 2D 或 3D 掩码卷积，卷积核中心位置被遮住，只允许周围子核看到上下文；二是通道维 Transformer 注意力，用来建模不同重建特征图之间的依赖关系。训练时，模块通过 Huber loss 约束输出特征去重建被遮住的输入特征。由于训练数据只有正常样本，模型主要学会恢复正常模式；测试时遇到异常样本，重建误差通常增大，从而形成异常分数。

论文把该模块接入 10 个已有异常检测模型，在 MVTec AD、BRATS、Avenue、ShanghaiTech 和 Thermal Rare Event 五个数据集上验证。结果显示，SSMCTB 在多数模型、指标和领域中带来稳定提升，并优于作者此前 CVPR 2022 的 SSPCAB 版本。

## 3. 论文解决的具体问题

论文瞄准的是重建式异常检测的一个结构性问题：很多方法把“遮挡-重建”当作模型级预训练或输入级任务，但这种做法依赖特定架构，难以自然迁移到不同模型和不同特征层。

具体问题包括：

- 异常检测通常只能获得正常训练样本，异常类型又高度依赖场景，难以穷举采集。
- 普通自编码器或生成式模型容易过度泛化，连异常样本也能较好重建，导致异常分数不够区分。
- 现有 masked reconstruction 方法往往在输入层做遮挡，例如遮图像 patch、预测未来帧、补视频片段，灵活性不足。
- CNN 卷积核局部感受野有限，对局部模式之间的全局排列关系建模不充分。
- 已有 SSPCAB 仍使用较简单的 SE 通道注意力和 MSE 损失，对复杂通道依赖和离群误差处理不够充分。

因此，作者希望构造一个“可插拔、可自监督、可用于 2D/3D 数据、能提升多个异常检测模型”的通用模块。

## 4. 创新点深度提炼

第一，论文把重建式异常检测从“完整模型行为”下沉为“基础网络块行为”。SSMCTB 本身就带有遮挡、上下文恢复和自监督损失，因此可以插在任意中间层，而不局限于输入图像或视频帧。

第二，提出掩码卷积而不是普通卷积。其卷积核中心区域不可见，模型只能使用四周 2D 子核或八个 3D 子核恢复中心特征。这个设计强制模块学习上下文一致性，而不是直接复制当前位置信息。

第三，将掩码卷积扩展到 3D。对视频片段、医学体数据等 3D 输入，模块可在空间和时间/深度维度同时利用上下文，适合视频异常和 MRI 异常检测。

第四，用通道维 Transformer 替代 SSPCAB 中的 SE 注意力。这里的 Transformer 不是 ViT 那种空间 token 建模，而是把通道作为 token，学习不同重建特征图之间的依赖，再用 sigmoid 生成通道权重。

第五，将自监督重建损失从 MSE 换成 Huber loss。Huber 在误差较小时接近二次损失，在误差较大时接近绝对值损失，对离群值更稳健，符合异常检测中“训练正常样本但仍可能存在噪声”的场景。

第六，验证范围较广。论文不只在一个模型上证明有效，而是把 SSMCTB 接入 DRAEM、NSA、FastViT+NSA、未来帧预测、记忆自编码器、对象中心模型、MAE、3D SSMTL++ 等多个模型，覆盖图像、视频、医学、热成像。

## 5. 科学问题与研究假设

核心科学问题是：如果在网络中间层强制模型根据上下文恢复被遮挡特征，是否会让模型更好地学习正常模式的结构规律，从而提升异常检测？

论文隐含了几条研究假设：

- 正常样本具有可学习的上下文一致性，局部特征可以由周围特征合理预测。
- 异常样本破坏这种上下文一致性，因此在同样的掩码重建任务下会产生更高误差。
- 把遮挡重建任务嵌入中间层，比只在输入层做 masking 更灵活，也能增强现有模型的异常判别能力。
- 通道间依赖对重建质量重要，Transformer 通道注意力比 SE 注意力能提供更强建模能力。
- Huber loss 比 MSE 更适合异常检测中的自监督重建，因为它降低了异常噪声或极端误差对训练的干扰。
- 2D 图像、3D 医学体数据和视频虽然数据形态不同，但“正常上下文可预测、异常上下文难预测”这一机制具有跨域性。

## 6. 科学方法与技术路线

技术路线可以概括为“掩码卷积生成重建特征，Transformer 重标定通道，自监督损失约束模块，整体模型继续完成原异常检测任务”。

SSMCTB 的 2D 掩码卷积把卷积核中心设为不可见区域，只保留四个角落子核。设输入特征为 `X`，每个位置的中心特征被视为待预测目标，卷积只能使用中心周围、由膨胀率 `d` 控制距离的可见区域。输出 `Z` 与输入尺寸相同，因此可以逐位置比较重建结果和原特征。

3D 版本则把四个角落子核扩展为八个空间/深度角落子核，适合视频时空块或医学 3D 扫描。核心仍是遮住中心体素或中心特征，用周围 3D 上下文恢复。

通道 Transformer 的处理方式是：先对掩码卷积输出做平均池化，把每个通道压缩成 token；再经过线性投影、位置嵌入、多头自注意力和 MLP；最后通过 sigmoid 得到每个通道的权重，并与掩码卷积输出相乘。它的重点不是空间注意力，而是判断哪些重建通道更可信或更有用。

训练目标由原模型损失 `LF` 和模块自监督损失组成：`Ltotal = LF + λ * LSSMCTB`。`LSSMCTB` 使用 Huber loss 比较模块输出和原输入特征。作者大多采用 `λ=0.1`，但对个别原模型损失尺度较小的情况降为 `0.001`。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   图像工业缺陷使用 MVTec AD，包含 15 类对象/纹理、3629 张正常训练图和 1725 张测试图。医学影像使用 BRATS，作者重新构造异常检测划分：无病灶切片用于训练，有病灶切片进入测试。视频使用 Avenue 和 ShanghaiTech，训练集只有正常视频，测试集含异常。热成像使用作者从 Seasons in Drift 中标注的一周视频，形成 Thermal Rare Event。

2. 预处理  
   论文正文没有逐项展开所有 resize、归一化和采样细节，而是说明尽量沿用各基线官方实现和原论文超参数。视频任务中部分方法采用帧级输入，部分对象中心方法依赖目标区域或时空块；BRATS 则利用 MRI 切片，3D SSMCTB 版本进一步利用体数据结构。

3. 模型与基线  
   图像侧包括 NSA、DRAEM、FastViT+NSA。视频侧包括未来帧预测、Park 等人的 memory-guided autoencoder、Liu 等人的 flow/frame 混合方法、Georgescu 等人的伪异常对抗训练框架、Wang 等人的对象中心 Transformer、SSMTL++v2，以及 masked autoencoder。

4. 模块接入  
   大多数模型中，作者用 SSMCTB 替换倒数第二个卷积层。对 Georgescu 等人的方法，模块插入 decoder 的倒数第二个卷积层；对 ViT/MAE，则放在第一个 Transformer block 之前。通常只插入一个 SSMCTB。

5. 训练  
   保留原基线的 epoch、学习率、batch size 等设置。总损失为原任务损失加 SSMCTB 的 Huber 重建损失。通道 Transformer 默认设置为池化到 `1×1`，token 维度 64，4 个 head，2 个 Transformer block。

6. 指标  
   图像异常检测使用 detection AUROC、localization AUROC 和 localization AP。视频检测使用 frame-level micro AUC 和 macro AUC；定位使用 RBDC 和 TBDC，其中区域或轨迹与标注的 IOU/overlap 阈值设为 0.1。

7. 消融与敏感性  
   作者在 Avenue 上系统考察子核大小 `k'`、膨胀率 `d`、注意力类型、损失函数、插入位置、masked region 尺寸、Transformer 结构、Huber 的 `δ`，以及掩码卷积和普通膨胀卷积的差异。

8. 结果核查  
   主要核查方式是比较原基线、加入 SSPCAB、加入 SSMCTB 三组结果；同时展示 MVTec、BRATS、Avenue、ShanghaiTech、Thermal Rare Event 上的定性定位图或帧级异常曲线，观察异常分数是否覆盖真实异常区间。

## 8. 关键结果、结论与证据

在 MVTec AD 上，SSMCTB 对三个图像异常检测基线的 detection AUROC 普遍有提升。对 DRAEM 的 localization AUROC 提升不明显，但 localization AP 有约 2 个百分点收益；对 NSA 和 FastViT+NSA，定位 AUROC 也改善。定性图显示 SSMCTB 后的异常轮廓更贴近真实缺陷区域。

在 BRATS 上，提升更明显。DRAEM、NSA、FastViT+NSA 接入 SSMCTB 后，病灶检测和定位指标都有显著提升，而且 SSMCTB 始终比 SSPCAB 增益更大。3D SSMCTB 接入 DRAEM 后进一步提高，说明 3D 上下文对医学体数据有价值。

在 Avenue 和 ShanghaiTech 上，SSMCTB 对多种视频模型多数指标有效。尤其是与 3D SSMTL++v2 结合时，在 Avenue 上达到很高的 micro AUC、macro AUC 和 RBDC；在 ShanghaiTech 上，3D SSMCTB 也带来多个指标提升。曲线图显示，加入 SSMCTB 后模型对跑动、投掷、禁区骑车等异常片段的分数抬升更明显。

在 Thermal Rare Event 上，很多深模型或对象中心方法不适合热成像域，作者最终用 Park 的记忆自编码器作为底座。SSMCTB 对 micro AUC 的提升超过 SSPCAB，说明模块不只依赖 RGB 纹理，也能在热成像中利用上下文异常。

推理时间方面，SSMCTB 相比基线只增加约 0.2 到 0.4 ms 量级；相比 SSPCAB 增量也很小。论文据此认为性能收益超过计算开销。

## 9. 局限性与待解决问题

第一，论文的主要验证域仍是视觉异常检测，不是网络流量、主机日志或入侵检测。把 SSMCTB 迁移到网络安全数据时，需要重新定义“局部上下文”“通道 token”和“可重建正常模式”。

第二，异常检测数据集通常没有验证集，作者承认没有针对每个数据集和模型单独调参。虽然这避免了验证集缺失下的过拟合，但也意味着最优插入层、`λ`、`d`、Transformer 规模可能没有被充分探索。

第三，SSMCTB 的解释性仍有限。它能提高异常分数和定位轮廓，但论文没有深入分析 Transformer 通道权重究竟捕获了哪些语义或异常机制。

第四，重建误差作为异常分数仍有经典风险：某些异常可能与正常上下文高度相似，或者模型仍能恢复；某些正常但罕见模式也可能被误判。

第五，BRATS 划分是作者为异常检测重新构造的，是否与临床真实无监督筛查场景完全一致，还需谨慎看待。

第六，Thermal Rare Event 是新标注的小规模热成像异常集，异常类别和场景较窄，外推到更复杂热成像监控需要更多验证。

第七，本次正文包标记为未截断，因此没有明显因正文缺失导致的理解空白；但若用于正式复现实验，仍应回到 PDF 和官方代码核对实现细节、预处理脚本与超参数。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”的直接相关性较弱，因为它处理的是图像、医学影像和视频中的视觉异常，而非网络包、流、日志、系统调用或图结构攻击。

但方法思想有迁移价值：

- 对网络流量，可以把时间窗口内的多维特征矩阵视为类似 2D/3D 张量，遮挡某些时间-特征位置，用上下文恢复正常通信模式。
- 对主机行为序列，可以在 Transformer 或 1D CNN 中插入类似 masked convolution block，预测被遮住的事件嵌入。
- 对多源安全日志，可以把“通道维注意力”理解为不同日志字段、协议特征、端口行为、统计特征之间的依赖建模。
- Huber loss 对安全数据尤其有意义，因为真实正常流量中常混有噪声、突发流量和少量未标注异常。
- 可插拔设计适合给现有 IDS 模型加自监督辅助任务，而不是完全替换原模型。

需要注意的是，网络安全异常常包含强时序、离散符号、图关系和攻击策略演化，不能直接照搬 2D 图像卷积核。更合理的迁移是抽象其“局部遮挡-上下文恢复-异常残差”的机制。

## 11. 代码对照分析

本地代码包状态为“未发现；无”，因此无法对本地目录中的具体源码逐文件核验。论文正文中提到作者公开代码和 Thermal Rare Event 数据，地址为 `https://github.com/ristea/ssmctb/`，但本次任务没有提供该仓库代码包。

如果获取官方代码，最需要定位的文件应包括：

- 数据预处理：MVTec、BRATS、Avenue、ShanghaiTech、Thermal Rare Event 的 dataset/dataloader 文件，重点看图像 resize、MRI 切片选择、视频帧采样、异常标签读取。
- 模型模块：应存在 SSMCTB 或 masked convolution 的实现文件，核心对应 2D/3D masked convolution、channel-wise transformer、Huber loss。
- 基线接入：应有对 DRAEM、NSA、MAE、Park memory autoencoder、SSMTL++ 等模型的 wrapper 或修改版网络结构。
- 训练脚本：需要查 `λ` 权重、Huber `δ`、学习率、epoch、batch size，以及是否完全沿用基线默认配置。
- 评估脚本：应实现 image-level AUROC、pixel-level AUROC/AP、frame-level micro/macro AUC、RBDC/TBDC。
- 消融脚本或配置：应能切换 `d`、`k'`、attention type、masked region size、Transformer heads/token size/block 数。

从论文方法看，最核心代码对象应当是一个可替换卷积层的模块，其 forward 过程返回重建特征，并在训练阶段额外暴露 `LSSMCTB`。如果代码设计较规范，模型总 loss 中会有类似 `loss = base_loss + lambda_ssmctb * ssmctb_loss` 的组合逻辑。

## 12. 本篇精华

- SSMCTB 的关键贡献不是又做了一个异常检测模型，而是把 masked reconstruction 封装成可插拔网络块。
- 掩码卷积的中心不可见设计，使每个位置都必须由上下文恢复，避免模型直接复制局部输入。
- 通道维 Transformer 是为了建模重建特征图之间的依赖，不是传统 ViT 的空间 patch attention。
- Huber loss 替代 MSE 是一个务实改动：正常训练集中存在噪声时，对极端误差更稳健。
- 2D 和 3D 版本统一了图像、视频、医学体数据中的上下文恢复机制。
- 实验强点在于跨多个基线和多个领域验证，而不是只在单一模型上报最高分。
- 与网络异常检测的联系主要在自监督思想：用正常上下文可预测性构造异常分数。
- 真正可借鉴的是“在已有模型中加入中间层自监督约束”，而不是视觉卷积结构本身。

## 13. 建议精读路线

建议先读 Introduction 和 Method 的 Motivation，抓住作者为什么要把重建任务做成网络块，而不是只看公式。

第二步精读 2D/3D masked convolution。重点理解中心 masked region、周围 sub-kernel、膨胀率 `d` 如何共同决定上下文范围。

第三步读 channel-wise transformer。不要把它误解成普通 ViT；这里 token 是通道，目的是给重建通道分配注意力权重。

第四步读 loss 设计和总损失。关注 Huber loss、`λ`、以及模块如何与原模型训练目标相加。

第五步读实验表格时按“基线、+SSPCAB、+SSMCTB”三列比较，不要只看最高分。这样才能判断新模块相对旧模块的真实收益。

第六步重点看消融实验。Table II、VIII、IX、X、XI、XII 是理解设计选择的关键证据，尤其是 Huber、通道注意力、masked convolution 优于 dilated convolution 的部分。

第七步若服务网络安全课题，最后再回到方法抽象层：把图像中的“空间上下文恢复”改写成流量、日志或行为序列中的“时间-字段上下文恢复”。