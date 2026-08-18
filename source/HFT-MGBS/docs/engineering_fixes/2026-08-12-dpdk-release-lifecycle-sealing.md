# DPDK 发布门生命周期、资源口径与证据封存加固

## 问题现象

2026-07-31 的 release gate v2 已把数据面、资源、恢复和证据拆层，但终审仍发现以下
发布阻断：TX worker panic 可能使 RX 永久等待；runner 没有硬超时；清理期间第二次信号
可能中断回绑；策略规则只识别 `iifname/oifname`；HugePage 只统计 node1 却声称全局；
接口只恢复部分字段；最终 acceptance 在证据哈希之前生成且没有完整绑定所有退出状态。

## 工程修复

- Rust `TxCompletionGuard` 在正常返回和 panic 展开时均递减 TX worker 计数，最后一个
  worker 必须发布 `done=true`；独立 watchdog 覆盖 setup、ready 和 shutdown 生命周期。
- runner 使用 `timeout --signal=TERM --kill-after=5s` 限制 DPDK 子进程总寿命；清理开始后
  只移除 EXIT trap，并忽略第二个 HUP/INT/TERM，先完成 PF、HugePage 和运行目录恢复。
- 策略路由同时识别 iproute2 JSON 的 `iif/oif` 与兼容字段
  `iifname/oifname`。
- HugePage schema 升至 v2：遍历所有 NUMA node 的 2 MiB 计数，要求运行前全局为 0、
  运行中只有冻结的目标 node 增加，恢复后逐 node 与运行前完全一致。
- 冻结专用接口基线：UP、MTU 1500、txqlen 1000，以及 features、coalesce、ring、
  channels、qdisc 的规范化 SHA-256。解绑前必须匹配；回绑后除动态 stats 外，完整快照
  逐项一致，否则恢复门失败。
- runner、validator、最终验收组合器、CPU 预检、DPDK/NIC 预检和 DPDK 构建清单均由
  release 配置 SHA-256 绑定。二进制仍采用“远端构建后再冻结”的两阶段流程。
- `compose_dpdk_run_acceptance.py` 绑定原始退出、validator、恢复、证据、base/complete
  哈希检查状态。封存清单先生成并核验，acceptance 随后作为派生回执生成；回执明确
  `standalone_receipt_trusted=false`，不能脱离其绑定的清单独立采信。

## 本地验证

- `python -m unittest discover -s tests -p 'test_dpdk*.py' -v`：初始 30 项通过；证据空数组
  回归修复后为 31 项通过。
- validator、composer、CPU preflight、DPDK preflight 均通过 `py_compile`。
- `scripts/check_local_policy.py`：0 violations。
- 物理机 release 构建、fmt、12 项 Rust 测试、clippy `-D warnings` 均通过；二进制已冻结为
  `3c655ef3684f8157e52d12a89157a6c1c5f0d586fe493d610b60a2fc796ec0a6`，
  `binary_freeze_pending=false`。
- non-mutating preflight 已在不修改 PF 的条件下通过过一次；正式运行期间暴露并修复了
  证据空数组/错误退出码问题，详见独立修复记录。

## 性能影响

热路径新增逻辑仅是 Rust worker 生命周期原子计数/看门狗；接口哈希、全 NUMA 计数、
快照比较和 acceptance 组合均在运行前后，不进入逐包路径。实际性能影响必须由新 Q1
实机运行测量，不能从本地合同测试推断。故障前一次诊断运行的数据面、资源与恢复门均
通过，但证据封存失败，因此只作诊断、不作发布验收。

## 回退与失败边界

- 如预检发现接口基线、CPU 空闲度、地址/路由、策略规则、XDP 占用、HugePage 所有权或
  文件哈希不一致，必须在 PF 解绑前退出。
- 如恢复、证据或 validator 任一失败，`runner_qualified` 和
  `r0_capture_only_qualified` 均为 false。
- 当前修复后的正式重跑被生产物理机 CPU 空闲预检阻断；没有完整 acceptance，所以
  `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false` 不变。
