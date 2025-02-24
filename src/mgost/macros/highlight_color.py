from docx.enum.text import WD_COLOR_INDEX

from ._exceptions import WrongArgument
from ._mixins import DuringDocxCreation


class Macros(DuringDocxCreation):
    """Changes background color of run. Use WD_COLOR_INDEX names"""
    __slots__ = ()

    def __init__(self, macros) -> None:
        super().__init__(macros)
        self.macros = macros

    def process_during_docx_creation(self, p, context):
        if len(self.macros.args) != 1:
            raise WrongArgument("One argument is mandatory")
        if self.macros.args[0] not in {i.name for i in WD_COLOR_INDEX}:
            raise WrongArgument(
                f"First argument is not in set {''}"
                f"{{i.name for i in WD_COLOR_INDEX}}"
            )
        run = p.add_run(self.macros.value)
        run.font.highlight_color = getattr(WD_COLOR_INDEX, self.macros.args[0])

        return [run]
