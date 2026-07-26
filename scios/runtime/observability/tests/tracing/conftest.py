"""
Pytest configuration for tracing tests.

This module automatically registers all tracing fixtures
for every test under this package.
"""

pytest_plugins = [
    "scios.runtime.observability.tests.tracing.fixtures",
]