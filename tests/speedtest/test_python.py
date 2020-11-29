def func():
    return 42


def test_python():
    a = 0
    for i in range(10000000):
        a += func()
