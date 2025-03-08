from argparse import ArgumentParser, Namespace
from logging import warning
from pathlib import Path

from . import exceptions, convert


def _build_args_parser() -> ArgumentParser:
    parser = ArgumentParser("MGost")
    parser.add_argument(
        'source',
        type=str,
        action='store',
        help='source file (.md)'
    )
    parser.add_argument(
        'destination', type=str, action='store',
        help='path to destination where save file'
    )
    return parser


def _parse_namespace(args: Namespace) -> tuple[Path, Path]:
    assert hasattr(args, 'source')
    assert hasattr(args, 'destination')

    source_str: str = args.source
    assert isinstance(source_str, str)
    source_path = Path(source_str)
    if not source_path.exists():
        raise exceptions.SourceDoesNotExist(
            f"File {source_str} does not exist"
        )

    destination_name: str = args.destination
    assert isinstance(destination_name, str)
    destination_path = Path(destination_name)
    if not destination_name.endswith('.docx'):
        warning(
            'Destination name does not end with ".docx" extension'
        )

    return source_path, destination_path


def _parse_args() -> tuple[Path, Path]:
    args_parser = _build_args_parser()
    try:
        return _parse_namespace(args_parser.parse_args())
    except (
        exceptions.SourceDoesNotExist,
        exceptions.UnknownSourceFormat
    ) as e:
        print(e.args[0])
        raise e

def main():
    source, dest = _parse_args()
    convert(source, dest)


if __name__ == '__main__':
    main()
