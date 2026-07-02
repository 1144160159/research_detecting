# [704] HoneyLLMd: A Large Language Model-Powered Adaptive Honeypot System

## 1. 基本信息

- 论文：HoneyLLMd: A Large Language Model-Powered Adaptive Honeypot System
- 年份：2026
- DOI：10.1109/TNSE.2026.3683862
- 来源：IEEE Transactions on Network Science and Engineering
- 主题：LLM 驱动自适应蜜罐、恶意流量捕获、反向 Shell、欺骗防御
- 本地代码状态：未发现该论文对应开源代码包
- 正文状态：本次正文包完整，未截断

## 2. 中文翻译与核心摘要

这篇论文提出 HoneyLLMd，一个用大语言模型增强的自适应蜜罐系统。它试图解决传统蜜罐长期存在的矛盾：高交互蜜罐能观察真实入侵链，但暴露真实系统，风险高；低/中交互蜜罐风险低，但只能模拟有限服务，很难支撑真实感 Shell 交互，尤其难以处理现代攻击中常见的反向 Shell。

HoneyLLMd 的核心思路是：不把真实 OS 暴露给攻击者，而是让 LLM 生成“看起来像真实系统”的命令响应；同时用分层概率自动机 HPA 建模攻击者命令状态转移，根据攻击路径的概率收益动态决定是否阻断某些命令，并由 LLM 生成合理的失败或成功反馈。这样系统既能诱导攻击者继续操作、泄露意图和行为，又能降低真实系统被攻陷的风险。

论文不仅做了概念设计，还实现了 Python 原型，支持 bind shell 与 reverse shell 两类交互，并在 Cowrie 日志数据、真实云环境部署、CTFAgent 仿真攻击中评估了 LLM 响应质量、Shell 解码能力、阻断阈值、会话持续时间和采集命令数量。

## 3. 论文解决的具体问题

论文瞄准的是蜜罐交互深度与安全风险之间的结构性冲突。

第一，传统 LIH/MIH 通常只能做浅层协议或命令模拟。攻击者一旦进入后渗透阶段，执行复杂 Shell 命令、反弹连接、持久化、信息收集时，这类蜜罐容易露馅。

第二，HIH 可以真实执行攻击载荷，支持反向 Shell，但代价是把真实 OS、服务、文件系统和网络能力暴露给攻击者。攻击者可能真正控制蜜罐、横向移动或把蜜罐变成攻击跳板。

第三，已有 LLM 蜜罐多停留在“收到命令后生成回复”的层面，缺少攻击路径级策略控制。也就是说，它们可能更像一个会聊天的假 Shell，而不是一个会根据攻击链风险调整诱导策略的欺骗系统。

第四，现代攻击框架大量使用 reverse shell，但多数低/中交互蜜罐只适合 bind shell。论文把安全支持 reverse shell 作为重点问题之一。

## 4. 创新点深度提炼

1. 把 LLM 用作 Shell 响应生成器，而不是部署真实 OS。  
   这使蜜罐在交互效果上接近 HIH，但安全暴露面接近 MIH。论文用公式把暴露水平、数据捕获能力和被攻陷概率联系起来，强调 LLM 可以让“交互暴露”看似接近 1，而真实系统风险不随之上升。

2. 支持 bind shell 与 reverse shell。  
   这是相对很多 LLM Shell 蜜罐更重要的工程扩展。反向 Shell 更符合真实攻击实践，尤其是 NAT、入站防火墙和 C2 场景下的攻击链。

3. 用 HPA 对攻击命令链建模。  
   论文不是只看单条命令，而是把命令拆成宏状态和微状态，例如程序名、参数、路径，再构建状态转移矩阵。这样系统可以估计攻击者下一步更可能走向哪里。

4. 用 payoff 和 block threshold 做动态策略。  
   当攻击者当前路径过于接近高概率攻击目标时，蜜罐可以阻断，并让 LLM 生成“permission denied”“timeout”等合理失败响应；当风险可接受时，则生成成功执行结果来继续诱导。

5. 提出一组 Shell 欺骗指标。  
   论文定义 SALC、SANLC、FALC、FANLC 四类，并派生 Precision、Temptation、Attack Success Rate、Accuracy，用真实系统输出作为参照，评估蜜罐响应是否既像真实系统，又足够吸引攻击者继续操作。

6. 进行了模型、阈值、消融和仿真多维实验。  
   论文比较 GPT-5-mini、GPT-4o-mini、Gemini-2.5-flash、Claude-haiku-3.5 等模型，评估 Shell 解码、响应欺骗、会话持续时间、唯一命令数量和阻断收益。

## 5. 科学问题与研究假设

核心科学问题可以概括为：能否在不暴露真实操作系统的前提下，让蜜罐获得接近高交互蜜罐的数据捕获能力，并通过自适应策略降低被识破或被利用的风险？

论文隐含了几条研究假设：

- LLM 能生成足够符合 OS 语义的 Shell 响应，使攻击者愿意继续交互。
- 攻击命令序列存在可学习的状态转移规律，可以被 HPA 捕获。
- 对高 payoff 攻击路径进行动态阻断，可以迫使攻击者尝试替代路径，从而采集更多行为数据。
- LLM 生成的失败反馈如果上下文合理，不一定会终止攻击，反而可能诱导攻击者进行更多探测。
- 支持 reverse shell 能显著提升蜜罐对真实攻击链的覆盖能力。

## 6. 科学方法与技术路线

系统由 Request Handler、Shell Engine、Logger、Countermeasure Engine 和外部 LLM Engine 组成。

Request Handler 负责监听端口、管理连接和会话。它既处理 SSH/Telnet 等 bind 交互，也捕获可能触发 reverse shell 的恶意 payload。

Shell Engine 是交互核心，包括 Shell Decoder、Bind Port Interaction、Connect Back Interaction 和 Shell Emulation。Decoder 用正则或 LLM 解析 payload，提取反连地址、端口、语言和编码特征；Shell Emulation 不执行真实命令，而是调用 LLM 生成模拟输出。

Countermeasure Engine 使用 HPA 建模攻击过程。命令先被拆成子命令，再映射为宏状态和微状态，形成过程向量；系统统计状态转移次数矩阵 C，再归一化为概率矩阵 M，并加入平滑项避免零概率。

策略层计算实际路径概率与最优路径概率的比值，形成攻击者收益 Rap，蜜罐收益 Rhp = 1 - Rap。当 Rap 超过阻断阈值 B 时，系统认为攻击者过于接近高收益攻击路径，于是阻断并生成合理失败响应。

## 7. 实验设计与实验步骤

1. 数据  
   使用两个 Cowrie 真实日志数据集。Dataset 1 来自 2022 年云蜜罐日志，214,132 条记录，82 个唯一命令，用于 LLM 能力评估和 HPA 构建。Dataset 2 来自 Kaggle，2024 年 10 月，42,817 条记录，67 个唯一命令，用作 HPA 启用后的攻击与评估集，避免训练/评估污染。

2. 预处理  
   从 JSON 日志中抽取输入事件，保留 session、源地址、时间戳；按 session 分组并按时间排序；对管道、分号、条件操作符等复合命令做子命令拆分，同时避免错误切分引号内内容。

3. 模型与基线  
   LLM 侧比较 GPT-5-mini、GPT-4o-mini、Gemini-2.5-flash、Claude-haiku-3.5。蜜罐基线包括真实系统、Cowrie、Amun、LLM-only HoneyLLMd 和 LLM+HPA HoneyLLMd。

4. 训练/建模  
   用 Dataset 1 构建 HPA 状态空间和转移矩阵。状态包括命令主程序和参数/路径等微状态；状态转移矩阵动态更新。阻断策略通过 block threshold B 控制。

5. Shell Decoder 实验  
   构造 91 个 payload，其中 64 个为混淆恶意 payload，27 个为正常 payload；覆盖 Bash、Perl、Python、PHP、Ruby、Netcat、PowerShell、Lua，以及 Base64、URL、十六进制、多层编码、环境变量拼接等混淆方式。比较正则和 LLM 的识别准确率与延迟。

6. 欺骗响应指标  
   用真实系统输出作为 oracle，将 LLM 响应标注为 SALC、SANLC、FALC、FANLC，并计算 Precision、Temptation、Attack Success Rate、Accuracy。

7. 消融与敏感性  
   比较 LLM-only 与 LLM+HPA；改变阻断阈值 B，观察攻击者 payoff、蜜罐 payoff、阻断比例和欺骗指标变化。论文认为 B = 0.6 是较合适折中点。

8. 结果核查  
   在 CloudLab 部署 Amun、Cowrie 和 HoneyLLMd，比较真实攻击中的会话持续时间和唯一命令数；在隔离 cyber-range 中用 CTFAgent 模拟攻击，观察阻断后攻击路径扩展、状态转移增加和 token 消耗变化。

## 8. 关键结果、结论与证据

Shell 解码方面，正则延迟最低，约 53.48 ms，接近真实系统响应延迟，但对混淆 payload 漏检和误报明显。LLM 平均延迟约 805.38 ms，慢得多，但 GPT-5-mini、Claude-haiku-3.5、Gemini-2.5-flash 对混淆 payload 的识别正确率普遍超过 90%。这说明 LLM 更适合复杂语义解析，但实时部署需要混合架构。

欺骗响应方面，LLM 蜜罐整体优于 Cowrie。GPT-5-mini 的吸引力和攻击成功模拟能力最强，Claude-haiku-3.5 的准确性最高或接近最高。Cowrie 在部分命令响应中存在逻辑不一致，说明硬编码 Shell 很难覆盖真实攻击命令空间。

数据集相似度方面，2022 与 2024 两个数据集命令分布余弦相似度只有约 0.15。2022 数据更偏系统画像和资源探测，2024 数据更偏持久化、反向 Shell、BusyBox 和 SSH key 注入。这支持论文关于攻击行为动态变化的判断，也说明 HPA 必须持续更新。

阻断阈值方面，B 从 0.1 到 0.6 时，大部分高风险转移仍被阻断，蜜罐收益较高；超过 0.6 后攻击者平均 payoff 明显上升，系统风险增加。论文选择 0.6 作为数据捕获与风险控制的折中点。

消融方面，LLM+HPA 相比 LLM-only 提升 Precision 和 Accuracy，同时降低 Temptation 与 Attack Success Rate。这不是坏事，而是说明 HPA 减少了过度“放行”攻击的风险。部署实验中，LLM+HPA 最大会话时长达到 390.67 秒，平均 76.41 秒，采集唯一命令 2,842 条，比 LLM-only 多 1,337 条。

CTFAgent 仿真中，HoneyLLMd 阻断后诱导攻击代理尝试更多替代命令和状态转移，尤其在信息探测、密码修改、执行、SSH key 持久化阶段更明显。token 消耗升高也侧面说明攻击代理需要重新规划。

## 9. 局限性与待解决问题

第一，payoff 被建模为零和互补关系，即 Rap + Rhp = 1，但真实攻防并不一定是常和博弈。攻击者可能失败但获得环境信息，蜜罐可能捕获数据但付出 API 成本和被识别风险。

第二，LLM 评估模型数量有限，且成本、延迟、上下文长度和安全策略差异会影响结论。论文虽然比较了几个主流模型，但还不足以抽象出“什么模型能力最适合蜜罐”。

第三，LLM 解码与响应延迟较高。对实时 Shell 来说，800 ms 级别的解析延迟可能已经成为侧信道特征，熟练攻击者可能通过响应时间识别蜜罐。

第四，系统主要评估 Shell 交互，对 Web、数据库、ICS、云 API、容器编排等复杂环境的欺骗能力还没有展开。

第五，LLM 可能产生幻觉式输出，尤其是跨命令状态一致性、文件系统持久状态、权限模型、包管理器差异等方面。论文用逻辑一致性指标评估了一部分，但真正长期交互下的状态管理仍是难点。

第六，反向 Shell 的安全边界需要更严格说明。论文强调不执行真实 OS 命令，但 connect-back 交互本身涉及网络连接行为，实际部署时仍需要网络隔离、出站控制和审计策略。

## 10. 与本项目的关系

这篇论文与“恶意流量、暗网与攻击检测”方向强相关。它不是单纯做流量分类，而是把蜜罐作为主动采集恶意行为数据的前端传感器，用交互诱导方式获取攻击命令、payload、反连行为和持久化尝试。

对异常检测项目的价值主要有三点：一是可用于构建更丰富的攻击序列数据集，而不仅是五元组或单包特征；二是 HPA 状态转移矩阵可以转化为序列异常检测特征；三是 LLM 生成响应与阻断策略可以帮助采集攻击者在受挫后的替代路径，这类数据对检测未知攻击和攻击策略迁移很有价值。

如果本项目关注暗网扫描、SSH/Telnet 爆破、IoT botnet 或 C2 行为，HoneyLLMd 的 reverse shell 捕获和命令序列建模尤其值得借鉴。

## 11. 代码对照分析

本地未发现该论文对应开源代码包，因此无法逐文件核验实现。但根据论文实现描述，可以推断其代码结构大概率会包含以下模块：

- 数据预处理：读取 Cowrie JSON 日志，按 session 聚合，按 timestamp 排序，拆分复合命令，生成 process vector。
- HPA 建模：维护状态字典、count transition matrix C、probability transition matrix M，CSV 读写和动态更新。
- 策略控制：实现 payoff 计算、Dijkstra 最优路径搜索、pmin 剪枝、block threshold 判断。
- Shell Decoder：一套正则解析器和一套 LLM 调用解析器，用于识别反向 Shell payload 的语言、编码、IP、端口和命令结构。
- Shell Engine：bind shell 会话、reverse shell connect-back、命令输入输出重定向、LLM 响应封装。
- LLM Engine：OpenRouter/OpenAI-compatible chat completion endpoint、prompt 配置、模型 ID、会话历史 JSON cache。
- 评估脚本：payload recognition、latency、SALC/SANLC/FALC/FANLC 标注、指标计算、阈值敏感性、消融实验、CDF 绘图。

论文明确提到原型使用 Python 2.7 和 `asynchat`。如果将来复现，我会优先寻找或实现类似 `request_handler.py`、`shell_engine.py`、`decoder.py`、`hpa.py`、`countermeasure.py`、`llm_engine.py`、`metrics.py`、`preprocess_cowrie.py` 这类文件。

## 12. 本篇精华

- HoneyLLMd 的关键价值是把“高交互的观测能力”和“低交互的安全边界”用 LLM 连接起来：响应像真实系统，但背后没有真实 OS 执行。
- 论文真正区别于普通 LLM Shell 蜜罐的地方在 HPA：它不只生成回复，还用攻击路径概率决定何时放行、何时阻断、如何诱导偏离。
- reverse shell 支持是本文的重要工程贡献，因为现代攻击链中反连 C2 比 bind shell 更常见。
- LLM 解码混淆 payload 明显强于正则，但延迟是硬伤，实际系统应采用“正则快速路径 + LLM 复杂路径”的混合方案。
- B = 0.6 的阻断阈值体现了论文的核心折中：既不让攻击者太顺利，也不频繁失败导致交互中断。
- 真实部署结果显示，HPA 不只是理论模块，它确实延长了会话并增加了唯一命令采集量。
- 两个数据集相似度仅 0.15，说明攻击行为随时间漂移明显，蜜罐策略必须在线更新，静态规则很快过时。
- 对异常检测研究而言，HoneyLLMd 产出的不是普通日志，而是带攻击意图、命令链、受阻后重规划行为的高价值序列数据。

## 13. 建议精读路线

建议先读 Introduction 和 Problem Statement，抓住本文的核心矛盾：HIH 风险高，LIH/MIH 交互浅，LLM 蜜罐缺少策略控制。

第二步读 System Overview 与 Key Functional Components，画出 RH、SE、CE、LE 的数据流，特别关注 reverse shell 从 payload 捕获到 connect-back 模拟的流程。

第三步重点读 Honeypot Modeling。这里是论文最有科研含量的部分，需要弄清宏/微状态、转移矩阵、payoff、block threshold 和最优路径搜索之间的关系。

第四步读 Deception Evaluation Metrics，理解 SALC、SANLC、FALC、FANLC，因为后面所有“像不像真实系统”“能不能诱导攻击者”的结论都依赖这套标注。

最后读 Experiments，按“模型选择、解码能力、欺骗能力、数据集漂移、阈值敏感性、消融、CTFAgent 仿真”的顺序整理证据链。重点不是记住每个数值，而是理解 HPA 为什么能让 LLM 蜜罐从被动回复变成自适应欺骗系统。

<!-- codex-cli-deep-read: complete -->
