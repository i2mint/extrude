"""A child module that includes inline configs for extrude's multi app dispatch."""

from streamlitfront import dispatch_funcs


def foo_1(a: int = 0, b: int = 0, c=0):
    """This is foo. It computes something"""
    return (a * b) + c


def bar_1(x, greeting='hello'):
    """bar greets its input"""
    return f'{greeting} {x}'


def confuser_1(a: int = 0, x: float = 3.14):
    return (a ** 2) * x


def dispatch_child_app():
    return dispatch_funcs([foo_1, bar_1, confuser_1])


extrude_configs = {
    'display_name': 'Streamlitfront App with Inline Config',
    'dispatch': dispatch_child_app,
}
