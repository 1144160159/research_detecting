from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")


DELETE_IDS = {
    "M051",
    "M052",
    "M053",
    "M054",
    "M055",
    "M056",
    "M057",
    "M058",
    "M059",
    "M060",
    "M061",
    "M062",
    "M063",
    "M064",
    "M065",
    "S08",
}


S07_TEXT = """[补充事项07/26：证据排序、压缩与覆盖率计算模块整体替换] 建议将“5、证据排序、压缩与覆盖率计算模块”标题及其后全部内容整体替换为以下内容，替换范围截至“6、路径调度模块”标题之前，不替换第6节标题：
5、证据排序、压缩与覆盖率计算模块
证据排序、压缩与覆盖率计算模块用于在大模型上下文长度受限的条件下，从统一证据库中选择与当前告警关联程度较高、来源可靠、时间有效且重复程度较低的证据，并保证模型证据、流量证据和已经发现的负证据不会被数量较多的历史记录或长文本证据挤出上下文。该模块依次执行证据质量计算、同类去重、分类排序、跨类型合并、证据压缩和覆盖率判定。

对于每条候选证据[[MATH:e_i]]，系统计算综合得分：
[[MATH:Score(e_i)=αrel_i+βtrust_i+γfresh_i+δrare_i+μneg_i-νred_i]]
其中，[[MATH:rel_i]]为相关度，[[MATH:trust_i]]为来源可信度，[[MATH:fresh_i]]为新鲜度，[[MATH:rare_i]]为稀有度，[[MATH:neg_i]]为负证据强度，[[MATH:red_i]]为冗余度；上述分量均归一化至[[MATH:0≤rel_i,trust_i,fresh_i,rare_i,neg_i,red_i≤1]]。各权重均为非负数且满足[[MATH:α+β+γ+δ+μ+ν=1]]，因此在后述实施例权重下，综合得分位于[[MATH:-0.10≤Score(e_i)≤0.90]]，仅用于候选证据之间的相对排序，不将其解释为概率。

冗余度用于衡量候选证据与已选同类证据之间的信息重复程度。系统首先将证据的规范化内容编码为排序向量[[MATH:z_i]]。对于文本证据，[[MATH:z_i]]由固定版本的文本编码模型生成；对于结构化证据，系统按照固定字段顺序将类别字段、数值字段和摘要字段编码为向量。候选证据[[MATH:e_i]]与已选证据[[MATH:e_j]]的归一化相似度为：
[[MATH:q_ij=(1+cos(z_i,z_j))/2]]
令[[MATH:S_(type_i)]]表示已经选入上下文且与[[MATH:e_i]]类型相同的证据集合。当[[MATH:S_(type_i)=∅]]时，令[[MATH:red_i=0]]；否则计算：
[[MATH:red_i=max_(e_j∈S_(type_i)) q_ij]]
若两条证据具有相同证据编号、原始数据索引或内容摘要，则在排序前直接去重；若相似度较高但来源不同，则保留得分较高者，并在其摘要中记录其余证据编号和来源数量。冗余度仅在同一证据类型内计算，避免流量证据与模型证据因描述同一告警而相互抑制。

相关度[[MATH:rel_i]]由字段匹配度、时间匹配度、标签一致度、特征贡献重合度和语义相似度组成：
[[MATH:rel_i=0.30M_i^field+0.20M_i^time+0.20M_i^label+0.10M_i^contrib+0.20M_i^sem]]
其中，第3节中的对象匹配项在本模块中细化为字段匹配度、标签一致度和特征贡献重合度。

字段匹配度按照证据与告警之间能够对应的索引字段计算：
[[MATH:M_i^field=(∑_(r∈F)b_r I(value_(ir)=value_(ar)))/(∑_(r∈F)b_r)]]
其中，[[MATH:F]]为可比较字段集合，包括[[MATH:FID]]、源地址、目的地址、域名、证书摘要、规则编号和协议类型；[[MATH:b_r]]为字段权重；指示函数[[MATH:I(·)]]在字段值一致时取1，否则取0。[[MATH:FID]]直接一致时优先判定为同一检测对象。字段权重由验证集中删除相应字段后造成的匹配准确率下降量归一化得到。

时间匹配度为：
[[MATH:M_i^time=exp(-|t_i-t_a|/τ_r)]]
其中，[[MATH:t_i]]为证据时间，[[MATH:t_a]]为告警时间，[[MATH:τ_r]]为时间衰减参数。实施例中流量证据和模型证据的[[MATH:τ_r]]取3600秒，资产证据取7天，历史证据取30天。

标签一致度[[MATH:M_i^label]]根据证据标签与当前检测标签的关系计算。模型证据的标签一致度取当前告警标签对应的类别概率；历史证据标签与当前标签一致时取1，不一致时取0；不包含标签字段的证据不计算该项，并对其余相关度权重重新归一化。

特征贡献重合度根据证据涉及的特征与特征贡献集合[[MATH:C_f]]之间的重合程度计算：
[[MATH:M_i^contrib=(∑_(j∈F_i∩I_M)a_j(f))/(∑_(j∈I_M)a_j(f))]]
其中，[[MATH:F_i]]为证据涉及的特征集合，[[MATH:I_M]]为特征贡献集合[[MATH:C_f]]中前[[MATH:M]]个高贡献特征的索引集合，[[MATH:a_j(f)]]为第[[MATH:j]]个特征的综合贡献分数。当分母为0时，删除特征贡献重合度项并对其余相关度权重重新归一化。

对于文本或摘要证据，系统将告警的检测标签、高贡献特征、协议类型和关键流量字段组织为告警查询文本，并编码为查询向量[[MATH:q]]；将证据内容编码为向量[[MATH:z_i]]，计算：
[[MATH:sim(q,z_i)=(q^T z_i)/(‖q‖_2 ‖z_i‖_2+ε)]]
语义相似度为：
[[MATH:M_i^sem=(1+sim(q,z_i))/2]]
因此，原文中的余弦相似度对应相关度[[MATH:rel_i]]中的语义相似度分量[[MATH:M_i^sem]]，并通过相关度权重间接进入综合得分，而不是再次作为独立得分重复累加。对于不存在文本或摘要内容的证据，系统删除语义相似度项，并对其余相关度权重重新归一化。查询向量和证据向量必须由同一固定版本的编码模型产生，编码模型更新时重新构建证据向量索引。

来源可信度根据数据源历史可靠度、字段完整率和解析错误率计算：
[[MATH:trust_i=clip(q_(s_i)c_i(1-err_i),0,1)]]
其中，字段完整率为：
[[MATH:c_i=n_i^valid/n_i^required]]
[[MATH:n_i^valid]]为有效字段数量，[[MATH:n_i^required]]为该类证据要求的字段数量；[[MATH:err_i]]为解析错误、字段冲突或索引失效字段数量与已解析字段总数之比。数据源历史可靠度为：
[[MATH:q_(s_i)=(N_(s_i)^correct+1)/(N_(s_i)^correct+N_(s_i)^wrong+2)]]
其中，[[MATH:N_(s_i)^correct]]和[[MATH:N_(s_i)^wrong]]分别为该来源在训练集或验证集中经实验标签或后续一致性结果确定为正确和错误的记录数量。该式采用加一平滑，避免样本较少时可信度直接取0或1。

新鲜度根据证据产生时间与告警时间的距离计算：
[[MATH:fresh_i=I(t_a-t_i≤TTL_i) exp(-max(0,t_a-t_i)/τ_(type_i))]]
其中，[[MATH:τ_(type_i)]]为证据类型对应的时间衰减参数，[[MATH:TTL_i]]为有效期。实施例中流量证据和模型证据的衰减参数取3600秒，资产证据取7天，历史证据和参考基线证据取30天；有效期取对应衰减参数的3倍。证据超过有效期时令[[MATH:fresh_i=0]]。

稀有度根据当前告警之前的滚动窗口[[MATH:W_r]]内同类证据值的出现频率计算。对于类别型证据，采用拉普拉斯平滑计算：
[[MATH:p_i=(n(x_i)+1)/(N+B)]]
[[MATH:rare_i=1-p_i]]
其中，[[MATH:n(x_i)]]为当前证据值在滚动窗口中的出现次数，[[MATH:N]]为同类型证据总数，[[MATH:B]]为取值类别数。对于连续数值，系统先按照训练数据确定的分位点划分统计区间，再根据所在区间的出现频率计算稀有度。

负证据强度根据当前证据命中的反向条件计算：
[[MATH:neg_i=1-∏_(k∈K_i)(1-m_(ik))]]
其中，[[MATH:K_i]]为证据命中的负向条件集合，[[MATH:m_(ik)]]为第[[MATH:k]]个条件的匹配强度。内部域名、测试网段等精确匹配条件取1；常见证书的匹配强度取其在正常流量中的归一化频率；历史正常样本匹配强度取最大余弦相似度；规则误报匹配强度取该规则在验证窗口内的误报比例。非负证据令[[MATH:neg_i=0]]。

综合得分的权重参数通过验证集约束搜索确定。系统在满足各权重非负且总和为1的条件下，搜索能够提高高价值证据保留率、负证据保留率和证据覆盖率，同时降低重复证据比例、无证据结论率和上下文占用量的参数组合。一个实施例取：
[[MATH:α=0.30, β=0.20, γ=0.15, δ=0.10, μ=0.15, ν=0.10]]
上述数值为实施例参数，不构成对保护范围的限制。当业务数据分布或模型版本发生变化时，仅使用新的训练集或验证集重新搜索并更新权重版本，不使用待检测样本的真实标签调整权重。

证据选择采用分类型保留和跨类型贪心合并方式。系统先在流量证据、模型证据、资产证据、历史证据和负证据内部按照综合得分降序排列；随后为流量证据和模型证据预留最低数量，为已经发现的负证据预留至少一个位置，再从各类型候选队列中依次选择当前综合得分最高的证据。每选入一条证据后，系统重新计算同类型剩余证据的冗余度和综合得分，直至达到上下文长度预算。

对于重复历史事件和相似流量证据，系统按照证据类型、检测标签和相似度进行分组。组内仅保留得分最高证据的关键内容，同时记录该组包含的证据数量、证据编号集合、时间范围和来源集合。压缩后的单条证据至少保留证据编号、证据类型、关键字段、来源、采集时间、综合得分和原始数据索引，完整内容继续保存在证据库中。

证据覆盖率用于衡量当前证据集合是否满足生成可信解释的最低要求。对于告警[[MATH:a]]，定义类型[[MATH:t]]的有效证据数量：
[[MATH:n_t(a)=∑_(e_i∈S) I(type_i=t)I(Score(e_i)≥θ_e)I(trust_i≥θ_trust)I(fresh_i>0)]]
其中，[[MATH:S]]为压缩后进入证据包的证据集合。实施例中取[[MATH:θ_e=0.35]]，[[MATH:θ_trust=0.50]]。证据覆盖率为：
[[MATH:Cov(a)=(∑_(t∈T)w_t I(n_t(a)≥m_t))/(∑_(t∈T)w_t)]]
其中，[[MATH:T]]为当前告警场景的必要证据类型集合，始终包含流量证据和模型证据；资产库或历史库存在可用记录时加入对应类型；已经构造出负证据候选时加入负证据类型。[[MATH:w_t]]为证据类型权重，[[MATH:m_t]]为最低有效证据数量。证据类型权重根据验证集中删除该类型后造成的解释支持率下降量归一化得到，最低数量通过验证集搜索得到。一个实施例中：
[[MATH:(w_flow,w_model,w_asset,w_history,w_negative)=(0.30,0.30,0.15,0.15,0.10)]]
[[MATH:(m_flow,m_model,m_asset,m_history,m_negative)=(2,1,1,1,1)]]
当[[MATH:T=∅]]或[[MATH:∑_(t∈T)w_t=0]]时，系统拒绝计算覆盖率并将告警标记为证据配置无效。

系统将[[MATH:Cov(a)<0.70]]判定为证据覆盖率不足。若[[MATH:0.50≤Cov(a)<0.70]]，系统自动扩大历史检索时间窗口、增加相似流量检索数量或重新读取流量摘要，并在补证后重新计算覆盖率；若补证后仍满足[[MATH:Cov(a)<0.70]]，则进入轻量模板路径。若[[MATH:Cov(a)<0.50]]，或者不存在有效流量证据、有效模型证据中的任意一类，则直接进入轻量模板路径，仅输出检测标签、风险分数、已有证据和证据缺失说明，不允许流量大模型生成确定性的攻击归因结论。"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    specs = json.loads(args.source.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in specs}
    expected = DELETE_IDS | {"S07"}
    missing = sorted(expected - set(by_id))
    if missing:
        raise RuntimeError(f"Missing specifications: {missing}")
    if S07_TEXT.count("[[MATH:") != len(MATH_RE.findall(S07_TEXT)):
        raise RuntimeError("Unclosed math marker in S07.")
    if "]]]" in S07_TEXT:
        raise RuntimeError("Ambiguous math marker terminator in S07.")

    before_count = len(MATH_RE.findall(by_id["S07"]["text"]))
    filtered = [item for item in specs if item["id"] not in DELETE_IDS]
    filtered_by_id = {item["id"]: item for item in filtered}
    filtered_by_id["S07"]["text"] = S07_TEXT

    args.target.write_text(
        json.dumps(filtered, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = {
        "source_comment_count": len(specs),
        "target_comment_count": len(filtered),
        "retained_replacement_id": "S07",
        "deleted_ids": sorted(DELETE_IDS),
        "s07_formula_count_before": before_count,
        "s07_formula_count_after": len(MATH_RE.findall(S07_TEXT)),
        "target_formula_count": sum(
            len(MATH_RE.findall(item["text"])) for item in filtered
        ),
        "s07_chars": len(S07_TEXT),
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
