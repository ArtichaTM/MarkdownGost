from . import logger
from ._flags import MacrosFlags
from ._mixins import Instant


class Macros(Instant):
    """Saves variable in context and removed macros run"""
    __slots__ = ()

    def process_instant(self, context):
        if len(self.macros.args) != 1:
            logger.info(
                f'Macros "{self.get_name()}":'
                ' first argument is mandatory'
            )
            return []
        context.variables[self.macros.args[0]] = self.parse_markdown(
            self.macros.value, context
        )
        return []

    @staticmethod
    def flags():
        return MacrosFlags.ADD_VARIABLES
