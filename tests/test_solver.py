from scios.cognitive_core.reasoning.solver import ProblemSolver

def test_solver_applies_rules_and_inference():
    solver = ProblemSolver()
    problem = {"condition": "rain", "goal": "stay dry"}
    result = solver.solve(problem)

    # Kết quả phải là list
    assert isinstance(result, list)
    # Có thể chứa rule áp dụng hoặc inference
    assert any("Rule applied" in r or "Inferred" in r for r in result)

def test_solver_reset_clears_state():
    solver = ProblemSolver()
    solver.solve({"condition": "test"})
    solver.reset()
    # Sau reset, rulebase và engine phải trống
    assert solver.rulebase.get_rules() == []
