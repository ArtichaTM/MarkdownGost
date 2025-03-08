from abc import abstractmethod
from typing import Generator

from docx.document import Document as _Document

from .mixins import AddableToDocument, ListElement
from mgost.context import Context, ContextVariable


class ListBase(ListElement[AddableToDocument], AddableToDocument):
    __slots__ = ('style_base',)

    def __init__(self, elements: list[AddableToDocument]) -> None:
        super().__init__()
        assert len(elements) > 0, elements
        self.elements = elements

    def build_style_name(self, level: int, context: Context) -> str:
        assert isinstance(context, Context)
        assert isinstance(level, int)
        assert hasattr(self, 'style_base')
        assert isinstance(self.style_base, str)
        return f"{self.style_base}{f' {level+1}' if level > 0 else ''}"

    @abstractmethod
    def prefixes(self, context: Context) -> Generator[str, None, None]:
        ...

    def add_to_document(self, d: _Document, context: Context) -> None:
        assert isinstance(d, _Document)
        assert isinstance(context, Context)

        current_level = context.get('list_level', 0)
        style_name = self.build_style_name(current_level, context)
        markers = self.prefixes(context)
        with (
            ContextVariable(context, 'paragraph_style', style_name),
            ContextVariable(context, 'list_level', current_level+1),
            ContextVariable(context, 'do_not_add_tab', True)
        ):
            for el in self.elements:
                assert isinstance(el, AddableToDocument)
                if isinstance(el, ListBase):
                    marker = False
                else:
                    marker = next(markers)
                with ContextVariable(
                    context, 'marker', marker
                ):
                    el.add_to_document(d, context)

    def as_dict(self):
        return {
            type(self).__qualname__: [i.as_dict() for i in self.elements]
        }

    def walk(self):
        yield (self,)
        for element in self.elements:
            for sub_elements in element.walk():
                yield (self, *sub_elements)
