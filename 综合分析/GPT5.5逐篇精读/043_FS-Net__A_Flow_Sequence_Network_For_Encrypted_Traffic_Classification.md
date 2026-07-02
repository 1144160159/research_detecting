# [043] FS-Net: A Flow Sequence Network For Encrypted Traffic Classification

## 1. 基本信息
- 题名：FS-Net: A Flow Sequence Network For Encrypted Traffic Classification，即“用于加密流量分类的流序列网络”。
- 作者：Chang Liu、Longtao He、Gang Xiong、Zigang Cao、Zhen Li。
- 发表：IEEE INFOCOM 2019，DOI：10.1109/INFOCOM.2019.8737507。
- 任务定位：加密流量的应用级分类，不解密、不依赖端口或明文负载签名。
- 输入对象：原始流序列，实验主输入为 packet length sequence。
- 正文包状态：本次提供正文未截断。
- 代码包：`source/Fs-net` 与 `source/WSPTTH_FS-Net`，后者更接近论文复现。

## 2. 中文翻译与核心摘要
这篇论文的核心意思是：加密让端口、负载签名和人工协议规则逐渐失效，而传统机器学习又严重依赖人工统计特征。FS-Net 试图把“特征学习”和“分类器训练”合成一个端到端模型，让模型直接从流量包长序列中学习应用指纹。

FS-Net 的结构类似“有监督分类 + 序列自编码器”的结合体。编码器用多层双向 GRU 从包长序列中提取全局序列表示；解码器把编码表示展开回序列层面，并通过重构原始序列迫使编码特征保留更多可区分信息；最后分类层用编码器特征、解码器特征及二者交互关系预测应用类别。论文在 18 个真实应用、约 95.6 万条加密流上取得 99.14% TPR、0.05% FPR 和 0.9906 FTF，显著超过 Markov 指纹类方法。

## 3. 论文解决的具体问题
论文解决的是闭集应用识别问题：给定一条加密流的序列表示，判断它属于 18 个已知应用中的哪一个。这里的关键不是发现未知攻击，而是在内容不可见的情况下，利用包长、消息类型等元数据序列恢复应用层差异。

作者针对三类旧方法的缺陷展开：端口法会被动态端口和通用端口破坏；负载签名法在加密后难以获得有效明文特征；传统机器学习方法需要人工设计最大包长、均值、字节分布、Markov 概率等特征，并且“先造特征、再训练分类器”的分段流程不能保证分类目标真正指导特征表示。

FS-Net 的目标是：让分类标签直接反向指导流序列表示学习，同时用重构任务约束表示不要丢失序列结构信息。

## 4. 创新点深度提炼
第一，论文把加密流量分类明确建模为流序列学习问题，而不是统计特征表格分类。包长序列不只是若干均值、方差或分布，而是带顺序的行为轨迹。

第二，FS-Net 用多层双向 GRU 替代一阶或二阶 Markov 模型。Markov 方法只能看相邻或短距离依赖，FS-Net 试图捕获整条流中的上下文关系，这对握手、证书、应用请求、数据传输阶段混合出现的流很重要。

第三，重构机制是本文最有辨识度的设计。分类损失只要求“够分类”，可能学到偏窄特征；重构损失要求编码表示还能恢复原始序列，从而迫使特征保留更多流形结构和细粒度差异。

第四，编码器特征和解码器特征共同参与分类。论文不是只拿 encoder 最终状态分类，而是认为 decoder 在逐步重构时会形成另一种细粒度表示，因此将 `ze`、`zd`、逐元素乘积和绝对差拼接，再经过 dense 层压缩。

第五，FS-Net 设计上可扩展到多属性序列。论文实验中把 message type sequence 与 packet length sequence 组合为 FS-Net-SL，说明该框架可以并行建模多个流属性。

## 5. 科学问题与研究假设
核心科学问题是：加密流量在内容被隐藏后，是否仍然存在稳定、可学习、可泛化的序列侧信道特征，足以区分应用？

论文隐含了几条研究假设。其一，不同应用的协议实现、交互模式、对象大小和请求节奏会在包长序列中留下稳定模式。其二，深度序列模型能比低阶 Markov 链更充分地捕获这些模式。其三，端到端监督学习比人工特征加传统分类器更适合任务目标。其四，重构任务可以作为辅助约束，提高表示的判别性。其五，包长序列比粗粒度 message type 序列包含更多分类信息。

## 6. 科学方法与技术路线
FS-Net 的技术路线是：原始流序列输入、embedding 表示、多层双向 GRU 编码、多层双向 GRU 解码、序列重构、特征融合、softmax 分类、联合损失训练。

具体来说，包长值先通过 embedding 层映射为向量。编码器从正向和反向读取序列，每层最终隐状态拼接成 `ze`。解码器将 `ze` 在每个时间步重复输入，生成重构用的 decoder outputs，同时取最终状态形成 `zd`。重构层对每个时间步预测原始包长元素；分类层根据组合特征预测应用标签。

损失函数是 `L = LC + αLR`。`LC` 是应用分类交叉熵，`LR` 是序列重构交叉熵，`α` 控制重构任务权重。这个设计让模型同时受到“分得准”和“记得住原始序列”的约束。

## 7. 实验设计与实验步骤
数据：使用前作 [11] 的真实校园网数据，采集 7 天，经过 packet recombination 和 flow reduction 后得到 18 个应用、约 95.6 万条加密流。类别明显不均衡，例如 Baidu 约 37.3 万条，QQ、Apple、Gmail 也远多于 Mozilla、Sogou 等小类。

预处理：将每条流表示为同长度语义下的序列，主实验采用 packet length sequence；对 message type sequence 和二者组合也做变体实验。论文没有展开数据清洗细节，因此复现实验时需要回到数据生成脚本核查流截断、padding、包长离散化和训练测试划分。

模型/基线：FS-Net 对比 FoSM、SOCRT、SOB、FoLM、SOB-L、MaMPF。前几类主要是 message type 或 packet length 的 Markov 指纹方法，MaMPF 则结合多属性 Markov 概率和随机森林。

训练：论文设置 packet length embedding 维度 128，GRU hidden 维度 128，encoder 和 decoder 均为 2 层 bi-GRU，dropout 0.3，Adam 学习率 0.0005，主表中 `α=1`，采用 5-fold cross validation。

指标：使用各类 TPR、FPR，以及加权总体 `TPR_AVE`、`FPR_AVE` 和 FTF。FTF 本质上奖励高 TPR、惩罚高 FPR，并按类别流量占比加权。

消融/敏感性：消融包括去掉 decoder/reconstruction 的 FS-ND、只用 message type 的 FS-Net-S/FS-ND-S、多属性输入的 FS-Net-SL/FS-ND-SL。敏感性分析考察 hidden 维度从 4 到 512、`α` 从 0.125 到 256 的影响。

结果核查：主表应同时看总体指标和逐应用指标。FS-Net 在 17/18 个应用上取得最高 TPR，OneNote 不是最高 TPR，但 FPR 为 0。多属性 FS-Net-SL 略高于 FS-Net，但提升极小，说明包长序列已经吸收了大部分有效信息。

## 8. 关键结果、结论与证据
最强结果来自 Table II：FS-Net 达到 `TPR_AVE=0.9914`、`FPR_AVE=0.0005`、`FTF=0.9906`。相比之下，MaMPF 为 `0.9632 / 0.0020 / 0.9567`，SOB-L 为 `0.9385 / 0.0034 / 0.9328`。这说明端到端序列模型不仅超过传统 Markov 指纹，也超过结合多属性与随机森林的分段式方法。

消融结果更能支撑论文主张。FS-ND 去掉 decoder 和重构机制后，FTF 从 0.9906 降到 0.9798，约 1 个百分点差距，说明重构不是装饰性模块。message type-only 的 FS-Net-S 只有 0.7248 FTF，远低于 packet length 输入，证明包长序列在该任务中更有判别力。FS-Net-SL 达到 0.9911 FTF，只比 FS-Net 略高，说明 message type 对包长的补充有限。

敏感性分析表明 hidden 维度增大通常提升 TPR/FTF、降低 FPR，但 128 之后收益变小，训练成本和过拟合风险上升。`α` 在 0.125 到 2 之间表现稳定，过大时重构任务压过分类任务，性能下降。

## 9. 局限性与待解决问题
第一，这是闭集应用分类，不是开放世界异常检测。模型默认测试样本属于已知 18 类之一，对未知应用、协议版本迁移、恶意伪装和分布漂移没有系统处理。

第二，数据来自特定校园网环境和特定时期的应用流量，泛化到移动网络、企业网、QUIC/HTTP3、大规模 CDN 或流量填充场景仍需重新验证。

第三，论文主要依赖包长序列，时间间隔、方向、burst 结构、TLS/QUIC 握手元数据等没有被充分联合建模。包长很强，但也容易受到 padding、分片策略、代理和隧道影响。

第四，随机 5 折交叉验证可能高估跨时间、跨用户、跨网络环境的泛化能力。更严格的复核应使用按时间切分、按用户/主机切分、跨网络采集测试。

第五，重构机制提升了精度，但也增加了训练成本。论文没有充分讨论在线部署延迟、吞吐、模型压缩和资源约束。

第六，源码复现与论文设置存在差异，尤其不同仓库的 embedding 维度、学习率、dropout、重构权重和特征融合实现并不完全一致，需要谨慎对照。

## 10. 与本项目的关系
这篇论文与“异常检测”项目强相关，但它本身更准确地说是加密流量应用识别和流量指纹学习。对异常检测项目的价值在于：FS-Net 提供了一种从加密流量元数据中学习序列表示的方法，可以把 encoder 表示作为下游异常检测、恶意流量识别、未知流量聚类或跨域迁移的基础特征。

如果项目目标是恶意加密流量检测，FS-Net 可作为两类模块使用：一是监督式分类器，用于识别已知应用或已知恶意家族；二是表示学习器，用 `ze/zd` 或重构误差支持 OOD 检测、异常分数建模。需要注意的是，直接把 FS-Net 当异常检测模型会不够严谨，因为论文没有解决未知类拒识、概念漂移和告警阈值校准。

## 11. 代码对照分析
`source/WSPTTH_FS-Net` 更接近论文方法。运行入口在 [main.py](<F:/泉城实验室/二期/论文/异常检测/source/WSPTTH_FS-Net/main.py:25>)，README 给出的流程是 `python main.py --mode=prepro`、`python main.py --mode=train`、`python main.py --mode=test --test_json=... --test_model_dir=...`。它默认 `class_num=18`、`hidden=128`、`layer=2`，与论文主设置一致；但 `length_dim=16`、`learning_rate=0.001`、`rec_loss=0.5`，和论文中的 embedding 128、学习率 0.0005、`α=1` 不完全一致。

数据预处理在 [preprocess.py](<F:/泉城实验室/二期/论文/异常检测/source/WSPTTH_FS-Net/preprocess.py:12>)。README 说每个 `.num` 文件一类应用，每行由 status sequence 和 packet length sequence 组成，中间用 `;` 分隔。代码实际读取的是 `;` 后面的包长序列，截断过大包长，将包长按 block 映射到离散 id，并保留 `0/1/2` 给 PAD/START/END。数据加载在 [dataset.py](<F:/泉城实验室/二期/论文/异常检测/source/WSPTTH_FS-Net/dataset.py:12>)，会给每条流加 START/END，并按最大长度过滤。

模型主体在 [model.py](<F:/泉城实验室/二期/论文/异常检测/source/WSPTTH_FS-Net/model.py:101>)。`_embedding` 对应论文 embedding layer，`_encoder` 对应多层 bi-GRU encoder，`_decoder` 和 `_reconstruct` 对应 decoder 与 reconstruction layer，`_classify` 对应 softmax 分类。需要特别注意：论文 dense feature 使用 `[ze, zd, ze*zd, |ze-zd|]`，而该实现的 `_make_graph` 只拼接 `[e_fea, d_fea]` 后压缩；文件里虽有 `_fusion`，但主图没有调用它。

训练和评估在 [train.py](<F:/泉城实验室/二期/论文/异常检测/source/WSPTTH_FS-Net/train.py:13>) 与 [eval.py](<F:/泉城实验室/二期/论文/异常检测/source/WSPTTH_FS-Net/eval.py:71>)。训练使用 TensorFlow 1.x、Adam、梯度裁剪、checkpoint 评估；评估计算 TPR、FPR 和 FTF，指标与论文一致。

`source/Fs-net` 更像简化实验，不建议当作论文忠实复现。其 [model.py](<F:/泉城实验室/二期/论文/异常检测/source/Fs-net/model.py:3>) 中 `n_outputs=4`，训练脚本 [train.py](<F:/泉城实验室/二期/论文/异常检测/source/Fs-net/train.py:10>) 使用的是 `dataset_pcap_length.py`，类别是 `iqiyi/taobao/weibo/weixin` 四类。`build_loss()` 调用 `tinny_fs_net()`，并把 `ae_loss=0`，所以实际训练没有论文强调的重构损失。另一个 `build_fs_net_loss()` 分支包含拼写错误 `sparse_softmax_cross_entrop...`，且 embedding 分支也没有真正用于 encoder。日志显示该仓库曾在 4 类数据上得到约 0.9649 test accuracy，但这不能和论文 18 应用结果直接比较。

## 12. 本篇精华
- FS-Net 的关键不是“用了 RNN”，而是把加密流量分类从人工统计特征工程改成端到端流序列表示学习。
- 包长序列在该数据集上远强于 message type sequence，是应用级加密流量指纹的主信息源。
- 多层双向 GRU 解决的是低阶 Markov 链看不到长距离上下文的问题。
- 重构机制提供了辅助自监督约束，使 encoder 表示不只服务分类边界，也保留原始序列结构。
- FS-Net 在 18 应用真实数据上达到 0.9906 FTF，显著超过 MaMPF 的 0.9567。
- 消融显示去掉 decoder/reconstruction 后 FTF 降至 0.9798，证明重构模块有实际贡献。
- 该方法适合作为加密流量异常检测的表征模块，但不能直接等同于开放集异常检测模型。
- 复现优先看 `WSPTTH_FS-Net`，但要记录其与论文超参数和特征融合公式的差异。

## 13. 建议精读路线
先读 Introduction，抓住作者为什么反对“人工特征 + 分类器”的分段范式。然后精读 Section IV，尤其是 encoder、decoder、reconstruction layer、dense feature 组合和联合损失。接着看 Table II 和 Table III，把“端到端优于 Markov”“重构机制有效”“包长优于 message type”三条证据串起来。

复现时先跑 `WSPTTH_FS-Net` 的预处理、训练、评估流程，再对照论文修改 embedding 维度、学习率、dropout、`rec_loss/α` 和 dense feature 拼接方式。最后再考虑把 encoder 表示迁移到本项目的异常检测任务中，优先做按时间切分和未知类测试，而不是只复现随机划分准确率。

<!-- codex-cli-deep-read: complete -->
