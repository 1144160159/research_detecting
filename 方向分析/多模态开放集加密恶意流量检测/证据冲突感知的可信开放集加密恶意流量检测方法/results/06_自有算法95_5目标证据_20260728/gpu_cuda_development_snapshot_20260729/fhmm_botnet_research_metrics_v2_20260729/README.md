# FHMM Botnet研究指标v2证据

日期：2026-07-29

## 来源与边界

- 远端项目：`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717`
- 原任务：`runs/strict_v4_family_heldout_meta_botnet_pilot_v1/unknown_botnet_seed29`与`unknown_botnet_seed31`
- 复算器：`evaluate_strict_v4_family_heldout_meta_pilot_v2.py`
- 指标实现：`strict_v4_open_set_metric_contract_v2.py`
- 复算只读取既有冻结分数，不训练、不调阈值、不选择候选。
- v1操作指标、扩展门和阴性结论保持不变。
- 当前分数缓存没有K类概率矩阵，因此Known-ECE/Brier/NLL为unavailable，不作推断。
- 当前known拆分为`flow_id`哈希分层，不是capture-grouped；全部结果仅为开发证据。

## 研究指标

unknown固定为正类，风险越大越未知。`FPR_known@95TPR_unknown`不是Benign FPR。

| Seed | Known Macro-F1 | Balanced Acc | AUROC-Out | AUPR-Out | FPR_known@95TPR_unknown | exact OSCR v2 | Unknown-F1 | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 29 | 0.882837 | 0.950146 | 0.928259 | 0.675661 | 0.122090 | 0.920959 | 0.400000 | 0.962118 | 0.283740 |
| 31 | 0.943113 | 0.957424 | 0.890607 | 0.667603 | 0.388407 | 0.884136 | 0.353791 | 0.968508 | 0.239024 |
| 两种子均值 | 0.912975 | 0.953785 | 0.909433 | 0.671632 | 0.255249 | 0.902548 | 0.376895 | 0.965313 | 0.261382 |

## 解释

seed31的操作告警显著好于seed29，但AUROC-Out、FPR95、OSCR和Unknown-F1反而更差。该结果直接证明闭集/告警性能不能替代未知拒识性能，也说明当前FHMM的未知排序与最终告警头尚未稳定协同。

两种子研究指标不能用于选择新阈值或回改risk formula。下一机制必须在结果产生前冻结，并重新执行Botnet资格试验；未通过两种子绝对门时不得扩展到七家族。

## 文件校验

| 文件 | SHA-256 |
|---|---|
| `research_evaluation_seed29.json` | `485d121f60d7937fd4609780bb4bb576756bd14b23ed02f6d34985f61b8f28eb` |
| `research_evaluation_seed31.json` | `5abc99a2be0612122f9b4b0327f97254182e566e60f875b7c035dee61a0c3c22` |

远端与本地逐文件SHA一致。
