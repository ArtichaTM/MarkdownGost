from ._mixins import AfterDocxCreation, DuringDocxCreation


class Macros(DuringDocxCreation, AfterDocxCreation):
    """Returns amount of all formulas in document"""
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        return [p.add_run()]

    def process_after_docx_creation(self, context):
        assert self.macros.runs is not None
        count = sum((i for i in context.counters.formula.values()))
        self.macros.runs[0].text = f"{count}"
