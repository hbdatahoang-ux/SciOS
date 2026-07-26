"""
SciOS-NG Runtime Metrics Enrichment Processor

Metadata enrichment processor.

SciOS-NG v0.2
"""


from __future__ import annotations

from datetime import datetime
from typing import Any, Callable


from .processor import MetricProcessor



# ==================================================================
# EnrichmentProcessor
# ==================================================================


class EnrichmentProcessor(
    MetricProcessor
):
    """
    Runtime Metric Metadata Enrichment Processor.

    Responsibilities
    ----------------
    - Add runtime metadata
    - Attach contextual information
    - Inject tags and attributes
    - Prepare metrics for observability backends
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "EnrichmentProcessor",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Enrichment Sources
        # ----------------------------------------------------------

        self._static_metadata: dict[str, Any] = {}

        self._dynamic_sources: dict[
            str,
            Callable
        ] = {}



        self._tags: dict[str, str] = {}



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._enriched = 0



    # ==============================================================
    # Processing
    # ==============================================================

    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Add metadata to metric.
        """

        result = self.enrich(
            metric,
            **kwargs,
        )


        self._enriched += 1


        return result



    # ==============================================================
    # Enrichment API
    # ==============================================================

    def enrich(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Enrich metric object.
        """

        if isinstance(
            metric,
            dict,
        ):

            result = dict(
                metric
            )

        else:

            result = {

                "value":
                    metric,

            }



        metadata = {}


        metadata.update(
            self._static_metadata
        )


        metadata.update(
            self.collect_dynamic()
        )


        metadata.update(
            kwargs
        )



        if metadata:

            result[
                "metadata"
            ] = metadata



        if self._tags:

            result[
                "tags"
            ] = dict(
                self._tags
            )



        return result



    # ==============================================================
    # Metadata Management
    # ==============================================================

    def add_metadata(
        self,
        key: str,
        value: Any,
    ):

        self._static_metadata[key] = value


        return self



    def remove_metadata(
        self,
        key: str,
    ):

        self._static_metadata.pop(
            key,
            None,
        )


        return self



    def metadata(
        self,
    ):

        return dict(
            self._static_metadata
        )



    # ==============================================================
    # Dynamic Sources
    # ==============================================================

    def register_source(
        self,
        name: str,
        provider: Callable,
    ):

        self._dynamic_sources[name] = provider


        return self



    def remove_source(
        self,
        name: str,
    ):

        self._dynamic_sources.pop(
            name,
            None,
        )


        return self



    def collect_dynamic(
        self,
    ) -> dict[str, Any]:
        """
        Collect dynamic metadata.
        """

        result = {}


        for name, provider in self._dynamic_sources.items():

            try:

                result[name] = provider()


            except Exception:

                result[name] = None



        return result



    # ==============================================================
    # Tag Management
    # ==============================================================

    def add_tag(
        self,
        key: str,
        value: str,
    ):

        self._tags[key] = value


        return self



    def remove_tag(
        self,
        key: str,
    ):

        self._tags.pop(
            key,
            None,
        )


        return self



    def tags(
        self,
    ):

        return dict(
            self._tags
        )



    # ==============================================================
    # Built-in Enrichment
    # ==============================================================

    def add_timestamp(
        self,
    ):

        return self.add_metadata(
            "processed_at",
            datetime.utcnow().isoformat(),
        )



    def add_runtime(
        self,
        runtime_name: str,
    ):

        return self.add_metadata(
            "runtime",
            runtime_name,
        )



    def add_component(
        self,
        component: str,
    ):

        return self.add_metadata(
            "component",
            component,
        )



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "enriched":
                self._enriched,


            "metadata_fields":
                len(
                    self._static_metadata
                ),


            "dynamic_sources":
                len(
                    self._dynamic_sources
                ),


            "tags":
                len(
                    self._tags
                ),

        })


        return data



    # ==============================================================
    # Reset
    # ==============================================================

    def reset(
        self,
    ):

        self._enriched = 0

        return self



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return (

            len(self._static_metadata)

            +

            len(self._tags)

        )



    def __repr__(
        self,
    ):

        return (

            f"EnrichmentProcessor("
            f"metadata={len(self._static_metadata)}, "
            f"tags={len(self._tags)}, "
            f"enriched={self._enriched}"
            f")"

        )