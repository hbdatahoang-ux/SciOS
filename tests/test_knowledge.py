import pytest
from scios.cognitive_core.pipeline.pipeline import CognitivePipeline
from scios.cognitive_core.knowledge.knowledge import KnowledgeStage

def test_knowledge_stage_runs():
    pipeline = CognitivePipeline([KnowledgeStage()])
    result = pipeline.run("What is AI?")
    assert result is not None
    assert "knowledge" in result
    assert "output" in result["knowledge"]
    assert "AI" in result["knowledge"]["output"]

def test_knowledge_multiple_calls():
    pipeline = CognitivePipeline([KnowledgeStage()])
    outputs = []
    for query in ["Python", "Machine Learning", "Neural Networks"]:
        outputs.append(pipeline.run(query)["knowledge"]["output"])
    assert all("retrieved knowledge" in o for o in outputs)
