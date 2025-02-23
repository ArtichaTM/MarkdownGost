from ._mixins import Instant
from mgost.types.complex.formula_describe import FormulaDescribe


class Macros(Instant):
    __slots__ = ()

    def process_instant(self, context):
        return FormulaDescribe([
            i.strip() for i in self.macros.args
        ])
