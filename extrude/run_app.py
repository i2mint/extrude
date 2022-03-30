
import json
from typing import Callable, Iterable
from i2 import name_of_obj


def run_app(funcs: Iterable[Callable], **kwargs):
    from py2http import mk_app, run_app as run_webservice
    from py2http.util import run_process
    import streamlit.bootstrap

    with run_process(
        func=run_webservice,
        func_kwargs=dict(
            app_obj=funcs,
            publish_openapi=True,
            publish_swagger=True
        ),
        is_ready=3
    ):
        app = mk_app(funcs)
        func_names = [name_of_obj(func) for func in funcs]
        streamlit.bootstrap.run(
            __file__,
            args=[
                json.dumps(app.openapi_spec),
                json.dumps(func_names),
                json.dumps(kwargs),
            ],
            command_line='',
            flag_options={}
        )


if __name__ == '__main__':

    from sys import argv
    from functools import wraps
    from http2py import HttpClient
    from i2.wrapper import Sig
    from streamlitfront.base import dispatch_funcs

    def _flatten(meth):
        sig = Sig(meth) - 'self'

        @sig
        @wraps(meth)
        def flat_func(*args, **kwargs):
            return meth(*args, **kwargs)

        return flat_func


    openapi_spec=json.loads(argv[1])
    func_names=json.loads(argv[2])
    kwargs = json.loads(argv[3])
    api = HttpClient(openapi_spec=openapi_spec)
    funcs = [_flatten(getattr(api, name)) for name in func_names]

    app = dispatch_funcs(funcs, **kwargs)
    app()
