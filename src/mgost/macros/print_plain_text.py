from multiprocessing import Process, Queue
from pathlib import Path
from io import StringIO

from mgost.settings import Settings
from ._mixins import DuringDocxCreation, AfterDocxCreation


def exec_code(file_path: Path, q: Queue):
    code = file_path.read_text(encoding='utf-8')
    import sys
    sys.stdout = StringIO()
    exec(code)
    q.put(sys.stdout.getvalue())


class Macros(DuringDocxCreation, AfterDocxCreation):
    """Prints simple python code from stdout into document"""
    __slots__ = ('process', 'q', 'run')
    process: Process
    q: Queue

    def process_during_docx_creation(self, p, context):
        file_name = self.macros.value
        current_folder = context.current_file_path.parent
        file_path = current_folder / file_name
        if not file_path.exists():
            raise RuntimeError(f"File {file_name} does not exist")

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
        try:
            self.process.join(timeout=Settings.get().code_run_timeout)
        except TimeoutError:
            print(f"Timeout for code in {self.macros.value}")
            return
        assert self.q.full(), self.q.qsize()
        received = self.q.get()
        assert isinstance(received, str)
        received = received.strip()
        assert self.macros.runs is not None
        assert len(self.macros.runs) == 1
        self.macros.runs[0].text = received
