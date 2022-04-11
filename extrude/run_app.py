import json
from functools import wraps
from typing import Callable, Iterable

import streamlit.bootstrap
from http2py import HttpClient
from i2 import name_of_obj
from i2.wrapper import Sig
from py2http import mk_app as mk_webservice
from py2http import run_app as run_webservice
from py2http.util import run_process
from streamlitfront.base import dispatch_funcs


def mk_app(
    funcs: Iterable[Callable] = None,
    *,
    openapi_spec: dict = None,
    func_names: Iterable[str] = None,
    **kwargs
):
    """Generates an front application which will consume a web service exposing a bunch
    of functions. There are two ways to call this function: from a list of functions or
    directly from the openapi specification of the web service and a list of function
    names to pick from the openapi specification

    :param funcs: A list of functions. Overwrites ``openapi_spec`` and ``func_names``
    if not None.
    :param openapi_spec: A web service openapi specification.
    :param func_names: A list of function names to pick from the openapi specification.
    :param kwargs: Any extra keyword argument used to make the front application.

    >>> def foo():
    ...     pass
    ...
    >>> app = mk_app([foo])
    >>>
    >>> ws = mk_webservice([foo])
    >>> app = mk_app(
    ...     openapi_spec=ws.openapi_spec,
    ...     func_names=['foo']
    ... )
    """

    def _flatten(meth):
        sig = Sig(meth) - 'self'

        @sig
        @wraps(meth)
        def flat_func(*args, **kwargs):
            return meth(*args, **kwargs)

        return flat_func

    if funcs:
        ws = mk_webservice(funcs)
        openapi_spec = ws.openapi_spec
        func_names = [name_of_obj(func) for func in funcs]
    api = HttpClient(openapi_spec=openapi_spec)
    ws_funcs = [_flatten(getattr(api, name)) for name in func_names]

    return dispatch_funcs(ws_funcs, **kwargs)


def run_app(funcs: Iterable[Callable], *, ws_config: dict = None, **kwargs):
    """Runs a extrude application from a bunch of fucntions. It first run a web service
    application from those functions then runs a front applciation to consume these web
    services

    :param funcs: A list of functions.
    :param ws_config: A predefined configuration for the web service application.
    :param kwargs: Any extra keyword argument used to make the front application.
    """

    ws_config = ws_config or {}

    with run_process(
        func=run_webservice, func_kwargs=dict(app_obj=funcs, **ws_config), is_ready=3,
    ):
        ws = mk_webservice(funcs)
        func_names = [name_of_obj(func) for func in funcs]
        streamlit.bootstrap.run(
            __file__,
            args=[
                json.dumps(ws.openapi_spec),
                json.dumps(func_names),
                json.dumps(kwargs),
            ],
            command_line='',
            flag_options={},
        )


if __name__ == '__main__':
    from sys import argv

    openapi_spec = json.loads(argv[1])
    func_names = json.loads(argv[2])
    kwargs = json.loads(argv[3])

    app = mk_app(openapi_spec=openapi_spec, func_names=func_names, **kwargs,)
    app()
