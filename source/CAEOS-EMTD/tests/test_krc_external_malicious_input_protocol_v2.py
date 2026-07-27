import pytest

from create_strict_v4_krc_external_malicious_input_protocol_v2 import (
    corrected_tasks,
)


def tasks():
    values = []
    for dataset, count in (("LSNM2024", 15), ("CICDDoS2019", 17)):
        for attack in range(count):
            for seed in (223, 227, 229):
                values.append(
                    {
                        "dataset": dataset,
                        "unknown_attack_family": f"attack-{attack}",
                        "training_seed": seed,
                        "split_seed": seed + 1000,
                        "opendetect_seed": seed + 2000,
                        "augmentation_seed": seed + 3000,
                        "validation_profile_seed": seed + 4000,
                    }
                )
    return values


def test_corrects_only_split_coupled_seeds():
    source = tasks()
    corrected = corrected_tasks(source)
    assert len(corrected) == 96
    for before, after in zip(source, corrected):
        seed = before["training_seed"]
        assert after["prepared_seed"] == seed
        assert after["split_seed"] == seed
        assert after["opendetect_seed"] == seed
        assert (
            after["augmentation_seed"] == before["augmentation_seed"]
        )
        assert (
            after["validation_profile_seed"]
            == before["validation_profile_seed"]
        )


def test_rejects_incomplete_task_universe():
    with pytest.raises(ValueError, match="96 unique"):
        corrected_tasks(tasks()[:-1])


def test_rejects_duplicate_task_identity():
    source = tasks()
    source[-1] = dict(source[0])
    with pytest.raises(ValueError, match="96 unique"):
        corrected_tasks(source)
