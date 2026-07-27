import numpy as np

from audit_strict_v4_krc_external_malicious import (
    METRICS,
    aggregate,
    gate,
    oriented,
)


def report(value):
    return {
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
        "known_macro_f1": value,
    }


def records(candidate=0.8, comparator=0.6):
    output = []
    for dataset in ("LSNM2024", "CICDDoS2019"):
        for attack in ("a", "b"):
            for seed in (223, 227, 229):
                output.append(
                    {
                        "dataset": dataset,
                        "unknown_attack_family": attack,
                        "seed": seed,
                        "candidate": report(candidate),
                        "comparator": report(comparator),
                    }
                )
    return output


def test_independent_oriented_direction():
    assert oriented(report(0.8), report(0.6), "unknown_auroc") > 0
    assert oriented(report(0.8), report(0.6), "unknown_fpr95") > 0


def test_independent_aggregation_averages_seed_blocks():
    value = aggregate(records(), repetitions=100, seed=7)
    assert value["label_block_count"] == 4
    assert np.isclose(
        value["metrics"]["unknown_auroc"]["oriented_mean_gain"], 0.2
    )


def test_effect_gate_is_separate_from_integrity():
    value = aggregate(records(), repetitions=100, seed=7)
    gates = {
        "known_macro_f1_mean_gain_minimum": -0.01,
        "known_macro_f1_each_dataset_gain_minimum": -0.02,
    }
    checks = gate(value, gates)
    assert checks["all_four_oriented_means_strictly_positive"]
    failed = aggregate(
        records(candidate=0.6, comparator=0.8),
        repetitions=100,
        seed=7,
    )
    assert not all(gate(failed, gates).values())
