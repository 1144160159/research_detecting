# [120] An intelligent network monitoring approach for online classification of Darknet traffic

## 1. 基本信息

- 题名：An intelligent network monitoring approach for online classification of Darknet traffic  
- 中文题意：一种用于暗网流量在线分类的智能网络监测方法  
- 年份与来源：2023，Computers and Electrical Engineering  
- DOI：10.1016/j.compeleceng.2023.108852  
- 作者：Rodrigo Moreira、Larissa Ferreira Rodrigues Moreira、Flávio de Oliveira Silva  
- 任务定位：Tor/non-Tor 二分类、暗网流量识别、在线网络监测、自适应采样  
- 数据集：ISCXVPN2016 作为 non-Tor，ISCXTor2017 作为 Tor  
- 正文包：`综合分析\_data\full_text_cache_plain\120.txt`，标注未截断  
- 代码包：`source\adaptive-monitoring`，已查看 README、采样、CNN 推理计时、Gym/DQN 相关代码和结果 CSV

## 2. 中文翻译与核心摘要

这篇论文不是单纯提出一个“更高准确率的 Tor 分类器”，而是把问题推进到在线监测场景：高速网络接口上数据包持续到达，监测系统既要尽快判断 Tor/non-Tor，又不能把所有包都拿去做深度模型推理，否则监测本身会成为性能负担。

作者的方案由两部分拼起来：第一部分用 CNN 将网络包转换成图像后分类 Tor/non-Tor；第二部分用强化学习决定当前时刻应该采样多少个包。论文中最关键的工程判断是：DenseNet 和 ResNet 准确率最高，达到 99.84%，但在线场景下 SqueezeNet 虽然准确率略低，为 99.35%，单包预测时间更短，约 0.027 秒，因此更适合作为在线采样代理里的分类器。

核心摘要可以概括为：用 CNN 负责“看懂包”，用 RL 负责“少看但看得准”。论文声称该组合能在接近实时的网络监测中保持较高 Tor 识别能力，同时降低固定采样或全量推理带来的资源开销。

## 3. 论文解决的具体问题

论文解决的问题是：在高吞吐网络中，如何在线识别 Tor/Darknet 流量，同时自适应决定采样包数，避免监测系统因过量抓包和深度模型推理而产生过高开销。

这个问题包含三个具体矛盾：

- 分类精度与在线延迟的矛盾：DenseNet/ResNet 更准，但 SqueezeNet 更快。
- 采样充分性与监测开销的矛盾：包采得太少会误判当前流量状态，采得太多会拖慢接口监控。
- 静态策略与流量波动的矛盾：固定采样率不能适应 Tor/non-Tor 比例随时间变化的情况。

论文把 Tor 流量等同为 Darknet/malicious，把 non-Tor 视为 benign。这个设定便于建模，但在真实安全语义上较粗糙，后面需要作为局限看待。

## 4. 创新点深度提炼

1. 从离线分类转向在线监测闭环  
   相关工作多把 ISCXVPN2016、ISCXTor2017 做成离线特征、流统计或图像分类任务。本文的重点是把分类器嵌入网络接口监测流程，让“采样-分类-反馈-再采样”形成闭环。

2. 用强化学习学习采样数量，而不是固定采样率  
   论文的动作空间对应采样包数，目标是在较少观测下估计 Tor 流量比例。这个点比“换一个更强 CNN”更有研究价值，因为它直接面对高速监测中的资源约束。

3. 包级图像化，而不是流级统计特征  
   作者沿用 Packet Vision 思路，将包的原始字节排成矩阵并转成图像，让 CNN 从包结构、头部与载荷字节模式中学习差异。它避免依赖 CICFlowMeter 这类离线流特征生成过程。

4. 明确比较准确率和预测时间的取舍  
   DenseNet/ResNet 准确率为 99.84%，SqueezeNet 为 99.35%，差距只有约 0.49 到 0.59 个百分点；但 SqueezeNet 推理时间明显更低。因此论文选择 SqueezeNet 进入在线分类流程，这比只报告最高准确率更贴近部署。

5. 用随机采样作为 RL 采样的对照  
   论文比较了 random sampling 和 RL adaptive sampling。随机采样无法稳定追踪 Tor 比例，RL 在约 80 个 episode 后奖励趋稳，说明采样策略确实在学习。

6. 加入 Ablation-CAM 做解释  
   作者用 Ablation-CAM 观察 CNN 激活区域，认为 Tor 与 non-Tor 包在图像纹理/结构上有可学习差异，尤其 DenseNet 和 ResNet 激活更清晰。

## 5. 科学问题与研究假设

科学问题可以表述为：在不全量处理网络包的情况下，能否通过自适应采样和轻量 CNN 推理，稳定估计并识别 Tor/Darknet 流量？

论文隐含了几条研究假设：

- 原始包字节转成图像后仍保留足够的可分类结构。
- Tor 与 non-Tor 的包级结构差异能被 CNN 学到，不必完全依赖人工流统计特征。
- 在线监测不需要每个包都分类，只需要在每个时间窗口采到足够代表性的样本。
- 强化学习能根据历史采样效果学习“采多少包”更合适。
- 在在线系统中，低延迟模型可能比最高准确率模型更有实用价值。

论文显式提出的 RQ 也围绕这几件事：哪种 CNN 更准、哪种 CNN 更快、RL 采样行为如何、RL 如何帮助在线流量预测。

## 6. 科学方法与技术路线

技术路线是一个两层结构。

第一层是 CNN 分类器。作者将 pcap 中的数据包转换成图像：把十六进制字节按固定宽度排列，不足处填充，再扩展成 RGB 图像，之后 resize 到 224×224，使用 ImageNet 预训练 CNN 进行 Tor/non-Tor 二分类。比较的模型包括 ResNet、SqueezeNet 和 DenseNet。

第二层是 RL 自适应采样器。监测代理附着在网络接口上，RL agent 每一步选择一个采样动作，也就是本轮采多少包；采样得到的包送入 CNN，CNN 输出 Tor/non-Tor；系统根据采样结果中的 Tor 占比给 reward，并把状态、动作、奖励、下一状态存入 replay memory，用 DQN/Q-learning 更新策略。

整体链路是：pcap/接口流量 → 包采样 → 字节图像化 → CNN 分类 → 统计 Tor 比例 → RL 奖励与策略更新 → 下一轮采样数量。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 ISCXVPN2016 的 non-Tor 流量和 ISCXTor2017 的 Tor 流量。non-Tor 合并了 audio-streaming、browsing、chat、email、P2P、FTP、video-streaming、VoIP 等类别。论文报告图像数量为 non-Tor 3196、Tor 2892，并按 80/10/10 划分训练、验证和测试。

2. 预处理  
   将数据包原始字节转换为图像。代码中的 `pooling.py` 体现了这一点：按 8 个字节一行组织矩阵，不足位置用 `FF` 填充，再把单个字节值复制到 RGB 三个通道，生成 PNG。

3. 模型与基线  
   CNN 模型比较 ResNet、SqueezeNet、DenseNet。采样策略比较 RL adaptive sampling 与 random sampling。文献对照包括 Lashkari、Iliadis、Jadav、Marim、Singh 等在同类数据集上的方法。

4. 训练  
   CNN 使用 SGD，batch size 32，epoch 50，学习率 0.001，momentum 0.9，损失函数为 cross entropy。DQN 参数包括 epsilon、batch size、discount factor、learning rate、reward 和 200 个 episode。

5. 在线测试环境  
   在 Ubuntu 18.04 上建立 veth0/veth1 虚拟接口，用 `tcpreplay` 回放 pcap，随机设置传输循环和间隔；采样代理在接收端抓包并调用 CNN 分类。

6. 指标  
   分类部分使用 accuracy；在线部分看单包预测时间、训练 loss、reward 累积和 reward 收敛情况。

7. 消融/敏感性  
   论文做了 CNN 架构对比、推理时间对比、随机采样与 RL 采样对比、Ablation-CAM 可解释性分析。严格意义上的 reward、动作空间、目标 Tor 比例、不同流量分布敏感性实验还不充分。

8. 结果核查  
   论文关键结果包括 DenseNet/ResNet 99.84%、SqueezeNet 99.35%、SqueezeNet 约 0.027 秒单包预测、RL 在约 80 episode 后奖励稳定。代码包中的预测时间 CSV 与 SqueezeNet 最快这一结论一致。

## 8. 关键结果、结论与证据

- 分类准确率：DenseNet 与 ResNet 均达到 99.84%，SqueezeNet 达到 99.35%。最高准确率来自 DenseNet/ResNet。
- 在线推理速度：SqueezeNet 平均单包预测时间约 0.027 秒。代码 CSV 中我核算到的均值为 SqueezeNet 0.0273 秒、ResNet 0.0409 秒、DenseNet 0.1180 秒。
- 模型选择结论：在线监测场景下，SqueezeNet 牺牲很小准确率，换来明显更低推理时间，因此被作者选为在线分类任务的优先模型。
- 采样策略结论：random sampling 的 reward 不稳定，无法有效追踪目标 Tor 比例；RL adaptive sampling 奖励逐步累积并稳定，论文图示约 80 episode 后进入较好状态。
- 可解释性证据：Ablation-CAM 显示 DenseNet/ResNet 对 Tor/non-Tor 图像纹理区域有较明显激活，作者据此认为包结构差异能被 CNN 捕捉。
- 文献比较：论文报告 99.84% 高于表中同数据集相关方法，同时本文额外具备 near-real-time classification 和 intelligent sampling 两项能力。

## 9. 局限性与待解决问题

正文包标注未截断，因此本次理解不是建立在残缺正文上；但图 5 到图 9 的坐标细节、误差范围和曲线读数仍建议回 PDF 复核。

主要局限如下：

- Tor 不等于恶意，Darknet 也不只等于 Tor。论文为了实验简化把 Tor 视作 malicious/Darknet，把 non-Tor 视作 benign，这在真实安全场景中会引入语义偏差。
- 数据划分可能存在包级或会话级泄漏风险。论文没有充分说明是否按 flow/session/time 做隔离划分，如果同一流的相邻包进入训练和测试，准确率会偏乐观。
- 在线实验仍是合成回放环境。veth + tcpreplay 能验证流程，但不能等价代表真实高吞吐骨干网、数据中心东西向流量或复杂攻击混合流量。
- RL reward 依赖目标 Tor 比例。实验目标约为 48.26%，这来自构造数据集本身；真实网络中 Tor 基线未知且漂移，reward 设计需要重新定义。
- 开销评估不完整。论文强调降低 overhead，但主要报告了单包预测时间和 reward/loss，没有系统报告 CPU、GPU、内存、丢包率、吞吐上限和端到端延迟。
- 模型可能学习数据集痕迹。包图像化方法可能捕捉 pcap 生成、协议栈、数据集采集环境或长度分布特征，而不一定是稳健的 Tor 本质特征。
- 代码包不是开箱即复现。缺少 `adaptative_pooling.py`、`packetVision.py`、训练好的 `.pth` 模型和 `dataset.pcap`；多个脚本含硬编码 `/home/rodrigo/...` 路径。

## 10. 与本项目的关系

这篇论文与“异常检测、恶意流量、暗网与网络流量监测”强相关，但它更接近资源感知的在线二分类监测，而不是严格意义上的未知异常检测。

对本项目最有价值的不是 99.84% 这个数字，而是研究范式：把检测模型和采样策略一起设计。很多异常检测论文只优化分类器，默认数据已经被完整采集；本文提醒我们，在真实网络安全系统中，“采多少、何时采、用什么模型处理”本身就是科学问题。

如果本项目关注跨域异常检测，可以借鉴它的三点：包级表征、轻量模型部署、RL/自适应策略控制监测成本。但需要补上更严格的数据隔离、真实流量漂移、多类别异常和未知攻击测试。

## 11. 代码对照分析

代码包与论文方法的对应关系如下：

| 论文环节 | 代码位置 | 对应关系与问题 |
|---|---|---|
| 环境搭建 | `source\adaptive-monitoring\README.md`、`requirements.txt` | 给出 Python 3.7、Scapy、Torch、TorchVision、Gym、Stable-Baselines、TensorFlow 1.15 等依赖 |
| 合成流量回放 | `syntetic_packet_workload_gen.sh` | 创建 veth pair，用 `tcpreplay` 循环回放 `dataset.pcap`，对应论文 Fig. 3 的测试环境 |
| pcap 时间处理 | `change_timestamp.py` | 用 Scapy 修改 pcap 时间戳，输出 `out_nontor_final.pcap`，属于数据准备辅助脚本 |
| 接口采样 | `pooling.py` | `dumpcap` 从接口抓包到 `/tmp/output.pcap`，对应采样代理；但路径和 root 依赖很强 |
| 包图像化 | `pooling.py:create_image` | 把包 hex 按 8 字节成行、填充 `FF`、转 RGB PNG，对应 Packet Vision 式预处理 |
| CNN 推理 | `pooling.py:cnn_start/cnn_predict`、`load_example.py` | 加载预训练 CNN checkpoint 并输出 Tor/non-Tor；但模型文件未随仓库提供 |
| 推理计时 | `prediction_time.py`、`*_exp_time_spent_on_prediction.csv` | CSV 记录 start/end/time/class/image，支撑论文 Fig. 6 的预测时间比较 |
| RL/DQN | `gym-basic\gym_basic\envs\teste.py`、`agent.py` | 实现 replay memory、DQN、epsilon-greedy、MSE loss、episode 训练和 reward/loss CSV |
| Gym 环境 | `basic_env.py`、`__init__.py` | 当前 `basic_env.py` 是 toy 环境；`__init__.py` 引用缺失的 `adaptative_pooling.py`，说明真正网络采样环境未包含在快照中 |
| 结果记录 | `adaptative_pooling_results_*.csv`、`results\*.pdf` | 保存 RL/random reward 与 loss，对应论文 Fig. 7/Fig. 8 的实验痕迹 |

运行线索是：先创建 conda 环境并安装 `gym-basic`，再运行 `syntetic_packet_workload_gen.sh` 回放流量，用 `sudo python3 pooling.py <包数> <持续时间> <接口>` 做接口采样，最后运行 `teste.py --env "gym_basic:basic-v1" ...` 做 RL 训练。

需要注意，当前代码包更像论文实验原型的残留快照，而不是完整复现实验仓库。尤其是 `load_example.py` 中设置 `model_name = "densenet"`，但初始化函数没有 densenet 分支；`pooling.py` 又有 densenet/squeezenet 相关逻辑。论文中说 ResNet-34，代码里部分位置用的是 `resnet18`。这些不一致需要复现实验前先清理。

## 12. 本篇精华

- 本文真正的研究点是“在线监测中的自适应采样”，不是单纯 Tor 分类准确率。
- CNN 负责包级 Tor/non-Tor 判断，RL 负责决定每轮采多少包，两者结合形成监测闭环。
- DenseNet/ResNet 最准，SqueezeNet 最快；在线部署中作者选择了速度更优的 SqueezeNet。
- RL 采样相对随机采样更能稳定追踪目标 Tor 比例，但 reward 设计强依赖实验中的 Tor 基线。
- 包图像化降低了人工特征工程需求，但可能学习到数据集或采集环境痕迹。
- 99.84% 的结果很强，但需要用 flow/session 级隔离、真实高速链路和跨数据集测试重新验证。
- 代码包能看出论文实现思路，但缺少核心环境文件、模型权重和数据，不能直接视作完整复现包。

## 13. 建议精读路线

先读 Introduction 和 Table 1，抓住作者与已有工作的区别：实时分类和智能采样。

然后精读 Section 3 的 Fig. 2、Algorithm 1、Algorithm 2，重点理解状态、动作、奖励、replay memory 如何服务“采样包数”决策。

接着读 Section 4，看数据集构造、Tor/non-Tor 合并、虚拟接口、tcpreplay、CNN 参数和 DQN 参数。

再读 Section 5，按三个问题核查：CNN 准确率是否可信、SqueezeNet 的速度收益是否足够、RL 曲线是否真的优于随机采样。

最后对照代码读：`README.md` → `syntetic_packet_workload_gen.sh` → `pooling.py` → `prediction_time.py` → `gym-basic\gym_basic\envs\teste.py`。读代码时重点标出缺失文件和硬编码路径，因为这决定了后续能否复现实验。

<!-- codex-cli-deep-read: complete -->
