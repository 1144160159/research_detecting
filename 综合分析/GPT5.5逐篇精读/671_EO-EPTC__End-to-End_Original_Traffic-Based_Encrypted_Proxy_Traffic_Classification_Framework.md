# [671] EO-EPTC: End-to-End Original Traffic-Based Encrypted Proxy Traffic Classification Framework

## 1. 基本信息

论文题名可译为：**EO-EPTC：端到端的基于原始流量的加密代理流量分类框架**。作者为 Yige Chen、Huajie Jia、Zhenzhou Tang、Yipeng Wang、Hui Liu。DOI 为 `10.1109/TIFS.2025.3646874`。元数据年份为 2025；正文页眉显示刊于 **IEEE TIFS Vol. 21, 2026**，接收日期为 2025-12-16，发布日期为 2025-12-22，当前版本为 2026-01-02。

主题属于加密流量分类、代理协议流量识别、分布迁移/数据生成。正文包未截断，因此本次理解不受正文缺页影响。代码包存在两个版本：`source\EO-EPTC` 是较简实现，`source\ygchen1_eo-eptc` 是更完整的数据处理到分类流水线。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：**如果只有普通访问目标网站时采集到的原始流量，能不能训练出能识别加密代理流量的分类器？**

作者观察到 Shadowsocks、VMess、Trojan、VLESS 这类代理协议通常只是对原始流量做封装和加密，不做显式 payload padding 或压缩。因此，原始流量和代理流量虽然分布不同，但长度序列、方向模式、边界结构之间仍存在可学习的相关性。EO-EPTC 的做法不是为每种代理协议、每个目标类别重新采集大量代理流量，而是先用一批原始/代理配对流量学习“原始序列到代理序列”的转换，再用转换出的模拟代理序列训练现有分类器。

论文最重要的结论是：直接用原始流量训练、代理流量测试时 F1-Macro 只有约 1.46% 到 4.93%；加入 EO-EPTC 后，部分场景可达到 99.70%，接近直接用真实代理流量训练的上限。

## 3. 论文解决的具体问题

论文处理的是一个典型分布偏移问题：训练域是原始流量，测试域是加密代理流量。传统加密流量分类默认训练集和测试集同分布，而代理协议会引入握手、封装头、TLS record 边界、长度偏置、片段合并等结构差异，导致原始流量模型迁移到代理流量时几乎失效。

威胁模型是：攻击者位于网关、防火墙等可嗅探位置，不能解密代理 payload，但能观察 IP 头和侧信道特征。攻击者可在本地无代理访问目标应用/网站，低成本采集带标签原始流量，然后希望在真实攻击阶段识别经过代理后的应用或网站类别。

关键不是“检测是否使用代理”，而是**在已观测到代理流量时，进一步识别其背后的应用/网站类别**。

## 4. 创新点深度提炼

第一，论文把代理流量分类转化为**序列特征翻译问题**。它不直接做 domain adversarial learning 或简单数据增强，而是显式学习原始长度序列到代理长度序列的协议变换。

第二，提出了序列特征对齐，包括方向编码、TCP PUSH 引导的重组，以及针对过度重组的长度分段。这一步很关键，因为 Seq2Seq 不应把 MTU 分片、TCP PUSH 缺失等偶然传输噪声误学成代理协议语义。

第三，用 Transformer encoder-decoder 建模代理协议“语义”。这里的语义不是 payload 内容，而是封装导致的序列边界、固定偏移、可变偏移、合并错位等结构性变换。

第四，框架对现有分类器是插件式的。论文把 FS-Net、ETC-PS、Random Forest、XGBoost、Transformer 都作为下游分类器，证明生成的代理序列能服务不同模型族。

第五，论文还把生成序列用于 OOD 检测：先用分类器输出概率向量，再用监督二分类器识别未知类别。这一点与异常检测方向直接相关。

## 5. 科学问题与研究假设

科学问题可以概括为：**代理协议引入的分布差异是否主要由可学习的协议变换造成，而不是不可恢复的随机扰动？**

主要研究假设包括：

- H1：主流加密代理协议不做 padding/压缩，因此原始流量和代理流量的长度序列保留强相关。
- H2：经过重组和分段后，原始/代理序列之间的随机错位减少，剩余差异更接近协议封装规律。
- H3：有限数量的无标签原始/代理配对流可让 Seq2Seq 学到跨网站泛化的协议转换函数。
- H4：转换后的模拟代理序列既接近真实代理分布，又保留网站/应用分类所需的指纹信息。
- H5：操作系统和浏览器影响小于代理协议本身，模型主要学习的是协议层变换。

## 6. 科学方法与技术路线

EO-EPTC 分四阶段。

阶段一是序列特征对齐。TCP/UDP 原始流量提取 payload length 序列，TLS 型代理流量提取 application data record 长度。方向用正负号编码。正文叙述和伪代码在正负方向上略有不一致；代码采用 **C2S 为负、S2C 为正**。

阶段二是序列特征转换建模。Transformer encoder 将原始序列编码为隐表示，decoder 生成代理序列。masked softmax cross entropy 忽略 padding，避免变长序列训练时被填充值污染。

阶段三是模拟代理序列生成。训练好的 Seq2Seq 接收新的原始流量序列，输出对应代理协议下的模拟序列。

阶段四是代理流量分类。下游分类器用模拟代理序列训练，用真实代理序列测试，从而避免为每个目标类别采集真实代理训练集。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：搭建 user、proxy client、proxy server 三主机平台；采集 TCP-based 与 QUIC-based 两类数据；协议包括 Shadowsocks、VMess、Trojan、VLESS；访问 60 个热门网站，每协议每站点 750 次。
2. 预处理：从 pcap 提取 TCP/UDP/TLS/QUIC 长度与方向；过滤重传、乱序和背景流；匹配原始流与代理流；生成原始/代理配对缓存；按 30/30 网站划分 Seq2Seq 训练集和分类集。
3. 模型/基线：Seq2Seq 比较 LSTM、LSTM-Att、GRU、GRU-Att、Transformer；下游分类器包括 FS-Net、ETC-PS、Random Forest、XGBoost、Transformer；另与 FlowPic、FlowFormers、mini-FlowPic 比较。
4. 训练：Seq2Seq 用原始/代理配对流学习转换；分类器用生成的代理序列训练，真实代理序列测试；5 折交叉验证。
5. 指标：F1-Macro 衡量分类性能；ANED 衡量生成序列与真实代理序列的平均归一化编辑距离。
6. 消融/敏感性：比较 Seq2Seq 架构、注意力机制、D/R/S 对齐组合、配对数据规模、QUIC 兼容性、OOD 检测、跨平台鲁棒性。
7. 结果核查：同时比较 `original -> proxied`、`proxied -> proxied`、`original + EO-EPTC -> proxied`，确认提升来自分布桥接而不是分类器偶然优势。

## 8. 关键结果、结论与证据

Transformer Seq2Seq 效果最好，ANED 最低，下游 F1-Macro 最高。Scaled Dot-Product Attention 优于 additive、dot-product 和 local attention，说明代理序列转换依赖较强全局上下文。

对齐特征中，D/R/S 全组合最好。单独方向编码或单独重组提升有限，说明代理协议差异不是一个简单长度偏移，而是边界、方向、分段共同作用。

数据规模实验显示，配对网站数从 1 到 10 时提升最明显，超过 26 后趋于稳定。这支持“模型逐渐学到协议转换，而非记住特定网站”的解释。

核心性能上，原始训练直接测试代理几乎失败；EO-EPTC 后接近真实代理训练。例如 FS-Net 在 Shadowsocks 上从 4.02% 提升到 99.70%，接近真实代理训练的 99.93%。QUIC 场景 F1-Macro 为 85.77% 到 93.70%，低于 TCP，但仍显著优于无 EO-EPTC。

跨平台实验均超过 90%，浏览器影响较小，VMess 在不同 OS 上波动更明显，可能来自 TCP 栈差异导致的合并和错位。

## 9. 局限性与待解决问题

正文包未截断，本次不需要因缺失正文保留复核项。

论文自身承认一个重要限制：当前方法默认原始流和代理流是一对一映射。Hysteria2 等基于 QUIC/HTTP3 multiplexing 的协议可能把多个应用流封装到一个代理流中，变成多对一映射，长度序列会更不稳定。

方法并没有完全消除代理流量采集成本。它仍需要每种代理协议的一批原始/代理配对流来训练 Seq2Seq，只是减少了为每个目标类别采集代理训练集的需求。

评估主要在受控平台和热门网站闭集上完成。真实网络中的丢包、拥塞、CDN 变化、广告个性化、中间盒重写、代理配置差异都可能削弱序列稳定性。

代码层面有若干复现风险：公开完整仓库主要实现 RandomForest 分类，论文中的 FS-Net、ETC-PS、XGBoost、Transformer 分类器未完整随仓库提供；部分阈值和握手丢弃计数是协议硬编码；最小仓库 `source\EO-EPTC\main.py` 中 seq2seq/classify 路径命名疑似反置，复现时应优先使用 `source\ygchen1_eo-eptc`。

## 10. 与本项目的关系

对“异常检测/跨域异常检测”项目来说，这篇论文的价值不在于新分类器本身，而在于它提供了一种**协议诱导分布偏移的特征空间迁移范式**。如果项目面对的是“正常环境有标签、代理/隧道/加密环境无标签或少标签”的场景，EO-EPTC 可作为数据生成与域桥接模块。

OOD 检测部分尤其值得借鉴：先训练闭集分类器，再把概率向量作为识别特征训练未知类检测器。这比单纯设置最大 softmax 阈值更适合异常检测系统。

但若本项目关注恶意行为异常，而不是网站/应用闭集识别，还需要补充行为级特征、时间特征、会话上下文和开放世界评估。EO-EPTC 目前主要证明“代理后的类别指纹可恢复”，不是完整的攻击检测框架。

## 11. 代码对照分析

更完整的仓库是 `source\ygchen1_eo-eptc`。

- `01feature_extract.py`：对应论文数据采集后的特征提取。它调用 `tshark -r ... -V -T json` 解析 pcapng，提取 TCP payload length、TCP flags、TLS record length、UDP/QUIC length，并过滤重传、乱序和部分浏览器背景流。
- `02flow_merge.py`：对应原始流与代理流配对。TCP 使用长度序列严格匹配，并引入协议固定 bias；QUIC 主要按时间窗口和持续时间粗匹配。
- `03dataset_cache.py`：把匹配后的流转成论文所需的 `local_length_seq` 与 `proxy_length_seq`，区分 TCP、QUIC、TLS 型代理。
- `04dataset_split.py`：把 60 类按奇偶索引拆成 `seq2seq` 与 `seqclassify` 两部分，正好对应论文 30/30 网站划分。
- `05classify.py`：主实验入口。实现 TCP 重组/分段、QUIC 序列提取、Seq2Seq 训练、模拟代理序列生成、5 折 RandomForest 分类评估。
- `transformer.py`：实现 Transformer encoder-decoder、masked loss、词表、padding、训练和推理。长度值被当作离散 token，低频或未知 token 最后会通过 `unk2zero` 转为 0。
- `args.py`：给出关键超参：`learning_rate=0.005`、`batch_size=128`、`num_hiddens=32`、`num_layers=3`、`num_heads=4`、`num_steps=64`、`packet_limits=32`。

`source\EO-EPTC` 更像早期或精简版：只有 `main.py`、`transformer.py`、`args.py` 和数据下载链接，不包含 pcap 提取、流匹配、缓存构建、数据拆分脚本。复现实验应优先看 `ygchen1_eo-eptc`。

本次未运行训练：当前工作区只读，且本机 `python/python3` 命令无法正常执行脚本输入。因此代码结论基于源码阅读、目录核对和文件内容检查，不等同于完整复现实验。

## 12. 本篇精华

- EO-EPTC 的核心不是分类器，而是把原始流量到代理流量的差异建模为可学习的序列转换。
- 论文最强假设是：Shadowsocks/VMess/Trojan/VLESS 通常不 padding、不压缩，所以长度序列指纹不会被彻底抹掉。
- 序列对齐是成败关键；不先处理 TCP PUSH、MTU 分片和过度重组，Seq2Seq 会学习大量传输噪声。
- Transformer encoder-decoder 比 LSTM/GRU 更适合处理边界偏移、固定偏置、可变偏置和片段合并。
- EO-EPTC 将原始训练代理测试的 F1 从个位数提升到接近真实代理训练，证明分布桥接有效。
- QUIC 场景仍有效但性能下降，暴露了 UDP/QUIC 缺少 TCP 式重组信息的问题。
- 对异常检测项目，最可借鉴的是“生成目标域特征 + OOD 概率向量检测”的组合，而不是具体网站分类任务。
- 代码可支持主流程复现，但公开实现与论文完整实验矩阵之间仍有差距。

## 13. 建议精读路线

先读 Introduction 的问题设定和 threat model，明确它解决的是“原始训练、代理测试”的跨域分类。再精读 Section III-C 的重组/分段算法和 Figure 4，因为这里解释了为什么代理差异可学。随后读 Transformer 转换建模部分，重点理解它如何处理边界、固定偏移、可变偏移和合并错位。

实验部分建议按 Section V 的三个消融先读，再读 Table IV、Table V、OOD 和跨平台实验。最后对照代码时，从 `05classify.py` 和 `transformer.py` 入手，再回到 `01feature_extract.py` 到 `04dataset_split.py` 理解数据如何进入主实验。

<!-- codex-cli-deep-read: complete -->
