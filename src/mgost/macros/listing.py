from pathlib import Path

from . import logger
from ._flags import MacrosFlags
from ._mixins import Instant
from mgost.types.media import Listing
from mgost.types.run import Run


class Macros(Instant):
    """Places listing in appendix"""
    __slots__ = ()
    # TODO: implement convert from `.ipynb` to `.py`
    # jupyter nbconvert mynotebook.ipynb --to python

    def process_instant(self, context):
        if len(self.macros.args) != 1:
            logger.info(
                f'Макрос "{self.get_name()}": первый'
                ' аргумент обязательный'
            )
            return [Run("<Ошибка аргументов>")]
        path = self.check_file(self.macros.value[:30], context)
        if isinstance(path, list):
            return path
        assert isinstance(path, Path)
        return Listing(
            self.macros.args[0],
            path.read_text(encoding='utf-8').strip()
        )

    @staticmethod
    def flags():
        return MacrosFlags.ADD_VARIABLES | MacrosFlags.FILE_READING
