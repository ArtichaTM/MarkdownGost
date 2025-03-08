from ._mixins import Instant


class Macros(Instant):
    """During docx render prints macros content to stdout"""
    __slots__ = ()

    def process_instant(self, context):
        if self.macros.value:
            value = f": {self.macros.value}"
        else:
            value = ''
        print(f"TODO in file {context.source}: {value}")
        return []
