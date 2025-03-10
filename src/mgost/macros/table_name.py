from . import logger
from ._flags import MacrosFlags
from ._mixins import DuringDocxCreation


class Macros(DuringDocxCreation):
    """Names previous table"""
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        if context.table_name is not None:
            logger.info(
                "Название таблицы уже установленно. Старое"
                f" название: {context.table_name}"
            )
        else:
            context.table_name = self.macros.value
        return []

    @staticmethod
    def flags():
        return MacrosFlags.SETTINGS_CHANGE
