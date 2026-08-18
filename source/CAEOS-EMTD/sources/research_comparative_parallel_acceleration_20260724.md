# Pairwise-OpenDetect comparative-chain parallel acceleration

更新时间：2026-07-24

## 瓶颈证据

2026-07-24 07:03 UTC，GPU服务器有80个CPU核、503 GiB内存、约481 GiB可用内存，RTX A6000空闲。原 `run_strict_v4_comparative_corruption.py` 仅串行运行一个source pair，活动capture约占4个CPU核和7.6 GiB内存。运行约5小时后只完成26/306 source pairs，按原速度仍需超过两天。

比较污染不是效率benchmark。每个结果块的模型输入、训练参数、runtime equivalence、污染生成、六指标和canonical identity均由冻结v2 protocol、capture实现和evaluator约束；调度顺序不进入指标公式。因此允许增加一个不改变协议语义的外部调度层，但必须继续调用原实现并通过原block验证。

## 加速器契约

新增 `accelerate_strict_v4_comparative_corruption.py`：

- 只接受canonical `strict_v4_comparative_corruption_protocol_v2`；
- 每次启动复核原trainer/runtime/capture/evaluator/runner SHA；
- 从source registry末端反向选任务；
- 启动时和每项执行前复核连续串行前沿；
- `minimum_source_index` 必须保留冻结的frontier gap；
- 每个source index使用独立原子claim目录；
- 发现未被claim的部分目录时失败关闭；
- 训练命令只替换 `--output-dir`，其余参数来自冻结provenance；
- comparator仍固定CPU、`1e-12`容差和same-device shadow；
- evaluator仍为原v2 evaluator；
- 每个结果必须通过原 `strict_v4_comparative_corruption_block_v1` canonical、source identity、split fingerprint、五污染族、输入相等和无未知拟合门；
- 不写 `execution_complete`，不生成比较summary，不改变最终统计门。

实现SHA：

- accelerator：`d7bd83eb7683a5e5ed2c30407d2536895f32e9aad53fe3c5f28f407da3f6dfa3`
- accelerator test：`870d2bc61b700649ab739e641c4af21d7da1459b88c6ccfe99499c74d4d19913`

## 两任务真实试点

试点 `pilot_reverse_304_305_20260724T0705Z` 使用2 workers，只处理source indices 305/304：

- USTC-TFC2016 / Zeus / seed149
- USTC-TFC2016 / Zeus / seed139

两项距当时串行前沿超过270项，目录不重合。约3分钟后均由原evaluator完成：

- index305 block canonical：
  `02f179fd187732b9d555b1588f6e7cd58f2616cfb208035129f7404cfe80199d`
- index304 block canonical：
  `63758ccc2a5a289b076164a6a69822e1f4ba7ec1dfe11c3d50566c630cdbb936`
- pilot manifest canonical/file：
  `6962f398801df0c81118dcc4f37c29eec03b9924f41606f1bbddda097c8b5304`
  / `a66e7d16ec98f3ddbdb80b4033590cee9e684863a879340672c0327225184acb`
- pilot summary canonical/file：
  `893c6412395b764882eecbd22ccd3efd53f972646a4fda74f50a937f593c25b4`
  / `26299df0401a626a153c58ea99d667d256f8a13be59d10b510a865ed92307e15`
- failure：0

## 受控扩展与负载纠偏

正式加速run为 `reverse64_w10_20260724T0715Z`：

- v2 protocol canonical/file：
  `ef9461fd25d383cc2a509da8ce85868f1936607402302e2d7d55d53e444cd8cf`
  / `96af30d4746f664ae8859f550bf5b45612cefa20951c407c305d0a68a39a9629`
- run manifest canonical/file：
  `a3917d94e157d8c16a154197fba8f1e40c197c66d0dbb4694bbb4af92e01e74c`
  / `f0a2bc9fa366a8a98c7e69a7c10a3c3f4ae9aad428795ec68da679f4763bfad5`
- 启动连续前沿：27
- 最小source index：64
- 最小frontier gap：32
- 选择240项：indices 303..64，已完成的304/305不重复选择
- accelerator PID：`3644689`

初始10个active workers使1分钟load峰值达到112.89/80核。为避免过度排队，暂停其中6个本轮创建的capture子进程，保留claim和内存状态，不删除、不重算输出；有效active workers降为4后1分钟load降至28.14，结果继续产生。

新增自动恢复守护器。当四个活动槽处理完剩余队列、父进程只剩6个暂停子进程时，才核验父子PID和stop状态并发送SIGCONT；结果写入同一run目录的canonical throttle record。

- monitor SHA：
  `9c06b8e570789e218492238244c691781063953c535d37f6c7c6b02b88b19d79`
- monitor test SHA：
  `e94648f86c6aecf07d6e8166c0f2708c34993ae7ac716e7caf9ded4eee4b7336`
- monitor PID：`4151738`
- 当前throttle resume record：0，表示仍在处理主队列

## 当前进度与边界

2026-07-24 07:39 UTC：

- 总paired blocks：48/306
- 总conditions：240/1530
- capture manifests：96
- 连续串行前沿：28
- 反向加速新增完成：20（pilot 2 + active run 18）
- active run failures：0
- active run summary：0
- 比较总summary：0
- MDR/MEDAF仍等待比较summary

本地新增调度/恢复测试为 `7/7 + 3/3 PASS`；GPU与原比较回归合并为 `18/18 PASS`。调度提速不构成算法效果：在306/306、1530/1530、正式summary和统计门完成前，不能声明Pairwise相对OpenDetect鲁棒性通过，也不能声明全面SOTA或最终自有算法成立。
