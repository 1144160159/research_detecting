# HCRP-OSD strict-v4 pilot

- Evidence level: same-split six-scenario pilot.
- Implementation: paper-structure adapter; not an author-code reproduction.
- Decision: `hold_hcrp_at_pilot`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean unknown rank |
|---|---:|---:|---:|---:|---:|---:|
| HCRP-OSD adapter | 0.658410 | 0.718892 | 0.466669 | 0.509114 | 0.545018 | 11.000 |
| CAEOS | 0.710071 | 0.816769 | 0.645206 | 0.395800 | 0.573549 | 3.500 |

## Oriented HCRP-OSD delta versus CAEOS

- `known_macro_f1`: -0.051661
- `unknown_auroc`: -0.097877
- `unknown_aupr`: -0.178537
- `unknown_fpr95`: -0.113314
- `oscr`: -0.028531

## Sixteen-method ranking

1. `opendetect`: mean unknown rank 2.500
2. `mlp_openmax`: mean unknown rank 3.250
3. `mlp_knn`: mean unknown rank 3.250
4. `caeos`: mean unknown rank 3.500
5. `mlp_vim`: mean unknown rank 5.250
6. `mlp_mahalanobis`: mean unknown rank 6.750
7. `mlp_energy`: mean unknown rank 6.750
8. `mlp_energy_cea`: mean unknown rank 8.000
9. `mlp_relative_mahalanobis`: mean unknown rank 8.250
10. `mlp_scale`: mean unknown rank 10.000
11. `mlp_max_logit`: mean unknown rank 10.500
12. `hcrp_osd_adapter`: mean unknown rank 11.000
13. `mlp_nci`: mean unknown rank 12.500
14. `mlp_nci_cea`: mean unknown rank 13.500
15. `mlp_msp`: mean unknown rank 15.500
16. `ronetc`: mean unknown rank 15.500
