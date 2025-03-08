from pathlib import Path
from xml.etree import ElementTree as et

from marko.ext.gfm import gfm

from .parser import parse_element
from mgost.context import Context
from mgost.types.simple import Root


def parse_from_text(value: str, context: Context) -> Root:
    html = gfm(value)
    values = et.fromstring(f"<html>{html}</html>")
    assert isinstance(values, et.Element), type(values)
    root = parse_element(values, context)
    return root


def parse(path: Path, context: Context) -> Root:
    markdown = path.read_text(encoding='utf-8')
    return parse_from_text(markdown, context)
