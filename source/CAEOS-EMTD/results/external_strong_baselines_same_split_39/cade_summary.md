# CADE same-split matrix summary

The calibrated protocol uses the 95th percentile of known validation risk. The official protocol uses the fixed CADE MAD threshold 3.5.

| Scope | Runs | Protocol | Known Macro-F1 | AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| global | 39 | calibrated | 0.877801 | 0.630395 | 0.604512 | 0.712898 | 0.562140 | 0.938337 | 0.118947 |
| global | 39 | official_mad35 | 0.877801 | 0.630395 | 0.604512 | 0.712898 | 0.562140 | 0.910171 | 0.182820 |
| doh | 9 | calibrated | 0.865653 | 0.523544 | 0.684103 | 0.899174 | 0.470240 | 0.919271 | 0.066833 |
| doh | 9 | official_mad35 | 0.865653 | 0.523544 | 0.684103 | 0.899174 | 0.470240 | 0.831038 | 0.170500 |
| hikari | 12 | calibrated | 0.941217 | 0.604984 | 0.675499 | 0.551725 | 0.589178 | 0.939161 | 0.040480 |
| hikari | 12 | official_mad35 | 0.941217 | 0.604984 | 0.675499 | 0.551725 | 0.589178 | 0.861963 | 0.321360 |
| mal_tls | 18 | calibrated | 0.841597 | 0.700762 | 0.517393 | 0.727208 | 0.590065 | 0.947322 | 0.197315 |
| mal_tls | 18 | official_mad35 | 0.841597 | 0.700762 | 0.517393 | 0.727208 | 0.590065 | 0.981876 | 0.096620 |

## Scenario AUROC

| Scenario | Runs | AUROC | Known Macro-F1 | Unknown reject (calibrated) | Unknown reject (MAD=3.5) |
|---|---:|---:|---:|---:|---:|
| doh/dns2tcp | 3 | 0.571590 | 0.887497 | 0.065500 | 0.139000 |
| doh/dnscat2 | 3 | 0.511736 | 0.848580 | 0.097833 | 0.276083 |
| doh/iodine | 3 | 0.487306 | 0.860882 | 0.037167 | 0.096417 |
| hikari/brutefoce | 3 | 0.741258 | 0.929170 | 0.095929 | 0.433187 |
| hikari/bruteforce_xml | 3 | 0.871442 | 0.922089 | 0.000168 | 0.720616 |
| hikari/probing | 3 | 0.484326 | 0.953896 | 0.065824 | 0.131636 |
| hikari/xmrigcc | 3 | 0.322910 | 0.959711 | 0.000000 | 0.000000 |
| mal_tls/caphaw | 3 | 0.734917 | 0.844010 | 0.136667 | 0.000000 |
| mal_tls/cobalt | 3 | 0.608193 | 0.836831 | 0.077778 | 0.001111 |
| mal_tls/panda | 3 | 0.731782 | 0.877201 | 0.052778 | 0.021111 |
| mal_tls/qakbot | 3 | 0.488706 | 0.833422 | 0.047778 | 0.000000 |
| mal_tls/scanners | 3 | 0.850751 | 0.829934 | 0.517778 | 0.429722 |
| mal_tls/tor | 3 | 0.790221 | 0.828185 | 0.351111 | 0.127778 |
