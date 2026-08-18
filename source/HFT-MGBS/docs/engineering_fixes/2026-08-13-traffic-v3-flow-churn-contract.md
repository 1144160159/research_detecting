# Traffic-v3 flow-churn 独立合同与前置阻断

## 目的与边界

本文件记录 traffic-v3 的单变量合同/TDD。它不修改已冻结的 UDP fastpath Rust 源或正式 binary，不替换现有可运行 runner，也未进行网卡实验。独立 runner 为 `run_current_hardware_279_tpacket_traffic_v3_contract.sh`，独立 config 为 `current_hardware_2_79_tpacket_traffic_v3_contract.json`。两项 P0 前置条件未解除前，runner 在创建 evidence directory 或进行任何主机变更前以 RC86 fail closed。

## R3 真实证据与停止 direct-map 的原因

`udp_fastpath_capacity_r3` 的 NIC discard 为 10,796，集中于 queue 0/5；18 个完整窗最低 2.624822 Mpps，最后三个活动窗连续降至约 2.637/2.625/2.625 Mpps；八个 pktgen 线程结束时实测速率合计约 2.779 Mpps。恢复台账和 evidence manifest 全绿，但该轮不满足吞吐及零丢包门。

八个 worker 仍各消耗约 20.8--20.9 CPU s/21 s。UDP local update 微基准约 60 ns/packet，现场完整 worker 约 2.86 us/packet；即使完全消除 update，Amdahl 上限约 2.1%。因此 direct-map/raw-entry 候选停止，不再用较高语义风险换取低上限收益。

## Traffic-v3 唯一变量与样本率预期

QM 运行时证据已证明现有五元组空间不重叠：每队列固定不同 source IP 与 UDP source port，每队列 145 个 distinct flow，全局 1,160，跨 worker collision=0。该证据也证明本机 Linux 5.10 pktgen 对 `.1`--`.145` 的实际行为为 inclusive，而非先前推断的 exclusive。

Traffic-v3 保留 64 B、8 queues、145 flows/queue、inclusive destination range、每队列唯一 source IP/UDP source、UDP dst 53、FLOW_SEQ、clone_skb 64、burst 8 和约 2.79 Mpps 发生器配置；唯一流量变量是把 `flowlen` 从 36 改为 1。重访周期从约 `145×36×64=334,080` packets/queue 缩短至 `145×1×64=9,280` packets/queue。按现场约 350 kpps/queue 估算每 26.5 ms 重访一轮；active timeout 1 s 的扫描预期关闭约 145 flows/queue/s，即全局约 1,160 flow receipts/s。该值是待实跑验证的预期，不是合格结果。

## Params、Current 与真实逐窗 receipt 门

发流前必须严格回读全部八个 pktgen Params 与 Current：145 flows、flowlen 1、inclusive `.1`--`.145`、唯一 source IP/UDP source、UDP dst 53、固定 queue map、packets=0、errors=0。结束后再次解析 Current，要求 packets>0、errors=0，source/destination/UDP ports/queue 均保持在冻结身份与范围内。

聚合 closed-flow density 门继续存在，但不能替代逐窗证明。runner 从 raw `LatencySampleReceipt.window_id` 重算完整窗口，去掉 `epoch_second_counts` 的首尾边缘窗。每个完整窗必须满足：

- `flow_materialization_to_feature_enqueue` >= 1000；
- `kernel_receive_to_feature_enqueue` >= 1000；
- `flow_kernel_receive_to_remote_score_end_to_end` >= 1000；
- `gpu_batch_round_trip` >= 100。

所有 receipt source ID 必须唯一且不得截断。禁止复制 GPU batch receipt、展开 batch 为伪 per-flow 样本或制造重复 source ID。结果落入 `per_window_latency_receipt_gate.json`，任一完整窗不足即非零退出。

## P0 阻断及风险

当前冻结 binary 没有相关的 per-flow kernel-receive-to-remote-score end-to-end receipt，不能以 GPU batch RTT 冒充。R3 同时证明 generator 尾段降到约 2.625 Mpps 的活动窗、结束汇总约 2.779 Mpps；traffic-v3 会把 flow closure/GPU 工作提升约十倍，更可能恶化吞吐。

因此 config 固定两个不可授权绕过的 blocker：先独立重新证明 generator 尾段持续 >=2.79 Mpps；再实现并验证真实、可关联、每 flow 一条的 end-to-end receipt。解除 blocker 必须形成新代码、测试、证据及重新冻结的 runner/config SHA。本合同目前只能运行静态/负测试，不得执行正式网卡。

