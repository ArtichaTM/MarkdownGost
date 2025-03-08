from datetime import datetime, timedelta
from logging import warning
from random import random

from ._base import SourceConverter


def find_enclosed(text: str, tag: str) -> tuple[str, int, int]:
    assert isinstance(text, str), text
    assert isinstance(tag, str), tag
    start = text.find(f'<{tag}>') + len(tag)+2
    assert start != -1, f"{tag}: {text!r}"
    end = text[start:].find(f"</{tag}>") + start
    assert end != -1, f"{tag}: {text!r}"
    return text[start:end], start, end


class Converter(SourceConverter):
    __slots__ = ('today', 'difference')

    def __init__(self) -> None:
        super().__init__()
        self.today = datetime.today().timestamp()
        self.difference = self.today - (
            datetime.today() - timedelta(weeks=30)
        ).timestamp()

    def _random_date(self) -> str:
        random_date_fl = self.today - self.difference*random()
        random_date = datetime.fromtimestamp(random_date_fl)
        return random_date.strftime('%d.%m.%Y')

    def get_parsing_domain(self) -> str:
        return ''

    def parse(self, p, parsed_result, context):
        url = parsed_result.geturl()
        try:
            page = context.internet_connection(
                url,
                url_expire=60*60*24*7.0
            )
        except ConnectionResetError:
            p.add_run(
                f"Connection reset while tried connecting to {url}"
            )
            return
        except Exception as e:
            p.add_run(
                f"Got exception during parsing: {type(e).__qualname__}{e.args}"
            )
            warning(
                f"{type(e).__qualname__} during internet request",
                exc_info=e
            )
            return
        if page is None:
            p.add_run(
                f"Can't connect to {url}"
            )
            return
        title, *_ = find_enclosed(page.text, 'title')
        p.add_run(
            f"«{title}», "
            f"[Электронные ресурс]. — URL: {url} "
            f"(дата обращения: {self._random_date()})"
        )
