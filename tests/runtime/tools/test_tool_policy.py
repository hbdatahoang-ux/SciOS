"""
ToolPolicy tests
"""

from scios.runtime.tools import ToolPolicy



def test_default_policy():

    policy = ToolPolicy()


    assert policy.enabled is True



def test_disable_policy():

    policy = ToolPolicy()


    policy.disable()


    assert policy.enabled is False



def test_allow_check():

    policy = ToolPolicy()


    assert policy.allow(
        "echo"
    )