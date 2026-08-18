"""Generate the HFT-MGBS engineering and experiment progress snapshot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _fmt(value):
    if isinstance(value, float):
        return "{:.6g}".format(value)
    if value is None:
        return "未冻结"
    return str(value)


def _gate_row(name, relation, threshold, observed, evidence_scope):
    if relation == ">=":
        passed = (
            isinstance(threshold, (int, float))
            and isinstance(observed, (int, float))
            and observed >= threshold
        )
    else:
        passed = (
            isinstance(threshold, (int, float))
            and isinstance(observed, (int, float))
            and observed <= threshold
        )
    return (
        "| {} | {} {} | {} | {} | {} |".format(
            name,
            relation,
            _fmt(threshold),
            _fmt(observed),
            "通过" if passed else "未通过",
            evidence_scope,
        )
    )


def generate_markdown(search, release, generated_at):
    gates = release["frozen_non_live_gates"]
    quality = release["observed_confirmatory_lower_bounds"]
    physical = release["observed_physical_offline_confirmation"]
    recovery = release["observed_split_recovery_confirmation"]
    runtime_selection = release["observed_runtime_robust_selection"]
    virtual = release["observed_virtual_link_diagnostic"]
    split_resources = release[
        "observed_split_inference_resource_confirmation"
    ]
    capability = release["capture_capability"]
    timestamp_probe = release["observed_timestamp_driver_probe"]
    preflight = release["observed_latest_physical_live_preflight"]
    interface_readiness = release[
        "observed_final_10gbe_interface_readiness"
    ]
    xdp = release["observed_xdp_skb_diagnostic_stability"]
    capture_fallback = release[
        "observed_capture_driver_fallback_diagnostic"
    ]
    temporary_shadow = release["observed_temporary_passive_shadow"]
    runtime = release["runtime"]
    evidence = release["evidence"]
    budget = search["exploration_budget"]
    selected = search["selected_candidate"]

    rows = [
        _gate_row(
            "同域分组 Macro-F1",
            ">=",
            gates["min_grouped_macro_f1"],
            quality["grouped_macro_f1_min"],
            "新鲜确认组",
        ),
        _gate_row(
            "独立留出 Macro-F1",
            ">=",
            gates["min_independent_macro_f1"],
            quality["macro_f1_min"],
            "独立留出",
        ),
        _gate_row(
            "攻击召回率",
            ">=",
            gates["min_independent_attack_recall"],
            quality["attack_recall_min"],
            "独立留出",
        ),
        _gate_row(
            "良性召回率",
            ">=",
            gates["min_independent_benign_recall"],
            quality["benign_recall_min"],
            "独立留出",
        ),
        _gate_row(
            "AUPRC",
            ">=",
            gates["min_independent_auprc"],
            quality["auprc_min"],
            "独立留出",
        ),
        _gate_row(
            "ECE",
            "<=",
            gates["max_independent_ece"],
            quality["ece_max"],
            "独立留出",
        ),
        _gate_row(
            "事件召回率",
            ">=",
            gates["min_ground_truth_event_recall"],
            quality["ground_truth_event_recall_min"],
            "独立留出",
        ),
        _gate_row(
            "物理机离线回放丢包率",
            "<=",
            gates["max_capture_drop_rate"],
            physical["capture_drop_rate_max"],
            "三次完整 PCAP",
        ),
        _gate_row(
            "GPU 批次往返 P99(us)",
            "<=",
            gates["max_gpu_batch_p99_us"],
            physical["gpu_batch_p99_us_max"],
            "三次完整 PCAP",
        ),
        _gate_row(
            "流物化至特征入队 P99(us)",
            "<=",
            gates["max_internal_feature_enqueue_p99_us"],
            physical["feature_enqueue_p99_us_max"],
            "三次完整 PCAP，非端到端",
        ),
        _gate_row(
            "关键流覆盖率",
            ">=",
            gates["min_key_flow_coverage"],
            physical["key_flow_coverage_min"],
            "三次完整 PCAP",
        ),
        _gate_row(
            "预算超限次数",
            "<=",
            gates["max_budget_overrun_count"],
            physical["budget_overrun_count_max"],
            "三次完整 PCAP",
        ),
        _gate_row(
            "真实双机恢复时间(s)",
            "<=",
            gates["max_fallback_recovery_s"],
            recovery["recovery_to_success_s_max"],
            "三次断链恢复",
        ),
        _gate_row(
            "稳健运行时推理 P99(us)",
            "<=",
            gates["max_gpu_batch_p99_us"],
            runtime_selection["inference_batch_p99_us_max"],
            "4 候选 × 2 轮 × 3 次",
        ),
        _gate_row(
            "稳健运行时端到端 P99(us)",
            "<=",
            gates["max_diagnostic_end_to_end_p99_us"],
            runtime_selection["end_to_end_p99_us_max"],
            "虚拟链路诊断，跨轮最坏值",
        ),
        _gate_row(
            "虚拟链路分层丢包率",
            "<=",
            gates["max_capture_drop_rate"],
            virtual["pipeline_drop_rate_max"],
            "最终二进制三次严格计数对账",
        ),
        _gate_row(
            "xdp-skb 物理诊断丢包",
            "<=",
            gates["max_capture_drop_rate"],
            xdp["capture_packets_dropped_max"],
            "ens8 双口三次诊断",
        ),
        _gate_row(
            "XDP 入口至特征 P99(us)",
            "<=",
            gates["max_diagnostic_end_to_end_p99_us"],
            xdp["kernel_xdp_to_feature_p99_us_max"],
            "ens8 双口三次诊断",
        ),
        _gate_row(
            "XDP 入口至特征 P999(us)",
            "<=",
            gates["max_diagnostic_end_to_end_p999_us"],
            xdp["kernel_xdp_to_feature_p999_us_max"],
            "ens8 双口三次诊断",
        ),
        _gate_row(
            "xdp-skb 关键流覆盖率",
            ">=",
            gates["min_key_flow_coverage"],
            xdp["key_flow_coverage_min"],
            "ens8 双口三次诊断",
        ),
        _gate_row(
            "xdp-skb 同场推理 CPU 占整机",
            "<=",
            gates["resource_max"]["cpu_utilization_max"],
            xdp["inference_host_cpu_fraction_max"],
            "物理/GPU 三组时间绑定",
        ),
        _gate_row(
            "xdp-skb 同场推理内存占整机",
            "<=",
            gates["resource_max"]["memory_utilization_max"],
            xdp["inference_host_memory_fraction_max"],
            "物理/GPU 三组时间绑定",
        ),
        _gate_row(
            "XDP 至 AF_PACKET 回退恢复(ms)",
            "<=",
            gates["max_fallback_recovery_s"] * 1000,
            capture_fallback["fallback_recovery_ms_max"],
            "三次注入式运行时故障",
        ),
        _gate_row(
            "Python 服务进程树 CPU 占整机",
            "<=",
            gates["resource_max"]["cpu_utilization_max"],
            split_resources["host_cpu_fraction_max"],
            "与三次完整 PCAP 同步采样",
        ),
        _gate_row(
            "Python 服务进程树内存占整机",
            "<=",
            gates["resource_max"]["memory_utilization_max"],
            split_resources["host_memory_fraction_max"],
            "与三次完整 PCAP 同步采样",
        ),
        _gate_row(
            "A09 服务归因 GPU 利用率",
            "<=",
            gates["resource_max"]["gpu_utilization_max"],
            split_resources["service_gpu_utilization_fraction_max"],
            "PID 归因；系统 GPU 仅作背景",
        ),
    ]

    candidate = next(
        item for item in search["candidates"] if item["id"] == selected
    )
    blockers = "\n".join(
        "- `{}`".format(item) for item in preflight["blocking_errors"]
    )
    evidence_rows = [
        (
            "跨轮稳健运行时选择",
            evidence["runtime_search"],
            evidence["runtime_robust_selection_sha256"],
        ),
        (
            "最终虚拟链路诊断三轮",
            evidence["virtual_link_diagnostic"],
            evidence["virtual_link_diagnostic_sha256"],
        ),
        (
            "Python 推理节点资源三轮",
            evidence["inference_node_resource_confirmation"],
            evidence["inference_node_resource_confirmation_sha256"],
        ),
        (
            "物理机完整回放三轮",
            evidence["physical_replay_confirmation"],
            evidence["physical_replay_confirmation_sha256"],
        ),
        (
            "双机恢复三轮",
            evidence["split_recovery_confirmation"],
            evidence["split_recovery_confirmation_sha256"],
        ),
        (
            "内核接收时间戳驱动探针",
            evidence["timestamp_driver_probe"],
            evidence["timestamp_driver_probe_sha256"],
        ),
        (
            "最新 10GbE 双口预检包",
            evidence["latest_live_preflight_bundle"],
            evidence["latest_live_preflight_bundle_index_sha256"],
        ),
        (
            "最终 10GbE 双口就绪审计",
            evidence["final_10gbe_interface_readiness"],
            evidence["final_10gbe_interface_readiness_sha256"],
        ),
        (
            "xdp-skb 三轮物理诊断",
            evidence["xdp_skb_diagnostic_stability"],
            evidence["xdp_skb_diagnostic_stability_sha256"],
        ),
        (
            "xdp-skb 同场跨主机资源",
            evidence["xdp_skb_joint_resource_confirmation"],
            evidence["xdp_skb_joint_resource_confirmation_sha256"],
        ),
        (
            "xdp-skb 运行时抓包回退三轮",
            evidence["xdp_skb_capture_fallback_diagnostic"],
            evidence["xdp_skb_capture_fallback_diagnostic_sha256"],
        ),
        (
            "ens9f0 临时被动影子捕获",
            evidence["temporary_passive_shadow"],
            evidence["temporary_passive_shadow_summary_sha256"],
        ),
        (
            "ens9f0 三候选运行矩阵",
            evidence["temporary_runtime_matrix"],
            evidence["temporary_runtime_matrix_sha256"],
        ),
        (
            "旧版到新版基础特征映射",
            evidence["feature_base_mapping_comparison"],
            evidence["feature_base_mapping_comparison_sha256"],
        ),
        (
            "新版完整特征确定性",
            evidence["feature_determinism_comparison"],
            evidence["feature_determinism_comparison_sha256"],
        ),
        (
            "当前推理运行清单",
            evidence["active_runtime_manifest"],
            evidence["active_runtime_manifest_sha256"],
        ),
        (
            "远端发布审计",
            evidence["remote_release_audit"],
            evidence["remote_release_audit_sha256"],
        ),
    ]
    rendered_evidence = "\n".join(
        "| {} | `{}` | `{}` |".format(name, path, digest)
        for name, path, digest in evidence_rows
    )

    return """# HFT-MGBS 工程与实验进度

更新时间：`{generated_at}`

## 当前结论

- 离线发布候选：`{release_status}`，候选 `{selected}` 已通过非在线硬约束与双机恢复门。
- 最终 Pareto 资格：`{pareto}`。独立 10GbE 双口、xdp-skb 诊断和注入式运行时回退已通过，但生产目标负载/SLA、回退压力测试与长稳仍未完成。
- “最优”边界：算法只在冻结的 {actual} 个候选内成立；运行时只在冻结的 {runtime_candidates} 个候选、{runtime_campaigns} 轮、每候选 {runtime_repeats} 次运行内成立。两层均先过硬约束再计算 Pareto；不声称对所有可能算法全局最优，也不声称运行时搜索覆盖所有可能实现。

## 受控算法探索

- 搜索预算：最少 {minimum}、最多 {maximum}、实际 {actual} 个候选。
- 搜索维度：特征配置 {feature_count} 种、分类器族 {classifier_count} 种、阈值策略 {threshold_count} 种、自适应策略 {adaptation_count} 种。
- 严格 Pareto 前沿：`{strict_front}`；实用前沿：`{practical_front}`；最终选择：`{selected}`。
- `{selected}`：`{feature_profile} + {classifier} + {threshold_policy} + {adaptation_policy}`。
- 选择依据：{selection_reason}

## 受控运行时探索

- 总实验量：`{runtime_total}` 次（{runtime_candidates} 候选 × {runtime_campaigns} 轮 × 每轮 3 次）；任一轮失败即淘汰，聚合使用跨轮最坏值。
- 通过全部硬约束：`{runtime_passing}` 个；Pareto 前沿：`{runtime_front}`；初选 `{runtime_initial}`，当前激活 `{runtime_selected}`。激活变更未扩展候选集合，依据后续完整 PCAP 最坏值复核。
- 冻结部署：`prediction_execution={prediction_execution}`、`cpu_set={cpu_set}`、可用 CPU `{eligible_cpu_count}`、`model_n_jobs={n_jobs}`。
- 选择项跨轮最坏值：推理 P99 `{runtime_inference_p99}us`、内部 P99 `{runtime_internal_p99}us`、端到端 P99/P999 `{runtime_e2e_p99}/{runtime_e2e_p999}us`。
- 两个 inline 候选均因历史轮次越过尾延迟硬门禁被淘汰；最近一轮的更快结果不能覆盖历史失败。

## 已验证硬约束

| 约束 | 门限 | 保守观测值 | 状态 | 证据范围 |
| --- | ---: | ---: | --- | --- |
{gate_rows}

资源最坏观测：物理进程 CPU 占单核 `{physical_cpu}%`、物理主机 CPU 上界 `{physical_host_cpu}`、物理内存占比 `{physical_memory}`；与三次完整 PCAP 同步的 Python 服务进程树共采样至少 `{process_samples}` 次，最坏使用 `{python_cores}` 核、占整机 CPU `{python_cpu}`、RSS `{python_rss}` 字节、内存占比 `{python_memory}`、线程 `{python_threads}`。A09 服务在至少 `{gpu_samples}` 个 GPU 样本中无计算上下文，归因 GPU/显存占比均为 `{gpu_util}/{gpu_memory}`；系统 GPU 背景最高 `{system_gpu_background}`，不归因给 CPU ExtraTrees。这些仍不替代物理在线目标负载资源门。

## 工程实现状态

- 物理机 `10.0.5.8`：Rust 抓包、解析、多粒度特征、预算调度、反向推理传输和 Rust PCAP 批量发包器；只修改 `/home/wangwt/phase_2/code/HFT-MGBS`。
- GPU 节点 `10.0.5.103`：Python A09 推理服务；算法实际为 CPU ExtraTrees，未伪称 GPU 加速。
- RC1 运行参数：`n_jobs={n_jobs}`、`batch={batch}`、`feature_flush={feature_flush_us}us`、`timeout={timeout}ms`、`budget={budget_us}us`、`safety_ratio={safety_ratio}`。
- 正常路径：三轮各 `{packets}` 包、`{flows}` 流；评分、关键流覆盖均完整，队列满、批次失败、回退和预算超限均为 0。
- 内部流物化至特征队列入队 P99 最坏 `{feature_enqueue_p99}us`，GPU 批次往返 P99 最坏 `{gpu_batch_p99}us`；前者只证明内部排队边界，不替代 NIC/内核接收到特征入队的端到端 P99。
- `af-packet-ts` 已在隔离虚拟链路验证严格计数对账与内核 `SO_TIMESTAMPNS` 来源：三轮每次至少 `{virtual_packets}` 包、分层丢包 `{virtual_drop}`、关键流覆盖 `{virtual_coverage}`；`{timestamp_samples}` 个端到端样本的内核接收至特征入队 P99 `{timestamp_p99}us`，时间戳异常 `{timestamp_anomalies}`、实时时钟步变 `{clock_steps}`。该证据是诊断证据，不能进入最终物理 NIC Pareto。
- 两个 10GbE 口均为 `{nic_driver}`（`{nic_bus}`），`ens8f0/ens8f1` 均为 10GbE、UP、无 IP/管理桥/默认路由。bnx2x 原生 XDP 严格探测返回 EOPNOTSUPP；HFT 自有 8 队列 `xdp-skb` 三轮诊断均零丢包、关键流覆盖 1.0，最坏 kernel-XDP-entry-to-feature P99/P999 为 `{xdp_p99}/{xdp_p999}us`，GPU batch P99 `{xdp_gpu_p99}us`。
- `xdp-skb` 同场跨主机资源三轮通过：物理 RSS 最坏 `{xdp_physical_rss}` KiB，A09 推理使用 `{xdp_python_cores}` 核、RSS `{xdp_python_rss}` 字节，服务无 GPU 进程上下文。当前优先 `xdp-skb`、安全回退 `af-packet-ts`。
- 三次注入式运行中回退最坏 `{capture_fallback_recovery_ms}ms`，回退后至少继续处理 `{capture_fallback_packets}` 包；退出后 promisc=0、无残留 XDP 程序且 GRO 已恢复。切换窗口最多少收 `{capture_fallback_gap}` 包，因此该证据不复用正常路径零丢包结论，生产目标负载回退压力门仍未完成。
- 资源归因修正：一次探索采样发现整机 GPU 可被其他任务推至 100%，但 A09 服务 PID 始终无 GPU 上下文；发布硬门因此只使用服务 PID 归因值，系统 GPU 保留为背景干扰，不用整机忙碌度错误淘汰 CPU 模型。
- 恢复路径：三轮真实断链—反向重连—再次推理，最坏恢复 `{recovery_ms}ms`，门限 `{recovery_gate_ms}ms`。

## 最新在线预检

- 运行：`{preflight_run}`，结果 `accepted={preflight_accepted}`。
- 捕获口 `{capture_interface}`：carrier `{capture_carrier}`、operstate `{capture_state}`、speed `{capture_speed}` Mbps。
- 回放口 `{replay_interface}`：carrier `{replay_carrier}`、operstate `{replay_state}`、speed `{replay_speed}` Mbps。
- 捕获口 XDP metadata 时间戳能力：`{timestamp_ready}`。
- 阈值冻结：`{thresholds_frozen}`。

阻塞项：

{blockers}

## 临时替代接口（历史诊断）

- 已按 `temporary-ens9f0-passive-shadow-v1` 使用 `ens9f0` 完成 `{shadow_runs}` 次、每次 {shadow_duration} 秒的被动确认；该口为 `br0` 的 1GbE 管理/集群上联，不执行 PCAP 注入或主动发流。
- `ens8f0/ens8f1` 恢复后，`ens9f0` 不再是主验收接口；其历史结果仅保留用于回归比较。
- 每轮最少接收 `{shadow_packets}` 包，捕获丢包率最坏 `{shadow_drops}`、解析拒绝率最坏 `{shadow_parse_reject}`，关键流覆盖最小 `{shadow_coverage}`，GPU 最少评分 `{shadow_scored}` 流，批次失败/回退/预算超限均为 0。
- 最终临时组合为 `batch={shadow_batch}`、`feature_flush={shadow_flush}us`、`runtime={shadow_runtime}`；GPU 批次往返 P99 最坏 `{shadow_gpu_p99}us`，内部特征入队 P99 最坏 `{shadow_internal_p99}us`，均通过临时硬门。该结果只证明临时被动捕获与双机推理链路可用，不证明独立 10GbE 生产 P99。
- `final_pareto_ingestion_allowed=false`，不得将 1GbE 管理口结果冒充独立 10GbE 生产证据。

## 最终 10GbE 双口就绪状态

- 生产接口硬门固定为：两个不同物理接口、速率至少 `{readiness_speed}Mbps`、无管理桥、无 IP、无默认路由；当前候选对为 `ens8f0/ens8f1`。
- 当前硬件合格接口 `{readiness_hardware_count}` 个、合格接口对 `{readiness_hardware_pairs}` 对；连同冻结阈值检查后的完整合格接口对 `{readiness_full_pairs}` 对，因此 `final_live_run_allowed={readiness_allowed}`。
- 在线脚本只要证据合成失败也会返回非零状态，不再允许“原始运行完成但严格证据不合格”被误报为成功。

## 证据索引

| 证据 | 路径 | SHA-256 |
| --- | --- | --- |
{evidence_rows}

## 下一执行门

1. 由业务方冻结目标 Mpps/Gbps、解析拒绝率、端到端 P99/P999 和最小时长；不得从 0.01 Mpps 诊断结果反推生产门限。
2. 在冻结生产负载下对 `xdp-skb` 到 `af-packet-ts` 的已实现运行时回退做压力复测，单独报告切换损失，不复用正常路径零丢包证据。
3. 在冻结目标负载下执行至少三次独立 Rust 发包/抓包，保留分层 NIC、ring、parser、HFT、sender 与跨主机资源原始证据。
4. 完成 24 小时影子和 72 小时生产长稳门，期间要求零残留 XDP 程序、零未解释丢包和时间戳异常。
5. 全部门通过后才重新计算最终 Pareto 前沿并变更 `final_pareto_eligible`。
""".format(
        generated_at=generated_at,
        release_status=release["status"],
        selected=selected,
        pareto=str(release["final_pareto_eligible"]).lower(),
        minimum=budget["minimum_candidates"],
        maximum=budget["maximum_candidates"],
        actual=budget["actual_candidates"],
        runtime_candidates=runtime_selection["candidate_count"],
        runtime_campaigns=runtime_selection[
            "campaign_count_per_candidate"
        ],
        runtime_repeats=runtime_selection["repeats_per_candidate"],
        runtime_total=runtime_selection["total_runtime_runs"],
        runtime_passing=runtime_selection["passing_candidate_count"],
        runtime_front=", ".join(runtime_selection["pareto_front"]),
        runtime_initial=runtime_selection["initial_selected_candidate"],
        runtime_selected=runtime_selection["selected_candidate"],
        prediction_execution=runtime["prediction_execution"],
        cpu_set=runtime["cpu_set"],
        eligible_cpu_count=runtime["eligible_cpu_count"],
        runtime_inference_p99=_fmt(
            runtime_selection["inference_batch_p99_us_max"]
        ),
        runtime_internal_p99=_fmt(
            runtime_selection["internal_feature_p99_us_max"]
        ),
        runtime_e2e_p99=_fmt(
            runtime_selection["end_to_end_p99_us_max"]
        ),
        runtime_e2e_p999=_fmt(
            runtime_selection["end_to_end_p999_us_max"]
        ),
        feature_count=len(search["search_dimensions"]["feature_profiles"]),
        classifier_count=len(
            search["search_dimensions"]["classifier_families"]
        ),
        threshold_count=len(
            search["search_dimensions"]["threshold_policies"]
        ),
        adaptation_count=len(
            search["search_dimensions"]["adaptation_policies"]
        ),
        strict_front=", ".join(search["strict_pareto_front"]),
        practical_front=", ".join(search["practical_front"]),
        feature_profile=candidate["feature_profile"],
        classifier=candidate["classifier"],
        threshold_policy=candidate["threshold_policy"],
        adaptation_policy=candidate["adaptation_policy"],
        selection_reason=search.get(
            "selection_reason_zh", search["selection_reason"]
        ),
        gate_rows="\n".join(rows),
        physical_cpu=_fmt(
            physical["physical_process_cpu_percent_of_one_core_max"]
        ),
        physical_host_cpu=_fmt(
            physical["physical_host_cpu_fraction_upper"]
        ),
        physical_memory=_fmt(physical["physical_memory_fraction_max"]),
        process_samples=split_resources["process_sample_count_min"],
        gpu_samples=split_resources["gpu_sample_count_min"],
        python_cores=_fmt(split_resources["cpu_cores_used_max"]),
        python_cpu=_fmt(physical["python_host_cpu_fraction_upper"]),
        python_rss=split_resources["rss_bytes_max"],
        python_memory=_fmt(physical["python_memory_fraction_max"]),
        python_threads=split_resources["threads_max"],
        gpu_util=_fmt(physical["gpu_utilization_fraction_observed"]),
        gpu_memory=_fmt(physical["gpu_memory_fraction_observed"]),
        system_gpu_background=_fmt(
            split_resources[
                "system_gpu_utilization_fraction_background_max"
            ]
        ),
        n_jobs=runtime["model_n_jobs"],
        batch=runtime["batch_size"],
        feature_flush_us=runtime["feature_flush_us"],
        timeout=runtime["request_timeout_ms"],
        budget_us=runtime["budget_us"],
        safety_ratio=runtime["execution_budget_safety_ratio"],
        packets=physical["packets_per_run"],
        flows=physical["flows_per_run"],
        feature_enqueue_p99=_fmt(physical["feature_enqueue_p99_us_max"]),
        gpu_batch_p99=_fmt(physical["gpu_batch_p99_us_max"]),
        virtual_packets=virtual["offered_packets_min"],
        virtual_drop=_fmt(virtual["pipeline_drop_rate_max"]),
        virtual_coverage=_fmt(virtual["key_flow_coverage_min"]),
        timestamp_samples=timestamp_probe[
            "kernel_receive_to_feature_enqueue_samples"
        ],
        timestamp_p99=_fmt(
            timestamp_probe["kernel_receive_to_feature_enqueue_p99_us"]
        ),
        timestamp_anomalies=timestamp_probe["kernel_timestamp_anomalies"],
        clock_steps=timestamp_probe["realtime_clock_step_count"],
        nic_driver=capability["driver"],
        nic_bus=", ".join(capability["bus_functions"]),
        recovery_ms=_fmt(recovery["recovery_to_success_s_max"] * 1000),
        recovery_gate_ms=_fmt(gates["max_fallback_recovery_s"] * 1000),
        preflight_run=preflight["run_id"],
        preflight_accepted=str(preflight["accepted"]).lower(),
        capture_interface=preflight["capture_interface"],
        capture_carrier=preflight["capture_carrier"],
        capture_state=preflight["capture_operstate"],
        capture_speed=preflight["capture_speed_mbps"],
        replay_interface=preflight["replay_interface"],
        replay_carrier=preflight["replay_carrier"],
        replay_state=preflight["replay_operstate"],
        replay_speed=preflight["replay_speed_mbps"],
        timestamp_ready=str(
            preflight["kernel_xdp_timestamp_ready"]
        ).lower(),
        thresholds_frozen=str(preflight["thresholds_frozen"]).lower(),
        blockers=blockers,
        shadow_runs=temporary_shadow["run_count"],
        shadow_duration=temporary_shadow["confirmation_duration_s"],
        shadow_packets=temporary_shadow["packets_received_min"],
        shadow_drops=_fmt(temporary_shadow["capture_drop_rate_max"]),
        shadow_parse_reject=_fmt(
            temporary_shadow["parse_reject_rate_max"]
        ),
        shadow_coverage=_fmt(
            temporary_shadow["key_flow_coverage_min"]
        ),
        shadow_scored=temporary_shadow["gpu_flows_scored_min"],
        shadow_batch=temporary_shadow["batch_size"],
        shadow_flush=temporary_shadow["feature_flush_us"],
        shadow_runtime=temporary_shadow["runtime_candidate"],
        shadow_gpu_p99=_fmt(
            temporary_shadow["gpu_batch_round_trip_p99_us_max"]
        ),
        shadow_internal_p99=_fmt(
            temporary_shadow["internal_feature_enqueue_p99_us_max"]
        ),
        readiness_speed=interface_readiness["minimum_speed_mbps"],
        readiness_hardware_count=len(
            interface_readiness["hardware_eligible_interfaces"]
        ),
        readiness_hardware_pairs=interface_readiness[
            "hardware_pair_count"
        ],
        readiness_full_pairs=interface_readiness[
            "full_preflight_pair_count"
        ],
        readiness_allowed=str(
            interface_readiness["final_live_run_allowed"]
        ).lower(),
        xdp_p99=_fmt(xdp["kernel_xdp_to_feature_p99_us_max"]),
        xdp_p999=_fmt(xdp["kernel_xdp_to_feature_p999_us_max"]),
        xdp_gpu_p99=_fmt(xdp["gpu_batch_p99_us_max"]),
        xdp_physical_rss=xdp["joint_physical_maximum_rss_kib"],
        xdp_python_cores=_fmt(xdp["inference_cpu_cores_used_max"]),
        xdp_python_rss=xdp["inference_rss_bytes_max"],
        capture_fallback_recovery_ms=_fmt(
            capture_fallback["fallback_recovery_ms_max"]
        ),
        capture_fallback_packets=capture_fallback["fallback_packets_min"],
        capture_fallback_gap=capture_fallback[
            "transition_packet_gap_max"
        ],
        evidence_rows=rendered_evidence,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("algorithm_search", type=Path)
    parser.add_argument("release_candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--generated-at")
    args = parser.parse_args()
    search = json.loads(args.algorithm_search.read_text(encoding="utf-8"))
    release = json.loads(
        args.release_candidate.read_text(encoding="utf-8")
    )
    generated_at = args.generated_at or datetime.now(
        timezone.utc
    ).isoformat().replace("+00:00", "Z")
    content = generate_markdown(search, release, generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
