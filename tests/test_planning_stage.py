# tests/test_planning_stage.py

import pytest
from scios.cognitive_core.planner.stage import PlanningStage

def test_stage_initialization():
    stage = PlanningStage(name="initialization", description="Start planning")
    assert stage.name == "initialization"
    assert stage.description == "Start planning"
    assert stage.next_stages == []

def test_add_next_stage():
    stage = PlanningStage(name="planning")
    stage.add_next_stage("validation")
    assert "validation" in stage.next_stages

def test_add_next_stage_no_duplicates():
    stage = PlanningStage(name="execution")
    stage.add_next_stage("monitoring")
    stage.add_next_stage("monitoring")  # thêm trùng
    assert stage.next_stages.count("monitoring") == 1

def test_can_transition_to_valid_stage():
    stage = PlanningStage(name="validation", next_stages=["execution"])
    assert stage.can_transition_to("execution") is True

def test_can_transition_to_invalid_stage():
    stage = PlanningStage(name="validation", next_stages=["execution"])
    assert stage.can_transition_to("recovery") is False

def test_stage_repr():
    stage = PlanningStage(name="monitoring", next_stages=["recovery"])
    assert "monitoring" in repr(stage)
    assert "recovery" in repr(stage)
