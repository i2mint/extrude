"""Run a test against an app in one call: start the app, wait until it answers, run the test, stop the app.

The motivating case is a Selenium test of a Streamlit front: no second terminal, and the
app process (with its children) is gone when the test ends, pass or fail.

>>> import sys
>>> serve = lambda app, port: [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
>>> run_app_test("ignored", lambda url: url.startswith("http://"), command=serve, host="127.0.0.1")
True

From a shell: ``python -m extrude.testing app.py test_app.py`` (the test script reads
the app's address from ``sys.argv[1]`` or the ``EXTRUDE_APP_URL`` environment variable).

Stdlib only. Seams: ``command=`` builds the argv that serves ``app`` on a port (default:
``streamlit run``), and ``popen=`` starts it.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any

APP_URL_ENV = "EXTRUDE_APP_URL"
DFLT_HOST = "localhost"
DFLT_READY_TIMEOUT_S = 30.0
DFLT_POLL_S = 0.1
DFLT_STOP_GRACE_S = 5.0
OUTPUT_TAIL_CHARS = 2000

Command = Callable[[Any, int], Sequence[str]]


def streamlit_command(app: Any, port: int) -> list[str]:
    """The argv that serves the Streamlit script ``app`` headless on ``port``."""
    return [
        sys.executable, "-m", "streamlit", "run", str(app),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]  # fmt: skip


def free_port(host: str = DFLT_HOST) -> int:
    """A port nothing is listening on right now."""
    with socket.socket() as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def _answers(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=DFLT_POLL_S * 5):
            return True
    except OSError:
        return False


def _stop(proc: subprocess.Popen, *, grace_s: float) -> None:
    """End the app's whole process group (it may have spawned children); kill if it ignores SIGTERM."""
    if proc.poll() is not None:
        return
    posix = os.name == "posix"
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(proc.pid, signal.SIGTERM) if posix else proc.terminate()
    try:
        proc.wait(grace_s)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL) if posix else proc.kill()
        proc.wait()


@contextlib.contextmanager
def running_app(
    app: Any,
    *,
    port: int | None = None,
    command: Command = streamlit_command,
    host: str = DFLT_HOST,
    ready_timeout_s: float = DFLT_READY_TIMEOUT_S,
    stop_grace_s: float = DFLT_STOP_GRACE_S,
    env: dict[str, str] | None = None,
    cwd: str | Path | None = None,
    popen: Callable[..., subprocess.Popen] = subprocess.Popen,
) -> Iterator[str]:
    """Serve ``app`` in the background and yield its URL once it accepts connections.

    On exit (normal or by exception) the app's process group is stopped.

    :param app: what ``command`` serves (for the default, the path of a Streamlit script).
    :param port: the port to serve on; a free one is picked when ``None``.
    :param command: ``(app, port) -> argv``; default runs ``streamlit run``.
    :param ready_timeout_s: how long to wait for the app to answer.
    :raises RuntimeError: the app exited, or never answered; the message carries its output.
    """
    port = port or free_port(host)
    argv = list(command(app, port))
    popen_kwargs: dict[str, Any] = {"cwd": cwd, "env": {**os.environ, **(env or {})}}
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True  # own process group, so children stop with it
    else:  # pragma: no cover - windows
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    with tempfile.TemporaryFile() as output:
        proc = popen(argv, stdout=output, stderr=subprocess.STDOUT, **popen_kwargs)
        try:
            deadline = time.monotonic() + ready_timeout_s
            while not _answers(host, port):
                code = proc.poll()
                if code is not None or time.monotonic() > deadline:
                    output.seek(0)
                    tail = output.read().decode(errors="replace")[-OUTPUT_TAIL_CHARS:]
                    why = f"exited with code {code}" if code is not None else f"did not answer within {ready_timeout_s}s"
                    raise RuntimeError(f"The app {why} ({' '.join(argv)}). Its output:\n{tail}")
                time.sleep(DFLT_POLL_S)
            yield f"http://{host}:{port}"
        finally:
            _stop(proc, grace_s=stop_grace_s)


def run_app_test(app: Any, test: Callable[[str], Any] | str | Path, **running_app_kwargs: Any) -> Any:
    """Start ``app``, run ``test`` against it, stop the app; return the test's result.

    :param test: a callable taking the app's URL (its return value is returned), or the path
        of a Python script, run with the URL as ``sys.argv[1]`` and in ``EXTRUDE_APP_URL``
        (a non-zero exit raises ``subprocess.CalledProcessError``; the return is ``None``).
    :param running_app_kwargs: see :func:`running_app`.
    """
    with running_app(app, **running_app_kwargs) as url:
        if callable(test):
            return test(url)
        subprocess.run(
            [sys.executable, str(test), url],
            check=True,
            env={**os.environ, APP_URL_ENV: url},
        )


def main(argv: Sequence[str] | None = None) -> int:
    """``python -m extrude.testing APP TEST``: exit with the test script's exit code."""
    parser = argparse.ArgumentParser(prog="python -m extrude.testing", description=__doc__.split("\n")[0])
    parser.add_argument("app", help="the Streamlit script to serve")
    parser.add_argument("test", help="the Python script to run against it (gets the URL as argv[1])")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--ready-timeout", type=float, default=DFLT_READY_TIMEOUT_S)
    args = parser.parse_args(argv)
    try:
        run_app_test(args.app, args.test, port=args.port, ready_timeout_s=args.ready_timeout)
    except subprocess.CalledProcessError as error:
        return error.returncode
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
