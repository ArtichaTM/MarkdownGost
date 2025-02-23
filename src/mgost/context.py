from typing import TYPE_CHECKING, Any, Generator, Hashable, MutableMapping
from pathlib import Path
from dataclasses import dataclass, field
from io import BytesIO
from pprint import pformat

import sympy
from docx.document import Document
from docx.oxml.xmlchemy import BaseOxmlElement


if TYPE_CHECKING:
    from mgost.types.abstract import AbstractElement
    from mgost.types.simple import Root
    from mgost.types.complex.sources import Sources
    from mgost.macros import macros_mixins


@dataclass(frozen=True)
class ListMarkerInfo:
    mark: str
    endline: str
    endline_end: str


@dataclass(frozen=False, slots=True)
class Counters:
    headings: list[int] = field(default_factory=lambda: [0, 0, 0], init=False)
    image: dict[int, int] = field(default_factory=dict, init=False)
    table: dict[int, int] = field(default_factory=dict, init=False)
    formula: dict[int, int] = field(default_factory=dict, init=False)
    bookmarks: dict[str, 'AbstractElement'] = field(
        default_factory=dict, init=False
    )

    def __repr__(self) -> str:
        return (
            f"<C {self.headings},{self.image},{self.table},"
            f"{self.formula},{self.bookmarks}>"
        )

    def __str__(self) -> str:
        return (
            "Images: " + pformat(self.image) +
            "\nTables: " + pformat(self.image) +
            "\nFormulas: " + pformat(self.image) +
            "\nBookmarks: " + pformat(self.image)
        )

    def copy_to(self, other: 'Counters'):
        other.headings = self.headings.copy()
        other.image = self.image.copy()
        other.table = self.table.copy()
        other.formula = self.formula.copy()
        other.bookmarks = self.bookmarks.copy()


class Context(dict):
    """ Contains document building context
    Probable variables based on context:
    <paragraph_style>: style of the current paragraph.
        used to "paragraph = d.styles[STYLE]"
    <list_level>: current list level. Starts from 1, not 0
    <do_not_add_tab>: if set, no "\\t" is added to the tart of paragraph
    <bold>: if set, text will be bold
    <em>: if set, text will be italic
    <strike>: if set, text font will be strike
    <strip>: a ".strip()" will be called on run(-s) string
    <no_new_line>: if True, Run.end will NOT
        be replaced with '' if it equals to '\n'
    """
    __slots__ = (
        'source', 'output',

        'd', 'counters', 'root',
        'variables', 'mentions',
        'post_process_links', 'post_docx_macroses',
        'formula_symbols', 'sources',
        'list_marker_info', 'list_digit_info',
        'table_name', 'current_file_path',
    )
    _global_context: 'Context | None' = None
    source: Path
    output: Path | BytesIO

    d: Document
    counters: Counters
    root: 'Root'
    variables: dict[str, Any]
    mentions: dict[str, str]
    post_process_links: dict[str, BaseOxmlElement]
    post_docx_macroses: list['macros_mixins.AfterDocxCreation']
    formula_symbols: dict[str, sympy.Symbol | sympy.Function]
    sources: 'Sources'
    current_file_path: Path

    # Editable values
    list_marker_info: ListMarkerInfo
    list_digit_info: ListMarkerInfo
    table_name: str | None

    def __init__(
        self,
        source: Path,
        output: Path | BytesIO
    ):
        # Argument assertions
        assert isinstance(source, Path), source
        assert isinstance(output, (Path | BytesIO)), output
        assert source.exists()

        # Setting arguments
        self.source = source
        self.output = output

        # Dict init
        super().__init__()

        # Imports. They are here
        # bcz context should be independent during file imports
        from mgost.types.complex.sources import Sources

        self.counters = Counters()
        self.variables = dict()
        self.post_process_links = dict()
        self.formula_symbols = dict()
        self.list_marker_info = ListMarkerInfo('•', ';', '.')
        self.list_digit_info = ListMarkerInfo('{counter}. ', ';', '.')
        self.table_name = None
        self.post_docx_macroses = []
        self.sources = Sources()

        # Setting global context. Global context is the first context created
        if self._global_context is None:
            type(self)._global_context = self

    def __repr__(self) -> str:
        return f"<Settings -> {self.output}>"

    @classmethod
    def global_context(cls) -> 'Context':
        assert cls._global_context is not None
        return cls._global_context

    def walk_roots(self) -> Generator[
        tuple['AbstractElement', ...], None, None
    ]:
        for elements in self.root.walk():
            yield elements


class ContextVariable:
    __slots__ = ('target', 'key', 'previous_value', 'new_value', 'skip')

    def __init__(
        self,
        target: MutableMapping,
        key: Hashable,
        new_value: Any,
        /,
        apply: bool = True
    ) -> None:
        assert isinstance(target, MutableMapping)
        self.target = target
        self.key = key
        self.new_value = new_value
        self.previous_value = None
        self.skip = not apply

    def __enter__(self):
        if self.skip:
            return self
        if self.key in self.target:
            self.previous_value = self.target[self.key]
        self.target[self.key] = self.new_value
        return self

    def __exit__(self, *_):
        if self.skip:
            return
        assert self.key in self.target
        if self.previous_value is None:
            del self.target[self.key]
        else:
            self.target[self.key] = self.previous_value
