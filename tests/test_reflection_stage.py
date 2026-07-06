# tests/test_reflection_stage.py
import pytest
from scios.cognitive_core.reflection.reflection_stage import StageTracker

def test_stage_tracker_initialization():
    tracker = StageTracker()
    assert tracker is not None
    assert tracker.get_stage() == "initialized"

def test_stage_tracker_advance():
    tracker = StageTracker()
    tracker.advance("evaluation")
    assert tracker.get_stage() == "evaluation"

    tracker.advance("critique")
    assert tracker.get_stage() == "critique"

def test_stage_tracker_reset():
    tracker = StageTracker()
    tracker.advance("analysis")
    assert tracker.get_stage() == "analysis"

    tracker.reset()
    assert tracker.get_stage() == "initialized"

def test_stage_tracker_multiple_advances():
    tracker = StageTracker()
    stages = ["evaluation", "critique", "analysis", "metrics", "score", "feedback", "report"]
    for stage in stages:
        tracker.advance(stage)
        assert tracker.get_stage() == stage

def test_stage_tracker_repr_contains_stage():
    tracker = StageTracker()
    tracker.advance("evaluation")
    repr_str = repr(tracker)
    assert "StageTracker" in repr_str
    assert "evaluation" in repr_str
