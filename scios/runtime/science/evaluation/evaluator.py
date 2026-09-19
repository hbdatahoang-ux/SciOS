# ==============================================================================
# SciOS Runtime Science
# Evaluation Engine
# ==============================================================================

from __future__ import annotations

from numbers import Real
from typing import Any, Mapping

from .models import (
    EvaluationOutcome,
    EvaluationResult,
    InvalidEvaluationError,
)


# ==============================================================================
# Evaluator
# ==============================================================================


class Evaluator:
    """
    Deterministic evaluator for scientific hypotheses.

    The evaluator compares a hypothesis against an observation and produces
    an immutable EvaluationResult.

    Semantic boundary:

        Executor
            ↓
        Observation
            ↓
        Evaluator
            ↓
        EvaluationResult
            ↓
        Knowledge

    The evaluator interprets evidence.

    It does NOT:

        - execute experiments
        - mutate hypotheses
        - mutate observations
        - mutate world state
        - create Knowledge
        - perform probabilistic inference
        - perform fuzzy comparison
        - perform tolerance-based comparison
        - infer missing values
        - coerce values between types
        - modify domain objects
    """

    # ==========================================================================
    # Constants
    # ==========================================================================

    _EXPECTED_FIELDS: tuple[str, ...] = (
        "expected",
        "expected_value",
        "prediction",
    )

    _OBSERVED_RESPONSE_KEY = "response"

    # ==========================================================================
    # Public API
    # ==========================================================================

    def evaluate(
        self,
        hypothesis: Any,
        observation: Any,
    ) -> EvaluationResult:
        """
        Evaluate an observation against a hypothesis.

        Parameters
        ----------
        hypothesis:
            Domain hypothesis object or Mapping representation.

        observation:
            Domain observation object or Mapping representation.

        Returns
        -------
        EvaluationResult
            Immutable deterministic evaluation result.

        Raises
        ------
        InvalidEvaluationError
            If either input is missing or does not satisfy the required
            evaluation contract.
        """

        self._validate_input(
            hypothesis,
            "hypothesis",
        )

        self._validate_input(
            observation,
            "observation",
        )

        hypothesis_id = self._get_id(
            hypothesis,
            "hypothesis",
        )

        observation_id = self._get_id(
            observation,
            "observation",
        )

        expected = self._extract_expected(
            hypothesis,
        )

        observed = self._extract_observed(
            observation,
        )

        outcome, score, reason = self._evaluate_values(
            expected,
            observed,
        )

        return EvaluationResult(
            hypothesis_id=hypothesis_id,
            observation_id=observation_id,
            outcome=outcome,
            score=score,
            reason=reason,
        )

    # ==========================================================================
    # Input Validation
    # ==========================================================================

    @staticmethod
    def _validate_input(
        value: Any,
        kind: str,
    ) -> None:
        """
        Validate that a required evaluation input exists.

        The evaluator intentionally does not require a particular concrete
        domain class here. Both domain objects and Mapping representations
        are part of the public contract.
        """

        if value is None:
            raise InvalidEvaluationError(
                f"{kind} must not be None"
            )

    # ==========================================================================
    # Generic Field Access
    # ==========================================================================

    @staticmethod
    def _get_field(
        value: Any,
        field: str,
        default: Any = None,
    ) -> Any:
        """
        Read a field from either a Mapping or an object.

        Mapping access takes precedence because Mapping represents an explicit
        external/data representation.

        Attribute access is used only for non-Mapping objects.
        """

        if isinstance(value, Mapping):
            return value.get(
                field,
                default,
            )

        return getattr(
            value,
            field,
            default,
        )

    # ==========================================================================
    # Identifier Validation
    # ==========================================================================

    @classmethod
    def _get_id(
        cls,
        value: Any,
        kind: str,
    ) -> str:
        """
        Extract and validate an entity identifier.

        IDs must be non-empty strings.

        Whitespace surrounding the ID is not removed from the returned value;
        only whitespace-only IDs are rejected.
        """

        identifier = cls._get_field(
            value,
            "id",
        )

        if not isinstance(identifier, str):
            raise InvalidEvaluationError(
                f"{kind} must provide a non-empty string id"
            )

        if not identifier.strip():
            raise InvalidEvaluationError(
                f"{kind} must provide a non-empty string id"
            )

        return identifier

    # ==========================================================================
    # Expected Value Extraction
    # ==========================================================================

    @classmethod
    def _extract_expected(
        cls,
        hypothesis: Any,
    ) -> Any:
        """
        Extract the expected value from a hypothesis.

        Supported fields, in precedence order:

            1. expected
            2. expected_value
            3. prediction

        A value of ``None`` is treated as missing.

        This deliberately means that ``None`` cannot currently be used as an
        explicit expected value.
        """

        for field in cls._EXPECTED_FIELDS:
            value = cls._get_field(
                hypothesis,
                field,
            )

            if value is not None:
                return value

        raise InvalidEvaluationError(
            "hypothesis must provide expected value"
        )

    # ==========================================================================
    # Observed Value Extraction
    # ==========================================================================

    @classmethod
    def _extract_observed(
        cls,
        observation: Any,
    ) -> Any:
        """
        Extract the observed value from an observation.

        Supported representations:

            observation.value

            observation.values["response"]

        Mapping representations are also supported.

        ``value`` takes precedence over ``values["response"]``.
        """

        value = cls._get_field(
            observation,
            "value",
        )

        if value is not None:
            return value

        values = cls._get_field(
            observation,
            "values",
        )

        if isinstance(values, Mapping):
            if cls._OBSERVED_RESPONSE_KEY in values:
                response = values[
                    cls._OBSERVED_RESPONSE_KEY
                ]

                if response is not None:
                    return response

        raise InvalidEvaluationError(
            "observation must provide observed value"
        )

    # ==========================================================================
    # Evaluation Semantics
    # ==========================================================================

    @staticmethod
    def _evaluate_values(
        expected: Any,
        observed: Any,
    ) -> tuple[
        EvaluationOutcome,
        float,
        str,
    ]:
        """
        Deterministically compare expected and observed values.

        Semantic rules:

            exact equality
                → CONFIRMED / 1.0

            boolean mismatch
                → REFUTED / 0.0

            numeric mismatch
                → REFUTED / 0.0

            other mismatch
                → SURPRISE / 0.0

        No tolerance, coercion, approximation, or probabilistic inference
        is performed.
        """

        # ----------------------------------------------------------------------
        # Exact equality
        # ----------------------------------------------------------------------

        if Evaluator._values_equal(
            expected,
            observed,
        ):
            return (
                EvaluationOutcome.CONFIRMED,
                1.0,
                "observed value matches expected value",
            )

        # ----------------------------------------------------------------------
        # Boolean mismatch
        #
        # bool is a subclass of int in Python, so this check must happen
        # before numeric comparison.
        # ----------------------------------------------------------------------

        if (
            isinstance(expected, bool)
            and isinstance(observed, bool)
        ):
            return (
                EvaluationOutcome.REFUTED,
                0.0,
                "observed boolean differs from expected boolean",
            )

        # ----------------------------------------------------------------------
        # Numeric mismatch
        # ----------------------------------------------------------------------

        if Evaluator._are_numeric(
            expected,
            observed,
        ):
            return (
                EvaluationOutcome.REFUTED,
                0.0,
                "observed numeric value differs from expected value",
            )

        # ----------------------------------------------------------------------
        # Generic mismatch
        # ----------------------------------------------------------------------

        return (
            EvaluationOutcome.SURPRISE,
            0.0,
            "observed value differs from expected value",
        )

    # ==========================================================================
    # Equality
    # ==========================================================================

    @staticmethod
    def _values_equal(
        expected: Any,
        observed: Any,
    ) -> bool:
        """
        Perform deterministic equality comparison.

        The method exists as an explicit semantic boundary so equality logic
        can be tested independently and extended later without changing the
        public evaluate() contract.
        """

        try:
            result = expected == observed
        except Exception as exc:
            raise InvalidEvaluationError(
                "values could not be compared"
            ) from exc

        # Normal Python scalar/container equality produces bool.
        #
        # Some scientific objects (for example NumPy arrays) produce an
        # array-like equality result whose truth value is ambiguous. Such
        # values are deliberately not treated as exact equality here.
        if isinstance(result, bool):
            return result

        return False

    # ==========================================================================
    # Numeric Classification
    # ==========================================================================

    @staticmethod
    def _are_numeric(
        expected: Any,
        observed: Any,
    ) -> bool:
        """
        Return True when both values are real numeric values.

        bool is explicitly excluded because Python considers bool an int
        subclass.
        """

        return (
            isinstance(expected, Real)
            and not isinstance(expected, bool)
            and isinstance(observed, Real)
            and not isinstance(observed, bool)
        )