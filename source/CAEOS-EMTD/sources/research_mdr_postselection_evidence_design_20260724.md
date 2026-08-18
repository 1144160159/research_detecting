# MDR post-selection evidence design (2026-07-24)

## Purpose

This record freezes the evidence that would still be required if the reserved-seed MDR confirmation selects `mdr_caeos_v1`. It does not report an MDR effect and does not authorize a SOTA claim.

## Frozen artifact

- Schema: `strict_v4_mdr_postselection_evidence_design_v1`
- Canonical manifest SHA-256: `c589a0609c42cd0e7889208999a2311c24d90cc5f26db5453b426657a0be1ce1`
- File SHA-256: `997b32ac601fee291a970558fb33a0721cadbfc429f2d833063cdceef379365f`
- Creator SHA-256: `3d7b06b2008d0df19fa2765952bffc8dddde4bc2f39b4d39825dd356357bc560`
- Test SHA-256: `39fec7b5a165ce571747e37a096f69c892b747e34f1ee9a8fe0c4e3c30092bcb`
- GPU tests: `4 passed`
- Output counts at freeze: external metrics `0`, system blocks `0`, PARROT metrics `0`, integrated audits `0`

## Non-inheritance rules

1. Pairwise or VGRF external results cannot be relabelled as MDR results.
2. PARROT2025 is benign Android application traffic and cannot replace malicious external evaluation.
3. Pairwise or VGRF efficiency and deployment results cannot be inherited by MDR.
4. MDR full102 confirmation success alone cannot authorize any comprehensive SOTA claim.
5. Dataset-wise, metric-wise, or component-wise result splicing is forbidden.

## Required fresh evidence after positive MDR selection

- Accuracy and robustness: the frozen 102-scenario, three-reserved-seed MDR confirmation must pass all checks.
- Malicious external data: fresh clean and robust MDR runtimes on LSNM2024 and CICDDoS2019, using seeds 223/227/229 and OpenDetect as the primary comparator.
- Selected system: all 306 MDR runtime roundtrips, same-hardware inference and fit characterization, complete resource metrics, and zero failures.
- Benign safety: all 320 PARROT2025 captures from 80 applications, without decryption and without using PARROT for fit, selection, calibration, or thresholding.
- Integrated audit: every required gate must pass without substitution.

## Claim tiers

- `accuracy_robustness_external_sota_with_deployability` requires positive MDR confirmation, fresh two-dataset malicious external confirmation, selected-system deployability, and PARROT benign safety.
- `multidimensional_comprehensive_sota` additionally requires strict efficiency superiority over both the embedded Pairwise reference and OpenDetect.
- If strict efficiency superiority fails, efficiency trade-offs must be reported and the multidimensional claim remains false.

## Current execution state

At 2026-07-24 09:14 UTC, Pairwise-OpenDetect comparative corruption had produced 163/306 `paired_corruption.json` blocks, 815/1530 corruption conditions, 326 capture manifests, and zero failure files. Its authoritative summary was still absent. MDR pilot, MDR confirmation, and MEDAF effect outputs remained absent.

## Fresh malicious-external branch

- External design schema: `strict_v4_mdr_external_malicious_design_v1`
- External design canonical/file SHA-256: `28ab654fcea6666bf303eff55d522c7eaa6b3d6a23ac2ae5ca663adcd8d4bd00` / `adfca4541e151a3a308ddd0ae0fbb09b05ce5544028d942631e7f5ec25081407`
- Design creator/test SHA-256: `fe5220a1724199fbfad91fb49c886b4a2a58be2f4a0b708f38485b555ed90a6e` / `d1bb86ca96e9059704a661fc7fbc85125e8355b808edb023c581da7ea730015c`
- Protocol creator/test SHA-256: `a181d502a538b00e0d63e1ccfd3eddb4b6bf7928578be08af162cde80674af3e` / `871f7b846065cde8a30efe0d39cd7beacfaec2b16e1ee156878f56fef3f56c8f`
- Runtime evaluator/test SHA-256: `5e5afec35f3d5c6b3efb89aeff257014251efb28947c5b0d18bfec5c73c12523` / `ef54da3e0a0cc622ab22f238e969314ea9f19ceaaf23d7dcd3469fa46656a733`
- Resumable runner/test SHA-256: `9d8640de2a4c660df2c6f3f59c939ec665cb8ff30b07bb0069be1cbed09c3347` / `5e038867edaa1d7151e08f280239dfb6924a4dcfb65df80cbe91ea9706c38add`
- Combined GPU tests for the five new post-selection modules: `19 passed`
- Formal external metric count at design freeze: `0`

The branch fixes LSNM2024 and CICDDoS2019, seeds 223/227/229, fingerprint-grouped splitting, leave-one-attack-family-out scenarios, and the frozen OpenDetect policy. The MDR augmentation weight is read once from a positive canonical confirmation and cannot be reselected on external data. Scenario-specific augmentation and validation-profile seeds are derived from the external design manifest and scenario identity, without effect reads.

The runner is fail-closed for partial capture or metrics directories. It performs a fresh clean/robust MDR capture, validates the runtime and inactive Pairwise path, evaluates MDR with test labels used only for final metrics, then executes OpenDetect. Protocol creation and execution remain blocked until positive MDR selection, canonical confirmation audit, complete external preparation, and all required implementation hashes exist. The summarizer, independent auditor, and conditional watcher were not yet implemented at this snapshot; therefore the external execution chain was not yet complete or admitted.

At 2026-07-24 09:57 UTC, comparative corruption had 189/306 pairs, 945/1530 conditions, 378 captures, zero failures, and no authoritative summary. No MDR, MEDAF, or MDR-external effect result existed.

## Malicious-external branch completion

The result-free malicious-external implementation chain was completed after the preceding snapshot.

- Corrected protocol creator/test SHA-256: `ce6522143d6f4d8875a73a1601ce7dbbc267886870ff3ea16f130928044ea449` / `8a7a33db0f2a60a1837bb44998db246fd4bffeaaadd88094882e25f00d3082ef`
- Summarizer/test SHA-256: `72018d438b2fc120c6f1a822907fada185118cb1837d60f85b603679a33762b1` / `0ba02b1f623fae357827ed11c8639fdfc474e1cfdb4b57c11d7bdcf75d22fb89`
- Independent auditor/test SHA-256: `ae43c7d968632ec2fcb4701249368de718ade623cd0efb468755e249e705aff9` / `3bf184ae6c09587f3ee41b0b8317d61246d87dd43fdddb467f2a30ec7f2858e9`
- Conditional watcher/test SHA-256: `0ccb86a4500991ea9709adc4cc8ef34a4cb5c40ac9c18134ebffc3a83508377a` / `e10c134690dc90c6b4b0e658e3f99d85114c12d8e63b01e66c17bd0b6b3d99b0`
- Combined GPU regression: `33 passed`; target Bash syntax passed.
- The protocol implementation audit resolved all 13 required files and their SHA-256 values.
- Watcher PID: `1032116`; state: waiting for canonical MDR branch completion.

The summarizer averages the three seeds within each dataset/attack-family block before 10,000 block bootstrap resamples and Wilcoxon-Holm correction. FPR95 is oriented in the decreasing direction. The independent audit distinguishes artifact integrity (`passes`) from the scientific effect gate (`external_effect_gate_passes`); a structurally valid negative effect is preserved as negative.

The watcher writes a canonical not-required record if the reserved confirmation retains Pairwise. It creates and executes the external protocol only after canonical MDR selection, positive full confirmation, complete external preparation, and five consecutive idle observations. Therefore no training or external metric was produced by installing the watcher.

At 2026-07-24 11:28 UTC, comparative corruption had 252/306 pairs, 1260/1530 conditions, 508 captures, zero failures, and no authoritative summary. MDR, MDR-external, and MEDAF effect outputs remained absent.
