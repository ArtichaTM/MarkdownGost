from enum import IntFlag, auto, unique


@unique
class MacrosFlags(IntFlag):
    NONE = auto()

    "Adds context variables"
    ADD_VARIABLES = auto()
    "Reads context variables"
    READ_VARIABLES = auto()
    "Edits (changes name/pointer/....) context variables"
    EDIT_VARIABLES = auto()

    "Reads file"
    FILE_READING = auto()

    "Runs user python code"
    "Usually include FILE_READING"
    PYTHON_EXECUTION = auto()

    "Changes context settings. For example, "
    "edits marked list bullet, text ending, e.t.c."
    SETTINGS_CHANGE = auto()

    "Mixed variables"
    DEFAULT = (
        NONE |
        ADD_VARIABLES |
        READ_VARIABLES |
        EDIT_VARIABLES
    )
    ALL = (
        DEFAULT |
        PYTHON_EXECUTION |
        FILE_READING |
        SETTINGS_CHANGE
    )
