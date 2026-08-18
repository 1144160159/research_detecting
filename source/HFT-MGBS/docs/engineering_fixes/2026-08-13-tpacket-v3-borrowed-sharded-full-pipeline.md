# TPACKET_V3 借用式分片完整流水线入口

## 背景与边界

此前 2.794217 Mpps 来自 tpacket_v3_fastpath_probe，只读取和计数 mmap 帧。
正式 hft-capture 主程序没有 TPACKET_V3 入口，且 XDP/AF_PACKET trait 路径会把
每帧复制到 owned Vec，所以该结果不能证明 capture→parse→flow→feature→budget→GPU
完整流水线。本修复保留原主程序，新增独立 Linux 二进制
tpacket_v3_full_pipeline，用于后续生产验收原始证据。

## 实现

src/tpacket_v3.rs 是 HFT 自有公共模块，不修改
traffic-analysis-platform/rust：

- 每个 worker 独占 AF_PACKET socket、TPACKET_V3 mmap ring 和 cursor；
- PACKET_FANOUT 默认 HASH，确保同一五元组进入同一 worker 的独立
  HftFlowTable；QM 只有显式声明已验证 queue-to-flow affinity 才允许；
- 使用高阶生命周期回调借用 mmap frame，PacketParser::parse 和
  HftFlowTable::update_into 在 block 归还内核前完成，包数据不跨线程；
- block 状态先通过 raw pointer/volatile 读取，Acquire 后再以
  read_unaligned 复制 UAPI header；所有 offset 均限制在 blk_len；
- RAII BlockLease 在成功、回调错误和 unwind 时都执行 Release fence、写回
  TP_STATUS_KERNEL 并推进 cursor；
- 自动 fanout ID 由时间、PID 混合生成，并按 network namespace 在
  /run/lock 以 create_new 排他预留；显式 ID 还要求
  --allow-explicit-fanout-id，锁冲突失败关闭。

src/bin/tpacket_v3_full_pipeline.rs 固定八个 capture worker，worker CPU 唯一，
scheduler CPU 不得重叠。每 worker 拥有独立 flow table，在 mmap 借用帧内完成解析、
流更新与特征素材积累；只有闭流对象进入有界 crossbeam feature channel。单独的
scheduler/dispatcher 线程执行预算排序、深特征计算、GPU batch 与现有 circuit breaker。

`--worker-cpus` 由 clap 按 8 个独立值解析，正确写法为
`--worker-cpus 37 38 39 40 41 42 43 44`；不得写成逗号分隔的单个参数。

## 背压、计数与退出

- feature channel 与 GPU channel 都是有界队列；Full/Disconnected 不阻塞抓包，
  并分别计入 feature_queue_drops、key_feature_queue_drops、fallback 和关键流失败；
- 每 worker 保存 packet/byte/block/parsed/rejected/closed/submitted/drop、逐秒窗口、
  稀疏 parse+flow 时延和线程 CPU；
- PACKET_STATISTICS 是 destructive read，因此测量前先清零，此后每秒和结束时读取，
  将 u32 delta 累加成 u64 并保存每个原始窗口，避免长跑回绕；
- socket bind 后、正式窗口前持续 drain backlog，启动前积压和 drop 不混入正式窗口；
- worker 先绑核并通过 setup channel 回报，主线程收齐结果后才发布 start gate；
  绑核失败不会卡在固定 Barrier；
- SIGINT/SIGTERM 只设置原子终止标志，worker 归还当前 block、flush flow、读取最终
  socket stats，关闭 channel；scheduler 排空输入并调用 GpuDispatcher::finish 后 join；
- GPU 默认必须在采集前 ready。只读诊断可显式允许 unready，但
  raw_full_pipeline_observation 仍为 false。

## 严格资格

该二进制只写 hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw 原始结果。
代码固定：

- runtime_identity_verified=false
- full_pipeline_qualified=false
- final_pareto_ingestion_allowed=false

因此单次执行、编译通过或吞吐值都不能自行晋升为完整闭环。正式 runner/validator
仍须绑定二进制和输入 SHA，并以三次同配置运行验证 2.79 Mpps、零 socket/internal
drop、P99/P999、资源、关键流 completion、GPU 身份及回退恢复。

## 验证

在物理机 /tmp/hft_capture_hotpath_20260813T030627279Z 隔离副本执行 cargo fmt、
release tests 和 release build。公共模块 17 项和新 bin 4 项测试全部通过，release
build 通过。测试覆盖 borrowed frame 指针、畸形 block 边界、RAII block 归还、
fanout UAPI 值、有界队列 Full/Disconnected、关键流失败计数、完整秒边界以及显式
fanout 冲突授权门。未运行正式网卡实验，也未覆盖物理机正式 HFT 目录。
