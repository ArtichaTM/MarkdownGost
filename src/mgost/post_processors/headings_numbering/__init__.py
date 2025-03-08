from mgost.context import Context
from mgost.types.run import Run
from mgost.types.simple import Heading


def process_heading(el: Heading, counters: list[int]) -> None:
    first_run = el.elements[0]
    assert isinstance(first_run, Run)
    text = first_run.start
    assert isinstance(text, str)
    if text.startswith('**'):
        text = text[2:]
        el._centered = True
        first_run.start = text
        return
    elif text.startswith('*'):
        text = text[1:]
        first_run.start = text
        el._centered = True
        counters[el.level-1] += 1
        return
    for i in range(el.level, len(counters)):
        counters[i] = 0
    counters[el.level-1] += 1
    prefix = '.'.join((str(i) for i in counters[:el.level]))
    text = f"{prefix} {text}"
    first_run.start = text


def post_process(context: Context) -> None:
    counters = [0, 0, 0]
    for els in context.root.walk():
        if isinstance(els[-1], Heading):
            process_heading(els[-1], counters)
