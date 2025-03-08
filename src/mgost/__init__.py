from io import BytesIO
from pathlib import Path
from typing import overload

from docx import Document

from . import exceptions
from .context import Context
from .md_converter import parse as parse_md
from .post_processors import get_post_processors
from .types.simple import Root

__all__ = (
    'Context',
    'exceptions',
    'convert',
)


@overload
def convert(source: Path, dest: Path | BytesIO) -> None: ...


@overload
def convert(context: Context) -> None: ...


def convert(*args) -> None:  # type: ignore
    context = None
    match len(args):
        case 2:
            source, dest, *_ = args
            assert isinstance(source, Path)
            assert isinstance(dest, (Path, BytesIO))
            context = Context(source, dest)
        case 1:
            context, *_ = args
            assert isinstance(context, Context)
        case _:
            RuntimeError(f"Unsupported arguments: {args}")

    assert isinstance(context, Context)

    context.d = Document(str(context.paths.base_docx))
    # for style in context.d.styles:
    #     print(style.name)
    root = parse_md(context.source, context)
    root.file_path = context.source
    context.root = root

    for post_processor in get_post_processors().values():
        post_processor(context)

    root = context.root
    assert isinstance(root, Root)
    assert isinstance(root.file_path, Path)
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
