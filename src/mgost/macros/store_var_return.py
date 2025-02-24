from ._mixins import Instant


class Macros(Instant):
    """Saves variable in context and instantly places it"""
    __slots__ = ()

    def process_instant(self, context):
        assert len(self.macros.args) == 1
        v = self.parse_markdown(
            self.macros.value, context
        )
        context.variables[self.macros.args[0]] = v
        return v
