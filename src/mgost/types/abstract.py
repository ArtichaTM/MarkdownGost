from abc import ABC, abstractmethod
from typing import Any, Generator

__all__ = ('AbstractElement', )


class DynamicAttributes(object):
    def __init__(self) -> None:
        self.__dict__['__call__args__'] = []

    def __getattr__(self, name):
        setattr(self, name, DynamicAttributes())
        return getattr(self, name)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.__dict__['__call__args__'].append((args, kwargs))

    def to_dict(self) -> dict:
        output = dict()
        for key, value in self.__dict__.items():
            if key.startswith('__'):
                continue
            if isinstance(value, DynamicAttributes):
                output[key] = value.to_dict()
            else:
                output[key] = value
        if self.__dict__['__call__args__']:
            output['__call__'] = self.__dict__['__call__args__']
        return output


class AbstractElement(ABC):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__}>"

    @abstractmethod
    def as_dict(self) -> dict | list:
        ...

    def walk(self) -> Generator[tuple['AbstractElement', ...], None, None]:
        yield (self,)
