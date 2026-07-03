"""
SciOS Substrate
===============

Computational substrate of the Scientific Cognitive Operating
System (SciOS).

The Substrate provides the low-level computational foundation
for the entire system, including tensor abstraction, memory
management, vector storage, and qualitative temporal calculus
(QTC).

Architecture
------------
Substrate
├── Tensor abstraction
├── Memory management
├── Vector storage
└── Qualitative Temporal Calculus (QTC)

Public API
----------
SciOSTensor
    Unified tensor abstraction independent of the underlying
    numerical backend.

MemoryManager
    Low-level memory allocation and resource manager.
"""

from .tensor import SciOSTensor
from .memory import MemoryManager

__all__ = [
    "SciOSTensor",
    "MemoryManager",
]