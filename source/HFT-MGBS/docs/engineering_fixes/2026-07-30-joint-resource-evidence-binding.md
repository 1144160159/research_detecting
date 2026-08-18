# XDP 与跨主机资源证据时间绑定修复

## 问题现象

原有 XDP 稳定性汇总只包含物理机进程 RSS，GPU 节点资源证据来自较早
的独立采样，不能证明采样窗口覆盖同一批 XDP 流量。首次新增绑定器时，
又把 `diagnostic_accepted` 和 `capture_packets_dropped` 映射到错误层级，
导致三组有效证据被失败关闭。

## 根因

物理和 GPU 两台主机没有共同的 campaign 绑定层；live evidence 的诊断
状态位于 `composition.diagnostic_accepted`，而抓包丢包位于
`metrics.json` 顶层，初版绑定器按不存在的字段读取。

## 修改范围

- 新增 `summarize_xdp_joint_resources.py`，按一对一运行顺序绑定三组物理
  与 GPU 资源文件。
- 用 UTC 开始/结束时间计算真实采样重叠，默认每组至少 12 秒。
- 同时校验 `xdp-skb`、三项退出码、诊断通过、零抓包丢包、A09、
  `thread_all` 和 GPU 资源门。
- 修正字段映射，并新增单元测试。
- 明确区分 `diagnostic_resource_evidence_complete=true` 与
  `production_resource_evidence_complete=false`。

## 验证证据

远端单元测试 1 项通过。三组运行的采样重叠分别为 14.569、14.115、
14.677 秒，绑定汇总通过，SHA-256 为
`8935a0f46403302a2cfaf86cc220650bfe8a64ebf78a568aeaaea3d167864df7`，
路径为
`/home/wangwt/task/datasets/replay/hft_xdp_skb_joint_resource_v1_20260730/joint_summary.json`。

全量同步时发现测试夹具生成的 `08:00:17.00+00:00` 可由物理机较新
Python 解析，但 GPU 的 Python 3.9 拒绝。夹具已改为由带 UTC 时区的
`datetime.isoformat()` 生成标准格式；真实资源文件原本就是标准六位微秒
格式，实验结论未改变。

## 性能影响与回退

绑定器只离线读取 JSON 和 `/usr/bin/time` 文本，不进入实时数据面。若
运行数量、字段、哈希、身份或时间重叠不满足要求，则失败关闭并继续沿用
未绑定状态，不能补写“资源已验证”。

## 遗留风险

三组仍是 0.01 Mpps、15 秒诊断负载；系统 GPU 有其他进程干扰。正式
目标负载和 24/72 小时长稳前，只能作为诊断资源证据，不能进入最终
生产 Pareto。
