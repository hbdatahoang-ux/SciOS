"""Contract tests for the video perceptor."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core.result import PerceptionResult
from scios.cognitive_core.perception.core.types import (
    Modality,
    PerceptionStatus,
)
from scios.cognitive_core.perception.modalities.video.encoder import (
    VideoEncoder,
)
from scios.cognitive_core.perception.modalities.video.extractor import (
    VideoExtractor,
)
from scios.cognitive_core.perception.modalities.video.frames import (
    VideoFrameExtractor,
)
from scios.cognitive_core.perception.modalities.video.loader import (
    VideoLoader,
)
from scios.cognitive_core.perception.modalities.video.perceptor import (
    VideoPerceptor,
)
from scios.cognitive_core.perception.modalities.video.preprocess import (
    VideoPreprocessor,
)


@pytest.fixture
def perceptor() -> VideoPerceptor:
    return VideoPerceptor()


@pytest.fixture
def video_bytes() -> bytes:
    return (
        b"\x00\x00\x00\x18"
        b"ftyp"
        b"isom"
        b"\x00\x00\x02\x00"
    )


def test_default_identity(
    perceptor: VideoPerceptor,
) -> None:
    assert perceptor.name == "video"
    assert perceptor.modality is Modality.VIDEO


def test_default_components(
    perceptor: VideoPerceptor,
) -> None:
    assert isinstance(perceptor.loader, VideoLoader)
    assert isinstance(
        perceptor.frame_extractor,
        VideoFrameExtractor,
    )
    assert isinstance(
        perceptor.preprocessor,
        VideoPreprocessor,
    )
    assert isinstance(
        perceptor.extractor,
        VideoExtractor,
    )
    assert isinstance(
        perceptor.encoder,
        VideoEncoder,
    )


def test_custom_name(
    perceptor: VideoPerceptor,
) -> None:
    custom = VideoPerceptor(name="custom-video")

    assert custom.name == "custom-video"
    assert custom.modality is Modality.VIDEO


def test_custom_components_are_preserved() -> None:
    loader = VideoLoader()
    frame_extractor = VideoFrameExtractor()
    preprocessor = VideoPreprocessor()
    extractor = VideoExtractor()
    encoder = VideoEncoder()

    perceptor = VideoPerceptor(
        loader=loader,
        frame_extractor=frame_extractor,
        preprocessor=preprocessor,
        extractor=extractor,
        encoder=encoder,
    )

    assert perceptor.loader is loader
    assert perceptor.frame_extractor is frame_extractor
    assert perceptor.preprocessor is preprocessor
    assert perceptor.extractor is extractor
    assert perceptor.encoder is encoder


def test_perceive_returns_perception_result(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert isinstance(result, PerceptionResult)


def test_perceive_success_status(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.status is PerceptionStatus.SUCCESS


def test_perceive_video_modality(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.modality is Modality.VIDEO


def test_perceive_has_content(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert isinstance(result.content, dict)
    assert "frames" in result.content
    assert "frame_count" in result.content


def test_perceive_has_features(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.features["frame_count"] == 1
    assert result.features["has_frames"] is True


def test_perceive_has_embedding(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert isinstance(result.embedding, list)
    assert len(result.embedding) == 32


def test_perceive_confidence(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.confidence == 1.0


def test_perceive_entities_are_empty(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.entities == []


def test_perceive_relations_are_empty(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.relations == []


def test_perceive_metadata_contains_loader_information(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.metadata["source_name"] is None
    assert result.metadata["format"] == "mp4"


def test_perceive_metadata_contains_pipeline_information(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(video_bytes)

    assert result.metadata["backend"] == "deterministic"
    assert result.metadata["feature_frame_count"] == 1
    assert result.metadata["has_frames"] is True
    assert result.metadata["embedding_dimension"] == 32


def test_user_metadata_is_preserved(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    result = perceptor.perceive(
        video_bytes,
        metadata={
            "request_id": "req-001",
            "source": "test",
        },
    )

    assert result.metadata["request_id"] == "req-001"
    assert result.metadata["source"] == "test"


def test_perceive_is_deterministic(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    first = perceptor.perceive(video_bytes)
    second = perceptor.perceive(video_bytes)

    assert first.to_dict() == second.to_dict()


def test_perceive_path_source(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.mp4"
    path.write_bytes(video_bytes)

    result = perceptor.perceive(path)

    assert result.successful
    assert result.metadata["source_name"] == "sample.mp4"
    assert result.metadata["format"] == "mp4"


def test_perceive_string_path_source(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.mp4"
    path.write_bytes(video_bytes)

    result = perceptor.perceive(str(path))

    assert result.successful
    assert result.metadata["source_name"] == "sample.mp4"


def test_invalid_source_propagates(
    perceptor: VideoPerceptor,
) -> None:
    with pytest.raises(Exception):
        perceptor.perceive(b"")


def test_perceive_does_not_mutate_metadata(
    perceptor: VideoPerceptor,
    video_bytes: bytes,
) -> None:
    metadata = {
        "request_id": "req-002",
    }

    original = dict(metadata)

    perceptor.perceive(
        video_bytes,
        metadata=metadata,
    )

    assert metadata == original


def test_pipeline_uses_all_components(
    video_bytes: bytes,
) -> None:
    calls: list[str] = []

    class TrackingLoader(VideoLoader):
        def load(self, source):
            calls.append("loader")
            return super().load(source)

    class TrackingFrames(VideoFrameExtractor):
        def extract(self, data):
            calls.append("frames")
            return super().extract(data)

    class TrackingPreprocessor(VideoPreprocessor):
        def preprocess(self, data):
            calls.append("preprocess")
            return super().preprocess(data)

    class TrackingExtractor(VideoExtractor):
        def extract(self, data):
            calls.append("extractor")
            return super().extract(data)

    class TrackingEncoder(VideoEncoder):
        def encode(self, data):
            calls.append("encoder")
            return super().encode(data)

    perceptor = VideoPerceptor(
        loader=TrackingLoader(),
        frame_extractor=TrackingFrames(),
        preprocessor=TrackingPreprocessor(),
        extractor=TrackingExtractor(),
        encoder=TrackingEncoder(),
    )

    result = perceptor.perceive(video_bytes)

    assert result.successful
    assert calls == [
        "loader",
        "frames",
        "preprocess",
        "extractor",
        "encoder",
    ]
