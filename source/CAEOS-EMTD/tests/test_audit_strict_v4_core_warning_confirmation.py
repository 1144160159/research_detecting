from audit_strict_v4_core_warning_confirmation import identity_coverage


def test_identity_coverage_requires_all_three_seeds_and_scenarios() -> None:
    records = [
        {"suite": "cicids2017", "scenario": scenario, "seed": seed}
        for scenario in ("bot", "ddos")
        for seed in (907, 911, 919)
    ]
    coverage = identity_coverage(
        records, [907, 911, 919], ["bot", "ddos"]
    )
    assert coverage["passes"] is True
    assert coverage["record_count"] == 6
    assert coverage["duplicate_identity_count"] == 0


def test_identity_coverage_rejects_duplicate_and_missing_identity() -> None:
    records = [
        {"suite": "cicids2017", "scenario": "bot", "seed": 907},
        {"suite": "cicids2017", "scenario": "bot", "seed": 907},
    ]
    coverage = identity_coverage(records, [907, 911], ["bot"])
    assert coverage["passes"] is False
    assert coverage["duplicate_identity_count"] == 1
    assert coverage["missing_identities"] == [
        {"suite": "cicids2017", "scenario": "bot", "seed": 911}
    ]
