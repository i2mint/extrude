"""A module of functions imported by __init__.py"""
from from_func_list.utils import add


def foo(a: int = 0, b: int = 0, c=0):
    """This is foo. It computes something"""
    return add((a * b), c)


def bar(x, greeting='hello'):
    """bar greets its input"""
    return f'{greeting} {x}'


def confuser(a: int = 0, x: float = 3.14):
    return (a ** 2) * x
