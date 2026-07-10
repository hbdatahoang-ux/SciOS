import pytest
from scios.kernel.artifacts import ArtifactManager, ArtifactType


# ----------------------------------------------------------------------
# Phase A — Artifact Creation
# ----------------------------------------------------------------------

def test_create_text_artifact():
    manager = ArtifactManager()
    artifact = manager.create(
        name="demo",
        type=ArtifactType.TEXT,
        content="Hello World"
    )

    assert artifact.name == "demo"
    assert artifact.type == ArtifactType.TEXT
    assert artifact.content == "Hello World"


def test_create_multiple_artifacts():
    manager = ArtifactManager()
    a1 = manager.create(name="a1", type=ArtifactType.TEXT, content="One")
    a2 = manager.create(name="a2", type=ArtifactType.TEXT, content="Two")

    artifacts = manager.list()
    names = [a.name for a in artifacts]

    assert "a1" in names
    assert "a2" in names
    assert len(artifacts) == 2


# ----------------------------------------------------------------------
# Phase B — Event Publishing
# ----------------------------------------------------------------------

def test_artifact_creation_event_published():
    events = []

    def listener(event, **payload):
        events.append(event)

    manager = ArtifactManager()
    manager.event_bus.subscribe(listener)

    manager.create(name="demo", type=ArtifactType.TEXT, content="Hello")

    assert any(ev == "artifact.created" for ev in events)


# ----------------------------------------------------------------------
# Phase C — Registry Management
# ----------------------------------------------------------------------

def test_get_and_delete_artifact():
    manager = ArtifactManager()
    artifact = manager.create(name="demo", type=ArtifactType.TEXT, content="Hello")

    fetched = manager.get("demo")
    assert fetched is artifact

    manager.delete("demo")
    assert not any(a.name == "demo" for a in manager.list())
