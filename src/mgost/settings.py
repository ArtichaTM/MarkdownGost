from typing import TYPE_CHECKING, Callable
from pathlib import Path

from lxml import etree

if TYPE_CHECKING:
    from mgost.macros import macros_mixins
    from mgost.source_converters import SourceConverter
    from mgost.internet_connector import InternetConnection
    from mgost.context import Context


__all__ = ('get_settings', 'init_settings')


class Paths:
    __slots__ = (
        'module_root',
        'base_docx',
        'mml2omml',
    )

    def __init__(
        self,
        module_root: Path
    ) -> None:
        self.module_root = module_root
        self.base_docx = self.module_root / '_base.docx'
        self.mml2omml = self.module_root / 'MML2OMML.xsl'


class _Settings:
    __slots__ = (
        # Code classes, functions, e.t.c.
        # that imported dynamically
        'macroses', 'source_converters',
        'post_processors',

        'internet_connection', 'user_agent',
        'paths', 'mml2omml_xslt',
    )
    _instance: '_Settings | None' = None

    macroses: dict[str, type['macros_mixins.MacrosBase']]
    source_converters: dict[str, 'SourceConverter']
    post_processors: dict[str, Callable[['Context'], None]]

    internet_connection: 'InternetConnection'
    user_agent: str
    paths: Paths

    def __init__(
        self,
        temp_folder: Path
    ) -> None:
        assert isinstance(temp_folder, Path)
        temp_folder.mkdir(exist_ok=True)

        assert type(self)._instance is None
        type(self)._instance = self

        from mgost.macros import iter_macroses
        from mgost.source_converters import build_converters
        from mgost.internet_connector import InternetConnection
        from mgost.post_processors import build_callables

        self.internet_connection = InternetConnection(temp_folder)
        self.macroses = {name: cl for name, cl in iter_macroses()}
        self.source_converters = build_converters()
        self.post_processors = build_callables()
        self.user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/88.0.4324.150 Safari/537.36 '
            'RuxitSynthetic/1.0 v6278345041414680700 '
            't4399065582540647721 ath1fb31b7a '
            'altpriv cvcv=2 smf=0'
        )
        self.paths = Paths(Path(__file__).parent)

        tree = etree.parse(
            self.paths.mml2omml
        )  # type: ignore
        self.mml2omml_xslt = etree.XSLT(tree)

    def __enter__(self) -> '_Settings':
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        assert type(self)._instance is not None
        type(self)._instance = None
        self.internet_connection.close()


def get_settings() -> _Settings:
    s = _Settings._instance
    assert s is not None
    return s


def init_settings(temp_folder: Path) -> _Settings:
    assert isinstance(temp_folder, Path)
    assert _Settings._instance is None
    return _Settings(
        temp_folder=temp_folder
    )
