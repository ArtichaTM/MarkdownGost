from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from docx.text.paragraph import Paragraph as _Paragraph
from docx.text.run import Run as _Run

from ._flags import MacrosFlags
from mgost.context import Context
from mgost.types.run import Run

if TYPE_CHECKING:
    from mgost.types.macros import Macros
    from mgost.types.mixins import AddableToDocument, AddableToParagraph


logger = getLogger(__name__)


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

    @staticmethod
    @abstractmethod
    def flags() -> MacrosFlags:
        ...

    def check_file(self, name: str, context: Context) -> list[Run] | Path:
        assert isinstance(name, str)
        assert self.flags() & MacrosFlags.FILE_READING
        name = (
            name[:30]
            .replace('..\\', '')
            .replace('../', '')
        )
        if not name:
            logger.info(
                f'Макрос "{self.get_name()}": не '
                'указан файл'
            )
            return [Run("<Ошибка: не указан файл>")]
        path = context.source.parent / name
        if not path.exists():
            logger.info(
                f'Макрос "{self.get_name()}": файл '
                f'{name} не существует'
            )
            return [Run("<Ошибка: нет файла>")]
        if not path.is_file():
            logger.info(
                f'Макрос "{self.get_name()}": цель '
                f'{name} не является файлом'
            )
            return [Run("<Ошибка: цель не является файлом>")]
        return path

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
    ) -> Sequence['_Run']:
        ...


class AfterDocxCreation(MacrosBase):
    __slots__ = ()

    @abstractmethod
    def process_after_docx_creation(
        self,
        context: Context
    ) -> None:
        ...
