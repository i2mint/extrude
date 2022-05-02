import json
from functools import wraps
from typing import Callable, Iterable, Union

import streamlit.bootstrap
from http2py import HttpClient
from i2 import name_of_obj
from i2.wrapper import Sig
from py2http import mk_app as mk_webservice
from py2http import run_app as run_webservice
from py2http.util import run_process
from streamlitfront.base import dispatch_funcs
from meshed import DAG


# TODO: Maybe split this function in two, by adding mk_app_from_openapi_spec
def mk_app(
    obj: Union[DAG, Iterable[Callable]] = None,
    *,
    api_url: str = None,
    openapi_spec: dict = None,
    func_names: Iterable[str] = None,
    **kwargs
):
    """Generates a front application which will consume a web service exposing a bunch
    of functions. There are three ways to call this function: from a dag, a list of
    functions or directly from the openapi specification of the web service and a list
    of function names to pick from the openapi specification.

    :param obj: A dag or list of functions. Overwrites ``openapi_spec`` and
    ``func_names`` if not None.
    :param api_url: The base url of the API. Only used if ``obj`` is not None.
    :param openapi_spec: A web service openapi specification. Ignored if ``obj``
    is not None.
    :param func_names: A list of function names to pick from the openapi specification.
    Ignored if ``obj`` is not None.
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

    if obj:
        ws_config = dict(openapi=dict(base_url=api_url)) if api_url else {}
        funcs = [fn.func for fn in obj.func_nodes] if isinstance(obj, DAG) else obj
        ws = mk_webservice(funcs, **ws_config)
        openapi_spec = ws.openapi_spec
        func_names = [name_of_obj(func) for func in funcs]
    api = HttpClient(openapi_spec=openapi_spec)
    ws_funcs = [_flatten(getattr(api, name)) for name in func_names]

    return dispatch_funcs(ws_funcs, **kwargs)


def run_app(obj: Union[DAG, Iterable[Callable]], *, ws_config: dict = None, **kwargs):
    """Runs a extrude application from a bunch of fucntions. It first run a web service
    application from those functions then runs a front applciation to consume these web
    services

    :param obj: A dag or a list of functions.
    :param ws_config: A predefined configuration for the web service application.
    :param kwargs: Any extra keyword argument used to make the front application.
    """

    ws_config = ws_config or {}
    funcs = [fn.func for fn in obj.func_nodes] if isinstance(obj, DAG) else obj

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
