# SciOS Execution Graph

## Overview

The Execution Graph defines how stages within the SciOS Cognitive Pipeline are connected and executed.

Rather than embedding execution order directly into the pipeline implementation, the Execution Graph represents stage dependencies as a graph structure. This design enables validation, scheduling, optimization, and future support for parallel execution.

In the current SciOS implementation, the default execution model is sequential. The Execution Graph provides the abstraction layer that will evolve toward Directed Acyclic Graph (DAG) execution in future releases.

---

# Objectives

The Execution Graph is designed to:

* Represent dependencies between stages
* Validate execution order
* Detect invalid pipeline structures
* Support future parallel execution
* Enable conditional execution
* Separate execution logic from cognitive logic
* Provide a foundation for runtime scheduling

---

# Architecture

```text
                     Execution Graph
                            │
      ┌─────────────────────┼─────────────────────┐
      │                     │                     │
   Graph Builder      Graph Validator      Graph Scheduler
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            │
                    Stage Dependency Graph
                            │
                            ▼
                     Runtime Execution
```

---

# Position within SciOS

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
Execution Graph
   │
   ▼
Stage Dispatcher
   │
   ▼
Stage Execution
```

The Execution Graph determines **which stage may execute next**. The Dispatcher performs the actual invocation.

---

# Core Responsibilities

The Execution Graph is responsible for:

* Registering stage nodes
* Creating dependency edges
* Computing execution order
* Detecting dependency cycles
* Validating graph integrity
* Supporting execution scheduling
* Providing traversal operations

The graph does not execute cognitive logic.

---

# Graph Model

The graph consists of:

* Nodes
* Directed edges
* Entry node
* Exit node

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

Each node represents one pipeline stage.

---

# Graph Nodes

A node contains:

* Stage identifier
* Stage instance
* Input dependencies
* Output connections
* Execution metadata

Example conceptual structure:

```python
class GraphNode:
    stage
    parents
    children
```

---

# Graph Edges

An edge represents a dependency.

```text
Memory ─────────► Reasoning
```

Meaning:

* Reasoning cannot execute
* until Memory completes successfully.

---

# Sequential Execution

The default execution graph is linear.

```text
Input
   │
   ▼
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
   │
   ▼
Output
```

This execution order guarantees deterministic processing.

---

# Future DAG Execution

Future versions of SciOS will support Directed Acyclic Graph execution.

Example:

```text
                 Memory
                /      \
               ▼        ▼
      Knowledge     Episodic
             \        /
              ▼      ▼
             Reasoning
                  │
                  ▼
              Planning
```

Independent branches may execute concurrently.

---

# Dependency Validation

Before execution begins, the graph validates:

* Missing stages
* Duplicate stage identifiers
* Invalid dependencies
* Circular references
* Unreachable nodes

Execution starts only after successful validation.

---

# Cycle Detection

Cycles are prohibited.

Invalid example:

```text
Memory
   │
   ▼
Reasoning
   │
   ▼
Planning
   ▲
   │
Memory
```

Such graphs are rejected during validation.

---

# Topological Ordering

For DAG execution, stages are ordered using topological sorting.

Example:

```text
Input

↓

Perception

↓

Memory

↓

Reasoning

↓

Planning

↓

Reflection
```

A valid topological order guarantees that every dependency executes before its consumers.

---

# Runtime Integration

The Runtime queries the Execution Graph to determine executable stages.

```text
Runtime
    │
    ▼
Execution Graph
    │
    ▼
Ready Stage
    │
    ▼
Dispatcher
```

The graph does not execute stages directly.

---

# Pipeline Builder Integration

The Pipeline Builder creates both the pipeline and its execution graph.

```text
Pipeline Builder
       │
       ├── Register Stage
       ├── Register Dependency
       └── Build Graph
```

Different builders may produce different execution graphs for different workloads.

---

# Scheduler Integration

The Scheduler uses the Execution Graph to determine execution readiness.

Responsibilities include:

* Finding executable nodes
* Waiting for dependencies
* Prioritizing ready stages
* Supporting future parallel scheduling

---

# Context Flow

The Pipeline Context flows along graph edges.

```text
Context
    │
    ▼
Perception
    │
    ▼
Memory
    │
    ▼
Reasoning
```

Each stage receives the updated context produced by its predecessors.

---

# Execution States

Each graph node progresses through a lifecycle.

```text
Pending

↓

Ready

↓

Running

↓

Completed
```

Possible failure state:

```text
Running

↓

Failed
```

The Runtime may retry or terminate execution depending on policy.

---

# Error Handling

Execution Graph errors include:

* Invalid dependency
* Missing stage
* Duplicate node
* Circular dependency
* Unreachable node
* Invalid execution order

These errors are detected before runtime whenever possible.

---

# Extensibility

The Execution Graph is designed for future capabilities such as:

* Conditional execution
* Branching pipelines
* Parallel execution
* Distributed execution
* GPU scheduling
* Multi-agent coordination
* Dynamic graph modification

These extensions require no changes to the Cognitive Pipeline interface.

---

# Design Principles

The Execution Graph follows these principles:

* Graph-driven execution
* Deterministic scheduling
* Dependency-first validation
* Separation of orchestration and execution
* Extensible graph model
* Runtime independence
* Support for scalable cognitive workflows

---

# Related Documentation

* `architecture.md`
* `kernel.md`
* `runtime.md`
* `pipeline.md`
* `builder.md`
* `contracts.md`
* `scheduler.md`
* `configuration.md`

---

# Summary

The Execution Graph is the dependency model of the SciOS Cognitive Pipeline.

It represents stage relationships, validates execution order, enables deterministic scheduling, and provides the architectural foundation for future DAG-based, parallel, and distributed cognitive execution. By separating dependency management from stage implementation, the Execution Graph ensures that SciOS remains modular, extensible, and suitable for large-scale cognitive systems.
