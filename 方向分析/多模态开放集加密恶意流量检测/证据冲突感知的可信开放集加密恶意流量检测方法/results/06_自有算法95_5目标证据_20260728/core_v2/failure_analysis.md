# strict-v4 self-algorithm operational gap analysis

## Conclusion

- The 95/5 target applies to the self algorithm only.
- Aggregate alert accuracy is 95.8889%; benign FPR is 4.5016%.
- Known attack type accuracy is 96.3626%; unknown attack recall is 72.9006%.
- Aggregate means are not sufficient: all-seed basic gate = False; all-seed full gate = False.

## Primary gaps

- Unknown samples missed before alert: 15.5169%.
- Unknown samples alerted but not labeled unknown: 11.5825%.
- Unknown recall deficit to 95%: 22.0994%.

## Per-seed hard gate

| Seed | Alert accuracy | Benign FPR | Known type accuracy | Unknown recall | Basic | Full |
|---:|---:|---:|---:|---:|:---:|:---:|
| 907 | 95.0704% | 4.3333% | 96.3013% | 69.9294% | True | False |
| 911 | 96.6849% | 3.6095% | 96.5227% | 75.2573% | True | False |
| 919 | 95.9114% | 5.5619% | 96.2638% | 73.5151% | False | False |

## Next experiment

Use seed7 only for development. Decouple alert calibration from unknown rejection, then confirm the frozen choice on new unseen seeds. No fresh test or unknown label may select a threshold.
