[![PyPI](https://img.shields.io/pypi/v/mgost.svg?logo=python&logoColor=white)](https://pypi.org/project/mgost/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mgost.svg?logo=python&logoColor=white)](https://pypi.org/project/mgost/)
[![Flake8](https://github.com/ArtichaTM/MarkdownGost/actions/workflows/flake8.yml/badge.svg)](https://github.com/ArtichaTM/MarkdownGost/actions/workflows/flake8.yml)
[![WakaTime](https://wakatime.com/badge/github/ArtichaTM/MarkdownGost.svg)](https://wakatime.com/badge/github/ArtichaTM/MarkdownGost)

# MGost
> Конвертер markdown в документу docx установленного образца

## Сокращения
- Медиа - рисунок, таблица или формула в документе *docx*

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

## Примечания
- Все названия медиа хранятся в одном пространстве имён, поэтому нельзя использовать одинаковые заголовки для любого медиа. Это сделано с целью упрощения использования макроса *[mention](#mention)*.

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

## *Макросы*
В качестве расширения функционала конвертера библиотекой предусмотрены разные макросы, расширяющие функционал markdown от создания переменных до выполнения кода python. Список текущих макросов представлен ниже

### *color*
Позволяет поменять цвет текста. Цвет задаётся в формате rgb: ``` `color(255,0,0): Красный текст` ```, ``` `color(0,255,0): Зелёный текст` ```

### *comment*
Комментарии которые никак не влияют не рендер документа: ``` `comment: Надо будет булочки украсть` ```

### *count_images*
### *count_tables*
### *count_formulas*
Выводит количество всех рисунков/таблиц/формул:
```markdown
Документ включает в себя `count_images` рисунков и `count_tables` таблицы.
```

### *formula*
### *formula_describe*
`formula` позволяет генерировать формулы из latex. После этого макроса можно вызывать `formula_describe` для описания переменных формул
```md
`formula(число ошибок): N=n\frac{S}{v}`

`formula_describe(n — найденные собственные ошибки, S — всего внесённых ошибок, v — найденные внесённые ошибки)`

`formula(*число ошибок2): N=2\frac{10}{6}=3,(6)`

`formula(число необнаруженных ошибок): (N-n)=3,6-2=1,6`

`formula(формула соотношения): p=\frac{1,6}{1,6+K+1}=\frac{5}{5+0+1}=0,615`
```

### *highlight_color*
Позволяет поменять цвет фона текста. В качестве аргумента можно использовать *_только_* константу из python-docx [WD_COLOR_INDEX](https://python-docx.readthedocs.io/en/latest/api/enum/WdColorIndex.html). ``` `highlight_color(YELLOW): Что-то тут не понравилось. а где задача? Где?` ```

### *mention*
Позволяет упомянуть рисунок, таблицу или формулу по её названию. Так как данный макрос срабатывает после генерации всего документа, в него нельзя вставить какие-либо макросы, но он позволяет упомянуть любой рисунок/таблицу/формулу, независимо от позиции
```md
Упоминание до: `mention: Главный поток данных`

Неполное упоминание до: `mention: Главный поток`

![Главный поток данных](./DFD_Data.png)

Упоминание после: `mention: Главный поток данных`

Неполное упоминание после: `mention: Главный поток`
```

### *print_plain_text*
Позволяет выполнить код python, а вывод stdout записать вместо макроса в конечном документе `print_plain_text: data_struct_count.py`. ВНИМАНИЕ. Данная функция выполняет код python, поэтому в некоторых случаях необходимо ограничить обычных пользователей от этой функции. Выполняется асинхронно (выполняется во время создания docx документа, а результат получается в момент сохранения docx документа).

> Структура файлов в примере
```
├── main.md
├── counter.py
```

> counter.py
```python
for i in range(0,21):
    print(i, end=',')
```

> main.md
```md
Считаем от 0 до 20: `print_plain_text: counter.py` круто!
```

> Выполняем рендер
```bash
$ mgost main.md out.docx
```

Результат в документе docx (Файл `out.docx` в той же директории):
`Считаем от 0 до 20: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20, круто!`

![ResultInDocx](./static/print_plain_text_example.png)

### *set_list_digit*
### *set_list_marker*
Данные два макроса позволяет менять формат нумерованных и маркированных списков в рендере. MGost не использует встроенные в Docx списки, так как существует некоторые проблемы python-docx в их нумерации, поэтому MGost отсчитывает отступы в автоматическом режиме для следования ГОСТу. У обоих функций следующие аргументы:
1. Символ до текста
2. Окончание текста (но не последнего в списке!)
3. Окончание текста последнего в списке

![Пример маркированного списка с указанием аргументов](./static/set_list_marked.png)

В отличие от `set_list_marker`, `set_list_digit` в первому аргументе можно использовать аргумент *counter* в фигурных скобках 

> Пример использования макросов
```md
`set_list_marker(—,;,.)`
`set_list_digit({counter}. ,.,;)`
```

### *store_var*
### *store_var_return*
### *var*
Три данных макроса позволяют создавать и использовать переменные в документе Word. Если у вас какое-то предложение повторяется, его можно сохранить в переменную при первом использовании и повторять в документе далее. В данном случае изменение переменной в одном месте изменит её все использования.

> store_var_return
```md
### **Аннотация
В исследовательском разделе `store_var_return(исследовательский_старт): анализируется предметная область, существующие решения, устанавливаются цели, задачи и техническое задание.`

...

# Исследовательский раздел
В данном разделе `var(исследовательский_старт)`
```

> store_var
```md
### **Аннотация
`store_var(исследовательский_старт): анализируется предметная область, существующие решения, устанавливаются цели, задачи и техническое задание.`
В исследовательском разделе `var(исследовательский_старт)`

...

# Исследовательский раздел
В данном разделе `var(исследовательский_старт)`
```

### *table_name*
Макрос используется перед заданием какой-либо таблицы средствами markdown для её наименования

```md
`table_name: Типы данных динамического объекта`

|        Поле       |   Тип   |
|-------------------|---------|
| Позиция           | вектор  |
| Скорость          | вектор  |
| Поворот           | ротатор |
| Скорость поворота | Вектор  |
```

В случае, если рендер встречает таблицу, но не знает её названия, будет вызвано исключение и рендер остановлен

### *TODO*
Макрос-помощник. При встрече рендера с данным макросом MGost удаляет его из документа, но выводит об этом уведомление в stdout. ``` `TODO: доделать макияж` ```

## Кэширование
В библиотеке предусмотрено кэширование запросов, запрашиваемых с сайтов через макросы или для генерации умного списка источников. По умолчанию функционал включен для cli и выключен для python api. Для его использования требуется создать класс Settings:
> Без кэширования
```python
from mgost import convert

convert(Path('main.md'), Path('output.docx'))
```

> С кэшированием
```python
from mgost import convert, Settings

with Settings(Path('temp')): # В папке temp создаётся pickle файл internet_cache.pkl
    convert(Path('main.md'), Path('output.docx'))
```

> Используя [TemporaryDirectory](https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory)
```python
from tempfile import TemporaryDirectory
from mgost import convert, Settings

with TemporaryDirectory() as tmpdir:
    with Settings(Path(tmpdir)):
        convert(Path('main.md'), Path('output.docx'))
```

Примечание: временная папка и файл *internet_cache.pkl* создаётся в независимости от того, был ли запросы в интернет или нет

## Использование
Использовать в настоящем времени можно на сайте [articha.ru](https://articha.ru/mgost) (требуется регистрация)
