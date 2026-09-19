from pathlib import Path

from scios.shared.config import (
    AgentConfig,
    KernelConfig,
    LoggingConfig,
    MemoryConfig,
    QTCConfig,
    RuntimeConfig,
    SciOSConfig,
    SystemConfig,
    VectorStoreConfig,
    config,
)


# ============================================================================
# Public API
# ============================================================================


def test_config_public_api():
    assert SystemConfig is not None
    assert RuntimeConfig is not None
    assert KernelConfig is not None
    assert AgentConfig is not None
    assert MemoryConfig is not None
    assert VectorStoreConfig is not None
    assert QTCConfig is not None
    assert LoggingConfig is not None
    assert SciOSConfig is not None
    assert config is not None


# ============================================================================
# Default configuration
# ============================================================================


def test_system_config_defaults():
    cfg = SystemConfig()

    assert cfg.app_name == "SciOS"
    assert cfg.organization == "SciOS Project"
    assert cfg.version == "0.1.3"
    assert cfg.debug is False
    assert isinstance(cfg.root, Path)


def test_runtime_config_defaults():
    cfg = RuntimeConfig()

    assert cfg.workers == 4
    assert cfg.scheduler == "fifo"
    assert cfg.task_timeout == 300.0
    assert cfg.enable_async is False


def test_kernel_config_defaults():
    cfg = KernelConfig()

    assert cfg.auto_boot is True
    assert cfg.auto_shutdown is True
    assert cfg.lifecycle_checks is True


def test_agent_config_defaults():
    cfg = AgentConfig()

    assert cfg.planner_enabled is True
    assert cfg.reflection_enabled is True
    assert cfg.collaboration_enabled is True
    assert cfg.tool_use_enabled is True


def test_memory_config_defaults():
    cfg = MemoryConfig()

    assert cfg.working_capacity == 512
    assert cfg.semantic_capacity == 10_000
    assert cfg.episodic_capacity == 5_000
    assert cfg.longterm_capacity == 100_000
    assert cfg.enable_cache is True


def test_vectorstore_config_defaults():
    cfg = VectorStoreConfig()

    assert cfg.backend == "flat"
    assert cfg.dimension == 768
    assert cfg.similarity == "cosine"
    assert cfg.index_path == Path("vectorstore")


def test_qtc_config_defaults():
    cfg = QTCConfig()

    assert cfg.enable_compression is True
    assert cfg.verify_reasoning is True
    assert cfg.symbolic_backend == "native"


def test_logging_config_defaults():
    cfg = LoggingConfig()

    assert cfg.level == "INFO"
    assert cfg.console is True
    assert cfg.file is False
    assert cfg.directory == Path("logs")


# ============================================================================
# Root configuration
# ============================================================================


def test_scios_config_creates_all_subsystems():
    cfg = SciOSConfig()

    assert isinstance(cfg.system, SystemConfig)
    assert isinstance(cfg.runtime, RuntimeConfig)
    assert isinstance(cfg.kernel, KernelConfig)
    assert isinstance(cfg.agents, AgentConfig)
    assert isinstance(cfg.memory, MemoryConfig)
    assert isinstance(cfg.vectorstore, VectorStoreConfig)
    assert isinstance(cfg.qtc, QTCConfig)
    assert isinstance(cfg.logging, LoggingConfig)


def test_global_config_is_scios_config():
    assert isinstance(config, SciOSConfig)


def test_nested_default_objects_are_independent():
    first = SciOSConfig()
    second = SciOSConfig()

    assert first.system is not second.system
    assert first.runtime is not second.runtime
    assert first.kernel is not second.kernel
    assert first.agents is not second.agents
    assert first.memory is not second.memory
    assert first.vectorstore is not second.vectorstore
    assert first.qtc is not second.qtc
    assert first.logging is not second.logging


# ============================================================================
# Slots
# ============================================================================


def test_configuration_classes_use_slots():
    classes = (
        SystemConfig,
        RuntimeConfig,
        KernelConfig,
        AgentConfig,
        MemoryConfig,
        VectorStoreConfig,
        QTCConfig,
        LoggingConfig,
        SciOSConfig,
    )

    for cls in classes:
        assert hasattr(cls, "__slots__")


# ============================================================================
# Serialization
# ============================================================================


def test_to_dict_returns_dictionary():
    cfg = SciOSConfig()

    result = cfg.to_dict()

    assert isinstance(result, dict)
    assert set(result) == {
        "system",
        "runtime",
        "kernel",
        "agents",
        "memory",
        "vectorstore",
        "qtc",
        "logging",
    }


def test_to_dict_contains_expected_values():
    cfg = SciOSConfig()

    result = cfg.to_dict()

    assert result["system"]["app_name"] == "SciOS"
    assert result["runtime"]["workers"] == 4
    assert result["kernel"]["auto_boot"] is True
    assert result["agents"]["planner_enabled"] is True
    assert result["memory"]["working_capacity"] == 512
    assert result["vectorstore"]["backend"] == "flat"
    assert result["qtc"]["symbolic_backend"] == "native"
    assert result["logging"]["level"] == "INFO"


def test_to_dict_converts_paths_to_strings():
    cfg = SciOSConfig()

    result = cfg.to_dict()

    assert isinstance(result["system"]["root"], str)
    assert isinstance(result["vectorstore"]["index_path"], str)
    assert isinstance(result["logging"]["directory"], str)


# ============================================================================
# from_dict
# ============================================================================


def test_from_dict_restores_configuration():
    values = {
        "system": {
            "app_name": "SciOS-Test",
            "organization": "Test Organization",
            "version": "9.9.9",
            "debug": True,
            "root": "D:/scios-test",
        },
        "runtime": {
            "workers": 8,
            "scheduler": "priority",
            "task_timeout": 120.0,
            "enable_async": True,
        },
        "kernel": {
            "auto_boot": False,
            "auto_shutdown": True,
            "lifecycle_checks": False,
        },
        "agents": {
            "planner_enabled": False,
            "reflection_enabled": True,
            "collaboration_enabled": False,
            "tool_use_enabled": True,
        },
        "memory": {
            "working_capacity": 100,
            "semantic_capacity": 200,
            "episodic_capacity": 300,
            "longterm_capacity": 400,
            "enable_cache": False,
        },
        "vectorstore": {
            "backend": "hnsw",
            "dimension": 1536,
            "similarity": "l2",
            "index_path": "D:/vectors",
        },
        "qtc": {
            "enable_compression": False,
            "verify_reasoning": True,
            "symbolic_backend": "symbolic",
        },
        "logging": {
            "level": "DEBUG",
            "console": False,
            "file": True,
            "directory": "D:/logs",
        },
    }

    cfg = SciOSConfig.from_dict(values)

    assert cfg.system.app_name == "SciOS-Test"
    assert cfg.system.debug is True
    assert cfg.system.root == Path("D:/scios-test")

    assert cfg.runtime.workers == 8
    assert cfg.runtime.scheduler == "priority"
    assert cfg.runtime.enable_async is True

    assert cfg.kernel.auto_boot is False

    assert cfg.agents.planner_enabled is False
    assert cfg.agents.collaboration_enabled is False

    assert cfg.memory.working_capacity == 100
    assert cfg.memory.enable_cache is False

    assert cfg.vectorstore.backend == "hnsw"
    assert cfg.vectorstore.dimension == 1536
    assert cfg.vectorstore.index_path == Path("D:/vectors")

    assert cfg.qtc.enable_compression is False
    assert cfg.qtc.symbolic_backend == "symbolic"

    assert cfg.logging.level == "DEBUG"
    assert cfg.logging.file is True
    assert cfg.logging.directory == Path("D:/logs")


def test_from_dict_accepts_partial_configuration():
    cfg = SciOSConfig.from_dict(
        {
            "runtime": {
                "workers": 12,
                "scheduler": "fifo",
                "task_timeout": 60.0,
                "enable_async": True,
            }
        }
    )

    assert cfg.runtime.workers == 12
    assert cfg.runtime.task_timeout == 60.0
    assert cfg.runtime.enable_async is True

    assert cfg.system.app_name == "SciOS"
    assert cfg.kernel.auto_boot is True
    assert cfg.memory.working_capacity == 512


def test_from_dict_rejects_non_dictionary():
    try:
        SciOSConfig.from_dict(None)
    except TypeError:
        pass
    else:
        raise AssertionError(
            "SciOSConfig.from_dict() must reject non-dict input"
        )


# ============================================================================
# Round-trip
# ============================================================================


def test_configuration_round_trip():
    original = SciOSConfig()

    original.system.debug = True
    original.runtime.workers = 16
    original.vectorstore.dimension = 1536
    original.logging.file = True

    serialized = original.to_dict()
    restored = SciOSConfig.from_dict(serialized)

    assert restored.system.debug is True
    assert restored.runtime.workers == 16
    assert restored.vectorstore.dimension == 1536
    assert restored.logging.file is True

    assert restored.system.root == original.system.root
    assert restored.vectorstore.index_path == original.vectorstore.index_path
    assert restored.logging.directory == original.logging.directory


# ============================================================================
# Copy
# ============================================================================


def test_copy_returns_independent_configuration():
    original = SciOSConfig()

    copied = original.copy()

    assert isinstance(copied, SciOSConfig)
    assert copied is not original


def test_copy_does_not_share_nested_objects():
    original = SciOSConfig()
    copied = original.copy()

    assert copied.system is not original.system
    assert copied.runtime is not original.runtime
    assert copied.kernel is not original.kernel
    assert copied.agents is not original.agents
    assert copied.memory is not original.memory
    assert copied.vectorstore is not original.vectorstore
    assert copied.qtc is not original.qtc
    assert copied.logging is not original.logging


def test_copy_is_independent_after_mutation():
    original = SciOSConfig()
    copied = original.copy()

    copied.system.debug = True
    copied.runtime.workers = 99
    copied.memory.working_capacity = 999

    assert original.system.debug is False
    assert original.runtime.workers == 4
    assert original.memory.working_capacity == 512


# ============================================================================
# Representation
# ============================================================================


def test_repr_contains_version_and_debug():
    cfg = SciOSConfig()

    text = repr(cfg)

    assert "SciOSConfig" in text
    assert "0.1.3" in text
    assert "False" in text
