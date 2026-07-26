"""
SciOS Observability
===================

Metric Base Class.

Part 1
------

Foundation layer.

Responsibilities
----------------

- Abstract metric foundation
- Runtime identity
- Descriptor binding
- Metadata binding
- Label binding
- Attribute binding
- Thread safety

This class contains no aggregation logic.

Concrete implementations:

- Counter
- Gauge
- Histogram
- Summary
- Timer

"""

from __future__ import annotations


# ==========================================================
# Imports
# ==========================================================

from abc import ABC

from datetime import datetime
from datetime import timezone

from threading import RLock

from typing import Any

from uuid import UUID
from uuid import uuid4


from .attributes import MetricAttributes
from .descriptor import MetricDescriptor
from .labels import MetricLabels
from .metadata import MetricMetadata


__all__ = [
    "Metric",
]



# ==========================================================
# Metric Base Class
# ==========================================================


class Metric(ABC):
    """
    Abstract base class for all metrics.

    Metric is a runtime object.

    It combines:

    Descriptor
        Static schema.

    Metadata
        Semantic information.

    Labels
        Metric dimensions.

    Attributes
        Runtime properties.


    It does NOT implement:

    - counting
    - aggregation
    - histogram buckets
    - timing logic

    Those belong to subclasses.
    """


    # ======================================================
    # Constructor
    # ======================================================


    def __init__(
        self,
        *,
        descriptor: MetricDescriptor,
        metadata: MetricMetadata | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
    ) -> None:
        """
        Initialize metric instance.

        Parameters
        ----------

        descriptor:
            Metric schema definition.

        metadata:
            Runtime metadata.

        labels:
            Metric labels.

        attributes:
            Runtime attributes.
        """


        # --------------------------------------------------
        # Runtime Identity
        # --------------------------------------------------

        self._id: UUID = uuid4()
        


        self._created_at: datetime = (
            datetime.now(
                timezone.utc
            )
        )


        # --------------------------------------------------
        # Descriptor
        # --------------------------------------------------

        self._descriptor: MetricDescriptor = (
            descriptor
        )


        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._metadata: MetricMetadata = (

            metadata.copy()

            if metadata is not None

            else descriptor.metadata.copy()

        )


        # --------------------------------------------------
        # Labels
        # --------------------------------------------------

        self._labels: MetricLabels = (

            labels.copy()

            if labels is not None

            else MetricLabels()

        )


        # --------------------------------------------------
        # Attributes
        # --------------------------------------------------

        self._attributes: MetricAttributes = (

            attributes.copy()

            if attributes is not None

            else MetricAttributes()

        )


        # --------------------------------------------------
        # Synchronization
        # --------------------------------------------------

        self._lock: RLock = RLock()
        # ==================================================
        # Part 2. Runtime State
        # ==================================================


        # --------------------------------------------------
        # Runtime Value
        # --------------------------------------------------

        self._value: Any = None


        self._previous_value: Any = None



        # --------------------------------------------------
        # Update Tracking
        # --------------------------------------------------

        self._update_count: int = 0



        # --------------------------------------------------
        # Lifecycle State
        # --------------------------------------------------

        self._enabled: bool = True


        self._frozen: bool = False


        self._closed: bool = False



        # --------------------------------------------------
        # Runtime Timestamp
        # --------------------------------------------------

        self._updated_at: datetime = (
            self._created_at
        )



        # --------------------------------------------------
        # Version / Revision
        # --------------------------------------------------

        self._revision: int = 0



        # --------------------------------------------------
        # Dirty Tracking
        # --------------------------------------------------

        self._dirty: bool = False



    # ======================================================
    # Identity Properties
    # ======================================================


    @property
    def id(
        self,
    ) -> UUID:
        """
        Runtime unique identifier.
        """

        return self._id



    @property
    def created_at(
        self,
    ) -> datetime:
        """
        Metric creation time.
        """

        return self._created_at



    # ======================================================
    # Descriptor Access
    # ======================================================


    @property
    def descriptor(
        self,
    ) -> MetricDescriptor:
        """
        Metric descriptor.

        Descriptor is immutable schema.
        """

        return self._descriptor



    # ======================================================
    # Metadata Access
    # ======================================================


    @property
    def metadata(
        self,
    ) -> MetricMetadata:
        """
        Metric metadata.
        """

        return self._metadata



    # ======================================================
    # Labels Access
    # ======================================================


    @property
    def labels(
        self,
    ) -> MetricLabels:
        """
        Metric labels.
        """

        return self._labels



    # ======================================================
    # Attributes Access
    # ======================================================


    @property
    def attributes(
        self,
    ) -> MetricAttributes:
        """
        Metric attributes.
        """

        return self._attributes



    # ======================================================
    # Synchronization Access
    # ======================================================


    @property
    def lock(
        self,
    ) -> RLock:
        """
        Internal synchronization lock.

        Used internally by metric runtime.
        """

        return self._lock
    # ======================================================
    # Runtime State Properties
    # ======================================================


    @property
    def value(
        self,
    ) -> Any:
        """
        Current metric value.

        Read-only access.
        """

        return self._value



    @property
    def previous_value(
        self,
    ) -> Any:
        """
        Previous metric value.
        """

        return self._previous_value



    @property
    def update_count(
        self,
    ) -> int:
        """
        Number of successful updates.
        """

        return self._update_count



    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether metric accepts updates.
        """

        return self._enabled



    @property
    def frozen(
        self,
    ) -> bool:
        """
        Whether metric is frozen.
        """

        return self._frozen



    @property
    def closed(
        self,
    ) -> bool:
        """
        Whether metric is permanently closed.
        """

        return self._closed



    @property
    def updated_at(
        self,
    ) -> datetime:
        """
        Last update timestamp.
        """

        return self._updated_at



    @property
    def revision(
        self,
    ) -> int:
        """
        Runtime revision number.

        Incremented on state changes.
        """

        return self._revision



    @property
    def dirty(
        self,
    ) -> bool:
        """
        Whether state changed since last checkpoint.
        """

        return self._dirty
    # ======================================================
    # Part 3. Value API
    # ======================================================


    def get(
        self,
    ) -> Any:
        """
        Return current metric value.

        Thread-safe read access.
        """

        with self._lock:

            self._access()

            return self._value



    def set(
        self,
        value: Any,
    ) -> None:
        """
        Replace current metric value.

        This is the primitive mutation operation.

        Subclasses may override update()
        for specialized behavior.
        """

        with self._lock:

            self._ensure_mutable()


            old_value = self._value


            self._before_update(
                old_value,
                value,
            )


            self._previous_value = (
                self._value
            )


            self._value = value


            self._update_count += 1


            self._touch()


            self._after_update(
                old_value,
                value,
            )



    def update(
        self,
        value: Any,
    ) -> None:
        """
        Update metric value.

        Default implementation delegates
        to set().

        Specialized metrics override this.

        Examples:

        Counter:
            increment

        Histogram:
            observe

        Timer:
            record duration
        """

        self.set(
            value
        )



    def reset(
        self,
    ) -> None:
        """
        Reset metric value.

        Subclasses may override
        _default_value().
        """

        self.set(
            self._default_value()
        )



    def clear(
        self,
    ) -> None:
        """
        Clear current metric value.

        Equivalent to setting None.
        """

        self.set(
            None
        )



    def delta(
        self,
    ) -> Any:
        """
        Calculate value difference.

        Returns
        -------

        None
            If values cannot be subtracted.
        """


        with self._lock:

            if (
                self._value is None
                or self._previous_value is None
            ):
                return None


            try:

                return (
                    self._value
                    -
                    self._previous_value
                )


            except Exception:

                return None



    def changed(
        self,
    ) -> bool:
        """
        Check whether current value differs
        from previous value.
        """

        with self._lock:

            return (
                self._value
                !=
                self._previous_value
            )        
    # ======================================================
    # Internal Runtime Hooks
    # ======================================================


    def _access(
        self,
    ) -> None:
        """
        Record read access.
        """

        self._last_accessed_at = (
            datetime.now(
                timezone.utc
            )
        )



    def _touch(
        self,
    ) -> None:
        """
        Mark runtime state changed.
        """

        now = datetime.now(
            timezone.utc
        )


        self._updated_at = now

        self._revision += 1

        self._dirty = True



    def _ensure_mutable(
        self,
    ) -> None:
        """
        Validate mutation permission.
        """

        if self._closed:
            raise RuntimeError(
                "Metric is closed."
            )


        if self._frozen:
            raise RuntimeError(
                "Metric is frozen."
            )


        if not self._enabled:
            raise RuntimeError(
                "Metric is disabled."
            )



    def _default_value(
        self,
    ) -> Any:
        """
        Default reset value.

        Override in subclasses.
        """

        return None



    def _before_update(
        self,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """
        Update hook before mutation.
        """

        return None



    def _after_update(
        self,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """
        Update hook after mutation.
        """

        return None
    # ======================================================
    # Part 4. Snapshot API
    # ======================================================


    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Create immutable runtime snapshot.

        Snapshot contains:

        - descriptor
        - value
        - labels
        - attributes
        - revision
        - timestamps
        """

        with self._lock:

            self._before_snapshot()


            snapshot = MetricSnapshot(

                descriptor=self._descriptor,

                value=self._value,

                previous_value=self._previous_value,

                labels=self._labels.copy(),

                attributes=self._attributes.copy(),

                revision=self._revision,

                update_count=self._update_count,

                created_at=self._created_at,

                updated_at=self._updated_at,

            )


            self._last_snapshot_at = (
                datetime.now(
                    timezone.utc
                )
            )


            self._dirty = False


            self._after_snapshot(
                snapshot
            )


            return snapshot
    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Restore metric runtime state
        from snapshot.
        """

        with self._lock:

            self._ensure_mutable()


            if (
                snapshot.descriptor.id
                != self._descriptor.id
            ):

                raise ValueError(
                    "Snapshot descriptor mismatch."
                )


            self._before_restore(
                snapshot
            )


            self._value = (
                snapshot.value
            )


            self._previous_value = (
                snapshot.previous_value
            )


            self._labels = (
                snapshot.labels.copy()
            )


            self._attributes = (
                snapshot.attributes.copy()
            )


            self._revision = (
                snapshot.revision
            )


            self._update_count = (
                snapshot.update_count
            )


            self._updated_at = (
                snapshot.updated_at
            )


            self._touch()


            self._after_restore(
                snapshot
            )
    def clone(
        self,
    ) -> "Metric":
        """
        Create deep independent copy.

        New runtime identity.
        Same descriptor schema.
        """

        with self._lock:


            cloned = self.__class__(

                descriptor=(
                    self._descriptor.copy()
                ),

                metadata=(
                    self._metadata.copy()
                ),

                labels=(
                    self._labels.copy()
                ),

                attributes=(
                    self._attributes.copy()
                ),

            )


            cloned.restore(
                self.snapshot()
            )


            return cloned
    def copy(
        self,
    ) -> "Metric":
        """
        Alias of clone().
        """

        return self.clone()
    def _before_snapshot(
        self,
    ) -> None:
        """
        Hook before snapshot creation.
        """

        return None



    def _after_snapshot(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Hook after snapshot creation.
        """

        return None



    def _before_restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Hook before restore.
        """

        return None



    def _after_restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Hook after restore.
        """

        return None
    # ======================================================
    # Part 5. Lifecycle API
    # ======================================================


    def freeze(
        self,
    ) -> None:
        """
        Freeze metric.

        Frozen metrics:

        - keep current state
        - allow read operations
        - reject mutations

        Used for:
        - checkpoint
        - export
        - immutable snapshots
        """

        with self._lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot freeze closed metric."
                )


            if self._frozen:
                return


            self._before_freeze()


            self._frozen = True


            self._touch()


            self._after_freeze()



    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze metric.

        Allows future mutations.
        """

        with self._lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot unfreeze closed metric."
                )


            if not self._frozen:
                return


            self._before_unfreeze()


            self._frozen = False


            self._touch()


            self._after_unfreeze()



    def enable(
        self,
    ) -> None:
        """
        Enable metric updates.

        Disabled metrics preserve
        their runtime state but reject writes.
        """

        with self._lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot enable closed metric."
                )


            if self._enabled:
                return


            self._before_enable()


            self._enabled = True


            self._touch()


            self._after_enable()



    def disable(
        self,
    ) -> None:
        """
        Disable metric updates.

        Disabled metrics:

        - keep current value
        - reject mutations
        - remain observable
        """

        with self._lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot disable closed metric."
                )


            if not self._enabled:
                return


            self._before_disable()


            self._enabled = False


            self._touch()


            self._after_disable()



    def close(
        self,
    ) -> None:
        """
        Permanently close metric.

        Closed metric:

        - cannot update
        - cannot freeze/unfreeze
        - cannot enable/disable

        Read operations remain valid.
        """

        with self._lock:

            if self._closed:
                return


            self._before_close()


            self._closed = True


            self._enabled = False


            self._frozen = True


            self._touch()


            self._after_close()



    def reopen(
        self,
    ) -> None:
        """
        Reopen closed metric.

        Used by:

        - recovery system
        - checkpoint restore
        - distributed failover
        """

        with self._lock:

            if not self._closed:
                return


            self._before_reopen()


            self._closed = False


            self._enabled = True


            self._frozen = False


            self._touch()


            self._after_reopen()
    # ======================================================
    # Part 6. Internal Runtime Engine
    # ======================================================


    # ======================================================
    # Access Tracking
    # ======================================================


    def _access(
        self,
    ) -> None:
        """
        Record metric read access.

        Used for:

        - diagnostics
        - monitoring
        - idle detection
        """

        self._last_accessed_at = (
            datetime.now(
                timezone.utc
            )
        )



    # ======================================================
    # Runtime Mutation Tracking
    # ======================================================


    def _touch(
        self,
    ) -> None:
        """
        Mark runtime state changed.

        Updates:

        - timestamp
        - revision
        - dirty flag
        """

        self._updated_at = (
            datetime.now(
                timezone.utc
            )
        )


        self._revision += 1


        self._dirty = True



    # ======================================================
    # Mutation Protection
    # ======================================================


    def _ensure_mutable(
        self,
    ) -> None:
        """
        Validate metric mutation permission.

        Raises
        ------

        RuntimeError:
            If metric cannot be modified.
        """


        if self._closed:

            raise RuntimeError(
                "Metric is closed."
            )


        if self._frozen:

            raise RuntimeError(
                "Metric is frozen."
            )


        if not self._enabled:

            raise RuntimeError(
                "Metric is disabled."
            )



    # ======================================================
    # Default Reset Value
    # ======================================================


    def _default_value(
        self,
    ) -> Any:
        """
        Default value used by reset().

        Subclasses override this.

        Examples:

        Counter:
            0

        Gauge:
            0.0

        Histogram:
            empty buckets

        """

        return None



    # ======================================================
    # Runtime State Export
    # ======================================================


    def state(
        self,
    ) -> dict[str, Any]:
        """
        Return complete runtime state.

        Designed for:

        - debugging
        - exporters
        - APIs
        - diagnostics
        """

        with self._lock:

            self._access()


            return {

                "id": str(
                    self._id
                ),


                "value":
                    self._value,


                "previous_value":
                    self._previous_value,


                "update_count":
                    self._update_count,


                "enabled":
                    self._enabled,


                "frozen":
                    self._frozen,


                "closed":
                    self._closed,


                "revision":
                    self._revision,


                "dirty":
                    self._dirty,


                "created_at":
                    self._created_at.isoformat(),


                "updated_at":
                    self._updated_at.isoformat(),


                "descriptor":
                    self._descriptor.to_dict()
                    if hasattr(
                        self._descriptor,
                        "to_dict"
                    )
                    else str(
                        self._descriptor
                    ),


                "metadata":
                    self._metadata.to_dict()
                    if hasattr(
                        self._metadata,
                        "to_dict"
                    )
                    else dict(
                        self._metadata
                    ),


                "labels":
                    dict(
                        self._labels
                    ),


                "attributes":
                    dict(
                        self._attributes
                    ),

            }



    # ======================================================
    # Health Diagnostics
    # ======================================================


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Runtime health report.

        Returns:

        - healthy
        - issues
        - status
        """

        with self._lock:

            issues = []


            if self._closed:

                issues.append(
                    "closed"
                )


            if not self._enabled:

                issues.append(
                    "disabled"
                )


            if self._frozen:

                issues.append(
                    "frozen"
                )


            return {

                "healthy":
                    len(issues) == 0,


                "status":
                    "healthy"
                    if not issues
                    else "degraded",


                "issues":
                    issues,


                "revision":
                    self._revision,


                "updates":
                    self._update_count,

            }



    # ======================================================
    # Runtime Statistics
    # ======================================================


    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Runtime metric statistics.

        Used by:

        - observability dashboards
        - exporters
        - debugging
        """

        with self._lock:

            return {

                "updates":
                    self._update_count,


                "revision":
                    self._revision,


                "dirty":
                    self._dirty,


                "enabled":
                    self._enabled,


                "frozen":
                    self._frozen,


                "closed":
                    self._closed,


                "has_value":
                    self._value is not None,

            }
    # ======================================================
    # Part 7. Diagnostics
    # ======================================================


    # ======================================================
    # Validation
    # ======================================================


    def validate(
        self,
    ) -> dict[str, Any]:
        """
        Validate internal metric state.

        Returns
        -------

        dict

            {
                "valid": bool,
                "errors": list
            }
        """

        with self._lock:

            errors: list[str] = []


            # ----------------------------------------------
            # Descriptor
            # ----------------------------------------------

            if self._descriptor is None:

                errors.append(
                    "Missing descriptor."
                )


            # ----------------------------------------------
            # Identity
            # ----------------------------------------------

            if self._id is None:

                errors.append(
                    "Missing metric identity."
                )


            # ----------------------------------------------
            # Lifecycle consistency
            # ----------------------------------------------

            if (
                self._closed
                and self._enabled
            ):

                errors.append(
                    "Closed metric cannot be enabled."
                )


            if (
                self._closed
                and not self._frozen
            ):

                errors.append(
                    "Closed metric must be frozen."
                )


            # ----------------------------------------------
            # Counters
            # ----------------------------------------------

            if self._update_count < 0:

                errors.append(
                    "Invalid update counter."
                )


            if self._revision < 0:

                errors.append(
                    "Invalid revision."
                )


            return {

                "valid":
                    len(errors) == 0,


                "errors":
                    errors,

            }



    # ======================================================
    # Dump
    # ======================================================


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Export complete diagnostic dump.

        Intended for:

        - debugging
        - support
        - incident reports
        """

        with self._lock:

            return {

                "identity": {

                    "id":
                        str(
                            self._id
                        ),

                    "created_at":
                        self._created_at.isoformat(),

                },


                "descriptor":
                    self._descriptor.to_dict()
                    if hasattr(
                        self._descriptor,
                        "to_dict"
                    )
                    else str(
                        self._descriptor
                    ),


                "runtime":
                    self.state(),


                "statistics":
                    self.statistics(),


                "health":
                    self.health(),


                "validation":
                    self.validate(),

            }



    # ======================================================
    # Info
    # ======================================================


    def info(
        self,
    ) -> dict[str, Any]:
        """
        Return compact metric information.

        Suitable for APIs.
        """

        with self._lock:

            return {

                "id":
                    str(
                        self._id
                    ),


                "name":
                    getattr(
                        self._descriptor,
                        "name",
                        None,
                    ),


                "value":
                    self._value,


                "enabled":
                    self._enabled,


                "frozen":
                    self._frozen,


                "closed":
                    self._closed,


                "revision":
                    self._revision,

            }



    # ======================================================
    # Debug Information
    # ======================================================


    def debug(
        self,
    ) -> str:
        """
        Human readable debug output.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self._id}, "
            f"value={self._value!r}, "
            f"enabled={self._enabled}, "
            f"frozen={self._frozen}, "
            f"closed={self._closed}, "
            f"revision={self._revision}"
            ")"
        )



    # ======================================================
    # Error Diagnostics
    # ======================================================


    def errors(
        self,
    ) -> list[str]:
        """
        Return current validation errors.

        Convenience wrapper around validate().
        """

        result = self.validate()


        return result[
            "errors"
        ]



    # ======================================================
    # Representation
    # ======================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return self.debug()
    # ======================================================
    # Part 8. Python Protocols
    # ======================================================


    # ======================================================
    # String Representation
    # ======================================================


    def __str__(
        self,
    ) -> str:
        """
        Human readable value representation.
        """

        return str(
            self._value
        )



    # ======================================================
    # Equality
    # ======================================================


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare metric values.

        Supports:

        Metric == Metric
        Metric == raw value
        """

        if isinstance(
            other,
            Metric,
        ):

            return (
                self._value
                ==
                other._value
            )


        return (
            self._value
            ==
            other
        )



    # ======================================================
    # Hash
    # ======================================================


    def __hash__(
        self,
    ) -> int:
        """
        Hash by immutable runtime identity.

        Allows:

        set()
        dict keys
        """

        return hash(
            self._id
        )



    # ======================================================
    # Boolean Conversion
    # ======================================================


    def __bool__(
        self,
    ) -> bool:
        """
        Metric truth value.

        False when:

        - no value
        - disabled
        - closed
        """

        if self._closed:

            return False


        if not self._enabled:

            return False


        return bool(
            self._value
        )



    # ======================================================
    # Iterator Protocol
    # ======================================================


    def __iter__(
        self,
    ):
        """
        Iterate over metric value.

        Examples:

        Gauge(10)
            -> [10]

        Histogram([...])
            -> iterate buckets
        """

        try:

            return iter(
                self._value
            )


        except TypeError:

            return iter(
                (
                    self._value,
                )
            )



    # ======================================================
    # Length Protocol
    # ======================================================


    def __len__(
        self,
    ) -> int:
        """
        Return length of metric value.

        Scalar values return 1.
        """

        if self._value is None:

            return 0


        try:

            return len(
                self._value
            )


        except TypeError:

            return 1



    # ======================================================
    # Context Manager
    # ======================================================


    def __enter__(
        self,
    ):
        """
        Enter metric context.

        Example:

        with metric:
            metric.update(value)
        """

        with self._lock:

            if self._closed:

                raise RuntimeError(
                    "Cannot enter closed metric."
                )


            return self



    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """
        Exit metric context.

        Does not suppress exceptions.
        """

        self.close()


        return False
    # ======================================================
    # Part 9. Final Integration
    # ======================================================


    # ======================================================
    # Update Hooks
    # ======================================================


    def _before_update(
        self,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """
        Hook before value mutation.

        Subclasses override:

        - validation
        - preprocessing
        - constraints
        """

        return None



    def _after_update(
        self,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """
        Hook after value mutation.

        Used by:

        - exporters
        - observers
        - event systems
        """

        return None



    # ======================================================
    # Snapshot Hooks
    # ======================================================


    def _before_snapshot(
        self,
    ) -> None:
        """
        Hook before snapshot creation.
        """

        return None



    def _after_snapshot(
        self,
        snapshot: Any,
    ) -> None:
        """
        Hook after snapshot creation.
        """

        return None



    def _before_restore(
        self,
        snapshot: Any,
    ) -> None:
        """
        Hook before snapshot restore.
        """

        return None



    def _after_restore(
        self,
        snapshot: Any,
    ) -> None:
        """
        Hook after snapshot restore.
        """

        return None



    # ======================================================
    # Lifecycle Hooks
    # ======================================================


    def _before_freeze(
        self,
    ) -> None:

        return None



    def _after_freeze(
        self,
    ) -> None:

        return None



    def _before_unfreeze(
        self,
    ) -> None:

        return None



    def _after_unfreeze(
        self,
    ) -> None:

        return None



    def _before_enable(
        self,
    ) -> None:

        return None



    def _after_enable(
        self,
    ) -> None:

        return None



    def _before_disable(
        self,
    ) -> None:

        return None



    def _after_disable(
        self,
    ) -> None:

        return None



    def _before_close(
        self,
    ) -> None:

        return None



    def _after_close(
        self,
    ) -> None:

        return None



    def _before_reopen(
        self,
    ) -> None:

        return None



    def _after_reopen(
        self,
    ) -> None:

        return None



    # ======================================================
    # Type Safety
    # ======================================================


    def validate_type(
        self,
        value: Any,
    ) -> bool:
        """
        Validate runtime value type.

        Base metric accepts all values.

        Subclasses override.

        Examples:

        Counter:
            int

        Gauge:
            float

        Histogram:
            numeric
        """

        return True



    def ensure_type(
        self,
        value: Any,
    ) -> None:
        """
        Raise error if value type invalid.
        """

        if not self.validate_type(
            value
        ):

            raise TypeError(
                f"Invalid value type: "
                f"{type(value).__name__}"
            )



    # ======================================================
    # Export Helpers
    # ======================================================


    def export(
        self,
    ) -> dict[str, Any]:
        """
        Export metric representation.

        Used by:

        - exporters
        - APIs
        - telemetry pipelines
        """

        return {

            "id":
                str(
                    self._id
                ),


            "name":
                getattr(
                    self._descriptor,
                    "name",
                    None,
                ),


            "value":
                self._value,


            "labels":
                dict(
                    self._labels
                ),


            "attributes":
                dict(
                    self._attributes
                ),


            "timestamp":
                self._updated_at.isoformat(),


            "revision":
                self._revision,

        }



    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Compatibility alias.

        Same as export().
        """

        return self.export()



    # ======================================================
    # Compatibility Helpers
    # ======================================================


    def copy_value(
        self,
    ) -> Any:
        """
        Return safe value copy.

        Prevent external mutation.
        """

        value = self._value


        if hasattr(
            value,
            "copy"
        ):

            return value.copy()


        return value



    def compatible_with(
        self,
        other: "Metric",
    ) -> bool:
        """
        Check runtime compatibility.

        Metrics are compatible when:

        - same descriptor
        - same metric schema
        """

        if not isinstance(
            other,
            Metric,
        ):

            return False


        return (
            self._descriptor
            ==
            other._descriptor
        )



    # ======================================================
    # Final Representation
    # ======================================================


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Compact production summary.
        """

        return {

            "id":
                str(
                    self._id
                ),

            "name":
                getattr(
                    self._descriptor,
                    "name",
                    None,
                ),

            "value":
                self._value,

            "state":
                {
                    "enabled":
                        self._enabled,

                    "frozen":
                        self._frozen,

                    "closed":
                        self._closed,
                },

            "revision":
                self._revision,

        }                                                                                                                