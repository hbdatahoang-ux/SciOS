"""
End-to-end tests for SciOS reasoning pipeline
"""

from scios.cognitive_core.reasoning import ReasoningStage, ProblemSolver, ReasoningEngine


def test_pipeline_stage_to_solver_to_engine():
    # Stage tạo plan và inference
    stage = ReasoningStage()
    query = "How to stay dry in rain?"
    context = {"condition": "rain", "goal": "stay dry"}
    stage_result = stage.run(query, context)

    assert stage_result["stage"] == "ReasoningStage"
    assert "plan" in stage_result
    assert "inference" in stage_result

    # Solver áp dụng rule và inference
    solver = ProblemSolver()
    solver_result = solver.solve(context)

    assert isinstance(solver_result, list)
    assert any("Rule applied" in r or "Inferred" in r for r in solver_result)

    # Engine thực hiện inference và goal reasoning
    engine = ReasoningEngine()
    engine.add_rule("rain", "carry umbrella")
    engine_result = engine.infer(context)

    assert "carry umbrella" in engine_result

    goal_result = engine.reason_about_goal({"event": "exam", "requirements": []})
    assert isinstance(goal_result, list)


def test_pipeline_reset_and_status():
    stage = ReasoningStage()
    solver = ProblemSolver()
    engine = ReasoningEngine()

    stage.run("Test query", {"condition": "rain"})
    solver.solve({"condition": "rain"})
    engine.add_rule("rain", "carry umbrella")

    # Reset tất cả
    stage.reset()
    solver.reset()
    engine.reset()

    assert stage.status()["records"] == 0
    assert solver.rulebase.get_rules() == []
    assert engine.rules == []
