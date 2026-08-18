from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")


OVERRIDES = {
    "M028": (
        "[标记事项028/154：④特征贡献与检测证据输出整体替换建议] "
        "建议将本节整体替换为以下内容：\n"
        "④ 特征贡献与检测证据输出\n"
        "恶意流量检测模块输出最终检测标签和风险分数，同时输出轻量恶意流量分类模型结果、"
        "原型距离异常检测分支结果、特征贡献、规则命中、模型版本和检测上下文。"
        "本节所称“模型输出”仅指前述两个检测模型的输出，不包括流量大模型生成的自然语言内容。\n"
        "轻量恶意流量分类模型具体为面向标准化流量特征向量[[MATH:x_f]]的多层感知机。"
        "具体实施例采用包含128维和64维隐藏层的两层全连接网络，隐藏层采用ReLU激活，输出层产生C个已知类别的逻辑值和类别概率。"
        "该模型输出预测已知类别[[MATH:k̂]]、对应类别概率[[MATH:p_(k̂)]]、分类不确定性[[MATH:U_f]]以及64维隐藏层特征表示[[MATH:h_f]]。"
        "已知类别包括正常流量和训练集中已登记的恶意流量类别。\n"
        "原型距离异常检测分支具体为基于类别均值原型的欧氏距离检测器，不是另一套大模型。"
        "该分支以[[MATH:h_f]]为输入，将每个已知类别训练样本特征表示的均值作为类别原型[[MATH:μ_k]]，"
        "输出最近原型类别[[MATH:k^*]]、最小原型距离[[MATH:d_f]]和归一化异常分数[[MATH:s_a(f)]]。"
        "样本与最近已知类别原型距离越大，表示其偏离已知类别的程度越高。规则命中结果单独记为[[MATH:H_f]]，"
        "记录规则编号、命中字段、字段值和触发条件。\n"
        "为解释两个检测分支的判断依据，对第j个输入特征分别计算分类贡献"
        "[[MATH:φ_j^(cls)(f)=(x_j-x_j^0)(∂z_(k̂)/∂x_j)]]和原型距离贡献"
        "[[MATH:φ_j^(pro)(f)=(x_j-x_j^0)(∂d_f/∂x_j)]]。"
        "其中[[MATH:x_j^0]]为训练集对应特征的均值；输入完成零均值标准化时取0。"
        "将两类贡献的绝对值分别归一化为[[MATH:φ̄_j^(cls)(f)]]和[[MATH:φ̄_j^(pro)(f)]]，"
        "再计算综合贡献[[MATH:a_j(f)=λφ̄_j^(cls)(f)+(1-λ)φ̄_j^(pro)(f)]]，其中[[MATH:0≤λ≤1]]，实施例取0.5。"
        "若某一分支全部特征贡献的绝对值之和为0，则该分支的归一化贡献统一取0。\n"
        "按照[[MATH:a_j(f)]]降序排列，取前[[MATH:M=10]]个特征索引形成集合[[MATH:I_M]]，"
        "并构造特征贡献集合[[MATH:C_f={c_j∣j∈I_M}]]。其中每个贡献项表示为"
        "[[MATH:c_j=(id_j,name_j,x_j,φ_j^(cls),φ_j^(pro),a_j,dir_j)]]，"
        "分别记录特征编号、名称、原始值、两个检测分支的贡献、综合贡献分数和贡献方向。"
        "因此，“贡献较高的特征项”就是[[MATH:C_f]]中按照[[MATH:a_j(f)]]选出的前M项，"
        "而[[MATH:C_f]]是这些高贡献特征项组成的结构化集合，二者不是相互独立的输出。\n"
        "恶意流量检测模块最终输出检测对象"
        "[[MATH:D_f=(FID,label_f,k̂,p_(k̂),R_f,U_f,k^*,d_f,s_a(f),C_f,H_f,V_m,T_f,Ctx_f)]]。"
        "其中label_f为综合检测标签，R_f为综合风险分数，V_m同时记录分类模型、类别原型、阈值和校准参数版本，"
        "T_f为检测时间窗口，Ctx_f为协议类型、通信方向、持续时间、报文数和字节数等检测上下文。"
        "上述结果构成后续证据包中的检测模型证据层，使流量大模型只能依据实际检测证据生成解释。"
    ),
    "M029": (
        "[标记事项029/154：贡献集合计算] 本实施方式已将检测模型限定为轻量多层感知机和共享特征表示的原型距离分支，"
        "因此不再使用TreeSHAP或线性模型的系数乘积。第j个输入特征的分类贡献为"
        "[[MATH:φ_j^(cls)(f)=(x_j-x_j^0)(∂z_(k̂)/∂x_j)]]，原型距离贡献为"
        "[[MATH:φ_j^(pro)(f)=(x_j-x_j^0)(∂d_f/∂x_j)]]。"
        "对两类贡献的绝对值分别归一化后，计算"
        "[[MATH:a_j(f)=λφ̄_j^(cls)(f)+(1-λ)φ̄_j^(pro)(f)]]。"
        "按[[MATH:a_j(f)]]降序排列并保留前[[MATH:M=10]]项，得到[[MATH:C_f]]。"
        "若某一分支贡献绝对值之和为0，则该分支的归一化贡献取0。"
    ),
    "M030": (
        "[标记事项030/154：C_f与高贡献项的关系] 令[[MATH:I_M]]表示综合贡献分数[[MATH:a_j(f)]]最大的前M个特征索引，"
        "则[[MATH:C_f={c_j∣j∈I_M}]]。每个元素"
        "[[MATH:c_j=(id_j,name_j,x_j,φ_j^(cls),φ_j^(pro),a_j,dir_j)]]"
        "记录特征编号、名称、取值、分类贡献、原型距离贡献、综合贡献和贡献方向。"
        "因此，贡献较高的特征项就是构成[[MATH:C_f]]的前M个元素；[[MATH:C_f]]是这些特征项的结构化集合。"
        "异常包长分布、上行字节突增、连接周期性增强或罕见可见TLS指纹，仅在进入前M项时才写入[[MATH:C_f]]。"
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    specs = json.loads(args.source.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in specs}
    if len(specs) != 180 or len(by_id) != 180:
        raise RuntimeError("Expected 180 unique comment specifications.")

    before_counts = {cid: len(MATH_RE.findall(by_id[cid]["text"])) for cid in OVERRIDES}
    for cid, text in OVERRIDES.items():
        if cid not in by_id:
            raise RuntimeError(f"Missing specification {cid}.")
        if text.count("[[MATH:") != len(MATH_RE.findall(text)):
            raise RuntimeError(f"Unclosed math marker in {cid}.")
        if "]]]" in text:
            raise RuntimeError(f"Ambiguous math marker terminator in {cid}.")
        by_id[cid]["text"] = text

    args.target.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
    formula_count = sum(len(MATH_RE.findall(item["text"])) for item in specs)
    report = {
        "comment_count": len(specs),
        "updated_ids": sorted(OVERRIDES),
        "formula_count": formula_count,
        "formula_counts_before": before_counts,
        "formula_counts_after": {cid: len(MATH_RE.findall(by_id[cid]["text"])) for cid in OVERRIDES},
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
