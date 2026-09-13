from scios.cognitive_core.reflection.stage import (
    ReflectionStage,
    StageTracker,
)


def test_stage_tracker_initialization():
    tracker = StageTracker()

    assert tracker.get_stage() == "initialized"
    assert tracker.get_stage_enum() is ReflectionStage.INITIALIZED
    assert tracker.history == [ReflectionStage.INITIALIZED]


def test_stage_tracker_explicit_transition():
    tracker = StageTracker()

    tracker.advance("evaluation")
    tracker.advance("critique")

    assert tracker.get_stage() == "critique"
    assert tracker.history == [
        ReflectionStage.INITIALIZED,
        ReflectionStage.EVALUATION,
        ReflectionStage.CRITIQUE,
    ]


def test_stage_tracker_canonical_sequential_lifecycle():
    tracker = StageTracker()

    expected = [
        "evaluation",
        "critique",
        "analysis",
        "metrics",
        "scoring",
        "improvement",
        "feedback",
        "report",
        "self_review",
        "validation",
        "adaptive",
        "completed",
    ]

    actual = []
    for _ in expected:
        tracker.advance()
        actual.append(tracker.get_stage())

    assert actual == expected


def test_stage_tracker_compatibility_score_stage():
    tracker = StageTracker()

    tracker.advance("score")

    assert tracker.get_stage() == "score"
    assert tracker.get_stage_enum() is ReflectionStage.SCORING


def test_stage_tracker_invalid_stage():
    tracker = StageTracker()

    try:
        tracker.advance("not-a-stage")
    except ValueError as exc:
        assert str(exc) == "Unknown reflection stage: not-a-stage"
    else:
        raise AssertionError("Expected ValueError")


def test_stage_tracker_reset():
    tracker = StageTracker()

    tracker.advance("analysis")
    tracker.reset()

    assert tracker.get_stage() == "initialized"
    assert tracker.history == [ReflectionStage.INITIALIZED]


def test_stage_tracker_status():
    tracker = StageTracker()

    tracker.advance("evaluation")
    status = tracker.status()

    assert status == {
        "stage": "evaluation",
        "history": ["initialized", "evaluation"],
    }


def test_stage_tracker_repr_contains_stage():
    tracker = StageTracker()
    tracker.advance("evaluation")

    representation = repr(tracker)

    assert "StageTracker" in representation
    assert "evaluation" in representation
