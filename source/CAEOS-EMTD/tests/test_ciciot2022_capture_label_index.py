import io
import tarfile
from pathlib import Path

from build_caeos_ciciot2022_capture_label_index import attack_labels, build_index


def add_member(archive: tarfile.TarFile, name: str, payload: bytes):
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def test_attack_hierarchy_mapping():
    assert attack_labels("6-Attacks/1-Flood/Camera/UDP/x.pcap") == ("Flood", "Flood-UDP")
    assert attack_labels("6-Attacks/2-RTSP Brute Force/Hydra/Camera/x.pcap") == ("RTSP Brute Force", "RTSP Brute Force-Hydra")


def test_build_index_filters_appledouble(tmp_path: Path):
    (tmp_path / "Readme.txt").write_text("official")
    active = tmp_path / "5-Active" / "active.pcap"
    active.parent.mkdir()
    active.write_bytes(b"active")
    for name in ("1-Power.tar.gz", "2-Idle.tar.gz", "3-Interactions.tar.gz", "4-Scenarios.tar.gz"):
        with tarfile.open(tmp_path / name, "w:gz"):
            pass
    with tarfile.open(tmp_path / "6-Attacks.tar.gz", "w:gz") as archive:
        add_member(archive, "6-Attacks/Readme.txt", b"1-Flood and 2-RTSP BruteForce")
        add_member(archive, "6-Attacks/1-Flood/Camera/TCP/x.pcap", b"pcap")
        add_member(archive, "6-Attacks/1-Flood/Camera/TCP/._x.pcap", b"metadata")
    report = build_index(tmp_path)
    assert report["summary"]["active_capture_count"] == 1
    assert report["summary"]["attack_capture_count"] == 1
    assert report["summary"]["ignored_appledouble_pcap_entries"] == 1
    assert report["summary"]["ready_for_prefix_check"] is True
