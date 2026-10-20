"""``extrude.testing``: the app is up for the test and gone afterwards, whatever the test does."""

import os
import subprocess
import sys
import textwrap

import pytest

from extrude.testing import APP_URL_ENV, main, run_app_test, running_app

HOST = "127.0.0.1"


def serve(app, port):
    """A stand-in for ``streamlit run``: a plain HTTP server."""
    return [sys.executable, "-m", "http.server", str(port), "--bind", HOST]


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_the_app_answers_inside_and_is_stopped_after():
    pids = []

    def popen(*args, **kwargs):
        proc = subprocess.Popen(*args, **kwargs)
        pids.append(proc.pid)
        return proc

    with running_app("x", command=serve, host=HOST, popen=popen) as url:
        assert url.startswith(f"http://{HOST}:") and alive(pids[0])
    assert not alive(pids[0])


def test_the_app_is_stopped_when_the_test_raises():
    seen = []
    with pytest.raises(ZeroDivisionError):
        with running_app("x", command=serve, host=HOST) as url:
            seen.append(url)
            1 / 0
    from extrude.testing import _answers

    assert not _answers(HOST, int(seen[0].rsplit(":", 1)[1]))


def test_run_app_test_returns_what_the_callable_returns():
    assert run_app_test("x", lambda url: url.upper(), command=serve, host=HOST).startswith("HTTP://")


def test_a_script_gets_the_url_in_argv_and_env(tmp_path):
    script = tmp_path / "check.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import os, sys, urllib.request
            assert sys.argv[1] == os.environ["{APP_URL_ENV}"]
            urllib.request.urlopen(sys.argv[1]).read()
            """
        )
    )
    run_app_test("x", script, command=serve, host=HOST)
    script.write_text("import sys; sys.exit(3)")
    with pytest.raises(subprocess.CalledProcessError) as error:
        run_app_test("x", script, command=serve, host=HOST)
    assert error.value.returncode == 3


def test_an_app_that_dies_reports_its_output():
    crash = lambda app, port: [sys.executable, "-c", "print('boom: no such module'); raise SystemExit(1)"]  # noqa: E731
    with pytest.raises(RuntimeError, match="exited with code 1") as error:
        with running_app("x", command=crash, host=HOST):
            pass
    assert "boom: no such module" in str(error.value)


def test_an_app_that_never_answers_times_out_and_is_stopped():
    sleeper = lambda app, port: [sys.executable, "-c", "import time; time.sleep(60)"]  # noqa: E731
    with pytest.raises(RuntimeError, match="did not answer within"):
        with running_app("x", command=sleeper, host=HOST, ready_timeout_s=0.5, stop_grace_s=2):
            pass


def test_the_cli_reports_a_dead_app_with_exit_code_2(capsys):
    assert main(["no_such_app.py", "t.py", "--ready-timeout", "1"]) == 2
    assert "Its output" in capsys.readouterr().err
