# Code Layout

## Authoritative paths

| Path | Role |
|---|---|
| `contracts/` | Machine-readable delivery, metric, and acceptance rules |
| `caeos/` | Reusable model, data, fusion, runtime, and contract library |
| `configs/` | Dataset and model configuration |
| `tests/` | Unit and protocol regression tests |
| `scripts/` | Shell launchers used only after their Python entrypoint is admitted |
| `reproducibility/` | Environment and reproducibility records |
| `results/`, `runs/` | Generated artifacts; never source-of-truth code |
| `sources/` | Literature/source material; never deployed as executable code |
| top-level `*.py` | Compatibility entrypoints and historical experiment tools |

The large flat top-level script set is retained because active GPU jobs import
or invoke those paths. It is a compatibility surface, not an endorsement that
every script is a current entrypoint.

## Canonical entrypoints for the current objective

| Concern | Entrypoints |
|---|---|
| Contract and metrics | `audit_project_contract.py`, `strict_v4_open_set_metric_contract_v2.py` |
| Engineering self-algorithm | `train_strict_v4_fhmm_stable_task_cuda.py`, `evaluate_strict_v4_fhmm_stable_confirmation.py` |
| Neural/paper backbone | `train_neural_open_set.py`, `run_neural_baseline_matrix.py` |
| Hybrid diagnostic | `evaluate_strict_v4_neural_empirical_tail_hybrid_screening.py` |
| Data preparation | `prepare_cicids2017_strict.py`, `prepare_cic_iot2023_strict.py`, `prepare_strict_v4_cicids2017_packet_sequences.py` |

An unlisted top-level script is historical or experimental until a protocol
document names it, its tests pass, and its result schema includes the current
contract version.

## Remote rule

`sync_to_gpu.cmd` publishes an immutable release under
`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/releases` and atomically
updates `CAEOS-EMTD/current`. Historical workspaces are under
`CAEOS-EMTD/legacy`; workspaces still referenced by watchers are under
`CAEOS-EMTD/active`. New experiments must start from `CAEOS-EMTD/current`.
