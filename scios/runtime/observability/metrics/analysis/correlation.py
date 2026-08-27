"""
SciOS-NG Runtime Metrics Analysis

Correlation Analysis Engine

SciOS/scios/runtime/observability/metrics/analysis/correlation.py
"""

from __future__ import annotations

import copy
import math
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable

from .statistics import MetricStatistics


# ==========================================================
# MetricCorrelationAnalyzer
# ==========================================================

class MetricCorrelationAnalyzer:
    """
    Runtime Metrics Correlation Analysis Engine.

    Features
    --------
    - Pearson Correlation
    - Spearman Correlation
    - Kendall Tau
    - Covariance
    - Cosine Similarity
    - Distance Correlation
    - Mutual Information
    - Correlation Matrix
    - Custom Algorithms
    """

    # ======================================================
    # Part 1. Foundation
    # ======================================================

    def __init__(
        self,
        name: str = "MetricCorrelationAnalyzer",
        description: str = "",
    ) -> None:

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(uuid.uuid4())

        self._name = name

        self._description = description

        self._version = "0.2.0"

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False

        self._running = False

        # --------------------------------------------------
        # Correlation Configuration
        # --------------------------------------------------

        self._config = {

            "method": "pearson",

            "min_samples": 2,

            "normalize": True,

            "absolute": False,

            "epsilon": 1e-12,

        }

        # --------------------------------------------------
        # Correlation Registry
        # --------------------------------------------------

        self._algorithms: dict[
            str,
            dict[str, Any],
        ] = {}

        self._history: list[dict] = []

        self._last_result: dict | None = None

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._started_at = time.perf_counter()

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self._statistics = MetricStatistics()

        self._correlation_count = 0

        self._analysis_count = 0

        self._error_count = 0

        self._latency = 0.0

        # --------------------------------------------------
        # Events
        # --------------------------------------------------

        self._hooks: dict[
            str,
            list[Callable],
        ] = {}

        self._events: list[dict] = []

        # --------------------------------------------------
        # Runtime Objects
        # --------------------------------------------------

        self._snapshot = None

        self._context: dict[str, Any] = {}

        self._lock = threading.RLock()

    # ======================================================
    # Identity
    # ======================================================

    @property
    def id(self) -> str:

        return self._id

    @property
    def name(self) -> str:

        return self._name

    @property
    def description(self) -> str:

        return self._description

    @property
    def version(self) -> str:

        return self._version

    # ======================================================
    # Runtime State
    # ======================================================

    @property
    def enabled(self) -> bool:

        return self._enabled

    @property
    def disabled(self) -> bool:

        return not self._enabled

    @property
    def frozen(self) -> bool:

        return self._frozen

    @property
    def closed(self) -> bool:

        return self._closed

    @property
    def running(self) -> bool:

        return self._running

    @property
    def active(self) -> bool:

        return (

            self._enabled
            and
            not self._frozen
            and
            not self._closed

        )

    # ======================================================
    # Correlation Configuration
    # ======================================================

    @property
    def config(self) -> dict:

        return dict(
            self._config
        )

    def configure(
        self,
        **kwargs,
    ):

        with self._lock:

            self._config.update(
                kwargs
            )

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Metadata
    # ======================================================

    @property
    def created_at(self):

        return self._created_at

    @property
    def updated_at(self):

        return self._updated_at

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def statistics(self):

        return self._statistics

    @property
    def correlation_count(self):

        return self._correlation_count

    @property
    def analysis_count(self):

        return self._analysis_count

    @property
    def error_count(self):

        return self._error_count

    # ======================================================
    # NOTE
    # ======================================================
    # Part 2  : Correlation API
    # Part 3  : Correlation Algorithms
    # Part 4  : Correlation Registry API
    # Part 5  : Lifecycle
    # Part 6  : Runtime Operations
    # Part 7  : Statistics & Diagnostics
    # Part 8  : Serialization
    # Part 9  : Events & Hooks
    # Part 10 : Python Protocols
    # ======================================================
        # ======================================================
    # Part 2. Correlation API
    # ======================================================

    def analyze(
        self,
        x,
        y,
        method: str = "pearson",
        **kwargs,
    ):
        """
        Analyze correlation between two datasets.

        Parameters
        ----------
        x:
            First dataset.

        y:
            Second dataset.

        method:
            Registered correlation algorithm.

        Returns
        -------
        dict
        """

        if not self.active:

            raise RuntimeError(
                "MetricCorrelationAnalyzer is not active."
            )

        entry = self._algorithms.get(
            method
        )

        if entry is None:

            raise KeyError(
                f"Unknown correlation algorithm: {method}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Correlation algorithm '{method}' is disabled."
            )

        start = time.perf_counter()

        self._running = True

        try:

            result = entry["callable"](

                x,

                y,

                **kwargs,

            )

            self._latency = (

                time.perf_counter()

                -

                start

            )

            self._analysis_count += 1

            if isinstance(
                result,
                dict,
            ):

                if "correlation" in result:

                    self._correlation_count += 1

            self._last_result = result

            self._history.append(
                result
            )

            self._updated_at = datetime.utcnow()

            return result

        except Exception:

            self._error_count += 1

            raise

        finally:

            self._running = False

    def analyze_one(
        self,
        x,
        y,
        method: str = "pearson",
        **kwargs,
    ):
        """
        Analyze one pair of datasets.
        """

        return self.analyze(

            x,

            y,

            method=method,

            **kwargs,

        )

    def analyze_many(
        self,
        pairs,
        method: str = "pearson",
        **kwargs,
    ):
        """
        Analyze multiple dataset pairs.

        Parameters
        ----------
        pairs:
            Iterable of (x, y) tuples.
        """

        results = []

        for x, y in pairs:

            results.append(

                self.analyze(

                    x,

                    y,

                    method=method,

                    **kwargs,

                )

            )

        return results

    def analyze_batch(
        self,
        batches,
        method: str = "pearson",
        **kwargs,
    ):
        """
        Batch correlation analysis.
        """

        return self.analyze_many(

            batches,

            method=method,

            **kwargs,

        )

    # ------------------------------------------------------
    # Aliases
    # ------------------------------------------------------

    run = analyze

    execute = analyze

    process = analyze
    # ======================================================
    # Part 3. Correlation Algorithms
    # ======================================================

    import math
    from collections import Counter

    def _validate(
        self,
        x,
        y,
    ):
        """
        Validate input datasets.
        """

        x = list(x)
        y = list(y)

        if len(x) != len(y):

            raise ValueError(
                "Datasets must have the same length."
            )

        if len(x) < 2:

            raise ValueError(
                "At least two samples are required."
            )

        return x, y

    def pearson(
        self,
        x,
        y,
    ):
        """
        Pearson correlation coefficient.
        """

        x, y = self._validate(x, y)

        n = len(x)

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        dx = [v - mean_x for v in x]
        dy = [v - mean_y for v in y]

        numerator = sum(a * b for a, b in zip(dx, dy))

        denominator = (
            math.sqrt(sum(a * a for a in dx))
            *
            math.sqrt(sum(b * b for b in dy))
        )

        value = (
            numerator / denominator
            if denominator
            else 0.0
        )

        return numerator / denominator


    def spearman(
        self,
        x,
        y,
    ):
        """
        Spearman rank correlation.
        """

        def rank(values):

            ordered = sorted(
                enumerate(values),
                key=lambda item: item[1],
            )

            ranks = [0] * len(values)

            for i, (idx, _) in enumerate(ordered):

                ranks[idx] = i + 1

            return ranks

        return self.pearson(

            rank(x),

            rank(y),

        )

    def kendall(
        self,
        x,
        y,
    ):
        """
        Kendall Tau correlation.
        """

        x, y = self._validate(x, y)

        concordant = 0

        discordant = 0

        n = len(x)

        for i in range(n):

            for j in range(i + 1, n):

                sign = (

                    (x[i] - x[j])

                    *

                    (y[i] - y[j])

                )

                if sign > 0:

                    concordant += 1

                elif sign < 0:

                    discordant += 1

        total = concordant + discordant

        tau = (

            (concordant - discordant)

            / total

            if total

            else 0.0

        )

        return {

            "algorithm": "kendall",

            "correlation": tau,

        }

    def covariance(
        self,
        x,
        y,
    ):
        """
        Compute covariance between two sequences.
        """

        x, y = self._validate(x, y)

        n = len(x)

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        return sum(
            (a - mean_x) * (b - mean_y)
            for a, b in zip(x, y)
        ) / (len(x) - 1)

    def cosine(
        self,
        x,
        y,
    ):
        """
        Cosine similarity.
        """

        x, y = self._validate(x, y)

        dot = sum(

            a * b

            for a, b in zip(x, y)

        )

        norm_x = math.sqrt(

            sum(v * v for v in x)

        )

        norm_y = math.sqrt(

            sum(v * v for v in y)

        )

        value = (

            dot / (norm_x * norm_y)

            if norm_x and norm_y

            else 0.0

        )

        return dot / (norm_x * norm_y)


    def distance(
        self,
        x,
        y,
    ):
        """
        Euclidean distance.
        """

        x, y = self._validate(x, y)

        dist = math.sqrt(

            sum(

                (a - b) ** 2

                for a, b in zip(x, y)

            )

        )

        return dist

    def mutual_information(
        self,
        x,
        y,
    ):
        """
        Approximate mutual information.
        """

        x, y = self._validate(x, y)

        n = len(x)

        px = Counter(x)

        py = Counter(y)

        pxy = Counter(zip(x, y))

        mi = 0.0

        for pair, count in pxy.items():

            pxv = px[pair[0]] / n

            pyv = py[pair[1]] / n

            pxyv = count / n

            mi += pxyv * math.log2(

                pxyv / (pxv * pyv)

            )

        return {

            "algorithm": "mutual_information",

            "mutual_information": mi,

        }

    def matrix(
        self,
        datasets,
    ):
        """
        Correlation matrix.
        """

        datasets = list(datasets)

        matrix = []

        for row in datasets:

            values = []

            for col in datasets:

                values.append(

                    self.pearson(

                        row,

                        col,

                    )["correlation"]

                )

            matrix.append(values)

        return {

            "algorithm": "matrix",

            "matrix": matrix,

        }

    def custom(
        self,
        x,
        y,
        analyzer,
        **kwargs,
    ):
        """
        User-defined algorithm.
        """

        if not callable(analyzer):

            raise TypeError(
                "analyzer must be callable."
            )

        return analyzer(

            x,

            y,

            **kwargs,

        )
    # ======================================================
    # Part 4. Correlation Registry API
    # ======================================================

    def register_algorithm(
        self,
        name: str,
        algorithm: Callable,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a correlation algorithm.
        """

        if not callable(algorithm):

            raise TypeError(
                "algorithm must be callable."
            )

        with self._lock:

            self._algorithms[name] = {

                "name": name,

                "callable": algorithm,

                "enabled": enabled,

                "metadata": metadata or {},

                "created_at": datetime.utcnow(),

            }

            self._updated_at = datetime.utcnow()

        return self

    def remove_algorithm(
        self,
        name: str,
    ):
        """
        Remove a registered algorithm.
        """

        with self._lock:

            self._algorithms.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    # Backward compatibility

    unregister_algorithm = remove_algorithm

    def algorithm(
        self,
        name: str,
        default=None,
    ):
        """
        Return the registered algorithm callable.
        """
        with self._lock:
            entry = self._algorithms.get(name)

            if entry is None:
                return default

            return entry["callable"]

    def algorithms(self):
        """
        Return registered algorithms as a name -> callable mapping.
        """
        with self._lock:
            return {
                name: entry["callable"]
                for name, entry in self._algorithms.items()
            }

    def contains_algorithm(
        self,
        name: str,
    ) -> bool:
        """
        Whether an algorithm exists.
        """

        return (

            name

            in

            self._algorithms

        )

    def exists_algorithm(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_algorithm().
        """

        return self.contains_algorithm(
            name
        )

    def enable_algorithm(
        self,
        name: str,
    ):
        """
        Enable an algorithm.
        """

        entry = self._algorithms.get(
            name
        )

        if entry is not None:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self

    def disable_algorithm(
        self,
        name: str,
    ):
        """
        Disable an algorithm.
        """

        entry = self._algorithms.get(
            name
        )

        if entry is not None:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self

    def algorithm_names(
        self,
    ):
        """
        Return algorithm names.
        """

        return list(
            self._algorithms.keys()
        )

    @property
    def algorithm_count(
        self,
    ) -> int:
        """
        Number of registered algorithms.
        """

        return len(
            self._algorithms
        )

    def clear_algorithms(
        self,
    ):
        """
        Remove all registered algorithms.
        """

        with self._lock:

            self._algorithms.clear()

            self._updated_at = datetime.utcnow()

        return self

    def execute_algorithm(
        self,
        name: str,
        x,
        y,
        **kwargs,
    ):
        """
        Execute a registered algorithm.
        """

        entry = self._algorithms.get(
            name
        )

        if entry is None:

            raise KeyError(
                f"Unknown correlation algorithm: {name}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Correlation algorithm '{name}' is disabled."
            )

        return entry["callable"](

            x,

            y,

            **kwargs,

        )

    def register_builtin_algorithms(
        self,
    ):
        """
        Register built-in correlation algorithms.
        """

        self.register_algorithm(
            "pearson",
            self.pearson,
        )

        self.register_algorithm(
            "spearman",
            self.spearman,
        )

        self.register_algorithm(
            "kendall",
            self.kendall,
        )

        self.register_algorithm(
            "covariance",
            self.covariance,
        )

        self.register_algorithm(
            "cosine",
            self.cosine,
        )

        self.register_algorithm(
            "distance",
            self.distance,
        )

        self.register_algorithm(
            "mutual_information",
            self.mutual_information,
        )

        self.register_algorithm(
            "matrix",
            self.matrix,
        )

        self.register_algorithm(
            "custom",
            self.custom,
        )

        return self
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(
        self,
    ):
        """
        Enable the correlation analyzer.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ):
        """
        Disable the correlation analyzer.
        """

        with self._lock:

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def freeze(
        self,
    ):
        """
        Freeze the correlation analyzer.
        """

        with self._lock:

            self._frozen = True

            self._updated_at = datetime.utcnow()

        return self

    def unfreeze(
        self,
    ):
        """
        Unfreeze the correlation analyzer.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ):
        """
        Close the correlation analyzer.
        """

        with self._lock:

            self._closed = True

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def reopen(
        self,
    ):
        """
        Reopen the correlation analyzer.
        """

        with self._lock:

            self._closed = False

            self._updated_at = datetime.utcnow()

        return self
    # ======================================================
    # Part 6. Runtime Operations
    # ======================================================

    def reset(
        self,
    ):
        """
        Reset runtime statistics while preserving configuration
        and registered algorithms.
        """

        with self._lock:

            self._correlation_count = 0

            self._analysis_count = 0

            self._error_count = 0

            self._latency = 0.0

            self._running = False

            self._last_result = None

            self._history.clear()

            self._updated_at = datetime.utcnow()

        return self

    def clear(
        self,
    ):
        """
        Clear runtime history.
        """

        with self._lock:

            self._history.clear()

            self._last_result = None

            self._updated_at = datetime.utcnow()

        return self

    def snapshot(
        self,
    ):
        """
        Create a runtime snapshot.
        """

        with self._lock:

            self._snapshot = {

                "config": dict(
                    self._config
                ),

                "history": list(
                    self._history
                ),

                "last_result": self._last_result,

                "correlation_count":
                    self._correlation_count,

                "analysis_count":
                    self._analysis_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._latency,

                "enabled":
                    self._enabled,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

                "updated_at":
                    self._updated_at,

            }

            return dict(
                self._snapshot
            )

    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore runtime state from a snapshot.
        """

        if snapshot is None:

            snapshot = self._snapshot

        if snapshot is None:

            return self

        with self._lock:

            self._config = dict(

                snapshot.get(
                    "config",
                    {},
                )

            )

            self._history = list(

                snapshot.get(
                    "history",
                    [],
                )

            )

            self._last_result = snapshot.get(
                "last_result"
            )

            self._correlation_count = snapshot.get(
                "correlation_count",
                0,
            )

            self._analysis_count = snapshot.get(
                "analysis_count",
                0,
            )

            self._error_count = snapshot.get(
                "error_count",
                0,
            )

            self._latency = snapshot.get(
                "latency",
                0.0,
            )

            self._enabled = snapshot.get(
                "enabled",
                True,
            )

            self._frozen = snapshot.get(
                "frozen",
                False,
            )

            self._closed = snapshot.get(
                "closed",
                False,
            )

            self._updated_at = datetime.utcnow()

        return self

    def clone(
        self,
    ):
        """
        Create an independent analyzer clone.

        Runtime synchronization primitives are recreated.
        Built-in algorithm methods are rebound to the cloned instance.
        Custom algorithm callables are preserved by reference.
        Hooks are copied as independent callback lists.
        """

        with self._lock:

            cloned = self.__class__(
                name=self._name,
                description=self._description,
            )

            # ------------------------------------------------------------
            # Restore serializable/runtime state
            # ------------------------------------------------------------

            cloned.restore(
                copy.deepcopy(
                    self.snapshot()
                )
            )

            # ------------------------------------------------------------
            # Rebuild algorithm registry
            #
            # Built-in algorithms are rebound to the cloned instance.
            # Custom callables are preserved by reference.
            # ------------------------------------------------------------

            cloned._algorithms = {}

            for name, entry in self._algorithms.items():

                cloned_entry = dict(entry)

                if "metadata" in cloned_entry:
                    cloned_entry["metadata"] = copy.deepcopy(
                        cloned_entry["metadata"]
                    )

                original_callable = entry["callable"]

                # --------------------------------------------------------
                # Detect built-in bound methods.
                #
                # A built-in algorithm is a method belonging to this
                # analyzer class. Rebind it to the cloned instance.
                # --------------------------------------------------------

                bound_method = getattr(
                    cloned,
                    name,
                    None,
                )

                if (
                    bound_method is not None
                    and callable(bound_method)
                    and getattr(
                        original_callable,
                        "__self__",
                        None,
                    ) is self
                    and getattr(
                        original_callable,
                        "__func__",
                        None,
                    ) is getattr(
                        bound_method,
                        "__func__",
                        None,
                    )
                ):
                    cloned_entry["callable"] = bound_method

                else:
                    # Custom callable: preserve identity.
                    cloned_entry["callable"] = original_callable

                cloned._algorithms[name] = cloned_entry

            # ------------------------------------------------------------
            # Hooks
            #
            # Preserve callback identity while separating containers.
            # ------------------------------------------------------------

            cloned._hooks = {
                event: list(callbacks)
                for event, callbacks in self._hooks.items()
            }

            # ------------------------------------------------------------
            # Fresh synchronization primitive
            # ------------------------------------------------------------

            cloned._lock = threading.RLock()

            return cloned

    def copy(
        self,
    ):
        """
        Alias of clone().
        """

        return self.clone()
    # ======================================================
    # Part 7. Statistics & Diagnostics
    # ======================================================

    def summary(
        self,
    ) -> dict:
        """
        Return runtime summary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "running": self._running,

            "correlation_count":
                self._correlation_count,

            "analysis_count":
                self._analysis_count,

            "error_count":
                self._error_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

        }

    def report(
        self,
    ) -> dict:
        """
        Return a detailed diagnostic report.
        """

        return {

            "summary":
                self.summary(),

            "configuration":
                dict(self._config),

            "algorithms":
                self.algorithm_names(),

            "algorithm_count":
                self.algorithm_count,

            "history_size":
                len(self._history),

            "last_result":
                self._last_result,

            "created_at":
                self._created_at,

            "updated_at":
                self._updated_at,

        }

    def health(
        self,
    ) -> dict:
        """
        Return analyzer health information.
        """

        healthy = (

            self._enabled

            and

            not self._closed

            and

            not self._frozen

        )

        return {

            "healthy": healthy,

            "status":

                "healthy"

                if healthy

                else

                "inactive",

            "running":
                self._running,

            "errors":
                self._error_count,

        }

    def status(
        self,
    ) -> dict:
        """
        Alias of health().
        """

        return self.health()

    # ------------------------------------------------------
    # Runtime Statistics
    # ------------------------------------------------------

    @property
    def correlation_count(
        self,
    ) -> int:
        """
        Total successful correlations.
        """

        return self._correlation_count

    @property
    def analysis_count(
        self,
    ) -> int:
        """
        Total analyses.
        """

        return self._analysis_count

    @property
    def error_count(
        self,
    ) -> int:
        """
        Total runtime errors.
        """

        return self._error_count

    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime in seconds.
        """

        return (

            time.perf_counter()

            -

            self._started_at

        )

    @property
    def latency(
        self,
    ) -> float:
        """
        Last analysis latency.
        """

        return self._latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize analyzer to dictionary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "description": self._description,

            "version": self._version,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "config": dict(
                self._config
            ),

            "correlation_count":
                self._correlation_count,

            "analysis_count":
                self._analysis_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

            "created_at":
                self._created_at.isoformat(),

            "updated_at":
                self._updated_at.isoformat(),

            "algorithm_names":
                self.algorithm_names(),

            "history":
                list(self._history),

            "last_result":
                self._last_result,

        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):
        """
        Restore analyzer from dictionary.
        """

        obj = cls(

            name=data.get(
                "name",
                "MetricCorrelationAnalyzer",
            ),

            description=data.get(
                "description",
                "",
            ),

        )

        obj._id = data.get(
            "id",
            obj._id,
        )

        obj._version = data.get(
            "version",
            obj._version,
        )

        obj._enabled = data.get(
            "enabled",
            True,
        )

        obj._frozen = data.get(
            "frozen",
            False,
        )

        obj._closed = data.get(
            "closed",
            False,
        )

        obj._config.update(

            data.get(
                "config",
                {},
            )

        )

        obj._correlation_count = data.get(
            "correlation_count",
            0,
        )

        obj._analysis_count = data.get(
            "analysis_count",
            0,
        )

        obj._error_count = data.get(
            "error_count",
            0,
        )

        obj._latency = data.get(
            "latency",
            0.0,
        )

        obj._history = list(

            data.get(
                "history",
                [],
            )

        )

        obj._last_result = data.get(
            "last_result"
        )

        created = data.get(
            "created_at"
        )

        if created:

            obj._created_at = datetime.fromisoformat(
                created
            )

        updated = data.get(
            "updated_at"
        )

        if updated:

            obj._updated_at = datetime.fromisoformat(
                updated
            )

        return obj

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize analyzer to JSON.
        """

        import json

        return json.dumps(

            self.to_dict(),

            **kwargs,

        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ):
        """
        Restore analyzer from JSON.
        """

        import json

        return cls.from_dict(

            json.loads(
                text
            )

        )

    def serialize(
        self,
    ) -> dict:
        """
        Alias of to_dict().
        """

        return self.to_dict()

    @classmethod
    def deserialize(
        cls,
        data,
    ):
        """
        Deserialize analyzer from dictionary or JSON.
        """

        if isinstance(
            data,
            str,
        ):

            return cls.from_json(
                data
            )

        return cls.from_dict(
            data
        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================

    def before_analyze(
        self,
        x,
        y,
        method: str,
        **kwargs,
    ):
        """
        Hook executed before correlation analysis.
        """

        self.emit(

            "before_analyze",

            x=x,

            y=y,

            method=method,

            kwargs=kwargs,

        )

        return self

    def after_analyze(
        self,
        result,
        method: str,
    ):
        """
        Hook executed after correlation analysis.
        """

        self.emit(

            "after_analyze",

            result=result,

            method=method,

        )

        return self

    def before_algorithm(
        self,
        name: str,
    ):
        """
        Hook executed before algorithm execution.
        """

        self.emit(

            "before_algorithm",

            algorithm=name,

        )

        return self

    def after_algorithm(
        self,
        name: str,
        result=None,
    ):
        """
        Hook executed after algorithm execution.
        """

        self.emit(

            "after_algorithm",

            algorithm=name,

            result=result,

        )

        return self

    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register an event hook.
        """

        if not callable(callback):

            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            self._hooks.setdefault(

                event,

                []

            ).append(

                callback

            )

        return self

    def remove_hook(
        self,
        event: str,
        callback: Callable | None = None,
    ):
        """
        Remove one hook or all hooks from an event.
        """

        with self._lock:

            if event not in self._hooks:

                return self

            if callback is None:

                self._hooks.pop(

                    event,

                    None,

                )

                return self

            try:

                self._hooks[event].remove(
                    callback
                )

            except ValueError:

                pass

            if not self._hooks[event]:

                self._hooks.pop(
                    event,
                    None,
                )

        return self

    def emit(
        self,
        event: str,
        **payload,
    ):
        """
        Emit an event.
        """

        record = {

            "timestamp":
                datetime.utcnow(),

            "event":
                event,

            "payload":
                payload,

        }

        self._events.append(
            record
        )

        for callback in self._hooks.get(
            event,
            [],
        ):

            callback(

                self,

                **payload,

            )

        return self

    def subscribe(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Alias of add_hook().
        """

        return self.add_hook(

            event,

            callback,

        )
    # ======================================================
    # Part 10. Python Protocols
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"name={self._name!r}, "

            f"enabled={self._enabled}, "

            f"running={self._running}, "

            f"algorithms={len(self._algorithms)}, "

            f"analyses={self._analysis_count}"

            f")"

        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self._name} "

            f"[enabled={self._enabled}, "

            f"running={self._running}, "

            f"algorithms={len(self._algorithms)}]"

        )

    def __len__(
        self,
    ) -> int:
        """
        Number of registered algorithms.
        """

        return len(
            self._algorithms
        )

    def __iter__(
        self,
    ):
        """
        Iterate over registered algorithm names.
        """

        return iter(
            self._algorithms
        )

    def __contains__(
        self,
        name,
    ) -> bool:
        """
        Membership test.
        """

        return (

            name

            in

            self._algorithms

        )

    def __call__(
        self,
        x,
        y,
        method: str = "pearson",
        **kwargs,
    ):
        """
        Callable interface.
        """

        return self.analyze(

            x,

            y,

            method=method,

            **kwargs,

        )

    def __copy__(
        self,
    ):
        """
        Shallow copy.
        """

        return self.copy()

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy.
        """

        del memo

        return self.clone()                                                            