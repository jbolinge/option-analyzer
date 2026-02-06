"""Core domain enums."""

from enum import StrEnum


class OptionType(StrEnum):
    CALL = "call"
    PUT = "put"


class PositionSide(StrEnum):
    LONG = "long"
    SHORT = "short"


class ExerciseStyle(StrEnum):
    AMERICAN = "american"
    EUROPEAN = "european"
