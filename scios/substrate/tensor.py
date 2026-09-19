"""
SciOS Tensor
============

Backend-independent tensor abstraction.

Responsibilities
----------------
- Unified tensor interface
- Backend abstraction
- Device management
- Tensor metadata
- Serialization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator

import numpy as np

HAS_NUMPY = True

#
# Torch is optional.
#
try:

    import torch

    HAS_TORCH = True

except Exception:
    #
    # Handles:
    #
    # ImportError
    # OSError
    # DLL load failure
    # CUDA runtime failure
    #

    torch = None

    HAS_TORCH = False


__all__ = [
    "HAS_NUMPY",
    "HAS_TORCH",
    "TensorBackend",
    "Device",
    "SciOSTensor",
]


# ==========================================================
# Backend
# ==========================================================

class TensorBackend(str, Enum):

    NUMPY = "numpy"

    TORCH = "torch"


# ==========================================================
# Device
# ==========================================================

class Device(str, Enum):

    CPU = "cpu"

    CUDA = "cuda"

    AUTO = "auto"


# ==========================================================
# Tensor
# ==========================================================

@dataclass(slots=True)
class SciOSTensor:

    data: Any

    backend: TensorBackend = TensorBackend.NUMPY

    device: Device = Device.CPU

    metadata: dict[str, Any] = field(default_factory=dict)

    # ======================================================
    # Constructors
    # ======================================================

    @classmethod
    def from_numpy(
        cls,
        array: np.ndarray,
    ) -> "SciOSTensor":

        return cls(
            data=array,
            backend=TensorBackend.NUMPY,
            device=Device.CPU,
        )

    @classmethod
    def from_torch(
        cls,
        tensor: Any,
    ) -> "SciOSTensor":

        if not HAS_TORCH:
            raise RuntimeError(
                "PyTorch backend unavailable."
            )

        device = (
            Device.CUDA
            if tensor.is_cuda
            else Device.CPU
        )

        return cls(
            data=tensor,
            backend=TensorBackend.TORCH,
            device=device,
        )

    @classmethod
    def from_list(
        cls,
        values: list[Any],
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.asarray(values)
        )

    @classmethod
    def zeros(
        cls,
        shape: tuple[int, ...],
        dtype=float,
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.zeros(shape, dtype=dtype)
        )

    @classmethod
    def ones(
        cls,
        shape: tuple[int, ...],
        dtype=float,
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.ones(shape, dtype=dtype)
        )

    @classmethod
    def empty(
        cls,
        shape: tuple[int, ...],
        dtype=float,
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.empty(shape, dtype=dtype)
        )

    @classmethod
    def full(
        cls,
        shape: tuple[int, ...],
        value: Any,
        dtype=None,
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.full(shape, value, dtype=dtype)
        )

    @classmethod
    def random(
        cls,
        shape: tuple[int, ...],
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.random.random(shape)
        )

    # ======================================================
    # Properties
    # ======================================================

    @property
    def shape(self):

        return self.data.shape

    @property
    def ndim(self):

        return self.data.ndim

    @property
    def dtype(self):

        return self.data.dtype

    # ======================================================
    # Backend
    # ======================================================

    @staticmethod
    def backend_available(
        backend: TensorBackend,
    ) -> bool:

        if backend == TensorBackend.NUMPY:
            return True

        if backend == TensorBackend.TORCH:
            return HAS_TORCH

        return False

    # ======================================================
    # Conversion
    # ======================================================

    def numpy(self) -> np.ndarray:

        if self.backend == TensorBackend.NUMPY:
            return self.data

        if HAS_TORCH:
            return self.data.detach().cpu().numpy()

        raise RuntimeError(
            "Torch backend unavailable."
        )

    def torch(self):

        if not HAS_TORCH:
            raise RuntimeError(
                "PyTorch backend unavailable."
            )

        if self.backend == TensorBackend.TORCH:
            return self.data

        return torch.from_numpy(
            self.data
        )

    def to(
        self,
        backend: TensorBackend,
    ) -> "SciOSTensor":

        if backend == self.backend:
            return self

        if backend == TensorBackend.NUMPY:
            return SciOSTensor.from_numpy(
                self.numpy()
            )

        if backend == TensorBackend.TORCH:
            return SciOSTensor.from_torch(
                self.torch()
            )

        raise ValueError(
            f"Unsupported backend: {backend}"
        )

    # ======================================================
    # Utilities
    # ======================================================

    def clone(self) -> "SciOSTensor":

        return self.copy()

    def copy(self) -> "SciOSTensor":

        return SciOSTensor(
            data=self.numpy().copy(),
            backend=self.backend,
            device=self.device,
            metadata=self.metadata.copy(),
        )

    def astype(
        self,
        dtype: Any,
    ) -> "SciOSTensor":

        return SciOSTensor.from_numpy(
            self.numpy().astype(dtype)
        )

    def tolist(self):

        return self.numpy().tolist()

    def to_dict(self):

        return {
            "backend": self.backend.value,
            "device": self.device.value,
            "shape": list(self.shape),
            "dtype": str(self.dtype),
            "metadata": self.metadata,
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __array__(self):

        return self.numpy()

    def __len__(self):

        return len(self.data)

    def __iter__(self) -> Iterator[Any]:

        return iter(self.data)

    def __getitem__(
        self,
        item,
    ):

        return self.data[item]

    def __setitem__(
        self,
        key,
        value,
    ):

        self.data[key] = value

    def __repr__(self):

        return (
            "SciOSTensor("
            f"shape={self.shape}, "
            f"dtype={self.dtype}, "
            f"backend={self.backend.value}, "
            f"device={self.device.value})"
        )