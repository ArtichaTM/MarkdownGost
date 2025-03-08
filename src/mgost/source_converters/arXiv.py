from dataclasses import dataclass
from datetime import datetime
from re import findall

from ._base import SourceConverter


@dataclass
class ArXivData:
    id: str
    published: datetime
    title: str
    summary: str
    authors: list[str]


@dataclass
class ArXivError:
    info: str


def find_enclosed(text: str, tag: str) -> tuple[str, int, int]:
    start = text.find(f'<{tag}>') + len(tag)+2
    assert start != -1, f"{tag}: {text!r}"
    end = text[start:].find(f"</{tag}>") + start
    assert end != -1, f"{tag}: {text!r}"
    return text[start:end], start, end


def parse_xml(text: str) -> 'ArXivData | ArXivError':
    assert isinstance(text, str)
    text = text.replace('\n', '')
    entry, *_ = find_enclosed(text, 'entry')
    assert entry, f"{text}, {entry}"
    id, *_ = find_enclosed(entry, 'id')
    assert id, id
    title, *_ = find_enclosed(entry, 'title')
    assert title, title
    summary, _, end = find_enclosed(entry, 'summary')
    assert summary, summary
    if title == 'Error':
        return ArXivError(summary)
    published, *_ = find_enclosed(entry, 'published')
    assert published, published

    entry = entry[end:]
    authors = [i for i in findall(r'<name>([\w\s]+)<\/name>', entry)]

    return ArXivData(
        id=id,
        published=datetime.fromisoformat(published),
        title=title,
        summary=summary.strip(),
        authors=authors
    )


class Converter(SourceConverter):
    __slots__ = ()

    def get_parsing_domain(self) -> str:
        return 'arxiv.org'

    def parse(self, p, parsed_result, context):
        temp = parsed_result.path.split('/')
        assert len(temp) == 3, f"{temp}({len(temp)})"
        work_id = temp[-1]
        assert '.' in work_id, work_id

        url = f'https://export.arxiv.org/api/query?id_list={work_id}v1'
        page = context.internet_connection(url, url_expire=-1.0)

        if page is None:
            p.add_run("- Error during requesting site -")
            return

        try:
            parsed = parse_xml(page.text)
        except AssertionError as e:
            p.add_run(f"- Error during arXiv parse: {e.args[0]!r}- ")
            return
        if isinstance(parsed, ArXivError):
            p.add_run(f"- Error in arXiv request: {parsed.info}- ")
            return
        p.add_run(
            f"{', '.join(parsed.authors)}. "
            f"{parsed.title} — arXiv, {parsed.published.year}."
        )
