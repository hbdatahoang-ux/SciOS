import pytest

from scios.cognitive_core.perception.modalities.text.tokenizer import (
    TextTokenizer,
)


@pytest.fixture
def tokenizer() -> TextTokenizer:
    return TextTokenizer()


def test_tokenizer_can_be_constructed() -> None:
    tokenizer = TextTokenizer()

    assert isinstance(tokenizer, TextTokenizer)


def test_tokenize_returns_list(tokenizer: TextTokenizer) -> None:
    result = tokenizer.tokenize("Hello world")

    assert isinstance(result, list)


def test_tokenize_splits_words(tokenizer: TextTokenizer) -> None:
    assert tokenizer.tokenize("Hello world") == ["Hello", "world"]


def test_tokenize_separates_punctuation(tokenizer: TextTokenizer) -> None:
    assert tokenizer.tokenize("Hello, world!") == [
        "Hello",
        ",",
        "world",
        "!",
    ]


def test_tokenize_handles_multiple_whitespace(tokenizer: TextTokenizer) -> None:
    assert tokenizer.tokenize("Hello   world\tagain\n") == [
        "Hello",
        "world",
        "again",
    ]


def test_tokenize_empty_string_returns_empty_list(
    tokenizer: TextTokenizer,
) -> None:
    assert tokenizer.tokenize("") == []


def test_tokenize_whitespace_returns_empty_list(
    tokenizer: TextTokenizer,
) -> None:
    assert tokenizer.tokenize("   \t\n") == []


def test_tokenize_preserves_unicode(tokenizer: TextTokenizer) -> None:
    assert tokenizer.tokenize("Xin chào Việt Nam!") == [
        "Xin",
        "chào",
        "Việt",
        "Nam",
        "!",
    ]


def test_tokenize_preserves_apostrophe_inside_word(
    tokenizer: TextTokenizer,
) -> None:
    assert tokenizer.tokenize("don't stop") == ["don't", "stop"]


def test_tokenize_supports_unicode_apostrophe(
    tokenizer: TextTokenizer,
) -> None:
    assert tokenizer.tokenize("Việt Nam’s") == ["Việt", "Nam’s"]


@pytest.mark.parametrize(
    "value",
    [None, 123, 1.5, [], {}, object()],
)
def test_tokenize_requires_string(
    tokenizer: TextTokenizer,
    value: object,
) -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        tokenizer.tokenize(value)  # type: ignore[arg-type]


def test_call_delegates_to_tokenize(tokenizer: TextTokenizer) -> None:
    text = "Hello, SciOS!"

    assert tokenizer(text) == tokenizer.tokenize(text)


def test_call_returns_independent_list(tokenizer: TextTokenizer) -> None:
    first = tokenizer("Hello world")
    first.append("extra")

    assert tokenizer("Hello world") == ["Hello", "world"]


def test_public_exports_are_locked() -> None:
    from scios.cognitive_core.perception.modalities.text import tokenizer

    assert tokenizer.__all__ == ["TextTokenizer"]
