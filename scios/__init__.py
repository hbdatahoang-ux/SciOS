"""
SciOS
=====

Scientific Cognitive Operating System

Public API
----------

Example
-------
>>> from scios import SciOS

>>> os = SciOS()
>>> os.boot()
>>> os.run("analyze this system")
"""

from .api.scios import SciOS

__all__ = ["SciOS"]

__version__ = "0.1.2"
__author__ = "Bui Dinh Hoang"