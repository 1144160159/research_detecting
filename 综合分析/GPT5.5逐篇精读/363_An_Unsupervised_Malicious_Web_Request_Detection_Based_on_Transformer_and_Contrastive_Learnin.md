# [363] An Unsupervised Malicious Web Request Detection Based on Transformer and Contrastive Learning

## 1. 基本信息
题名可译为“基于 Transformer 与对比学习的无监督恶意 Web 请求检测”。论文发表于 IEEE Transactions on Network and Service Management，2025 年，DOI 为 `10.1109/TNSM.2025.3563089`。任务类型是恶意 Web 请求/URL 异常检测，方法名为 UTCDetector。正文包未截断；本地代码仓库实际是 School 2023 样例数据包，不包含模型源码。

## 2. 中文翻译与核心摘要
论文的核心主张是：恶意 Web 请求检测不能只依赖有标签攻击样本，也不能在分词时丢掉 `?`、`&`、`=`、`../`、`<`、`>` 等特殊字符，因为这些字符往往正是攻击载荷的结构信号。UTCDetector 用预处理还原混淆请求，用 2-gram 保留相邻词/符号关系，再用 Word2vec 和 Transformer 学习正常请求的语义模式，最后用超球损失和对比学习把正常请求特征压到一个可判别的空间内；新请求如果离正常超球中心过远，就判为异常。

## 3. 论文解决的具体问题
论文聚焦的是“未知恶意 Web 请求”的检测，而不是已知攻击类型分类。作者认为现有方法有四个具体痛点：监督深度模型需要异常标签且偏向已知攻击；人工标注 Web 请求成本高；常规分词会过滤特殊字符，导致 SQLi、XSS、路径穿越等关键结构被削弱；公开数据集偏旧且 Web 请求数据量相对不足，难以支撑大规模监督训练。

## 4. 创新点深度提炼
第一，论文把 Web 请求当作具有语义和结构的短文本/长序列来处理，但没有直接套通用 NLP，而是用 2-gram 显式绑定相邻 token 与特殊字符。第二，Transformer 被用于捕获远距离共现，例如 `union` 与 `select`、`<script>` 与 `alert`、`../` 与敏感文件名之间的关系。第三，超球损失替代交叉熵，使训练只需要正常样本。第四，对比学习中的 alignment 与 uniformity 同时约束“正常样本彼此接近”和“特征不要塌缩”，这是比单纯 one-class 压缩更细的设计。第五，作者补充了 School 2023 数据集，用来弥补 CSIC 2010、Torpeda 2012、ECML/PKDD 2007 偏旧的问题。

## 5. 科学问题与研究假设
科学问题可以概括为：在缺少异常标签、样本量有限、攻击载荷被编码/混淆且含大量特殊字符的情况下，能否仅凭正常请求学习出足够稳定的判别边界？论文隐含的核心假设是：正常 Web 请求在语义-结构空间中形成相对紧凑的分布；恶意请求即使经过大小写、编码、函数替换或组合混淆，也会在 token 共现、特殊字符组合、路径/参数结构上偏离正常分布；正常样本之间的对比学习可以用更少数据逼近这种分布。

## 6. 科学方法与技术路线
技术路线是“请求规范化 → 2-gram 结构保留 → Word2vec 向量化 → Transformer 编码 → 超球/对比损失训练 → 距离阈值检测”。预处理包括抽取 URL/query/body、去域名、大小写归一、重复关键词清理、URL/Base64 解码、等价函数归一。2-gram 让 `or 1=1--` 这类载荷不只变成孤立 token，而是形成 `or 1`、`1 =`、`= 1`、`1 -` 等局部关系。模型端用 Transformer Encoder 输出语义向量，再经均值、池化、dropout、线性层得到深层特征。总损失为超球损失加 alignment loss 和 uniformity loss。

## 7. 实验设计与实验步骤
可复核流程如下：数据使用 CSIC 2010、CSIC TORPEDA 2012、ECML/PKDD 2007 和 School 2023；School 2023 论文中含 99,746 条正常请求和 25,000 条恶意请求。预处理先统一提取 GET 的 URL 与 POST 的 URL/body，再做混淆还原和 2-gram 分词。模型比较包括 One-Class SVM、Pattern-tree、HQTN、Autoencoder、OMRDetector，以及 Word2vec-LSTM、BERT-Transformer、BERT-LSTM 等消融模型。训练时使用正常样本，Word2vec 维度默认 300，Transformer hidden 维度默认 128，多头数 12，batch size 64，max epoch 100。指标为 Precision、Recall、F1-score 和训练/测试时间。消融验证特征提取器、检测器和对比学习；敏感性分析 n-gram、窗口大小、embedding 维度、hidden 维度、多头数。结果核查重点应看同一数据划分下的 F1、阈值选择方式、不同攻击类型检出率。

## 8. 关键结果、结论与证据
论文给出的结论是 UTCDetector 在四个数据集上整体优于既有方法和消融变体。正文明确提到，相比已有方法 F1-score 提升约 0.6% 到 10.6%，相比消融方法提升约 0.1% 到 15.6%。CSIC 2010 上可见最佳 F1 约为 0.99682，ECML/PKDD 2007 上达到 0.98931，且无异常标签时超过 LogBERT-BiLSTM 的 0.97。对比学习的证据较关键：达到相近 F1 时，UTCDetector 所需训练数据接近无对比学习版本的一半。ECML/PKDD 2007 的攻击案例中，SQLi、XSS、DT、SSI、XPathi、Ldapi、OS Commanding 的检测率均为 1。

## 9. 局限性与待解决问题
“无监督”表述需要谨慎：论文说最佳超球半径可由少量正常和异常验证数据确定，这在真实零日场景下仍依赖异常样本或人工阈值策略。School 2023 完整数据未随代码仓库发布，只有样例，复现实验受限。本地样例中正常集也出现 `wp-login.php`、`viewtopic.php?...` 等业务归属不清的路径，提示真实 Web 流量的标签清洗和正常定义需要进一步审查。对加密与组合攻击，论文主要依靠分布偏离和上下文特征，并不能真正理解加密载荷语义。正文包未截断，但纯文本中的部分表格行值没有完整展开；若要复核每个基线的 Precision/Recall/F1，应回到 PDF 表格逐项核对。

## 10. 与本项目的关系
这篇论文与“异常检测”项目是中相关：它的对象是 Web 请求，不一定覆盖通用网络流量、主机日志或多变量时序，但方法上很有参考价值。对本项目最有用的是三点：一是 one-class/超球式正常建模；二是特殊符号与上下文共现对安全异常的重要性；三是用对比学习缓解标注少和样本少的问题。如果本项目涉及 HTTP 日志、WAF、API 网关或 Web 访问日志，它可以作为直接基线；如果项目是跨域异常检测，它更适合作为“文本化安全事件序列”的方法参考。

## 11. 代码对照分析
本地 `source\School-2023-sample` 不是 UTCDetector 源码，而是 School 2023 样例数据。`README.md` 只说明这些样例来自 2023 年某高校 Web 应用服务器。`NormalTrainingSet-Sample.txt` 有 3000 行、3000 个请求起始行，基本是单行 GET，可对应论文中的正常训练集。`NormalTestingSet-Sample.txt` 有 3000 行，其中 2998 个 GET、2 个 POST，可对应正常测试集。`AbnormalTestingSet-Sample.txt` 有 23222 行、约 2282 个请求起始行，其中 2232 个 GET、50 个 POST，保留了完整 HTTP 报文块；其中能看到 `/../../download_validate.jsp`、`/etc/passwd`、`php://filter` 等路径穿越/文件读取类载荷。缺失的源码部分包括预处理脚本、2-gram/Word2vec 训练、Transformer 模型、超球与对比损失、训练和评估脚本，因此只能做数据级对照，不能做函数级复现。

## 12. 本篇精华
- 恶意 Web 请求检测中，特殊字符不是噪声，而是攻击语法的一部分。
- UTCDetector 的关键不是单独使用 Transformer，而是“2-gram 保结构 + Transformer 建上下文 + 超球做 one-class + 对比学习省数据”的组合。
- 对比学习在这里不是构造正常/异常正负样本，而是在正常样本内部同时做拉近与均匀化，减少正常特征塌缩。
- 论文把旧公开数据集不足的问题说清楚，并尝试用 School 2023 补充现代复杂攻击。
- 方法适合未知攻击检测，但阈值选择、真实流量漂移、标签噪声和私有数据复现仍是硬问题。
- 本地仓库只提供样例数据，不提供模型实现；引用该论文时不能把 GitHub 当作完整开源代码依据。

## 13. 建议精读路线
先读 III 节的问题定义，弄清楚作者把 POST body 也合并进 URL 表示；再精读 IV-B 和 IV-C，因为预处理与 2-gram 是这篇论文区别于普通 NLP 检测器的关键；随后读 IV-D/IV-E，重点理解超球损失、alignment、uniformity 三者如何共同塑造正常空间；最后读 V 节时不要只看 F1，要重点核查数据划分、阈值选择、消融对照和 School 2023 的可复现性。

<!-- codex-cli-deep-read: complete -->
