from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from logging import INFO, StreamHandler, getLogger
from pathlib import Path

from . import Context, MacrosFlags, convert, exceptions

logger = getLogger(__name__)


@dataclass(frozen=True, repr=True, slots=True)
class ArgsInfo:
    source: Path
    destination: Path
    quite: bool
    user_agent: str | None
    macros_permissions: MacrosFlags


def _build_args_parser() -> ArgumentParser:
    parser = ArgumentParser("MGost")
    parser.add_argument(
        'source',
        type=str,
        action='store',
        help='source file (.md)',
        default='main.md'
    )
    parser.add_argument(
        'destination', type=str, action='store',
        help='path to destination where save file',
        default='output.docx'
    )
    parser.add_argument(
        '-q', '--quite', help='Disabled output in std',
        action='store_true',
    )
    parser.add_argument(
        '--user-agent', help='User agent of internet requests',
        action='store'
    )
    parser.add_argument(
        '--macros-allow', help='Allow specific macros flag',
        action='append'
    )
    return parser


def _parse_namespace(args: Namespace) -> ArgsInfo:
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
        logger.warning(
            'Destination name does not end with ".docx" extension'
        )

    macros_permissions = MacrosFlags.DEFAULT
    if args.macros_allow:
        for new_permission_name in args.macros_allow:
            new_permission_name: str
            new_permission_name = new_permission_name.upper()
            try:
                new_permission = MacrosFlags[new_permission_name]
            except KeyError:
                logger.exception(
                    f"There's no permission {new_permission_name}"
                )
                raise
            macros_permissions |= new_permission

    return ArgsInfo(
        source=source_path,
        destination=destination_path,
        quite=args.quite,
        user_agent=args.user_agent,
        macros_permissions=macros_permissions,
    )


def _parse_args() -> ArgsInfo:
    args_parser = _build_args_parser()
    try:
        return _parse_namespace(args_parser.parse_args())
    except (
        exceptions.SourceDoesNotExist,
        exceptions.UnknownSourceFormat
    ) as e:
        logger.exception(e.args[0], exc_info=e)
        raise e


def main():
    from . import logger
    args = _parse_args()
    if not args.quite:
        logger.addHandler(StreamHandler())
    logger.setLevel(INFO)
    convert(Context(
        args.source, args.destination,
        user_agent=args.user_agent,
        macros_permissions=args.macros_permissions
    ))


if __name__ == '__main__':
    main()
