from dataclasses import replace
from typing import Sequence

from docx.document import Document as _Document
from docx.text.paragraph import Paragraph as _Paragraph
from docx.text.run import Run as _Run

from mgost.context import Context
from mgost.macros import get_macroses, macros_mixins
from mgost.types.mixins import AddableToDocument, AddableToParagraph
from mgost.types.run import Run


class Macros(Run):
    __slots__ = (
        'cl',
        'command', 'value', 'args',
        'paragraph', 'runs',
        'counters',
    )
    cl: macros_mixins.MacrosBase | None
    command: str
    value: str
    args: list[str]
    paragraph: _Paragraph | None
    runs: list[_Run] | None

    def __init__(self, code: str, tail: str | None):
        super().__init__(code, tail)
        self.paragraph = None
        self.runs = None

        command_index = code.find(': ')
        if command_index == -1:
            command, value = code, ''
        else:
            command = code[:command_index]
            value = code[command_index+2:]

        square_opening = code.find('(')
        if square_opening == -1:
            command = command
            args = []
        else:
            command = command.strip()
            args = command[square_opening+1:-1]
            command = command[:square_opening]
            if args:
                args = args.split(',')
            else:
                args = []

        self.command = command
        self.value = value
        self.args = args
        cl = get_macroses().get(self.command, None)
        if cl is None:
            self.cl = None
        else:
            self.cl = cl(self)

    def replace[T: Macros](
        self: T, context: Context
    ) -> Sequence[AddableToParagraph | T] | AddableToDocument:
        if self.cl is None:
            return [self]
        elif isinstance(self.cl, macros_mixins.Instant):
            return self.cl.process_instant(context)
        return [self]

    def add_to_paragraph(self, p: _Paragraph, context: Context) -> list[_Run]:
        self.paragraph = p
        runs = []
        if self.cl is None:
            runs = [p.add_run(
                f'- - ERROR: No function called "{self.command}" - -'
            )]
        else:
            if isinstance(self.cl, macros_mixins.AfterDocxCreation):
                context.post_docx_macroses.append(self.cl)
            if isinstance(self.cl, macros_mixins.DuringDocxCreation):
                runs = self.cl.process_during_docx_creation(p, context)
        self.runs = runs
        self.counters = replace(context.counters)
        context.counters.copy_to(self.counters)
        self.start = None
        super().add_to_paragraph(p, context)
        return runs

    def add_to_document(self, d: _Document, context: Context) -> None:
        raise NotImplementedError()

    def as_dict(self):
        return {
            'command': self.command,
            'value': self.value,
            'args': self.args,
            'processor': self.cl
        }

    def walk(self):
        yield (self,)
