# [851] Towards Open Set Deep Networks

## 1. 基本信息

- 论文：Towards Open Set Deep Networks
- 作者：Abhijit Bendale, Terrance E. Boult
- 会议：CVPR 2016
- DOI：10.1109/CVPR.2016.173
- 主题：开放集识别、深度网络异常/未知类拒识、SoftMax 校准、极值理论、Meta-Recognition
- 本地 PDF：`paper/10.1109_CVPR.2016.173.pdf`
- 代码状态：本地未发现该论文对应代码包

## 2. 中文翻译与核心摘要

这篇论文要解决的是：传统深度分类网络默认测试样本一定属于训练时见过的类别，因此 SoftMax 必须在已知类别里选一个答案。现实环境不是闭集，系统会遇到未知类别、无意义图像、攻击性构造图像或分布外输入。SoftMax 的高置信度并不等于“样本可信”，尤其面对 fooling images 时，网络会把人类看不出语义的图像判成某个类别并给出极高概率。

作者提出 OpenMax，把最后的 SoftMax 层改造成可显式分配“未知类”概率的层。核心做法不是直接阈值化 SoftMax，而是在倒数分类激活层的 activation vector 上建立每类的平均激活向量 MAV，并用极值理论拟合“正确训练样本到 MAV 的尾部距离”。测试时，如果样本的激活模式偏离某个已知类的典型模式，OpenMax 就削弱该类激活，并把削弱掉的激活质量转移给 unknown 类。

一句话概括：OpenMax 把“分类置信度”改造成“已知类相似性 + 未知风险”的联合估计，使深度网络第一次在形式上满足开放集识别中的开放空间风险控制。

## 3. 论文解决的具体问题

论文针对的是深度网络在开放世界部署中的一个基础缺陷：模型只能在训练类别集合内做归一化判断，无法表达“这不是任何已知类别”。

具体问题包括：

1. SoftMax 的闭集归一化会强迫未知输入落入某个已知类。即使输入是无意义图像或未见类别，概率总和仍为 1。
2. 简单设置 SoftMax 置信度阈值只能拒绝“不确定样本”，但不能可靠拒绝“错误但高置信样本”。
3. fooling images 说明深度网络可以被构造出高置信但无语义的输入，这类风险不是普通闭集准确率能反映的。
4. 传统开放集识别要求控制 open space risk，即不要在远离训练样本的区域仍然大量赋予已知类标签。深度网络此前缺少这类形式化保证。
5. 对抗样本与开放集样本不同：对抗样本在像素空间可能接近训练样本，但在某些深层激活空间中可能偏离目标类别的典型激活结构。论文尝试用 activation vector 捕捉这种偏离。

## 4. 创新点深度提炼

第一，论文把开放集风险从像素空间转移到深度激活空间。作者认为，对深度网络而言，是否“远离已知类”不应主要在原始像素中衡量，而应在网络已经学习出的类别相关激活模式中衡量。

第二，提出 activation vector 的多类 Meta-Recognition。论文不是只看某一个类别 logit，而是看整个类别激活向量。一个真实 hammerhead shark 图像不仅会激活 hammerhead，还可能同时激活其他鲨鱼、鲸、鱼类等相关类别；而 fooling image 往往只人为推高目标类，缺少这种相关类别的自然激活结构。

第三，用 EVT/Weibull 拟合每类正确训练样本的尾部距离。作者只使用被网络正确分类的训练样本来计算每类 MAV，并对距离分布的最大尾部拟合 Weibull，进而估计测试样本是否是该类的离群点。

第四，OpenMax 引入 unknown 类概率。它对 top-α 类别的激活进行按距离衰减，把被削弱的激活量累计到未知类，再做类似 SoftMax 的归一化。

第五，论文给出形式化论证：OpenMax 中的 Weibull CDF 随距离单调变化，构成 compact abating probability，因此阈值化后可以控制开放空间风险。这是它区别于普通置信度阈值的理论支撑。

## 5. 科学问题与研究假设

核心科学问题是：深度网络中是否存在一个特征空间，使未知类、fooling images 和部分对抗样本相对于已知类别表现为可识别的离群点？

论文的主要假设包括：

1. 倒数分类激活层包含类别之间的语义相关结构，不只是独立类别分数。
2. 同一已知类的正确样本在 activation vector 空间中围绕某个典型激活模式聚集。
3. 未知输入或 fooling input 即使能得到高 SoftMax 分数，其整体激活模式仍可能偏离已知类训练样本的典型分布。
4. 每类距离分布的尾部可用极值理论建模，特别是 Weibull 分布可以估计“样本不像该类”的风险。
5. 在开放集识别中，应同时使用 unknown 概率拒识和低置信度拒识；两者解决的问题不同。

## 6. 科学方法与技术路线

技术路线可以概括为“训练后校准”，不重新训练 AlexNet 主体。

1. 使用已有闭集深度网络，例如 Caffe Model Zoo 中的 BVLC AlexNet。
2. 对训练集样本前向传播，取 SoftMax 前一层的 activation vector。
3. 对每个类别，只保留被网络正确分类的训练样本。
4. 计算每个类别的 Mean Activation Vector，即 MAV。
5. 计算该类正确样本 AV 到 MAV 的距离。论文实验中使用归一化欧氏距离与余弦距离的加权组合。
6. 对每类距离分布的尾部进行 Weibull 拟合，得到每类 Meta-Recognition 模型。
7. 测试时对输入图像得到 AV，找 top-α 激活类别。
8. 对 top-α 类别，根据其到对应 MAV 的距离计算衰减权重。
9. 被衰减掉的激活量转移给 unknown 类。
10. 对已知类和 unknown 类一起归一化，得到 OpenMax 概率。
11. 若 unknown 类概率最大，或最大已知类概率低于阈值，则拒识。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 ILSVRC 2012 作为已知类闭集数据，包含 1000 类。训练集约 130 万张，验证集 5 万张。由于测试集标签不可用，评估使用验证集。未知类来自 ILSVRC 2010 中未进入 ILSVRC 2012 的约 360 个类别。fooling images 使用 Nguyen 等人生成的高置信无语义图像，每个 2012 类别约 15 张，共 15000 张。

2. 预处理  
   使用 Caffe BVLC AlexNet 的标准输入流程，并保留多 crop/channel 输出。论文中测试激活为 1000×10，对应 1000 个类别和 10 个 crop/channel。

3. 模型与基线  
   主模型是预训练 AlexNet + OpenMax。基线包括原始 SoftMax、SoftMax 加置信度阈值、以及在 FC8 特征上训练的 1-vs-set 开放集线性模型。

4. 训练/校准  
   不重新训练 CNN。对训练集前向传播，提取 FC8 activation vector。每类仅使用训练阶段被正确 top-1 分类的样本计算 MAV。然后计算样本到 MAV 的距离，对最大尾部距离做 Weibull 拟合。尾部大小通过保留数据调参，最终实验中整体 tail size 为 20。

5. 测试  
   测试集由 50000 张 ILSVRC 2012 验证图像、15000 张未知类图像、15000 张 fooling images 组成。每张图像先通过 AlexNet 得到 AV，再通过 OpenMax 重分配已知类和 unknown 类概率。

6. 指标  
   使用 F-measure 评估开放集性能。原因是开放集下 accuracy 可能被大量 true negative 扭曲，F-measure 更关注已知类正确识别与未知类错误接收之间的平衡。

7. 消融/敏感性  
   正文主要展示概率阈值变化下 SoftMax-threshold 与 OpenMax 的 F-measure 曲线。论文还提到补充材料分析了不同距离度量和 OpenMax 参数变化，如 α、tail size、距离形式等。

8. 结果核查  
   重点核查三类结果：OpenMax 是否保持已知类识别能力；是否比 SoftMax 阈值更能拒绝未知类；是否能显著拒绝 fooling images。还需关注被 OpenMax 拒绝的已知类样本中是否存在多目标、标注歧义或定位问题。

## 8. 关键结果、结论与证据

论文的关键结果是 OpenMax 明显优于 SoftMax 阈值法。图 3 中，OpenMax 相比最优 SoftMax-threshold 有约 4.3% 的准确性提升，相比原始深度网络有约 12.3% 提升。在 80000 张测试图像上，论文称 OpenMax 比 SoftMax 多正确处理 3450 张，比基础深度网络多 9847 张。

在 fooling image 检测上，OpenMax 的优势更明显。原因是 fooling image 往往只操纵目标类激活，使 SoftMax 分母结构发生变化，但没有同时形成真实图像应有的“相关类别激活模式”。因此在 AV 空间中，它们距离 MAV 更远。

1-vs-set 基线在 FC8 上的 F-measure 约为 0.407，而 OpenMax 达到约 0.595。这说明简单把传统开放集线性分类器套在深度特征上，不如直接利用深度分类层激活结构进行后校准。

论文还指出 OpenMax 能发现一些训练或验证中的“问题图像”，例如一张图像同时包含 agama 和 jeep，原始标签是 agama，但整体图像的激活模式可能更接近 jeep。局部裁剪后，OpenMax 又能分别接受 jeep 区域和 agama 区域。这说明拒识不一定只是失败，也可能揭示多目标、定位不足或标注语义不完整。

## 9. 局限性与待解决问题

第一，单个 MAV 表达能力有限。一个类别可能有多视角、多场景、多上下文，例如棒球在桌面上和投手手中，对应的相关类别激活模式可能不同。单均值模型会把复杂类内结构压成一个中心。

第二，OpenMax 对细粒度近邻对抗样本不一定有效。作者明确承认，如果 adversarial image 从 hammerhead shark 变成 great white shark 这类相近类别，AV 可能仍然相似，拒识会失败。

第三，unknown 类样本的选择会影响实验结果。论文使用 ILSVRC 2010 中未进入 2012 的类别，但真实开放世界中的未知分布更复杂，无法靠有限未知类完全代表。

第四，OpenMax 是训练后校准方法，没有从训练目标上直接优化开放集边界。它依赖原始网络学到的激活结构，如果基础网络表示不稳定，OpenMax 的 MAV/Weibull 校准也会受影响。

第五，论文主要在图像分类上验证，尚未直接覆盖网络安全异常检测中的时序流量、日志序列、协议字段、攻击阶段迁移等问题。迁移到安全场景时，需要重新定义 activation vector、类别语义相关性和距离度量。

第六，正文包未被截断，本次理解覆盖了提供正文的主要内容；但若用于正式复现，仍建议回到 PDF 检查图表细节和补充材料中的参数敏感性实验。

## 10. 与本项目的关系

这篇论文与“异常检测”项目的关系是中高相关，尤其适合作为“闭集分类器如何扩展到未知攻击/未知异常拒识”的基础论文。

在网络安全中，常见模型会把流量或日志分类为已知攻击族、恶意类型或正常类别。但真实部署中会出现未知攻击、变种攻击、噪声流量、混合行为和分布漂移。OpenMax 的价值在于提供一种思路：不要只相信分类器输出的最大概率，而要检查样本在深层表示空间中是否符合该类的典型激活模式。

可迁移启发包括：

1. 对每个已知攻击类别建立深层表示中心，而不是只看最终分类概率。
2. 对类内距离尾部建模，用于估计未知风险。
3. 把“未知攻击/未知异常”作为显式输出，而非事后人工解释。
4. 对安全模型的高置信误报进行 Meta-Recognition 校准。
5. 在增量学习或开放世界检测中，把拒识样本交给人工分析，再纳入新类别。

需要注意的是，网络安全数据通常不是自然图像，类别相关结构未必像 ImageNet 那样稳定。特征空间、距离函数、时间窗口和类别粒度会决定 OpenMax 思路是否有效。

## 11. 代码对照分析

本地未发现该论文对应代码包，因此不能给出实际源码文件级对应关系。根据论文方法，若复现 OpenMax，代码通常应拆成以下功能模块：

1. 数据预处理  
   对应功能：加载 ImageNet 或安全数据，执行模型输入标准化，生成 train/val/open/fooling 划分。  
   可能文件形态：`data_loader.py`、`preprocess.py`、`make_open_set_split.py`。

2. 特征/激活提取  
   对应论文：提取 FC8 activation vector，保留 10 crop/channel。  
   可能文件形态：`extract_activations.py`、`caffe_forward.py`、`features.py`。

3. MAV 计算  
   对应 Algorithm 1 第 1-2 行：每类仅使用正确分类训练样本计算均值激活向量。  
   可能文件形态：`compute_mav.py`、`calibration.py`。

4. Weibull/EVT 拟合  
   对应 Algorithm 1 第 3 行：使用 libMR 的 `FitHigh` 拟合尾部距离。  
   可能文件形态：`weibull_fit.py`、`libmr_wrapper.py`、`evt.py`。

5. OpenMax 推理  
   对应 Algorithm 2：top-α 类别重校准、unknown 激活累计、OpenMax 概率计算和拒识。  
   可能文件形态：`openmax.py`、`inference.py`。

6. 评估  
   对应图 3、图 4：计算 F-measure，比较 SoftMax、SoftMax-threshold、OpenMax、1-vs-set。  
   可能文件形态：`evaluate.py`、`metrics.py`、`plot_results.py`。

运行线索上，复现至少需要 Caffe/BVLC AlexNet、ImageNet 2012 验证集、ILSVRC 2010 未知类子集、Nguyen fooling images、libMR。论文不是端到端训练新网络，而是对预训练网络做后处理校准。

## 12. 本篇精华

1. SoftMax 的问题不是“概率不够准”这么简单，而是闭集归一化机制本身无法表达未知类。
2. OpenMax 的关键洞察是：真实样本的类别激活不是孤立峰值，而是有相关类别共同响应的结构。
3. fooling image 能骗过 SoftMax，是因为它能制造目标类高分；但它通常骗不过整体 activation vector 的类相关模式。
4. 用正确分类训练样本计算 MAV，相当于为每个类别建立“可信激活原型”。
5. EVT/Weibull 的作用是建模类内距离尾部，而不是建模全部样本分布。
6. OpenMax 把偏离已知类的激活质量转移给 unknown 类，从机制上打破“必须属于 1000 类之一”的限制。
7. 论文的重要性在于同时给出工程方法、开放集实验和 open space risk 的形式化论证。
8. 对异常检测项目而言，它提供了从闭集攻击分类走向未知攻击拒识的一条经典技术路线。

## 13. 建议精读路线

建议先读 Introduction，抓住 SoftMax 闭集假设、fooling images 和 open set recognition 的矛盾。

然后重点读 2.1 和 2.2，理解 activation vector 为什么不是单类分数，而是类别相关结构。这里是论文最有启发的部分。

接着读 Algorithm 1 和 Algorithm 2，把 MAV、Weibull 拟合、top-α 重校准、unknown 激活累计连成完整流程。

再读 2.4 的定理，理解 OpenMax 为什么比普通 SoftMax 阈值更接近形式化开放集识别。

最后读实验部分，重点看数据构成、F-measure 计算方式、SoftMax-threshold 对照和 fooling images 拒识结果。对本项目复用时，应优先思考如何在安全数据中定义类似 activation vector 的稳定表示空间。