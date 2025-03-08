from docx.document import Document as _Document
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml.ns import qn
from docx.oxml.parser import OxmlElement
from docx.table import Table as _Table
from docx.text.paragraph import Paragraph as _Paragraph
from docx.text.run import Run as _Run

from mgost.context import Context

__all__ = ('add_hyperlink', 'add_bookmark')


def find_tags_recursively(element, tag: str):
    """
    Recursively find all occurrences
        of a specific tag in an XML element.
    """
    if element.tag == tag:
        yield element
    for child in element:
        yield from find_tags_recursively(child, tag)


def create_namespace() -> dict:
    return {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }


def add_bookmark(
    p: _Paragraph,
    context: Context,
    /,
    w_id_str: str | None = None
) -> str:
    assert w_id_str not in context.counters.bookmarks, f"{w_id_str} repeats"
    start = OxmlElement('w:bookmarkStart')
    if w_id_str is None:
        w_id = len(context.counters.bookmarks)
        w_id_str = f"{w_id}"
    start.set(qn('w:id'), w_id_str)
    start.set(qn('w:name'), w_id_str)
    end = OxmlElement('w:bookmarkEnd')
    end.set(qn('w:id'), w_id_str)

    p._p.append(start)
    p._p.append(end)

    return w_id_str


# def create_page_url(bookmark: str, context: Context) -> _Run:
#     number = OxmlElement('w:instrText')
#     number.set(qn('xml:space'), 'preserve')
#     number.text = f' {context.counters.bookmarks[bookmark]} '  # type: ignore
#     number_run = _Run(
#         OxmlElement('w:r'), p
#     )
#     number_run._element.append(number)
#     return number_run


def add_linked_run(
    p: _Paragraph,
    text: str,
    link_to: str,
    context: Context
) -> _Run:
    new_run = _Run(
        OxmlElement('w:r'), p  # type: ignore
    )
    new_run.text = text

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.append(new_run._element)
    p._p.append(hyperlink)

    try:
        hyperlink.set(qn('w:anchor'), context.counters.bookmarks[link_to])
    except KeyError:
        raise KeyError(
            f'Текст "{text}" ссылается на {link_to}'
            ', однако такого объекта не существует. '
            'Возможные варианты: '
            f'{', '.join(context.counters.bookmarks.keys())}'
        )
    return new_run


def add_hyperlink(paragraph: _Paragraph, text: str, url: str) -> _Run:
    assert isinstance(paragraph, _Paragraph)
    assert isinstance(text, str)
    assert isinstance(url, str)
    assert url.startswith('http'), 'use `link_to_bookmark` for internal links'
    # This gets access to the document.xml.rels file
    # and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id,)

    # Create a new run object (a wrapper over a 'w:r' element)
    new_run = _Run(
        OxmlElement('w:r'), paragraph  # type: ignore
    )
    new_run.text = text

    # Join all the xml elements together
    hyperlink.append(new_run._element)
    paragraph._p.append(hyperlink)
    return new_run


def table_autofit(table: _Table) -> None:
    for tag in find_tags_recursively(table._tbl, qn('w:tcW')):
        attrib = tag.attrib
        attrib[qn("w:type")] = 'auto'


def remove_paragraph(d: _Document, index: int) -> _Paragraph:
    p = d.paragraphs[index]
    p._element.getparent().remove(p._element)
    return p
