from ._flags import MacrosFlags
from ._mixins import Instant


class Macros(Instant):
    """Noop macros allowing comments"""
    __slots__ = ()

    def process_instant(self, context):
        return []

    @staticmethod
    def flags():
        return MacrosFlags.NONE
