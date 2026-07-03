# SciOS

> **Scientific Cognitive Operating System**

SciOS is an experimental operating system architecture for autonomous scientific intelligence.

Unlike traditional AI frameworks, SciOS is designed as a **cognitive operating system** with a microkernel architecture where reasoning, memory, planning, execution, and autonomous scientific agents operate as coordinated subsystems.

---

# Vision

SciOS aims to become a general cognitive infrastructure for:

- Autonomous Scientific Discovery
- Cognitive Computing
- Scientific AI
- Distributed AI Systems
- Planetary-scale AI Runtime
- AI Operating Systems

---

# Core Architecture

```
SciOS
│
├── API
├── Kernel
│   ├── Bootstrap
│   ├── Lifecycle
│   ├── Runtime
│   ├── Scheduler
│   ├── Registry
│   ├── EventBus
│   └── Context
│
├── Agents
│   ├── Memory
│   ├── Reasoning
│   ├── Planner
│   ├── Reflection
│   ├── Collaboration
│   └── ToolUse
│
├── Runtime
├── Substrate
├── Infrastructure
└── Applications
```

---

# Current Status

Current development milestone:

**SciOS Boot Kernel v0.2**

Implemented:

- Boot sequence
- Shutdown sequence
- Runtime engine
- Scheduler
- Component registry
- Event bus
- Execution context
- Agent executor
- Semantic memory
- Reasoning engine
- CLI application
- Boot integration tests

Current test status:

```
12 Boot Tests Passed
```

---

# Installation

Clone the repository

```bash
git clone <repository-url>

cd SciOS
```

Install in editable mode

```bash
pip install -e .
```

---

# Quick Start

Create a SciOS instance

```python
from scios import SciOS

os = SciOS()

os.boot()

result = os.run("Analyze this system")

print(result)

os.shutdown()
```

---

# Run Tests

```bash
pytest
```

or

```bash
pytest -v
```

---

# Project Structure

```
SciOS/
│
├── apps/
├── benchmarks/
├── docs/
├── examples/
├── scripts/
├── tests/
│
├── scios/
│   ├── api/
│   ├── agents/
│   ├── kernel/
│   ├── runtime/
│   ├── substrate/
│   └── shared/
│
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

---

# Development Roadmap

## Version 0.2

- Boot Kernel
- Runtime
- Scheduler
- Registry
- Event Bus
- Context
- Agent Executor

## Version 0.3

- Long-Term Memory
- Planning Engine
- Reflection Engine
- Tool Execution

## Version 0.4

- Distributed Runtime
- Remote Nodes
- Resource Scheduling
- Fault Recovery

## Version 0.5

- GPU Runtime
- High Performance Tensor Backend
- Scientific Computing Pipeline

## Version 1.0

- Autonomous Scientific Agent
- Planetary Cognitive Operating System
- Scientific Discovery Platform

---

# Design Principles

SciOS follows several architectural principles.

- Microkernel architecture
- Component isolation
- Modular reasoning
- Explicit lifecycle management
- Typed public APIs
- Autonomous cognition
- Extensible execution pipeline

---

# License

SciOS is released under the MIT License.

See the LICENSE file for details.

---

# Author

**Bui Dinh Hoang**

Scientific Cognitive Operating System (SciOS)

2026