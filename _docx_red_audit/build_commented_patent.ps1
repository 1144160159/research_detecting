$ErrorActionPreference = 'Stop'

$source = 'F:\泉城实验室\二期\专利\流量大模型辅助的告警证据包生成与幻觉校验方法及系统\（2026.8.4初修稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx'
$output = 'F:\泉城实验室\二期\专利\流量大模型辅助的告警证据包生成与幻觉校验方法及系统\（2026.8.7标红问题批注稿）流量大模型辅助的告警证据包生成与幻觉校验方法及系统.docx'

$comments = @(
    @{ Anchor='请解释一下，TCP连接、UDP或QUIC通信、短连接或高频连接分别指？'; Text=@'
[标红问题1/35：通信对象术语定义] 建议在本段后补充：TCP连接是指同一五元组下自握手开始至FIN/RST或空闲超时结束的双向报文集合；UDP通信是指同一规范化五元组下、相邻报文间隔不超过设定超时的双向数据报集合；QUIC通信优先利用可见连接标识CID聚合，CID不可见时采用五元组与空闲超时构造近似会话；短连接可示例定义为持续时间不超过10秒或报文数不超过20；高频连接可示例定义为同一源目的关系在60秒内建立不少于20个会话。上述时长和数量均为可配置实施例，不构成固定限制。
'@ },
    @{ Anchor='流对象指？与上述得到的会话有何关系吗？'; Text=@'
[标红问题2/35：流对象与会话关系] 建议明确：会话构造结果形成基础流对象，普通会话与流对象一一对应；持续时间超过处理窗口的长连接被拆分为多个子流对象，各子流对象共享父会话标识。流索引可表示为[[MATH:FID=Hash(K_(5tuple),proto,wid,sid)]]，其中[[MATH:K_(5tuple)]]为方向规范化五元组，[[MATH:proto]]为协议类型，[[MATH:wid]]为窗口编号，[[MATH:sid]]为采集点编号。该索引用于关联检测、证据包、解释和校验记录。
'@ },
    @{ Anchor='与上述术语解释中的“协议特征”是一个概念吗？'; Text=@'
[标红问题3/35：协议特征术语统一] 建议全文统一使用“协议可见侧信道特征”。其是指不解密应用载荷即可从协议首部、握手过程和关联元数据中获得的属性，包括TLS或QUIC版本、加密套件数量、扩展字段摘要、SNI、ALPN、证书摘要、JA3或JA4指纹及DNS关联信息。术语解释中的“协议特征”同步改为该名称，避免形成两个概念。
'@ },
    @{ Anchor='为使不同尺度特征进入统一模型'; Text=@'
[标红问题4/35：数值特征范围] 建议补充：[[MATH:x_j]]表示包级、流级或协议可见侧信道特征中可直接数值化的第[[MATH:j]]个标量特征；类别字段经字典编码、哈希编码或嵌入编码后进入检测向量，不直接套用数值归一化公式。归一化所用最大值和最小值应由训练集或历史基准窗口确定，并在模型版本中记录。
'@ },
    @{ Anchor='为防止分母为零的极小常数'; Text=@'
[标红问题5/35：极小常数取值] 建议补充：[[MATH:ε]]可取[[MATH:10^(-8)]]，并可根据数值精度在[[MATH:10^(-12)≤ε≤10^(-6)]]范围内配置。若某特征在训练窗口中的最大值与最小值相等，则该维归一化结果直接置为0，并记录常量特征标记，避免仅依赖极小常数掩盖无变化特征。
'@ },
    @{ Anchor='均为归一化后的对应特征吗？'; Text=@'
[标红问题6/35：检测向量组成] 建议补充：[[MATH:X_(pkt)]]为前[[MATH:K]]个包长、方向和到达间隔序列经截断、补齐、掩码及归一化后形成的向量；[[MATH:X_(flow)]]为持续时间、报文数、字节数、上下行比例等流级统计量归一化后的向量；[[MATH:X_(proto)]]为协议数值字段归一化后与类别字段编码拼接所得向量；[[MATH:X_(ctx)]]为采集点、时间窗口和历史轻量上下文编码。四者均为处理后的模型输入表示，而非原始字段集合。
'@ },
    @{ Anchor='分别如何得到或计算得到？'; Text=@'
[标红问题7/35：四类检测输出的计算] 建议补充：已知类别概率由轻量分类模型的Softmax层得到，[[MATH:p_k=(e^(z_k))/(\sum_(l=1)^C e^(z_l))]]；异常分数可由流表征到最近已知类原型的距离归一化得到，[[MATH:s_a(f)=min(1,d(f)/τ_d)]]；规则命中分数为[[MATH:s_r(f)=(\sum_m q_m I_m)/(\sum_m q_m+ε)]]，其中[[MATH:I_m]]为第[[MATH:m]]条规则的命中指示量；不确定性采用归一化熵[[MATH:U_f=-(\sum_(k=1)^C p_k log(p_k+ε))/(log C)]]。上述四个量均满足[[MATH:0≤p_k,s_a,s_r,U_f≤1]]。
'@ },
    @{ Anchor='权重如何得到，或者可取值多少？'; Text=@'
[标红问题8/35：风险融合参数和阈值] 建议说明：[[MATH:w_1]]至[[MATH:w_4]]及偏置[[MATH:b]]可在验证集上通过带正则约束的逻辑回归或网格搜索确定。实施例可取[[MATH:(w_1,w_2,w_3,w_4)=(1.0,0.8,0.6,0.7)]]、[[MATH:b=-1.2]]。示例判定为：[[MATH:R_f≥0.70]]输出恶意；[[MATH:0.35≤R_f<0.70]]或[[MATH:U_f≥0.45]]输出可疑或未知；[[MATH:R_f<0.35]]且[[MATH:U_f<0.45]]输出正常。阈值应通过验证集ROC、F1或误报率约束校准并记录版本。
'@ },
    @{ Anchor='检测模块输出的不仅是标签和分数'; Text=@'
[标红问题9/35：检测模块及模型输出指代] 建议明确：本段“检测模块”是前述由规则初筛、轻量分类、异常检测和风险校准组成的恶意流量检测模块；“模型输出”专指其中轻量分类模型与异常检测分支的输出。特征贡献、规则命中、模型版本和检测上下文可以采用现有解释与记录方法获得，但将这些信息与流索引、风险和不确定性共同组织成可追溯检测证据，是本方案后续构包与校验的输入环节。
'@ },
    @{ Anchor='特征贡献集合如何得到'; Text=@'
[标红问题10/35：特征贡献集合] 建议补充：对树模型采用TreeSHAP，对线性模型采用“特征值乘模型系数”，对浅层神经网络采用梯度乘输入，得到各特征对当前检测结果的贡献。按贡献绝对值选取前[[MATH:M]]项，构成[[MATH:C_f={(id_j,value_j,contrib_j,direction_j)}_(j=1)^M]]。文中“贡献较高的特征项”即[[MATH:C_f]]中按[[MATH:abs(contrib_j)]]排序靠前的元素。
'@ },
    @{ Anchor='该过程是否为现有技术？'; Text=@'
[标红问题11/35：外部告警风险映射] 建议说明：线性映射、Platt缩放和等距回归属于可选的风险校准手段，本发明利用校准结果形成统一告警对象。仅有等级时，可将正常、低、中、高、严重示例映射为[[MATH:0.10,0.30,0.50,0.75,0.95]]；映射值可由各等级在历史验证样本中的实际恶意比例或等级区间中点得到，并按时间窗口更新。转换后统一风险满足[[MATH:0≤r_a≤1]]。
'@ },
    @{ Anchor='这些证据存在于哪里'; Text=@'
[标红问题12/35：证据来源和统一对象] 建议补充：流量证据来自流记录库与摘要存储；模型证据来自恶意流量检测结果记录；资产证据来自资产与业务基线表；历史证据来自历史告警库和相似流索引；负证据来自正常业务基线、历史误报记录及与当前攻击假设冲突的字段。系统通过流索引[[MATH:FID]]、告警索引[[MATH:AID]]和时间窗口联合检索，并统一转换为包含证据编号、类型、内容、来源、采集时间、有效期、质量、告警索引和原始数据索引的证据对象。
'@ },
    @{ Anchor='证据向量可表示为：'; Text=@'
[标红问题13/35：证据向量各维计算] 建议补充：相关度[[MATH:rel_i]]由字段匹配、时间重叠、检测标签匹配和语义相似度加权得到；来源可信度[[MATH:trust_i=r_(src,i)·c_i]]，其中[[MATH:r_(src,i)]]为来源基础可靠度，[[MATH:c_i]]为采集完整度；新鲜度[[MATH:fresh_i=e^(-abs(t_i-t_a)/τ)]]；稀有度可取[[MATH:rare_i=min(1,-log(P(value_i)+ε)/κ)]]；负证据强度[[MATH:neg_i]]为证据与当前攻击假设的冲突程度；来源类型编码[[MATH:src_i]]采用独热编码或嵌入编码。除来源编码外各标量均满足[[MATH:0≤rel_i,trust_i,fresh_i,rare_i,neg_i≤1]]。
'@ },
    @{ Anchor='相关度可由证据与告警字段'; Text=@'
[标红问题14/35：证据排序参数] 建议定义冗余度为[[MATH:red_i=max_(e_j∈S) cos(v_i,v_j)]]，其中[[MATH:S]]为当前已选证据集合。权重可示例取[[MATH:(α,β,γ,δ,μ,ν)=(0.30,0.20,0.15,0.10,0.15,0.10)]]，并通过验证集上的引用覆盖率、无证据结论率和上下文长度联合调优。相关度、可信度、新鲜度、稀有度及负证据强度按证据向量定义计算，避免仅作定性描述。
'@ },
    @{ Anchor='对于文本或摘要证据'; Text=@'
[标红问题15/35：余弦相似度的用途] 建议明确：余弦相似度是相关度[[MATH:rel_i]]中的语义匹配分量，而不是新增独立参数。实施例可取[[MATH:rel_i=0.35M_(field)+0.20M_(time)+0.20M_(label)+0.25sim(q,e_i)]]。对没有文本摘要的纯数值证据，将语义相似度分量置零并对其余权重重新归一化。
'@ },
    @{ Anchor='若证据覆盖率过低'; Text=@'
[标红问题16/35：覆盖率阈值] 建议设置覆盖率阈值[[MATH:θ_(cov)=0.60]]作为实施例：[[MATH:Cov(a)<0.60]]为低覆盖率，[[MATH:0.60≤Cov(a)<0.80]]为中等覆盖率，[[MATH:Cov(a)≥0.80]]为充分覆盖。必要证据类型集合、最低数量[[MATH:m_t]]和权重[[MATH:w_t]]按告警类型配置并记录策略版本。
'@ },
    @{ Anchor='路径调度模块用于根据检测风险'; Text=@'
[标红问题17/35：路径输入与执行过程] 建议将“不确定性”统一为[[MATH:U_f]]，并定义负证据压力[[MATH:P_(neg)=(\sum_i q_i neg_i)/(\sum_i q_i+ε)]]。轻量模板路径仅填充固定字段；完整生成路径使用完整证据包并执行全部校验；补证路径检索缺失证据后重算覆盖率；高强度校验路径增加IOC、归因、语义支持和风险越界校验；降级输出路径删除未通过命题，仅输出已有事实、证据编号和缺口。
'@ },
    @{ Anchor='路径选择可表示为：'; Text=@'
[标红问题18/35：路径目标函数] 建议定义：[[MATH:G(a,p)]]为预期覆盖率增量、历史校验通过率和高风险解释收益的加权值；[[MATH:C(a,p)]]为Token量、推理时延和模型调用次数的归一化成本；[[MATH:H(a,p)]]由[[MATH:U_f]]、[[MATH:1-Cov(a)]]、负证据压力及IOC/归因敏感标志估计；[[MATH:D(a,p)=1-Cov(a)]]或必要类型缺失权重和。示例取[[MATH:(λ,ρ,η)=(0.25,0.45,0.30)]]。[[MATH:P]]为候选路径集合，[[MATH:p^*]]为目标函数值最大的最终选择路径。
'@ },
    @{ Anchor='低风险、低覆盖率或字段不完整的告警进入轻量模板路径'; Text=@'
[标红问题19/35：统一选路逻辑] 建议改为“硬约束筛选+目标函数排序”：先依据字段完整性、IOC/归因敏感性、预算和强制校验要求，从[[MATH:P]]中得到可行路径集合[[MATH:P_(feasible)]]；再计算[[MATH:p^*=argmax_(p∈P_(feasible)){G-λC-ρH-ηD}]]。本段文字条件作为可行性约束，不再与公式并列形成第二套独立决策逻辑。
'@ },
    @{ Anchor='风险等级如何得到？；待校验字段是指？，如何得到？'; Text=@'
[标红问题20/35：命题风险和待校验字段] 建议要求大模型按结构化模式输出claim_text、claim_type、risk_status、evidence_ids、entities和ioc_list。风险状态限定为正常、可疑、高风险、已确认，并可映射为[[MATH:0.10,0.40,0.70,0.90]]。待校验字段根据命题类型和实体抽取结果生成，至少包括证据编号、IOC、归因实体、风险状态和处置动作。
'@ },
    @{ Anchor='结构校验用于检查模型输出'; Text=@'
[标红问题21/35：结构化输出缺项] 建议在大模型输出中增加key_conclusions数组，每项包含claim_id、claim_text、claim_type、risk_status、evidence_ids和insufficient_evidence。证据编号由证据包构建阶段分配，大模型只能引用当前证据包中已有编号；关键结论直接来自key_conclusions，不在校验阶段从自由文本中猜测产生。
'@ },
    @{ Anchor='包括检测证据集合、流量证据集合、环境证据集合吗？'; Text=@'
[标红问题22/35：命题支持度计算] 建议明确：[[MATH:Ref(c_j)]]为命题显式引用且存在于[[MATH:E_(det)∪E_(flow)∪E_(env)∪E_(neg)]]中的证据；[[MATH:Neg(c_j)]]是与命题相关的负证据子集，不等同于全部[[MATH:E_(neg)]]。匹配度由字段规则、余弦相似度和自然语言蕴含概率融合，冲突度由字段矛盾规则和自然语言矛盾概率融合。令[[MATH:ω_i=Score(e_i)/(\sum_h Score(e_h)+ε)]]，并采用[[MATH:Support(c_j)=clip(S_(pos)-κS_(neg),0,1)]]，正负部分分别归一化，避免证据数量改变分值尺度。
'@ },
    @{ Anchor='则该命题不得作为确定结论输出'; Text=@'
[标红问题23/35：支持度阈值] 建议定义[[MATH:θ_s]]为命题成为确定结论所需的最低支持度，实施例可取[[MATH:θ_s=0.65]]。该阈值通过验证集在控制无证据结论率的前提下最大化有效结论保留率；[[MATH:Support(c_j)<θ_s]]时，将命题改写为“证据不足”或删除。
'@ },
    @{ Anchor='未见IOC校验用于检查模型'; Text=@'
[标红问题24/35：IOC集合来源] 建议明确：候选IOC从大模型生成的结构化解释初稿中抽取，具体扫描summary、key_conclusions、ioc_list和attribution字段。证据包增加visible_ioc字段，汇总检测证据、流量证据、环境证据和历史证据中可见且可追溯的IP、域名、URL、哈希、证书指纹及账号标识，形成[[MATH:IOC_(ep)]]。
'@ },
    @{ Anchor='并进入删除、降级或重写流程'; Text=@'
[标红问题25/35：未见IOC集合定义] 建议补充：[[MATH:IOC_(new)=IOC_(out)\setminus IOC_(ep)]]表示生成文本中出现但当前证据包不存在的IOC集合。若[[MATH:IOC_(new)≠∅]]，则涉及该IOC的命题判定为强校验失败，删除相关IOC后重写，或直接降级输出。
'@ },
    @{ Anchor='归因校验用于检查模型是否在证据不足时归因'; Text=@'
[标红问题26/35：归因校验时点] 建议改写为：大模型初稿生成并完成命题化后，系统从命题的entities或attribution字段识别攻击组织、攻击家族和工具名称，再执行归因证据核验。这里执行的是“归因实体抽取与校验”，并非执行攻击组织、攻击家族或工具。
'@ },
    @{ Anchor='风险越界校验用于判断模型生成的风险等级'; Text=@'
[标红问题27/35：风险术语统一] 建议全文将大模型输出侧的“风险等级”统一为“生成风险状态”。检测侧使用连续风险分数[[MATH:R_f]]，生成侧使用限定枚举状态并映射为数值[[MATH:R_(gen)]]，二者概念不同但可在风险越界公式中比较。
'@ },
    @{ Anchor='允许解释偏差'; Text=@'
[标红问题28/35：生成风险值和允许偏差] 建议补充：[[MATH:R_(gen)]]由结构化输出的risk_status字段映射得到，正常、可疑、高风险、已确认可示例映射为[[MATH:0.10,0.40,0.70,0.90]]；允许偏差可取[[MATH:Δ=0.15]]，并可根据验证集上的风险越界误放率在[[MATH:0.10≤Δ≤0.20]]内调整。不得直接从自由文本主观估值。
'@ },
    @{ Anchor='后，如何使用？'; Text=@'
[标红问题29/35：风险越界结果用途] 建议补充：若[[MATH:F_(risk)>0]]，对应风险命题判定为强校验失败并进入降级或重写流程；同时将[[MATH:F_(risk)]]作为最终可信度公式中的连续扣分项。由此形成“硬性阻断+可信度惩罚”的双重控制。
'@ },
    @{ Anchor='若可信度高于输出阈值'; Text=@'
[标红问题30/35：可信度变量和输出区间] 建议统一：[[MATH:R_f]]为融合检测风险；[[MATH:Support=(\sum_j v_j Support(c_j))/(\sum_j v_j+ε)]]；[[MATH:Q_(ref)=N_(valid)/N_(required)]]；[[MATH:U_f]]为归一化检测不确定性；[[MATH:F_(hall)=(\sum_l h_l I_l)/(\sum_l h_l+ε)]]。当[[MATH:T(a)≥0.75]]且结构、引用、未见IOC、归因和风险越界等强校验全部通过时输出可信解释；[[MATH:0.50≤T(a)<0.75]]时降级输出；[[MATH:T(a)<0.50]]时仅输出已有事实和证据缺口。
'@ },
    @{ Anchor='分别表示？；如何取值？'; Text=@'
[标红问题31/35：可信度权重] 建议定义[[MATH:θ_1]]至[[MATH:θ_7]]依次为检测风险、证据覆盖率、命题支持度、引用质量、检测不确定性、幻觉失败惩罚和风险越界惩罚的权重。实施例可取[[MATH:(θ_1,θ_2,θ_3,θ_4,θ_5,θ_6,θ_7)=(0.20,0.20,0.25,0.15,0.08,0.07,0.05)]]，通过验证集网格搜索或非负约束逻辑回归确定，并将最终结果截断为[[MATH:T(a)=clip(T(a),0,1)]]。
'@ },
    @{ Anchor='在需要自适应调度时，系统可采用上下文策略学习方式'; Text=@'
[标红问题32/35：Q学习变量] 建议补充：[[MATH:Q(s_t,a_t)]]表示在状态[[MATH:s_t]]选择路径动作[[MATH:a_t]]后的期望累计折扣收益；[[MATH:max_(a∈A)Q(s_(t+1),a)]]表示到达下一状态[[MATH:s_(t+1)]]后，在允许动作集合[[MATH:A]]中能够获得的最大后续价值。未通过硬约束的动作不进入[[MATH:A]]，防止策略为降低成本而绕过强校验。
'@ },
    @{ Anchor='图3中，直接生成是指？；检索生成是指？'; Text=@'
[标红问题33/35：图3基线定义] 建议在图注和实施例中补充：直接生成是指仅输入基础告警字段，不检索外部证据、不强制证据编号且不执行生成后校验；检索生成是指检索Top-K相关证据后生成，但不构建分层证据包、不强制逐结论引用且不执行多级幻觉校验；本发明包含恶意流量检测、结构化证据包、证据约束生成、逐命题校验、可信度控制和反馈更新。
'@ },
    @{ Anchor='其中数据集1至6分别为哪种数据集？'; Text=@'
[标红问题34/35：图3实验条件和数据占位符] 当前图3缺少可核验的真实数据，不能直接把候选值写成已完成效果。建议新增实验数据说明表，逐项给出数据集名称、流对象或告警数量、类别构成、证据总量、每告警平均证据数、训练测试划分、硬件、模型版本和重复次数。证据数量可按[[MATH:K={4,8,12,16,24,32}]]设置，数据规模可按[[MATH:N={1,5,10,20,50,100}]]万条设置；六个数据集仅可从实际已完成实验的数据中选取。图中应显示数值刻度、均值、误差范围和完整基线名称。
'@ },
    @{ Anchor='图1字太小了，不清楚'; Text=@'
[标红问题35/35：图1清晰度] 建议按4K重新绘制并统一使用黑体，删去重复的细粒度子框、无实际流程含义的省略号和过长说明，仅保留“流量接入—恶意流量检测—告警标准化—证据包—受控生成—幻觉校验—可信输出—反馈更新”主链及必要支路。插入Word后按页面实际宽度检查，最小文字不低于约9磅，主模块文字建议12至14磅。
'@ },
    @{ Anchor='开放集风险和模态冲突构建了路径调度依据'; Text=@'
[补充问题1/6：未定义技术突然出现] “开放集风险”和“模态冲突”在前述模块、变量和公式中均未定义。建议删除该处两个术语，改为“融合检测风险、检测不确定性、证据覆盖率和负证据压力”；若确需保留，则必须新增计算模块、公式和实施例，不能只在有益效果中出现。
'@ },
    @{ Anchor='恶意流量识别率、证据引用覆盖率、无证据结论比例'; Text=@'
[补充问题2/6：图3指标因果关系] 若直接生成、检索生成和本发明共用同一底层恶意流量检测器，生成方式不会直接改变恶意流量识别率。建议将该指标改为“告警解释正确率”或“关键结论支持率”；若坚持使用识别率，应明确反馈更新了检测模型，并增加关闭反馈后的独立消融实验。
'@ },
    @{ Anchor='恶意流量检测模块最终输出检测对象'; Text=@'
[补充问题3/6：变量和名称统一] 建议建立变量表并全文统一：不确定性统一记为[[MATH:U_f]]，融合检测风险统一记为[[MATH:R_f]]，标准化告警风险记为[[MATH:r_a]]；生成侧使用“风险状态”及[[MATH:R_(gen)]]，不再混用风险等级。图号统一采用“图1、图2、图3”。
'@ },
    @{ Anchor='最终可信度不是简单采用大模型自报置信度'; Text=@'
[补充问题4/6：模型自报置信度未进入公式] 后续可信度公式没有模型自报置信度变量。建议删除“模型自报置信度”表述，继续强调检测证据和机器校验结果；不建议为了保持该表述额外引入低可信的自报分数。
'@ },
    @{ Anchor='可信度可表示为：'; Text=@'
[补充问题5/6：可信度范围] 线性组合结果可能小于0或大于1，建议将公式改为[[MATH:T(a)=clip(θ_1R_f+θ_2Cov(a)+θ_3Support+θ_4Q_(ref)-θ_5U_f-θ_6F_(hall)-θ_7F_(risk),0,1)]]，再与输出阈值比较。
'@ },
    @{ Anchor='本发明提出了一种流量大模型辅助的告警证据包生成与幻觉校验方法及装置'; Text=@'
[补充问题6/6：系统与装置称谓] 标题为“方法及系统”，本段写为“方法及装置”，附图说明又写“装置流程图”。建议根据申请主题全文统一为“方法及系统”，系统实施方式可继续使用模块或单元描述。
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
        try {
            $omath.BuildUp()
        }
        catch {
            $script:mathBuildFailures.Add($mathText)
        }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($omath)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($mathRange)
    }
}

if (Test-Path -LiteralPath $output) {
    Remove-Item -LiteralPath $output -Force
}
Copy-FileShared -From $source -To $output

$word = $null
$document = $null
$oldUserName = $null
$oldInitials = $null
$missing = New-Object System.Collections.Generic.List[string]
$script:mathBuildFailures = New-Object System.Collections.Generic.List[string]
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
Write-Output ('MATH_BUILD_FAILURES=' + $script:mathBuildFailures.Count)
if ($script:mathBuildFailures.Count -gt 0) {
    Write-Output ('MATH_BUILD_FAILURE_ITEMS=' + ($script:mathBuildFailures -join ' | '))
}





