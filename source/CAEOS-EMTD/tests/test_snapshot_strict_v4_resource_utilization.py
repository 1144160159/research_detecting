from snapshot_strict_v4_resource_utilization import busy_fraction


def test_busy_fraction_excludes_idle_ticks() -> None:
    before = (1000, 400)
    after = (1100, 420)
    assert busy_fraction(before, after) == 0.8
