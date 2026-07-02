# [610] Ano2Rule: Rule-Based Global Interpretation for Unsupervised Anomaly Detection in Security

## 1. 基本信息

- **题名中文释义**：Ano2Rule：面向安全领域无监督异常检测的基于规则的全局解释方法。
- **作者**：Ruoyu Li、Yu Zhang、Qing Li、Nengwu Wu、Yong Jiang、Weizhi Meng、Laizhong Cui。
- **年份与来源**：2026，IEEE Transactions on Dependable and Secure Computing，Vol. 23 No. 3，pp. 6685-6702。
- **DOI**：10.1109/TDSC.2026.3667688。
- **主题定位**：入侵检测与网络异常检测中的可解释 AI，尤其是无监督异常检测模型的全局规则抽取。
- **正文状态**：正文包标注未截断，本次理解基于完整正文包。
- **代码状态**：用户给出的 `source\UADRule-Extraction` 不存在；本地实际存在高度相关目录 `source\UAD-Rule-Extraction`，README 对应论文前身 NeurIPS 2023 版本，核心 IC-Tree/CBE 方法一致，但不完全覆盖 TDSC 2026 版全部实验。

## 2. 中文翻译与核心摘要

这篇论文要解决的是：安全场景里无监督异常检测模型能发现未知攻击，但模型输出通常是黑盒分数，安全分析员难以信任，也难以把模型直接部署到 Snort、iptables 一类规则驱动工具中。Ano2Rule 的核心思想不是解释单个告警，而是把黑盒无监督检测器的“正常区域”抽成一组人可读规则：样本落入任一规则覆盖区域则视为正常，否则视为异常。

方法分两步：先用 **Interior Clustering Tree, IC-Tree** 把复杂、多模态的正常流量分布拆成若干组合分布；再用 **Compositional Boundary Exploration, CBE** 在每个子分布内探索黑盒模型的判定边界，得到边界规则。最终规则集既是全局解释，也是可在线执行的代理检测器。

## 3. 论文解决的具体问题

论文针对的是一个很具体的安全工程痛点：**无监督异常检测只用正常数据训练，但部署时必须解释“模型为什么认为某些流量不正常”**。已有方法的问题在于：

- 监督式规则抽取依赖正常/攻击双类标签，而无监督异常检测的优势恰恰是无需已知攻击标签。
- LIME、SHAP 等局部解释能解释单个样本，却不能让安全团队审计整个检测逻辑。
- 简单决策树代理模型在高维、多模态网络流量上容易牺牲保真度。
- 单一超立方体或单一规则集难以覆盖正常行为：服务器的 Web、数据库、邮件等服务本来就对应不同流量分布。

因此，Ano2Rule 的目标是：在只给定训练数据、黑盒模型 `f` 和阈值 `ϕ` 的情况下，抽取一组与黑盒预测高一致、可读、可部署的正常性规则。

## 4. 创新点深度提炼

1. **把无监督异常检测解释问题改写为“正常区域 allowlist 抽取”**  
   规则不是描述攻击签名，而是描述黑盒模型眼中的正常行为边界；不匹配任何正常规则即为异常。这一点非常贴近安全部署。

2. **提出分布分解规则，而不是直接拟合全局边界**  
   论文承认正常流量是多模态的，因此先拆分正常分布，再在每个局部子空间估计边界。这个“先分布、后边界”的结构是方法有效的关键。

3. **IC-Tree 用黑盒模型分数驱动无标签划分**  
   它类似 CART，但分裂准则不使用类别标签，而使用黑盒模型输出的正常性/异常性分数。这样它能在无攻击标签条件下把样本划入更同质的子分布。

4. **CBE 用查询式边界探索替代异常样本依赖**  
   CBE 从每个子分布的最小包围超立方体出发，在每个维度上采样 explorer，并用近似梯度方向向外寻找黑盒模型阈值边界。

5. **一套规则同时支持全局解释、局部解释和反事实解释**  
   全局上是规则集；局部上可以用样本到规则边界的距离表示特征贡献；反事实上可以把异常样本投影到最近的正常规则区域。

## 5. 科学问题与研究假设

核心科学问题是：**在没有攻击标签的情况下，能否用有限的轴对齐规则高保真近似无监督黑盒检测器的判定边界？**

论文隐含了几条关键假设：

- 正常安全数据并非单峰分布，而是由多个组合分布构成。
- 黑盒模型输出分数能反映样本属于某个正常子分布的相似性。
- 子分布内部的边界比全局边界更简单，因此可由轴对齐规则近似。
- 通过有限黑盒查询可以在每个维度上探索出足够接近的边界。
- 中等比例噪声不会显著破坏规则抽取，因为 IC-Tree/CBE 关注的是整体正常区域。

这些假设很重要：如果黑盒模型依赖强交互特征、斜向边界或数据分布剧烈漂移，Ano2Rule 的规则数、规则长度或保真度都可能恶化。

## 6. 科学方法与技术路线

技术路线可以概括为：

1. 给定正常训练集 `X`、黑盒无监督检测器 `f`、异常阈值 `ϕ`。
2. 用 IC-Tree 在训练样本上递归分裂：
   - 每个节点计算样本的黑盒输出分数。
   - 用类似 soft Gini 的准则选择特征和阈值。
   - 停止条件包括样本过少、分数差异足够小或达到最大深度 `τ`。
3. 每个叶节点形成一条分布分解规则，即从根到叶的路径约束。
4. 在每个叶节点上执行 CBE：
   - 找到该子分布内正常样本的初始包围区域。
   - 在每个特征维度的上下边界处采样 explorer。
   - 用 beam search 保留最接近黑盒异常边界的候选点。
   - 用有限差分近似梯度方向，逐步外推边界。
5. 将 IC-Tree 路径规则与 CBE 边界规则合取，所有叶规则取并集。
6. 推理时，样本匹配任一规则为正常，不匹配则为异常。

本质上，Ano2Rule 是一个 **post-hoc、model-agnostic、query-based、rule-based surrogate**。

## 7. 实验设计与实验步骤

可复核流程如下：

1. **数据**：使用 CIC-IDS2017、CSE-CIC-IDS2018、TON-IoT、CIC-IoT、RT-IoT2022 五个网络/IoT 安全数据集，样本为表格化流量特征。
2. **预处理**：按 6:2:2 划分训练、验证、测试；训练阶段只使用正常流量；论文还使用修正后的 CIC-IDS2017/CSE-CIC-IDS2018 版本以减少标签错误。
3. **黑盒模型**：训练 AE、VAE、OCSVM、iForest 四类无监督异常检测器，并在 Table III 报告 AUC、TPR、TNR。
4. **规则抽取**：对训练样本查询黑盒分数，先拟合 IC-Tree，再对每个叶节点运行 CBE，得到最终规则集。
5. **基线方法**：比较 UAD rule extraction、EGDT、Trustee、LIME 聚合式全局解释、KD/REDT 类蒸馏树方法。
6. **指标**：主要看 Fidelity、Robustness、TPR、TNR；可解释性补充看规则数量、平均规则长度、Top-10 规则覆盖率。
7. **消融/敏感性**：比较无 IC-Tree、KMeans 替代 IC-Tree、仅超立方体替代 CBE；测试噪声比例、树深 `τ`、explorer 数 `Ne`、采样半径 `ρ`、步长 `η`。
8. **结果核查**：除汇总指标外，论文用 DDoS、XSS、password、ransomware 等样例检查规则解释是否符合安全专家直觉。

## 8. 关键结果、结论与证据

论文结论是：Ano2Rule 在大多数数据集和黑盒模型上能保持较高保真度和鲁棒性。

- Fidelity 在所有数据集上超过 0.95，超过一半设置达到 0.99 以上。
- Robustness 大致处于 0.9890 到 1.00，说明小扰动下代理规则输出稳定。
- 在 TON-IoT 上，多种黑盒模型的 TPR 达到 1.00，最低 TNR 仍约为 0.9715。
- 论文称 Ano2Rule 在 64 个评测设置中有 50 个指标超过 0.95，体现的是稳定性而非单点最优。
- 噪声实验中，40 个 fidelity 分数有 36 个保持在 0.95 以上，但 iForest 在较高噪声下会受影响。
- 规则集规模较可控：例如 TON-IoT 上规则数约 21-28；平均规则长度约 12，低于 CIC-IDS2017 近 80 维特征规模。
- 案例分析中，DDoS 样本违反了包大小均值、包间隔均值、连接时长等正常规则，这与高频短连接、小包冲击资源的攻击直觉一致。

需要注意一处文字层面的可疑点：论文正文称在 CIC-IDS2017 上 TNR “提升约 0.16”，但括号里的数值从 0.9947 到 0.9915 并不是提升。若要引用该结论，应回 PDF 的 Table IV 逐项复核。

## 9. 局限性与待解决问题

- Ano2Rule 主要面向表格化流量特征；论文也承认扩展到图像、原始包、日志序列等模态仍需新机制。
- 轴对齐规则天然偏向矩形边界，对强特征交互、斜向边界、复杂流形的表达能力有限。
- 方法保真的是黑盒模型本身，不保证黑盒模型依据合理特征决策；论文案例也提醒了 shortcut learning 和伪相关问题。
- CBE 需要大量黑盒查询，复杂度与叶子数、特征维度、迭代次数、采样数线性相关；离线抽取可接受，但大规模高维场景仍需优化。
- 实验中的扰动鲁棒性更接近普通噪声稳定性，不等价于对自适应攻击者鲁棒。
- 本地代码是 NeurIPS 2023 前身仓库，TDSC 2026 正文中的 CIC-IoT、RT-IoT2022 以及部分新基线在该代码目录中没有完整对应。
- 正文包未截断；本次不存在因正文截断导致的理解缺口，但表格数值和图中曲线若用于正式综述，仍建议回到 PDF 精确核对。

## 10. 与本项目的关系

这篇论文与“异常检测”项目的关系是中高价值但偏解释层：它不是提出更强的异常检测模型，而是给现有无监督检测器增加可审计、可部署的规则外壳。

对项目可直接借鉴的点包括：

- 给 AE/VAE/OCSVM/iForest 等模型统一加一层规则解释。
- 将正常行为抽成 allowlist，用于 SOC 告警解释和误报分析。
- 用规则检查模型是否学到 IP、端口、测试床环境等伪相关特征。
- 把高维异常分数转成安全人员熟悉的“特征-阈值”谓词。
- 作为论文综述中“可解释异常检测/规则抽取/无监督安全 XAI”的代表工作。

## 11. 代码对照分析

本地可读代码目录是 `source\UAD-Rule-Extraction`，不是元数据里的 `source\UADRule-Extraction`。README 显示仓库地址为 `Ruoyu-Li/UAD-Rule-Extraction`，对应 NeurIPS 2023 前身版本。

关键对应关系如下：

- 项目说明与运行入口：[README.md](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/README.md:1)、[example.ipynb](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/example.ipynb:126)。
- 数据下载：[script.sh](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/dataset/script.sh:1)、[downloader.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/dataset/downloader.py:1)。
- 数据加载与预处理：[data_load.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/data_load.py:8)、[global_var.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/global_var.py:1)、[normalize.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/normalize.py:1)。
- PCAP 到流特征：[feature_extract.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/feature_extract.py:16)，包含包大小、IAT、duration、协议/端口等 30 维自定义特征。
- 黑盒模型训练：[AE.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/AE.py:1)、[VAE.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/VAE.py:1)、[OCSVM.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/OCSVM.py:1)、[IForest.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/IForest.py:1)、[blackbox.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/blackbox.py:22)。
- IC-Tree 与规则模型：[KITree.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/KITree.py:9)，其中 `fit` 对应 IC-Tree 训练，`get_rules_dict` 对应规则导出，`interpret_sample` 和 `counterfactual` 对应局部/反事实扩展。
- CBE 边界探索：[ExtBound.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/ExtBound.py:4)，`fit`、`explorer_sampling`、`set_bound` 对应论文 CBE。
- 消融和噪声实验：[ablation.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/experiment/ablation.py:21)、[noise.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/experiment/noise.py:46)。

运行线索：README 建议用 `example.ipynb` 复现规则抽取；单模型可用类似 `python src/AE.py train toniot_custom dos`、`python src/AE.py test toniot_custom dos` 的方式。需要注意：`src/experiment/train.py` 顶部导入了 `Whisper`，但本地未见 `Whisper.py`；`KITree_main.ipynb` 也引用了未列出的 `IBMMExtraction`，因此批量实验脚本可能需要修正后再跑。

## 12. 本篇精华

- Ano2Rule 的核心不是解释攻击，而是抽取黑盒模型认可的“正常行为规则”。
- 论文抓住了无监督安全检测的特殊性：没有攻击标签，不能照搬监督式规则抽取。
- IC-Tree 的价值在于把多模态正常流量拆成更容易解释的组合分布。
- CBE 的价值在于用黑盒查询探索边界，减少对真实异常样本的依赖。
- 最终规则集既是全局解释，也是轻量在线代理模型，适合安全规则系统集成。
- 规则解释还能暴露模型是否依赖伪相关特征，这是安全部署中比单纯高 AUC 更关键的问题。
- 代码可验证核心算法，但本地版本更接近 2023 版，不能视作完整复现 TDSC 2026 全部实验。

## 13. 建议精读路线

1. 先读 Introduction 的 CH1-CH3，明确无监督解释为什么不同于监督解释。
2. 再读 Section III 的问题定义，抓住规则集 `C` 作为正常 allowlist 的形式化目标。
3. 精读 Section IV，重点画出 IC-Tree 到 CBE 再到规则合并的流程图。
4. 快读 Section V，理解理论分析依赖的是“子分布重叠很小”和“分数紧致”假设。
5. 精读 Table IV、Table V、Fig. 3-7，分别对应主结果、规则复杂度、噪声、消融、超参、局部/反事实扩展。
6. 对照代码读 [KITree.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/KITree.py:9) 和 [ExtBound.py](F:/泉城实验室/二期/论文/异常检测/source/UAD-Rule-Extraction/src/ExtBound.py:4)，确认论文算法在实现里如何落地。
7. 最后读案例分析 Table VI，把规则解释和真实攻击机理对应起来，这是写综述或汇报时最有说服力的部分。