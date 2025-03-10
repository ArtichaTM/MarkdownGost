from . import logger
from ._flags import MacrosFlags
from ._mixins import DuringDocxCreation
from mgost.context import ListMarkerInfo


class Macros(DuringDocxCreation):
    """Changes marker list format"""
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        args = self.macros.args
        if len(args) != 3:
            logger.info(
                f"Error during evaluation {self.get_name()} macros. "
                "This macros requires this arguments: ("
                "new_digit, new_endline, new_endline_end). "
                f"Example: `{self.get_name()}(•,;,.)`"
            )
            return []
        context.list_marker_info = ListMarkerInfo(*args)
        return []

    @staticmethod
    def flags():
        return MacrosFlags.SETTINGS_CHANGE
