from enum import Enum


class Opcode(Enum):
    """
    Opcode = Instruction Set Architecture (ISA) for ExecutionGraph.
    Each opcode represents a standardized action.
    """

    # Node operations
    ADD_NODE = "add_node"
    REMOVE_NODE = "remove_node"
    UPDATE_NODE = "update_node"

    # Edge operations
    ADD_EDGE = "add_edge"
    REMOVE_EDGE = "remove_edge"
    UPDATE_EDGE = "update_edge"

    # Metadata operations
    UPDATE_METADATA = "update_metadata"
    CLEAR_METADATA = "clear_metadata"

    # Graph operations
    COMMIT_REVISION = "commit_revision"
    ROLLBACK_REVISION = "rollback_revision"
    APPLY_CHANGESET = "apply_changeset"

    # Execution operations
    START_NODE = "start_node"
    COMPLETE_NODE = "complete_node"
    FAIL_NODE = "fail_node"
    RETRY_NODE = "retry_node"
    CANCEL_NODE = "cancel_node"

    # Analysis operations
    TOPO_SORT = "topological_sort"
    DETECT_CYCLE = "detect_cycle"
    CRITICAL_PATH = "critical_path"
