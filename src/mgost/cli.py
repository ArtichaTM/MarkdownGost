from pathlib import Path
from .settings import Settings

from . import _parse_args, convert


def main():
    with Settings(Path() / 'mgost'):
        source, dest = _parse_args()
        convert(source, dest)


if __name__ == '__main__':
    main()
