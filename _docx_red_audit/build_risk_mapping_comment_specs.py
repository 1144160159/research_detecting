from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")


M032_TEXT = (
    "[标记事项032/154：等级映射表生成及替换文本] "
    "风险等级到数值风险的转换属于告警标准化和概率校准的常规技术，不作为本发明的主要创新点。"
    "但正文需要公开映射表的生成依据、版本范围和具体转换步骤。建议将第二段中从“对于不同检测器分数区间不一致的问题”开始，"
    "至“若某检测器仅输出等级，则根据等级映射表转换为数值风险”结束的内容整体替换为以下文字：\n"
    "对于不同检测器分数区间不一致的问题，系统将检测器输出统一转换为满足[[MATH:0≤r_a≤1]]的风险值[[MATH:r_a]]。"
    "对于输出连续分数[[MATH:s]]的检测器，读取该检测器规定的最小分数[[MATH:s_min]]和最大分数[[MATH:s_max]]，并计算"
    "[[MATH:r_a=min(1,max(0,(s-s_min)/(s_max-s_min)))]]。当[[MATH:s_max=s_min]]时，不执行线性归一化，而将该检测器标记为校准参数无效。\n"
    "对于仅输出低风险、中风险、高风险或严重风险等离散等级的检测器，系统针对检测器标识和检测器版本建立版本化等级映射表"
    "[[MATH:M_g=(detector_id,detector_version,g,r_g,calibration_version)]]。"
    "其中[[MATH:g]]为原始风险等级，[[MATH:r_g]]为该等级对应的统一风险值，calibration_version为映射表版本。"
    "不同检测器或者同一检测器的不同版本分别建立映射表，不共用等级风险值。\n"
    "等级映射表仅使用训练集或验证集中带有正常、恶意标签的样本生成。对于等级[[MATH:g]]，统计该等级下的恶意样本数"
    "[[MATH:n_g^+]]和正常样本数[[MATH:n_g^-]]，并计算"
    "[[MATH:r_g=(n_g^++α)/(n_g^++n_g^-+2α)]]。其中[[MATH:α=1]]为平滑参数，用于避免样本较少时风险值直接取0或1。"
    "系统按照风险等级顺序检查映射结果，使其满足"
    "[[MATH:r_low≤r_medium≤r_high≤r_critical]]；若相邻等级不满足该顺序，则按照对应样本数量对相邻等级风险值进行加权合并，直至风险值单调不降低。\n"
    "例如，某检测器验证集中低风险等级包含50个恶意样本和950个正常样本，中风险等级包含160个恶意样本和240个正常样本，"
    "高风险等级包含150个恶意样本和50个正常样本，严重风险等级包含92个恶意样本和8个正常样本。"
    "取[[MATH:α=1]]并按上述公式计算后，可形成“低风险0.05、中风险0.40、高风险0.75、严重风险0.91”的映射表。"
    "当检测器输出“高风险”时，系统根据检测器标识、检测器版本、原始等级和映射表版本查询得到[[MATH:r_a=0.75]]。\n"
    "实际转换时，系统读取detector_id、detector_version、grade和calibration_version，并执行"
    "[[MATH:r_a=M(detector_id,detector_version,grade,calibration_version)]]。"
    "转换结果同时保留原始等级、统一风险值和映射表版本。若原始等级未登记、检测器版本不匹配或者对应等级的验证样本数低于最低校准数量，"
    "则将告警标记为“等级映射缺失”或“校准不足”，保留原始等级并进入输入不完整处理路径，不使用固定默认值替代。"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    specs = json.loads(args.source.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in specs}
    if len(specs) != 180 or "M032" not in by_id:
        raise RuntimeError("Expected 180 specifications including M032.")
    if M032_TEXT.count("[[MATH:") != len(MATH_RE.findall(M032_TEXT)) or "]]]" in M032_TEXT:
        raise RuntimeError("Invalid math placeholder syntax in M032.")

    before = len(MATH_RE.findall(by_id["M032"]["text"]))
    by_id["M032"]["text"] = M032_TEXT
    args.target.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "comment_count": len(specs),
        "updated_id": "M032",
        "m032_formula_count_before": before,
        "m032_formula_count_after": len(MATH_RE.findall(M032_TEXT)),
        "formula_count": sum(len(MATH_RE.findall(item["text"])) for item in specs),
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
