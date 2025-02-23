from typing import Generator
from pathlib import Path
from importlib import import_module
from logging import warning

from . import _mixins as macros_mixins


def iter_macroses() -> Generator[tuple[
    str, type[macros_mixins.MacrosBase]
], None, None]:
    p = Path(__file__).parent
    name = None
    key = None
    for key in p.iterdir():
        if not key.name.endswith('.py'): continue
        if key.name.startswith('_'): continue
        name = key.name[:-3]
        module = import_module(f".{name}", __package__)
        if not hasattr(module, 'Macros'):
            warning(f'Macros {name} file has no "Macros" class')
            continue
        macros_cl = module.Macros
        if not issubclass(macros_cl, macros_mixins.MacrosBase):
            warning(
                f'Macros {name} class "Macros" is not'
                f' derived from {macros_mixins.MacrosBase}'
            )
            continue
        yield macros_cl.get_name(), macros_cl
    del name
    del p
    del key
