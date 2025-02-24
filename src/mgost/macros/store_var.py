from ._exceptions import WrongArgument
from ._mixins import Instant


class Macros(Instant):
    """Saves variable in context and removed macros run"""
    __slots__ = ()

    def process_instant(self, context):
        if len(self.macros.args) != 1:
            raise WrongArgument("First argument is mandatory")
        context.variables[self.macros.args[0]] = self.parse_markdown(
            self.macros.value, context
        )
        return []
