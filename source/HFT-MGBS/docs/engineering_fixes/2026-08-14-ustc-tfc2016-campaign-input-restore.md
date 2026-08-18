# USTC-TFC2016 campaign input restore

## Problem

The bounded A01--A10 campaign references 18 USTC-TFC2016 PCAP files under the
GPU dataset root.  A three-host exact-name search found no verified copy, so the
formal campaign could not even build its 27-entry input hash manifest.

## Source and boundary

The restore is pinned to public repository commit
`4bc9683b996f582c3843815b68da8e4dce9c7e1e` and tree
`fba77dcee81c1a6046eaf2f4de64c13ed4a3a1f8`.  The repository exposes eleven
required PCAPs directly and seven required captures as one-PCAP 7z archives.
The repository is a recovery source, not a pre-existing project backup; the
result must therefore retain its source commit, Git blob SHA-1, downloaded
SHA-256 and extracted target SHA-256.  Until those checks and PCAP parsing pass,
none of the files count toward the campaign.

## Implementation

`scripts/restore_ustc_tfc2016_campaign_inputs.sh`:

- downloads only from the pinned commit with resumable `.part` files;
- checks the exact Git blob SHA-1 and byte count before installing a source;
- requires exactly one PCAP in each archive and validates every output with
  `capinfos`;
- rejects symlinks and residual partial files;
- creates a source provenance JSON, a target SHA-256 manifest and `ALL_DONE`;
- writes all data only below the GPU contract path.

This step restores inputs only.  It does not authorize the 60-unit campaign,
does not prove algorithm optimality, and does not change any production or
Pareto flag.

## 2026-08-14 GPU execution receipt

The pinned restore was executed on the GPU host and completed without using
symlinks or residual `.part` files.  The contract target now contains exactly
18 PCAP files.  Re-running `sha256sum -c _control/input_pcaps.sha256` verified
all 18 entries.

- target: `/opt/data/private/wangwt/ParkAttackKE/datasets/USTC-TFC2016`;
- source manifest SHA-256:
  `c2e0a5edcda42b2ba81d916f0c5e9e9164ceff7171a34977bfbca20e5a8dd74f`;
- PCAP checksum-list SHA-256:
  `3d024b3f1ed596bc9229379dcf8ce18ea488123951b40a3d41982ced6149d5ad`;
- `ALL_DONE` SHA-256:
  `2ab66060f45b601cdd4d96e22b9501abed109e120c78227c002f78058d4eaaf6`;
- symlink count: `0`; residual `.part` count: `0`.

The campaign's own `freeze_input_manifest.py` was then run as a separate
preflight against the training and holdout manifests.  It discovered exactly
27 unique regular files: the two manifests, 18 USTC PCAPs, six UNSW PCAPs and
one UNSW ground-truth CSV.  This confirms input availability only.  Its
timestamped preflight manifest is not reused as the formal campaign manifest;
the authorized runner must freeze and seal a fresh copy inside its own result
root.
