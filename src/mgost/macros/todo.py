from . import logger
from ._flags import MacrosFlags
from ._mixins import Instant


class Macros(Instant):
    """During docx render prints macros content to stdout"""
    __slots__ = ()

    def process_instant(self, context):
        if self.macros.value:
            value = self.macros.value
        else:
            value = ''
        logger.info(f"TODO: {value}")
        return []

    @staticmethod
    def flags():
        return MacrosFlags.NONE
