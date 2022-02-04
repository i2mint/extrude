"""
Control complex python object through strings.
Wrap functions so that the complex arguments can be specified through a string key
that points to the actual python object (which is stored in a session's memory or
persisted in some fashion).
"""

from typing import Any, Mapping, Optional, Callable
from i2 import Sig
from i2.wrapper import Ingress, wrap
from inspect import Parameter
from contextlib import suppress

ignore_import_problems = suppress(ImportError, ModuleNotFoundError)


KT = str
VT = Any
StoreType = Mapping[KT, VT]
StoreName = KT
Mall = Mapping[StoreName, StoreType]


def auto_key(*args, **kwargs) -> KT:
    """Make a str key from arguments.

    >>> auto_key(1,2,c=3,d=4)
    '1,2,c=3,d=4'
    >>> auto_key(1,2)
    '1,2'
    >>> auto_key(c=3,d=4)
    'c=3,d=4'
    >>> auto_key()
    ''
    """
    args_str = ",".join(map(str, args))
    kwargs_str = ",".join(map(lambda kv: f"{kv[0]}={kv[1]}", kwargs.items()))
    return ",".join(filter(None, [args_str, kwargs_str]))


def prepare_for_crude_dispatch(
    func: Callable,
    store_for_param: Optional[Mall] = None,
    output_store_name: Optional[str] = None,
    save_name_param="save_name",
):
    """Wrap func into something that is ready for CRUDE dispatch.

    :param func: The function to wrap
    :param store_for_param:
    :param output_store_name:
    :param save_name_param:
    :return:
    """

    ingress = None
    if store_for_param is not None:
        sig = Sig(func)
        crude_params = [x for x in sig.names if x in store_for_param]

        def kwargs_trans(outer_kw):
            def gen():
                for store_name in crude_params:
                    store_key = outer_kw[store_name]
                    yield store_name, store_for_param[store_name][store_key]

            return dict(gen())

        save_name_param = Parameter(
            name=save_name_param,
            kind=Parameter.KEYWORD_ONLY,
            default="",
            annotation=str,
        )

        ingress = Ingress(
            inner_sig=sig,
            kwargs_trans=kwargs_trans,
            outer_sig=(
                sig.ch_annotations(**{name: str for name in crude_params})
                + [save_name_param]
            ),
        )

    egress = None
    if output_store_name:

        def egress(func_output):
            print(f"{list(store_for_param[output_store_name])=}")
            store_for_param[output_store_name] = func_output
            print(f"{list(store_for_param[output_store_name])=}")
            return func_output

    wrapped_f = wrap(func, ingress, egress)

    return wrapped_f
