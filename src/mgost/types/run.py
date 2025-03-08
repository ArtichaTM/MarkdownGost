from .functions import add_run
from .mixins import AddableToParagraph, HasEditableText, ListElement
from mgost.context import ContextVariable


class Run(
    ListElement[AddableToParagraph],
    AddableToParagraph,
    HasEditableText
):
    __slots__ = (
        'in_table',

        'start', 'end', 'href',
        'bold', 'italic', 'strike', 'strip',
    )

    def __init__(
        self,
        start: str | None,
        end: str | None = None,
        /,
        bold: bool = False,
        italic: bool = False,
        strike: bool = False,
        strip: bool = False,
        href: str | None = None,
        in_table: bool = False
    ) -> None:
        assert start is None or isinstance(start, str)
        assert end is None or isinstance(end, str)
        assert isinstance(bold, bool)
        assert isinstance(italic, bool)
        assert isinstance(strike, bool)
        assert isinstance(strip, bool)
        assert href is None or isinstance(href, str)
        super().__init__()
        self.start = start
        self.end = end
        self.bold = bold
        self.italic = italic
        self.strike = strike
        self.strip = strip
        self.href = href
        self.in_table = in_table

    def __repr__(self) -> str:
        if not self:
            return "<Run empty>"
        if self.end == '\n':
            return f"<Run {repr(self.start)}>"
        else:
            return f"<Run {repr(self.start)}+{repr(self.end)}>"

    def __bool__(self) -> bool:
        if any((bool(i) for i in self.elements)):
            return True
        start = self.start
        end = self.end
        if start is None:
            start = ''
        if end is None:
            end = ''
        return bool(
            (start+end)
            .replace('\n', '')
            .replace(' ', '')
        )

    def __hash__(self) -> int:
        start = self.start if self.start else ''
        end = self.end if self.end else ''
        return hash(start + end + ''.join((
            str(hash(i)) for i in self.elements
        )))

    def add_to_paragraph(self, p, context):
        runs = []
        if not self:
            return runs
        with (
            ContextVariable(context, 'strip', self.strip, apply=self.strip)
        ):
            with (
                ContextVariable(
                    context, 'bold', self.bold, apply=self.bold
                ),
                ContextVariable(
                    context, 'italic', self.italic, apply=self.italic
                ),
                ContextVariable(
                    context, 'strike', self.strike, apply=self.strike
                ),
                ContextVariable(
                    context, 'href', self.href, apply=self.href is not None
                ),
            ):
                run = add_run(self.start, p, context)
                if run is not None:
                    runs.append(run)
                for sub_run in self.elements:
                    sub_run.add_to_paragraph(p, context)
            if self.end == '\n' and context.get('no_new_line', True):
                pass
            else:
                run = add_run(self.end, p, context)
                if run is not None:
                    runs.append(run)
            return runs

    def get_text(self):
        assert self.start is not None, self
        return self.start

    def set_text(self, text):
        self.start = text

    def as_dict(self):
        output: dict = {
            'start': self.start,
            'end': self.end
        }
        if self.bold:
            output['bold'] = 'True'
        if self.italic:
            output['italic'] = 'True'
        if self.strike:
            output['strike'] = 'True'
        if self.strip:
            output['strip'] = 'True'
        if self.elements:
            output['elements'] = [i.as_dict() for i in self.elements]
        return output

    def walk(self):
        yield (self,)
        for element in self.elements:
            for sub_elements in element.walk():
                yield (self, *sub_elements)
