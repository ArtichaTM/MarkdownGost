from ._mixins import Instant


class Macros(Instant):
    """Places variable from context (error if not exists)"""
    __slots__ = ()

    def process_instant(self, context):
        assert len(self.macros.args) == 1
        assert self.macros.args[0] in context.variables, self.macros.args[0]
        value = context.variables[self.macros.args[0]]
        assert isinstance(value, list)
        return value
