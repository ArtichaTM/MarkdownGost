from ._mixins import Instant


class Macros(Instant):
    __slots__ = ()

    def process_instant(self, context):
        return []
