from . import logger
from ._flags import MacrosFlags
from ._mixins import AfterDocxCreation, DuringDocxCreation


class Macros(DuringDocxCreation, AfterDocxCreation):
    """Places counter and media name in place of macros"""
    __slots__ = ()

    def process_during_docx_creation(self, p, context):
        return [p.add_run()]

    def process_after_docx_creation(self, context):
        from mgost.types.media import BaseMedia
        assert isinstance(self.macros.runs, list)
        assert len(self.macros.runs) == 1, [i.text for i in self.macros.runs]
        ctx_var = self.macros.value
        if ctx_var not in context:
            for key in context:
                assert isinstance(key, str)
                if key.startswith(ctx_var):
                    ctx_var = key
                    break
        if ctx_var not in context:
            error = f"Переменная {ctx_var} не существует"
            logger.info(error)
            self.macros.runs[0].text = error
            return
        value = context[ctx_var]
        if not isinstance(value, BaseMedia):
            error = f"Не могу упомянуть {type(value).__qualname__}"
            logger.info(error)
            self.macros.runs[0].text = error
        assert isinstance(value, BaseMedia)
        counters = self.macros.counters

        only_number = False
        if 'only_number' in self.macros.args:
            only_number = True

        self.macros.runs[0].text = value.mention(
            counters.headings,
            value.counter(counters),
            only_number=only_number
        )

    @staticmethod
    def flags():
        return MacrosFlags.READ_VARIABLES
