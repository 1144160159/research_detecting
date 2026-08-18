@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "ROOT=%~dp0..\..\..\..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "OUT=%~dp0..\03_全文抽取缓存"

where pdftotext >nul 2>nul || (
  echo ERROR: pdftotext is not available on PATH.
  exit /b 2
)

if not exist "%OUT%" mkdir "%OUT%"

call :extract "10.1016_j.comnet.2024.110824.pdf" "01_Open_set_multi_feature_fusion.txt"
call :extract "10.1109_tifs.2025.3544067.pdf" "02_RoNeTC.txt"
call :extract "Dahanayaka2023_Robust_Open_Set_Traffic_Fingerprinting.pdf" "03_Robust_open_set_traffic_fingerprinting.txt"
call :extract "10.1109_TAI.2023.3244168.pdf" "04_Extensible_ETC_UQ.txt"
call :extract "10.1109_TIFS.2026.3653575.pdf" "05_FEC_OSL.txt"
call :extract "10.1109_TIFS.2025.3612141.pdf" "06_Gaussian_prototype_VAE.txt"
call :extract "10.1109_TNSM.2026.3693141.pdf" "07_Cross_granularity_OS_NID.txt"
call :extract "10.1109_TIFS.2025.3608666.pdf" "08_Open_world_NID.txt"
call :extract "10.1016_j.comnet.2024.110403.pdf" "09_Intra_inter_flow_multimodal.txt"
call :extract "10.48550_arXiv.1806.01768.pdf" "10_Evidential_deep_learning.txt"
call :extract "10.1145_3485447.3512217.pdf" "11_ET_BERT.txt"
call :extract "10.1609_aaai.v37i4.25674.pdf" "12_YaTC.txt"
call :extract "10.1016_j.comnet.2025.111184.pdf" "13_RAGN.txt"
call :extract "10.1016_j.array.2024.100349.pdf" "14_Multimodal_NID.txt"
call :extract "10.1109_TDSC.2026.3688655.pdf" "15_Normality_in_anomaly.txt"
call :extract "10.1038_s41598-025-08568-0.pdf" "16_Encrypted_traffic_anomaly_detection.txt"
call :extract "10.1109_TON.2026.3674624.pdf" "17_Pretrain_contrast_novelty_detection.txt"
call :extract "10.1109_TIFS.2025.3574971.pdf" "18_TIFS_2025_3574971.txt"
call :extract "10.1016_j.comnet.2023.109990.pdf" "19_AAE_DSVDD.txt"
call :extract "10.1109_TON.2025.3648394.pdf" "20_SOFA.txt"
call :extract "10.1016_j.jpdc.2026.105240.pdf" "21_MAGNN.txt"
call :extract "10.1109_TNET.2024.3413789.pdf" "22_FOSS.txt"
call :extract "10.1109_TDSC.2025.3649110.pdf" "23_MTRF.txt"
call :extract "10.1109_TNSM.2026.3652529.pdf" "24_Zero_day_contrastive_loss.txt"
call :extract "10.1109_TCE.2026.3674715.pdf" "25_Edge_aware_multimodal_IDS.txt"
call :extract "10.48550_arXiv.2505.21462.pdf" "26_M3S_UPD.txt"
call :extract "10.1109_TIFS.2024.3515821.pdf" "27_ReTrial.txt"
call :extract "10.1109_TIFS.2024.3426304.pdf" "28_ECNet.txt"
call :extract "10.1109_TNSM.2025.3565614.pdf" "29_DM_IDS.txt"
call :extract "10.1109_TNSM.2025.3600378.pdf" "30_Hierarchical_IDS_unknown_attacks.txt"
call :extract "10.3390_s24206507.pdf" "31_Semi_supervised_multimodal_EMT.txt"
call :extract "10.1016_j.comnet.2025.111499.pdf" "32_EncryptoVision.txt"
call :extract "1511.06233.pdf" "33_OpenMax.txt"
call :extract "1811.04110.pdf" "34_OSCR_agnostophobia.txt"
call :extract "2110.06207.pdf" "35_Good_closed_set_classifier.txt"
call :extract "2210.13458.pdf" "36_OpenAUC.txt"
call :extract "2204.11423.pdf" "37_Trusted_multi_view_classification.txt"
call :extract "2402.16897.pdf" "38_Reliable_conflictive_multi_view_learning.txt"
call :extract "2412.18024.pdf" "39_Discounted_belief_fusion.txt"
call :extract "10.48550_arXiv.2010.03759.pdf" "40_Energy_OOD.txt"

echo DONE: core paper text extracted to "%OUT%"
exit /b 0

:extract
set "SRC=%ROOT%\paper\%~1"
set "DST=%OUT%\%~2"
if not exist "%SRC%" (
  echo MISSING: "%SRC%"
  exit /b 3
)
echo EXTRACT: %~1
pdftotext -layout -enc UTF-8 "%SRC%" "%DST%" || exit /b 4
exit /b 0
