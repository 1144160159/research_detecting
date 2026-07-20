# Neural comparison strict v2

Inference unit: scenario. Seed repeats are averaged within scenario before inference.
CI: scenario-block percentile bootstrap. Wilcoxon p-values use Holm correction within each scope.
Positive oriented deltas favor the gate method; FPR95 is sign-reversed.
Validated seeds: [7, 11, 19, 23, 37]; inference seeds: [7, 11, 19, 23, 37]; excluded from inference: [].

## Coverage

- edge_iiot: 70 tasks; 490 paired split-fingerprint checks; validated
- nf_cse: 70 tasks; 490 paired split-fingerprint checks; validated
- ustc_tfc2016: 50 tasks; 350 paired split-fingerprint checks; validated

## Global

Runs: 190; scenario units: 38.

| Method | Metric | Gate | Baseline | Oriented delta [95% CI] | dz | Rank-biserial | W/T/L | p | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| arpl | known_macro_f1 | 0.877701 | 0.807637 | +0.070064 [+0.052801, +0.087771] | 1.268 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| arpl | unknown_auroc | 0.839183 | 0.691587 | +0.147597 [+0.077589, +0.219401] | 0.647 | 0.649 | 28/0/10 | 0.00028 | 0.00112 |
| arpl | unknown_aupr | 0.737376 | 0.557072 | +0.180304 [+0.104507, +0.256075] | 0.741 | 0.703 | 30/0/8 | 6.78e-05 | 0.000407 |
| arpl | unknown_fpr95 | 0.401565 | 0.555520 | +0.153955 [+0.049891, +0.259297] | 0.458 | 0.441 | 24/0/14 | 0.0169 | 0.0198 |
| arpl | oscr | 0.755264 | 0.624621 | +0.130643 [+0.074346, +0.190753] | 0.703 | 0.744 | 33/0/5 | 2.06e-05 | 0.000165 |
| cade | known_macro_f1 | 0.877701 | 0.738231 | +0.139470 [+0.106938, +0.173899] | 1.292 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| cade | unknown_auroc | 0.839183 | 0.596176 | +0.243007 [+0.185120, +0.300259] | 1.325 | 0.906 | 32/0/6 | 3.14e-08 | 7.21e-07 |
| cade | unknown_aupr | 0.737376 | 0.474151 | +0.263225 [+0.209199, +0.314549] | 1.537 | 0.957 | 35/0/3 | 1.23e-09 | 3.07e-08 |
| cade | unknown_fpr95 | 0.401565 | 0.697514 | +0.295949 [+0.212097, +0.380569] | 1.097 | 0.822 | 27/0/11 | 1.38e-06 | 1.79e-05 |
| cade | oscr | 0.755264 | 0.441363 | +0.313901 [+0.262195, +0.364811] | 1.904 | 0.995 | 37/0/1 | 2.18e-11 | 6.11e-10 |
| closr | known_macro_f1 | 0.877701 | 0.694292 | +0.183410 [+0.143457, +0.223917] | 1.436 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| closr | unknown_auroc | 0.839183 | 0.584712 | +0.254471 [+0.183933, +0.322666] | 1.150 | 0.892 | 34/0/4 | 6.33e-08 | 1.14e-06 |
| closr | unknown_aupr | 0.737376 | 0.494232 | +0.243144 [+0.182446, +0.300588] | 1.294 | 0.889 | 34/0/4 | 7.24e-08 | 1.23e-06 |
| closr | unknown_fpr95 | 0.401565 | 0.678789 | +0.277224 [+0.170893, +0.378223] | 0.837 | 0.744 | 28/0/10 | 2.06e-05 | 0.000165 |
| closr | oscr | 0.755264 | 0.423947 | +0.331317 [+0.263849, +0.393297] | 1.597 | 0.949 | 36/0/2 | 2.23e-09 | 5.36e-08 |
| foss | known_macro_f1 | 0.877701 | 0.599615 | +0.278086 [+0.232711, +0.323264] | 1.940 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| foss | unknown_auroc | 0.839183 | 0.561910 | +0.277273 [+0.208475, +0.339461] | 1.351 | 0.897 | 36/0/2 | 4.8e-08 | 1.01e-06 |
| foss | unknown_aupr | 0.737376 | 0.468244 | +0.269132 [+0.206165, +0.322240] | 1.458 | 0.895 | 35/0/3 | 5.52e-08 | 1.05e-06 |
| foss | unknown_fpr95 | 0.401565 | 0.808725 | +0.407161 [+0.295161, +0.508586] | 1.197 | 0.892 | 34/2/2 | 1.45e-07 | 2.22e-06 |
| foss | oscr | 0.755264 | 0.304616 | +0.450648 [+0.375745, +0.515538] | 2.026 | 0.973 | 37/0/1 | 3.13e-10 | 8.45e-09 |
| opendetect | known_macro_f1 | 0.877701 | 0.836475 | +0.041226 [+0.032691, +0.050310] | 1.455 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| opendetect | unknown_auroc | 0.839183 | 0.725590 | +0.113594 [+0.059264, +0.171714] | 0.632 | 0.676 | 29/0/9 | 0.000141 | 0.000705 |
| opendetect | unknown_aupr | 0.737376 | 0.587420 | +0.149956 [+0.096336, +0.204610] | 0.873 | 0.798 | 32/0/6 | 3.41e-06 | 4.09e-05 |
| opendetect | unknown_fpr95 | 0.401565 | 0.546521 | +0.144956 [+0.044228, +0.242624] | 0.467 | 0.479 | 25/0/13 | 0.00914 | 0.0198 |
| opendetect | oscr | 0.755264 | 0.637653 | +0.117611 [+0.071625, +0.164409] | 0.790 | 0.784 | 32/0/6 | 5.49e-06 | 5.49e-05 |
| ronetc | known_macro_f1 | 0.877701 | 0.812653 | +0.065048 [+0.054534, +0.075789] | 1.918 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| ronetc | unknown_auroc | 0.839183 | 0.634555 | +0.204629 [+0.128522, +0.284018] | 0.830 | 0.795 | 30/0/8 | 3.76e-06 | 4.13e-05 |
| ronetc | unknown_aupr | 0.737376 | 0.495547 | +0.241829 [+0.170544, +0.313872] | 1.040 | 0.854 | 32/0/6 | 3.67e-07 | 5.14e-06 |
| ronetc | unknown_fpr95 | 0.401565 | 0.582191 | +0.180626 [+0.069509, +0.292551] | 0.511 | 0.498 | 25/0/13 | 0.0066 | 0.0198 |
| ronetc | oscr | 0.755264 | 0.590936 | +0.164328 [+0.101617, +0.231918] | 0.786 | 0.784 | 30/0/8 | 5.49e-06 | 5.49e-05 |
| sieve | known_macro_f1 | 0.877701 | 0.698673 | +0.179028 [+0.141749, +0.218154] | 1.473 | 1.000 | 38/0/0 | 7.28e-12 | 2.55e-10 |
| sieve | unknown_auroc | 0.839183 | 0.659416 | +0.179768 [+0.128821, +0.229165] | 1.122 | 0.897 | 33/0/5 | 4.8e-08 | 1.01e-06 |
| sieve | unknown_aupr | 0.737376 | 0.514563 | +0.222814 [+0.167746, +0.276023] | 1.282 | 0.906 | 32/0/6 | 3.14e-08 | 7.21e-07 |
| sieve | unknown_fpr95 | 0.401565 | 0.680560 | +0.278995 [+0.198901, +0.360328] | 1.086 | 0.876 | 32/0/6 | 1.39e-07 | 2.22e-06 |
| sieve | oscr | 0.755264 | 0.497123 | +0.258141 [+0.208941, +0.306630] | 1.652 | 0.973 | 37/0/1 | 3.13e-10 | 8.45e-09 |

### Resource reporting

Missing measurements are reported as NA; they are never imputed as zero.

| Method | Resource | Status | Recorded/Missing | Mean |
|---|---|---|---:|---:|
| confirmed_composite_caeos_strict_v2_20260717 | training_seconds | missing | 0/190 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | inference_seconds | missing | 0/190 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | peak_gpu_memory_mb | missing | 0/190 | NA |
| arpl | training_seconds | recorded | 190/0 | 37.573260 |
| arpl | inference_seconds | missing | 0/190 | NA |
| arpl | peak_gpu_memory_mb | missing | 0/190 | NA |
| cade | training_seconds | recorded | 190/0 | 228.330008 |
| cade | inference_seconds | missing | 0/190 | NA |
| cade | peak_gpu_memory_mb | missing | 0/190 | NA |
| closr | training_seconds | recorded | 190/0 | 97.611669 |
| closr | inference_seconds | missing | 0/190 | NA |
| closr | peak_gpu_memory_mb | missing | 0/190 | NA |
| foss | training_seconds | recorded | 190/0 | 1.419023 |
| foss | inference_seconds | missing | 0/190 | NA |
| foss | peak_gpu_memory_mb | missing | 0/190 | NA |
| opendetect | training_seconds | recorded | 190/0 | 257.140399 |
| opendetect | inference_seconds | missing | 0/190 | NA |
| opendetect | peak_gpu_memory_mb | missing | 0/190 | NA |
| ronetc | training_seconds | recorded | 190/0 | 121.861363 |
| ronetc | inference_seconds | missing | 0/190 | NA |
| ronetc | peak_gpu_memory_mb | missing | 0/190 | NA |
| sieve | training_seconds | recorded | 190/0 | 295.050853 |
| sieve | inference_seconds | missing | 0/190 | NA |
| sieve | peak_gpu_memory_mb | missing | 0/190 | NA |

## Suite: edge_iiot

Runs: 70; scenario units: 14.

| Method | Metric | Gate | Baseline | Oriented delta [95% CI] | dz | Rank-biserial | W/T/L | p | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| arpl | known_macro_f1 | 0.927941 | 0.787475 | +0.140465 [+0.134528, +0.145802] | 12.274 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| arpl | unknown_auroc | 0.836599 | 0.614611 | +0.221988 [+0.101763, +0.355230] | 0.873 | 0.867 | 11/0/3 | 0.00232 | 0.0232 |
| arpl | unknown_aupr | 0.733479 | 0.473416 | +0.260063 [+0.149159, +0.378707] | 1.136 | 0.943 | 13/0/1 | 0.00061 | 0.00977 |
| arpl | unknown_fpr95 | 0.517759 | 0.675217 | +0.157457 [-0.031080, +0.351007] | 0.416 | 0.448 | 8/0/6 | 0.153 | 0.459 |
| arpl | oscr | 0.764639 | 0.531584 | +0.233055 [+0.136153, +0.340372] | 1.127 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| cade | known_macro_f1 | 0.927941 | 0.651392 | +0.276549 [+0.265094, +0.288074] | 11.984 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| cade | unknown_auroc | 0.836599 | 0.555683 | +0.280915 [+0.175771, +0.380164] | 1.386 | 0.905 | 12/0/2 | 0.00122 | 0.0146 |
| cade | unknown_aupr | 0.733479 | 0.444080 | +0.289399 [+0.182161, +0.389996] | 1.410 | 0.924 | 12/0/2 | 0.000854 | 0.0111 |
| cade | unknown_fpr95 | 0.517759 | 0.783765 | +0.266006 [+0.133746, +0.413986] | 0.960 | 0.810 | 10/0/4 | 0.00525 | 0.0367 |
| cade | oscr | 0.764639 | 0.330129 | +0.434510 [+0.376354, +0.497179] | 3.585 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| closr | known_macro_f1 | 0.927941 | 0.583841 | +0.344100 [+0.332713, +0.355604] | 15.174 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| closr | unknown_auroc | 0.836599 | 0.554887 | +0.281711 [+0.211701, +0.357462] | 1.994 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| closr | unknown_aupr | 0.733479 | 0.433113 | +0.300366 [+0.237157, +0.370154] | 2.311 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| closr | unknown_fpr95 | 0.517759 | 0.806020 | +0.288261 [+0.132634, +0.445249] | 0.918 | 0.771 | 10/0/4 | 0.00854 | 0.0513 |
| closr | oscr | 0.764639 | 0.333040 | +0.431598 [+0.379051, +0.486837] | 4.063 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| foss | known_macro_f1 | 0.927941 | 0.487322 | +0.440619 [+0.422178, +0.460508] | 11.599 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| foss | unknown_auroc | 0.836599 | 0.511168 | +0.325431 [+0.260999, +0.386282] | 2.641 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| foss | unknown_aupr | 0.733479 | 0.397091 | +0.336389 [+0.272117, +0.393966] | 2.785 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| foss | unknown_fpr95 | 0.517759 | 0.897672 | +0.379912 [+0.250341, +0.508698] | 1.487 | 1.000 | 12/2/0 | 0.000488 | 0.0083 |
| foss | oscr | 0.764639 | 0.172067 | +0.592571 [+0.554540, +0.635095] | 7.398 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| opendetect | known_macro_f1 | 0.927941 | 0.852150 | +0.075790 [+0.069032, +0.082049] | 5.804 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| opendetect | unknown_auroc | 0.836599 | 0.714953 | +0.121645 [+0.035528, +0.217222] | 0.673 | 0.676 | 10/0/4 | 0.0245 | 0.0981 |
| opendetect | unknown_aupr | 0.733479 | 0.573505 | +0.159974 [+0.068923, +0.251483] | 0.877 | 0.733 | 11/0/3 | 0.0134 | 0.0671 |
| opendetect | unknown_fpr95 | 0.517759 | 0.693871 | +0.176112 [-0.016293, +0.370987] | 0.457 | 0.448 | 9/0/5 | 0.153 | 0.459 |
| opendetect | oscr | 0.764639 | 0.603558 | +0.161081 [+0.084277, +0.244179] | 1.019 | 0.848 | 11/0/3 | 0.00305 | 0.0275 |
| ronetc | known_macro_f1 | 0.927941 | 0.822089 | +0.105851 [+0.098432, +0.112906] | 7.392 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| ronetc | unknown_auroc | 0.836599 | 0.577194 | +0.259404 [+0.117429, +0.411613] | 0.874 | 0.848 | 11/0/3 | 0.00305 | 0.0275 |
| ronetc | unknown_aupr | 0.733479 | 0.460905 | +0.272574 [+0.157683, +0.393629] | 1.155 | 0.943 | 13/0/1 | 0.00061 | 0.00977 |
| ronetc | unknown_fpr95 | 0.517759 | 0.705203 | +0.187444 [-0.040119, +0.410630] | 0.423 | 0.429 | 9/0/5 | 0.173 | 0.459 |
| ronetc | oscr | 0.764639 | 0.520286 | +0.244353 [+0.120048, +0.383228] | 0.935 | 0.886 | 11/0/3 | 0.00171 | 0.0188 |
| sieve | known_macro_f1 | 0.927941 | 0.594435 | +0.333505 [+0.322204, +0.345911] | 14.078 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| sieve | unknown_auroc | 0.836599 | 0.618807 | +0.217791 [+0.141004, +0.294711] | 1.425 | 0.981 | 13/0/1 | 0.000244 | 0.00464 |
| sieve | unknown_aupr | 0.733479 | 0.454579 | +0.278900 [+0.194667, +0.363974] | 1.659 | 0.962 | 13/0/1 | 0.000366 | 0.00659 |
| sieve | unknown_fpr95 | 0.517759 | 0.778080 | +0.260321 [+0.136553, +0.402257] | 0.982 | 0.943 | 12/0/2 | 0.00061 | 0.00977 |
| sieve | oscr | 0.764639 | 0.366010 | +0.398629 [+0.352448, +0.446744] | 4.242 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |

### Resource reporting

Missing measurements are reported as NA; they are never imputed as zero.

| Method | Resource | Status | Recorded/Missing | Mean |
|---|---|---|---:|---:|
| confirmed_composite_caeos_strict_v2_20260717 | training_seconds | missing | 0/70 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | inference_seconds | missing | 0/70 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | peak_gpu_memory_mb | missing | 0/70 | NA |
| arpl | training_seconds | recorded | 70/0 | 39.576187 |
| arpl | inference_seconds | missing | 0/70 | NA |
| arpl | peak_gpu_memory_mb | missing | 0/70 | NA |
| cade | training_seconds | recorded | 70/0 | 217.326225 |
| cade | inference_seconds | missing | 0/70 | NA |
| cade | peak_gpu_memory_mb | missing | 0/70 | NA |
| closr | training_seconds | recorded | 70/0 | 95.249860 |
| closr | inference_seconds | missing | 0/70 | NA |
| closr | peak_gpu_memory_mb | missing | 0/70 | NA |
| foss | training_seconds | recorded | 70/0 | 1.367360 |
| foss | inference_seconds | missing | 0/70 | NA |
| foss | peak_gpu_memory_mb | missing | 0/70 | NA |
| opendetect | training_seconds | recorded | 70/0 | 225.014797 |
| opendetect | inference_seconds | missing | 0/70 | NA |
| opendetect | peak_gpu_memory_mb | missing | 0/70 | NA |
| ronetc | training_seconds | recorded | 70/0 | 171.596499 |
| ronetc | inference_seconds | missing | 0/70 | NA |
| ronetc | peak_gpu_memory_mb | missing | 0/70 | NA |
| sieve | training_seconds | recorded | 70/0 | 302.486694 |
| sieve | inference_seconds | missing | 0/70 | NA |
| sieve | peak_gpu_memory_mb | missing | 0/70 | NA |

## Suite: nf_cse

Runs: 70; scenario units: 14.

| Method | Metric | Gate | Baseline | Oriented delta [95% CI] | dz | Rank-biserial | W/T/L | p | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| arpl | known_macro_f1 | 0.788887 | 0.763471 | +0.025416 [+0.021900, +0.029371] | 3.432 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| arpl | unknown_auroc | 0.838957 | 0.722857 | +0.116100 [-0.018968, +0.249858] | 0.435 | 0.429 | 8/0/6 | 0.173 | 0.812 |
| arpl | unknown_aupr | 0.721551 | 0.577334 | +0.144217 [-0.016215, +0.304241] | 0.457 | 0.448 | 8/0/6 | 0.153 | 0.812 |
| arpl | unknown_fpr95 | 0.271590 | 0.428001 | +0.156411 [-0.025522, +0.337096] | 0.442 | 0.448 | 9/0/5 | 0.153 | 0.812 |
| arpl | oscr | 0.717072 | 0.655405 | +0.061667 [-0.034535, +0.157272] | 0.326 | 0.333 | 9/0/5 | 0.296 | 0.812 |
| cade | known_macro_f1 | 0.788887 | 0.741184 | +0.047703 [+0.041639, +0.053932] | 3.898 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| cade | unknown_auroc | 0.838957 | 0.622408 | +0.216549 [+0.116968, +0.310474] | 1.138 | 0.810 | 11/0/3 | 0.00525 | 0.11 |
| cade | unknown_aupr | 0.721551 | 0.481420 | +0.240131 [+0.159412, +0.320545] | 1.496 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| cade | unknown_fpr95 | 0.271590 | 0.579453 | +0.307863 [+0.160405, +0.449681] | 1.057 | 0.714 | 9/0/5 | 0.0166 | 0.266 |
| cade | oscr | 0.717072 | 0.484297 | +0.232775 [+0.155020, +0.310508] | 1.475 | 0.981 | 13/0/1 | 0.000244 | 0.00659 |
| closr | known_macro_f1 | 0.788887 | 0.724307 | +0.064580 [+0.058333, +0.070493] | 5.329 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| closr | unknown_auroc | 0.838957 | 0.615200 | +0.223757 [+0.067529, +0.367560] | 0.748 | 0.714 | 11/0/3 | 0.0166 | 0.266 |
| closr | unknown_aupr | 0.721551 | 0.521794 | +0.199756 [+0.079506, +0.304971] | 0.901 | 0.714 | 11/0/3 | 0.0166 | 0.266 |
| closr | unknown_fpr95 | 0.271590 | 0.485061 | +0.213471 [+0.031801, +0.375019] | 0.624 | 0.619 | 10/0/4 | 0.0419 | 0.423 |
| closr | oscr | 0.717072 | 0.481463 | +0.235610 [+0.099491, +0.365219] | 0.890 | 0.810 | 12/0/2 | 0.00525 | 0.11 |
| foss | known_macro_f1 | 0.788887 | 0.669304 | +0.119583 [+0.105202, +0.134654] | 4.072 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| foss | unknown_auroc | 0.838957 | 0.599579 | +0.239378 [+0.087137, +0.361574] | 0.863 | 0.733 | 13/0/1 | 0.0134 | 0.228 |
| foss | unknown_aupr | 0.721551 | 0.514615 | +0.206935 [+0.078133, +0.310088] | 0.871 | 0.714 | 12/0/2 | 0.0166 | 0.266 |
| foss | unknown_fpr95 | 0.271590 | 0.632612 | +0.361023 [+0.130360, +0.545547] | 0.861 | 0.752 | 13/0/1 | 0.0107 | 0.193 |
| foss | oscr | 0.717072 | 0.430198 | +0.286874 [+0.145888, +0.405645] | 1.125 | 0.867 | 13/0/1 | 0.00232 | 0.051 |
| opendetect | known_macro_f1 | 0.788887 | 0.771237 | +0.017650 [+0.014780, +0.020831] | 2.979 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| opendetect | unknown_auroc | 0.838957 | 0.718400 | +0.120557 [+0.004280, +0.236207] | 0.526 | 0.638 | 11/0/3 | 0.0353 | 0.423 |
| opendetect | unknown_aupr | 0.721551 | 0.562810 | +0.158740 [+0.052871, +0.265279] | 0.748 | 0.771 | 12/0/2 | 0.00854 | 0.162 |
| opendetect | unknown_fpr95 | 0.271590 | 0.415947 | +0.144357 [-0.013266, +0.304818] | 0.460 | 0.467 | 8/0/6 | 0.135 | 0.812 |
| opendetect | oscr | 0.717072 | 0.631440 | +0.085632 [-0.002850, +0.170010] | 0.496 | 0.581 | 11/0/3 | 0.058 | 0.445 |
| ronetc | known_macro_f1 | 0.788887 | 0.751682 | +0.037205 [+0.030419, +0.043445] | 2.927 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| ronetc | unknown_auroc | 0.838957 | 0.668076 | +0.170881 [+0.033984, +0.301450] | 0.641 | 0.600 | 9/0/5 | 0.0494 | 0.445 |
| ronetc | unknown_aupr | 0.721551 | 0.506970 | +0.214581 [+0.058719, +0.360196] | 0.717 | 0.638 | 9/0/5 | 0.0353 | 0.423 |
| ronetc | unknown_fpr95 | 0.271590 | 0.466791 | +0.195202 [+0.033242, +0.351682] | 0.616 | 0.600 | 9/0/5 | 0.0494 | 0.445 |
| ronetc | oscr | 0.717072 | 0.627329 | +0.089743 [-0.005520, +0.182695] | 0.474 | 0.467 | 9/0/5 | 0.135 | 0.812 |
| sieve | known_macro_f1 | 0.788887 | 0.704568 | +0.084319 [+0.072667, +0.097533] | 3.429 | 1.000 | 14/0/0 | 0.000122 | 0.00427 |
| sieve | unknown_auroc | 0.838957 | 0.620664 | +0.218293 [+0.128129, +0.294119] | 1.313 | 0.886 | 13/0/1 | 0.00171 | 0.0393 |
| sieve | unknown_aupr | 0.721551 | 0.451007 | +0.270544 [+0.187866, +0.345411] | 1.726 | 0.943 | 13/0/1 | 0.00061 | 0.0153 |
| sieve | unknown_fpr95 | 0.271590 | 0.630719 | +0.359129 [+0.237626, +0.461749] | 1.612 | 0.943 | 13/0/1 | 0.00061 | 0.0153 |
| sieve | oscr | 0.717072 | 0.502249 | +0.214824 [+0.145781, +0.271613] | 1.740 | 0.962 | 13/0/1 | 0.000366 | 0.00952 |

### Resource reporting

Missing measurements are reported as NA; they are never imputed as zero.

| Method | Resource | Status | Recorded/Missing | Mean |
|---|---|---|---:|---:|
| confirmed_composite_caeos_strict_v2_20260717 | training_seconds | missing | 0/70 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | inference_seconds | missing | 0/70 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | peak_gpu_memory_mb | missing | 0/70 | NA |
| arpl | training_seconds | recorded | 70/0 | 30.334448 |
| arpl | inference_seconds | missing | 0/70 | NA |
| arpl | peak_gpu_memory_mb | missing | 0/70 | NA |
| cade | training_seconds | recorded | 70/0 | 198.864631 |
| cade | inference_seconds | missing | 0/70 | NA |
| cade | peak_gpu_memory_mb | missing | 0/70 | NA |
| closr | training_seconds | recorded | 70/0 | 96.141194 |
| closr | inference_seconds | missing | 0/70 | NA |
| closr | peak_gpu_memory_mb | missing | 0/70 | NA |
| foss | training_seconds | recorded | 70/0 | 1.206634 |
| foss | inference_seconds | missing | 0/70 | NA |
| foss | peak_gpu_memory_mb | missing | 0/70 | NA |
| opendetect | training_seconds | recorded | 70/0 | 199.265608 |
| opendetect | inference_seconds | missing | 0/70 | NA |
| opendetect | peak_gpu_memory_mb | missing | 0/70 | NA |
| ronetc | training_seconds | recorded | 70/0 | 74.251968 |
| ronetc | inference_seconds | missing | 0/70 | NA |
| ronetc | peak_gpu_memory_mb | missing | 0/70 | NA |
| sieve | training_seconds | recorded | 70/0 | 160.006535 |
| sieve | inference_seconds | missing | 0/70 | NA |
| sieve | peak_gpu_memory_mb | missing | 0/70 | NA |

## Suite: ustc_tfc2016

Runs: 50; scenario units: 10.

| Method | Metric | Gate | Baseline | Oriented delta [95% CI] | dz | Rank-biserial | W/T/L | p | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| arpl | known_macro_f1 | 0.931705 | 0.897697 | +0.034008 [+0.031202, +0.036487] | 7.682 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| arpl | unknown_auroc | 0.843119 | 0.755575 | +0.087544 [+0.052495, +0.120881] | 1.519 | 0.964 | 9/0/1 | 0.00391 | 0.0742 |
| arpl | unknown_aupr | 0.764988 | 0.645823 | +0.119164 [+0.064035, +0.171175] | 1.309 | 0.927 | 9/0/1 | 0.00586 | 0.0762 |
| arpl | unknown_fpr95 | 0.420857 | 0.566470 | +0.145613 [-0.008717, +0.317718] | 0.524 | 0.455 | 7/0/3 | 0.232 | 0.422 |
| arpl | oscr | 0.795608 | 0.711776 | +0.083832 [+0.055042, +0.114646] | 1.661 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| cade | known_macro_f1 | 0.931705 | 0.855672 | +0.076033 [+0.069243, +0.082536] | 6.618 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| cade | unknown_auroc | 0.843119 | 0.616141 | +0.226978 [+0.140525, +0.317362] | 1.493 | 0.964 | 9/0/1 | 0.00391 | 0.0742 |
| cade | unknown_aupr | 0.764988 | 0.506075 | +0.258913 [+0.172003, +0.340611] | 1.803 | 0.964 | 9/0/1 | 0.00391 | 0.0742 |
| cade | unknown_fpr95 | 0.420857 | 0.742048 | +0.321190 [+0.171065, +0.465708] | 1.274 | 0.891 | 8/0/2 | 0.00977 | 0.107 |
| cade | oscr | 0.795608 | 0.536984 | +0.258624 [+0.179640, +0.338716] | 1.909 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| closr | known_macro_f1 | 0.931705 | 0.806900 | +0.124805 [+0.117213, +0.132081] | 9.779 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| closr | unknown_auroc | 0.843119 | 0.583785 | +0.259335 [+0.147197, +0.381768] | 1.288 | 0.964 | 9/0/1 | 0.00391 | 0.0742 |
| closr | unknown_aupr | 0.764988 | 0.541213 | +0.223775 [+0.110223, +0.345814] | 1.102 | 0.891 | 9/0/1 | 0.00977 | 0.107 |
| closr | unknown_fpr95 | 0.420857 | 0.771884 | +0.351027 [+0.129482, +0.554800] | 0.984 | 0.818 | 8/0/2 | 0.0195 | 0.137 |
| closr | oscr | 0.795608 | 0.470695 | +0.324913 [+0.227049, +0.432871] | 1.890 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| foss | known_macro_f1 | 0.931705 | 0.659260 | +0.272445 [+0.254789, +0.290538] | 8.850 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| foss | unknown_auroc | 0.843119 | 0.580214 | +0.262905 [+0.156429, +0.373850] | 1.423 | 0.964 | 9/0/1 | 0.00391 | 0.0742 |
| foss | unknown_aupr | 0.764988 | 0.502938 | +0.262049 [+0.171377, +0.354600] | 1.675 | 0.964 | 9/0/1 | 0.00391 | 0.0742 |
| foss | unknown_fpr95 | 0.420857 | 0.930758 | +0.509901 [+0.308701, +0.696165] | 1.529 | 0.927 | 9/0/1 | 0.00586 | 0.0762 |
| foss | oscr | 0.795608 | 0.314370 | +0.481238 [+0.390787, +0.581968] | 2.974 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| opendetect | known_macro_f1 | 0.931705 | 0.905864 | +0.025842 [+0.023285, +0.028443] | 5.866 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| opendetect | unknown_auroc | 0.843119 | 0.750546 | +0.092573 [+0.040722, +0.151873] | 0.977 | 0.891 | 8/0/2 | 0.00977 | 0.107 |
| opendetect | unknown_aupr | 0.764988 | 0.641355 | +0.123632 [+0.069654, +0.167601] | 1.463 | 0.891 | 9/0/1 | 0.00977 | 0.107 |
| opendetect | unknown_fpr95 | 0.420857 | 0.523034 | +0.102176 [-0.010122, +0.213531] | 0.543 | 0.636 | 8/0/2 | 0.084 | 0.42 |
| opendetect | oscr | 0.795608 | 0.694085 | +0.101523 [+0.055302, +0.155372] | 1.191 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| ronetc | known_macro_f1 | 0.931705 | 0.884801 | +0.046904 [+0.043497, +0.050453] | 7.922 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| ronetc | unknown_auroc | 0.843119 | 0.667931 | +0.175188 [+0.114657, +0.243643] | 1.567 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| ronetc | unknown_aupr | 0.764988 | 0.528056 | +0.236932 [+0.180759, +0.299194] | 2.368 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| ronetc | unknown_fpr95 | 0.420857 | 0.571533 | +0.150676 [-0.000811, +0.332710] | 0.520 | 0.491 | 7/0/3 | 0.193 | 0.422 |
| ronetc | oscr | 0.795608 | 0.638896 | +0.156712 [+0.102413, +0.220549] | 1.541 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| sieve | known_macro_f1 | 0.931705 | 0.836353 | +0.095352 [+0.086237, +0.103483] | 6.603 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |
| sieve | unknown_auroc | 0.843119 | 0.770521 | +0.072598 [+0.009946, +0.153193] | 0.603 | 0.709 | 7/0/3 | 0.0488 | 0.293 |
| sieve | unknown_aupr | 0.764988 | 0.687518 | +0.077470 [+0.003215, +0.151084] | 0.615 | 0.600 | 6/0/4 | 0.105 | 0.422 |
| sieve | unknown_fpr95 | 0.420857 | 0.613807 | +0.192950 [+0.033589, +0.365051] | 0.684 | 0.600 | 7/0/3 | 0.105 | 0.422 |
| sieve | oscr | 0.795608 | 0.673506 | +0.122102 [+0.067166, +0.191757] | 1.142 | 1.000 | 10/0/0 | 0.00195 | 0.0684 |

### Resource reporting

Missing measurements are reported as NA; they are never imputed as zero.

| Method | Resource | Status | Recorded/Missing | Mean |
|---|---|---|---:|---:|
| confirmed_composite_caeos_strict_v2_20260717 | training_seconds | missing | 0/50 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | inference_seconds | missing | 0/50 | NA |
| confirmed_composite_caeos_strict_v2_20260717 | peak_gpu_memory_mb | missing | 0/50 | NA |
| arpl | training_seconds | recorded | 50/0 | 44.903498 |
| arpl | inference_seconds | missing | 0/50 | NA |
| arpl | peak_gpu_memory_mb | missing | 0/50 | NA |
| cade | training_seconds | recorded | 50/0 | 284.986832 |
| cade | inference_seconds | missing | 0/50 | NA |
| cade | peak_gpu_memory_mb | missing | 0/50 | NA |
| closr | training_seconds | recorded | 50/0 | 102.976867 |
| closr | inference_seconds | missing | 0/50 | NA |
| closr | peak_gpu_memory_mb | missing | 0/50 | NA |
| foss | training_seconds | recorded | 50/0 | 1.788694 |
| foss | inference_seconds | missing | 0/50 | NA |
| foss | peak_gpu_memory_mb | missing | 0/50 | NA |
| opendetect | training_seconds | recorded | 50/0 | 383.140948 |
| opendetect | inference_seconds | missing | 0/50 | NA |
| opendetect | peak_gpu_memory_mb | missing | 0/50 | NA |
| ronetc | training_seconds | recorded | 50/0 | 118.885328 |
| ronetc | inference_seconds | missing | 0/50 | NA |
| ronetc | peak_gpu_memory_mb | missing | 0/50 | NA |
| sieve | training_seconds | recorded | 50/0 | 473.702723 |
| sieve | inference_seconds | missing | 0/50 | NA |
| sieve | peak_gpu_memory_mb | missing | 0/50 | NA |
