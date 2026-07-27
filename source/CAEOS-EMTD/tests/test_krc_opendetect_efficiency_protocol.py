import pytest

from create_strict_v4_krc_opendetect_efficiency_protocol import (
    build_sources,
    zero_output_counts,
)


def test_zero_output_counts_rejects_existing_result(tmp_path):
    assert zero_output_counts(tmp_path) == {
        "benchmarks": 0,
        "summary": 0,
        "audit": 0,
        "completion": 0,
    }
    (tmp_path / "audit.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="zero-result"):
        zero_output_counts(tmp_path)


def test_build_sources_rejects_incomplete_selected_matrix():
    with pytest.raises(ValueError, match="incomplete"):
        build_sources({"sources": []}, {})
