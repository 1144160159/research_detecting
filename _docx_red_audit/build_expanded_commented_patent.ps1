$ErrorActionPreference = 'Stop'

$source = 'F:\泉城实验室\二期\专利\流量大模型辅助的告警证据包生成与幻觉校验方法及系统\（2026.8.7标红问题批注稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx'
$output = 'F:\泉城实验室\二期\专利\流量大模型辅助的告警证据包生成与幻觉校验方法及系统\（2026.8.7全量问题补充批注稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx'

$comments = @(
    @{ Anchor='对于每个流对象'; Text=@'
[遗漏补充1/48：异常分数完整计算] 前一批注引入距离异常分数后，还需定义距离项。建议补充：轻量模型倒数第二层输出流表征[[MATH:h_f]]；第[[MATH:k]]个已知类别原型为训练样本表征均值[[MATH:μ_k=(1/N_k)\sum_(n:y_n=k)h_n]]；样本到最近原型的距离为[[MATH:d(f)=min_k sqrt((h_f-μ_k)^TΣ_k^(-1)(h_f-μ_k))]]。距离阈值[[MATH:τ_d]]取验证集中已知类距离的95%分位数，异常分数为[[MATH:s_a(f)=min(1,d(f)/τ_d)]]。若采用欧氏距离，应明确特征已标准化。
'@ },
    @{ Anchor='流量证据包括五元组'; Text=@'
[遗漏补充2/48：流量证据提取过程] 建议逐步补充：以[[MATH:FID]]检索同一流对象，以告警时间前后各[[MATH:Δt_f]]的窗口读取流摘要；实施例可取[[MATH:Δt_f=30s]]。对包长、方向和间隔生成统计摘要并保留前[[MATH:K=16]]项；缺失字段写入missing_mask，不用零值冒充真实观测；相同字段仅保留时间最近且原始索引可回溯的一份。
'@ },
    @{ Anchor='模型证据包括检测标签'; Text=@'
[遗漏补充3/48：模型证据提取过程] 建议补充：根据[[MATH:FID]]和模型运行编号检索检测记录，读取类别概率、异常分数、规则分数、不确定性、融合风险、阈值版本和特征贡献；多检测器结果按detector_id分别保存，不先合并为单一文本。若模型版本或阈值版本缺失，则模型证据标记为不完整，其来源可信度上限设为0.5。
'@ },
    @{ Anchor='资产证据包括资产类型'; Text=@'
[遗漏补充4/48：资产证据提取过程] 建议补充：以源/目的IP、端口和告警时间查询资产基线表，匹配资产类型、业务角色、常用端口、所属网段和服务暴露状态；资产记录有效期应覆盖告警时间。若同一地址对应多个资产版本，选择时间最近且有效的版本；无法匹配时生成“资产未知”证据，不得推断资产角色。
'@ },
    @{ Anchor='历史证据包括相似告警'; Text=@'
[遗漏补充5/48：历史证据提取过程] 建议补充：在告警时间之前的历史窗口[[MATH:W_h]]中检索相同源、相同目的、相同指纹或表征相似事件；实施例可取[[MATH:W_h=30d]]、相似度阈值[[MATH:θ_h=0.80]]、最多保留[[MATH:K_h=20]]条。相同事件按AID去重，并汇总正常、恶意和未确认结果，禁止使用当前告警之后的数据。
'@ },
    @{ Anchor='负证据包括可能削弱攻击判断的信息'; Text=@'
[遗漏补充6/48：负证据提取过程] 建议补充：负证据由当前攻击假设与业务基线、白名单、历史误报模式和字段一致性规则比对产生。每条负证据记录其反驳的claim_type、命中规则、冲突字段和来源索引；同一冲突事实按标准化字段值去重。白名单过期、来源不可回溯或与告警时间不重叠时，不作为有效负证据。
'@ },
    @{ Anchor='检测标签、时间窗口和特征贡献之间的匹配程度计算'; Text=@'
[遗漏补充7/48：相关度完整公式] 建议定义[[MATH:rel_i=a_1M_(field)+a_2M_(time)+a_3M_(label)+a_4M_(contrib)+a_5M_(sem)]]，其中字段匹配为告警关键字段一致率，时间匹配可取[[MATH:M_(time)=e^(-abs(t_i-t_a)/τ_r)]]，标签匹配为证据类型与检测标签规则的一致度，贡献匹配为证据字段是否进入[[MATH:C_f]]，语义匹配为余弦相似度。示例取[[MATH:(a_1,a_2,a_3,a_4,a_5)=(0.25,0.20,0.20,0.20,0.15)]]。
'@ },
    @{ Anchor='数据源稳定性'; Text=@'
[遗漏补充8/48：来源基础可靠度表] 建议设置可版本化的来源可靠度表。例如原始流摘要0.95、检测模型记录0.90、规则命中记录0.90、资产基线0.80、历史已确认事件0.85、未确认历史事件0.60、外部文本摘要0.50。该值记为[[MATH:r_(src,i)]]，只能由来源类型和运行质量确定，不由大模型自行给出。
'@ },
    @{ Anchor='采集完整性决定'; Text=@'
[遗漏补充9/48：采集完整度计算] 建议定义[[MATH:c_i=0.4r_(field)+0.3r_(packet)+0.3r_(trace)]]，其中[[MATH:r_(field)]]为必要字段完整率，[[MATH:r_(packet)]]为可用报文数与预期报文数之比的截断值，[[MATH:r_(trace)]]表示原始索引、采集点和时间戳是否可回溯。来源可信度取[[MATH:trust_i=r_(src,i)c_i]]。
'@ },
    @{ Anchor='新鲜度由证据时间与告警时间的距离决定'; Text=@'
[遗漏补充10/48：新鲜度参数] 建议按证据类型设置衰减常数：流量和模型证据[[MATH:τ=1h]]，资产证据[[MATH:τ=30d]]，历史事件证据[[MATH:τ=7d]]，规则与基线证据[[MATH:τ=14d]]。统一采用[[MATH:fresh_i=e^(-abs(t_i-t_a)/τ_(type_i))]]；证据产生时间晚于告警且不属于补证结果时，直接标记为时间越界。
'@ },
    @{ Anchor='稀有度表示该证据是否区别于常见背景行为'; Text=@'
[遗漏补充11/48：稀有度统计] 建议在仅包含告警前历史数据的基准窗口[[MATH:W_r]]内统计证据值频率，采用拉普拉斯平滑[[MATH:P_i=(count(value_i)+1)/(N+V)]]，再计算[[MATH:rare_i=min(1,-log(P_i)/κ)]]；实施例可取[[MATH:W_r=7d]]、[[MATH:κ=10]]。连续值先按训练集分位点离散化，避免每个浮点值都被误判为稀有。
'@ },
    @{ Anchor='负证据强度用于保证反证信息进入提示'; Text=@'
[遗漏补充12/48：负证据强度公式] 建议定义[[MATH:neg_i=b_1M_(field-conflict)+b_2P_(contradiction)+b_3M_(baseline)+b_4trust_i]]，其中字段冲突、基线冲突为0或1，自然语言矛盾概率由固定版本的蕴含模型输出。示例取[[MATH:(b_1,b_2,b_3,b_4)=(0.30,0.30,0.25,0.15)]]，并执行[[MATH:neg_i=clip(neg_i,0,1)]]。
'@ },
    @{ Anchor='来源类型编码'; Text=@'
[遗漏补充13/48：来源类型编码表] 建议将来源划分为流量、检测模型、规则、资产、历史事件、业务基线和外部摘要七类，采用7维独热编码；未知来源使用全零向量并设置unknown_source标志。若使用嵌入编码，应固定编码表版本和维数，不得由大模型临时生成来源向量。
'@ },
    @{ Anchor='系统首先为每条证据计算综合得分'; Text=@'
[遗漏补充14/48：证据得分范围] 原公式可能产生负值或超过1。建议先计算[[MATH:S_i=αrel_i+βtrust_i+γfresh_i+δrare_i+μneg_i-νred_i]]，再转换为非负排序权重[[MATH:q_i=(max(0,S_i)+ε)/(\sum_j(max(0,S_j)+ε))]]。[[MATH:Score(e_i)]]用于排序，[[MATH:q_i]]用于后续加权，避免直接把未归一化得分当作概率或证据权重。
'@ },
    @{ Anchor='系统可采用余弦相似度计算证据与告警描述之间的相关性'; Text=@'
[遗漏补充15/48：语义编码模型] 建议说明告警查询向量和证据摘要向量由同一固定版本的文本编码模型生成，记录encoder_id、维数和版本哈希。编码模型仅计算相似度，不生成事实；模型更新后应重新建立证据向量索引，禁止混用不同版本向量。
'@ },
    @{ Anchor='证据覆盖率用于衡量当前证据包'; Text=@'
[遗漏补充16/48：必要证据类型实施例] 建议增加配置表：检测证据、流量证据、来源索引为必需类型，示例权重分别为0.30、0.30、0.15，最低数量均为1；环境证据和负证据权重分别为0.15、0.10，最低数量分别为1和0。不同告警类型可调整[[MATH:w_t]]和[[MATH:m_t]]，但配置必须与证据包版本绑定。
'@ },
    @{ Anchor='路径集合包括轻量模板路径'; Text=@'
[遗漏补充17/48：五条路径输入输出] 建议为每条路径增加输入、触发和输出表：轻量模板路径输入基础告警并输出固定字段；完整生成路径输入充分证据包并输出结构化初稿；补证路径输入缺失类型列表并输出新证据包版本；高强度校验路径输入敏感命题并输出逐命题校验结果；降级输出路径输入失败命题并输出事实、证据编号和缺口。每条路径还应给出超时和失败转移。
'@ },
    @{ Anchor='检测解释收益'; Text=@'
[遗漏补充18/48：路径收益公式] 建议定义[[MATH:G(a,p)=0.35ΔCov(a,p)+0.35PassRate_(hist)(p,type_a)+0.20R_f+0.10U_f]]，其中[[MATH:ΔCov]]为执行路径后的预计覆盖率增量，历史通过率按告警类型和路径统计。各分量均截断至0至1，避免收益项量纲不一致。
'@ },
    @{ Anchor='生成与校验成本'; Text=@'
[遗漏补充19/48：路径成本公式] 建议定义[[MATH:C(a,p)=0.4min(1,token_p/B_(token))+0.3min(1,lat_p/B_(lat))+0.3min(1,calls_p/B_(call))]]，其中三个预算分别为允许Token数、时延和模型调用次数。成本估计来自最近运行窗口的指数移动平均，不使用大模型自报成本。
'@ },
    @{ Anchor='路径选择可表示为：'; Text=@'
[遗漏补充20/48：路径幻觉风险公式] 建议定义[[MATH:H(a,p)=0.30U_f+0.25(1-Cov(a))+0.20P_(neg)+0.15I_(IOC)+0.10I_(attr)]]，其中IOC敏感和归因敏感指示量由命题类型及证据包字段确定。高强度校验路径可对该风险乘以小于1的历史风险折扣，但不能把风险直接置零。
'@ },
    @{ Anchor='证据缺口惩罚'; Text=@'
[遗漏补充21/48：证据缺口惩罚公式] 建议定义[[MATH:D(a,p)=(\sum_(t∈T)w_t I(n_t^(after)(a,p)<m_t))/(\sum_(t∈T)w_t)]]，其中[[MATH:n_t^(after)]]为执行路径后预计获得的第[[MATH:t]]类证据数量。补证路径根据历史检索成功率估计该数量，其他路径不应假定缺失证据自动出现。
'@ },
    @{ Anchor='生成完成后，系统把模型输出拆解为关键结论命题'; Text=@'
[遗漏补充22/48：命题解析失败处理] 建议补充：优先要求模型按JSON模式直接输出命题数组；系统执行JSON Schema校验、字段类型校验和证据编号格式校验。解析失败时仅允许一次受约束修复，仍失败则进入降级输出，不再从任意长文本中反复猜测。缺少risk_status或evidence_ids的命题标记为结构不完整。
'@ },
    @{ Anchor='包括检测证据集合、流量证据集合、环境证据集合吗？'; Text=@'
[遗漏补充23/48：不同命题的引用范围] 建议区分命题类型：攻击行为命题的正引用来自检测、流量和环境证据，负证据进入[[MATH:Neg(c_j)]]；边界命题可以把负证据作为正向引用，用于支持“证据不足”结论；风险命题还必须引用检测风险和支持度。不得对所有命题统一把全部[[MATH:E_(neg)]]放入[[MATH:Ref(c_j)]]。
'@ },
    @{ Anchor='表示支持匹配程度'; Text=@'
[遗漏补充24/48：支持匹配度公式] 建议定义[[MATH:match(c_j,e_i)=0.35M_(field)+0.25M_(type)+0.20sim(c_j,e_i)+0.20P_(entail)(c_j,e_i)]]。字段和类型匹配由确定性规则计算，语义相似度和蕴含概率使用固定模型；缺少可比文本时，重新归一化规则分量，不得用默认高分填充。
'@ },
    @{ Anchor='表示冲突程度'; Text=@'
[遗漏补充25/48：冲突度公式] 建议定义[[MATH:conflict(c_j,e_k)=0.40M_(rule-conflict)+0.35P_(contradiction)(c_j,e_k)+0.25neg_k]]，其中规则冲突检查风险状态、IOC归属、资产角色和时间关系。冲突度截断至0至1，并保存触发规则编号，便于校验结果回溯。
'@ },
    @{ Anchor='表示冲突程度'; Text=@'
[遗漏补充26/48：正负证据权重] 建议分别定义[[MATH:ω_i=q_i·trust_i]]和[[MATH:ω_k=q_k·trust_k·(1+ξneg_k)]]，实施例可取[[MATH:ξ=0.5]]，然后分别在正证据集合和负证据集合内归一化。[[MATH:ω_i]]表示支持证据权重，[[MATH:ω_k]]表示冲突负证据权重，不能共用未说明的同一符号。
'@ },
    @{ Anchor='幻觉校验失败惩罚'; Text=@'
[遗漏补充27/48：幻觉失败惩罚] 建议定义[[MATH:F_(hall)=(\sum_(l=1)^L h_l I_l)/(\sum_(l=1)^L h_l)]]，其中[[MATH:I_l=1]]表示第[[MATH:l]]项校验失败。示例权重为结构0.10、引用0.15、支持度0.15、未见IOC 0.20、归因0.15、一致性0.10、风险越界0.15。未见IOC、无证据归因和风险越界同时属于硬失败，不能仅靠加权平均放行。
'@ },
    @{ Anchor='其中数据集1至6分别为哪种数据集？'; Text=@'
[遗漏补充28/48：图3六组数据的逐项映射] 若确有对应实验，建议在图注中逐项写明：数据集1为USTC-TFC2016，数据集2为CIC-IDS2017，数据集3为CSE-CIC-IDS2018，数据集4为CIC-DDoS2019，数据集5为CIC-Darknet2020，数据集6为TON_IoT；证据数量1至6对应[[MATH:4,8,12,16,24,32]]条/告警；数据规模1至6对应[[MATH:1,5,10,20,50,100]]万条流对象或告警。上述仅为候选实验设计，必须与实际日志核对；未实测的数据集不得保留在效果图中。
'@ },
    @{ Anchor='并以五元组、协议类型和时间窗口为基本键构造会话'; Text=@'
[遗漏补充29/48：会话键重复] 五元组通常已包含协议号，因此“以五元组、协议类型”为键存在重复。建议改为“以源地址、目的地址、源端口、目的端口和协议号组成的规范化五元组，并结合时间窗口构造会话”，或者使用“四元组+协议号”的写法，二者择一并全文统一。
'@ },
    @{ Anchor='对于UDP或QUIC通信'; Text=@'
[遗漏补充30/48：会话超时与时间窗口关系] 建议增加实施例：TCP空闲超时可取300秒，UDP和QUIC空闲超时可取30秒；固定统计窗口可取60秒、步长30秒。会话超时用于判断通信是否结束，统计窗口用于切分长会话，两者功能不同。子流对象应记录父会话标识和窗口编号。
'@ },
    @{ Anchor='对于数值特征'; Text=@'
[遗漏补充31/48：归一化统计量来源] 建议明确最小值和最大值仅由训练集或告警发生前的历史基准窗口估计，推理阶段保持固定；不得使用包含当前测试样本的全量数据重新计算，以避免数据泄漏。每个模型版本同时保存各维最小值、最大值、缺失值策略和更新时间。
'@ },
    @{ Anchor='历史轻量上下文'; Text=@'
[遗漏补充32/48：上下文向量字段] 建议明确[[MATH:X_(ctx)]]至少包括采集点编号、小时/星期周期编码、所属网段、同源近窗连接数、同目的近窗连接数、最近一次同类告警时间差和历史轻量风险均值。所有历史字段只使用当前告警时间之前的数据，并设置有效窗口和缺失掩码。
'@ },
    @{ Anchor='模型不确定性可采用熵形式表示'; Text=@'
[遗漏补充33/48：正文熵公式需归一化] 原正文公式未除以[[MATH:log C]]，其上界随类别数量变化，无法直接使用0.45等固定阈值。建议将正文公式替换为[[MATH:U_f=-(\sum_(k=1)^C p_k log(p_k+ε))/(log C)]]，从而保证[[MATH:0≤U_f≤1]]。
'@ },
    @{ Anchor='融合风险可表示为：'; Text=@'
[遗漏补充34/48：低置信量重复计权] [[MATH:1-max_k p_k]]与熵[[MATH:U_f]]均反映低置信，直接同时加入可能重复放大同一信息。建议通过消融实验或相关性约束确定是否同时保留；若两者相关系数超过0.8，可删除其中一项，或约束其权重和[[MATH:w_3+w_4≤1]]。
'@ },
    @{ Anchor='则输出恶意标签'; Text=@'
[遗漏补充35/48：标签判定优先级] 建议明确优先顺序：当[[MATH:U_f≥θ_u]]或原型距离超过未知阈值时，先输出可疑/未知，不因[[MATH:R_f]]较高直接归入已知恶意类；仅当不确定性低于阈值且[[MATH:R_f≥θ_m]]时输出已知恶意。由此避免同一样本同时满足恶意与未知条件。
'@ },
    @{ Anchor='生成统一风险值'; Text=@'
[遗漏补充36/48：标准化风险与检测风险关系] 建议规定：本发明自身检测模块输出时[[MATH:r_a=R_f]]；外部检测器输出时先经过校准得到[[MATH:r_a]]。证据包、路径调度和可信度计算统一读取标准化告警中的[[MATH:r_a]]，若继续使用[[MATH:R_f]]，应注明它是[[MATH:r_a]]的内部来源而非并列风险变量。
'@ },
    @{ Anchor='系统首先为每条证据计算综合得分'; Text=@'
[遗漏补充37/48：证据得分量纲和负值] 相关度、可信度、新鲜度、稀有度、负证据强度和冗余度必须先统一至0至1。排序可以使用原始线性得分，但进入支持度、负证据压力和路径目标前必须采用非负归一化权重[[MATH:q_i]]；否则负分证据会产生方向相反的权重。
'@ },
    @{ Anchor='如图2所示，本发明还提供一种'; Text=@'
[遗漏补充38/48：图2失败路径关系] 图2当前把“补证—降级—重写”画成连续串行步骤，容易理解为每次失败都依次执行。建议改为条件分支：缺少可检索证据时进入补证；支持度不足或预算不足时进入降级；结构、引用或未见IOC失败且仍具备生成条件时进入重写；重写后返回幻觉校验，超过次数上限则降级。
'@ },
    @{ Anchor='路径选择可表示为：'; Text=@'
[遗漏补充39/48：路径目标统一量纲] [[MATH:G,C,H,D]]相减前均应归一化至0至1，并记录各估计量的统计窗口。建议目标函数增加可行性指示[[MATH:I_(feasible)(a,p)]]，仅对可行路径计算；不可行路径的效用直接设为负无穷，避免高收益抵消硬约束。
'@ },
    @{ Anchor='可信度可表示为：'; Text=@'
[遗漏补充40/48：风险严重度不等于解释可信度] 现公式把[[MATH:R_f]]作为正向可信度项，会导致风险越高、解释越可信，科学含义不成立。建议将其替换为检测校准置信度[[MATH:Conf_(det)=1-U_f]]或多检测器一致性[[MATH:Agree_(det)]]；风险分数仅用于路径优先级和风险越界比较，不直接提高解释可信度。
'@ },
    @{ Anchor='可信度融合与输出控制模块用于将检测风险'; Text=@'
[遗漏补充41/48：证据充分性重复计权] [[MATH:Cov(a)]]、平均[[MATH:Support]]和[[MATH:Q_(ref)]]均与证据充分程度相关。建议在验证集上计算相关矩阵和方差膨胀因子；高度相关时合并为证据质量子分数[[MATH:Q_(evid)]]，或对权重增加和为1及非负约束，并通过消融实验报告各项增益。
'@ },
    @{ Anchor='该模块是本发明保证可信输出的关键环节'; Text=@'
[遗漏补充42/48：强校验先于连续惩罚] 建议明确两级机制：第一层对结构缺失、无效证据编号、未见IOC、无证据归因和风险越界执行硬阻断；第二层仅对可降级问题计算[[MATH:F_(hall)]]。任何硬失败均不得被高覆盖率、高风险或低成本抵消。
'@ },
    @{ Anchor='系统根据运行结果更新检测阈值'; Text=@'
[遗漏补充43/48：反馈自强化风险] 不能直接用大模型生成结果更新检测阈值和特征权重。建议只接收具有后续确认标签、跨检测器一致且通过全部强校验的样本；参数更新在影子版本中执行，通过固定验证集门限后再发布，并保留旧版本及回滚条件，防止错误解释反向强化检测器。
'@ },
    @{ Anchor='在需要自适应调度时'; Text=@'
[遗漏补充44/48：强化学习实施细节] 建议展开奖励[[MATH:r_t=c_1Y_(trusted)+c_2Gain_(evid)-c_3F_(hall)-c_4Lat-c_5Cost]]，示例取[[MATH:(c_1,c_2,c_3,c_4,c_5)=(1.0,0.4,1.2,0.2,0.2)]]；学习率[[MATH:α=0.1]]、折扣因子[[MATH:γ=0.9]]、初始探索率[[MATH:ε_g=0.1]]。状态连续量按固定分箱离散化；先利用历史日志离线训练，线上仅在硬约束后的动作集合中小幅探索，并设置性能下降回滚门限。
'@ },
    @{ Anchor='实施例一，面向加密恶意流量的检测与解释'; Text=@'
[遗漏补充45/48：实施例验证条件] 三个实施例均应补充同一套可复现字段：硬件型号、模型版本、流对象数量、类别构成、训练/验证/测试划分、证据数量、上下文长度、风险与校验阈值、基线方法、重复次数、均值和标准差。没有原始日志时只能写“示例性参数”，不能写成已经获得的效果结论。
'@ },
    @{ Anchor='如图3所示，本发明具体有益效果为'; Text=@'
[遗漏补充46/48：图3数值化要求] 图3目前只有“高/低”方向和示意曲线，缺少可核验数据。建议每个子图增加数值纵轴、单位、数据点、均值、误差线和样本规模；图下附原始数据表。恶意流量识别、证据引用覆盖、无证据结论比例和平均时延分别使用百分比、百分比、百分比和毫秒，不能共用无量纲高低刻度。
'@ },
    @{ Anchor='如图1所示，本发明的整体系统包括'; Text=@'
[遗漏补充47/48：图1输入范围] 图1把主机日志、安全设备日志、应用日志和威胁情报与网络流量并列为检测输入，但正文底层检测主要处理网络流量。建议将网络流量明确为恶意流量检测输入，其余日志移至环境证据/补证输入；如仍作为检测输入，必须在会话构造和特征抽取部分增加对应处理方法。
'@ },
    @{ Anchor='如图2所示，本发明还提供一种'; Text=@'
[遗漏补充48/48：模块步骤对应关系] 建议增加对应表：系统模块、图2步骤、输入、输出和权利要求单元一一关联。例如S1对应流量接入与会话构造，S2对应多粒度特征抽取，S3对应恶意流量检测，S4对应告警标准化，S5至S10依次对应证据抽取、构包、提示、生成、命题化和幻觉校验。反馈更新和可信输出也应分配明确步骤编号。
'@ }
)

function Copy-FileShared {
    param([string]$From, [string]$To)
    $inputStream = [System.IO.File]::Open($From,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::ReadWrite)
    try {
        $outputStream = [System.IO.File]::Open($To,[System.IO.FileMode]::Create,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $inputStream.CopyTo($outputStream) } finally { $outputStream.Dispose() }
    }
    finally { $inputStream.Dispose() }
}

function Find-DocumentRange {
    param($Document,[string]$Text)
    $range = $Document.Content.Duplicate
    $find = $range.Find
    $find.ClearFormatting()
    $find.Text = $Text
    $find.Forward = $true
    $find.Wrap = 0
    $find.Format = $false
    $found = $find.Execute()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($find)
    if (-not $found) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($range)
        return $null
    }
    return $range
}

function Convert-MathPlaceholders {
    param($Document,$Comment)
    $commentText = $Comment.Range.Text
    $matches = [regex]::Matches($commentText,'\[\[MATH:(.*?)\]\]')
    for ($i = $matches.Count - 1; $i -ge 0; $i--) {
        $match = $matches[$i]
        $mathText = $match.Groups[1].Value
        $mathRange = $Comment.Range.Duplicate
        $start = $Comment.Range.Start + $match.Index
        $end = $start + $match.Length
        $mathRange.SetRange($start,$end)
        $mathRange.Text = $mathText
        $mathRange.Font.Name = 'Cambria Math'
        $mathRange.Font.NameAscii = 'Cambria Math'
        $mathRange.Font.NameOther = 'Cambria Math'
        [void]$Document.OMaths.Add($mathRange)
        $omath = $mathRange.OMaths.Item(1)
        try { $omath.BuildUp() } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($omath)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($mathRange)
    }
}

if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
Copy-FileShared -From $source -To $output

$word = $null
$document = $null
$oldUserName = $null
$oldInitials = $null
$missing = New-Object System.Collections.Generic.List[string]
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $oldUserName = $word.UserName
    $oldInitials = $word.UserInitials
    $word.UserName = '王文同'
    $word.UserInitials = 'WWT'
    $document = $word.Documents.Open($output,$false,$false)
    foreach ($spec in $comments) {
        $anchorRange = Find-DocumentRange -Document $document -Text $spec.Anchor
        if ($null -eq $anchorRange) {
            $missing.Add($spec.Anchor)
            continue
        }
        $comment = $document.Comments.Add($anchorRange,$spec.Text.Trim())
        Convert-MathPlaceholders -Document $document -Comment $comment
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($comment)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($anchorRange)
    }
    if ($missing.Count -gt 0) {
        throw ('未匹配批注锚点：' + ($missing -join ' | '))
    }
    $document.Save()
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($null -ne $word) {
        if ($null -ne $oldUserName) { $word.UserName = $oldUserName }
        if ($null -ne $oldInitials) { $word.UserInitials = $oldInitials }
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Write-Output ('OUTPUT=' + $output)
Write-Output ('COMMENTS_ADDED=' + $comments.Count)


