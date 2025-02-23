from ..mixins import AddableToDocument


class FormulaDescribe(AddableToDocument):
    __slots__ = ('lines',)

    def __init__(self, lines: list[str]) -> None:
        super().__init__()
        self.lines = lines

    def add_to_document(self, d, context):
        end = ',' if len(self.lines) > 1 else ''
        d.add_paragraph(f"где\t{self.lines[0]}{end}")

        for line in self.lines[1:-1]:
            d.add_paragraph(f"\t{line},")

        end = '' if self.lines[-1].endswith('.') else '.'
        d.add_paragraph(f"\t{self.lines[-1]}{end}")

    def as_dict(self) -> dict | list:
        return {
            'lines': self.lines
        }
