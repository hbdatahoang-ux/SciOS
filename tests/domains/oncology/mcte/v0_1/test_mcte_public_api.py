"""
Tests for the MCTE v0.1 public API.
"""

import importlib


MODULE_NAME = "scios.domains.oncology.mcte.v0_1"


EXPECTED_PUBLIC_API = {
    "PhenotypeState",
    "PHENOTYPES",
    "STATE_DIMENSION",
    "EnvironmentState",
    "HostState",
    "BaseFitnessModel",
    "ToyLinearFitnessModel",
    "compute_system_derivatives",
    "Intervention",
    "ControlPolicy",
    "BaseControlPolicy",
    "ConstantControlPolicy",
    "MetronomicControlPolicy",
    "EvaluationMetrics",
    "compute_step_metrics",
    "SimulationResult",
    "SimulationEngine",
}


def test_public_api_matches_expected_contract():
    module = importlib.import_module(MODULE_NAME)

    assert set(module.__all__) == EXPECTED_PUBLIC_API


def test_public_api_contains_no_duplicates():
    module = importlib.import_module(MODULE_NAME)

    assert len(module.__all__) == len(set(module.__all__))


def test_all_public_symbols_are_exposed():
    module = importlib.import_module(MODULE_NAME)

    for name in module.__all__:
        assert hasattr(module, name), (
            f"Public API symbol {name!r} is missing."
        )


def test_public_symbols_are_importable():
    module = importlib.import_module(MODULE_NAME)

    for name in module.__all__:
        namespace = {}
        exec(
            f"from {MODULE_NAME} import {name}",
            namespace,
        )

        assert name in namespace
        assert namespace[name] is getattr(module, name)


def test_star_import_matches_public_api():
    module = importlib.import_module(MODULE_NAME)

    namespace = {}
    exec(
        f"from {MODULE_NAME} import *",
        namespace,
    )

    exported = {
        name
        for name in namespace
        if name != "__builtins__"
    }

    assert exported == EXPECTED_PUBLIC_API


def test_public_api_is_explicit():
    module = importlib.import_module(MODULE_NAME)

    assert isinstance(module.__all__, list)
    assert all(
        isinstance(name, str)
        for name in module.__all__
    )


def test_public_api_preserves_expected_order():
    module = importlib.import_module(MODULE_NAME)

    expected_order = [
        "PhenotypeState",
        "PHENOTYPES",
        "STATE_DIMENSION",
        "EnvironmentState",
        "HostState",
        "BaseFitnessModel",
        "ToyLinearFitnessModel",
        "compute_system_derivatives",
        "Intervention",
        "ControlPolicy",
        "BaseControlPolicy",
        "ConstantControlPolicy",
        "MetronomicControlPolicy",
        "EvaluationMetrics",
        "compute_step_metrics",
        "SimulationResult",
        "SimulationEngine",
    ]

    assert module.__all__ == expected_order