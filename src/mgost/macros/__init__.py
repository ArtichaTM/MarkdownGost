from importlib import import_module
from logging import getLogger
from pathlib import Path

from . import _mixins as macros_mixins
from ._flags import MacrosFlags

__macroses: dict[str, type[macros_mixins.MacrosBase]] | None = None
logger = getLogger(__name__)


def get_macroses() -> dict[str, type[macros_mixins.MacrosBase]]:
    global __macroses
    if __macroses is not None:
        return __macroses
    __macroses = dict()
    p = Path(__file__).parent
    name = None
    key = None
    for key in p.iterdir():
        if not key.name.endswith('.py'): continue
        if key.name.startswith('_'): continue
        name = key.name[:-3]
        module = import_module(f".{name}", __package__)
        if not hasattr(module, 'Macros'):
            logger.warning(
                f'Macros {name} file has no "Macros" class. '
                'If this not supposed to be a macros, use underline'
                ' to exclude it from macros indexing'
            )
            continue
        macros_cl = module.Macros
        if not issubclass(macros_cl, macros_mixins.MacrosBase):
            logger.error(
                f'Macros {name} class "Macros" is not'
                f' derived from {macros_mixins.MacrosBase}'
            )
            continue
        __macroses[macros_cl.get_name()] = macros_cl
    return __macroses
