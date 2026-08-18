from pathlib import Path

from build_caeos_ciciot2023_capture_label_index import build_index, family_for


def test_family_mapping_is_explicit():
    assert family_for("DDoS-UDP_Flood") == "DDoS"
    assert family_for("DictionaryBruteForce") == "BruteForce"
    assert family_for("Benign_Final") == "Benign"


def test_build_index_crosschecks_same_name_csv(tmp_path: Path):
    root = tmp_path
    notebook = root / "example" / "example.ipynb"
    notebook.parent.mkdir(parents=True)
    notebook.write_text('{"cells":[{"source":["dict_7classes[\'DoS-TCP_Flood\'] = \'DoS\'\\n"]}]}')
    pcap = root / "PCAP" / "DoS-TCP_Flood" / "DoS-TCP_Flood.pcap"
    csv = root / "CSV" / "CSV" / "DoS-TCP_Flood" / "DoS-TCP_Flood.pcap.csv"
    pcap.parent.mkdir(parents=True)
    csv.parent.mkdir(parents=True)
    pcap.write_bytes(b"pcap")
    csv.write_text("feature\n")
    report = build_index(root)
    assert report["summary"]["capture_count"] == 1
    assert report["summary"]["missing_official_csv_count"] == 0
    assert report["captures"][0]["attack_family"] == "DoS"
    assert report["summary"]["ready_for_prefix_check"] is True
