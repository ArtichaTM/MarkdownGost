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
                f'Macros "{self.get_name()}": first '
                'argument is mandatory'
            )
            return [Run("<No first argument error>")]
        name = (
            self.macros.value[:30]
            .replace('..\\', '')
            .replace('../', '')
        )
        path = context.source.parent / name
        if not path.exists():
            logger.info(
                f'Macros "{self.get_name()}": no '
                f'file {path} exists'
            )
            return [Run("<No file error>")]
        if not path.is_file():
            logger.info(
                f'Macros "{self.get_name()}": target '
                f'{path} is not a file'
            )
            return [Run("<Target is not a file error>")]
        return Listing(
            self.macros.args[0],
            path.read_text(encoding='utf-8').strip()
        )

    @staticmethod
    def flags():
        return MacrosFlags.ADD_VARIABLES | MacrosFlags.FILE_READING
