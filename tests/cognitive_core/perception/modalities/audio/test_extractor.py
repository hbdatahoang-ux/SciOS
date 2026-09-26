"""Contract tests for the audio extractor."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.audio.extractor import (
    AudioExtractor,
)


@pytest.fixture
def extractor() -> AudioExtractor:
    return AudioExtractor()


def test_extractor_imports() -> None:
    extractor = AudioExtractor()

    assert extractor is not None


def test_validate_input_accepts_speech_result(
    extractor: AudioExtractor,
) -> None:
    data = {
        "text": "hello world",
        "segments": [],
    }

    assert extractor.validate_input(data) is None


@pytest.mark.parametrize(
    "data",
    [
        None,
        "audio",
        b"audio",
        [],
        123,
    ],
)
def test_validate_input_rejects_non_dictionary(
    extractor: AudioExtractor,
    data: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(data)


def test_validate_input_requires_text(
    extractor: AudioExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input({"segments": []})


def test_validate_input_requires_string_text(
    extractor: AudioExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
            {
                "text": 123,
                "segments": [],
            }
        )


def test_validate_input_requires_list_segments(
    extractor: AudioExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
            {
                "text": "hello",
                "segments": {},
            }
        )


def test_extract_text_length(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "hello world",
            "segments": [],
        }
    )

    assert result["features"]["text_length"] == 11


def test_extract_word_count(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "hello world from audio",
            "segments": [],
        }
    )

    assert result["features"]["word_count"] == 4


def test_extract_segment_count(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "hello world",
            "segments": [
                {"text": "hello"},
                {"text": "world"},
            ],
        }
    )

    assert result["features"]["segment_count"] == 2


def test_extract_empty_text(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "",
            "segments": [],
        }
    )

    assert result["features"] == {
        "text_length": 0,
        "segment_count": 0,
        "word_count": 0,
    }


def test_extract_returns_entities(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "hello",
            "segments": [],
        }
    )

    assert result["entities"] == []


def test_extract_returns_relations(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "hello",
            "segments": [],
        }
    )

    assert result["relations"] == []


def test_extract_has_expected_structure(
    extractor: AudioExtractor,
) -> None:
    result = extractor.extract(
        {
            "text": "hello",
            "segments": [],
        }
    )

    assert set(result) == {
        "features",
        "entities",
        "relations",
    }
