from ._mixins import Instant
from mgost.types.media import Formula
from mgost.types.simple import Run


class Macros(Instant):
    """Places formula in-place of macros"""
    __slots__ = ()

    def process_instant(self, context):
        if len(self.macros.args) != 1:
            return [Run(
                f"- {self.get_name()} requires name"
                " formula as first argument -",
                bold=True
            )]
        return Formula(self.macros.args[0], self.macros.value)
