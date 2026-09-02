import pytest

from scios.cognitive_core.perception.modalities.text.cleaner import (
    TextCleaner,
)


@pytest.fixture
def cleaner() -> TextCleaner:
    return TextCleaner()


def test_cleaner_can_be_constructed() -> None:
    cleaner = TextCleaner()

    assert isinstance(cleaner, TextCleaner)


def test_clean_returns_string(cleaner: TextCleaner) -> None:
    assert isinstance(cleaner.clean("Hello world"), str)


def test_clean_strips_leading_and_trailing_whitespace(
    cleaner: TextCleaner,
) -> None:
    assert cleaner.clean("  Hello world  ") == "Hello world"


def test_clean_collapses_spaces(cleaner: TextCleaner) -> None:
    assert cleaner.clean("Hello    world") == "Hello world"


def test_clean_collapses_tabs(cleaner: TextCleaner) -> None:
    assert cleaner.clean("Hello\t\tworld") == "Hello world"


def test_clean_collapses_newlines(cleaner: TextCleaner) -> None:
    assert cleaner.clean("Hello\n\nworld") == "Hello world"


def test_clean_handles_mixed_whitespace(cleaner: TextCleaner) -> None:
    assert cleaner.clean("  Hello \t world \n again  ") == (
        "Hello world again"
    )


def test_clean_empty_string(cleaner: TextCleaner) -> None:
    assert cleaner.clean("") == ""


def test_clean_whitespace_only_returns_empty_string(
    cleaner: TextCleaner,
) -> None:
    assert cleaner.clean(" \t\n\r ") == ""


def test_clean_preserves_case(cleaner: TextCleaner) -> None:
    assert cleaner.clean("Hello SCIOS") == "Hello SCIOS"


def test_clean_preserves_unicode(cleaner: TextCleaner) -> None:
    assert cleaner.clean("  Xin   chào   Việt Nam  ") == (
        "Xin chào Việt Nam"
    )


def test_clean_preserves_punctuation(cleaner: TextCleaner) -> None:
    assert cleaner.clean(" Hello,   world! ") == "Hello, world!"


def test_clean_preserves_apostrophes(cleaner: TextCleaner) -> None:
    assert cleaner.clean("  don't   stop  ") == "don't stop"


@pytest.mark.parametrize(
    "value",
    [None, 123, 1.5, [], {}, object()],
)
def test_clean_requires_string(
    cleaner: TextCleaner,
    value: object,
) -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        cleaner.clean(value)  # type: ignore[arg-type]


def test_call_delegates_to_clean(cleaner: TextCleaner) -> None:
    text = "  Hello   SciOS!  "

    assert cleaner(text) == cleaner.clean(text)


def test_call_returns_normalized_text(cleaner: TextCleaner) -> None:
    assert cleaner("  SciOS \t Runtime\n") == "SciOS Runtime"


def test_clean_is_stateless(cleaner: TextCleaner) -> None:
    cleaner.clean("first   value")

    assert cleaner.clean("second   value") == "second value"


def test_public_exports_are_locked() -> None:
    from scios.cognitive_core.perception.modalities.text import cleaner

    assert cleaner.__all__ == ["TextCleaner"]
