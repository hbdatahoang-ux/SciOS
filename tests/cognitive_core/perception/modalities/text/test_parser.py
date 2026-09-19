import pytest

from scios.cognitive_core.perception.modalities.text.parser import (
    TextParser,
)
from scios.cognitive_core.perception.modalities.text.tokenizer import (
    TextTokenizer,
)


@pytest.fixture
def parser() -> TextParser:
    return TextParser()


def test_parser_can_be_constructed() -> None:
    assert isinstance(TextParser(), TextParser)


def test_parser_uses_default_tokenizer(parser: TextParser) -> None:
    assert isinstance(parser.tokenizer, TextTokenizer)


def test_parser_accepts_custom_tokenizer() -> None:
    tokenizer = TextTokenizer()
    parser = TextParser(tokenizer)

    assert parser.tokenizer is tokenizer


def test_parser_rejects_invalid_tokenizer() -> None:
    with pytest.raises(TypeError, match="tokenizer must be a TextTokenizer"):
        TextParser(object())  # type: ignore[arg-type]


def test_parse_returns_dictionary(parser: TextParser) -> None:
    result = parser.parse("Hello world.")

    assert isinstance(result, dict)


def test_parse_preserves_text(parser: TextParser) -> None:
    text = "Hello world."

    result = parser.parse(text)

    assert result["text"] == text


def test_parse_generates_tokens(parser: TextParser) -> None:
    result = parser.parse("Hello world!")

    assert result["tokens"] == ["Hello", "world", "!"]


def test_parse_counts_tokens(parser: TextParser) -> None:
    result = parser.parse("Hello world!")

    assert result["token_count"] == 3


def test_parse_counts_words(parser: TextParser) -> None:
    result = parser.parse("Hello world!")

    assert result["word_count"] == 2


def test_parse_counts_sentences(parser: TextParser) -> None:
    result = parser.parse("Hello world!")

    assert result["sentence_count"] == 1


def test_parse_multiple_sentences(parser: TextParser) -> None:
    result = parser.parse("Hello. How are you? Fine!")

    assert result["sentence_count"] == 3


def test_parse_empty_text(parser: TextParser) -> None:
    result = parser.parse("")

    assert result == {
        "text": "",
        "tokens": [],
        "token_count": 0,
        "word_count": 0,
        "sentence_count": 0,
    }


def test_parse_whitespace_text(parser: TextParser) -> None:
    result = parser.parse("   ")

    assert result["tokens"] == []
    assert result["token_count"] == 0
    assert result["word_count"] == 0
    assert result["sentence_count"] == 0


def test_parse_preserves_unicode(parser: TextParser) -> None:
    result = parser.parse("Xin chào Việt Nam!")

    assert result["tokens"] == [
        "Xin",
        "chào",
        "Việt",
        "Nam",
        "!",
    ]
    assert result["word_count"] == 4


def test_parse_accepts_explicit_tokens(parser: TextParser) -> None:
    tokens = ["Custom", "tokens", "!"]

    result = parser.parse("ignored text", tokens=tokens)

    assert result["tokens"] == tokens
    assert result["token_count"] == 3


def test_parse_copies_explicit_tokens(parser: TextParser) -> None:
    tokens = ["Hello", "world"]

    result = parser.parse("Hello world", tokens=tokens)
    tokens.append("extra")

    assert result["tokens"] == ["Hello", "world"]


def test_parse_does_not_mutate_explicit_tokens(parser: TextParser) -> None:
    tokens = ["Hello", ",", "world", "!"]

    parser.parse("Hello, world!", tokens=tokens)

    assert tokens == ["Hello", ",", "world", "!"]


@pytest.mark.parametrize(
    "value",
    [None, 123, 1.5, [], {}, object()],
)
def test_parse_requires_string(
    parser: TextParser,
    value: object,
) -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        parser.parse(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "tokens",
    [None, "tokens", 123, {}, object()],
)
def test_explicit_tokens_must_be_list(
    parser: TextParser,
    tokens: object,
) -> None:
    if tokens is None:
        pytest.skip("None means use the tokenizer")

    with pytest.raises(TypeError, match="tokens must be a list"):
        parser.parse("text", tokens=tokens)  # type: ignore[arg-type]


def test_explicit_tokens_must_contain_strings(
    parser: TextParser,
) -> None:
    with pytest.raises(
        TypeError,
        match="tokens must contain only strings",
    ):
        parser.parse("text", tokens=["valid", 123])  # type: ignore[list-item]


def test_public_exports_are_locked() -> None:
    from scios.cognitive_core.perception.modalities.text import parser

    assert parser.__all__ == ["TextParser"]
