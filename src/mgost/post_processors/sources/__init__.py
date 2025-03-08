from logging import warning

from mgost.context import Context
from mgost.types.mixins import AbstractElement
from mgost.types.run import Run
from mgost.types.simple import Paragraph, Root


def replace_el(els: tuple[AbstractElement, ...], context: Context) -> None:
    assert len(els) == 3
    root, p, run = els
    assert isinstance(root, Root)
    assert isinstance(p, Paragraph)
    assert isinstance(run, Run)
    root.find_and_replace(p, context.sources)


def post_process(context: Context) -> None:
    target_els: list[tuple[AbstractElement, ...]] = []
    for *els, el in context.root.walk():
        if not isinstance(el, Run):
            continue

        text = el.start
        if text is None:
            continue

        if not (text.startswith('[') and text.endswith(']')):
            continue

        text = text[1:-1].lower()
        if text not in {'источники', 'sources'}:
            continue

        target_els.append((*els, el))

    if not target_els:
        warning(
            'Trying to use preprocessor "sources", '
            "but no target found. "
            "Use [sources] in any line"
        )

    for els in target_els:
        replace_el(els, context)
