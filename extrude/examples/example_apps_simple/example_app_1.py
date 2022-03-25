"""Example app 1"""

from streamlitfront import dispatch_funcs


def foo_1(a: int = 0, b: int = 0, c=0):
    """This is foo. It computes something"""
    return (a * b) + c


def bar_1(x, greeting='hello'):
    """bar greets its input"""
    return f'{greeting} {x}'


def confuser_1(a: int = 0, x: float = 3.14):
    return (a ** 2) * x


dispatch_funcs([foo_1, bar_1, confuser_1])()
