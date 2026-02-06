"""Tests for domain enums."""

import pytest

from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide


class TestOptionType:
    def test_members(self) -> None:
        assert OptionType.CALL == "call"
        assert OptionType.PUT == "put"

    def test_has_exactly_two_members(self) -> None:
        assert len(OptionType) == 2

    def test_string_values_are_lowercase(self) -> None:
        for member in OptionType:
            assert member.value == member.value.lower()

    def test_is_string(self) -> None:
        assert isinstance(OptionType.CALL, str)

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            OptionType("invalid")


class TestPositionSide:
    def test_members(self) -> None:
        assert PositionSide.LONG == "long"
        assert PositionSide.SHORT == "short"

    def test_has_exactly_two_members(self) -> None:
        assert len(PositionSide) == 2

    def test_string_values_are_lowercase(self) -> None:
        for member in PositionSide:
            assert member.value == member.value.lower()

    def test_is_string(self) -> None:
        assert isinstance(PositionSide.LONG, str)

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            PositionSide("invalid")


class TestExerciseStyle:
    def test_members(self) -> None:
        assert ExerciseStyle.AMERICAN == "american"
        assert ExerciseStyle.EUROPEAN == "european"

    def test_has_exactly_two_members(self) -> None:
        assert len(ExerciseStyle) == 2

    def test_string_values_are_lowercase(self) -> None:
        for member in ExerciseStyle:
            assert member.value == member.value.lower()

    def test_is_string(self) -> None:
        assert isinstance(ExerciseStyle.AMERICAN, str)

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            ExerciseStyle("invalid")
