"""Contract tests for the image perception modality package."""

import importlib


EXPECTED_EXPORTS = {
    "ImageDetector",
    "ImageEncoder",
    "ImageLoader",
    "ImagePerceptor",
    "ImagePreprocessor",
}


def test_image_package_imports() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.image"
    )

    assert module is not None


def test_image_package_public_exports() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.image"
    )

    assert set(module.__all__) == EXPECTED_EXPORTS


def test_image_package_exports_are_importable() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.image"
    )

    for name in EXPECTED_EXPORTS:
        assert hasattr(module, name)


def test_image_package_export_identity() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.image"
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

    assert module.ImageDetector is ImageDetector
    assert module.ImageEncoder is ImageEncoder
    assert module.ImageLoader is ImageLoader
    assert module.ImagePerceptor is ImagePerceptor
    assert module.ImagePreprocessor is ImagePreprocessor
