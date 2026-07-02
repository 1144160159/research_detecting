# [150] Rosetta: Enabling Robust TLS Encrypted Traffic Classification in Diverse Network Environments with TCP-Aware Traffic Augmentation

## 1. 基本信息

- 论文主题：TLS 加密流量分类在不同网络环境下的鲁棒性。
- 年份：2023。
- DOI：10.1145/3603165.3607437。
- 正文显示会议版本：32nd USENIX Security Symposium 2023；元数据来源标为 ACM Turing Award Celebration Conference - China 2023，建议后续引用时以 PDF 首页和 DOI 页面复核。
- 本地 PDF：`paper/10.1145_3603165.3607437.pdf`。
- 本地正文包：`综合分析/_data/full_text_cache_plain/150.txt`，本次未截断。
- 代码目录：[source/Rosetta](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta>)。

## 2. 中文翻译与核心摘要

题名可译为：**Rosetta：通过 TCP 感知流量增强，在多样网络环境中实现鲁棒 TLS 加密流量分类**。

这篇论文的核心不是再提出一个更复杂的分类器，而是指出一个更基础的问题：很多基于包长序列的深度学习加密流量分类模型，在离线数据集上很准，但换到不同网络环境后会明显失效。原因不是 TLS 内容变了，而是 TCP 的可靠传输机制会改变观察到的包长序列，例如重传导致的子序列移位/重复、Nagle/MTU/RTT 导致的包大小变化。Rosetta 用 TCP 机制驱动的数据增强生成同一流的多种“网络环境变体”，再用 BYOL 式自监督学习训练 Traffic Invariant Extractor，提取对这些 TCP 扰动不敏感的特征，供 CNN、LSTM、DF、FS-Net、Transformer 等既有分类器使用。

## 3. 论文解决的具体问题

论文解决的是**加密流量分类的跨网络环境泛化问题**。以往方法默认训练集和测试集包长序列分布相近，因此在同一离线数据集切分上能达到很高准确率；但真实部署时，路径、时延、丢包、无线接入、MTU、路由变化都会改变 TCP 层表现，使同一网站/应用生成的 TLS 流在包长序列上看起来像另一类。

更具体地说，论文要解决三个层面的失配：

- 输入失配：同一 TLS 流在不同网络环境下的 packet length sequence 发生结构变化。
- 表征失配：深度模型中倒数第二层的特征向量随环境漂移，不能稳定表示“同一流”。
- 部署失配：训练环境有限，而真实网络环境时变且不可穷举，周期性重训和人工标注成本高。

## 4. 创新点深度提炼

1. **把环境鲁棒性作为加密流量分类的核心问题**：论文系统测试六类主流模型，证明高离线精度不能代表真实部署鲁棒性。

2. **将性能下降归因到 TCP 机制，而不是泛泛归因于噪声或域偏移**：作者把包长序列变化拆成子序列移位、子序列重复、包大小变化，并对应到 RTO、fast retransmit、Nagle、MTU、RTT 等机制。

3. **TCP-aware traffic augmentation**：增强不是随机 mask/swap，而是按 TCP 传输语义生成可能出现的流量变体，使增强样本更接近真实环境扰动。

4. **自监督学习提取流量不变量**：Rosetta 用 BYOL 将同一原始流的不同增强版本拉近，训练出 TIE，使后续分类器看到的是更稳定的特征向量，而不是原始易漂移包长序列。

5. **插件式兼容既有分类器**：Rosetta 不要求重写 CNN、LSTM、DF、FS-Net、Transformer，只需把输入改成 TIE 输出的特征向量。

## 5. 科学问题与研究假设

科学问题一：基于包长序列的深度模型是否能跨网络环境稳定分类 TLS 流？  
论文的回答是否定的。CIRA-CIC-DoHBrw-2020 上，训练在 θ0 时，六个模型平均 F1 在 θ0 为 96.98%，但在 θ3 降到 37.89%，在 θ6 降到 39.97%。

科学问题二：这种失效是否由 TCP 层可解释机制导致？  
论文假设并验证：TLS 建立在 TCP 上，网络环境变化会通过 TCP 可靠传输和分段/合并机制改变包长序列。

科学问题三：如果模型学习 TCP 语义下的不变量，是否能提升跨环境鲁棒性？  
Rosetta 的实验支持该假设：在多个 replayed 和 real TLS 场景中，TIE+分类器显著优于原始分类器。

## 6. 科学方法与技术路线

论文技术路线分三步：

1. **测量与诊断**：在多种有线/无线环境中 replay 或真实采集 TLS 流，用六类模型评估跨环境性能，并观察特征向量相似度和 t-SNE 分布漂移。

2. **机制建模与增强**：基于 TCP 机制设计五类增强算法，覆盖 RTO/fast retransmit 造成的子序列重复与移位，以及 RTT/MSS/Nagle/MTU 造成的包大小变化。

3. **不变量学习与分类**：用增强后的一对同源流变体作为 BYOL 正样本对，训练 TIE；下游分类时，先由 TIE 提取鲁棒特征，再训练常规深度分类器。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：使用 CIRA-CIC-DoHBrw-2020、ISCX-VPN 做 replayed TLS 实验；另采集真实网站 TLS 流约 180 万条、真实应用 TLS 流 292,523 条。

2. 网络环境：replayed 实验构造 θ0 到 θ6，包括本地 LAN、中国/韩国/美国到中国的有线路径，以及 Wi-Fi、4G LTE、3G WCDMA；真实流量实验构造 τ1 到 τ6。

3. 预处理：抽取每条 TLS 流的包长序列；序列长度固定为 100，长序列截断，短序列补零；replay 前去除原数据集中重复包并按时间戳重排。

4. 模型/基线：CNN、SDAE、LSTM、DF、FS-Net、Transformer；另比较 Random Mask、Random Swap 两类非 TCP 语义增强。

5. 训练：先在单一环境训练分类器，再直接测试其他环境；Rosetta 中，TIE 用第三方 TLS 数据集通过 TCP-aware augmentation 生成变体并自监督训练，下游分类器只使用 TIE 特征训练。

6. 指标：Accuracy、F1-score；敏感性实验还看 recall 和 false positive rate。

7. 消融/敏感性：分别控制丢包率、时延、MTU；移除五个增强算法或移除 TIE 做消融；比较 TCP-aware augmentation 与 RM/RS。

8. 结果核查：重点核查跨环境性能，而不是只看同环境测试；同时核查特征向量分布是否在不同环境中保持接近。

## 8. 关键结果、结论与证据

- **原始模型跨环境明显退化**：CIRA replayed 流量中，θ0 训练下平均 F1 从 96.98% 降到 θ3 的 37.89%、θ6 的 39.97%。
- **真实流量同样退化**：真实网站 TLS 流中，平均 F1 从 τ1 的 83.53% 降到 τ3 的 63.71%；真实应用流中，τ2、τ3 平均 F1 分别降到 63.88%、65.11%。
- **Rosetta 显著提升鲁棒性**：CIRA 上 Rosetta 在 θ2、θ3、θ6 的平均 F1 分别提升 41.18%、44.65%、39.17%。
- **受控环境验证了机制解释**：DF 在 50 ms delay 下准确率约降到 55%，启用 Rosetta 后仍保持 86% 以上；MTU 降到 700 bytes 时，原始 DF F1 低于 70%，Rosetta 仍能保持约 80% 以上 F1。
- **TCP 语义增强优于通用增强**：RM/RS 平均 F1 约 47.73%/46.72%，TCP-aware augmentation 达到 87.49%。
- **消融说明包大小变化很关键**：去掉 Algorithm 5 后准确率只有 60.42%、F1 只有 41.32%，说明 RTT/MSS/Nagle/MTU 相关增强对鲁棒性贡献很大。

## 9. 局限性与待解决问题

本次正文包未截断，因此主要理解不受正文缺页影响。但论文把五个 TCP-aware augmentation 的详细伪代码放到了额外技术报告中，若要严格复现算法细节，仍需回到 PDF 附录和技术报告核对。

主要局限包括：

- Rosetta 针对 TCP 上的 TLS，不能直接覆盖 QUIC/HTTP3 等 UDP 加密流量。
- 方法主动舍弃 timing information，提升环境鲁棒性的同时可能损失某些网站指纹任务中的判别信号。
- 论文关注自然网络环境变化，对主动规避、流量填充、防御性 traffic morphing 的鲁棒性讨论不足。
- 需要预训练 TIE，且完整第三方数据集并未完全公开，复现实验存在数据可得性问题。
- 在训练环境与测试环境相近时，Rosetta 有时会带来轻微精度下降，这是鲁棒特征与环境特异特征之间的取舍。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，因为它指出：网络安全模型的错误不一定来自攻击样本复杂，而可能来自**网络环境导致的输入分布漂移**。如果本项目涉及加密流量恶意检测、应用识别、VPN/Tor/DoH 检测或跨域部署，Rosetta 的思路可以作为一个通用前置模块：先学习 TCP 语义不变量，再做异常/类别判别。

对项目可借鉴的方向：

- 用 TCP-aware augmentation 做跨环境数据增强，降低对单一采集环境的过拟合。
- 用 BYOL/SimSiam 类自监督方法预训练流量编码器，减少标注依赖。
- 在异常检测评估中必须加入跨地域、跨接入、跨时延/丢包/MTU 的测试集，而不能只做随机划分。
- 对 QUIC、HTTP/3、移动网络弱网场景，需要设计类似的协议感知增强，而不能照搬 TCP 规则。

## 11. 代码对照分析

代码能对应论文主线，但工程质量偏研究原型。

- README：说明 TIE 训练代码、部分增强数据、test-app/test-web 数据位置，见 [README.md](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/README.md>)。
- TIE 入口：[main.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/main.py:31>) 读取 `TIE-data/train-byol.csv`，构建 `ResNet18` online/target network、`MLPHead` predictor，并用 SGD 训练 BYOL。
- BYOL 训练：[trainer.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/trainer.py:27>) 实现 target network 动量更新；[trainer.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/trainer.py:87>) 用两路增强视图计算 normalized regression loss。
- TCP 增强/数据预处理：[dataTraffic_1.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/loader/dataTraffic_1.py:41>) 生成两份增强视图；[dataTraffic_1.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/loader/dataTraffic_1.py:72>) 近似模拟 RTT/MSS/Nagle 导致的包合并/切分；[dataTraffic_1.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/loader/dataTraffic_1.py:105>) 近似模拟丢包导致的序列扰动。
- 表征网络：[resnet_base_network.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/TIE/code/models/resnet_base_network.py>) 用 torchvision ResNet18 加 projection head，把 100 个包长位置补成 3×10×10 输入。
- Rosetta+LSTM 评估：[Eval-Rosseta-LSTM.ipynb](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/test-data/test-app/Eval-Rosseta-LSTM.ipynb:70>) 加载 TIE encoder；[Eval-Rosseta-LSTM.ipynb](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/test-data/test-app/Eval-Rosseta-LSTM.ipynb:91>) 提取特征、标准化、补齐到 512 维后送入 LSTM。
- 原始 LSTM 对照：[Eval-origin-LSTM.ipynb](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/test-data/test-app/Eval-origin-LSTM.ipynb:102>) 直接加载 `origin/lstm.pth`，用原始 100 维包长序列评估。
- 基线模型：`CNN.ipynb`、`DF.ipynb`、`SDAE.ipynb`、`lstm.ipynb`、[FS-Net.py](</F:/泉城实验室/二期/论文/异常检测/source/Rosetta/FS-Net.py>)、`Transformer-master/train.ipynb` 对应论文六类模型；但 `Transformer-master/train.py` 更像通用翻译 Transformer 代码，真正分类改造主要在 notebook。
- 运行风险：`Rosseta` 拼写混用，部分路径是作者本机绝对路径；`well-trained-TIE` 目录只有下载提示，未包含完整 TIE 权重；`util/test.py` 基本是占位文件。因此代码适合作方法对照和局部验证，不是开箱即用的完整复现包。

## 12. 本篇精华

1. 离线高准确率的加密流量分类模型，在真实多网络环境下可能严重失效。
2. 失效根源之一是 TCP 机制改变包长序列，而不是 TLS 应用语义改变。
3. 子序列移位、子序列重复、包大小变化是论文抽象出的三类关键扰动。
4. 通用随机增强不足以解决该问题，必须引入协议语义。
5. Rosetta 的关键思想是“先学跨 TCP 环境不变量，再分类”。
6. BYOL 式自监督适合该场景，因为同一流的不同 TCP 增强版本天然构成正样本对。
7. 论文对异常检测的启发是：评估必须跨环境，模型必须显式处理采集域偏移。
8. 工程代码证明了总体路线，但完整复现仍需补齐预训练 TIE、数据和路径整理。

## 13. 建议精读路线

1. 先读 Introduction，抓住“包长序列模型在真实环境中不鲁棒”这一主问题。
2. 精读 Section 3 和 Table 2-5，重点看同环境与跨环境性能差距。
3. 精读 Section 3.3，把三类包长变化与 TCP 机制对应起来。
4. 读 Figure 4 和 Section 4，理解 Rosetta 的三阶段流程：增强、TIE、自监督特征供分类器使用。
5. 读 Table 6-9 和 Figure 5-7，关注 Rosetta 在丢包、时延、MTU 下的鲁棒性证据。
6. 最后读 Appendix B 的消融，明确哪些模块真正贡献最大。
7. 对照代码时优先看 `TIE/code/main.py`、`trainer.py`、`loader/dataTraffic_1.py` 和两个 Eval notebook。

<!-- codex-cli-deep-read: complete -->
