"""Contract tests for the video modality public API."""

from scios.cognitive_core.perception.modalities.video import (
    VideoEncoder,
    VideoExtractor,
    VideoFrameExtractor,
    VideoLoader,
    VideoPerceptor,
    VideoPreprocessor,
)


def test_public_exports() -> None:
    from scios.cognitive_core.perception.modalities.video import (
        __all__,
    )

    assert __all__ == [
        "VideoEncoder",
        "VideoExtractor",
        "VideoFrameExtractor",
        "VideoLoader",
        "VideoPerceptor",
        "VideoPreprocessor",
    ]


def test_public_classes_are_importable() -> None:
    assert VideoEncoder.__name__ == "VideoEncoder"
    assert VideoExtractor.__name__ == "VideoExtractor"
    assert VideoFrameExtractor.__name__ == "VideoFrameExtractor"
    assert VideoLoader.__name__ == "VideoLoader"
    assert VideoPerceptor.__name__ == "VideoPerceptor"
    assert VideoPreprocessor.__name__ == "VideoPreprocessor"


def test_public_exports_are_classes() -> None:
    for exported in (
        VideoEncoder,
        VideoExtractor,
        VideoFrameExtractor,
        VideoLoader,
        VideoPerceptor,
        VideoPreprocessor,
    ):
        assert isinstance(exported, type)
