from pathlib import Path
from typing import TYPE_CHECKING

from lxml import etree

if TYPE_CHECKING:
    from mgost.internet_connector import InternetConnection


__all__ = (
    'Settings',
)


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


class Settings:
    __slots__ = (
        # Code classes, functions, e.t.c.
        # that imported dynamically

        'internet_connection', 'user_agent',
        'paths', 'mml2omml_xslt',

        'code_run_timeout',
    )
    _instance: 'Settings | None' = None

    internet_connection: 'InternetConnection'
    user_agent: str
    paths: Paths
    code_run_timeout: int

    def __init__(
        self,
        temp_folder: Path | None
    ) -> None:
        assert type(self)._instance is None, \
            'There are 2 settings instances'
        type(self)._instance = self

        assert any((
            temp_folder is None,
            isinstance(temp_folder, Path)
        ))
        if isinstance(temp_folder, Path):
            temp_folder.mkdir(exist_ok=True)

        from mgost.internet_connector import InternetConnection

        self.internet_connection = InternetConnection(temp_folder)
        self.user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/88.0.4324.150 Safari/537.36 '
            'RuxitSynthetic/1.0 v6278345041414680700 '
            't4399065582540647721 ath1fb31b7a '
            'altpriv cvcv=2 smf=0'
        )
        self.paths = Paths(Path(__file__).parent)
        self.code_run_timeout = 1

        tree = etree.parse(
            self.paths.mml2omml
        )  # type: ignore
        self.mml2omml_xslt = etree.XSLT(tree)

    def __enter__(self) -> 'Settings':
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        assert type(self)._instance is not None
        type(self)._instance = None
        self.internet_connection.close()

    @classmethod
    def initialized(cls) -> bool:
        return cls._instance is not None

    @classmethod
    def get(cls) -> 'Settings':
        s = cls._instance
        assert s is not None
        return s
