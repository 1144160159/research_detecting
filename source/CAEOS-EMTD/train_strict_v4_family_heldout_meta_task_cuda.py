from __future__ import annotations

import json

from train_strict_v4_dual_metric_contrastive_task_cuda import (
    parse_arguments,
    train_task,
)


def main() -> None:
    args = parse_arguments()
    if args.meta_heldout_loss_weight <= 0.0:
        raise ValueError(
            "FHMM-CAEOS requires a positive meta heldout loss weight"
        )
    report = train_task(args)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
