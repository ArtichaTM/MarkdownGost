from typing import Callable
from logging import warning
from pathlib import Path


from mgost.context import Context


def build_callables() -> dict[str, Callable[[Context], None]]:
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
    return output
