import sys


def test_python_is_new_enough() -> None:
    assert sys.version_info >= (3, 12), f"Python 3.12+ required, found {sys.version.split()[0]}"
