"""
SciOS-NG Runtime Metrics Processors

Public API for Runtime Metrics Processing subsystem.

SciOS-NG v0.2
"""


# ==============================================================
# Base Processor
# ==============================================================

from .processor import (
    MetricProcessor,
)



# ==============================================================
# Built-in Processors
# ==============================================================

from .filter import (
    FilterProcessor,
)


from .sampler import (
    SamplingProcessor,
)


from .normalizer import (
    NormalizerProcessor,
)


from .validator import (
    ValidatorProcessor,
)


from .enrichment import (
    EnrichmentProcessor,
)


from .batching import (
    BatchingProcessor,
)


from .compression import (
    CompressionProcessor,
)



# ==============================================================
# Aliases
# ==============================================================

Processor = MetricProcessor

SamplerProcessor = SamplingProcessor



# ==============================================================
# Processor Registry
# ==============================================================

PROCESSORS = {

    "processor":
        MetricProcessor,


    "filter":
        FilterProcessor,


    "sampler":
        SamplingProcessor,


    "sampling":
        SamplingProcessor,


    "normalizer":
        NormalizerProcessor,


    "validator":
        ValidatorProcessor,


    "enrichment":
        EnrichmentProcessor,


    "batching":
        BatchingProcessor,


    "compression":
        CompressionProcessor,

}



# ==============================================================
# Factory
# ==============================================================

def create_processor(
    processor: str,
    **kwargs,
):
    """
    Create Runtime Metric Processor.

    Example:

        processor = create_processor(
            "filter"
        )

    """

    if processor not in PROCESSORS:

        raise ValueError(
            f"Unknown processor: {processor}"
        )


    return PROCESSORS[processor](
        **kwargs
    )



# ==============================================================
# Pipeline Builder
# ==============================================================

def build_pipeline(
    processors: list[str],
):
    """
    Create processor pipeline.

    Example:

        build_pipeline(
            [
                "validator",
                "normalizer",
                "compression"
            ]
        )

    """

    return [

        create_processor(
            name
        )

        for name
        in processors

    ]



# ==============================================================
# Public Namespace
# ==============================================================

__all__ = [

    # Base

    "MetricProcessor",

    "Processor",



    # Processors

    "FilterProcessor",

    "SamplingProcessor",

    "SamplerProcessor",

    "NormalizerProcessor",

    "ValidatorProcessor",

    "EnrichmentProcessor",

    "BatchingProcessor",

    "CompressionProcessor",



    # Registry

    "PROCESSORS",



    # Factory

    "create_processor",

    "build_pipeline",

]