# [603] AI-on-RAN for Cyber Defense: An XAI-LLM Framework for Interpretable Anomaly Detection

## 1. 基本信息

- 题名：AI-on-RAN for Cyber Defense: An XAI-LLM Framework for Interpretable Anomaly Detection
- 中文题意：面向网络防御的 AI-on-RAN：用于可解释异常检测的 XAI-LLM 框架
- 年份：2025，IEEE TNSE 在线发表；卷期页面显示为 IEEE Transactions on Network Science and Engineering, Vol. 13, 2026
- DOI：10.1109/TNSE.2025.3629983
- 作者：Sotiris Chatzimiltis, Mohammad Shojafar, Mahdi Boloursaz Mashhadi, Rahim Tafazolli
- 任务类型：5G/Open RAN 场景下，基于 UE 侧 KPM 多变量时间序列的 DDoS/异常检测，并用 XAI 与 LLM 生成可读解释
- 本地代码状态：未发现论文对应开源代码
- 正文完整性：正文包未截断

## 2. 中文翻译与核心摘要

这篇论文的核心不是单纯提出一个更高 F1 的入侵检测模型，而是把“RAN 边缘早期检测”“深度模型解释”“面向运维人员的自然语言说明”串成一个可部署到 Open RAN 架构中的安全工作流。

作者关注下一代 RAN 的两个变化：一是 Near-RT RIC/xApp 让 RAN 侧可以承载近实时智能控制；二是 AI-RAN/AI-on-RAN 允许在网络基础设施中运行额外 AI 能力，包括 XAI 与 LLM。论文以恶意 UE 发起 DDoS 为代表场景，使用来自 E2 节点的 KPM 指标构造多变量时间序列，训练 LSTM 序列分类器识别正常与攻击行为。检测之后，框架用 LIME 和 SHAP 解释单次预测，再把局部解释、全局特征重要性、输入序列、模型输出和特征统计一起喂给 LLM，让 LLM 生成非专家也能理解的告警原因与处置建议。

实验使用真实 5G 测试床数据 NCSRD-DS-5GDDoS。最终 LSTM 在宏平均 F1 上超过 0.96，并且作者特别讨论了历史数据比例对灾难性遗忘的抑制作用。论文的落点是：检测模型应放在 Near-RT RIC 的 IDS xApp 中，而计算更重、时延更宽松的 XAI+LLM 解释模块更适合作为 Non-RT RIC/rApp 侧的辅助决策模块。

## 3. 论文解决的具体问题

论文要解决的是 RAN 安全中一个很实际的断点：攻击通常从 UE 或边缘接入侧开始，但传统检测和防御更多位于核心网，响应链路长，无法充分利用 RAN 侧的近实时遥测。

具体问题包括：

- 如何在 Near-RT RIC 中利用 UE 级 KPM 时间序列提前发现恶意 UE 行为，尤其是 DDoS 型流量异常。
- 如何避免把 IDS 只做成黑盒分类器，因为安全运维场景需要知道“为什么判为攻击”。
- 如何把 SHAP/LIME 这类技术性解释转化为可读、可操作的告警说明，降低非机器学习专家的理解成本。
- 如何在 Open RAN 架构约束下拆分实时检测与非实时解释，避免 LLM 推理时延拖垮 near-real-time 检测链路。
- 如何处理真实攻击数据中的类别不平衡和跨天持续学习时的灾难性遗忘。

## 4. 创新点深度提炼

第一，论文把 AI-for-RAN 与 AI-on-RAN 分工明确化。LSTM 检测模型属于 AI-for-RAN，用 AI 改善 RAN 安全；XAI+LLM 模块属于 AI-on-RAN，在 RAN 计算环境中运行辅助 AI 能力，服务解释和决策。

第二，框架采用 xApp/rApp 解耦设计。IDS xApp 只负责预处理与近实时二分类；XAI+LLM rApp 负责较慢的解释、总结和缓解建议。这比把 LLM 直接塞进实时检测链路更符合 RIC 的时间尺度。

第三，输入不是普通网络流量五元组，而是 UE 级 KPM 多变量时间序列。作者强调 DDoS 行为并不一定能从孤立样本稳定判断，必须看短时间窗口中的 uplink/downlink bitrate、tx、retx、error 等指标演化。

第四，论文同时做局部解释和全局解释。局部 LIME/SHAP 服务单条告警解释，全局 SHAP 用来观察模型整体依赖哪些 KPM 与时间步。

第五，LLM 的使用不是替代检测器，而是解释器和决策支持器。论文没有让 LLM 直接判断是否攻击，而是让 LSTM 做结构化检测，让 LIME/SHAP 给出证据，再让 LLM 做语言组织和处置建议生成。

第六，论文讨论了历史数据比例对灾难性遗忘的影响。跨天数据训练时，如果只用新数据，模型在旧日测试集上性能会塌陷；混入一定比例历史数据后，宏 F1 稳定在 0.96 以上。

## 5. 科学问题与研究假设

核心科学问题可以概括为：在 Open RAN 的近实时架构中，能否用 UE 级 KPM 时间序列实现高精度、可解释、可由人类快速理解的异常检测？

论文隐含并部分验证了几条研究假设：

- 假设一：DDoS 攻击会在 UE KPM 的时间结构中留下可学习模式，而不是只体现在单点异常值上。
- 假设二：轻量 LSTM 足以捕捉短窗口 KPM 依赖，并满足 near-RT RIC 对推理开销的要求。
- 假设三：SHAP 和 LIME 能把黑盒序列分类器的判定转化为可审查的特征贡献证据。
- 假设四：LLM 能在不参与核心检测的情况下提升解释可读性，使告警从“特征归因表”变成“运维可理解的事件说明”。
- 假设五：在连续多日或增量式训练中，保留一定比例历史数据能缓解灾难性遗忘。
- 假设六：XAI+LLM 的解释任务更适合放在 Non-RT RIC/rApp，而不是 Near-RT xApp。

## 6. 科学方法与技术路线

技术路线可以分为六段。

1. 数据采集  
   RAN 组件从 UE 连接和传输过程中收集 KPM，通过 E2 接口发送到 Near-RT RIC。指标包括上下行 bit rate、CQI、发送字节、传输错误、重传等。

2. IDS xApp 预处理  
   xApp 对 KPM 做清洗、归一化和窗口化，把连续采样点组织成形状为 `(3, 14)` 的短序列输入。

3. 序列分类  
   主模型是 32 单元 LSTM，后接 sigmoid 输出层，执行正常/攻击二分类。训练使用 Adam、binary cross-entropy、batch size 64、early stopping。

4. 本地解释  
   对单次预测使用 LIME 和 SHAP。LIME 用局部线性替代模型描述“哪些条件推动了该判定”；SHAP 用特征贡献值描述各时间步、各 KPM 对攻击或正常类别的贡献。

5. 全局解释  
   聚合测试集上的 SHAP 绝对值，获得模型总体依赖的关键特征和关键时间步。论文发现 dl_bitrate、ul_bitrate、ul_tx、dl_tx、ul_retx 等是重要信号。

6. LLM 自然语言解释  
   Prompt 中包含正常/攻击统计、模型输入序列、模型输出、LIME/SHAP 局部解释、全局 SHAP 重要性和任务指令。作者比较 zero-shot 与 few-shot，并比较 GPT-4-Turbo、DeepSeek-V3-R1、Mistral-Large、Gemini-2.0-Flash 等模型的解释质量。

## 7. 实验设计与实验步骤

可复核流程如下。

**数据**  
使用 NCSRD-DS-5GDDoS 数据集，来自 Demokritos 真实 5G 测试床。测试床包含 3 个小区、共享 5G core、9 个 UE。最多 5 个恶意 UE 发起 SYN flood、ICMP flood、UDP fragmentation、DNS flood、GTP-U flood。KPM 每 5 秒采样一次。总样本 686,009 条，其中 benign 674,553 条，malicious 11,456 条，攻击比例约 1.7%。

**预处理**  
删除单一取值特征和无关标识符，例如 IP 地址；删除 NaN 记录；选择连续传输时段；构造 3 个时间步、14 个特征的序列；用 RobustScaler 归一化；训练/测试按 80/20 划分。为缓解跨天训练的灾难性遗忘，实验比较是否混入历史数据，并搜索历史数据比例 0.1 到 0.5。

**模型/基线**  
主模型为 LSTM。对比模型包括 TCN 和 Transformer。外部相关工作对比中还重新实现了 kNN 和 XGBoost，并与既有 NCSRD 数据集研究中的 CNN/LSTM 等结果比较。

**训练**  
优化器 Adam，损失函数 binary cross-entropy，batch size 64，early stopping patience 为 5。搜索窗口大小、历史数据比例、模型结构相关超参数。最终选择窗口大小 3、历史数据比例 0.3。

**指标**  
检测指标包括 macro F1、FPR、FNR、误分类分布、推理时间和模型大小。解释质量指标包括 Flesch Reading Ease、Gunning Fog Index、BERTScore。LLM 输出还做了小规模用户研究，12 名电信工程师评价 10 条解释是否清晰有用。

**消融/敏感性**  
论文重点分析了两类敏感性：历史数据比例对 F1 的影响，以及窗口大小/比例组合对 FPR 和 FNR 的影响。类别不平衡方面比较了无重采样与 SMOTE+Tomek 重采样。

**结果核查**  
最终 LSTM 被选中，不仅因为 F1 高，还因为 FPR/FNR、推理时间和模型大小之间折中最好。SMOTE+Tomek 把 FNR 从 6.24% 降到 3.01%，但 FPR 从 0.045% 升到 0.334%，说明召回提升以更多误报为代价。作者还用 TP/TN/FP/FN 四类样本的 LIME/SHAP 图检查模型决策依据，避免只报告总体分数。

## 8. 关键结果、结论与证据

最重要的检测结论是：短窗口 UE KPM 序列足以支持高精度 DDoS 检测。论文报告最终框架 macro F1 超过 0.96，并且平均单样本推理时间约 0.03 ms，约 36K FLOPs，在标准 Intel i7-10700 CPU 上即可运行，说明 IDS xApp 侧部署具备现实可能。

历史数据比例实验很有价值。没有历史比例时，平均 macro F1 峰值约 0.90，且跨天性能不稳；引入历史数据后，F1 稳定超过 0.95。表 VIII 中 Day 4 在无历史比例时跌到 0.36，而比例 0.3 时各天都超过 0.96。这说明论文不是只做静态随机划分，而是触及了网络安全数据随时间变化的问题。

类别不平衡实验给出了清晰取舍。重采样后 FNR 从 6.24% 降到 3.01%，尤其改善了较难检测的 GTP-U 类攻击召回；但 FPR 上升到 0.334%。在安全场景下，这种取舍通常可接受，但取决于运营商能否承受误报成本。

XAI 结果显示模型确实依赖合理的网络指标。TP 和 FP 中，ul_bitrate、ul_tx、ul_retx、dl_tx、dl_bitrate 等特征有明显攻击方向贡献；TN 中虽然 dl_bitrate 可能有攻击倾向，但其他上行和发送特征抵消后仍判为正常；FN 往往表现为关键攻击指示特征贡献较弱。

LLM 解释实验的结论是：reasoning 强的模型语义忠实度略高，Mistral/Gemma 类模型可读性更好；few-shot 通常比 zero-shot 略有提升。用户研究中，良性解释 90% 被评为清晰有用，异常解释为 76.7%，总体 83.3%。这说明攻击解释仍比正常解释更难写得让工程师满意。

## 9. 局限性与待解决问题

第一，攻击类型仍偏集中。论文以 DDoS 为代表，包含 SYN、ICMP、UDP fragmentation、DNS、GTP-U flood，但尚未验证低速、慢速、隐蔽型攻击，也没有覆盖更复杂的控制面攻击、xApp 恶意行为或 E2 接口协议滥用。

第二，部署验证还不完整。论文提出 xApp/rApp 架构，但实验主要是离线评估，没有真正把 IDS xApp 和 XAI+LLM rApp 部署进 Open RAN emulator 或真实 RIC 环境，端到端时延、A1/E2 接口负载、故障恢复和多 UE 并发仍待验证。

第三，LLM 解释质量的评估还偏初步。可读性指标和 BERTScore 只能衡量语言层面，不能充分证明缓解建议在真实网络中安全、有效、无副作用。12 人用户研究规模也较小。

第四，XAI 本身对时间序列模型的解释仍有近似误差。Kernel SHAP 和 LIME 都是模型无关近似方法，在高维序列输入上计算成本和解释稳定性需要进一步分析。

第五，重采样带来的误报上升需要业务化讨论。FNR 降低有价值，但 FPR 从 0.045% 到 0.334% 的增长在大规模 RAN 中可能意味着大量额外告警。

第六，正文包未截断，因此本次理解不受正文缺页影响；但图表中的部分数值细节仍建议回到 PDF 高清版本复核，尤其是 Table VII、Table XI 和图 6/7/9/10 的精确数值。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”高度相关，尤其适合放在“面向 5G/6G、Open RAN、AI-native 网络的可解释异常检测”方向。

对本项目有三点直接借鉴价值：

- 数据形态上，它证明 KPM/遥测指标也可以作为异常检测主数据源，不必局限于传统流量包、NetFlow 或系统日志。
- 方法框架上，它提供了“轻量检测模型 + XAI 归因 + LLM 解释”的分层范式，适合本项目构建面向运维人员的可解释异常检测报告。
- 实验设计上，它提醒不能只看随机划分 F1，应加入跨时间、类别不平衡、误报/漏报权衡、解释质量和用户可读性评估。

如果本项目也关注跨域异常检测，这篇论文可作为“电信 RAN 域异常检测如何接入 LLM 解释”的代表工作，但不能简单迁移其结论到企业网、工业控制或云原生场景，因为 KPM 特征和攻击表现有明显领域特异性。

## 11. 代码对照分析

本地未发现该论文对应开源代码，因此无法进行逐文件复现映射。根据论文方法，若后续获得代码包，目录大概率应能对应以下模块：

- 数据预处理：读取 NCSRD KPM 数据，删除 IP/单值列/NaN，筛选连续传输时段，构造 `(window_size=3, features=14)` 序列，执行 RobustScaler。
- 模型定义：LSTM、TCN、Transformer 三类序列模型；最终 LSTM 结构应包含 32 hidden units 和 sigmoid 二分类输出。
- 训练脚本：80/20 划分、Adam、binary cross-entropy、batch size 64、early stopping、窗口大小和历史数据比例搜索。
- 不平衡处理：SMOTE 过采样到约 10% 攻击占比，再用 Tomek links 清理边界样本。
- 评估脚本：macro F1、FPR、FNR、按攻击类型统计 FN/FP、推理时间和模型大小。
- XAI 脚本：LIME 局部解释、Kernel SHAP 局部解释、全局 mean absolute SHAP、beeswarm/heatmap/误分类归因图。
- LLM 解释脚本：组装 zero-shot/few-shot prompt，调用 GPT、DeepSeek、Mistral、Gemini API，计算 Flesch、Gunning Fog、BERTScore。
- 部署线索：理论上会有 xApp/rApp 接口模拟代码，但论文并未证明存在完整 RIC 部署实现。

因此，当前可确认的是论文有清晰方法链路，但没有本地源码可验证其工程实现、依赖版本、数据处理细节和随机种子控制。

## 12. 本篇精华

- 论文真正的贡献是把 RAN 异常检测从“高分黑盒分类器”推进到“近实时检测 + 可解释证据 + 自然语言运维说明”的完整链路。
- IDS xApp 与 XAI+LLM rApp 的拆分是关键架构选择：检测走 near-real-time，解释和建议走 non-real-time。
- UE 级 KPM 多变量时间序列可以有效捕捉 DDoS 行为，最终 LSTM 在真实 5G 数据上 macro F1 超过 0.96。
- 历史数据比例 0.3 对缓解灾难性遗忘非常关键；没有历史数据时跨天性能可能严重崩塌。
- 类别不平衡不能被忽视，SMOTE+Tomek 明显降低漏报，但会提高误报。
- SHAP/LIME 让模型依赖的关键 KPM 变得可审查，主要包括 dl_bitrate、ul_bitrate、ul_tx、dl_tx、ul_retx 等。
- LLM 不负责最终检测，而是把 XAI 表格和特征统计转成可读解释；few-shot 通常比 zero-shot 更稳定。
- 论文尚未完成真实 RIC 闭环部署，后续重点应是 Open RAN emulator 实测、自动缓解策略和低速隐蔽攻击检测。

## 13. 建议精读路线

建议先读 Introduction 和 Fig. 1，抓住 xApp/rApp 分工，这是全文架构主线。

第二步读 Section IV-A 和 IV-B，重点看数据集、KPM 特征、窗口构造、训练配置和模型选择。这里决定了实验结果是否可信。

第三步精读 Fig. 6、Fig. 7、Table VIII、Table IX。它们比单个 F1 分数更重要，因为展示了灾难性遗忘、误报漏报和类别不平衡处理。

第四步读 Section III-B、Fig. 8 到 Fig. 11，理解 LIME/SHAP 如何解释 TP/TN/FP/FN，尤其关注误分类样本的归因模式。

最后读 Section III-C、Fig. 12、Fig. 13、Table XI 和用户研究部分，判断 LLM 解释到底是在增强可用性，还是只是把归因表重新包装成自然语言。

<!-- codex-cli-deep-read: complete -->
