from typing import Sequence
from urllib.parse import unquote
from xml.etree import ElementTree as et

from .exceptions import UnknownTag
from mgost.context import Context
from mgost.types.lists import ListBullet, ListNumbered
from mgost.types.macros import Macros
from mgost.types.media import Image, Table
from mgost.types.mixins import AddableToDocument, AddableToParagraph
from mgost.types.run import Run
from mgost.types.simple import Heading, Paragraph, Root


def parse_plain_text(
    text: str, context: Context
) -> Sequence[AddableToParagraph]:
    from . import parse_from_text
    v = parse_from_text(text, context)
    p = v.elements[0]
    assert isinstance(p, Paragraph)
    return p.elements


def _parse_text(
    element: et.Element
) -> list[AddableToParagraph] | AddableToDocument:
    assert isinstance(element, et.Element)
    runs: list[AddableToParagraph] | None = None
    match element.tag:
        case 'strong':
            runs = [Run(element.text, element.tail, bold=True)]
        case 'em':
            runs = [Run(element.text, element.tail, italic=True)]
        case 'del':
            runs = [Run(element.text, element.tail, strike=True)]
        case 'a':
            runs = [Run(
                element.text,
                element.tail,
                href=unquote(element.attrib['href'])
            )]
        case 'code':
            assert element.text is not None
            temp = Macros(element.text, element.tail)
            temp = temp.replace(Context.global_context())
            if isinstance(temp, AddableToDocument):
                return temp
            assert isinstance(temp, list), f"{type(temp).__qualname__}({temp})"
            runs = temp
        case 'th' | 'td':
            runs = [Run(element.text, element.tail, in_table=True)]
        case _:
            raise UnknownTag(f"What is {element.tag}?")

    assert isinstance(runs, list), f"{type(runs)}({runs})"
    assert all((isinstance(i, AddableToParagraph) for i in runs)), runs

    for child in element:
        try:
            temp = _parse_text(child)
            if isinstance(temp, AddableToDocument):
                return temp
            assert isinstance(temp, list)
            runs.extend(temp)
        except UnknownTag as e:
            print(f"Got unknown tag: UnknownTag({e.args[0]!r})")
            pass

    return runs


def _parse_li(element: et.Element) -> Sequence[AddableToDocument]:
    assert isinstance(element, et.Element)
    assert element.tag == 'li'
    runs: list[AddableToParagraph] = [Run(element.text, element.tail)]
    elements: Sequence[AddableToDocument] = []

    for child in element:
        try:
            new_runs = _parse_text(child)
        except UnknownTag:
            pass
        else:
            if isinstance(new_runs, AddableToDocument):
                elements.append(new_runs)
            else:
                runs.extend(new_runs)
            continue

        if runs:
            elements.append(Paragraph(runs))
            runs = []

        new_elements = _parse_element(child)  # type: ignore
        assert isinstance(new_elements, list)
        assert all(isinstance(i, AddableToDocument) for i in new_elements)
        new_elements: list[AddableToDocument]
        elements.extend(new_elements)

    if runs:
        elements.append(Paragraph(runs))

    assert elements
    return elements


def _parse_table_row(element: et.Element) -> list[Paragraph]:
    output: list[Paragraph] = []
    assert element.tag == 'tr', element.tag
    for column in element:
        runs = _parse_text(column)
        assert isinstance(runs, list)
        if runs and isinstance(runs[-1], Run) and runs[-1].start:
            start = runs[-1].start
            start = start.strip(',. :;')
            start = f"{start[0].upper()}{start[1:]}"
        output.append(Paragraph(runs))
    return output


def _parse_table(element: et.Element) -> Table:
    output: list[list[Paragraph]] = []
    thead, tbody = element

    thead = thead.find('tr')
    assert thead is not None
    output.append(_parse_table_row(thead))
    for p in output[0]:
        for run in p.elements:
            assert isinstance(run, Run)
            run.bold = True

    for tr in tbody:
        output.append(_parse_table_row(tr))

    return Table(output)


def _parse_element(
    element: et.Element
) -> Sequence[AddableToDocument] | Sequence[AddableToParagraph] | Root:
    elements: Sequence[AddableToDocument]
    runs: list[AddableToParagraph]
    match element.tag:
        case 'html':
            elements = []
            for child in element:
                assert isinstance(child, et.Element), type(child)
                new_elements = _parse_element(child)  # type: ignore
                assert not isinstance(new_elements, Root)
                assert all(isinstance(
                    i, AddableToDocument
                ) for i in new_elements), new_elements
                new_elements: list[AddableToDocument]
                elements.extend(new_elements)
            assert all(isinstance(i, AddableToDocument) for i in elements)
            return Root(elements)
        case 'h1' | 'h2' | 'h3':
            runs: list[AddableToParagraph] = [Run(element.text, element.tail)]
            for child in element:
                temp = _parse_text(child)
                if isinstance(temp, AddableToDocument):
                    return [temp]
                runs.extend(temp)
            return [Heading(runs, int(element.tag[1:]))]
        case 'p':
            runs = []
            if element.text:
                runs.append(Run(element.text, element.tail))
            for child in element:
                if child.tag == 'img':
                    src = child.attrib.get('src', None)
                    assert isinstance(src, str)
                    src = src.replace('%20', ' ')
                    alt = child.attrib.get('alt', None)
                    assert isinstance(alt, str)
                    title = child.attrib.get('title', None)
                    assert title is None or isinstance(title, str)
                    parsed_alt = parse_plain_text(
                        alt, Context.global_context()
                    )
                    image = Image(
                        src=src,
                        alt=parsed_alt,  # type: ignore
                        title=title
                    )
                    return [image]
                t = _parse_text(child)
                if isinstance(t, AddableToDocument):
                    return [t]
                runs.extend(t)
            return [Paragraph(runs)]
        case 'hr':
            runs = [Run(element.text, element.tail)]
            for child in element:
                runs.append(Run(child.text, child.tail))
            return [Paragraph(runs)]
        case 'ul':
            elements = []
            for li in element:
                assert li.tag == 'li'
                elements.extend(_parse_li(li))
            assert elements
            return [ListBullet(elements)]
        case 'ol':
            elements = []
            for li in element:
                assert li.tag == 'li'
                elements.extend(_parse_li(li))
            assert elements
            return [ListNumbered(elements)]
        case 'pre':
            code_el = element[0]
            assert code_el.tag == 'code'
            result = _parse_text(code_el)
            if isinstance(result, list):
                return [Paragraph(result)]
            return [result]
        case 'table':
            return [_parse_table(element)]
        case _:
            raise UnknownTag(f"What is {element.tag}?")


def parse_element(element: et.Element, context: Context) -> Root:
    output = _parse_element(element)
    assert isinstance(output, Root)
    return output
