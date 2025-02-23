from pathlib import Path
from .settings import init_settings

from . import _parse_args, convert


def main():
    with init_settings(Path() / 'mgost'):
        source, dest = _parse_args()
        convert(source, dest)


if __name__ == '__main__':
    main()
