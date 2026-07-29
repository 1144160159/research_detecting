# Pairwise-OpenDetect 失败集中度与自有算法决策

## 证据来源与边界

输入为已完成的三新种子 `137/139/149`、102 场景 Pairwise-OpenDetect 外部确认汇总。每个场景先平均三个种子，再计算候选相对 OpenDetect 的有向增益。以下“严重场景”是结果后的诊断标签：四项指标至少三项回退，或任一指标有向增益不高于 `-0.1`。该标签只用于决定后续研究方向，不能用于修改已冻结 LCB 试点或回写主结果。

## 失败集中度

| 指标 | 总体有向增益 | 回退场景 | 灾难性回退 | 最差 5 场景占负收益质量 |
|---|---:|---:|---:|---:|
| AUROC | +0.057252 | 36 | 9 | 50.6% |
| AUPR | +0.072720 | 26 | 7 | 53.8% |
| FPR95 | +0.041876 | 47 | 21 | 40.9% |
| OSCR | +0.049214 | 30 | 12 | 51.6% |

最严重的联合失败包括 `cicids2017/web_xss`、`ustc_tfc2016/tinba`、`cic_ton_iot/mitm`、`cic_ton_iot/ddos`、`cicids2017/web_bruteforce`、`cic_iot2023/mirai_udpplain`、`edge_iiot/backdoor` 和 `cic_iot2023/ddos_udp_flood`。这些场景不是单一套件或单一攻击大类，因此不能用一个基于测试套件名称的路由解释或修复。

## 对 LCB 探索的含义

严重场景共 `35` 个，冻结 LCB 14 场景试点覆盖其中 `7` 个，覆盖率 `20.0%`。覆盖项包含 `web_xss`、`web_bruteforce`、`tinba`、`ddos_udp_flood` 等关键失败，足以检验保守尾部学习能否缓解最显著的尾部问题，但不足以证明覆盖全部外部失败。

因此执行规则保持：

1. 先运行冻结 LCB 试点，不在结果前增加第二个尾部分数候选。
2. LCB 未过门则保留 Pairwise，记录“已知伪未知证据不能可靠预测真实未知尾部”。
3. LCB 过门也只允许进入预留三新种子确认，不直接替换 incumbent。
4. 若确认后未覆盖严重场景仍主导回退，下一候选优先研究表示层或 known-only 安全路由，不再叠加全局分数。
5. Mal_TLS2023 异构编码器承担表示层假设的第一项试验；其结果早于任何新表示层候选扩展。

可复现诊断位于 GPU 项目 `source/CAEOS-EMTD/results/strict_v4_external_failure_concentration/`，生成脚本为 `analyze_external_failure_concentration.py`，相关测试 `2/2 PASS`；本地 `source` 不保存结果副本。
