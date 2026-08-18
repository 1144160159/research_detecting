from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")


M034_TEXT = """[标记事项034/154：检测证据抽取与证据向量化模块整体替换] 建议将“3、检测证据抽取与证据向量化模块”标题及其后全部内容整体替换为以下内容，替换范围截至“4、结构化证据包构建模块”标题之前，不替换第4节标题：
3、检测证据抽取与证据向量化模块
检测证据抽取与证据向量化模块用于根据统一告警索引[[MATH:AID]]和流标识[[MATH:FID]]，从流量特征库、检测结果库、资产画像库、历史告警库、历史流量特征库和参考基线库中检索与当前告警相关的数据，分别形成流量证据、模型证据、资产证据、历史证据和负证据。上述数据库为逻辑存储结构，可以采用内存表、关系表、键值表、时序表或向量索引实现。若某类数据源中不存在与当前告警匹配的记录，则不生成对应证据，并记录该类证据缺失状态，禁止流量大模型补充未经检测系统获取的事实。

流量证据的原始数据存在于流量特征库和原始流量索引表中。系统根据[[MATH:FID]]和满足[[MATH:T_s≤t≤T_e]]的告警时间窗口读取对应流记录，对报文长度、报文方向、到达时间、协议类型、TCP标志位以及TLS或QUIC可见字段进行解析和统计，得到五元组、包长序列摘要、方向序列摘要、包间隔统计、域名、证书摘要、连接持续时间、上下行比例、突发强度、失败连接比例和会话重试次数。对于高速链路，系统不要求长期保存全部报文字节，而是保存流标识、采集文件编号、报文偏移量、时间范围、可复算摘要和关键统计量。例如，系统对一个流对象的包长序列计算均值、方差、偏度、峰度、前[[MATH:K]]个包长、方向转移次数和突发窗口数量，并将计算结果与原始流量索引[[MATH:rawref_i]]绑定。

模型证据存在于检测结果库中，由恶意流量检测模块在推理过程中直接产生。轻量恶意流量分类模型输出类别概率向量[[MATH:p_f=(p_1,p_2,...,p_C)]]、预测标签[[MATH:k̂=argmax_k p_k]]、最大分类置信度[[MATH:p_max=max_k p_k]]和分类不确定性[[MATH:U_f=-(∑_(k=1)^C p_k ln(p_k))/ln(C)]]；原型距离异常检测分支以分类模型的隐藏层表示[[MATH:h_f]]为输入，输出最近原型类别、最小原型距离[[MATH:d_f=min_k ‖h_f-μ_k‖_2]]和归一化异常分数[[MATH:s_a(f)]]；规则检测分支输出规则编号、命中字段及触发条件。系统同时保存综合风险分数[[MATH:R_f]]、特征贡献集合[[MATH:C_f]]、模型版本[[MATH:V_m]]和阈值版本[[MATH:V_th]]。若检测模块包含多个子检测器，则分别保存各子检测器的输出及融合权重，禁止在证据生成阶段将不同子检测器的结果合并为未经记录的单一结论。

资产证据存在于资产画像库中。资产画像库以源地址、目的地址或设备标识作为索引，由网络地址配置和历史流量滚动统计共同形成。系统在预设统计周期[[MATH:W_a]]内统计各地址的常用端口、协议分布、访问时段、通信对象集合、入站和出站连接比例、服务响应情况以及连接成功率，据此形成资产类型、业务角色、所属网段、常用端口、访问基线和服务暴露状态。没有资产画像记录时，系统将资产证据标记为缺失，不依据地址特征推测资产类型。

历史证据存在于历史告警库和历史流量特征库中。系统首先根据源地址、目的地址、域名、证书摘要、规则编号和检测标签进行精确索引，再利用当前流量特征向量[[MATH:x_a]]与历史流量特征向量[[MATH:x_j]]之间的余弦相似度[[MATH:sim(x_a,x_j)=(x_a^T x_j)/(‖x_a‖_2 ‖x_j‖_2)]]检索相似度最高的前[[MATH:K_h]]个历史记录，从而得到相似告警、相似流量、历史检测结论、同源地址事件、同目的域名事件和同类规则命中情况。历史证据均保存原历史告警索引和历史流量索引，以保证检索结果能够回溯。

负证据不是独立采集的原始数据，而是由负证据构造单元将当前告警与资产画像库、历史正常流量库、域名和证书频率统计表、网络地址配置表以及规则检测统计表进行自动比对后产生。例如，目的域名与内部服务域名匹配、证书摘要在正常业务中高频出现、源地址属于测试网段、当前流量与历史正常样本高度相似或者当前命中规则在验证数据中的误报比例较高时，系统生成对应负证据。负证据表示存在削弱恶意判断的观测信息，不直接覆盖检测标签，并与正向证据共同进入后续支持度计算。

系统按照字段规范化、索引绑定、来源标识、量化评分、编号生成和入库保存六个步骤，将不同来源的数据转换为统一证据对象[[MATH:E_i]]。统一证据对象表示为：
[[MATH:E_i=(EID_i,AID,FID,type_i,content_i,source_i,t_i,TTL_i,rawref_i,v_i,ver_i)]]
其中，[[MATH:EID_i]]为证据编号；[[MATH:AID]]为关联告警索引；[[MATH:FID]]为关联流标识；[[MATH:type_i]]为证据类型；[[MATH:content_i]]为规范化后的证据内容；[[MATH:source_i]]为数据来源；[[MATH:t_i]]为采集时间；[[MATH:TTL_i]]为有效期；[[MATH:rawref_i]]为原始数据索引；[[MATH:v_i]]为证据向量；[[MATH:ver_i]]为提取规则或统计模型版本。系统将时间统一转换为标准时间戳，将流量长度统一转换为字节，对连续数值进行区间归一化，对类别字段进行固定字典编码，并按照[[MATH:AID]]、[[MATH:FID]]和时间窗口完成索引绑定。证据编号按照下式生成：
[[MATH:EID_i=Hash(AID∥FID∥type_i∥source_i∥t_i∥rawref_i)]]
其中，符号“[[MATH:∥]]”表示字段连接操作。相同原始数据、相同证据类型和相同时间条件生成相同证据编号，从而避免证据重复写入。

统一证据向量表示为：
[[MATH:v_i=(type_i,rel_i,trust_i,fresh_i,rare_i,neg_i,src_i)]]
其中，[[MATH:type_i]]为流量证据、模型证据、资产证据、历史证据或负证据的独热编码。相关度[[MATH:rel_i]]根据对象匹配程度、时间接近程度和特征相似度计算：
[[MATH:rel_i=λ_o I_i^obj+λ_t exp(-|t_i-t_a|/τ_r)+λ_s sim(x_i,x_a)]]
其中，[[MATH:I_i^obj]]表示证据与当前告警是否具有相同[[MATH:FID]]、地址、域名、证书或其他索引对象，匹配时取1，否则取0；[[MATH:t_a]]为告警时间；[[MATH:sim(x_i,x_a)]]为证据特征与告警特征的余弦相似度；各权重满足[[MATH:λ_o+λ_t+λ_s=1]]。各权重通过验证集约束搜索确定，并固定记录于证据提取规则版本中；某类证据不存在可比较向量时删除相似度项，并对其余权重重新归一化。

来源可信度[[MATH:trust_i]]根据数据源历史可靠度、字段完整度和解析一致性计算：
[[MATH:trust_i=clip(q_(s_i)c_i(1-err_i),0,1)]]
其中，字段完整度[[MATH:c_i=n_i^valid/n_i^required]]；[[MATH:err_i]]为解析错误字段数与已解析字段数之比；数据源历史可靠度[[MATH:q_(s_i)]]由训练集或验证集中该数据源记录的正确、错误统计得到：
[[MATH:q_(s_i)=(N_(s_i)^correct+α)/(N_(s_i)^correct+N_(s_i)^wrong+α+β)]]
其中，[[MATH:N_(s_i)^correct]]和[[MATH:N_(s_i)^wrong]]分别为该数据源历史记录中经实验标签或后续一致性结果确定为正确和错误的数量，[[MATH:α]]和[[MATH:β]]为平滑参数。

新鲜度[[MATH:fresh_i]]根据证据产生时间与告警时间的间隔计算：
[[MATH:fresh_i=I(t_a-t_i≤TTL_i) exp(-max(0,t_a-t_i)/τ_(type_i))]]
其中，[[MATH:τ_(type_i)]]为按证据类型设置的时间衰减参数，[[MATH:TTL_i]]由同类证据历史有效时长分布或验证集确定；超过有效期的证据令[[MATH:fresh_i=0]]，不再用于生成确定性结论。

稀有度[[MATH:rare_i]]根据同类型证据在当前告警之前的滚动统计窗口[[MATH:W_r]]内的出现频率计算。对于类别型证据，先计算平滑频率：
[[MATH:p_i=(n(x_i)+α)/(N+αB)]]
再计算[[MATH:rare_i=1-p_i]]。其中，[[MATH:n(x_i)]]为当前字段值的出现次数，[[MATH:N]]为窗口内同类型字段总数，[[MATH:B]]为字段取值或统计区间数量。对于连续数值，先将其划入依据训练数据确定的直方图区间，再采用相同方法计算区间稀有度。

负证据强度[[MATH:neg_i]]根据当前证据与各项正常基线的匹配程度计算。对于负证据，定义：
[[MATH:neg_i=1-∏_(k∈K_i)(1-m_(ik))]]
其中，[[MATH:K_i]]为当前证据命中的负向条件集合，[[MATH:m_(ik)]]为第[[MATH:k]]项负向条件的匹配强度。内部域名或测试网段精确匹配时取1；常见证书匹配强度取该证书在正常流量中的归一化出现频率；历史正常流量匹配强度取当前流量与最相似正常样本的余弦相似度；规则误报匹配强度取该规则在验证窗口内的误报比例。对于非负证据，令[[MATH:neg_i=0]]。

来源类型编码[[MATH:src_i]]采用固定来源字典进行独热编码。报文解析与流量统计来源、检测器输出来源、资产画像来源、历史记录来源和参考基线来源分别对应一个编码位置。例如，检测器输出来源表示为[[MATH:src_i=(0,1,0,0,0)]]。证据类型[[MATH:type_i]]表示证据在语义上的类别，来源类型编码[[MATH:src_i]]表示证据由哪个数据存储或处理单元产生，两者相互独立。完成上述转换后，系统将统一证据对象写入证据库，并以[[MATH:EID_i]]、[[MATH:AID]]和[[MATH:FID]]建立索引，供结构化证据包构建、生成约束和幻觉校验模块调用。"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    specs = json.loads(args.source.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in specs}
    if len(specs) != 180 or "M034" not in by_id:
        raise RuntimeError("Expected 180 specifications including M034.")
    if M034_TEXT.count("[[MATH:") != len(MATH_RE.findall(M034_TEXT)):
        raise RuntimeError("Unclosed math marker in M034.")
    if "]]]" in M034_TEXT:
        raise RuntimeError("Ambiguous math marker terminator in M034.")

    before = len(MATH_RE.findall(by_id["M034"]["text"]))
    by_id["M034"]["text"] = M034_TEXT
    args.target.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "comment_count": len(specs),
        "updated_id": "M034",
        "replacement_scope": "section_3_heading_to_before_section_4",
        "m034_formula_count_before": before,
        "m034_formula_count_after": len(MATH_RE.findall(M034_TEXT)),
        "formula_count": sum(len(MATH_RE.findall(item["text"])) for item in specs),
        "m034_chars": len(M034_TEXT),
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
