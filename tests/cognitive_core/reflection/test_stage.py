from scios.cognitive_core.reflection.stage import ReflectionStage


def test_reflection_stage_values():
    assert ReflectionStage.INITIALIZED.value == "initialized"
    assert ReflectionStage.EVALUATION.value == "evaluation"
    assert ReflectionStage.CRITIQUE.value == "critique"
    assert ReflectionStage.ANALYSIS.value == "analysis"
    assert ReflectionStage.METRICS.value == "metrics"
    assert ReflectionStage.SCORING.value == "scoring"
    assert ReflectionStage.SCORE.value == "score"
    assert ReflectionStage.IMPROVEMENT.value == "improvement"
    assert ReflectionStage.FEEDBACK.value == "feedback"
    assert ReflectionStage.REPORT.value == "report"
    assert ReflectionStage.SELF_REVIEW.value == "self_review"
    assert ReflectionStage.VALIDATION.value == "validation"
    assert ReflectionStage.ADAPTIVE.value == "adaptive"
    assert ReflectionStage.COMPLETED.value == "completed"


def test_scoring_is_canonical_and_score_is_compatibility():
    assert ReflectionStage.SCORING.value == "scoring"
    assert ReflectionStage.SCORE.value == "score"
    assert ReflectionStage.SCORING is not ReflectionStage.SCORE


def test_reflection_stage_string_representation():
    assert str(ReflectionStage.SCORING) == "scoring"
    assert str(ReflectionStage.SCORE) == "score"
