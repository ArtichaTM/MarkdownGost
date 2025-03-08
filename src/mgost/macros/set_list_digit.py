from ._mixins import DuringDocxCreation
from mgost.context import ListMarkerInfo


class Macros(DuringDocxCreation):
    """Changes digit list format"""
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        args = self.macros.args
        if len(args) != 3:
            raise RuntimeError(
                f"Error during evaluation {self.get_name()} macros. "
                "This macros requires this arguments: ("
                "new_digit, new_endline, new_endline_end). "
                f"Example: `{self.get_name()}(•,;,.)`"
            )
        context.list_digit_info = ListMarkerInfo(*args)
        return []
