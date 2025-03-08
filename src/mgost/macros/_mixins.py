from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

from docx.text.paragraph import Paragraph as _Paragraph
from docx.text.run import Run as _Run

from mgost.context import Context

if TYPE_CHECKING:
    from mgost.types.macros import Macros
    from mgost.types.mixins import AddableToDocument, AddableToParagraph


class MacrosBase(ABC):  # type: ignore
    __slots__ = ('macros',)

    def __init__(self, macros: 'Macros') -> None:
        super().__init__()
        self.macros = macros

    def __repr__(self) -> str:
        return f"<Macros {type(self).__module__}>"

    @classmethod
    def get_name(cls) -> str:
        return cls.__module__.split('.')[-1]

    def parse_markdown(
        self, value: str, context: Context
    ) -> list['AddableToParagraph']:
        from mgost.md_converter import parse_from_text
        from mgost.types.simple import Paragraph

        v = parse_from_text(value, context)
        p = v.elements[0]
        assert isinstance(p, Paragraph)

        return p.elements


class Instant(MacrosBase):
    __slots__ = ()

    @abstractmethod
    def process_instant(
        self,
        context: Context
    ) -> 'Sequence[AddableToParagraph] | AddableToDocument':
        ...


class DuringDocxCreation(MacrosBase):
    __slots__ = ()

    @abstractmethod
    def process_during_docx_creation(
        self,
        p: _Paragraph,
        context: Context
    ) -> list['_Run']:
        ...


class AfterDocxCreation(MacrosBase):
    __slots__ = ()

    @abstractmethod
    def process_after_docx_creation(
        self,
        context: Context
    ) -> None:
        ...
