"""Child process for the Python playground. Reads {code, trace, stdin} as JSON on stdin, prints a JSON result.

Run only via app.pyexec, which applies a timeout, an empty temp cwd and a scrubbed environment.
"""

import io
import json
import sys
import traceback

MAX_STEPS = 400
MAX_OUT = 20_000
MAX_REPR = 90
FILENAME = "<playground>"


def _limit_resources():
    try:
        import resource
    except ImportError:
        return
    for name, value in (("RLIMIT_CPU", 4), ("RLIMIT_FSIZE", 1 << 20), ("RLIMIT_AS", 1 << 30)):
        lim = getattr(resource, name, None)
        if lim is None:
            continue
        try:
            resource.setrlimit(lim, (value, value))
        except (ValueError, OSError):
            pass


class CappedIO(io.StringIO):
    def write(self, s):
        room = MAX_OUT - self.tell()
        if room <= 0:
            return len(s)
        return super().write(s[:room])


def _short(v):
    try:
        r = repr(v)
    except Exception:
        r = f"<{type(v).__name__}>"
    return r if len(r) <= MAX_REPR else r[: MAX_REPR - 1] + "…"


def _frame_vars(frame):
    out = {}
    for k, v in frame.f_locals.items():
        if k.startswith("__") or type(v).__name__ == "module":
            continue
        out[k] = {"type": type(v).__name__, "repr": _short(v), "id": id(v) % 100000}
    return out


def main():
    req = json.loads(sys.stdin.read() or "{}")
    code, want_trace = req.get("code", ""), bool(req.get("trace"))
    _limit_resources()

    out = CappedIO()
    sys.stdin = io.StringIO(req.get("stdin", ""))
    steps, truncated = [], False

    def tracer(frame, event, arg):
        nonlocal truncated
        if frame.f_code.co_filename != FILENAME:
            return None
        if event in ("line", "return", "exception"):
            if len(steps) >= MAX_STEPS:
                truncated = True
                sys.settrace(None)
                return None
            stack, f = [], frame
            while f is not None:
                if f.f_code.co_filename == FILENAME:
                    stack.append({"func": f.f_code.co_name, "line": f.f_lineno, "vars": _frame_vars(f)})
                f = f.f_back
            step = {"line": frame.f_lineno, "event": event, "stack": stack[::-1], "stdout": out.getvalue()}
            if event == "return":
                step["returned"] = _short(arg)
            steps.append(step)
        return tracer

    error = None
    real_stdout = sys.stdout
    sys.stdout = out
    try:
        compiled = compile(code, FILENAME, "exec")
        if want_trace:
            sys.settrace(tracer)
        exec(compiled, {"__name__": "__main__", "__builtins__": __builtins__})
    except SystemExit:
        pass
    except BaseException as exc:  # noqa: BLE001 - learner code may raise anything
        tb = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == FILENAME]
        error = {
            "type": type(exc).__name__,
            "message": str(exc),
            "line": tb[-1].lineno if tb else getattr(exc, "lineno", None),
            "trace": "".join(traceback.format_list(tb)) + f"{type(exc).__name__}: {exc}",
        }
    finally:
        sys.settrace(None)
        sys.stdout = real_stdout

    print(json.dumps({"stdout": out.getvalue(), "error": error, "steps": steps if want_trace else None, "truncated": truncated}))


if __name__ == "__main__":
    main()
