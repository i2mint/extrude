from extrude.run_app import run_app


def foo(a: int = 0, b: int = 0, c=0):
    """This is foo. It computes something"""
    return (a * b) + c


def bar(x, greeting='hello'):
    """bar greets its input"""
    return f'{greeting} {x}'


def confuser(a: int = 0, x: float = 3.14):
    return (a ** 2) * x


funcs = [foo, bar, confuser]


if __name__ == '__main__':
    run_app(funcs)
