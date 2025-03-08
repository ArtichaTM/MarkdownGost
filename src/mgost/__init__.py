from argparse import ArgumentParser, Namespace
from io import BytesIO
from logging import warning
from pathlib import Path

from docx import Document

from . import exceptions
from .context import Context
from .md_converter import parse as parse_md
from .settings import Settings
from .types.simple import Root
from mgost.post_processors import get_post_processors

__all__ = (
    'convert',
    'Settings',
)


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


def convert(source: Path, dest: Path | BytesIO) -> None:
    if Settings.initialized():
        self_init_settings = False
        settings = Settings.get()
    else:
        self_init_settings = True
        settings = Settings(None)

    try:
        context = Context(source, dest)
        context.d = Document(str(settings.paths.base_docx))
        # for style in context.d.styles:
        #     print(style.name)
        assert isinstance(source, Path)
        context.current_file_path = source
        root = parse_md(source, context)
        root.file_path = source
        context.root = root

        for post_processor in get_post_processors().values():
            post_processor(context)

        root = context.root
        assert isinstance(root, Root)
        assert isinstance(root.file_path, Path)
        context.current_file_path = root.file_path
        root.add_to_document(context.d, context)
        # from pprint import pp
        # pp(context.sources.as_dict())
        # pp(root.as_dict())

        for macros in context.post_docx_macroses:
            macros.process_after_docx_creation(context)

        assert isinstance(context.output, (Path, BytesIO))
        if isinstance(context.output, Path):
            context.d.save(str(context.output))
        else:
            context.d.save(context.output)
    finally:
        if self_init_settings:
            settings.close()
