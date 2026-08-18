# A01--A10 算法证据三路只读访问审计

## 结论

2026-08-13 对十个算法候选执行了本机直连 GPU、经物理机探测 GPU、搜索本地及
物理机镜像三条只读路径。三条路径均未取得 A01--A10 原始证据文件的 size、SHA-256
和完整 schema，因此不能把已有的 A09/A10 决赛比较提升为全十候选最优性证明。
机器可读回执为 `2026-08-13-algorithm-evidence-access-three-route.json`。

## 路径一：本机直连 GPU 映射端口

`10.0.5.103:25696` 的 TCP 检查在 47.918 秒后返回 false；随后使用已冻结私钥、
`BatchMode=yes`、`IdentitiesOnly=yes`、`ClearAllForwardings=yes` 的 SSH 尝试超时，
退出码 124。未建立 SSH 会话，也没有读取任何候选文件。

## 路径二：经物理机访问

本机可正常登录 `10.0.5.8:22`。物理机到 `10.0.5.103:25696` 返回
`Connection refused`，到 `10.0.5.103:22` 在 0.01 秒内建立 TCP，但内部 22 的
ED25519 指纹为 `dtu+aVwQ+123SU8Qm6okbQMCdyZkSJN2az9GdxqEEsA`，与已信任的外部
25696 指纹 `ptg8SMNQvUQYHV0/hafU4hBlhZ/vb4wJUmM1XTVlROI` 不同，故不能把内部
22 当作原 GPU SSH 端点。物理机现有密钥及本机密钥经代理均被内部 22 以
`Permission denied (publickey)` 拒绝；未使用密码、未绕过主机身份检查。

物理机没有 `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/results`，也没有
`/home/wangwt/phase_2/code/HFT-MGBS/results`。在 HFT 代码目录与 replay 目录中没有
发现路径含 `HFT_G*` 的结果文件，仅有三个配置文件保留 GPU 结果路径字符串。物理机
同步的 `algorithm_search_rc1.json` 与本地 SHA 相同，但仍只有 A09/A10 两组
`mode_metrics`，十个候选的 `evidence_sha256` 数量为零。

## 路径三：本地与已有归档

工作区精确搜索只找到配置中的远端路径引用，没有找到任何 A01--A10 结果镜像。
检查小型同步归档 `.hft-gpu-sync-25150.tgz`，内容只有代码、配置、测试和文档，不含
结果摘要、数据或模型。

## 当前证据边界

A09/A10 的 schema 2 确认性摘要指标是在本次端口故障前通过只读 GPU 会话取得，故可
重算二者严格前沿 `[A09,A10]` 和 practical winner `A09`；但两份摘要的原始字节
size/SHA 尚未冻结。A01--A08 既没有成对 normal/fallback 指标，也没有 size/SHA。
所以当前必须保持：

- `algorithm_only_practical_optimum_proven=false`；
- `production_joint_optimum_proven=false`；
- `final_pareto_ingestion_allowed=false`。

恢复 GPU 映射 SSH 后，只需在远端原地计算十份文件的 `stat`、`sha256sum` 和小型 JSON
字段摘要；不需要、也不允许把数据集、模型或大型结果复制到本地。若 A01--A08 的旧
screening 文件不是同一合同下 normal/fallback 各三重复，则必须按冻结确认性协议重跑，
不能用单次 screening 指标补写最优性证据。
