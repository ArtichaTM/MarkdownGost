from typing import TYPE_CHECKING, Literal

from mgost.context import Context
from mgost.types.mixins import HasText
from mgost.types.run import Run
from mgost.types.simple import Heading

if TYPE_CHECKING:
    from mgost.types.complex.sources import SourceLine


def process_run(
    run: Run,
    variable: str,
    context: Context,
    cl: type['SourceLine']
) -> None:
    href = run.href
    pre_text: str = ''
    if variable.startswith('*'):
        variable = variable[1:]
        pre_text: str = ''
    else:
        pre_text = f"{variable} "
    assert isinstance(href, str)
    source = cl(len(context.sources)+1, variable, href)
    context.sources[variable] = source
    run.start = f"{pre_text}[{source.id}]"
    run.href = None


def post_process(context: Context) -> None:
    from mgost.types.complex.sources import SourceLine
    for *_, el in context.root.walk():
        if isinstance(el, Heading):
            run = el.elements[0]
            if isinstance(run, HasText) and isinstance(run.get_text(), str):
                if 'Заключение' in run.get_text():
                    break

        # Must be with a text
        if not isinstance(el, Run):
            continue

        # Must contain href
        if el.href is None:
            continue

        # Should be an external link
        if not el.href.startswith(('http', 'ssh', 'ftp')):
            continue

        # Text should be '[]'
        if el.start is None:
            continue
        if not (el.start.startswith('[') and el.start.endswith(']')):
            continue

        variable: str | Literal[''] = el.start[1:-1]

        process_run(el, variable, context, SourceLine)
