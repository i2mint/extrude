from functools import wraps
from streamlitfront.base import dispatch_funcs
from http2py import HttpClient
from i2.wrapper import Sig

def flat(meth):
    sig = Sig(meth) - 'self'

    @sig
    @wraps(meth)
    def flat_func(*args, **kwargs):
        return meth(*args, **kwargs)

    return flat_func

def mk_api():
    api_url = "http://127.0.0.1:3030"  # TODO: should get this from service object
    return HttpClient(url=f"{api_url}/openapi")  # Why openapi?

if __name__ == '__main__':
    api = mk_api()
    funcs = [
        flat(api.foo),
        flat(api.bar),
        flat(api.confuser),
    ]

    app = dispatch_funcs(funcs)
    app()
