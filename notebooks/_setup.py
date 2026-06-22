"""Path bootstrap for the lightweight notebooks.

Resolves `scripts/lakehouse.py` from the repo root regardless of where
Jupyter / Python was launched from. Used by all NB*/lite notebooks:

    import _setup  # noqa: F401  -- adds scripts/ to sys.path
    from lakehouse import path, reset

Why: the prior pattern `sys.path.insert(0, "../scripts")` is *cwd-relative*
and silently breaks if the notebook is run from the repo root or a CI
runner. This helper also tolerates Jupyter contexts where `__file__` is not
defined.
"""
from __future__ import annotations

import sys
from pathlib import Path

_DOCKER = Path("/workspace/scripts")

def _candidate_roots() -> list[Path]:
    roots: list[Path] = []
    if "__file__" in globals():
        roots.append(Path(__file__).resolve().parent)
    roots.append(Path.cwd().resolve())
    roots.extend(Path.cwd().resolve().parents)
    return roots


def _find_scripts_dir() -> Path:
    if _DOCKER.exists():
        return _DOCKER

    for root in _candidate_roots():
        candidates = [root / "scripts", root.parent / "scripts"]
        for candidate in candidates:
            if (candidate / "lakehouse.py").exists():
                return candidate

    raise FileNotFoundError("Could not find scripts/lakehouse.py from this notebook context.")


_TARGET = _find_scripts_dir()
sys.path.insert(0, str(_TARGET))
