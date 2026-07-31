from scios.runtime.agent.planner import Planner


def test_planner_create_plan():

    planner = Planner()

    plan = planner.plan(
        "build tool"
    )

    assert plan is not None