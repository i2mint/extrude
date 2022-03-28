from functools import wraps
import json
from sys import argv
from streamlitfront.base import dispatch_funcs
from http2py import HttpClient
from i2.wrapper import Sig


def flatten(meth):
    sig = Sig(meth) - 'self'

    @sig
    @wraps(meth)
    def flat_func(*args, **kwargs):
        return meth(*args, **kwargs)

    return flat_func


if __name__ == '__main__':
    openapi_spec = json.loads(argv[1])
    api = HttpClient(openapi_spec=openapi_spec)
    funcs = [
        flatten(api.foo),
        flatten(api.bar),
        flatten(api.confuser),
    ]

    app = dispatch_funcs(funcs)
    app()
