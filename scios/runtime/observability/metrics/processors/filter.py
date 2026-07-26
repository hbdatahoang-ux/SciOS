"""
SciOS-NG Runtime Metrics Filter Processor

Metric filtering processor.

SciOS-NG v0.2
"""


from __future__ import annotations

from typing import Any, Callable


from .processor import MetricProcessor



# ==================================================================
# FilterProcessor
# ==================================================================


class FilterProcessor(
    MetricProcessor
):
    """
    Runtime Metric Filter Processor.

    Responsibilities
    ----------------
    - Remove unwanted metrics
    - Apply filtering rules
    - Support custom predicates
    - Control metric flow in pipeline
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "FilterProcessor",
        description: str = "",
        predicate: Callable | None = None,
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Filtering Rules
        # ----------------------------------------------------------

        self._predicate = predicate


        self._rules: list[
            Callable
        ] = []



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._accepted = 0

        self._rejected = 0



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Apply filtering logic.
        """

        if self.accept(
            metric
        ):

            self._accepted += 1

            return metric



        self._rejected += 1


        return None



    def process(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Process metric with filter.
        """

        result = super().process(
            metric,
            **kwargs,
        )


        return result



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
    # Filtering API
    # ==============================================================

    def accept(
        self,
        metric: Any,
    ) -> bool:
        """
        Check metric acceptance.
        """

        # Custom predicate

        if self._predicate:

            if not self._predicate(
                metric
            ):

                return False



        # Registered rules

        for rule in self._rules:

            if not rule(
                metric
            ):

                return False



        return True



    def reject(
        self,
        metric: Any,
    ) -> bool:

        return not self.accept(
            metric
        )



    # ==============================================================
    # Common Filters
    # ==============================================================

    def by_name(
        self,
        name: str,
    ):

        return self.add_rule(

            lambda metric:
                (
                    metric.get("name")
                    ==
                    name
                    if isinstance(
                        metric,
                        dict
                    )
                    else False
                )

        )



    def by_type(
        self,
        metric_type: str,
    ):

        return self.add_rule(

            lambda metric:
                (
                    metric.get("type")
                    ==
                    metric_type
                    if isinstance(
                        metric,
                        dict
                    )
                    else False
                )

        )



    def by_value(
        self,
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
                "value"
            )


            if value is None:

                return False


            if minimum is not None:

                if value < minimum:

                    return False



            if maximum is not None:

                if value > maximum:

                    return False



            return True


        return self.add_rule(
            rule
        )



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "accepted":
                self._accepted,


            "rejected":
                self._rejected,


            "rules":
                len(
                    self._rules
                ),

        })


        return data



    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ):

        self._accepted = 0

        self._rejected = 0

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

            f"FilterProcessor("
            f"rules={len(self._rules)}, "
            f"accepted={self._accepted}, "
            f"rejected={self._rejected}"
            f")"

        )