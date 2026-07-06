# tests/test_goal.py

import pytest
from scios.cognitive_core.planner.goal import Goal

def test_goal_initialization():
    goal = Goal(description="Increase sales")
    assert goal.description == "Increase sales"
    assert goal.success_criteria == []

def test_add_success_criterion():
    goal = Goal(description="Improve customer satisfaction")
    goal.add_success_criterion("Survey score > 80%")
    assert "Survey score > 80%" in goal.success_criteria
    assert len(goal.success_criteria) == 1

def test_is_successful_with_criteria():
    goal = Goal(description="Launch new product")
    goal.add_success_criterion("Product released")
    # Skeleton: giả định criterion được thỏa mãn
    context = {"Product released": True}
    assert goal.is_successful(context) is True

def test_is_successful_without_criteria():
    goal = Goal(description="Generic goal")
    # Không có success criteria → mặc định coi là thành công
    context = {}
    assert goal.is_successful(context) is True
