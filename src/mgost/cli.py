from pathlib import Path

from . import _parse_args, convert
from .settings import Settings


def main():
    with Settings(Path() / 'mgost'):
        source, dest = _parse_args()
        convert(source, dest)


if __name__ == '__main__':
    main()
