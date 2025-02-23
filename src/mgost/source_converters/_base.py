from abc import ABC, abstractmethod
from urllib.parse import ParseResult

from docx.text.paragraph import Paragraph as _Paragraph

from mgost.context import Context


class SourceConverter(ABC):
    __slots__ = ()

    @abstractmethod
    def get_parsing_domain(self) -> str:
        """
        This method returns domain that it parses.
        for example for url
        `https://gist.github.com/RLBot/RLBot/wiki/Useful-Game-Values`
        this code will return "gist.github.com"
        """
        raise NotImplementedError()

    @abstractmethod
    def parse(
        self,
        p: _Paragraph,
        parsed_result: ParseResult,
        context: Context,
    ):
        raise NotImplementedError()
