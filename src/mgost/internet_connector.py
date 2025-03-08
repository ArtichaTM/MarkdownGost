import pickle
from logging import warning
from pathlib import Path
from time import time
from typing import Literal

import requests

from .context import Context


class RequestResultInfo:
    __slots__ = (
        '_result', 'url', 'method', 'context',
        'expire_time', 'creation_time'
    )
    url: str
    method: Literal['GET'] | Literal['HEAD']
    _result: requests.Response | None
    expire_time: float
    creation_time: float

    def __init__(
        self,
        url: str,
        method: Literal['GET'] | Literal['HEAD'],
        context: Context,
        expire_time: float = -1.0,
        creation_time: float | None = None,
    ) -> None:
        assert isinstance(url, str)
        assert isinstance(method, str)
        assert isinstance(context, Context)
        assert isinstance(expire_time, float)
        assert creation_time is None or isinstance(creation_time, float)
        if creation_time is None:
            self.creation_time = 0.0
        self.url = url
        self.method = method
        self.context = context
        self.expire_time = expire_time
        assert not hasattr(self, '_result')
        self._result = None

    def __repr__(self) -> str:
        return (
            f"<{type(self).__qualname__} "
            f"url={self.url}, "
            f"method={self.method}, "
            f"expire_time={self.expire_time}, "
            f"creation_time={self.creation_time}, "
            f"content={self._result}>"
        )

    def __getstate__(self) -> tuple[
        str, str,
        requests.Response | requests.exceptions.RequestException | None,
        float, float
    ]:
        return (
            self.url, self.method, self._result,
            self.expire_time, self.creation_time
        )

    def __setstate__(self, state: tuple[str, str, float, float]) -> None:
        assert len(state) == 5
        url, method, result, expire_time, creation_time = state
        assert isinstance(url, str), url
        assert result is None or isinstance(result, requests.Response), result
        assert isinstance(expire_time, float), expire_time
        assert isinstance(creation_time, float), creation_time
        self.url = url
        self.method = method
        self._result = result
        self.expire_time = expire_time
        self.creation_time = creation_time

    def _get(self) -> requests.Response:
        return requests.request(
            self.method,
            self.url,
            timeout=1.,
            headers={
                'User-Agent': self.context.user_agent
            }
        )

    def get_result(
        self
    ) -> requests.Response | None:
        """
        :raises TimeoutError:
        :raises requests.exceptions.RequestException:
        """
        if self.expired() or self._result is None:
            self._result = self._get()
            self.creation_time = time()
        return self._result

    def expired(self) -> bool:
        if self.expire_time < 0:
            return False
        current_time = time()
        return (current_time - self.creation_time) > self.expire_time


class InternetConnection:
    __slots__ = ('_cache', 'path_file', 'agent', 'context')
    _FILE_NAME: str = 'internet_cache.pkl'
    cache_folder_path: Path | None
    _cache: dict[str, RequestResultInfo]
    agent: str

    def __init__(
        self,
        cache_folder: Path | None,
        context: Context
    ) -> None:
        assert cache_folder is None or isinstance(cache_folder, Path)
        assert isinstance(context, Context)
        self.context = context
        self._cache = dict()

        if cache_folder is None:
            self.path_file = None
            return
        assert cache_folder.is_dir()
        self.path_file = cache_folder / self._FILE_NAME

        if not self.path_file.exists():
            return
        with self.path_file.open('rb') as file:
            try:
                self._cache = pickle.load(file)
            except Exception as e:
                warning("Error during pickle.load", exc_info=e)

    def __call__(
        self,
        url: str,
        url_expire: float = -1.0,
        method: Literal['GET'] | Literal['HEAD'] = 'GET'
    ) -> requests.Response | None:
        assert isinstance(url, str)
        assert isinstance(url_expire, float)
        assert '://' in url, url
        info = self._cache.get(url, None)
        if info is None:
            info = RequestResultInfo(
                url, method, self.context, url_expire
            )
            self._cache[url] = info

        try:
            return info.get_result()
        except requests.exceptions.RequestException:
            return None

    def __getstate__(self):
        raise NotImplementedError()

    def __setstate__(self, *_) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        if self.path_file is None:
            return
        assert not self.path_file.is_dir()
        with open(self.path_file, mode='wb') as file:
            pickle.dump(self._cache, file)
