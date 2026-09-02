import pytest

from scios.cognitive_core.perception.modalities.text.cleaner import (
    TextCleaner,
)
from scios.cognitive_core.perception.modalities.text.extractor import (
    TextExtractor,
)
from scios.cognitive_core.perception.modalities.text.parser import (
    TextParser,
)
from scios.cognitive_core.perception.modalities.text.perceptor import (
    TextPerceptor,
)
from scios.cognitive_core.perception.modalities.text.tokenizer import (
    TextTokenizer,
)
from scios.cognitive_core.perception.core import (
    BasePerceptor,
    Modality,
    PerceptionInputError,
    PerceptionProcessingError,
    PerceptionResult,
    PerceptionStatus,
)


@pytest.fixture
def perceptor() -> TextPerceptor:
    return TextPerceptor()


def test_perceptor_can_be_constructed() -> None:
    assert isinstance(TextPerceptor(), TextPerceptor)


def test_perceptor_is_base_perceptor(perceptor: TextPerceptor) -> None:
    assert isinstance(perceptor, BasePerceptor)


def test_default_name(perceptor: TextPerceptor) -> None:
    assert perceptor.name == "text"


def test_modality_is_text(perceptor: TextPerceptor) -> None:
    assert perceptor.modality is Modality.TEXT


def test_default_cleaner(perceptor: TextPerceptor) -> None:
    assert isinstance(perceptor.cleaner, TextCleaner)


def test_default_tokenizer(perceptor: TextPerceptor) -> None:
    assert isinstance(perceptor.tokenizer, TextTokenizer)


def test_default_parser(perceptor: TextPerceptor) -> None:
    assert isinstance(perceptor.parser, TextParser)


def test_default_extractor(perceptor: TextPerceptor) -> None:
    assert isinstance(perceptor.extractor, TextExtractor)


def test_components_are_wired_together(perceptor: TextPerceptor) -> None:
    assert perceptor.parser.tokenizer is perceptor.tokenizer
    assert perceptor.extractor.parser is perceptor.parser


def test_custom_components_are_preserved() -> None:
    cleaner = TextCleaner()
    tokenizer = TextTokenizer()
    parser = TextParser(tokenizer=tokenizer)
    extractor = TextExtractor(parser=parser)

    perceptor = TextPerceptor(
        name="custom-text",
        cleaner=cleaner,
        tokenizer=tokenizer,
        parser=parser,
        extractor=extractor,
    )

    assert perceptor.name == "custom-text"
    assert perceptor.cleaner is cleaner
    assert perceptor.tokenizer is tokenizer
    assert perceptor.parser is parser
    assert perceptor.extractor is extractor


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("cleaner", object(), "cleaner must be a TextCleaner"),
        ("tokenizer", object(), "tokenizer must be a TextTokenizer"),
        ("parser", object(), "parser must be a TextParser"),
        ("extractor", object(), "extractor must be a TextExtractor"),
    ],
)
def test_invalid_components_are_rejected(
    argument: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        TextPerceptor(**{argument: value})  # type: ignore[arg-type]


def test_perceive_returns_perception_result(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world.")

    assert isinstance(result, PerceptionResult)


def test_perceive_returns_success(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world.")

    assert result.status is PerceptionStatus.SUCCESS
    assert result.successful


def test_perceive_uses_text_modality(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world.")

    assert result.modality is Modality.TEXT


def test_perceive_cleans_content(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("  Hello   world!  ")

    assert result.content == "Hello world!"


def test_perceive_extracts_features(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world!")

    assert result.features == {
        "character_count": 12,
        "token_count": 3,
        "word_count": 2,
        "sentence_count": 1,
    }


def test_perceive_returns_empty_entities(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world.")

    assert result.entities == []


def test_perceive_returns_empty_relations(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world.")

    assert result.relations == []


def test_perceive_confidence_is_complete_for_deterministic_pipeline(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Hello world.")

    assert result.confidence == 1.0


def test_perceive_preserves_metadata(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive(
        "Hello world.",
        metadata={"source": "test"},
    )

    assert result.metadata["source"] == "test"


def test_perceive_adds_length_metadata(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("  Hello world.  ")

    assert result.metadata["raw_length"] == 16
    assert result.metadata["cleaned_length"] == 12


@pytest.mark.parametrize(
    "value",
    [None, 123, 1.5, [], {}, object()],
)
def test_perceive_rejects_non_string_input(
    perceptor: TextPerceptor,
    value: object,
) -> None:
    with pytest.raises(
        PerceptionInputError,
        match="text perception input must be a string",
    ):
        perceptor.perceive(value)  # type: ignore[arg-type]


def test_perceive_does_not_mutate_metadata(
    perceptor: TextPerceptor,
) -> None:
    metadata = {"source": "test"}

    result = perceptor.perceive(
        "Hello.",
        metadata=metadata,
    )

    result.metadata["extra"] = True

    assert metadata == {"source": "test"}


def test_perceive_empty_text(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("")

    assert result.content == ""
    assert result.features == {
        "character_count": 0,
        "token_count": 0,
        "word_count": 0,
        "sentence_count": 0,
    }


def test_perceive_unicode_text(
    perceptor: TextPerceptor,
) -> None:
    result = perceptor.perceive("Xin chào Việt Nam!")

    assert result.content == "Xin chào Việt Nam!"
    assert result.features["word_count"] == 4


def test_perceive_wraps_processing_failure() -> None:
    class FailingCleaner(TextCleaner):
        def clean(self, text: str) -> str:
            raise RuntimeError("boom")

    perceptor = TextPerceptor(cleaner=FailingCleaner())

    with pytest.raises(
        PerceptionProcessingError,
        match="text perception processing failed",
    ):
        perceptor.perceive("Hello")


def test_processing_error_preserves_cause() -> None:
    class FailingTokenizer(TextTokenizer):
        def tokenize(self, text: str) -> list[str]:
            raise RuntimeError("tokenizer failure")

    perceptor = TextPerceptor(tokenizer=FailingTokenizer())

    with pytest.raises(PerceptionProcessingError) as exc_info:
        perceptor.perceive("Hello")

    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_public_exports_are_locked() -> None:
    from scios.cognitive_core.perception.modalities.text import perceptor

    assert perceptor.__all__ == ["TextPerceptor"]
