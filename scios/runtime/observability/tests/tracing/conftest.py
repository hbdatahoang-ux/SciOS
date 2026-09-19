"""
Pytest configuration for tracing tests.
"""

pytest_plugins = [
    "scios.runtime.observability.tests.tracing.fixtures",
]
