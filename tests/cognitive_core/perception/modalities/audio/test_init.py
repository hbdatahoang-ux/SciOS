"""Contract tests for the audio perception modality package."""

import importlib


EXPECTED_EXPORTS = {
    "AudioEncoder",
    "AudioExtractor",
    "AudioLoader",
    "AudioPerceptor",
    "AudioPreprocessor",
    "SpeechProcessor",
}


def test_audio_package_imports() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.audio"
    )

    assert module is not None


def test_audio_package_public_exports() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.audio"
    )

    assert set(module.__all__) == EXPECTED_EXPORTS


def test_audio_package_exports_are_importable() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.audio"
    )

    for name in EXPECTED_EXPORTS:
        assert hasattr(module, name)


def test_audio_package_export_identity() -> None:
    module = importlib.import_module(
        "scios.cognitive_core.perception.modalities.audio"
    )

    from scios.cognitive_core.perception.modalities.audio.encoder import (
        AudioEncoder,
    )
    from scios.cognitive_core.perception.modalities.audio.extractor import (
        AudioExtractor,
    )
    from scios.cognitive_core.perception.modalities.audio.loader import (
        AudioLoader,
    )
    from scios.cognitive_core.perception.modalities.audio.perceptor import (
        AudioPerceptor,
    )
    from scios.cognitive_core.perception.modalities.audio.preprocess import (
        AudioPreprocessor,
    )
    from scios.cognitive_core.perception.modalities.audio.speech import (
        SpeechProcessor,
    )

    assert module.AudioEncoder is AudioEncoder
    assert module.AudioExtractor is AudioExtractor
    assert module.AudioLoader is AudioLoader
    assert module.AudioPerceptor is AudioPerceptor
    assert module.AudioPreprocessor is AudioPreprocessor
    assert module.SpeechProcessor is SpeechProcessor
