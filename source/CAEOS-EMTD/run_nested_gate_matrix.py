from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path


PROVENANCE_SCHEMA_VERSION = 1
PROVENANCE_FILENAME = "provenance.json"


DOH_SCENARIOS = {
    "dns2tcp": "dns2tcp",
    "dnscat2": "dnscat2",
    "iodine": "iodine",
}

MAL_TLS_SCENARIOS = {
    "caphaw": "Caphaw.AH_None_TLS_CC,Caphaw.A_None_TLS_CC",
    "cobalt": "CobaltStrike_None_TLS_CC",
    "panda": "Panda.BZA!tr_None_TLS_CC,PandaZeuSCC_None_TLS_CC",
    "qakbot": "Qakbot_None_TLS_CC",
    "scanners": (
        "arachni_arachni_TLS_scan,burpsuite_burpsuite_TLS_scan,"
        "golistmero_golistmero_TLS_scan,nessus_nessus_TLS_scan"
    ),
    "tor": "Tor_None_TLS_CC",
}

HIKARI_SCENARIOS = {
    "brutefoce": "Brutefoce",
    "bruteforce_xml": "Bruteforce-XML",
    "probing": "Probing",
    "xmrigcc": "XMRIGCC CryptoMiner",
}

NF_UNSW_SCENARIOS = {
    "analysis": "Analysis",
    "backdoor": "Backdoor",
    "dos": "DoS",
    "exploits": "Exploits",
    "fuzzers": "Fuzzers",
    "generic": "Generic",
    "reconnaissance": "Reconnaissance",
    "shellcode": "Shellcode",
    "worms": "Worms",
}

CICIDS2017_SCENARIOS = {
    "bot": "Bot",
    "ddos": "DDoS",
    "dos_goldeneye": "DoS GoldenEye",
    "dos_hulk": "DoS Hulk",
    "dos_slowhttptest": "DoS Slowhttptest",
    "dos_slowloris": "DoS slowloris",
    "ftp_patator": "FTP-Patator",
    "heartbleed": "Heartbleed",
    "infiltration": "Infiltration",
    "portscan": "PortScan",
    "ssh_patator": "SSH-Patator",
    "web_bruteforce": "Web Attack - Brute Force",
    "web_sql_injection": "Web Attack - Sql Injection",
    "web_xss": "Web Attack - XSS",
}

CIC_IOT2023_SCENARIOS = {
    "backdoor_malware": "Backdoor_Malware",
    "browser_hijacking": "BrowserHijacking",
    "command_injection": "CommandInjection",
    "ddos_ack_fragmentation": "DDoS-ACK_Fragmentation",
    "ddos_http_flood": "DDoS-HTTP_Flood",
    "ddos_icmp_flood": "DDoS-ICMP_Flood",
    "ddos_icmp_fragmentation": "DDoS-ICMP_Fragmentation",
    "ddos_pshack_flood": "DDoS-PSHACK_FLOOD",
    "ddos_rstfin_flood": "DDoS-RSTFINFLOOD",
    "ddos_syn_flood": "DDoS-SYN_Flood",
    "ddos_slowloris": "DDoS-SlowLoris",
    "ddos_synonymous_ip_flood": "DDoS-SynonymousIP_Flood",
    "ddos_tcp_flood": "DDoS-TCP_Flood",
    "ddos_udp_flood": "DDoS-UDP_Flood",
    "ddos_udp_fragmentation": "DDoS-UDP_Fragmentation",
    "dns_spoofing": "DNS_Spoofing",
    "dictionary_bruteforce": "DictionaryBruteForce",
    "dos_http_flood": "DoS-HTTP_Flood",
    "dos_syn_flood": "DoS-SYN_Flood",
    "dos_tcp_flood": "DoS-TCP_Flood",
    "dos_udp_flood": "DoS-UDP_Flood",
    "mitm_arp_spoofing": "MITM-ArpSpoofing",
    "mirai_greeth_flood": "Mirai-greeth_flood",
    "mirai_greip_flood": "Mirai-greip_flood",
    "mirai_udpplain": "Mirai-udpplain",
    "recon_host_discovery": "Recon-HostDiscovery",
    "recon_os_scan": "Recon-OSScan",
    "recon_ping_sweep": "Recon-PingSweep",
    "recon_port_scan": "Recon-PortScan",
    "sql_injection": "SqlInjection",
    "vulnerability_scan": "VulnerabilityScan",
    "xss": "XSS",
}

CIC_TON_IOT_SCENARIOS = {
    "xss": "xss",
    "password": "password",
    "injection": "injection",
    "scanning": "scanning",
    "backdoor": "backdoor",
    "ransomware": "ransomware",
    "mitm": "mitm",
    "ddos": "ddos",
    "dos": "dos",
}

EDGE_IIOT_SCENARIOS = {
    "backdoor": "Backdoor",
    "ddos_http": "DDoS_HTTP",
    "ddos_icmp": "DDoS_ICMP",
    "ddos_tcp": "DDoS_TCP",
    "ddos_udp": "DDoS_UDP",
    "fingerprinting": "Fingerprinting",
    "mitm": "MITM",
    "password": "Password",
    "port_scanning": "Port_Scanning",
    "ransomware": "Ransomware",
    "sql_injection": "SQL_injection",
    "uploading": "Uploading",
    "vulnerability_scanner": "Vulnerability_scanner",
    "xss": "XSS",
}

NF_CSE_SCENARIOS = {
    "bot": "Bot",
    "brute_force_web": "Brute Force -Web",
    "brute_force_xss": "Brute Force -XSS",
    "ddos_hoic": "DDOS attack-HOIC",
    "ddos_loic_http": "DDoS attacks-LOIC-HTTP",
    "ddos_loic_udp": "DDOS attack-LOIC-UDP",
    "dos_goldeneye": "DoS attacks-GoldenEye",
    "dos_hulk": "DoS attacks-Hulk",
    "dos_slowhttptest": "DoS attacks-SlowHTTPTest",
    "dos_slowloris": "DoS attacks-Slowloris",
    "ftp_bruteforce": "FTP-BruteForce",
    "infilteration": "Infilteration",
    "sql_injection": "SQL Injection",
    "ssh_bruteforce": "SSH-Bruteforce",
}

USTC_TFC2016_SCENARIOS = {
    "cridex": "Cridex",
    "geodo": "Geodo",
    "htbot": "Htbot",
    "miuref": "Miuref",
    "neris": "Neris",
    "nsis_ay": "Nsis-ay",
    "shifu": "Shifu",
    "tinba": "Tinba",
    "virut": "Virut",
    "zeus": "Zeus",
}

SUITE_NAMES = (
    "doh",
    "mal_tls",
    "hikari",
    "nf_unsw",
    "cicids2017",
    "cic_iot2023",
    "cic_ton_iot",
    "edge_iiot",
    "nf_cse",
    "ustc_tfc2016",
)


@dataclass(frozen=True)
class Experiment:
    suite: str
    scenario: str
    unknown_classes: str
    seed: int
    output_dir: str


class ProvenanceMismatchError(RuntimeError):
    """Raised when an existing run cannot be proven identical to the request."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_path(value: str) -> str:
    return str(Path(value).expanduser().resolve(strict=False))


def _command_value(command: list[str], flag: str) -> str:
    try:
        return command[command.index(flag) + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"command is missing required option {flag}") from error


def _declared_sidecar_sha(path: Path) -> dict[str, str] | None:
    candidates = (
        Path(f"{path}.json"),
        Path(f"{path}.sha256"),
        path.with_suffix(".sha256"),
    )
    for sidecar in candidates:
        if not sidecar.is_file():
            continue
        declared = None
        if sidecar.suffix == ".json":
            try:
                payload = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValueError(f"invalid dataset SHA sidecar: {sidecar}") from error
            for key in ("output_sha256", "source_sha256", "sha256"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    declared = value.strip().lower()
                    break
        else:
            try:
                token = sidecar.read_text(encoding="utf-8").strip().split()[0]
            except (OSError, UnicodeDecodeError, IndexError) as error:
                raise ValueError(f"invalid dataset SHA sidecar: {sidecar}") from error
            if len(token) == 64:
                declared = token.lower()
        if declared is not None:
            return {
                "path": _canonical_path(str(sidecar)),
                "declared_sha256": declared,
                "sidecar_file_sha256": _sha256_file(sidecar),
            }
    return None


def _code_identity(command: list[str]) -> dict[str, object]:
    training_script = Path(command[1])
    files = [training_script]
    package = Path("caeos")
    if package.is_dir():
        files.extend(sorted(package.rglob("*.py")))
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing code files for provenance: {missing}")
    file_hashes = {
        _canonical_path(str(path)): _sha256_file(path)
        for path in files
    }
    digest = hashlib.sha256()
    for path, file_hash in sorted(file_hashes.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\0")
    return {"sha256": digest.hexdigest(), "files": file_hashes}


def build_run_provenance(
    experiment: Experiment,
    command: list[str],
) -> dict[str, object]:
    csv_path = Path(_command_value(command, "--csv"))
    config_path = Path(_command_value(command, "--config"))
    inputs: dict[str, object] = {
        "csv": {
            "path": _canonical_path(str(csv_path)),
            "sidecar_sha": _declared_sidecar_sha(csv_path),
        },
        "config": {
            "path": _canonical_path(str(config_path)),
            "sha256": _sha256_file(config_path) if config_path.is_file() else None,
        },
    }
    task = {
        key: value
        for key, value in asdict(experiment).items()
        if key != "output_dir"
    }
    parameter_payload = {
        "command": command,
        "task": task,
        "inputs": inputs,
    }
    parameter_fingerprint = hashlib.sha256(
        json.dumps(
            parameter_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "task": task,
        "command": command,
        "inputs": inputs,
        "code": _code_identity(command),
        "parameter_fingerprint": parameter_fingerprint,
    }


def effective_metrics_arguments(command: list[str]) -> dict[str, object]:
    risk_selection = _command_value(command, "--risk-selection")
    try:
        risk_policy = _command_value(command, "--risk-policy-name")
    except ValueError:
        risk_policy = risk_selection
    return {
        "csv": _command_value(command, "--csv"),
        "config": _command_value(command, "--config"),
        "split_strategy": _command_value(command, "--split-strategy"),
        "max_per_class": int(_command_value(command, "--max-per-class")),
        "benign_class": _command_value(command, "--benign-class"),
        "risk_selection": risk_selection,
        "risk_policy": risk_policy,
    }


def attach_metrics_arguments(metrics_path: Path, command: list[str]) -> None:
    """Attach auditable effective arguments without overwriting conflicting data."""
    try:
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot attach arguments to {metrics_path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"metrics file must contain a JSON object: {metrics_path}")
    arguments = payload.get("arguments", {})
    if not isinstance(arguments, dict):
        raise ValueError(f"metrics arguments must be an object: {metrics_path}")
    effective = effective_metrics_arguments(command)
    conflicts = {
        key: (arguments[key], value)
        for key, value in effective.items()
        if key in arguments and arguments[key] != value
    }
    if conflicts:
        raise ProvenanceMismatchError(
            f"refusing to overwrite conflicting metrics arguments in "
            f"{metrics_path}: {conflicts}"
        )
    if all(arguments.get(key) == value for key, value in effective.items()):
        return
    payload["arguments"] = {**arguments, **effective}
    temporary = metrics_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(metrics_path)


def _identity_mismatches(
    actual: object,
    expected: object,
    prefix: str = "provenance",
) -> list[str]:
    if type(actual) is not type(expected):
        return [f"{prefix}: {actual!r} != {expected!r}"]
    if isinstance(expected, dict):
        mismatches = []
        keys = set(actual) | set(expected)
        for key in sorted(keys):
            if key not in actual:
                mismatches.append(f"{prefix}.{key}: missing from frozen provenance")
            elif key not in expected:
                mismatches.append(f"{prefix}.{key}: unexpected frozen field")
            else:
                mismatches.extend(
                    _identity_mismatches(actual[key], expected[key], f"{prefix}.{key}")
                )
        return mismatches
    if isinstance(expected, list):
        if len(actual) != len(expected):
            return [f"{prefix}: list length {len(actual)} != {len(expected)}"]
        mismatches = []
        for index, (left, right) in enumerate(zip(actual, expected)):
            mismatches.extend(
                _identity_mismatches(left, right, f"{prefix}[{index}]")
            )
        return mismatches
    return [] if actual == expected else [f"{prefix}: {actual!r} != {expected!r}"]


def freeze_or_validate_provenance(
    output_dir: Path,
    expected: dict[str, object],
    completed_artifacts: tuple[Path, ...],
) -> bool:
    """Validate a prior identity, or freeze a new one; return whether to skip."""
    provenance_path = output_dir / PROVENANCE_FILENAME
    existing_artifacts = [path for path in completed_artifacts if path.exists()]
    if provenance_path.exists():
        try:
            frozen = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProvenanceMismatchError(
                f"cannot read frozen provenance for {output_dir}: {error}"
            ) from error
        mismatches = _identity_mismatches(frozen, expected)
        if mismatches:
            detail = "; ".join(mismatches[:8])
            raise ProvenanceMismatchError(
                f"refusing to reuse incompatible run {output_dir}: {detail}"
            )
    elif existing_artifacts:
        names = ", ".join(path.name for path in existing_artifacts)
        raise ProvenanceMismatchError(
            f"refusing to reuse legacy run without {PROVENANCE_FILENAME}: "
            f"{output_dir} ({names})"
        )
    else:
        temporary = provenance_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(expected, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(provenance_path)
    return all(path.exists() for path in completed_artifacts)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run resumable nested conflict-gate confirmation matrices"
    )
    parser.add_argument(
        "--suite",
        choices=(
            "doh",
            "mal_tls",
            "hikari",
            "nf_unsw",
            "cicids2017",
            "cic_iot2023",
            "cic_ton_iot",
            "edge_iiot",
            "nf_cse",
            "ustc_tfc2016",
            "both",
            "extended",
            "all",
            "strict_v3",
            "strict_v4",
        ),
        default="both",
    )
    parser.add_argument("--seeds", default="11,19,23,29")
    parser.add_argument("--scenarios", default="all")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model-jobs", type=int, default=20)
    parser.add_argument("--estimators", type=int, default=80)
    parser.add_argument(
        "--risk-selection",
        choices=(
            "fixed_entropy",
            "fixed_named",
            "fixed_cauchy_modality_support_union",
            "nested_pseudo_unknown_blend",
            "nested_robust_pseudo_unknown_blend",
            "nested_local_rank_pseudo_unknown_blend",
            "nested_boundary_pseudo_unknown_blend",
            "nested_boundary_pairwise_pseudo_unknown_blend",
            "nested_tail_aware_pairwise_pseudo_unknown_blend",
            "nested_conflict_gate",
            "nested_modality_gate",
            "nested_modality_support_gate",
            "nested_anchor_conflict_gate",
            "nested_hierarchical_anchor_gate",
            "nested_hierarchical_fallback_gate",
            "nested_hierarchical_joint_gate",
            "nested_density_reliability_gate",
            "nested_structural_partition_gate",
            "nested_structural_support_gate",
        ),
        default="nested_conflict_gate",
    )
    parser.add_argument("--fixed-risk-name", default="")
    parser.add_argument("--modality-gate-minimum-gain", type=float, default=0.02)
    parser.add_argument("--conflict-fallback-minimum-gain", type=float, default=0.055)
    parser.add_argument("--joint-fallback-minimum-gain", type=float, default=0.055)
    parser.add_argument("--density-gate-minimum-gain", type=float, default=0.02)
    parser.add_argument("--density-gate-minimum-known-classes", type=int, default=8)
    parser.add_argument("--density-gate-blend-weight", type=float, default=0.05)
    parser.add_argument("--pseudo-unknown-max-alpha", type=float, default=1.0)
    parser.add_argument("--pseudo-unknown-min-fold-gain", type=float, default=-0.125)
    parser.add_argument("--pseudo-unknown-local-rank-bins", type=int, default=5)
    parser.add_argument("--pseudo-unknown-local-rank-beta", type=float, default=1.0)
    parser.add_argument("--boundary-hard-pseudo-fraction", type=float, default=0.5)
    parser.add_argument("--boundary-interpolation", type=float, default=0.5)
    parser.add_argument("--boundary-max-per-task", type=int, default=512)
    parser.add_argument(
        "--boundary-training-objective",
        choices=("pointwise", "pairwise"),
        default="pointwise",
    )
    parser.add_argument(
        "--density-gate-supported-suites",
        default="",
        help=(
            "Comma-separated suites where nested_density_reliability_gate is "
            "allowed. Empty preserves the historical all-suite behavior."
        ),
    )
    parser.add_argument(
        "--density-gate-fallback-risk-selection",
        choices=(
            "nested_conflict_gate",
            "nested_modality_gate",
            "nested_anchor_conflict_gate",
            "nested_hierarchical_anchor_gate",
            "nested_hierarchical_fallback_gate",
            "nested_hierarchical_joint_gate",
            "nested_structural_partition_gate",
            "nested_structural_support_gate",
        ),
        default="nested_hierarchical_joint_gate",
    )
    parser.add_argument(
        "--risk-policy-name",
        default="",
        help="Optional stable name for a frozen suite-conditional risk policy.",
    )
    parser.add_argument("--structural-gate-minimum-gain", type=float, default=0.02)
    parser.add_argument("--foss-structural-view", action="store_true")
    parser.add_argument(
        "--foss-structural-view-mode",
        choices=("tree", "aggregate"),
        default="tree",
    )
    parser.add_argument(
        "--foss-structural-view-scope",
        choices=("full", "evidence", "support"),
        default="full",
    )
    parser.add_argument("--structural-support-weights", default="0,0.1,0.25,0.5,1.0")
    parser.add_argument("--structural-support-minimum-gain", type=float, default=0.005)
    parser.add_argument(
        "--test-corruption-kind",
        choices=(
            "none",
            "modality_missing",
            "field_missing",
            "row_missing",
            "feature_shuffle",
            "gaussian_drift",
        ),
        default="none",
    )
    parser.add_argument("--test-corruption-modality", type=int, default=0)
    parser.add_argument("--test-corruption-severity", type=float, default=0.0)
    parser.add_argument("--test-corruption-seed", type=int, default=20260717)
    parser.add_argument("--train-label-noise", type=float, default=0.0)
    parser.add_argument("--doh-max-per-class", type=int, default=4000)
    parser.add_argument("--mal-max-per-class", type=int, default=300)
    parser.add_argument("--hikari-max-per-class", type=int, default=2000)
    parser.add_argument("--nf-unsw-max-per-class", type=int, default=5000)
    parser.add_argument("--cicids2017-max-per-class", type=int, default=5000)
    parser.add_argument("--cic-iot2023-max-per-class", type=int, default=1000)
    parser.add_argument("--cic-ton-iot-max-per-class", type=int, default=1000)
    parser.add_argument("--edge-iiot-max-per-class", type=int, default=1000)
    parser.add_argument("--nf-cse-max-per-class", type=int, default=1000)
    parser.add_argument("--ustc-max-per-class", type=int, default=3000)
    parser.add_argument(
        "--doh-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/DoHBrw2020/"
            "caeos_multiclass_balanced_seed7.csv"
        ),
    )
    parser.add_argument(
        "--mal-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/"
            "data/malicious_TLS.csv"
        ),
    )
    parser.add_argument(
        "--hikari-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/HIKARI2021/"
            "HIKARI2021_model.csv"
        ),
    )
    parser.add_argument(
        "--nf-unsw-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/"
            "NF-UNSW-NB15-v2.csv"
        ),
    )
    parser.add_argument(
        "--nf-unsw-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument(
        "--cicids2017-csv",
        default="caches/strict_v3/cicids2017/source/cicids2017_strict.csv",
    )
    parser.add_argument(
        "--cicids2017-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument("--cic-iot2023-csv", default="")
    parser.add_argument(
        "--cic-iot2023-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument(
        "--cic-ton-iot-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/"
            "a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
        ),
    )
    parser.add_argument(
        "--cic-ton-iot-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument(
        "--edge-iiot-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument(
        "--edge-iiot-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/"
            "Edge-IIoTset dataset/Selected dataset for ML and DL/"
            "ML-EdgeIIoT-dataset.csv"
        ),
    )
    parser.add_argument(
        "--nf-cse-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/"
            "NF-CSE-CIC-IDS2018-v2.csv"
        ),
    )
    parser.add_argument(
        "--nf-cse-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument(
        "--ustc-csv",
        default="caches/ustc_tfc2016/ustc_tfc2016_nfstream.csv",
    )
    parser.add_argument(
        "--ustc-cache-dir",
        default="",
        help="Optional directory containing seed{seed}_max{max_per_class}.csv caches",
    )
    parser.add_argument(
        "--output-root", default="runs/nested_conflict_gate_confirmation"
    )
    return parser.parse_args()


def density_gate_supported_suites(args: argparse.Namespace) -> tuple[str, ...]:
    raw = str(getattr(args, "density_gate_supported_suites", "")).strip()
    if not raw:
        return ()
    values = tuple(value.strip() for value in raw.split(",") if value.strip())
    if len(values) != len(set(values)):
        raise ValueError("--density-gate-supported-suites must not contain duplicates")
    unknown = sorted(set(values) - set(SUITE_NAMES))
    if unknown:
        raise ValueError(
            f"unknown --density-gate-supported-suites values: {unknown}"
        )
    if getattr(args, "risk_selection", "nested_conflict_gate") != (
        "nested_density_reliability_gate"
    ):
        raise ValueError(
            "--density-gate-supported-suites requires "
            "--risk-selection nested_density_reliability_gate"
        )
    return tuple(sorted(values))


def risk_policy_name(args: argparse.Namespace) -> str:
    explicit = str(getattr(args, "risk_policy_name", "")).strip()
    if explicit:
        return explicit
    supported = density_gate_supported_suites(args)
    selection = getattr(args, "risk_selection", "nested_conflict_gate")
    if not supported:
        return selection
    fallback = getattr(
        args,
        "density_gate_fallback_risk_selection",
        "nested_hierarchical_joint_gate",
    )
    weight = float(getattr(args, "density_gate_blend_weight", 0.05))
    minimum_gain = float(getattr(args, "density_gate_minimum_gain", 0.02))
    minimum_known = int(
        getattr(args, "density_gate_minimum_known_classes", 8)
    )
    return (
        "frozen_suite_conditional_density_v1"
        f"[suites={','.join(supported)};fallback={fallback};"
        f"weight={weight:.12g};minimum_gain={minimum_gain:.12g};"
        f"minimum_known_classes={minimum_known}]"
    )


def effective_risk_selection(
    experiment: Experiment, args: argparse.Namespace
) -> str:
    selection = getattr(args, "risk_selection", "nested_conflict_gate")
    supported = density_gate_supported_suites(args)
    if not supported or experiment.suite in supported:
        return selection
    return getattr(
        args,
        "density_gate_fallback_risk_selection",
        "nested_hierarchical_joint_gate",
    )


def build_experiments(args: argparse.Namespace) -> list[Experiment]:
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    if not seeds:
        raise ValueError("--seeds must contain at least one integer")
    if len(seeds) != len(set(seeds)):
        raise ValueError("--seeds must not contain duplicates")
    requested = (
        None
        if getattr(args, "scenarios", "all") == "all"
        else {
            value.strip()
            for value in args.scenarios.split(",")
            if value.strip()
        }
    )
    density_gate_supported_suites(args)
    if args.suite == "both":
        suites = ("doh", "mal_tls")
    elif args.suite == "extended":
        suites = ("edge_iiot", "nf_cse", "ustc_tfc2016")
    elif args.suite == "strict_v3":
        suites = ("nf_unsw", "cicids2017")
    elif args.suite == "strict_v4":
        suites = ("cic_ton_iot", "cic_iot2023")
    elif args.suite == "all":
        suites = (
            "doh",
            "mal_tls",
            "hikari",
            "nf_unsw",
            "cicids2017",
            "cic_iot2023",
            "cic_ton_iot",
            "edge_iiot",
            "nf_cse",
            "ustc_tfc2016",
        )
    else:
        suites = (args.suite,)
    scenario_maps = {
        "doh": DOH_SCENARIOS,
        "mal_tls": MAL_TLS_SCENARIOS,
        "hikari": HIKARI_SCENARIOS,
        "nf_unsw": NF_UNSW_SCENARIOS,
        "cicids2017": CICIDS2017_SCENARIOS,
        "cic_iot2023": CIC_IOT2023_SCENARIOS,
        "cic_ton_iot": CIC_TON_IOT_SCENARIOS,
        "edge_iiot": EDGE_IIOT_SCENARIOS,
        "nf_cse": NF_CSE_SCENARIOS,
        "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
    }
    if requested is not None:
        known_scenarios = set().union(*(scenario_maps[suite] for suite in suites))
        unknown = requested - known_scenarios
        if not requested or unknown:
            raise ValueError(
                f"unknown or empty --scenarios selection: {sorted(unknown or requested)}"
            )
    experiments = []
    for suite in suites:
        scenarios = scenario_maps[suite]
        for scenario, unknown_classes in scenarios.items():
            if requested is not None and scenario not in requested:
                continue
            for seed in seeds:
                output_dir = str(
                    Path(args.output_root) / suite / f"{scenario}_seed{seed}"
                )
                experiments.append(
                    Experiment(suite, scenario, unknown_classes, seed, output_dir)
                )
    if not experiments:
        raise ValueError("experiment selection produced zero experiments")
    return experiments


def command_for(experiment: Experiment, args: argparse.Namespace) -> list[str]:
    if experiment.suite == "doh":
        csv_path = args.doh_csv
        config = "configs/dohbrw2020_multiclass.json"
        benign = "benign"
        maximum = args.doh_max_per_class
        split = "capture_grouped"
    elif experiment.suite == "mal_tls":
        csv_path = args.mal_csv
        config = "configs/mal_tls2023.json"
        benign = "benign"
        maximum = args.mal_max_per_class
        split = "fingerprint_grouped"
    elif experiment.suite == "hikari":
        csv_path = args.hikari_csv
        config = "configs/hikari2021.json"
        benign = "Benign"
        maximum = args.hikari_max_per_class
        split = "fingerprint_grouped"
    elif experiment.suite == "nf_unsw":
        cache_dir = str(getattr(args, "nf_unsw_cache_dir", "")).strip()
        if cache_dir:
            cached = Path(cache_dir) / (
                f"seed{experiment.seed}_max{args.nf_unsw_max_per_class}.csv"
            )
            if not cached.exists():
                raise FileNotFoundError(
                    f"missing NF-UNSW stratified cache: {cached}"
                )
            csv_path = str(cached)
        else:
            csv_path = args.nf_unsw_csv
        config = "configs/nf_unsw_nb15.json"
        benign = "Benign"
        maximum = args.nf_unsw_max_per_class
        split = "fingerprint_grouped"
    elif experiment.suite == "cicids2017":
        cache_dir = str(getattr(args, "cicids2017_cache_dir", "")).strip()
        if cache_dir:
            cached = Path(cache_dir) / (
                f"seed{experiment.seed}_max{args.cicids2017_max_per_class}.csv"
            )
            if not cached.exists():
                raise FileNotFoundError(
                    f"missing CIC-IDS2017 stratified cache: {cached}"
                )
            csv_path = str(cached)
        else:
            csv_path = args.cicids2017_csv
        config = "configs/cicids2017_strict.json"
        benign = "Benign"
        maximum = args.cicids2017_max_per_class
        split = "capture_grouped"
    elif experiment.suite == "cic_iot2023":
        cache_dir = str(getattr(args, "cic_iot2023_cache_dir", "")).strip()
        maximum = getattr(args, "cic_iot2023_max_per_class", 1000)
        if cache_dir:
            cached = Path(cache_dir) / (
                f"seed{experiment.seed}_max{maximum}.csv"
            )
            if not cached.exists():
                raise FileNotFoundError(
                    f"missing CICIoT2023 strict cache: {cached}"
                )
            csv_path = str(cached)
        else:
            csv_path = str(getattr(args, "cic_iot2023_csv", "")).strip()
            if not csv_path:
                raise ValueError(
                    "CICIoT2023 requires --cic-iot2023-cache-dir or "
                    "--cic-iot2023-csv"
                )
        config = "configs/cic_iot2023_strict.json"
        benign = "Benign"
        split = "capture_grouped"
    elif experiment.suite == "cic_ton_iot":
        cache_dir = str(getattr(args, "cic_ton_iot_cache_dir", "")).strip()
        maximum = getattr(args, "cic_ton_iot_max_per_class", 1000)
        if cache_dir:
            cached = Path(cache_dir) / f"seed{experiment.seed}_max{maximum}.csv"
            if not cached.exists():
                raise FileNotFoundError(f"missing CIC-ToN-IoT cache: {cached}")
            csv_path = str(cached)
        else:
            csv_path = str(getattr(args, "cic_ton_iot_csv", "")).strip()
        config = "configs/cic_ton_iot_strict.json"
        benign = "Benign"
        split = "fingerprint_grouped"
    elif experiment.suite == "edge_iiot":
        cache_dir = str(getattr(args, "edge_iiot_cache_dir", "")).strip()
        if cache_dir:
            cached = Path(cache_dir) / (
                f"seed{experiment.seed}_max{args.edge_iiot_max_per_class}.csv"
            )
            if not cached.exists():
                raise FileNotFoundError(
                    f"missing Edge-IIoT stratified cache: {cached}"
                )
            csv_path = str(cached)
        else:
            csv_path = args.edge_iiot_csv
        config = "configs/edge_iiot.json"
        benign = "Normal"
        maximum = args.edge_iiot_max_per_class
        split = "fingerprint_grouped"
    elif experiment.suite == "nf_cse":
        cache_dir = str(getattr(args, "nf_cse_cache_dir", "")).strip()
        if cache_dir:
            cached = Path(cache_dir) / (
                f"seed{experiment.seed}_max{args.nf_cse_max_per_class}.csv"
            )
            if not cached.exists():
                raise FileNotFoundError(
                    f"missing NF-CSE stratified cache: {cached}"
                )
            csv_path = str(cached)
        else:
            csv_path = args.nf_cse_csv
        config = "configs/nf_cse_cic_ids2018_v2.json"
        benign = "Benign"
        maximum = args.nf_cse_max_per_class
        split = "fingerprint_grouped"
    else:
        cache_dir = str(getattr(args, "ustc_cache_dir", "")).strip()
        if cache_dir:
            cached = Path(cache_dir) / (
                f"seed{experiment.seed}_max{args.ustc_max_per_class}.csv"
            )
            if not cached.exists():
                raise FileNotFoundError(
                    f"missing USTC-TFC2016 stratified cache: {cached}"
                )
            csv_path = str(cached)
        else:
            csv_path = args.ustc_csv
        config = "configs/ustc_tfc2016_nfstream.json"
        benign = "Benign"
        maximum = args.ustc_max_per_class
        split = "capture_grouped"
    command = [
        sys.executable,
        "train_hybrid_open_set.py",
        "--csv",
        csv_path,
        "--config",
        config,
        "--unknown-classes",
        experiment.unknown_classes,
        "--benign-class",
        benign,
        "--max-per-class",
        str(maximum),
        "--estimators",
        str(args.estimators),
        "--jobs",
        str(args.model_jobs),
        "--split-strategy",
        split,
        "--risk-selection",
        effective_risk_selection(experiment, args),
        "--risk-policy-name",
        risk_policy_name(args),
        "--modality-gate-minimum-gain",
        str(getattr(args, "modality_gate_minimum_gain", 0.02)),
        "--conflict-fallback-minimum-gain",
        str(getattr(args, "conflict_fallback_minimum_gain", 0.055)),
        "--joint-fallback-minimum-gain",
        str(getattr(args, "joint_fallback_minimum_gain", 0.055)),
        "--density-gate-minimum-gain",
        str(getattr(args, "density_gate_minimum_gain", 0.02)),
        "--density-gate-minimum-known-classes",
        str(getattr(args, "density_gate_minimum_known_classes", 8)),
        "--density-gate-blend-weight",
        str(getattr(args, "density_gate_blend_weight", 0.05)),
        "--pseudo-unknown-max-alpha",
        str(getattr(args, "pseudo_unknown_max_alpha", 1.0)),
        "--pseudo-unknown-min-fold-gain",
        str(getattr(args, "pseudo_unknown_min_fold_gain", -0.125)),
        "--pseudo-unknown-local-rank-bins",
        str(getattr(args, "pseudo_unknown_local_rank_bins", 5)),
        "--pseudo-unknown-local-rank-beta",
        str(getattr(args, "pseudo_unknown_local_rank_beta", 1.0)),
        "--boundary-hard-pseudo-fraction",
        str(getattr(args, "boundary_hard_pseudo_fraction", 0.5)),
        "--boundary-interpolation",
        str(getattr(args, "boundary_interpolation", 0.5)),
        "--boundary-max-per-task",
        str(getattr(args, "boundary_max_per_task", 512)),
        "--boundary-training-objective",
        str(getattr(args, "boundary_training_objective", "pointwise")),
        "--structural-gate-minimum-gain",
        str(getattr(args, "structural_gate_minimum_gain", 0.02)),
        "--seed",
        str(experiment.seed),
        "--output-dir",
        experiment.output_dir,
    ]
    if getattr(args, "risk_selection", "") == "fixed_named":
        fixed_risk_name = str(getattr(args, "fixed_risk_name", "")).strip()
        if not fixed_risk_name:
            raise ValueError("--fixed-risk-name is required for fixed_named")
        command.extend(["--fixed-risk-name", fixed_risk_name])
    if getattr(args, "foss_structural_view", False):
        command.append("--foss-structural-view")
        command.extend(
            [
                "--foss-structural-view-mode",
                getattr(args, "foss_structural_view_mode", "tree"),
                "--foss-structural-view-scope",
                getattr(args, "foss_structural_view_scope", "full"),
                "--structural-support-weights",
                getattr(args, "structural_support_weights", "0,0.1,0.25,0.5,1.0"),
                "--structural-support-minimum-gain",
                str(getattr(args, "structural_support_minimum_gain", 0.005)),
            ]
        )
    command.extend(
        [
            "--test-corruption-kind",
            str(getattr(args, "test_corruption_kind", "none")),
            "--test-corruption-modality",
            str(getattr(args, "test_corruption_modality", 0)),
            "--test-corruption-severity",
            str(getattr(args, "test_corruption_severity", 0.0)),
            "--test-corruption-seed",
            str(getattr(args, "test_corruption_seed", 20260717)),
            "--train-label-noise",
            str(getattr(args, "train_label_noise", 0.0)),
        ]
    )
    return command


def run_one(experiment: Experiment, args: argparse.Namespace) -> dict[str, object]:
    output_dir = Path(experiment.output_dir)
    metrics_path = output_dir / "metrics.json"
    log_path = output_dir / "run.log"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = command_for(experiment, args)
    provenance = build_run_provenance(experiment, command)
    if freeze_or_validate_provenance(output_dir, provenance, (metrics_path,)):
        attach_metrics_arguments(metrics_path, command)
        return {
            **asdict(experiment),
            "status": "skipped",
            "elapsed_seconds": 0.0,
            "command": command,
            "parameter_fingerprint": provenance["parameter_fingerprint"],
        }
    started = time.perf_counter()
    with log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    elapsed = time.perf_counter() - started
    if completed.returncode == 0 and metrics_path.exists():
        attach_metrics_arguments(metrics_path, command)
    status = "completed" if completed.returncode == 0 and metrics_path.exists() else "failed"
    return {
        **asdict(experiment),
        "status": status,
        "return_code": completed.returncode,
        "elapsed_seconds": elapsed,
        "command": command,
        "parameter_fingerprint": provenance["parameter_fingerprint"],
    }


def write_manifest(
    output_root: Path,
    args: argparse.Namespace,
    experiments: list[Experiment],
    results: list[dict[str, object]],
    state: str,
) -> dict[str, object]:
    total = len(experiments)
    manifest = {
        "state": state,
        "arguments": vars(args),
        "number_of_experiments": total,
        "reported": len(results),
        "pending": total - len(results),
        "completed": sum(result["status"] == "completed" for result in results),
        "skipped": sum(result["status"] == "skipped" for result in results),
        "failed": sum(result["status"] == "failed" for result in results),
        "runs": sorted(
            results,
            key=lambda value: (
                value["suite"], value["scenario"], value["seed"]
            ),
        ),
    }
    temporary = output_root / "manifest.json.tmp"
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(output_root / "manifest.json")
    return manifest


def main() -> None:
    args = parse_arguments()
    experiments = build_experiments(args)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    write_manifest(output_root, args, experiments, results, "running")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run_one, experiment, args): experiment
            for experiment in experiments
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            write_manifest(output_root, args, experiments, results, "running")
            print(
                f"{result['status']}: {result['suite']}/{result['scenario']} "
                f"seed={result['seed']} elapsed={result['elapsed_seconds']:.1f}s",
                flush=True,
            )
    manifest = write_manifest(output_root, args, experiments, results, "complete")
    if manifest["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
