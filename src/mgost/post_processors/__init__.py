from logging import warning
from pathlib import Path
from typing import Callable

from mgost.context import Context

__callables: dict[str, Callable[[Context], None]] | None = None


def get_post_processors() -> dict[str, Callable[[Context], None]]:
    global __callables
    if __callables is not None:
        return __callables
    output: dict[str, Callable[[Context], None]] = dict()
    for folder in Path(__file__).parent.iterdir():
        if not folder.is_dir():
            continue
        if not folder.joinpath('__init__.py').exists():
            continue
        values = globals()
        try:
            exec(f"from .{folder.name} import post_process", values)
        except Exception as e:
            warning(
                f"Can't import {folder.name} because of "
                f"{type(e).__qualname__}{e.args}",
                exc_info=e
            )
            continue
        assert 'post_process' in values
        output[folder.name] = values['post_process']
    __callables = output
    return output
