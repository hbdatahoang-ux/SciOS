# tests/test_tool_stage.py

import pytest
from scios.cognitive_core.tool_use.stage import ToolStage


def test_stage_initialization_and_schema():
    stage = ToolStage()
    assert stage.status == "idle"
    assert stage.message is None

    data = stage.to_dict()
    required_keys = {"status", "message"}
    assert required_keys.issubset(data.keys())
    assert data["status"] == "idle"


def test_stage_start_and_complete_success():
    stage = ToolStage()
    stage.start("Preparing to run")
    assert stage.status == "running"
    assert "Preparing" in stage.message

    stage.complete("Finished successfully")
    assert stage.status == "success"
    assert "Finished successfully" in stage.message


def test_stage_error_handling():
    stage = ToolStage()
    stage.start("Running")
    stage.error("Something went wrong")

    assert stage.status == "error"
    assert "Something went wrong" in stage.message


def test_stage_reset():
    stage = ToolStage()
    stage.start("Running")
    stage.error("Failed")
    assert stage.status == "error"

    stage.reset()
    assert stage.status == "idle"
    assert stage.message is None


def test_stage_repr_shows_status_and_message():
    stage = ToolStage()
    stage.start("Running")
    repr_str = repr(stage)
    assert "status=running" in repr_str
    assert "Running" in repr_str
