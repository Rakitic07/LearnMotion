"""Runs learner Python in a separate, time-limited interpreter process (see pyrunner.py)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RUNNER = Path(__file__).with_name("pyrunner.py")
MAX_CODE = 20_000
TIMEOUT = 6


class PythonRunError(Exception):
    pass


def run(code: str, trace: bool = False, stdin: str = "") -> dict:
    code = code or ""
    if not code.strip():
        raise PythonRunError("Nothing to run.")
    if len(code) > MAX_CODE:
        raise PythonRunError(f"Code is longer than {MAX_CODE} characters.")
    payload = json.dumps({"code": code, "trace": trace, "stdin": (stdin or "")[:5000]})
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="pyplay-") as cwd:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", str(RUNNER)],
                input=payload, capture_output=True, text=True, timeout=TIMEOUT, cwd=cwd,
                env={"PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0"},
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "stdout": "", "error": {"type": "Timeout", "message": f"Stopped after {TIMEOUT}s. Infinite loop?", "line": None, "trace": ""}, "steps": None, "ms": TIMEOUT * 1000}
    ms = round((time.monotonic() - started) * 1000)
    try:
        data = json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        reason = "Stopped: the CPU or memory limit was reached. Infinite loop or huge data?" if proc.returncode < 0 else (proc.stderr.strip()[-400:] or "The interpreter exited unexpectedly.")
        return {"ok": False, "stdout": "", "error": {"type": "RuntimeError", "message": reason, "line": None, "trace": ""}, "steps": None, "ms": ms}
    return {"ok": data["error"] is None, **data, "ms": ms}
