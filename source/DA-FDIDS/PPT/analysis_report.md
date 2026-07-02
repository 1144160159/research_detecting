# DA-FDIDS Full Experiment Report

**Parameters**: meta_epochs=100, pretrain_epochs=10, repetitions=10, way=5

**Total runs**: 0 | **Time**: 2026-06-02 05:04

## 1. Overall Ablation F1

| Setting | N | Mean F1 | Best F1 | Mean NMI | Mean Precision | Mean Recall |
|---|---|---|---|---|---|---|

## 2. Per-Mode Analysis


## 3. Alpha Optimization

### B3_F-DIDS-MFL

| Alpha | N | Mean F1 |
|---|---|---|
### B4_GRL

| Alpha | N | Mean F1 |
|---|---|---|
### B5_MMD

| Alpha | N | Mean F1 |
|---|---|---|
### B6_StableLoRA

| Alpha | N | Mean F1 |
|---|---|---|
### B7_RBF+MHA

| Alpha | N | Mean F1 |
|---|---|---|
### B8_Full_DA

| Alpha | N | Mean F1 |
|---|---|---|

## 4. Dataset Performance (In-Domain)


## 5. Cross-Domain Generalization


## 6. Efficiency


## 7. Key Findings

Traceback (most recent call last):
  File "/private/code/ParkAttackKE/DA-FDIDS/generate_report.py", line 119, in <module>
    main()
  File "/private/code/ParkAttackKE/DA-FDIDS/generate_report.py", line 106, in main
    best = max(all_rows, key=lambda r: r['f1_mean'])
ValueError: max() arg is an empty sequence
