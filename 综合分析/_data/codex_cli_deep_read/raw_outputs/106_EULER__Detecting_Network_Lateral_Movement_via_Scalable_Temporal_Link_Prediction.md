# [106] EULER: Detecting Network Lateral Movement via Scalable Temporal Link Prediction

## 1. 基本信息

- 论文：EULER: Detecting Network Lateral Movement via Scalable Temporal Link Prediction
- 年份/会议：2022，NDSS 2022
- DOI：10.14722/ndss.2022.24107
- 任务：把企业网络认证/主机交互日志建模为离散时序图，用时序链路预测发现横向移动中的异常连接。
- 正文包：`综合分析\_data\full_text_cache_plain\106.txt`，本次正文包未截断。
- 代码：`source\Euler`，包含通用框架、LANL 实验和小数据 benchmark；我阅读了核心接口、模型、加载器、训练入口和脚本。

## 2. 中文翻译与核心摘要

这篇论文的核心意思是：横向移动不一定表现为“从未见过的连接”或特殊协议特征，攻击者可能使用合法凭据、合法认证流程，甚至重复历史上出现过的边。真正异常的是“这个连接在当前时序上下文中不该出现”。因此作者把网络日志抽象成一串有向图快照，将异常检测改写为时序图上的低概率边检测。

EULER 的方法很直接：每个时间快照先用 GNN 学拓扑嵌入，再把连续快照的节点嵌入送入 GRU/LSTM 学时间动态，最后用节点向量内积估计边存在概率。低概率但真实发生的边就是告警候选。论文的重点不只是准确率，而是把 GNN 与 RNN 解耦：只要每个快照的 GNN 编码不依赖前一时刻 RNN 输出，就能把多个快照分给多个 worker 并行处理，leader 只负责顺序地跑 RNN。

## 3. 论文解决的具体问题

论文针对的是企业网络中 APT 横向移动检测的三个现实矛盾。

第一，横向移动的事件表面可能很正常。攻击者可用合法凭据、Kerberos ticket、远程服务等方式行动，单条事件特征不一定异常。

第二，静态图方法会丢掉时间上下文。某条主机到共享驱动器的边可能以前出现过，但如果它缺少前置认证事件，仍可能异常。

第三，现代时序图模型往往把 GNN 和 RNN 交织得太紧，必须逐快照串行运行，难以处理 LANL 这类几十天、千万级认证事件的日志。

EULER 试图同时回答：能不能把横向移动检测做成时序链路预测，并且在不牺牲检测质量的前提下，让最重的 GNN 消息传递阶段并行化？

## 4. 创新点深度提炼

- 问题重构：不是对单条认证事件分类，而是对“时序图中某条边在当前上下文下的发生概率”打分。
- 模型结构极简：GNN 只编码单个快照拓扑，RNN 只编码快照序列，最后内积解码边概率；作者反而证明复杂时序图自编码器未必带来明显收益。
- 可扩展性来自结构约束：GNN 阶段不能依赖时间信息，这个限制使每个快照可独立编码，从而天然适配 worker 并行。
- 兼容检测和预测两类任务：link detector 重构当前快照，偏事后审计；link predictor 用过去预测未来，偏在线 IDS。
- 告警更有解释粒度：静态图方法只说某条边异常，EULER 能给出某条边在某个时间窗口异常，更贴近安全分析流程。
- 实验价值在 LANL 上体现明显：小数据上 EULER 与 VGRNN 等接近或更好，但真正的贡献是大规模日志上训练/推理速度可接受。

## 5. 科学问题与研究假设

科学问题可以概括为：企业网络横向移动是否可以通过时序图链路概率的异常偏低来识别？

论文隐含了四个关键假设。

- 异常边假设：横向移动会造成与历史时序结构不一致的连接，因此真实发生但预测概率低的边值得告警。
- 上下文必要性假设：边是否异常不能只看边本身，还要看前一时刻和周边节点的交互状态。
- 解耦充分性假设：GNN 不接收 RNN 输出也足以学到有效拓扑信息，时间依赖可以交给后置 RNN。
- 简单模型泛化假设：GCN+GRU 这类低参数模型在异常检测里可能比高度工程化模型更稳，更适合大规模日志。

## 6. 科学方法与技术路线

论文将网络交互表示为离散时序图 `G={G1,...,GT}`，每个快照包含节点、边和可选节点特征。LANL 场景中，边主要表示源计算机到目的计算机的认证关系，边权来自窗口内认证频次。

编码阶段是：

`Z = RNN([GNN(X0,A0), ..., GNN(XT,AT)])`

解码阶段使用内积：

`score(u,v,t)=sigmoid(z_t[u] · z_t[v])`

训练时不重构完整邻接矩阵，而是在正边和随机负采样非边上做二元交叉熵。分类阈值不是固定 0.5，而是在验证快照上寻找兼顾 TPR/FPR 的 cutoff；论文默认 `lambda=0.6`，更偏向压低误报。

分布式路线是 leader/worker：worker 持有连续时间片并运行 GNN，leader 异步接收每个 worker 的拓扑嵌入并顺序跑 RNN，再把时间嵌入发回 worker 解码和算损失。这个设计的核心收益是把最耗内存和随机访问最重的消息传递阶段并行化。

## 7. 实验设计与实验步骤

1. 数据：小数据 benchmark 使用 Enron10、Facebook、COLAB/DBLP 类协作图；LANL 使用 2015 Comprehensive Multi-Source Cyber Security Events 的认证日志，论文表中为 17,685 节点、45,871,390 认证事件、518 条异常边、58 天。

2. 预处理：把日志按时间窗口切成图快照；LANL 中边为源计算机到目的计算机认证，重复认证压缩成带权边；边权用频次标准化后 sigmoid 归一；训练集截止到第一条异常边出现前，末尾约 5% 正常快照用于阈值/验证。

3. 模型/基线：小数据比较 VGAE、DynGraph2Vec、EvolveGCN、VGRNN/SI-VGRNN 和 EULER；LANL 比较 GCN/GAT/SAGE × GRU/LSTM/None，以及 UA 规则、GL-LV/GL-GV、VGRNN。

4. 训练：小数据训练 1500 epoch，验证集早停；LANL 早停更激进，论文写验证不再改善后通常很少反弹。优化器为 Adam，隐藏维 32、嵌入维 16。

5. 指标：回归打分用 AUC 和 AP；告警分类用 TPR、FPR、Precision/F1。论文特别强调 AP，因为 LANL 极端类别不平衡，AUC 容易显得过于乐观。

6. 消融/敏感性：比较有无 RNN，比较 GCN/GAT/SAGE，比较 detector/predictor，调时间窗口 `delta`，以及增加 worker 数量观察扩展性。

7. 结果核查：小数据核查最终 3 个快照；LANL 核查异常开始后的测试区间。EULER 的分数质量、误报率和训练/反向传播时间一起报告，避免只看准确率。

## 8. 关键结果、结论与证据

小数据动态链路检测中，EULER 几乎全面领先。Table II 中 EULER 在 Enron、COLAB、Facebook 的 AUC/AP 都处于最高或显著领先，Facebook 上约有 4 个百分点优势，说明简单 GCN+GRU 并非弱基线。

动态链路预测和新链路预测中，EULER 与 VGRNN/SI-VGRNN 大多统计上接近。作者的解释很关键：复杂模型把 RNN 信息送回 GNN，理论上更强，但实验并未证明这比“GNN 后接 RNN”更有实际收益。

LANL 上，GCN 系列的 AUC 很高，GCN+GRU link detection AUC 约 0.991、AP 约 0.052、TPR 约 86%、FPR 约 0.57%。注意 Precision 仍很低，这是极端不平衡数据的必然结果，不应被高 AUC 掩盖。

UA 规则 TPR 约 72%，意味着约 28% 异常认证边并不是“训练集中从未出现过的边”。这直接支持论文主张：仅靠 unknown edge 会漏掉一批使用历史上存在连接的横向移动行为。

时间窗口越小，分数通常越好，但计算成本上升。图 4 表明更细粒度快照保留了更多短期时序模式，尤其对预测式检测更重要。

扩展性结果是论文真正硬贡献：EULER 在 LANL 上 forward 约快于最强串行 GNN 方法 2 倍，backward 接近 16 倍提升；worker 增多后收益迅速出现，但小数据/少快照下会有边际递减。

## 9. 局限性与待解决问题

EULER 不是可直接单独上线的 IDS。论文自己承认，LANL 上 FPR 仍偏高；即使 0.5% 级误报，在企业网络每日百万级事件中也会产生大量告警。

LANL 标签粗糙。redteam 日志主要标“compromise events”，并不标注后续所有恶意活动，所以一部分模型所谓 false positive 可能是未标注攻击活动，但这也让定量评估存在不确定性。

方法主要依赖边是否符合时序拓扑，事件属性利用很少。协议、端口、账号、进程、命令行、资产角色等安全语义没有系统进入模型，导致告警解释仍偏弱。

内积解码过于简单。它默认节点嵌入相似即可解释边概率，但横向移动常常有方向性、角色约束和条件依赖，更复杂的边解码器可能提升可用性。

代码复现存在整理不足：LANL 路径变量需要手工填写；benchmark loader 有硬编码绝对路径；源码中的 LANL 特征构造和论文叙述不完全一致。这些不影响论文思想，但影响复现实验的直接性。

## 10. 与本项目的关系

这篇与“时序、日志、KPI 与云原生异常检测”的关系是中相关偏安全日志方向。它不是 KPI 数值预测模型，也不是面向指标漂移的云原生异常检测；它的价值在于提供了一种把认证日志、访问日志、服务调用日志转成时序图异常检测任务的范式。

对本项目可借鉴三点：第一，日志异常不一定要先抽事件特征，可以先建实体交互图；第二，异常分数应包含时间上下文，而不是只看历史是否出现过；第三，大规模系统里模型结构的可并行性和准确率同等重要。

如果本项目涉及主机登录、东西向访问、微服务调用、IAM 行为、容器间通信，EULER 可作为“实体关系异常检测”模块参考。若主要是 CPU、延迟、QPS 等 KPI 曲线异常，它只能提供辅助思路，不能直接替代时序预测模型。

## 11. 代码对照分析

通用框架主要在 `euler/`。核心接口是 [euler_interface.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/euler/euler_interface.py:10>)：`Euler_Embed_Unit` 定义单快照编码，`Euler_Encoder` 包装 DDP worker，`Euler_Recurrent` 在 leader 侧异步调 worker、串接 RNN、聚合 loss/score。

检测与预测目标分别在 [euler_detector.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/euler/euler_detector.py:7>) 和 [euler_predictor.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/euler/euler_predictor.py:7>)。Detector 用 `zs[i]` 重构同一时刻边；Predictor 在前面拼一个零 embedding，使 `Z_t` 对齐到下一时刻边，正好对应论文 link detector / link predictor 的区别。

GNN 编码器在 [embedders.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/euler/embedders.py:35>)：实现 GCN、GAT、GraphSAGE 和 DropEdge。RNN 在 [recurrent.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/euler/recurrent.py:3>)：GRU、LSTM、无时间模型 `EmptyModel`，对应论文里“有无时序层”的消融。

数据容器和负采样在 [tdata.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/euler/tdata.py:8>)：保存每个快照边表、mask、边权、标签，并用随机负采样构造非边。

LANL 入口在 [run.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/run.py:24>)，分布式训练/阈值/测试在 [spinup.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/spinup.py:57>)。预处理在 [split.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/loaders/split.py:22>)，它过滤 NTLM，抽取源/目的计算机，生成分片文件和节点映射；加载聚合在 [load_lanl.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/loaders/load_lanl.py:37>)；边划分和权重函数在 [load_utils.py](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/loaders/load_utils.py:7>)。

运行线索：先在 `split.py` 填 `RED/SRC/DST`，在 `load_lanl.py` 填 `LANL_FOLDER`，再运行 `python loaders/split.py` 生成清洗分片；LANL 实验可用 `python run.py -t 5 -d 0.5 -e GCN`，预测式用 `-i PRED`。批量脚本是 [runall_LANL.sh](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/runall_LANL.sh:1>) 和 [run_delta.sh](<F:/泉城实验室/二期/论文/异常检测/source/Euler/lanl_experiments/run_delta.sh:1>)。

复现注意：`load_lanl.py` 默认 `LANL_FOLDER=None` 会直接 assert；`benchmarks/loaders/load_vgrnn.py` 使用硬编码 `/mnt/raid0_24TB/...` 路径，虽然仓库里有 `benchmarks/data`，实际复跑需要改路径。论文说 LANL 拼接实体类型 one-hot，但当前源码里我看到的是 `torch.eye(cl_cnt+1)` 身份矩阵，未明显拼接 user/computer/special 三类特征；边权默认函数也与论文公式存在细节差异，复核实验时应统一这些实现。

## 12. 本篇精华

- 横向移动检测的关键不是“边是否见过”，而是“边是否符合当前时序上下文”。
- EULER 的核心贡献是把时序图模型拆成可并行的 GNN 快照编码和串行 RNN 时间编码。
- 简单 GCN+GRU 在多个 benchmark 上不输甚至超过 VGRNN/EvolveGCN，说明模型复杂度不是主要瓶颈。
- LANL 中 UA 规则只能抓未见过边，约 28% 异常边会被这种思路天然漏掉。
- AP 比 AUC 更能反映极端不平衡异常检测质量；EULER 的高 AUC 不能掩盖 precision 仍低的问题。
- 时间窗口 `delta` 是安全语义和计算成本的核心旋钮：越细越能捕获短期前置关系，但训练更慢。
- 这篇适合作为“日志到时序图异常检测”的代表论文，但不应被包装成完整可上线 IDS。

## 13. 建议精读路线

先读 Section III 的动机例子，抓住“同一条边在不同前置上下文下语义不同”这个核心。然后读 Section IV，重点看 encoder-decoder、leader/worker 流程、detector/predictor 两种训练目标。

接着读 Section V 的 benchmark，不必纠缠所有模型细节，重点比较 EULER 与 VGRNN/EvolveGCN 的差距是否显著。随后精读 Section VI 的 LANL 实验：图构造、训练区间、阈值选择、AP/FPR、时间窗口敏感性和扩展性图。

最后对照代码看四组文件：`euler_interface.py` 理解框架，`euler_detector.py`/`euler_predictor.py` 理解任务，`load_lanl.py`/`split.py` 理解日志到图，`run.py`/`spinup.py` 理解训练和评估。