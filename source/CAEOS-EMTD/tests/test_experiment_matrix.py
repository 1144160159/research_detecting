import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from run_nested_gate_matrix import build_experiments, command_for
from run_neural_baseline_matrix import (
    build_experiments as build_neural_experiments,
    command_for as neural_command_for,
)


class NestedGateMatrixTest(unittest.TestCase):
    def test_nested_matrix_rejects_empty_seeds_and_misspelled_scenarios(self):
        args = self.arguments("runs/test")
        args.seeds = ""
        with self.assertRaisesRegex(ValueError, "seeds"):
            build_experiments(args)

        args.seeds = "7"
        args.scenarios = "fingerprnting"
        args.suite = "edge_iiot"
        with self.assertRaisesRegex(ValueError, "scenarios"):
            build_experiments(args)

    def test_neural_matrix_rejects_empty_models_seeds_and_unknown_scenarios(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="", seeds="7",
            workers=1, epochs=3, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        with self.assertRaisesRegex(ValueError, "models"):
            build_neural_experiments(args)

        args.models = "mlp"
        args.seeds = ""
        with self.assertRaisesRegex(ValueError, "seeds"):
            build_neural_experiments(args)

        args.seeds = "7"
        args.scenarios = "probng"
        with self.assertRaisesRegex(ValueError, "scenarios"):
            build_neural_experiments(args)

        args.scenarios = "probing"
        args.models = "mlp,palmm"
        with self.assertRaisesRegex(ValueError, "models"):
            build_neural_experiments(args)

    def test_neural_matrix_filters_scenarios_and_expands_seeds(self):
        args = Namespace(
            suite="hikari", scenarios="probing,xmrigcc", models="mlp",
            seeds="7,11", workers=1, epochs=3, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiments = build_neural_experiments(args)
        self.assertEqual(len(experiments), 4)
        self.assertEqual({item.scenario for item in experiments}, {"probing", "xmrigcc"})

    def test_closr_matrix_uses_official_model_hyperparameters(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="closr",
            seeds="7", workers=1, epochs=20, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[command.index("--model") + 1], "closr")
        self.assertEqual(command[command.index("--hidden-dim") + 1], "1024")
        self.assertEqual(command[command.index("--embedding-dim") + 1], "64")
        self.assertEqual(command[command.index("--learning-rate") + 1], "1e-5")
        self.assertEqual(command[command.index("--weight-decay") + 1], "0.0403709")
        self.assertEqual(
            command[-4:], ["--batch-size", "4096", "--sampling", "weighted"]
        )

    def test_hcrp_osd_matrix_uses_frozen_paper_structure_adapter_settings(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="hcrp_osd",
            seeds="7", workers=1, epochs=0, patience=10,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)
        self.assertEqual(command[command.index("--model") + 1], "hcrp_osd")
        self.assertEqual(command[command.index("--epochs") + 1], "100")
        self.assertEqual(command[command.index("--hidden-dim") + 1], "32")
        self.assertEqual(command[command.index("--embedding-dim") + 1], "64")
        self.assertEqual(command[command.index("--radius-weight") + 1], "0.1")

    def test_tao_stage1_adapter_is_opt_in_and_uses_frozen_parameters(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="mlp",
            seeds="7", workers=1, epochs=35, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test", tao_stage1_adapter=True,
            tao_blood_estimators=50,
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertIn("--tao-stage1-adapter", command)
        self.assertEqual(command[command.index("--tao-blood-estimators") + 1], "50")
        self.assertEqual(command[command.index("--tao-pca-variance-ratio") + 1], "0.95")
        self.assertEqual(command[command.index("--tao-alpha") + 1], "0.6")

    def test_mlp_matrix_freezes_scale_arguments(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="mlp",
            seeds="7", workers=1, epochs=35, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[command.index("--scale-percentile") + 1], "85")
        self.assertEqual(command[command.index("--scale-temperature") + 1], "1")

    def test_cade_matrix_uses_official_detection_hyperparameters(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="cade",
            seeds="7", workers=1, epochs=250, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[command.index("--model") + 1], "cade")
        self.assertEqual(command[command.index("--cade-hidden") + 1], "64,32,16")
        self.assertEqual(command[command.index("--learning-rate") + 1], "1e-4")
        self.assertEqual(command[command.index("--cade-contrast-weight") + 1], "0.1")
        self.assertEqual(command[command.index("--cade-margin") + 1], "10")
        self.assertEqual(command[command.index("--cade-mad-threshold") + 1], "3.5")
        self.assertEqual(command[-2:], ["--sampling", "natural"])

    def test_open_detect_matrix_uses_official_objective_hyperparameters(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="opendetect",
            seeds="7", workers=1, epochs=100, patience=2,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[command.index("--model") + 1], "opendetect")
        self.assertEqual(command[command.index("--embedding-dim") + 1], "128")
        self.assertEqual(command[command.index("--learning-rate") + 1], "1e-3")
        self.assertEqual(
            command[command.index("--open-detect-generative-weight") + 1],
            "0.005",
        )
        self.assertEqual(
            command[command.index("--open-detect-reset-epochs") + 1],
            "50,80",
        )
        self.assertEqual(command[-2:], ["--sampling", "natural"])

    def test_ronetc_matrix_uses_evidential_adaptation_hyperparameters(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="ronetc",
            seeds="7", workers=1, epochs=100, patience=10,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[command.index("--model") + 1], "ronetc")
        self.assertEqual(command[command.index("--hidden-dim") + 1], "128")
        self.assertEqual(command[command.index("--embedding-dim") + 1], "64")
        self.assertEqual(command[command.index("--learning-rate") + 1], "1e-3")
        self.assertEqual(
            command[command.index("--ronetc-annealing-epochs") + 1], "10"
        )
        self.assertEqual(command[-4:], ["--batch-size", "256", "--sampling", "natural"])

    def test_foss_matrix_uses_paper_and_official_repository_parameters(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="foss",
            seeds="7", workers=1, epochs=100, patience=10,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[1], "train_foss_open_set.py")
        self.assertEqual(command[command.index("--foss-trees") + 1], "30")
        self.assertEqual(command[command.index("--foss-subsample-size") + 1], "100")
        self.assertEqual(
            command[command.index("--foss-candidate-dimensions") + 1], "5"
        )

    def test_m3s_upd_matrix_uses_secondary_transductive_runner(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="m3s_upd",
            seeds="7", workers=1, epochs=30, patience=5,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)

        self.assertEqual(command[1], "train_m3s_upd_strict_v2.py")
        self.assertNotIn("--model", command)
        self.assertEqual(command[command.index("--epochs") + 1], "30")
        self.assertEqual(command[command.index("--split-strategy") + 1], "fingerprint_grouped")

    def test_nested_matrix_filters_scenarios(self):
        args = self.arguments("runs/test")
        args.suite = "hikari"
        args.scenarios = "probing,xmrigcc"
        experiments = build_experiments(args)
        self.assertEqual(len(experiments), 4)
        self.assertEqual(
            {item.scenario for item in experiments}, {"probing", "xmrigcc"}
        )

    def arguments(self, root: str) -> Namespace:
        return Namespace(
            suite="both",
            seeds="11,19",
            workers=2,
            model_jobs=4,
            estimators=20,
            doh_max_per_class=100,
            mal_max_per_class=50,
            hikari_max_per_class=80,
            nf_unsw_max_per_class=90,
            edge_iiot_max_per_class=80,
            nf_cse_max_per_class=70,
            ustc_max_per_class=60,
            doh_csv="doh.csv",
            mal_csv="mal.csv",
            hikari_csv="hikari.csv",
            nf_unsw_csv="nf_unsw.csv",
            nf_unsw_cache_dir="",
            cicids2017_csv="cicids2017.csv",
            cicids2017_cache_dir="",
            cicids2017_max_per_class=120,
            cic_iot2023_csv="cic_iot2023.csv",
            cic_iot2023_cache_dir="",
            cic_iot2023_max_per_class=100,
            cic_ton_iot_csv="cic_ton_iot.csv",
            cic_ton_iot_cache_dir="",
            cic_ton_iot_max_per_class=100,
            edge_iiot_csv="edge.csv",
            edge_iiot_cache_dir="",
            nf_cse_csv="nf_cse.csv",
            nf_cse_cache_dir="",
            ustc_csv="ustc.csv",
            ustc_cache_dir="",
            output_root=root,
        )

    def test_matrix_has_all_scenarios_and_seeds(self):
        with tempfile.TemporaryDirectory() as directory:
            experiments = build_experiments(self.arguments(directory))
        self.assertEqual(len(experiments), 18)
        self.assertEqual(
            len({(item.suite, item.scenario) for item in experiments}), 9
        )

    def test_command_preserves_multi_family_unknown_argument(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            experiment = next(
                item
                for item in build_experiments(args)
                if item.suite == "mal_tls" and item.scenario == "scanners"
            )
            command = command_for(experiment, args)
        unknown_index = command.index("--unknown-classes") + 1
        self.assertEqual(command[unknown_index].count(","), 3)
        self.assertIn("--risk-selection", command)
        self.assertIn("nested_conflict_gate", command)
        self.assertEqual(
            command[command.index("--conflict-fallback-minimum-gain") + 1],
            "0.055",
        )

    def test_robust_pseudo_unknown_matrix_forwards_frozen_fold_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.scenarios = "mitm"
            args.seeds = "83"
            args.risk_selection = "nested_robust_pseudo_unknown_blend"
            args.pseudo_unknown_max_alpha = 0.5
            args.pseudo_unknown_min_fold_gain = -0.125
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1],
            "nested_robust_pseudo_unknown_blend",
        )
        self.assertEqual(
            command[command.index("--pseudo-unknown-max-alpha") + 1], "0.5"
        )
        self.assertEqual(
            command[command.index("--pseudo-unknown-min-fold-gain") + 1],
            "-0.125",
        )

    def test_local_rank_pseudo_unknown_matrix_forwards_order_constraints(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.scenarios = "mitm"
            args.seeds = "97"
            args.risk_selection = "nested_local_rank_pseudo_unknown_blend"
            args.pseudo_unknown_max_alpha = 0.5
            args.pseudo_unknown_min_fold_gain = -0.05
            args.pseudo_unknown_local_rank_bins = 5
            args.pseudo_unknown_local_rank_beta = 1.0
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1],
            "nested_local_rank_pseudo_unknown_blend",
        )
        self.assertEqual(
            command[command.index("--pseudo-unknown-min-fold-gain") + 1], "-0.05"
        )
        self.assertEqual(
            command[command.index("--pseudo-unknown-local-rank-bins") + 1], "5"
        )
        self.assertEqual(
            command[command.index("--pseudo-unknown-local-rank-beta") + 1], "1.0"
        )

    def test_boundary_pseudo_unknown_matrix_forwards_generation_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.scenarios = "xss"
            args.seeds = "7"
            args.risk_selection = "nested_boundary_pseudo_unknown_blend"
            args.boundary_hard_pseudo_fraction = 0.5
            args.boundary_interpolation = 0.5
            args.boundary_max_per_task = 512
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1],
            "nested_boundary_pseudo_unknown_blend",
        )
        self.assertEqual(
            command[command.index("--boundary-hard-pseudo-fraction") + 1], "0.5"
        )
        self.assertEqual(
            command[command.index("--boundary-interpolation") + 1], "0.5"
        )
        self.assertEqual(
            command[command.index("--boundary-max-per-task") + 1], "512"
        )

    def test_boundary_pairwise_matrix_selects_pairwise_training(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.scenarios = "mitm"
            args.seeds = "7"
            args.risk_selection = "nested_boundary_pairwise_pseudo_unknown_blend"
            args.boundary_training_objective = "pairwise"
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1],
            "nested_boundary_pairwise_pseudo_unknown_blend",
        )
        self.assertEqual(
            command[command.index("--boundary-training-objective") + 1],
            "pairwise",
        )

    def test_tail_aware_pairwise_matrix_forwards_distinct_risk_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.scenarios = "mitm"
            args.seeds = "7"
            args.risk_selection = (
                "nested_tail_aware_pairwise_pseudo_unknown_blend"
            )
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1],
            "nested_tail_aware_pairwise_pseudo_unknown_blend",
        )
        self.assertEqual(
            command[command.index("--boundary-hard-pseudo-fraction") + 1],
            "0.5",
        )

    def test_lcb_tail_aware_matrix_forwards_conservative_evidence_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.scenarios = "mitm"
            args.seeds = "173"
            args.risk_selection = (
                "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend"
            )
            args.tail_aware_confidence_z = 1.645
            args.tail_aware_min_metric_lcb_gain = 0.0
            args.tail_aware_min_aupr_lcb_gain = 0.0
            args.tail_aware_min_aupr_fold_gain = -0.05
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1],
            "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
        )
        self.assertEqual(
            command[command.index("--tail-aware-confidence-z") + 1], "1.645"
        )
        self.assertEqual(
            command[command.index("--tail-aware-min-metric-lcb-gain") + 1],
            "0.0",
        )
        self.assertEqual(
            command[command.index("--tail-aware-min-aupr-lcb-gain") + 1],
            "0.0",
        )
        self.assertEqual(
            command[command.index("--tail-aware-min-aupr-fold-gain") + 1],
            "-0.05",
        )

    def test_hikari_keeps_spaced_unknown_class_as_one_argument(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "hikari"
            experiment = next(
                item
                for item in build_experiments(args)
                if item.scenario == "xmrigcc"
            )
            command = command_for(experiment, args)
        unknown_index = command.index("--unknown-classes") + 1
        self.assertEqual(command[unknown_index], "XMRIGCC CryptoMiner")

    def test_nf_unsw_matrix_uses_leakage_resistant_split(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "nf_unsw"
            args.scenarios = "analysis,reconnaissance"
            experiments = build_experiments(args)
            command = command_for(experiments[0], args)
        self.assertEqual(len(experiments), 4)
        self.assertEqual(command[command.index("--config") + 1], "configs/nf_unsw_nb15.json")
        self.assertEqual(
            command[command.index("--split-strategy") + 1],
            "fingerprint_grouped",
        )

    def test_nf_unsw_matrix_covers_every_attack_label(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "nf_unsw"
            args.seeds = "7"
            args.scenarios = "all"
            experiments = build_experiments(args)
        self.assertEqual(len(experiments), 9)
        self.assertEqual(
            {item.unknown_classes for item in experiments},
            {
                "Analysis",
                "Backdoor",
                "DoS",
                "Exploits",
                "Fuzzers",
                "Generic",
                "Reconnaissance",
                "Shellcode",
                "Worms",
            },
        )

    def test_nf_unsw_matrix_uses_seed_specific_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "nf_unsw"
            args.seeds = "7"
            args.scenarios = "analysis"
            args.nf_unsw_cache_dir = directory
            cached = Path(directory) / "seed7_max90.csv"
            cached.touch()
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(command[command.index("--csv") + 1], str(cached))

    def test_strict_v3_matrix_covers_nf_unsw_and_cicids2017(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "strict_v3"
            args.seeds = "7"
            args.scenarios = "all"
            experiments = build_experiments(args)
        self.assertEqual(len(experiments), 23)
        self.assertEqual(
            {item.suite for item in experiments},
            {"nf_unsw", "cicids2017"},
        )

    def test_strict_v3_representative_pilot_has_6_caeos_and_18_baseline_runs(self):
        scenarios = "exploits,fuzzers,reconnaissance,ddos,portscan,web_bruteforce"
        nested_args = self.arguments("runs/pilot_caeos")
        nested_args.suite = "strict_v3"
        nested_args.seeds = "7"
        nested_args.scenarios = scenarios
        caeos = build_experiments(nested_args)
        self.assertEqual(6, len(caeos))
        self.assertEqual({"nf_unsw", "cicids2017"}, {item.suite for item in caeos})

        neural_args = self.arguments("runs/pilot_neural")
        neural_args.suite = "strict_v3"
        neural_args.scenarios = scenarios
        neural_args.models = "mlp,opendetect,ronetc"
        neural_args.seeds = "7"
        neural_args.epochs = 0
        neural_args.patience = 10
        neural_args.nf_unsw_max_per_class = 5000
        neural_args.cicids2017_max_per_class = 5000
        baselines = build_neural_experiments(neural_args)
        self.assertEqual(18, len(baselines))
        self.assertEqual(
            {"mlp", "opendetect", "ronetc"}, {item.model for item in baselines}
        )

    def test_cicids2017_uses_grouped_flow_split_and_seed_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cicids2017"
            args.seeds = "7"
            args.scenarios = "web_xss"
            args.cicids2017_cache_dir = directory
            cached = Path(directory) / "seed7_max120.csv"
            cached.touch()
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(command[command.index("--csv") + 1], str(cached))
        self.assertEqual(
            command[command.index("--config") + 1],
            "configs/cicids2017_strict.json",
        )
        self.assertEqual(
            command[command.index("--split-strategy") + 1],
            "capture_grouped",
        )

    def test_cic_iot2023_uses_frozen_scenarios_grouped_cache_and_pilot(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_iot2023"
            args.seeds = "7"
            args.scenarios = "ddos_icmp_flood,mirai_udpplain,command_injection"
            args.cic_iot2023_cache_dir = directory
            cached = Path(directory) / "seed7_max100.csv"
            cached.touch()
            caeos = build_experiments(args)
            command = command_for(caeos[0], args)

            args.models = "mlp,opendetect,ronetc"
            args.epochs = 0
            args.patience = 10
            baselines = build_neural_experiments(args)

        self.assertEqual(len(caeos), 3)
        self.assertEqual(len(baselines), 9)
        self.assertEqual(
            {item.unknown_classes for item in caeos},
            {"DDoS-ICMP_Flood", "Mirai-udpplain", "CommandInjection"},
        )
        self.assertEqual(command[command.index("--csv") + 1], str(cached))
        self.assertEqual(
            command[command.index("--config") + 1],
            "configs/cic_iot2023_strict.json",
        )
        self.assertEqual(
            command[command.index("--split-strategy") + 1],
            "capture_grouped",
        )

    def test_cic_ton_iot_uses_identity_free_grouped_cache_and_strict_v4(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "cic_ton_iot"
            args.seeds = "7"
            args.scenarios = "xss,scanning,ransomware"
            args.cic_ton_iot_cache_dir = directory
            cached = Path(directory) / "seed7_max100.csv"
            cached.touch()
            caeos = build_experiments(args)
            command = command_for(caeos[0], args)

            args.models = "mlp,opendetect,ronetc"
            args.epochs = 0
            args.patience = 10
            baselines = build_neural_experiments(args)

        self.assertEqual(len(caeos), 3)
        self.assertEqual(len(baselines), 9)
        self.assertEqual(
            {item.unknown_classes for item in caeos},
            {"xss", "scanning", "ransomware"},
        )
        self.assertEqual(command[command.index("--csv") + 1], str(cached))
        self.assertEqual(
            command[command.index("--config") + 1],
            "configs/cic_ton_iot_strict.json",
        )
        self.assertEqual(
            command[command.index("--split-strategy") + 1],
            "fingerprint_grouped",
        )

        args = self.arguments("runs/strict_v4")
        args.suite = "strict_v4"
        args.seeds = "7"
        strict_v4 = build_experiments(args)
        self.assertEqual(len(strict_v4), 41)
        self.assertEqual(
            {item.suite for item in strict_v4},
            {"cic_ton_iot", "cic_iot2023"},
        )
        self.assertNotIn(
            "Uploading_Attack",
            {item.unknown_classes for item in strict_v4},
        )

    def test_neural_strict_v3_matrix_uses_all_scenarios(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "strict_v3"
            args.scenarios = "all"
            args.models = "mlp"
            args.seeds = "7"
            args.epochs = 3
            args.patience = 2
            experiments = build_neural_experiments(args)
        self.assertEqual(len(experiments), 23)
        cicids = next(
            item for item in experiments
            if item.suite == "cicids2017" and item.scenario == "web_xss"
        )
        command = neural_command_for(cicids, args)
        self.assertEqual(
            command[command.index("--config") + 1],
            "configs/cicids2017_strict.json",
        )
        self.assertEqual(
            command[command.index("--split-strategy") + 1],
            "capture_grouped",
        )

    def test_extended_matrix_adds_all_new_attack_scenarios(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "extended"
            args.seeds = "7"
            experiments = build_experiments(args)
        self.assertEqual(len(experiments), 38)
        self.assertEqual(
            {item.suite for item in experiments},
            {"edge_iiot", "nf_cse", "ustc_tfc2016"},
        )

    def test_density_policy_is_frozen_to_supported_suites(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "extended"
            args.seeds = "7"
            args.risk_selection = "nested_density_reliability_gate"
            args.density_gate_supported_suites = "edge_iiot"
            args.density_gate_fallback_risk_selection = (
                "nested_hierarchical_joint_gate"
            )
            args.density_gate_blend_weight = 0.3
            experiments = build_experiments(args)
            commands = {
                item.suite: command_for(item, args)
                for item in experiments
                if item.scenario in {"fingerprinting", "bot", "zeus"}
            }
        edge = commands["edge_iiot"]
        nf_cse = commands["nf_cse"]
        ustc = commands["ustc_tfc2016"]
        self.assertEqual(
            edge[edge.index("--risk-selection") + 1],
            "nested_density_reliability_gate",
        )
        for command in (nf_cse, ustc):
            self.assertEqual(
                command[command.index("--risk-selection") + 1],
                "nested_hierarchical_joint_gate",
            )
        policies = {
            command[command.index("--risk-policy-name") + 1]
            for command in commands.values()
        }
        self.assertEqual(len(policies), 1)
        policy = policies.pop()
        self.assertIn("suites=edge_iiot", policy)
        self.assertIn("weight=0.3", policy)

    def test_fixed_entropy_is_forwarded_without_task_level_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "edge_iiot"
            args.seeds = "67"
            args.scenarios = "fingerprinting"
            args.risk_selection = "fixed_entropy"
            args.risk_policy_name = "fixed_entropy_candidate_v1"
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1], "fixed_entropy"
        )
        self.assertEqual(
            command[command.index("--risk-policy-name") + 1],
            "fixed_entropy_candidate_v1",
        )

    def test_fixed_named_risk_is_forwarded_without_task_level_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "nf_cse"
            args.seeds = "83"
            args.scenarios = "bot"
            args.risk_selection = "fixed_named"
            args.fixed_risk_name = "disagreement_augmented"
            args.risk_policy_name = "nf_cse_fixed_disagreement_augmented_v1"
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(
            command[command.index("--risk-selection") + 1], "fixed_named"
        )
        self.assertEqual(
            command[command.index("--fixed-risk-name") + 1],
            "disagreement_augmented",
        )

    def test_density_policy_rejects_unknown_supported_suite(self):
        args = self.arguments("runs/test")
        args.risk_selection = "nested_density_reliability_gate"
        args.density_gate_supported_suites = "edge_iiot,typo"
        with self.assertRaisesRegex(ValueError, "unknown"):
            build_experiments(args)

    def test_nf_cse_matrix_uses_seed_specific_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "nf_cse"
            args.seeds = "7"
            args.scenarios = "sql_injection"
            args.nf_cse_cache_dir = directory
            cached = Path(directory) / "seed7_max70.csv"
            cached.touch()
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(command[command.index("--csv") + 1], str(cached))
        self.assertEqual(
            command[command.index("--config") + 1],
            "configs/nf_cse_cic_ids2018_v2.json",
        )

    def test_ustc_matrix_uses_capture_groups(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.arguments(directory)
            args.suite = "ustc_tfc2016"
            args.seeds = "7"
            args.scenarios = "zeus"
            args.ustc_cache_dir = directory
            cached = Path(directory) / "seed7_max60.csv"
            cached.touch()
            experiment = build_experiments(args)[0]
            command = command_for(experiment, args)
        self.assertEqual(command[command.index("--csv") + 1], str(cached))
        self.assertEqual(
            command[command.index("--split-strategy") + 1],
            "capture_grouped",
        )

    def test_neural_extended_matrix_covers_all_new_scenarios(self):
        args = Namespace(
            suite="extended", scenarios="all", models="closr,cade", seeds="7",
            workers=1, epochs=0, patience=10,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            nf_unsw_max_per_class=20, edge_iiot_max_per_class=20,
            nf_cse_max_per_class=20, ustc_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            nf_unsw_csv="nf_unsw.csv", nf_unsw_cache_dir="",
            edge_iiot_csv="edge.csv", edge_iiot_cache_dir="",
            nf_cse_csv="nf_cse.csv", nf_cse_cache_dir="",
            ustc_csv="ustc.csv", ustc_cache_dir="", output_root="runs/test",
        )
        experiments = build_neural_experiments(args)
        self.assertEqual(len(experiments), 76)
        self.assertEqual(
            {item.suite for item in experiments},
            {"edge_iiot", "nf_cse", "ustc_tfc2016"},
        )

    def test_neural_default_uses_model_specific_epoch_budget(self):
        args = Namespace(
            suite="hikari", scenarios="probing", models="cade", seeds="7",
            workers=1, epochs=0, patience=10,
            doh_max_per_class=20, mal_max_per_class=20, hikari_max_per_class=20,
            doh_csv="doh.csv", mal_csv="mal.csv", hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_neural_experiments(args)[0]
        command = neural_command_for(experiment, args)
        self.assertEqual(command[command.index("--epochs") + 1], "250")


if __name__ == "__main__":
    unittest.main()
