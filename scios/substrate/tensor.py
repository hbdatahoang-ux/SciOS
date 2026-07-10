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
from typing import Any

import numpy as np

try:
    import torch

    HAS_TORCH = True

except ImportError:

    torch = None

    HAS_TORCH = False


__all__ = [
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
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.zeros(shape)
        )

    @classmethod
    def ones(
        cls,
        shape: tuple[int, ...],
    ) -> "SciOSTensor":

        return cls.from_numpy(
            np.ones(shape)
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

    def numpy(self):

        if self.backend == TensorBackend.NUMPY:
            return self.data

        if HAS_TORCH:
            return self.data.detach().cpu().numpy()

        raise RuntimeError(
            "Torch backend unavailable."
        )

    # ======================================================

    def torch(self):

        if not HAS_TORCH:
            raise RuntimeError(
                "PyTorch not installed."
            )

        if self.backend == TensorBackend.TORCH:
            return self.data

        return torch.from_numpy(
            self.data
        )

    # ======================================================

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

            return SciOSTensor(

                data=self.torch(),

                backend=TensorBackend.TORCH,

                device=Device.CPU,
            )

        raise ValueError(
            backend
        )

    # ======================================================

    def copy(self):

        return SciOSTensor(

            data=self.numpy().copy(),

            backend=self.backend,

            device=self.device,

            metadata=self.metadata.copy(),
        )

    # ======================================================

    def astype(
        self,
        dtype,
    ):

        return SciOSTensor(

            data=self.numpy().astype(dtype),

            backend=TensorBackend.NUMPY,
        )

    # ======================================================

    def to_dict(self):

        return {

            "backend": self.backend.value,

            "device": self.device.value,

            "shape": list(self.shape),

            "dtype": str(self.dtype),

            "metadata": self.metadata,
        }

    # ======================================================

    def __len__(self):

        return len(self.data)

    def __getitem__(self, item):

        return self.data[item]

    def __setitem__(self, key, value):

        self.data[key] = value

    def __repr__(self):

        return (

            "SciOSTensor("

            f"shape={self.shape}, "

            f"dtype={self.dtype}, "

            f"backend={self.backend.value})"

        )
