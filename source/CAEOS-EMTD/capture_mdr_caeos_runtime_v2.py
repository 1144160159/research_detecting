from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path
from types import FrameType, ModuleType
from typing import Any, Dict, List, Tuple

import capture_mdr_caeos_runtime as base


def load_importable_trainer_module(trainer_file: str) -> ModuleType:
    path = Path(trainer_file).resolve()
    module_name = path.stem
    existing = sys.modules.get(module_name)
    if existing is not None:
        existing_path = Path(getattr(existing, "__file__", "")).resolve()
        if existing_path != path:
            raise RuntimeError(
                f"module {module_name} already resolves to {existing_path}"
            )
        return existing
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load MDR trainer module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


def run_nested_base_capture(
    trainer_file: str, trainer_arguments: List[str]
) -> Tuple[Dict[str, Any], float]:
    module = load_importable_trainer_module(trainer_file)
    wrapper_main = module.main
    base_main = wrapper_main.__globals__["base"].main
    captured: Dict[str, Any] = {}

    def trace(frame: FrameType, event: str, arg: object):
        if frame.f_code is base_main.__code__:
            if event == "return":
                captured.update(frame.f_locals.copy())
            return trace
        return None

    original_argv = sys.argv[:]
    started = time.perf_counter()
    try:
        sys.argv = [trainer_file, *trainer_arguments]
        sys.settrace(trace)
        wrapper_main()
    finally:
        sys.settrace(None)
        sys.argv = original_argv
    if not captured:
        raise RuntimeError("MDR wrapper did not expose base trainer locals")
    return captured, time.perf_counter() - started


def main() -> None:
    base.run_nested_base_capture = run_nested_base_capture
    base.main()


if __name__ == "__main__":
    main()
