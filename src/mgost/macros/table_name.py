from ._mixins import DuringDocxCreation


class Macros(DuringDocxCreation):
    """Names previous table"""
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        if context.table_name is not None:
            raise RuntimeError(
                "Table name is already set. Old "
                f"table name: {context.table_name}"
            )
        context.table_name = self.macros.value
        return []
