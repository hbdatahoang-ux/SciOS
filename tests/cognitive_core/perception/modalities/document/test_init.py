"""Tests for the Document modality package boundary."""

def test_document_package_imports() -> None:
    from scios.cognitive_core.perception.modalities import document

    assert document is not None


def test_document_public_exports_are_deferred() -> None:
    from scios.cognitive_core.perception.modalities import document

    assert document.__all__ == []
