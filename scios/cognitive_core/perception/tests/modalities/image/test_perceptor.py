"""Contract tests for the image perceptor."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core import (
    BasePerceptor,
    Modality,
    PerceptionInputError,
    PerceptionResult,
    PerceptionStatus,
)
from scios.cognitive_core.perception.modalities.image.detector import (
    ImageDetector,
)
from scios.cognitive_core.perception.modalities.image.encoder import (
    ImageEncoder,
)
from scios.cognitive_core.perception.modalities.image.loader import (
    ImageLoader,
)
from scios.cognitive_core.perception.modalities.image.perceptor import (
    ImagePerceptor,
)
from scios.cognitive_core.perception.modalities.image.preprocess import (
    ImagePreprocessor,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-png-data"
JPEG_BYTES = b"\xff\xd8\xff\xe0fake-jpeg-data"


@pytest.fixture
def perceptor() -> ImagePerceptor:
    return ImagePerceptor()


def test_constructor() -> None:
    perceptor = ImagePerceptor()

    assert isinstance(perceptor, ImagePerceptor)
    assert isinstance(perceptor, BasePerceptor)


def test_default_name(perceptor: ImagePerceptor) -> None:
    assert perceptor.name == "image"


def test_modality(perceptor: ImagePerceptor) -> None:
    assert perceptor.modality is Modality.IMAGE


def test_default_components(perceptor: ImagePerceptor) -> None:
    assert isinstance(perceptor.loader, ImageLoader)
    assert isinstance(perceptor.preprocessor, ImagePreprocessor)
    assert isinstance(perceptor.detector, ImageDetector)
    assert isinstance(perceptor.encoder, ImageEncoder)


def test_custom_components_are_preserved() -> None:
    loader = ImageLoader()
    preprocessor = ImagePreprocessor()
    detector = ImageDetector()
    encoder = ImageEncoder()

    perceptor = ImagePerceptor(
        loader=loader,
        preprocessor=preprocessor,
        detector=detector,
        encoder=encoder,
    )

    assert perceptor.loader is loader
    assert perceptor.preprocessor is preprocessor
    assert perceptor.detector is detector
    assert perceptor.encoder is encoder


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("loader", object(), "loader must be an ImageLoader"),
        (
            "preprocessor",
            object(),
            "preprocessor must be an ImagePreprocessor",
        ),
        ("detector", object(), "detector must be an ImageDetector"),
        ("encoder", object(), "encoder must be an ImageEncoder"),
    ],
)
def test_invalid_component_rejected(
    argument: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        ImagePerceptor(**{argument: value})


def test_custom_name() -> None:
    perceptor = ImagePerceptor(name="vision")

    assert perceptor.name == "vision"
    assert perceptor.modality is Modality.IMAGE


def test_perceive_returns_result(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert isinstance(result, PerceptionResult)


def test_perceive_status(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.status is PerceptionStatus.SUCCESS


def test_perceive_modality(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.modality is Modality.IMAGE


def test_perceive_preserves_content(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.content is PNG_BYTES
    assert result.content == PNG_BYTES


def test_perceive_confidence(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.confidence == 1.0


def test_perceive_embedding(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert isinstance(result.embedding, tuple)
    assert len(result.embedding) == 32


def test_perceive_empty_detections(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.entities == []
    assert result.relations == []


def test_perceive_features(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.features == {
        "format": "png",
        "original_size": len(PNG_BYTES),
        "detection_count": 0,
        "detection_backend": "deterministic",
    }


def test_perceive_metadata_for_bytes(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    assert result.metadata["source_name"] is None
    assert result.metadata["format"] == "png"
    assert result.metadata["original_size"] == len(PNG_BYTES)
    assert result.metadata["detection_backend"] == "deterministic"
    assert result.metadata["encoding_backend"] == "deterministic"


def test_perceive_preserves_input_metadata(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(
        PNG_BYTES,
        metadata={
            "request_id": "req-001",
            "source": "test",
        },
    )

    assert result.metadata["request_id"] == "req-001"
    assert result.metadata["source"] == "test"


def test_perceive_path(
    perceptor: ImagePerceptor,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.png"
    path.write_bytes(PNG_BYTES)

    result = perceptor.perceive(path)

    assert result.content == PNG_BYTES
    assert result.metadata["source_name"] == "sample.png"
    assert result.metadata["format"] == "png"


def test_perceive_string_path(
    perceptor: ImagePerceptor,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.jpg"
    path.write_bytes(JPEG_BYTES)

    result = perceptor.perceive(str(path))

    assert result.content == JPEG_BYTES
    assert result.metadata["source_name"] == "sample.jpg"
    assert result.metadata["format"] == "jpeg"


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        123,
        1.5,
        [],
        {},
    ],
)
def test_invalid_input_propagates(
    perceptor: ImagePerceptor,
    value: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        perceptor.perceive(value)


def test_invalid_image_bytes_propagate(
    perceptor: ImagePerceptor,
) -> None:
    with pytest.raises(PerceptionInputError):
        perceptor.perceive(b"not-an-image")


def test_result_validates(
    perceptor: ImagePerceptor,
) -> None:
    result = perceptor.perceive(PNG_BYTES)

    result.validate()


def test_pipeline_components_are_used() -> None:
    class TrackingLoader(ImageLoader):
        def load(self, source):
            result = super().load(source)
            result["metadata"]["loader_called"] = True
            return result

    class TrackingPreprocessor(ImagePreprocessor):
        def preprocess(self, data):
            result = super().preprocess(data)
            result["metadata"]["preprocessor_called"] = True
            return result

    loader = TrackingLoader()
    preprocessor = TrackingPreprocessor()

    perceptor = ImagePerceptor(
        loader=loader,
        preprocessor=preprocessor,
    )

    result = perceptor.perceive(PNG_BYTES)

    assert result.metadata["loader_called"] is True
    assert result.metadata["preprocessor_called"] is True


def test_detector_and_encoder_metadata_reach_result() -> None:
    class TrackingDetector(ImageDetector):
        def detect(self, data):
            result = super().detect(data)
            result["metadata"]["detector_called"] = True
            return result

    class TrackingEncoder(ImageEncoder):
        def encode(self, data):
            result = super().encode(data)
            result["metadata"]["encoder_called"] = True
            return result

    perceptor = ImagePerceptor(
        detector=TrackingDetector(),
        encoder=TrackingEncoder(),
    )

    result = perceptor.perceive(PNG_BYTES)

    assert result.metadata["detection_backend"] == "deterministic"
    assert result.metadata["encoding_backend"] == "deterministic"


def test_perceive_deterministic(
    perceptor: ImagePerceptor,
) -> None:
    first = perceptor.perceive(PNG_BYTES)
    second = perceptor.perceive(PNG_BYTES)

    assert first.to_dict() == second.to_dict()
