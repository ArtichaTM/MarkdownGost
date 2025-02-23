from mgost.context import ListMarkerInfo
from ._mixins import DuringDocxCreation


class Macros(DuringDocxCreation):
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        args = self.macros.args
        if len(args) != 3:
            raise RuntimeError(
                f"Error during evaluation {self.name} macros. "
                "This macros requires this arguments: ("
                "new_digit, new_endline, new_endline_end). "
                f"Example: `{self.name}(•,;,.)`"
            )
        context.list_marker_info = ListMarkerInfo(*args)
        return []
