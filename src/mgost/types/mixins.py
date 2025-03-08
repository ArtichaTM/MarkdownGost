from abc import abstractmethod
from typing import Generator

from docx.document import Document as _Document
from docx.text.paragraph import Paragraph as _Paragraph
from docx.text.run import Run as _Run

from .abstract import AbstractElement
from mgost.context import Context


class AddableToParagraph(AbstractElement):
    __slots__ = ()

    @abstractmethod
    def add_to_paragraph(self, p: _Paragraph, context: Context) -> list[_Run]:
        ...


class AddableToDocument(AbstractElement):
    __slots__ = ()

    @abstractmethod
    def add_to_document(self, d: _Document, context: Context) -> None:
        ...


class ContainerElement[T: AbstractElement](AbstractElement):
    __slots__ = ()

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __iter__(self) -> Generator[T, None, None]:
        ...

    @abstractmethod
    def find_and_replace(self, key: T, replacement: T) -> None:
        ...


class ListElement[T: AbstractElement](ContainerElement[T]):
    __slots__ = ('elements',)
    elements: list[T]

    def __init__(self) -> None:
        super().__init__()
        self.elements = []

    def __repr__(self) -> str:
        return (
            f"<{type(self).__qualname__} of "
            f"{len(self.elements)} elements>"
        )

    def __len__(self) -> int:
        return len(self.elements)

    def __iter__(self) -> Generator[T, None, None]:
        yield from self.elements

    def __bool__(self) -> bool:
        return any((bool(run) for run in self.elements))

    def as_dict(self):
        return {
            f"{type(self).__qualname__}": [
                i.as_dict() for i in self.elements
            ]
        }

    def find_and_replace(self, key: T, replacement: T) -> None:
        index = self.elements.index(key)
        if index == -1:
            raise KeyError(key)
        self.elements.pop(index)
        self.elements.insert(index, replacement)

    def add(self, *el: T) -> None:
        assert T.__constraints__ is not None
        assert (isinstance(
            i, T.__constraints__
        ) for i in el), f"{type(el)}({el})"
        self.elements.extend(el)

    def iter_sub_elements(self) -> Generator[T, None, None]:
        yield from self.elements

    def pop(self, el: T) -> None:
        index = self.elements.index(el)
        if index == -1:
            raise KeyError(f"Can't find {el} in {self}")
        self.elements.pop(index)

    def walk(self):
        yield (self,)
        for element in self.elements:
            for sub_elements in element.walk():
                yield (self, *sub_elements)


class MappingElement[KT: (int, str), T: AbstractElement](
    dict[KT, T], ContainerElement[T]
):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} of {len(self)} elements>"

    def as_dict(self):
        return {
            k: v.as_dict() for k, v in self.items()
        }

    def find_and_replace(self, key: T, replacement: T) -> None:
        for k, value in self.items():
            if id(key) == id(value):
                self[k] = replacement
                return
        raise KeyError(key)

    def find(self, el: T) -> KT | None:
        k: KT | None = None
        target = id(el)
        for key, value in self.items():
            if target == id(value):
                k = key
                break
        return k

    def walk(self):
        yield (self,)
        for element in self.values():
            for sub_elements in element.walk():
                yield (self, *sub_elements)


class HasText(AbstractElement):
    @abstractmethod
    def get_text(self) -> str:
        ...


class HasEditableText(HasText):
    @abstractmethod
    def set_text(self, text: str) -> None:
        ...
