# XDP 负载边界受控实验

## 目标

在多队列 idle poll 修复后，确定当前 XDP/A09 分布式链路能够同时满足零
抓包丢包、P99/P999、解析、关键流覆盖和资源硬门的最高已验证诊断负载。

## 候选预算与冻结变量

- 候选严格限定为 3 个：0.02、0.03、0.04 Mpps；
- 已知区间端点：0.01 Mpps 三重复测通过，0.05 Mpps 修复后 P99
  30,449 us 失败；
- 固定驱动 `xdp-skb`、receive batch=64、8 个 RX 队列；
- 固定 FTP-EXP1 PCAP、15 秒、A09、GPU batch=128、flush=1000 us、
  timeout=150 ms；
- 硬门：capture drop=0、P99<=10 ms、P999<=50 ms、关键流覆盖>=0.99、
  parse reject<=0.001，并沿用冻结资源门。

## 选择规则

只有通过全部硬门的候选才进入 Pareto；从中选择 target Mpps 最高者，若
相同再比较 observed Mpps 和 P99。未通过硬门的吞吐不计入选择。最高通过
候选还必须完成三重复验，且仍仅为 diagnostic-only。

## 结果

待实验完成后追加运行目录、SHA-256、候选表、Pareto 和后续动作。
