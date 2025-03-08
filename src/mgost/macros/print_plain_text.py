from io import StringIO
from logging import warning
from multiprocessing import Process, Queue
from pathlib import Path

from ._mixins import AfterDocxCreation, DuringDocxCreation


def exec_code(file_path: Path, q: Queue):
    code = file_path.read_text(encoding='utf-8')
    import sys
    sys.stdout = StringIO()
    try:
        exec(code)
    except BaseException as e:
        text = (
            f"<Exception in {file_path.name}: "
            f"{type(e).__qualname__}({e}).>"
        )
        warning(text[1:-1])
    else:
        text = sys.stdout.getvalue()

    q.put(text)


class Macros(DuringDocxCreation, AfterDocxCreation):
    """Prints simple python code from stdout into document"""
    __slots__ = ('process', 'q', 'run')
    process: Process | None
    q: Queue

    def process_during_docx_creation(self, p, context):
        self.process = None
        file_name = self.macros.value
        current_folder = context.source.parent
        file_path = current_folder / file_name
        if not file_path.exists():
            text = f"<File {file_name} does not exist>"
            warning(text[1:-1])
            return [p.add_run(text)]

        self.q = Queue(maxsize=1)
        self.process = Process(
            target=exec_code,
            args=(
                file_path, self.q
            ),
            name=f"<{self.get_name()}: {self.macros.value}>",
            daemon=True
        )
        self.process.start()
        return [p.add_run(f'<CodeMacros {file_name}>')]

    def process_after_docx_creation(
        self, context
    ) -> None:
        assert self.macros.runs is not None
        assert len(self.macros.runs) == 1
        if self.process is None:
            return
        try:
            self.process.join(timeout=context.code_run_timeout)
        except TimeoutError:
            text = f"<Timeout for code in {self.macros.value}>"
            warning(text[1:-1])
            self.macros.runs[0].text = text
        assert self.q.full(), self.q.qsize()
        received = self.q.get()
        assert isinstance(received, str)
        received = received.strip()
        self.macros.runs[0].text = received
