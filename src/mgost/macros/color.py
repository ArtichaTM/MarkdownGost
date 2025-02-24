from docx.shared import RGBColor

from ._mixins import DuringDocxCreation


class Macros(DuringDocxCreation):
    """
    Changes run color
    """
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        assert len(self.macros.args) == 3
        r, g, b = map(int, self.macros.args)
        run = p.add_run(self.macros.value)
        run.font.color.rgb = RGBColor(r, g, b)
        return [run]
