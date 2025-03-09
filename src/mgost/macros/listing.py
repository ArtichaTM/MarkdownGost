from logging import warning

from ._mixins import Instant
from mgost.types.media import Listing


class Macros(Instant):
    """Places listing"""
    __slots__ = ()

    def process_instant(self, context):
        path = context.source.parent / self.macros.value
        if not path.exists():
            warning(f"No file {path} exists")
        if not path.is_file():
            warning(f"Target {path} is not a file")
        return Listing(
            self.macros.args[0],
            path.read_text(encoding='utf-8').strip()
        )
