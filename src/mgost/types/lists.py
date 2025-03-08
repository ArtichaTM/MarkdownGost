from typing import Generator

from mgost.context import Context
from mgost.types.bases import ListBase
from mgost.types.mixins import AddableToDocument


class ListBullet(ListBase):
    def __init__(self, elements: list[AddableToDocument]) -> None:
        super().__init__(elements)
        self.style_base = 'List Bullet'

    def prefixes(self, context: Context) -> Generator[str, None, None]:
        while True:
            yield f"{context.list_marker_info.mark} "


class ListNumbered(ListBase):
    def __init__(self, elements: list[AddableToDocument]) -> None:
        super().__init__(elements)
        self.style_base = 'List Number'

    def prefixes(self, context: Context) -> Generator[str, None, None]:
        counter = 1
        while True:
            yield context.list_digit_info.mark.format_map({'counter': counter})
            counter += 1
