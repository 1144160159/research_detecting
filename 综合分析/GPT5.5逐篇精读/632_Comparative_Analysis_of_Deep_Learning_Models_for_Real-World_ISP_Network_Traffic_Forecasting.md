# [632] Comparative Analysis of Deep Learning Models for Real-World ISP Network Traffic Forecasting

## 1. 基本信息
题名可译为《面向真实 ISP 网络流量预测的深度学习模型比较分析》。论文发表于 IEEE Transactions on Network and Service Management，DOI 为 `10.1109/TNSM.2025.3636557`；正文显示 2025 年 11 月 25 日在线发表，卷期排到 2026 年。正文包标注未截断；代码仓库已下载到 `source/isp-forecasting-benchmark`。

## 2. 中文翻译与核心摘要
这篇论文的核心不是提出一个新模型，而是借助 CESNET-TimeSeries24 这个真实 ISP 大规模时间序列数据集，系统回答“现有深度学习预测模型在真实网络流量上到底表现如何”。作者比较了 LSTM、GRU、FCN 混合模型、ResNet、InceptionTime、RCLSTM、ETSformer，并用 Mean 和 SARIMA 作基线。结论相当务实：复杂模型并不稳定胜出，GRU/LSTM 这类经典循环结构整体更可靠，GRU-FCN 在速度与精度之间最均衡，ETSformer 精度接近前列但计算代价过高。

## 3. 论文解决的具体问题
论文针对的是 ISP 场景中的网络流量预测，而不是直接的入侵检测分类。具体问题包括：如何在真实、长期、层级化的 ISP 流量数据上公平比较预测模型；训练窗口和预测窗口如何影响预测；机构、子网、单 IP 等不同聚合粒度是否改变可预测性；不同监控指标，如字节数、包数、流数、TCP/UDP 比例、方向比例，是否同样容易预测。它服务的下游场景包括容量规划、拥塞规避、SLA 预警、SDN/NFV 资源编排，以及基于预测残差的异常发现。

## 4. 创新点深度提炼
第一，论文把评测重心从合成数据或私有数据转向 CESNET-TimeSeries24 的真实 ISP 数据，覆盖 40 周、多个层级和 18 类指标。第二，它不是只比较单一 `n_bytes`，而是把窗口长度、层级粒度、指标类型、训练/推理耗时一起纳入分析。第三，论文强调可复现 benchmark，公开源码、结果和分析材料。第四，作者引入 Harmonic score，将 RMSE 与 R2 到理想值 1 的距离合并，用于兼顾误差大小和趋势解释能力。第五，论文给出了工程部署视角：ETSformer 虽强但训练/预测时间超过其他模型十倍以上，GRU-FCN 更适合资源受限或需要频繁重训的场景。

## 5. 科学问题与研究假设
论文的四个研究问题可以凝练为四个假设：深度学习在真实 ISP 流量上应优于简单统计基线；短期历史和短期预测可能比长窗口更稳；层级越粗，流量越平滑、越可预测；体量型指标比比例型、方向型指标更可预测。实验结果基本支持后三个假设，但第一个假设更微妙：深度模型通常降低 RMSE，但 Mean 在 R2 上反而很强，说明“预测总体水平/趋势”和“降低点误差”不是同一件事。

## 6. 科学方法与技术路线
技术路线是典型但规模很大的单变量时间序列预测流程：从 CESNET-TimeSeries24 选择 1 小时聚合数据；按机构、机构子网、IP 样本三个层级组织时间序列；每个监控指标单独建模；补齐缺失时间点；划分训练、验证、测试；归一化；滑动窗口生成输入输出对；训练不同模型；用 RMSE、R2 和 Harmonic score 聚合评估；最后按模型、窗口、层级、指标和耗时维度解释结果。论文明确采用 univariate 设置，因此没有利用不同流量指标之间的交互关系。

## 7. 实验设计与实验步骤
1. 数据：使用 CESNET-TimeSeries24 的 1 小时聚合数据，包含 283 个机构、548 个机构子网、1000 个 IP 地址样本，共 1831 条时间序列，时间跨度约 2023 年 10 月至 2024 年 7 月。  
2. 预处理：补齐时间轴；多数指标缺失值补 0，论文称 TCP/UDP ratio 和 direction ratio 用 0.5 表示无通信时的平衡状态；按 35%/5%/60% 划分训练、验证、测试。  
3. 滑动窗口：以训练窗口作为历史输入，以预测窗口作为未来输出；正文讨论日、周、月尺度，结果文件中可见 `(24,1)`、`(24,24)`、`(168,1)`、`(168,24)`、`(168,168)`、`(744,1)`、`(744,168)` 等窗口组合。  
4. 模型/基线：Mean、SARIMA、LSTM、GRU、LSTM-FCN、GRU-FCN、ResNet、InceptionTime、RCLSTM、ETSformer。  
5. 训练：深度模型使用 Adam 与 MSE loss；超参数不是逐序列调优，而是在每个数据部分随机抽 50 条时间序列找“总体可用”的配置。  
6. 指标：报告 RMSE、R2，并构造 Harmonic score；同时记录训练时间和预测时间。  
7. 消融/敏感性与核查：比较窗口长度、预测跨度、层级粒度、指标类型、缺失率；用 ANOVA 检验 GRU 与 ETSformer 差异，多数设置下差异显著。

## 8. 关键结果、结论与证据
最重要的结论是：没有单一模型在所有设置中统治全局。GRU 和 LSTM 整体最稳，GRU-FCN 在机构和子网层级上表现强且训练/预测最快，ETSformer 精度接近前列但部署代价过高。ResNet 与 InceptionTime 在该任务上较弱，说明图像/分类启发的卷积层级特征并不自动适合 ISP 流量预测。粒度方面，机构级最好预测，子网次之，单 IP 最难；IP 级缺失比例与 R2 有明显负相关，论文给出约 `-0.69`。指标方面，`n_bytes`、`n_packets`、`n_flows` 等体量指标更规律，TCP/UDP ratio、direction ratio 更动态、更难预测。预测窗口越长，误差越容易累积，短 horizon 明显更稳。

## 9. 局限性与待解决问题
论文最大局限是单变量、逐序列建模：1831 条序列 × 多指标 × 多窗口 × 多模型带来巨量模型，工程维护困难。缺失值补零虽然符合“无通信”的解释，但会把稀疏 IP 序列变成零膨胀预测问题；比例指标补值策略也需要更细致验证。Harmonic score 是自定义指标，截断阈值来自结果分布，适合作内部排序但外部可比性有限。正文包未截断，但纯文本没有完整保留表格排版；另外，公开代码与论文叙述存在若干需复核点，例如代码里有 `LSTMAE` 分支、结果 CSV 中窗口组合多于正文所称的五组、通用补值代码未看到 ratio 指标补 0.5 的专门逻辑。

## 10. 与本项目的关系
对“异常检测”项目而言，这篇论文中相关性属于中高但偏间接：它提供的是预测基线，而不是带标签的攻击检测器。价值在于可以把预测残差作为无监督异常分数，用于发现突发流量、离群峰值、设备静默、容量异常或 SLA 风险。若本项目关注跨域异常检测，它还提示了一个关键事实：模型在机构级看似优秀，不代表能迁移到 IP 级稀疏序列；指标类型和聚合粒度本身就是异常检测难度的重要变量。

## 11. 代码对照分析
入口在 [main.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\main.py:11>)，参数覆盖数据根目录、聚合粒度、层级、窗口、模型和指标；模型分派在同文件 94 行附近。通用预处理、补齐时间轴、滑窗和 MinMax 归一化在 [runner_component.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\runner_component.py:79>)。LSTM/GRU/FCN/ResNet/InceptionTime 通过 tsai 封装在 [dl_runner.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\dl_runner.py:22>)；超参数和模型映射在 [constants.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\utils\constants.py:3>)。ETSformer 走独立分支 [etsformer_runner.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\etsformer_runner.py:9>) 和 `src/ETSformer/`。评估指标在 [evaluation_metrics.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\utils\evaluation_metrics.py:14>)。批量 PBS 作业线索在 [job_generator.py](<F:\泉城实验室\二期\论文\异常检测\source\isp-forecasting-benchmark\src\metacentrum_scripts\job_generator.py:18>)。运行时需要把 CESNET 数据放成 `data/<group>/agg_1_hour/<file_id>.csv` 和 `times.csv` 结构；仓库自带 `results/` CSV 与分析 notebook，但 Mean/SARIMA 的生成入口未在主 runner 中看到，更像是另行生成后汇总。

## 12. 本篇精华
- 真实 ISP 流量预测中，经典 GRU/LSTM 比许多复杂结构更稳。  
- ETSformer 精度接近第一梯队，但训练和推理代价让部署价值打折。  
- GRU-FCN 是论文中最值得工程优先尝试的折中模型。  
- 粒度越细，缺失越多、突发越强，可预测性越差。  
- `n_bytes` 等体量指标相对容易，ratio/方向类指标明显更难。  
- 短预测窗口显著更可靠，长 horizon 面临误差累积。  
- 预测模型可作为异常检测的 expected baseline，但不能直接等同异常检测系统。  
- benchmark 的意义大于单个模型排名，因为它把数据、窗口、层级、指标和耗时一起纳入比较。

## 13. 建议精读路线
先读 Introduction 的四个 RQ，把论文问题意识固定住；再读 Dataset 和 Methodology，重点看 1 小时聚合、层级划分、缺失值处理、滑窗和 35/5/60 切分；随后读 Results 的 `n_bytes` 表和其他指标讨论，理解为什么 GRU/LSTM 胜出、为什么 IP 级困难；最后读 Discussion/Conclusion，把四个 RQ 的回答整理成综述材料。代码精读顺序建议为 `main.py` → `runner_component.py` → `constants.py` → `dl_runner.py` → `etsformer_runner.py` → `evaluation_metrics.py` → `analysis_HARMONIC-SCORE.ipynb`。

<!-- codex-cli-deep-read: complete -->
