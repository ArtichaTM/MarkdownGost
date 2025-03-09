from ._exceptions import WrongArgument
from ._mixins import Instant
from mgost.types.media import Listing


class Macros(Instant):
    """Places listing"""
    __slots__ = ()
    # TODO: implement convert from `.ipynb` to `.py`
    # jupyter nbconvert mynotebook.ipynb --to python

    def process_instant(self, context):
        if len(self.macros.args) != 1:
            raise WrongArgument("One argument is mandatory")
        path = context.source.parent / self.macros.value
        if not path.exists():
            raise WrongArgument(f"No file {path} exists")
        if not path.is_file():
            raise WrongArgument(f"Target {path} is not a file")
        return Listing(
            self.macros.args[0],
            path.read_text(encoding='utf-8').strip()
        )
