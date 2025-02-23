from urllib.parse import urlparse, ParseResult

from mgost.settings import get_settings
from ..mixins import AddableToDocument, MappingElement

__all__ = ('Sources', 'SourceLine')


class SourceLine(AddableToDocument):
    __slots__ = ('id', 'var', 'url')
    id: int
    var: str
    url: ParseResult

    def __init__(self, index: int, var: str, href: str) -> None:
        assert isinstance(index, int)
        assert isinstance(var, str)
        assert isinstance(href, str)
        super().__init__()
        self.id = index
        self.var = var
        self.url = urlparse(href)

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'var': self.var,
            'url': self.url
        }

    def add_to_document(self, d, context) -> None:
        settings = get_settings()
        converter = settings.source_converters.get(self.url.netloc, None)
        if converter is None:
            assert '' in settings.source_converters, settings.source_converters
            converter = settings.source_converters['']
        p = d.add_paragraph(style='List Number')
        p.add_run(f"{self.id}.\t")
        converter.parse(p, self.url, context)


class Sources(MappingElement[str, SourceLine], AddableToDocument):
    __slots__ = ()

    def as_dict(self) -> dict:
        return {
            i.id: i.as_dict() for i in self.values()
        }

    def add_to_document(self, d, context) -> None:
        for line in self.values():
            line.add_to_document(d, context)
