import json
from functools import wraps
from typing import Callable, Iterable, Mapping, Optional
from urllib.parse import urljoin
import glom

# import streamlit.bootstrap
from http2py import HttpClient
from i2 import name_of_obj
from i2.wrapper import Sig
from py2http import mk_app as mk_webservice, run_app as run_webservice

# from py2http.util import run_process
from streamlitfront.base import mk_app as mk_front_app
from meshed import DAG
from front.crude import Mall
from front import RENDERING_KEY, ELEMENT_KEY
from streamlitfront.elements import SelectBox

from extrude.util import SubDagSpec, split_dag

PARAM_TO_MALL_MAP_ATTR = 'param_to_mall_map'


def mk_web_app(
    funcs: Iterable[Callable], *, api: HttpClient = None, api_url: str = None, **kwargs
):
    """Generates a front application which will consume a web service exposing a bunch
    of functions.

    :param funcs: A list of functions.
    :param api: The HttpClient object to consume the API.
    :param api_url: The base url of the API to create a HttpClient object in case the 
    `api` parameter is not provided. Ignored otherwise
    :param kwargs: Any extra keyword argument used to make the front application.
    """

    def flatten_api_meth(meth):
        sig = Sig(meth) - 'self'

        @sig
        @wraps(meth)
        def flat_func(*args, **kwargs):
            return meth(*args, **kwargs)

        return flat_func

    def handle_crudified_params():
        def build_crude_config():
            for func in funcs:
                param_to_mall_map = getattr(func, PARAM_TO_MALL_MAP_ATTR, None)
                if param_to_mall_map:
                    yield name_of_obj(func), param_to_mall_map

        crude_config = {k: v for k, v in build_crude_config()}
        if crude_config:
            if not hasattr(api, 'get_light_mall'):
                raise RuntimeError(
                    'Some parameters have been crudified but there is \
no way to get the list of valid keys for them. Make sure to expose the \
"get_light_mall" endpoint through the API'
                )
            light_mall = api.get_light_mall()
            config = kwargs.get('config', {})
            for func_name, param_to_mall_map in crude_config.items():
                for param, store in param_to_mall_map.items():
                    path = '.'.join(
                        [RENDERING_KEY, func_name, 'execution', 'inputs', param]
                    )
                    param_config = glom.glom(config, path, default={})
                    if ELEMENT_KEY not in param_config:
                        param_config[ELEMENT_KEY] = SelectBox
                        param_config['options'] = list(light_mall.get(store, {}))
                        glom.assign(config, path, param_config, missing=dict)
            kwargs['config'] = config

    if not api:
        openapi_spec_url = urljoin(api_url, 'openapi')
        api = HttpClient(url=openapi_spec_url)
    func_names = [name_of_obj(func) for func in funcs]
    ws_funcs = [flatten_api_meth(getattr(api, name)) for name in func_names]
    handle_crudified_params()

    return mk_front_app(ws_funcs, **kwargs)


def mk_api(funcs: Iterable[Callable], mall: Optional[Mall] = None, **kwargs):
    """Generates a py2http application with default configuration for extrude.

    :param funcs: A list of functions.
    :param kwargs: Any extra keyword argument used to make the py2http application.

    >>> def foo():
    ...     pass
    ...
    >>> app = mk_api([foo])
    """

    if mall is not None:

        def get_light_mall():
            def remove_values(node):
                return {
                    k: (remove_values(v) if isinstance(v, Mapping) else None)
                    for k, v in node.items()
                }

            return remove_values(mall)

        funcs = funcs + [get_light_mall]

    dflt_config = dict(
        protocol='http',
        host='localhost',
        port='3030',
        enable_cors=True,
        publish_openapi=True,
        publish_swagger=True,
    )
    ws_config = dict(dflt_config, **kwargs)

    if 'openapi' not in ws_config:
        protocol = ws_config['protocol']
        host = ws_config['host']
        port = ws_config['port']
        ws_config['openapi'] = dict(base_url=f'{protocol}://{host}:{port}')

    return mk_webservice(funcs, **ws_config)


def run_api(app, **kwargs):
    run_webservice(app, **kwargs)
