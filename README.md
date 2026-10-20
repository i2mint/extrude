
# extrude
Tool to run a composite web application to easily interact with python functions


To install:	```pip install extrude```

See [examples here](https://github.com/i2mint/extrude/tree/master/extrude/examples).

## Test an app from a single command

`extrude.testing` starts the app in the background, waits until it answers, runs your test, and stops the app (and its children) when the test ends, pass or fail. Useful for a Selenium test of a Streamlit front:

```python
from extrude.testing import run_app_test


def test(url):  # drive the page with selenium here
    ...


run_app_test("my_app.py", test)
```

or `python -m extrude.testing my_app.py test_my_app.py` (the script gets the address as `sys.argv[1]` and in `EXTRUDE_APP_URL`). `running_app(...)` is the same as a context manager. Pass `command=` to serve something other than a Streamlit script.
