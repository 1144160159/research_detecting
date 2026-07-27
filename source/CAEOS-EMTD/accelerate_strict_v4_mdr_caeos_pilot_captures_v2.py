from __future__ import annotations

import accelerate_strict_v4_mdr_caeos_pilot_captures as base
from run_strict_v4_mdr_caeos_pilot_v2 import validate_protocol


def main() -> None:
    base.validate_protocol = validate_protocol
    base.main()


if __name__ == "__main__":
    main()
