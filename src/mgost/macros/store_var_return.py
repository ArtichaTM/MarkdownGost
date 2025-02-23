from ._mixins import Instant


class Macros(Instant):
    __slots__ = ()

    def process_instant(self, context):
        assert len(self.macros.args) == 1
        v = self.parse_markdown(
            self.macros.value, context
        )
        context.variables[self.macros.args[0]] = v
        return v
