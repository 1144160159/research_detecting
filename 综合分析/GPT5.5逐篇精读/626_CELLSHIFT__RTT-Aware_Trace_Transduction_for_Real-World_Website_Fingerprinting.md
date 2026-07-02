# [626] CELLSHIFT: RTT-Aware Trace Transduction for Real-World Website Fingerprinting

## 1. 基本信息
- 论文：**CELLSHIFT: RTT-Aware Trace Transduction for Real-World Website Fingerprinting**
- 中文题意：**CELLSHIFT：面向真实网站指纹攻击的 RTT 感知轨迹转导**
- 作者：Rob Jansen
- 年份/会议：NDSS 2026
- DOI：10.14722/ndss.2026.231004
- 主题归类：加密流量分类、Tor 网站指纹识别、真实世界分布迁移、流量轨迹增强
- 代码：`robgjansen/cellshift`，本地目录 `source\cellshift`
- 正文状态：正文包未截断。

## 2. 中文翻译与核心摘要
这篇论文研究 Tor 网站指纹攻击中的一个关键错位：攻击者较容易在 **exit relay** 侧收集带标签的真实 Tor 访问轨迹，但真实攻击通常发生在 **entry side**，而 entry 侧观察到的流量时序和方向序列并不等同于 exit 侧。直接用 exit 轨迹训练或测试，会低估或误估真实 entry-side WF 问题。

论文提出 **CellShift**：利用 Tor cell trace 中已有的时间戳、方向和 relay command 元数据估计电路 RTT，并把 exit 侧轨迹“移动”到 entry/ISP 等目标观测位置。基于 CellShift，作者实现两个具体方法：**TraceMove** 用于生成更真实的 entry-side 测试集，**TraceMorph** 用于生成 RTT 增强后的训练集，使分类器对传播时延和拥塞变化更鲁棒。

核心结论是：与 Retracer 这种重放进 Tor 大规模仿真的方法相比，CellShift 既更准确，又快几个数量级；TraceMorph 还能显著提升多种 WF 分类器在真实 GTT23 数据上的表现。

## 3. 论文解决的具体问题
论文解决的是 **真实世界网站指纹评估中的观测位置错位问题**。

传统 WF 研究常用自动浏览器采集 synthetic traces，但这会简化真实用户行为。GTT23 这类 genuine Tor traces 更接近真实世界，因为它来自 Tor exit relay 上真实用户自然交互产生的流量模式。不过 exit 侧可见目的站点标签，entry 侧才是攻击者部署 WF 的典型位置。于是产生矛盾：**有标签的数据在 exit，攻击和测试场景在 entry**。

已有方法 Retracer 通过在 Shadow/Tor 仿真中重放 exit trace 来提取 entry trace，但资源开销极高，并且本文发现它生成测试 trace 时甚至可能比原始 exit trace 更不像真实 entry trace。本文的问题就是：能否不做大型仿真，仅靠 trace 本身的元数据，把 exit trace 转导成更接近 entry trace 的数据？

## 4. 创新点深度提炼
1. **把 Tor 协议控制元数据转化为 RTT 估计信号**  
   论文不是只看方向序列，而是利用 `CONNECTED -> DATA`、每 31 个 `DATA -> SENDME` 这两类协议依赖关系，从 exit cell trace 中连续估计 circuit RTT。

2. **把 RTT 拆成传播时延与拥塞轮廓**  
   作者用最小 RTT 近似路径传播时延，用 `RTT_i - RTT_min` 表示动态拥塞。这是 TraceMorph 能做数据增强的关键：路径传播时延与拥塞被视为与网站内容弱相关的网络噪声。

3. **直接重写 cell 时间戳，而不是重放网络仿真**  
   CellShift 将 cell 分成 client→server 与 server→client 两个单向流，按源/目标观测位置和 RTT 重新计算时间戳，再排序合并。这让算法成为轻量级预处理，而不是仿真系统。

4. **区分测试集转导与训练集增强两个任务**  
   TraceMove 尽量保留单条 trace 原始 RTT，只改变观测位置，适合构造测试集；TraceMorph 则从整个数据集采样传播时延和拥塞轮廓，适合构造训练集。

5. **把真实 Tor trace 纳入 WF 风险评估闭环**  
   论文的价值不只是算法快，而是让 GTT23 这类 genuine exit trace 能被转成 entry-side 训练/测试数据，从而更贴近真实攻击评估。

## 5. 科学问题与研究假设
核心科学问题是：**RTT-aware trace transduction 能否缓解 WF 分类器在训练位置与测试位置不一致时的分布偏移？**

主要假设包括：
- Tor cell trace 中的时间戳、方向和 relay command 足以估计 circuit RTT 的动态变化。
- exit 与 entry 观察差异的一个重要来源是路径传播时延与拥塞导致的 cell 时间重排。
- 传播时延和拥塞更多由 Tor relay 路径和负载决定，而不是由具体网站决定，因此可作为增强维度。
- 如果训练集覆盖更多 RTT/拥塞变化，WF 分类器会更关注网站相关模式，而不是偶然网络条件。

## 6. 科学方法与技术路线
论文的技术路线是：

1. 输入 cell trace：每个 cell 包含时间 `t`、方向 `d`、relay command `c`。
2. 从 Tor 协议行为估计 RTT：
   - 初始 RTT：exit 发出 `CONNECTED`，客户端收到后发送首个 `DATA`。
   - 后续 RTT：exit 每发送第 31 个 `DATA`，客户端返回 `SENDME`。
3. 得到随 trace 位置变化的 RTT 序列，并用最近 RTT 调整对应 cell。
4. 将 RTT 拆分为：
   - `propagation_delay = min(RTTs)`
   - `congestion_i = RTT_i - propagation_delay`
5. 进行 timestamp shift：
   - server→client cell 从 exit 发出，向 entry 侧移动时加上对应 hop latency。
   - client→server cell 在 exit 被接收，向 entry 侧移动时先减去原始 client→exit 延迟，再加目标位置延迟。
6. 对两个方向的 cell 分别保持单向顺序，然后按新时间戳排序合并。
7. 基于核心 shift 函数形成：
   - **TraceMove**：单 trace 自身 RTT 转导，用于测试。
   - **TraceMorph**：跨数据集采样传播时延和拥塞轮廓，用于增强训练。

## 7. 实验设计与实验步骤
可复核流程如下：

1. **数据准备**
   - Dataset 1：作者新采集 correlated entry-exit traces，396 个 URL，每个 80 条，共 31,680 条成对 trace。
   - Dataset 2：已有 independent Tor(entry)/Tor(exit)，421 个 URL，entry 每类 40 条，exit 每类 60 条。
   - Dataset 3：GTT23 closed-world top 100，每站 1000 条 genuine exit trace，划分 80/10/10。
   - Dataset 4：GTT23 natural-world，按时间周切分训练与测试，模拟训练早于测试。

2. **预处理**
   - 过滤错误/重试 trace。
   - 过滤过短 outlier。
   - 依据 URL/website 做均衡或按自然分布保留。
   - 对测试 genuine exit trace 用 TraceMove 转成 entry trace。

3. **模型与基线**
   - 转导/增强基线：OnlineWF、Retracer、NetAugment、TraceMove→NetAugment、TraceMorph。
   - WF 分类器：AWF、DF、Tik-Tok、VarCNN、TF、BAPM、ARES、RF、NetCLR、TMWF。

4. **训练**
   - closed-world 多分类：训练 100 epoch 或 GTT23 上 30 epoch，保存验证集 F1 最优模型。
   - natural-world：对 top 200 网站分别训练二分类 DF 分类器，分两个时间阶段评估。

5. **指标**
   - trace 相似性：Manhattan、Canberra、Levenshtein、Euclidean、Cosine、Hamming。
   - closed-world：accuracy。
   - natural-world：precision、recall、average precision、optimized precision。

6. **消融/敏感性**
   - 比较 augmentation factor `naug=1..19` 对 DF accuracy 的影响。
   - 比较直接 exit 训练、仿真式 Retracer、RTT-aware TraceMorph 的差异。

7. **结果核查**
   - 先用有 entry ground truth 的 synthetic/correlated 数据验证 TraceMove。
   - 再把 TraceMove 应用于 GTT23 构造真实 entry-side 测试。
   - 最后评估 TraceMorph 是否提升真实攻击场景下的训练效果。

## 8. 关键结果、结论与证据
- 在 correlated trace 距离实验中，TraceMove 在 6 种距离函数上都比原始 exit trace 和 Retracer 更接近真实 entry trace。例如 Canberra mean：exit 147，Retracer 175，TraceMove 126。
- 在 Dataset 2 上，用 Tor(entry) 训练、不同测试集测试时，TraceMove 测试集让 10 个 WF 分类器均取得最高准确率，通常比直接 exit 测试高 3-4 个百分点。
- Retracer 在测试集生成上表现反常，论文指出它只重放 DATA cells，导致控制 cell 缺失，trace 偏短。
- 在训练增强实验中，TraceMorph 对 10 个分类器中 9 个取得最佳结果，相对第二名提升 4-14 个百分点。
- 在 GTT23 closed-world top100 上，TraceMorph 明显优于 OnlineWF 和 Retracer，例如 DF 从 46% 提升到 70%，NetCLR 从 42% 提升到 67%。
- natural-world 中，TraceMorph 的 median recall 为 0.66，而 Retracer/OnlineWF 约为 0.24/0.22；optimized precision 中位数为 0.49，明显高于 OnlineWF 0.23 和 Retracer 0.17。
- 性能方面，Retracer 处理 115k traces 需要 495 GiB RAM、36 核、29.9 小时；TraceMove 单核 40 秒，约 2875 traces/s/core。大规模 GTT23 上 TraceMorph 可达 18,706 traces/s/core。

## 9. 局限性与待解决问题
- CellShift 依赖 Tor 协议元数据，尤其是 `CONNECTED/DATA/SENDME` 模式；若 Tor 协议或拥塞控制参数变化，RTT 估计逻辑需要更新。
- `RTT/6` 平均分配到 6 个单向 hop 是简化假设，真实 relay 间延迟并不均匀。
- 用最小 RTT 近似传播时延、剩余部分近似拥塞，是工程上合理但并非严格可观测分解。
- TraceMove 生成的是 entry trace 估计，不是真实 entry relay 直接观测的带标签 trace；GTT23 真实评估仍建立在该估计方法可信的前提上。
- natural-world 中 TraceMorph 提升 recall 的同时原始 precision 下降，必须依赖阈值调优才能形成更高精度攻击。
- 代码当前更像 artifact/prototype：README 明确标注 experimental。
- 本地代码实现中，从非 exit 源位置转导的 RTT 细节尚未完成，`rtt.rs` 对非 exit source 使用 `unimplemented!`。
- 代码包不包含 WF 分类器训练与论文中 1200 个分类器实验的完整流水线，主要提供 trace 预处理工具。

## 10. 与本项目的关系
这篇论文与“异常检测”项目是**中相关**。它不是传统异常检测论文，但它处理的问题本质上是加密流量中的分布偏移、表示变换和数据增强，这些都可迁移到异常检测场景。

可借鉴点包括：
- 对加密流量分类，不能只依赖采集端位置固定的数据集；观测点变化会造成显著分布偏移。
- TraceMove 类似“域对齐”：把 source domain 的 trace 映射到 target observation domain。
- TraceMorph 类似“物理语义约束的数据增强”：增强变量不是随机扰动，而是 RTT、传播时延、拥塞这些网络因子。
- 对异常检测项目，若训练数据来自边界网关、测试数据来自主机/代理/出口链路，CellShift 的思想可作为跨视角流量归一化参考。
- 论文也提醒：真实用户行为 trace 与自动化采集 trace 的差异，可能比模型结构差异更影响安全结论。

## 11. 代码对照分析
我阅读了本地 `source\cellshift` 代码包。它是 Rust CLI + library，负责生成转导/增强后的 HDF5 trace，不负责训练 WF 分类器。

- [README.md](F:/泉城实验室/二期/论文/异常检测/source/cellshift/README.md:1)：安装、Docker/Apptainer、`cellshift move` 与 `cellshift morph` 用法。
- [Cargo.toml](F:/泉城实验室/二期/论文/异常检测/source/cellshift/Cargo.toml:1)：依赖 `gtt23`、`hdf5-metno`、`clap`、`rand_chacha`、`zstd`，说明数据格式围绕 GTT23 HDF5。
- [src/lib/rtt.rs](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/lib/rtt.rs:8)：`RttEstimator` 对应论文 RTT 提取；`sent_connected`、`received_data`、`sent_data`、`received_sendme` 分别实现 `CONNECTED→DATA` 与 `31 DATA→SENDME` 估计。
- [src/lib/shift.rs](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/lib/shift.rs:9)：`CellShift` 对应核心 timestamp shift；`shift_cell_time` 实现不同 source/destination 位置的时间换算；`latency(rtt, hops)=rtt/6*hops` 对应论文的 hop 平均假设。
- [src/trace.rs](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/trace.rs:14)：`run_tracemove` 是 TraceMove 入口；[run_tracemorph](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/trace.rs:33) 是 TraceMorph 入口；[MorphTargets](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/trace.rs:201) 保存传播时延分布和随机拥塞 profile。
- [src/lib/data.rs](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/lib/data.rs:11)：HDF5 读写、长度过滤、日期过滤、压缩写出。
- [src/cli.rs](F:/泉城实验室/二期/论文/异常检测/source/cellshift/src/cli.rs:35)：CLI 子命令包括 `move`、`morph`、`merge`、`index`。
- [Dockerfile](F:/泉城实验室/二期/论文/异常检测/source/cellshift/Dockerfile:1)：安装 clang/cmake/HDF5/ZSTD/Rust，并从 GitHub 安装 cellshift。

典型运行线索：
```bash
docker build -t cellshift -f Dockerfile .
docker run -it cellshift

cellshift morph --time-unit week --time-vals 1 --min-length 1000 --seed 654321 \
  gtt23.hdf5 gtt23_week1_entry_augmented10.hdf5 10

cellshift move --time-unit week --time-vals 2,3,4,5,6 --min-length 1000 \
  gtt23.hdf5 gtt23_weeks23456_entry.hdf5
```

## 12. 本篇精华
- 真实 WF 的关键难点不是单纯模型不够强，而是 **exit 有标签、entry 才是攻击位置** 的观测分布错位。
- CellShift 的关键洞察是：Tor cell trace 自身已经包含足够的 RTT 估计线索，不必重放大型 Tor 仿真。
- `CONNECTED→DATA` 与 `31 DATA→SENDME` 是把协议语义转为机器学习数据增强信号的核心。
- TraceMove 适合构造更可信的 entry-side 测试集；TraceMorph 适合构造覆盖多 RTT/拥塞条件的训练集。
- 论文显示 Retracer 在测试集生成上可能引入控制 cell 缺失等 artifact，不能简单认为仿真越复杂越真实。
- 在 GTT23 genuine traces 上，TraceMorph 对闭集和自然世界评估都有显著提升，尤其提升 recall 和可阈值调优空间。
- 对加密流量异常检测而言，本文最值得借鉴的是“网络物理因素感知的数据增强”，而不是某个具体 WF 分类器。

## 13. 建议精读路线
1. 先读 Introduction 和 II-B/II-C，明确 adversary model、genuine traces 与 exit-entry mismatch。
2. 精读 III-B，尤其 RTT 估计、传播时延/拥塞分解、timestamp shift 三部分。
3. 对照 III-C/III-D 区分 TraceMove 与 TraceMorph：一个保 RTT 做测试，一个换 RTT 做训练增强。
4. 阅读 IV-B，理解为什么作者先用 correlated/independent synthetic traces 验证转导可靠性。
5. 阅读 IV-D，把 GTT23 closed-world 与 natural-world 结果作为论文最终安全意义。
6. 最后结合代码看 `src/lib/rtt.rs`、`src/lib/shift.rs`、`src/trace.rs`，即可把论文方法和实际 artifact 对齐。

<!-- codex-cli-deep-read: complete -->
