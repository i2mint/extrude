# extrude.testing

Run a test against an app in one call: start the app, wait until it answers, run the test, stop the app.

The motivating case is a Selenium test of a Streamlit front: no second terminal, and the
app process (with its children) is gone when the test ends, pass or fail.

```pycon
>>> import sys
>>> serve = lambda app, port: [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
>>> run_app_test("ignored", lambda url: url.startswith("http://"), command=serve, host="127.0.0.1")
True
```

From a shell: `python -m extrude.testing app.py test_app.py` (the test script reads
the app’s address from `sys.argv[1]` or the `EXTRUDE_APP_URL` environment variable).

Stdlib only. Seams: `command=` builds the argv that serves `app` on a port (default:
`streamlit run`), and `popen=` starts it.

### Functions

| [`free_port`](#extrude.testing.free_port)([host])                                | A port nothing is listening on right now.                                    |
|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| [`main`](#extrude.testing.main)([argv])                                     | `python -m extrude.testing APP TEST`: exit with the test script's exit code. |
| [`run_app_test`](#extrude.testing.run_app_test)(app, test, \*\*running_app_kwargs)  | Start `app`, run `test` against it, stop the app; return the test's result.  |
| [`running_app`](#extrude.testing.running_app)(app, \*[, port, command, host, ...]) | Serve `app` in the background and yield its URL once it accepts connections. |
| [`streamlit_command`](#extrude.testing.streamlit_command)(app, port)                     | The argv that serves the Streamlit script `app` headless on `port`.          |

### extrude.testing.free_port(host='localhost')

A port nothing is listening on right now.

* **Return type:**
  [`int`](https://docs.python.org/3/builtins/functions.html#int)

### extrude.testing.main(argv=None)

`python -m extrude.testing APP TEST`: exit with the test script’s exit code.

* **Return type:**
  [`int`](https://docs.python.org/3/builtins/functions.html#int)

### extrude.testing.run_app_test(app, test, \*\*running_app_kwargs)

Start `app`, run `test` against it, stop the app; return the test’s result.

* **Parameters:**
  * **test** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)] | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)) – a callable taking the app’s URL (its return value is returned), or the path
    of a Python script, run with the URL as `sys.argv[1]` and in `EXTRUDE_APP_URL`
    (a non-zero exit raises `subprocess.CalledProcessError`; the return is `None`).
  * **running_app_kwargs** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – see [`running_app()`](#extrude.testing.running_app).
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)

### extrude.testing.running_app(app, \*, port=None, command=<function streamlit_command>, host='localhost', ready_timeout_s=30.0, stop_grace_s=5.0, env=None, cwd=None, popen=<class 'subprocess.Popen'>)

Serve `app` in the background and yield its URL once it accepts connections.

On exit (normal or by exception) the app’s process group is stopped.

* **Parameters:**
  * **app** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – what `command` serves (for the default, the path of a Streamlit script).
  * **port** ([`int`](https://docs.python.org/3/builtins/functions.html#int) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – the port to serve on; a free one is picked when `None`.
  * **command** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`Any`](https://docs.python.org/3/library/typing.html#typing.Any), [`int`](https://docs.python.org/3/builtins/functions.html#int)], [`Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – `(app, port) -> argv`; default runs `streamlit run`.
  * **ready_timeout_s** ([`float`](https://docs.python.org/3/builtins/functions.html#float)) – how long to wait for the app to answer.
* **Raises:**
  [**RuntimeError**](https://docs.python.org/3/builtins/exceptions.html#RuntimeError) – the app exited, or never answered; the message carries its output.
* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### extrude.testing.streamlit_command(app, port)

The argv that serves the Streamlit script `app` headless on `port`.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
