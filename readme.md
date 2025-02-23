[![PyPI](https://img.shields.io/pypi/v/mgost.svg?logo=python&logoColor=white)](https://pypi.org/project/mgost/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mgost.svg?logo=python&logoColor=white)](https://pypi.org/project/mgost/)
[![Flake8](https://github.com/ArtichaTM/MarkdownGost/actions/workflows/flake8.yml/badge.svg)](https://github.com/ArtichaTM/MarkdownGost/actions/workflows/flake8.yml)
[![WakaTime](https://wakatime.com/badge/github/ArtichaTM/MarkdownGost.svg)](https://wakatime.com/badge/github/ArtichaTM/MarkdownGost)

# MGost
> Конвертер markdown в документу docx установленного образца

## Установка
Установка проста:
```bash
$ pip install mgost
```

## Использование
Пакет предоставляет api для взаимодействия как в CLI, так и в качестве пакета python

### Cli
MGost предоставляет простую консольную команду для конвертации файла `.md` в `.docx`:
```bash
# Конвертирует файл main.md в текущей директории в файл output.docx
$ mgost main.md output.docx
# Конвертирует файл main.md в директории input в файл output.docx директории output
$ mgost input/main.md output/output.docx
```

### Python
В качестве единственной команды библиотеки выступает функция сигнатуры `convert(source: Path, dest: Path | BytesIO) -> None`. В неё необходимо передать путь до файла markdown, а выход может быть путь (при существовании файла перезаписывает его) или BytesIO переменная.

На вход необходим именно файл так как библиотека должна подхватывать различные файлы, на которые ссылается markdown: от изображений до кода python. Внизу можно найти аналог команд приведённых для CLI выше
```python
from pathlib import Path
from mgost import convert

# Конвертирует файл main.md в текущей директории в файл output.docx
convert(Path('main.md'), Path('output.docx'))

# Конвертирует файл main.md в директории input в файл output.docx директории output
convert(Path('input/main.md'), Path('output/output.docx'))
```

Конвертация в `BytesIO`:
```python
from pathlib import Path
from mgost import convert
from io import BytesIO

output = BytesIO()

# Конвертирует файл main.md в BytesIO
convert(Path('main.md'), output)

# Сохранение байтов в файл
Path('output.docx').write_bytes(output)
```

## Использование
Использовать в настоящем времени можно на сайте [articha.ru](https://articha.ru/mgost) (требуется регистрация)
