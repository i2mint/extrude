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
from meshed import DAG

from extrude.util import SubDagSpec, split_dag


def mk_app_from_dag(
    dag: DAG,
    sub_dag_spec: SubDagSpec = None,
    *,
    api_url: str = None,
    **kwargs
):
    """Generates a front application which will consume a web service exposing a dag or
    sub-dags of the dag.

    :param dag: A dag object.
    :param sub_dag_spec: The rules to split the dag in sub_dags.
    :param api_url: The base url of the API.
    :param kwargs: Any extra keyword argument used to make the front application.

    >>> def this(a, b=1):
    ...     return a + b
    >>> def that(x, b=1):
    ...     return x * b
    >>> def combine(this, that):
    ...     return (this, that)
    >>> 
    >>> dag = DAG((this, that, combine))
    >>> app = mk_app(
    ...         dag,
    ...         {
    ...             'this': [['a', 'b'], 'this'],
    ...             'that_compine': [['x', 'b'], 'combine']
    ...         }
    ...     )
    """

    
    funcs = split_dag(sub_dag_spec) if sub_dag_spec else [dag]
    return mk_app_from_funcs(funcs, api_url=api_url, **kwargs)


# TODO: Add a way to bind outputs and inputs between funcs (like for a dag)
def mk_app_from_funcs(
    funcs: Iterable[Callable],
    *,
    api_url: str = None,
    **kwargs
):
    """Generates a front application which will consume a web service exposing a bunch
    of functions.

    :param funcs: A list of functions.
    :param api_url: The base url of the API.
    :param kwargs: Any extra keyword argument used to make the front application.

    >>> def foo():
    ...     pass
    ...
    >>> app = mk_app([foo])
    """

    ws_config = dict(
        openapi=dict(
            base_url=api_url
        )
    ) if api_url else {}
    ws = mk_webservice(funcs, **ws_config)
    openapi_spec = ws.openapi_spec
    print(openapi_spec)
    func_names = [name_of_obj(func) for func in funcs]
    return mk_app_from_openapi_spec(openapi_spec, func_names, **kwargs)


def mk_app_from_openapi_spec(
    openapi_spec: dict,
    func_names: Iterable[str],
    **kwargs
):
    """Generates a front application which will consume a web service exposing a bunch
    of functions, directly from the openapi specification of the web service and a list
    of function names to pick from the openapi specification.

    :param openapi_spec: A web service openapi specification.
    :param func_names: A list of function names to pick from the openapi specification.
    :param kwargs: Any extra keyword argument used to make the front application.

    >>> def foo():
    ...     pass
    ...
    >>> ws = mk_webservice([foo])
    >>> app = mk_app(
    ...     openapi_spec=ws.openapi_spec,
    ...     func_names=['foo']
    ... )
    """
    def flatten_api_meth(meth):
        sig = Sig(meth) - 'self'

        @sig
        @wraps(meth)
        def flat_func(*args, **kwargs):
            return meth(*args, **kwargs)

        return flat_func

    api = HttpClient(openapi_spec=openapi_spec)
    ws_funcs = [flatten_api_meth(getattr(api, name)) for name in func_names]

    return dispatch_funcs(ws_funcs, **kwargs)


def run_app_from_dag(
    dag: DAG,
    sub_dag_spec: SubDagSpec = None,
    *,
    ws_config: dict = None,
    **kwargs
):
    """Runs an extrude application from a dag and an optional specification to split
    the dag into sub-dags. It first runs a web service application then runs a front
    applciation to consume these web services.

    :param dag: A dag object.
    :param sub_dag_spec: The rules to split the dag in sub_dags.
    :param ws_config: A predefined configuration for the web service application.
    :param kwargs: Any extra keyword argument used to make the front application.
    """

    funcs = split_dag(sub_dag_spec) if sub_dag_spec else [dag]
    run_app_from_funcs(funcs, ws_config=ws_config, **kwargs)


def run_app_from_funcs(funcs: Iterable[Callable], *, ws_config: dict = None, **kwargs):
    """Runs an extrude application from a bunch of functions. It first runs a web service
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

    app = mk_app_from_openapi_spec(openapi_spec=openapi_spec, func_names=func_names, **kwargs,)
    app()
