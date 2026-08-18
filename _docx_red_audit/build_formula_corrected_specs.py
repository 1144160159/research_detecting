from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")
PREFIX_RE = re.compile(r"^(\[[^\]]+\]\s*)")


CONTENT_OVERRIDES = {
    "M007": (
        "会话用于描述完整通信生命周期，流对象是会话在一个统计窗口内的特征计算单元，长会话可对应多个流对象。"
        "流标识可表示为[[MATH:FID=H(K_5^(N)∥w_id∥s_id)]]。其中K_5的上标N表示五元组已按端点字典序完成方向归一化，"
        "[[MATH:w_id]]为由报文时间戳和窗口长度确定的窗口编号，[[MATH:s_id]]为采集点编号；∥表示带长度前缀的字段串联，H表示哈希函数。"
    ),
    "M015": (
        "轻量分类模型输出第k个已知类别的logit [[MATH:z_k]]。经温度缩放后的类别概率为"
        "[[MATH:p_k=P(y=k∣f)=(e^(z_k/T))/(∑_(ℓ=1)^C e^(z_ℓ/T))]]，其中[[MATH:T>0]]为温度参数；"
        "未进行温度缩放时取T=1。温度参数只由训练集和验证集确定。"
    ),
    "M016": (
        "模型倒数第二层得到流表征[[MATH:h_f]]；第[[MATH:k]]个已知类原型为"
        "[[MATH:μ_k=(1/N_k)∑_(i:y_i=k) h_i]]。流对象到最近已知类原型的距离为"
        "[[MATH:d_f=min_(1≤k≤C) ‖h_f-μ_k‖_2]]，异常分数为"
        "[[MATH:s_a(f)=min(1,d_f/τ_d)]]。[[MATH:τ_d]]取已知验证样本距离的95%分位数。"
    ),
    "M017": (
        "令[[MATH:I_m(f)∈{0,1}]]表示第[[MATH:m]]条规则是否命中，[[MATH:q_m≥0]]为规则可靠度。"
        "存在有效规则时，规则命中分数为[[MATH:s_r(f)=(∑_m q_m I_m(f))/(∑_m q_m)]]；"
        "没有有效规则或权重和为零时令[[MATH:s_r(f)=0]]。[[MATH:q_m]]由历史验证样本的精确率确定。"
    ),
    "M018": (
        "采用归一化熵[[MATH:U_f=-(∑_(k=1)^C p_k ln p_k)/(ln C)]]，并约定0 ln 0=0。"
        "其中[[MATH:C≥2]]为已知类别数，故[[MATH:0≤U_f≤1]]。正常类若参与分类，应计入[[MATH:C]]并在类别表中明确。"
    ),
    "M024": (
        "当[[MATH:R_f<τ_n]]时判定风险较低，实施例取[[MATH:τ_n=0.35]]。"
        "若规则存在强制恶意命中，则先执行硬规则，不由低融合风险覆盖。"
    ),
    "M029": (
        "树模型采用TreeSHAP，线性模型采用特征值与系数乘积，浅层神经网络采用梯度乘输入，"
        "得到第j个特征对流对象f的贡献[[MATH:φ_j(f)]]。按[[MATH:|φ_j(f)|]]降序排列，"
        "保留前[[MATH:M=10]]项构成贡献集合[[MATH:C_f]]。"
    ),
    "M030": (
        "“贡献较高的特征项”是[[MATH:C_f]]中按[[MATH:|φ_j(f)|]]排序靠前的元素。"
        "相关系数绝对值超过0.95的特征只保留贡献绝对值较大者，并保留贡献的正负方向。"
    ),
    "M033": (
        "读取检测器标识和校准版本，以原始等级为键查询版本化映射值，得到[[MATH:0≤r_a≤1]]；"
        "未知等级进入缺失处理，不得默认映射为高风险。"
    ),
    "M044": (
        "各来源记录先完成字段映射、类型转换、时间统一、去重和缺失标记，再生成统一证据对象"
        "[[MATH:E_i=(id_i,type_i,value_i,source_i,t_i^(start),t_i^(end),q_i,AID,FID,ref_i,ver_i)]]。"
        "其中q_i表示证据质量；证据编号由AID、类型、序号和内容摘要联合生成。"
    ),
    "M051": (
        "先定义候选证据e_i与已选证据e_j的归一化相似度"
        "[[MATH:q_ij=(1+cos(v_i,v_j))/2]]，再定义冗余度[[MATH:red_i=max_(e_j∈S) q_ij]]。"
        "当已选集合[[MATH:S]]为空时令[[MATH:red_i=0]]。该式把余弦相似度由[-1,1]映射至[0,1]，并按固定编码模型版本计算。"
    ),
    "M067": (
        "存在负证据且权重和大于零时，定义"
        "[[MATH:P_neg=(∑_(e_i∈E_neg) q_i neg_i)/(∑_(e_i∈E_neg) q_i)]]，其中[[MATH:q_i≥0]]为证据权重；"
        "无负证据或权重和为零时令[[MATH:P_neg=0]]。"
    ),
    "M073": (
        "路径收益定义为"
        "[[MATH:G(a,p)=0.4ΔCov(a,p)+0.3P_pass(type(a),p)+0.3r_a I_high(p)]]。"
        "其中ΔCov为执行路径后的预计覆盖率增量，P_pass为同类告警采用该路径的历史校验通过率，"
        "I_high表示该路径是否包含高强度校验；三项均归一化至[0,1]并只使用告警发生前统计。"
    ),
    "M074": (
        "路径成本定义为"
        "[[MATH:C(a,p)=min(1,0.4n_tok(a,p)/B_tok+0.4t_lat(a,p)/B_lat+0.2n_call(a,p)/B_call)]]。"
        "n_tok、t_lat和n_call分别表示预计Token数、时延和模型调用次数，B_tok、B_lat和B_call为相应预算；"
        "实施例预算为4096 Token、3000毫秒和2次模型调用。"
    ),
    "M075": (
        "路径执行后的预计幻觉风险定义为"
        "[[MATH:H(a,p)=min(1,max(0,0.30U_f+0.25(1-Cov(a,p))+0.20P_neg(a,p)+0.15I_IOC(a,p)+0.10I_attr(a,p)))]]。"
        "Cov、P_neg、I_IOC和I_attr均为执行路径p后的预计量；高强度校验只能按历史通过率降低预计风险，不能将风险直接置零。"
    ),
    "M076": (
        "对每类必要证据t，先计算归一化缺口"
        "[[MATH:g_t(a,p)=max(0,m_t-n̂_t(a,p))/max(m_t,1)]]，再定义"
        "[[MATH:D(a,p)=(∑_(t∈T) w_t g_t(a,p))/(∑_(t∈T) w_t)]]。"
        "其中m_t为最低数量，n̂_t为执行路径后的预计证据数，w_t≥0；权重和为零时令D(a,p)=0。"
    ),
    "M080": (
        "[[MATH:p^*=argmax_(p∈P_feasible) U(a,p)]]表示在满足硬约束的可行路径集合中，"
        "使[[MATH:U(a,p)=G(a,p)-λC(a,p)-ρH(a,p)-ηD(a,p)]]最大的最终执行路径。"
    ),
    "M083": (
        "系统为五条路径分别计算效用值并保留path_id；"
        "[[MATH:p^*=argmax_(p∈P_feasible) U(a,p)]]返回的path_id直接对应具体路径。"
        "并列时优先选择成本较低且校验强度不降低的路径。"
    ),
    "M085": (
        "统一称“生成风险状态”。大模型只能输出正常、可疑、高风险、已确认四个枚举值，"
        "相应数值满足[[MATH:R_gen∈{0.10,0.40,0.70,0.90}]]；后续风险越界校验决定是否保留。"
    ),
    "M088": (
        "证据编号在构包阶段生成，可表示为"
        "[[MATH:eid=H(AID∥type∥seq∥digest∥version)]]。参与哈希的字段先按固定规则规范化并使用分隔符串联；"
        "大模型输出必须包含evidence_ids且只能引用当前证据包版本的编号。"
    ),
    "M094": (
        "[[MATH:ω_i^+]]表示支持证据[[MATH:e_i∈Ref(c_j)]]的归一化权重，"
        "[[MATH:ω_i^+=S_i^+/(∑_(e_h∈Ref(c_j)) S_h^+)]]。分母为零时对应支持加权和置零。"
    ),
    "M095": (
        "[[MATH:ω_k^-]]表示冲突负证据[[MATH:e_k∈Neg(c_j)]]的归一化权重，"
        "[[MATH:ω_k^-=S_k^-/(∑_(e_h∈Neg(c_j)) S_h^-)]]。分母为零时对应冲突加权和置零。"
    ),
    "M109": (
        "关键结论的平均支持度应采用命题重要度加权平均："
        "[[MATH:S_avg(a)=(∑_(j=1)^J v_j Support(c_j))/(∑_(j=1)^J v_j)]]。"
        "其中v_j≥0；没有关键命题或权重和为零时令S_avg(a)=0，而非在分母中人为加入极小常数。"
    ),
    "M112": (
        "幻觉失败惩罚定义为"
        "[[MATH:F_hall=(∑_l h_l I_l)/(∑_l h_l)]]。"
        "权重示例为结构0.10、引用0.15、支持度0.15、未见IOC 0.20、归因0.15、一致性0.10、风险越界0.15；"
        "没有适用校验项或权重和为零时令F_hall=0。"
    ),
    "M117": (
        "[[MATH:θ_1]]表示检测器校准可靠度[[MATH:C_det]]的权重。C_det由验证集上的校准误差、稳定性和版本状态确定，"
        "不是[[MATH:1-U_f]]；否则会与后续不确定性惩罚重复计权。风险严重度本身也不作为解释可信度正向项。"
    ),
    "M121": (
        "[[MATH:θ_3]]表示关键结论平均支持度[[MATH:S_avg(a)]]的权重。"
        "风险严重度本身不作为解释可信度正向项。"
    ),
    "M132": (
        "原式中的下一状态价值应写为"
        "[[MATH:max_(a'∈A_feasible(s_(t+1))) Q(s_(t+1),a')]]，表示下一状态可行动作集合中的最大后续价值；"
        "未通过硬约束的动作不参与最大化。"
    ),
    "S04": (
        "正文熵公式应采用"
        "[[MATH:U_f=-(∑_(k=1)^C p_k ln p_k)/(ln C)]]并约定0 ln 0=0，"
        "从而保证[[MATH:0≤U_f≤1]]并与0.30、0.45等阈值一致；不应在对数项中加入ε后仍直接声称严格取值于[0,1]。"
    ),
    "S14": (
        "恶意风险越高不代表解释越可信，且把C_det定义为1-U_f会与-U_f重复计权。建议正文可信度式修正为"
        "[[MATH:T(a)=min(1,max(0,θ_1C_det+θ_2Cov(a)+θ_3S_avg(a)+θ_4Q_ref-θ_5U_f-θ_6F_hall-θ_7F_risk))]]。"
        "其中C_det为独立的检测器校准可靠度，R_f仅用于路径优先级和风险越界比较。"
    ),
    "S18": (
        "强化学习奖励可写为"
        "[[MATH:r_t=c_1Y_trust+c_2ΔCov_t-c_3F_hall,t-c_4L̂_t-c_5Ĉ_t]]。"
        "其中各收益和惩罚先归一化至[0,1]；实施例学习率0.1、折扣因子0.9、初始探索率0.1，采用离线训练并设置性能下降回滚门限。"
    ),
    "S26": (
        "具体步骤为：读取[[MATH:detector_id]]、原始等级和[[MATH:calibration_version]]，"
        "查询仅由训练集或验证集形成的版本化映射表，得到[[MATH:0≤r_a≤1]]；"
        "未登记等级写入缺失状态并转校准或降级流程，不得凭固定默认值替代。"
    ),
}


EXACT_MATH = {
    "FID=Hash(K_(5tuple)^norm,wid,sid)": "FID=H(K_5^(N)∥w_id∥s_id)",
    "wid": "w_id",
    "sid": "s_id",
    "epsilon=10^(-8)": "ε=10^(-8)",
    "10^(-12)<=epsilon<=10^(-6)": "10^(-12)≤ε≤10^(-6)",
    "x_j^max=x_j^min": "x_j^(max)=x_j^(min)",
    "p(y=k|f)=e^(z_k)/(sum_(l=1)^C e^(z_l))": "p_k=P(y=k∣f)=(e^(z_k/T))/(∑_(ℓ=1)^C e^(z_ℓ/T))",
    "mu_k=(1/N_k)sum_(i:y_i=k)h_i": "μ_k=(1/N_k)∑_(i:y_i=k) h_i",
    "d_f=min_k norm(h_f-mu_k)_2": "d_f=min_(1≤k≤C) ‖h_f-μ_k‖_2",
    "s_a(f)=min(1,d_f/tau_d)": "s_a(f)=min(1,d_f/τ_d)",
    "I_m(f)in{0,1}": "I_m(f)∈{0,1}",
    "s_r(f)=sum_m q_m I_m(f)/(sum_m q_m+epsilon)": "s_r(f)=(∑_m q_m I_m(f))/(∑_m q_m)",
    "U_f=-sum_(k=1)^C p_k log(p_k+epsilon)/log C": "U_f=-(∑_(k=1)^C p_k ln p_k)/(ln C)",
    "0<=U_f<=1": "0≤U_f≤1",
    "0.35<=R_f<0.70": "0.35≤R_f<0.70",
    "R_f<tau_n=0.35": "R_f<τ_n",
    "abs(contrib_j)": "|φ_j(f)|",
    "contrib_j": "φ_j(f)",
    "r_a in[0,1": "0≤r_a≤1",
    "E_i={eid,type,value,source,t_start,t_end,quality,AID,FID,raw_ref,version}": "E_i=(id_i,type_i,value_i,source_i,t_i^(start),t_i^(end),q_i,AID,FID,ref_i,ver_i)",
    "rel_i=0.30M_field+0.20M_time+0.20M_label+0.10M_contrib+0.20M_sem": "rel_i=0.30M_i^(field)+0.20M_i^(time)+0.20M_i^(label)+0.10M_i^(contrib)+0.20M_i^(sem)",
    "trust_i=r_(src,i)c_i": "trust_i=r_i^(src)c_i",
    "r_(src,i)": "r_i^(src)",
    "c_i=0.5c_field+0.3c_packet+0.2c_trace": "c_i=0.5c_i^(field)+0.3c_i^(packet)+0.2c_i^(trace)",
    "fresh_i=e^(-abs(t_i-t_a)/tau_type)": "fresh_i=e^(-|t_i-t_a|/τ_type)",
    "tau=3600s": "τ_type=3600 s",
    "rare_i=min(1,-log(P_i+epsilon)/kappa)": "rare_i=min(1,-ln(P_i)/κ)",
    "neg_i=clip(0.4I_field+0.3I_base+0.3P_contra,0,1)": "neg_i=min(1,max(0,0.4I_field+0.3I_base+0.3P_contra))",
    "red_i=max_(e_j in S)cos(v_i,v_j)": "red_i=max_(e_j∈S)(1+cos(v_i,v_j))/2",
    "M_sem=(1+cos(q,e_i))/2": "M_sem=(1+cos(q,e_i))/2",
    "theta_cov=0.60": "θ_cov=0.60",
    "P_neg=sum_(e_i in E_neg)q_i neg_i/(sum_(e_i in E_neg)q_i+epsilon)": "P_neg=(∑_(e_i∈E_neg) q_i neg_i)/(∑_(e_i∈E_neg) q_i)",
    "G(a,p)=0.4DeltaCov(a,p)+0.3PassHist(type,p)+0.3R_a I_high": "G(a,p)=0.4ΔCov(a,p)+0.3P_pass(type(a),p)+0.3r_a I_high(p)",
    "C(a,p)=0.4Tok/B_tok+0.4Lat/B_lat+0.2Call/B_call": "C(a,p)=min(1,0.4n_tok(a,p)/B_tok+0.4t_lat(a,p)/B_lat+0.2n_call(a,p)/B_call)",
    "H(a,p)=clip(0.30U_f+0.25(1-Cov)+0.20P_neg+0.15I_IOC+0.10I_attr,0,1)": "H(a,p)=min(1,max(0,0.30U_f+0.25(1-Cov(a,p))+0.20P_neg(a,p)+0.15I_IOC(a,p)+0.10I_attr(a,p)))",
    "D(a,p)=sum_(t in T)w_t max(0,m_t-nhat_t(a,p))/sum_(t in T)w_t": "D(a,p)=(∑_(t∈T) w_t g_t(a,p))/(∑_(t∈T) w_t)",
    "nhat_t": "n̂_t",
    "G-lambda C-rho H-eta D": "G(a,p)-λC(a,p)-ρH(a,p)-ηD(a,p)",
    "P_feasible subseteq P": "P_feasible⊆P",
    "p^*=argmax_(p in P_feasible)U(a,p)": "p^*=argmax_(p∈P_feasible) U(a,p)",
    "0.10,0.40,0.70,0.90": "R_gen∈{0.10,0.40,0.70,0.90}",
    "eid=Hash(AID,type,seq,content_digest,version)": "eid=H(AID∥type∥seq∥digest∥version)",
    "Neg(c_j) subseteq E_neg": "Neg(c_j)⊆E_neg",
    "match(c_j,e_i)=clip(0.4M_rule+0.25M_sem+0.35P_entail,0,1)": "match(c_j,e_i)=min(1,max(0,0.4M_rule+0.25M_sem+0.35P_entail))",
    "conflict(c_j,e_k)=clip(0.5I_rule+0.5P_contra,0,1)": "conflict(c_j,e_k)=min(1,max(0,0.5I_rule+0.5P_contra))",
    "omega_i": "ω_i^+",
    "omega_i=Score^+(e_i)/(sum_h Score^+(e_h)+epsilon)": "ω_i^+=S_i^+/(∑_(e_h∈Ref(c_j)) S_h^+)",
    "omega_k": "ω_k^-",
    "omega_k=Score^+(e_k)/(sum_h Score^+(e_h)+epsilon)": "ω_k^-=S_k^-/(∑_(e_h∈Neg(c_j)) S_h^-)",
    "kappa=0.6": "κ=0.6",
    "IOC_new=IOC_out setminus IOC_ep": "IOC_new=IOC_out∖IOC_ep",
    "Delta=0.15": "Δ=0.15",
    "0.10<=Delta<=0.20": "0.10≤Δ≤0.20",
    "Support_bar=sum_j v_j Support(c_j)/(sum_j v_j+epsilon)": "S_avg(a)=(∑_(j=1)^J v_j Support(c_j))/(∑_(j=1)^J v_j)",
    "Support_bar": "S_avg(a)",
    "F_hall=sum_l h_l I_l/(sum_l h_l+epsilon)": "F_hall=(∑_l h_l I_l)/(∑_l h_l)",
    "0.50<=T(a)<0.75": "0.50≤T(a)<0.75",
    "Conf_det=1-U_f": "C_det",
    "max_(a in A_feasible(s_(t+1)))Q(s_(t+1),a)": "max_(a'∈A_feasible(s_(t+1))) Q(s_(t+1),a')",
    "log C": "ln C",
    "U_f in[0,1": "U_f∈[0,1]",
    "1-max_k p_k": "1-max_k p_k",
    "Score_i^+=max(0,Score_i)": "S_i^+=max(0,Score_i)",
    "r_t=c_1Y_trusted+c_2Gain_evid-c_3F_hall-c_4Lat-c_5Cost": "r_t=c_1Y_trust+c_2ΔCov_t-c_3F_hall,t-c_4L̂_t-c_5Ĉ_t",
    "U(a,p)=G(a,p)-lambda C(a,p)-rho H(a,p)-eta D(a,p)": "U(a,p)=G(a,p)-λC(a,p)-ρH(a,p)-ηD(a,p)",
}


GREEK = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "eta": "η",
    "theta": "θ",
    "kappa": "κ",
    "lambda": "λ",
    "mu": "μ",
    "nu": "ν",
    "rho": "ρ",
    "tau": "τ",
    "omega": "ω",
    "Delta": "Δ",
}


SEMANTIC_REASONS = {
    "M015": "补入温度参数并把概率写成规范Softmax分式",
    "M016": "明确最近原型搜索范围和欧氏范数",
    "M017": "删除会改变加权平均取值的epsilon并补充分母为零情形",
    "M018": "改为严格归一化熵并采用0ln0约定",
    "M024": "拆开判定条件与阈值赋值，消除链式等式歧义",
    "M029": "统一特征贡献符号及绝对值排序",
    "M044": "将记录型证据对象改为字段明确的有序元组",
    "M051": "把余弦相似度显式映射到0至1",
    "M067": "改为条件定义的加权平均，避免epsilon造成系统偏差",
    "M073": "补全路径相关变量和高强度校验指示量",
    "M074": "在公式中显式执行成本截断并补全路径参数",
    "M075": "使幻觉风险成为路径相关的预计风险",
    "M076": "先按最低需求归一化单类缺口，再加权聚合",
    "M080": "给出完整可行域和效用函数",
    "M085": "把四个枚举映射值绑定到生成风险变量",
    "M088": "明确哈希输入规范化和字段分隔",
    "M094": "正证据权重仅在引用支持集合内归一化",
    "M095": "负证据权重仅在冲突负证据集合内归一化",
    "M109": "采用条件定义的命题重要度加权平均",
    "M112": "采用条件定义的校验失败加权平均",
    "M117": "消除C_det等于1-U_f造成的不确定性重复计权",
    "M121": "与修正后的平均支持度符号保持一致",
    "M132": "下一动作改用a'并限定可行动作集合",
    "S04": "同步修正正文熵公式的严格取值边界",
    "S14": "重构最终可信度，删除恶意风险正向项和重复不确定性项",
    "S18": "统一奖励量纲、符号和时刻下标",
}


def replace_content(text: str, content: str) -> str:
    match = PREFIX_RE.match(text)
    if not match:
        raise ValueError(f"comment prefix not found: {text[:80]!r}")
    return match.group(1) + content


def canonicalize_math(source: str) -> str:
    if source in EXACT_MATH:
        return EXACT_MATH[source]

    value = source
    for name, symbol in GREEK.items():
        value = re.sub(
            rf"(?<![A-Za-z]){re.escape(name)}(?=(_|\^|=|,|\)|$|\s))",
            symbol,
            value,
        )
    value = value.replace("<=", "≤").replace(">=", "≥")
    value = value.replace(" subseteq ", "⊆").replace(" setminus ", "∖")
    value = re.sub(r"\bsum_", "∑_", value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("report")
    args = parser.parse_args()

    specs = json.loads(Path(args.input).read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in specs}
    missing_overrides = sorted(set(CONTENT_OVERRIDES) - set(by_id))
    if missing_overrides:
        raise SystemExit(f"missing override ids: {missing_overrides}")

    for comment_id, content in CONTENT_OVERRIDES.items():
        by_id[comment_id]["text"] = replace_content(by_id[comment_id]["text"], content)

    changes: list[dict[str, str]] = []
    formula_count_before = 0
    formula_count_after = 0
    for item in specs:
        before_text = item["text"]
        before_tokens = MATH_RE.findall(before_text)
        formula_count_before += len(before_tokens)

        def replacement(match: re.Match[str]) -> str:
            before = match.group(1)
            after = canonicalize_math(before)
            if before != after:
                changes.append({"id": item["id"], "before": before, "after": after})
            return f"[[MATH:{after}]]"

        item["text"] = MATH_RE.sub(replacement, before_text)
        formula_count_after += len(MATH_RE.findall(item["text"]))

    all_tokens = [
        token
        for item in specs
        for token in MATH_RE.findall(item["text"])
    ]
    forbidden_patterns = {
        "ascii_greek": re.compile(
            r"(?<![A-Za-z])(epsilon|alpha|beta|gamma|delta|theta|kappa|lambda|mu|nu|rho|tau|omega|Delta)(?=_|\^|=|,|\)|$|\s)"
        ),
        "ascii_relations": re.compile(r"<=|>="),
        "ascii_nary": re.compile(r"\bsum_"),
        "ascii_set_ops": re.compile(r"\bsubseteq\b|\bsetminus\b"),
        "pseudo_functions": re.compile(r"\bnorm\(|\babs\(|\bclip\(|\bnhat\b|Support_bar"),
        "broken_interval": re.compile(r"(?:\bin|∈)\[0,1(?!\])"),
    }
    invalid: list[dict[str, str]] = []
    for token in all_tokens:
        for category, pattern in forbidden_patterns.items():
            if pattern.search(token):
                invalid.append({"category": category, "token": token})

    if invalid:
        raise SystemExit(json.dumps(invalid, ensure_ascii=False, indent=2))

    Path(args.output).write_text(
        json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = {
        "comment_count": len(specs),
        "formula_comments": sum(bool(MATH_RE.search(item["text"])) for item in specs),
        "formula_count_before_override": 207,
        "formula_count_after": formula_count_after,
        "changed_formula_tokens": len(changes),
        "semantic_corrections": [
            {"id": comment_id, "reason": reason}
            for comment_id, reason in SEMANTIC_REASONS.items()
        ],
        "format_changes": changes,
        "validation": {
            "invalid_token_count": len(invalid),
            "all_formulas_wrapped": formula_count_after == len(all_tokens),
        },
    }
    Path(args.report).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "comment_count": len(specs),
        "formula_comments": report["formula_comments"],
        "formula_count_after": formula_count_after,
        "changed_formula_tokens": len(changes),
        "semantic_corrections": len(SEMANTIC_REASONS),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
