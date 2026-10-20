# extrude.base

Build composite web apps (webservice + streamlit front) from python functions.

### Functions

| [`mk_api`](#extrude.base.mk_api)(funcs[, mall])                 | Generates a py2http application with default configuration for extrude.                       |
|----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| [`mk_web_app`](#extrude.base.mk_web_app)(funcs, \*[, api, api_url]) | Generates a front application which will consume a web service exposing a bunch of functions. |
| `run_api`(app, \*\*kwargs)                                                             |                                                                                               |

### extrude.base.mk_api(funcs, mall=None, \*\*kwargs)

Generates a py2http application with default configuration for extrude.

* **Parameters:**
  * **funcs** ([`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)]) – A list of functions.
  * **kwargs** – Any extra keyword argument used to make the py2http application.

```pycon
>>> def foo():
...     pass
...
>>> app = mk_api([foo])
```

### extrude.base.mk_web_app(funcs, , api=None, api_url=None, \*\*kwargs)

Generates a front application which will consume a web service exposing a bunch
of functions.

* **Parameters:**
  * **funcs** ([`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)]) – A list of functions.
  * **api** (`HttpClient`) – The HttpClient object to consume the API.
  * **api_url** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The base url of the API to create a HttpClient object in case the
    `api` parameter is not provided. Ignored otherwise
  * **kwargs** – Any extra keyword argument used to make the front application.
