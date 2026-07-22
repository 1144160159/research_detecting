from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOTS = (
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT.parent / "CAEOS-EMTD-lcb-exploration-20260720" / "scripts",
)


def script(name: str) -> str:
    for root in SCRIPT_ROOTS:
        path = root / name
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"queue watcher script not found: {name}")


def source(relative: str) -> str:
    for root in (PROJECT_ROOT, PROJECT_ROOT.parent / "CAEOS-EMTD-lcb-exploration-20260720"):
        path = root / relative
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"queue producer source not found: {relative}")


class StrictV4QueueDependencyTests(unittest.TestCase):
    def test_wdiscood_uses_distinct_authoritative_source_roots(self) -> None:
        value = script("wait_and_run_strict_v4_wdiscood_pilot.sh")
        self.assertIn("--mlp-root runs/strict_v4_full103_mlp_seed7", value)
        self.assertIn(
            "--opendetect-root runs/strict_v4_full103_independent_baselines_seed7",
            value,
        )

    def test_downstream_markers_match_actual_producers(self) -> None:
        mal = script("wait_and_run_mal_tls_heterogeneous_pilot.sh")
        wdisc = script("wait_and_run_strict_v4_wdiscood_pilot.sh")
        doh = script("wait_and_run_doh_temporal_external.sh")
        vos = script("wait_and_run_strict_v4_vos_pilot.sh")
        self.assertIn(
            "results/strict_v4_lcb_tail_aware_pilot_seed191/pilot_complete", mal
        )
        self.assertIn(
            "results/mal_tls_heterogeneous_pilot_seed191/pilot_complete", wdisc
        )
        self.assertIn(
            "runs/strict_v4_wdiscood_pilot_seed7/pilot_complete", doh
        )
        self.assertIn("results/doh_temporal_external/execution_complete", vos)

    def test_self_algorithm_chain_precedes_external_baseline_expansion(self) -> None:
        lcb = script("wait_and_run_strict_v4_lcb_tail_aware_pilot.sh")
        geometry = script("wait_and_run_mal_tls_geometry_preserving_adapter.sh")
        topology = script(
            "wait_and_run_strict_v4_conflict_topology_copula_pilot.sh"
        )
        wdisc = script("wait_and_run_strict_v4_wdiscood_pilot.sh")
        grood = script("wait_and_run_strict_v4_grood_pilot.sh")
        self.assertIn("results/strict_v4_comprehensive_sota_audit/audit_complete", lcb)
        self.assertIn("results/strict_v4_final_efficiency_seed191_cache/caches_complete", lcb)
        self.assertNotIn("results/strict_v4_final_paper_readiness/audit_complete", lcb)
        self.assertIn("results/strict_v4_final_efficiency_v5/recovery_complete", geometry)
        self.assertNotIn("results/strict_v4_vos_pilot_seed7/analysis.json", geometry)
        self.assertIn("results/strict_v4_final_efficiency_v5/recovery_complete", wdisc)
        self.assertIn("results/mal_tls_self_algorithm_selection/audit_complete", wdisc)
        self.assertIn("results/mal_tls_self_algorithm_selection/audit_complete", topology)
        self.assertIn(
            "results/strict_v4_conflict_topology_copula_confirmation_branch/branch_complete",
            wdisc,
        )
        self.assertIn("results/strict_v4_vos_pilot_seed7/pilot_complete", grood)

    def test_every_consumed_marker_has_a_matching_producer(self) -> None:
        self.assertIn(
            '(output_root / "execution_complete").touch()',
            source("execute_strict_v4_final_efficiency_plan_v2.py"),
        )
        self.assertIn(
            'touch "$RESULT_ROOT/caches_complete"',
            source("scripts/prepare_strict_v4_final_efficiency_seed191_caches.sh"),
        )
        self.assertIn(
            'touch "$OUTPUT/audit_complete"',
            source("scripts/wait_and_audit_strict_v4_comprehensive_sota.sh"),
        )
        self.assertIn(
            'touch "$RESULT_ROOT/pilot_complete"',
            source("scripts/run_strict_v4_lcb_tail_aware_pilot.sh"),
        )
        self.assertIn(
            'touch "$RESULT_ROOT/pilot_complete"',
            source("scripts/run_mal_tls_heterogeneous_pilot.sh"),
        )
        self.assertIn(
            'marker = args.pilot_root / "pilot_complete"',
            source("summarize_strict_v4_wdiscood_pilot.py"),
        )
        self.assertIn(
            'touch "$RESULT_ROOT/execution_complete"',
            source("scripts/wait_and_run_doh_temporal_external.sh"),
        )
        self.assertIn(
            '(args.output_dir / "pilot_complete").touch()',
            source("summarize_strict_v4_vos_pilot.py"),
        )


if __name__ == "__main__":
    unittest.main()
