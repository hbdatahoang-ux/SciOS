from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ResourceProfile:
    """
    ResourceProfile = Cognitive resource layer for ExecutionContext.
    Defines resource requirements and allocations.
    Immutable, copy-on-write.
    """

    cpu: int = 1
    gpu: int = 0
    memory_mb: int = 512
    disk_mb: int = 0
    io_bandwidth: int = 0

    sandbox: bool = True
    quota: dict[str, Any] = field(default_factory=dict)

    parent: Optional["ResourceProfile"] = None

    # =========================================================
    # Copy-on-Write mutation API
    # =========================================================

    def fork(self, **overrides) -> "ResourceProfile":
        """
        Create new immutable resource snapshot.
        """
        data = self.__dict__.copy()
        data.update(overrides)
        return ResourceProfile(**data)

    def extend(self, cpu: int = 0, gpu: int = 0,
               memory_mb: int = 0, disk_mb: int = 0,
               io_bandwidth: int = 0, quota: dict[str, Any] = None) -> "ResourceProfile":
        """
        Create child resource profile with additional requirements.
        """
        return ResourceProfile(
            cpu=cpu or self.cpu,
            gpu=gpu or self.gpu,
            memory_mb=memory_mb or self.memory_mb,
            disk_mb=disk_mb or self.disk_mb,
            io_bandwidth=io_bandwidth or self.io_bandwidth,
            sandbox=self.sandbox,
            quota=quota or self.quota.copy(),
            parent=self
        )

    # =========================================================
    # Validation API
    # =========================================================

    def fits(self, available: "ResourceProfile") -> bool:
        """
        Check if resource requirements fit within available profile.
        """
        return (
            self.cpu <= available.cpu and
            self.gpu <= available.gpu and
            self.memory_mb <= available.memory_mb and
            self.disk_mb <= available.disk_mb and
            self.io_bandwidth <= available.io_bandwidth
        )

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Flatten resource profile into dict.
        """
        result = {}
        if self.parent:
            result.update(self.parent.to_dict())
        result.update({
            "cpu": self.cpu,
            "gpu": self.gpu,
            "memory_mb": self.memory_mb,
            "disk_mb": self.disk_mb,
            "io_bandwidth": self.io_bandwidth,
            "sandbox": self.sandbox,
            "quota": self.quota,
        })
        return result
