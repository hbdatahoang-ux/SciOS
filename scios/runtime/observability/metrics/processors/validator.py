"""
SciOS-NG Runtime Metrics Validation Processor

Metric validation processor.

SciOS-NG v0.2
"""


from __future__ import annotations

from typing import Any, Callable


from .processor import MetricProcessor



# ==================================================================
# ValidatorProcessor
# ==================================================================


class ValidatorProcessor(
    MetricProcessor
):
    """
    Runtime Metric Validation Processor.

    Responsibilities
    ----------------
    - Validate metric structure
    - Check schema consistency
    - Verify value constraints
    - Prevent invalid metrics entering pipeline
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "ValidatorProcessor",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Validation Rules
        # ----------------------------------------------------------

        self._rules: list[
            Callable
        ] = []


        self._schema: dict[str, type] = {}



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._validated = 0

        self._invalid = 0



        self._errors: list[str] = []



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Validate metric.

        Returns:
            metric if valid
            None if invalid
        """

        valid, errors = self.validate(
            metric
        )


        if valid:

            self._validated += 1

            return metric



        self._invalid += 1


        self._errors.extend(
            errors
        )


        return None



    # ==============================================================
    # Validation API
    # ==============================================================

    def validate(
        self,
        metric: Any,
    ) -> tuple[bool, list[str]]:
        """
        Run all validators.
        """

        errors = []



        for rule in self._rules:

            try:

                result = rule(
                    metric
                )


                if result is False:

                    errors.append(
                        "Rule validation failed"
                    )


                elif isinstance(
                    result,
                    str
                ):

                    errors.append(
                        result
                    )



            except Exception as exc:

                errors.append(
                    str(exc)
                )



        schema_errors = self.validate_schema(
            metric
        )


        errors.extend(
            schema_errors
        )



        return (

            len(errors) == 0,

            errors,

        )



    # ==============================================================
    # Rule Management
    # ==============================================================

    def add_rule(
        self,
        rule: Callable,
    ):

        self._rules.append(
            rule
        )


        return self



    def remove_rule(
        self,
        rule: Callable,
    ):

        if rule in self._rules:

            self._rules.remove(
                rule
            )


        return self



    def clear_rules(
        self,
    ):

        self._rules.clear()


        return self



    def rules(
        self,
    ):

        return list(
            self._rules
        )



    # ==============================================================
    # Schema Validation
    # ==============================================================

    def define_field(
        self,
        name: str,
        field_type: type,
    ):

        self._schema[name] = field_type


        return self



    def remove_field(
        self,
        name: str,
    ):

        self._schema.pop(
            name,
            None,
        )


        return self



    def schema(
        self,
    ):

        return dict(
            self._schema
        )



    def validate_schema(
        self,
        metric: Any,
    ) -> list[str]:
        """
        Validate metric fields.
        """

        errors = []



        if not self._schema:

            return errors



        if not isinstance(
            metric,
            dict
        ):

            return [
                "Metric must be dictionary"
            ]



        for field, expected in self._schema.items():


            if field not in metric:

                errors.append(
                    f"Missing field: {field}"
                )


                continue



            if not isinstance(
                metric[field],
                expected
            ):

                errors.append(

                    f"Invalid type for {field}"

                )



        return errors



    # ==============================================================
    # Built-in Validators
    # ==============================================================

    def require(
        self,
        *fields: str,
    ):

        def rule(metric):

            if not isinstance(
                metric,
                dict
            ):

                return False


            for field in fields:

                if field not in metric:

                    return (
                        f"Missing required field: {field}"
                    )


            return True


        return self.add_rule(
            rule
        )



    def range(
        self,
        field: str,
        minimum=None,
        maximum=None,
    ):

        def rule(metric):

            if not isinstance(
                metric,
                dict
            ):

                return False


            value = metric.get(
                field
            )


            if value is None:

                return (
                    f"Missing field: {field}"
                )


            if minimum is not None and value < minimum:

                return (
                    f"{field} below minimum"
                )


            if maximum is not None and value > maximum:

                return (
                    f"{field} above maximum"
                )


            return True


        return self.add_rule(
            rule
        )



    # ==============================================================
    # Diagnostics
    # ==============================================================

    def errors(
        self,
    ):

        return list(
            self._errors
        )



    def clear_errors(
        self,
    ):

        self._errors.clear()

        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "validated":
                self._validated,


            "invalid":
                self._invalid,


            "rules":
                len(
                    self._rules
                ),


            "schema_fields":
                len(
                    self._schema
                ),

        })


        return data



    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ):

        self._validated = 0

        self._invalid = 0

        self._errors.clear()


        return self



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return len(
            self._rules
        )



    def __repr__(
        self,
    ):

        return (

            f"ValidatorProcessor("
            f"rules={len(self._rules)}, "
            f"validated={self._validated}, "
            f"invalid={self._invalid}"
            f")"

        )