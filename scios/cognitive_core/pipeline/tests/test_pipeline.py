"""
SciOS Cognitive Pipeline Tests

Author: Bui Dinh Hoang
License: Apache-2.0
"""

import pytest

from scios.cognitive_core.pipeline.pipeline import CognitivePipeline
from scios.cognitive_core.pipeline.context import PipelineContext


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def pipeline():
    return CognitivePipeline()


@pytest.fixture
def context():
    return PipelineContext(input_data="Hello SciOS")


# ============================================================
# Initialization
# ============================================================

def test_pipeline_initialization(pipeline):
    assert pipeline is not None


def test_pipeline_has_registry(pipeline):
    assert hasattr(pipeline, "registry")


def test_pipeline_has_dispatcher(pipeline):
    assert hasattr(pipeline, "dispatcher")


def test_pipeline_has_graph(pipeline):
    assert hasattr(pipeline, "graph")


# ============================================================
# Context
# ============================================================

def test_context_creation(context):
    assert context is not None
    assert context.input_data == "Hello SciOS"


# ============================================================
# Stage Registration
# ============================================================

def test_register_stage(pipeline):

    class DummyStage:
        name = "dummy"

    pipeline.registry.register(DummyStage())

    assert pipeline.registry.exists("dummy")


# ============================================================
# Pipeline Execution
# ============================================================

def test_pipeline_execute(pipeline, context):
    result = pipeline.run(context)

    assert result is not None


def test_pipeline_returns_context(pipeline, context):
    result = pipeline.run(context)

    assert isinstance(result, PipelineContext)


# ============================================================
# Empty Pipeline
# ============================================================

def test_empty_pipeline(pipeline, context):
    pipeline.registry.clear()

    result = pipeline.run(context)

    assert result is context


# ============================================================
# Error Handling
# ============================================================

def test_invalid_stage_registration(pipeline):

    with pytest.raises(Exception):
        pipeline.registry.register(None)


# ============================================================
# Execution Graph
# ============================================================

def test_graph_exists(pipeline):
    assert pipeline.graph is not None


def test_dispatcher_exists(pipeline):
    assert pipeline.dispatcher is not None


# ============================================================
# Configuration
# ============================================================

def test_pipeline_has_config(pipeline):
    assert pipeline.config is not None


# ============================================================
# Runtime State
# ============================================================

def test_pipeline_state(pipeline):
    assert pipeline.state is not None


# ============================================================
# Smoke Test
# ============================================================

def test_pipeline_smoke():

    pipeline = CognitivePipeline()

    context = PipelineContext(
        input_data="SciOS Pipeline"
    )

    result = pipeline.run(context)

    assert result is not None
