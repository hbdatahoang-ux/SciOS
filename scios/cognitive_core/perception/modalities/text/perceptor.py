"""Text perceptor for the SciOS Cognitive Core."""

from __future__ import annotations

from ...core.base import BasePerceptor
from ...core.errors import PerceptionInputError, PerceptionProcessingError
from ...core.result import PerceptionResult
from ...core.types import Metadata, Modality, PerceptionStatus, RawInput
from .cleaner import TextCleaner
from .extractor import TextExtractor
from .parser import TextParser
from .tokenizer import TextTokenizer


class TextPerceptor(BasePerceptor):
    """Orchestrate the text perception pipeline."""

    def __init__(
        self,
        *,
        name: str = "text",
        cleaner: TextCleaner | None = None,
        tokenizer: TextTokenizer | None = None,
        parser: TextParser | None = None,
        extractor: TextExtractor | None = None,
    ) -> None:
        """Initialize the text perception pipeline."""

        super().__init__(
            name=name,
            modality=Modality.TEXT,
        )

        if cleaner is not None and not isinstance(cleaner, TextCleaner):
            raise TypeError("cleaner must be a TextCleaner")

        if tokenizer is not None and not isinstance(
            tokenizer,
            TextTokenizer,
        ):
            raise TypeError("tokenizer must be a TextTokenizer")

        if parser is not None and not isinstance(parser, TextParser):
            raise TypeError("parser must be a TextParser")

        if extractor is not None and not isinstance(
            extractor,
            TextExtractor,
        ):
            raise TypeError("extractor must be a TextExtractor")

        self.cleaner = cleaner or TextCleaner()
        self.tokenizer = tokenizer or TextTokenizer()
        self.parser = parser or TextParser(tokenizer=self.tokenizer)
        self.extractor = extractor or TextExtractor(parser=self.parser)

    def perceive(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Transform raw text into a standardized perception result."""

        if not isinstance(raw_input, str):
            raise PerceptionInputError(
                "text perception input must be a string"
            )

        input_metadata = dict(metadata or {})

        try:
            cleaned_text = self.cleaner.clean(raw_input)
            tokens = self.tokenizer.tokenize(cleaned_text)
            parsed = self.parser.parse(
                cleaned_text,
                tokens=tokens,
            )
            extracted = self.extractor.extract(
                cleaned_text,
                parsed=parsed,
            )
        except Exception as exc:
            if isinstance(exc, PerceptionInputError):
                raise

            raise PerceptionProcessingError(
                "text perception processing failed"
            ) from exc

        result_metadata = {
            **input_metadata,
            "raw_length": len(raw_input),
            "cleaned_length": len(cleaned_text),
        }

        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=Modality.TEXT,
            content=cleaned_text,
            features=extracted["features"],
            entities=extracted["entities"],
            relations=extracted["relations"],
            confidence=1.0,
            metadata=result_metadata,
        )


__all__ = ["TextPerceptor"]
