from logging import warning
from pathlib import Path

from ._base import SourceConverter


def build_converters() -> dict[str, SourceConverter]:
    output: dict[str, SourceConverter] = dict()
    for file in Path(__file__).parent.iterdir():
        if not file.name.endswith('.py'):
            continue
        if file.name.startswith('_'):
            continue
        values = globals()
        try:
            exec(f"from .{file.name.split('.')[0]} import Converter", values)
        except Exception as e:
            warning(
                f"Can't import {file.name} because of "
                f"{type(e).__qualname__}{e.args}",
                exc_info=e
            )
            continue
        assert 'Converter' in values
        assert values['Converter'] != SourceConverter
        assert issubclass(values['Converter'], SourceConverter)
        converter = values['Converter']()
        assert isinstance(converter, SourceConverter)
        output[converter.get_parsing_domain()] = converter
    return output
