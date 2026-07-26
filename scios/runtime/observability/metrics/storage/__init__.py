"""
SciOS-NG Runtime Metrics Storage

Public API for Metrics Storage subsystem.

SciOS-NG v0.2
"""


# ==============================================================
# Base Storage
# ==============================================================

from .backend import (
    MetricStorageBackend,
)



# ==============================================================
# Storage Backends
# ==============================================================

from .memory import (
    MemoryStorage,
)


from .sqlite import (
    SQLiteStorage,
)


from .duckdb import (
    DuckDBStorage,
)


from .parquet import (
    ParquetStorage,
)



# ==============================================================
# Aliases
# ==============================================================

StorageBackend = MetricStorageBackend

MemoryBackend = MemoryStorage

SQLiteBackend = SQLiteStorage

DuckDBBackend = DuckDBStorage

ParquetBackend = ParquetStorage



# ==============================================================
# Storage Registry
# ==============================================================

STORAGE_BACKENDS = {

    "backend":
        MetricStorageBackend,


    "memory":
        MemoryStorage,


    "sqlite":
        SQLiteStorage,


    "duckdb":
        DuckDBStorage,


    "parquet":
        ParquetStorage,

}



# ==============================================================
# Factory API
# ==============================================================

def create_storage(
    backend: str = "memory",
    **kwargs,
):
    """
    Create Runtime Metrics Storage backend.

    Example
    -------

    storage = create_storage(
        "sqlite",
        path="metrics.db"
    )

    """

    if backend not in STORAGE_BACKENDS:

        raise ValueError(

            f"Unknown storage backend: {backend}"

        )


    return STORAGE_BACKENDS[backend](
        **kwargs
    )



# ==============================================================
# Default Storage
# ==============================================================

def default_storage(
    **kwargs,
):

    return MemoryStorage(
        **kwargs
    )



# ==============================================================
# Public Namespace
# ==============================================================

__all__ = [

    # Base

    "MetricStorageBackend",

    "StorageBackend",



    # Backends

    "MemoryStorage",

    "SQLiteStorage",

    "DuckDBStorage",

    "ParquetStorage",



    # Aliases

    "MemoryBackend",

    "SQLiteBackend",

    "DuckDBBackend",

    "ParquetBackend",



    # Registry

    "STORAGE_BACKENDS",



    # Factory

    "create_storage",

    "default_storage",

]