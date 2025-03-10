from . import logger
from ._flags import MacrosFlags
from ._mixins import Instant


class Macros(Instant):
    """Saves variable in context and removed macros run"""
    __slots__ = ()

    def process_instant(self, context):
        if len(self.macros.args) != 1:
            logger.info(
                f'Макрос "{self.get_name()}":'
                ' первый аргумент обязательный'
            )
            return []
        context.variables[self.macros.args[0]] = self.parse_markdown(
            self.macros.value, context
        )
        return []

    @staticmethod
    def flags():
        return MacrosFlags.ADD_VARIABLES
