# SciOS Pipeline Builder

## Overview

The Pipeline Builder is responsible for constructing and configuring the **Cognitive Pipeline** used by the SciOS Kernel.

Rather than embedding pipeline construction inside the Kernel or Bootstrap, SciOS delegates this responsibility to the Pipeline Builder. This follows the **Composition Root** pattern, keeping subsystem initialization separate from cognitive orchestration.

The Pipeline Builder assembles pipeline stages, validates the composition, constructs the execution graph, and returns a fully configured `CognitivePipeline`.

---

# Objectives

The Pipeline Builder is designed to:

* Construct Cognitive Pipelines
* Register cognitive stages
* Configure execution order
* Build the Execution Graph
* Validate pipeline composition
* Support multiple pipeline profiles
* Reduce coupling between Kernel and Cognitive Core

---

# Position in the Architecture

```text
                    SciOS Kernel
                          │
                          ▼
                  Pipeline Builder
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
 Register Stages   Build Execution Graph   Validate
      │                   │                   │
      └───────────────────┼───────────────────┘
                          ▼
                 Cognitive Pipeline
```

The Builder creates the pipeline. The Kernel owns and executes it.

---

# Responsibilities

The Pipeline Builder performs the following tasks:

* Create a new pipeline instance
* Register stage handlers
* Define execution order
* Connect stage dependencies
* Construct the Execution Graph
* Validate the pipeline
* Return a ready-to-run pipeline

The Builder does **not** execute any cognitive logic.

---

# Why Pipeline Builder?

Without a Builder:

```text
Kernel
 ├── Create Pipeline
 ├── Create Memory
 ├── Create Reasoning
 ├── Create Planning
 ├── Register Stages
 ├── Validate
 └── Execute
```

The Kernel becomes tightly coupled to every cognitive subsystem.

With a Builder:

```text
Kernel
    │
    ▼
Pipeline Builder
    │
    ▼
Cognitive Pipeline
```

The Kernel only requests a pipeline and remains independent of its internal composition.

---

# Composition Root

The Pipeline Builder acts as the Composition Root of the Cognitive Core.

```text
Bootstrap
     │
     ▼
Kernel
     │
     ▼
Pipeline Builder
     │
     ▼
Create Subsystems
     │
     ▼
Build Pipeline
```

This ensures that object creation is centralized and maintainable.

---

# Default Pipeline

The default SciOS pipeline consists of:

```text
Perception
      │
      ▼
Memory
      │
      ▼
Reasoning
      │
      ▼
Planning
      │
      ▼
Tool Use
      │
      ▼
Reflection
      │
      ▼
Memory Update
```

The Builder assembles these stages in the correct order.

---

# Build Process

Pipeline construction follows these steps:

```text
Create Pipeline
        │
        ▼
Register Stages
        │
        ▼
Create Execution Graph
        │
        ▼
Validate Pipeline
        │
        ▼
Return Pipeline
```

The pipeline is not executed during construction.

---

# Stage Registration

Each stage is added through the generic `Stage` abstraction.

Conceptually:

```python
pipeline.add_stage(Stage("memory", memory_manager))
pipeline.add_stage(Stage("reasoning", reasoning_engine))
pipeline.add_stage(Stage("planning", planner))
pipeline.add_stage(Stage("tool_use", tool_executor))
pipeline.add_stage(Stage("reflection", reflection_engine))
```

This allows any subsystem implementing the expected processing interface to participate in the pipeline.

---

# Execution Graph Construction

The Builder also creates stage dependencies.

Example:

```text
Memory
   │
   ▼
Reasoning
   │
   ▼
Planning
```

These relationships are stored inside the Execution Graph.

---

# Validation

Before returning the pipeline, the Builder validates:

* Stage uniqueness
* Required stages
* Dependency correctness
* Execution graph integrity
* Pipeline contracts

Invalid pipelines are rejected before runtime.

---

# Multiple Pipeline Profiles

Different workloads may require different pipeline compositions.

Examples include:

```text
Scientific Pipeline

Perception
↓

Memory
↓

Reasoning
↓

Simulation
↓

Planning
↓

Reflection
```

```text
Agent Pipeline

Perception
↓

Memory
↓

Reasoning
↓

Tool Use
↓

Reflection
```

```text
Evaluation Pipeline

Input
↓

Reasoning
↓

Reflection
↓

Report
```

The Kernel remains unchanged regardless of the selected profile.

---

# Configuration-Driven Construction

Pipeline composition may be defined through configuration.

Example:

```yaml
pipeline:
  stages:
    - perception
    - memory
    - reasoning
    - planning
    - tool_use
    - reflection
```

The Builder interprets this configuration and constructs the corresponding pipeline.

---

# Kernel Integration

The Kernel delegates pipeline creation to the Builder.

```text
Kernel
    │
    ▼
Pipeline Builder
    │
    ▼
Cognitive Pipeline
    │
    ▼
Runtime
```

This separation keeps the Kernel focused on lifecycle management.

---

# Runtime Integration

The Runtime executes the pipeline produced by the Builder.

```text
Pipeline Builder
        │
        ▼
Cognitive Pipeline
        │
        ▼
Runtime Execution
```

Construction and execution remain independent.

---

# Extensibility

New cognitive stages can be introduced without modifying the Kernel.

Possible extensions include:

* Knowledge Retrieval
* Simulation
* Collaboration
* Verification
* Optimization
* Multi-Agent Coordination

Only the Builder requires updates to include the new stages.

---

# Future Builder Types

SciOS may provide specialized builders such as:

* `DefaultPipelineBuilder`
* `ScientificPipelineBuilder`
* `ResearchPipelineBuilder`
* `DistributedPipelineBuilder`
* `EdgePipelineBuilder`
* `EvaluationPipelineBuilder`

Each builder assembles a pipeline tailored to a specific execution scenario.

---

# Design Principles

The Pipeline Builder follows these principles:

* Single Responsibility
* Composition over inheritance
* Dependency Injection
* Configuration-driven assembly
* Loose coupling
* Extensible architecture
* Validation before execution

---

# Related Documentation

* `architecture.md`
* `kernel.md`
* `pipeline.md`
* `execution_graph.md`
* `contracts.md`
* `configuration.md`
* `runtime.md`

---

# Summary

The Pipeline Builder is the composition engine of the SciOS Cognitive Core.

It constructs the `CognitivePipeline`, registers cognitive stages, builds the Execution Graph, validates pipeline integrity, and returns a ready-to-execute workflow. By separating pipeline construction from execution, the Builder enables modular design, multiple execution profiles, and long-term extensibility while keeping the Kernel lightweight and maintainable.
