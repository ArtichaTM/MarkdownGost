from ._mixins import Instant


class Macros(Instant):
    __slots__ = ()

    def process_instant(self, context):
        if self.macros.value:
            value = f": {self.macros.value}"
        else:
            value = ''
        print(f"TODO in file {context.current_file_path}: {value}")
        return []
