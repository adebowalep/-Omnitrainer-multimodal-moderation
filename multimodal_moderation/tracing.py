"""
OpenTelemetry tracing setup for OmniTrainer.

Configures a TracerProvider with two span processors:
  - :class:`OpenInferenceSpanProcessor` — enriches AI spans with LLM-specific attributes
  - :class:`SimpleSpanProcessor` + :class:`OTLPSpanExporter` — ships traces to Arize Phoenix

Usage::

    from multimodal_moderation.tracing import setup_tracing, get_tracer, add_media_to_span

    setup_tracing()
    tracer = get_tracer(__name__)
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from multimodal_moderation.env import PHOENIX_URL


def setup_tracing() -> None:
    """
    Initialise OpenTelemetry tracing and register the global TracerProvider.

    Should be called once at application startup before any spans are created.
    Subsequent calls are safe but have no additional effect.
    """
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    provider.add_span_processor(OpenInferenceSpanProcessor())

    exporter = OTLPSpanExporter(endpoint=f"{PHOENIX_URL}/v1/traces")
    provider.add_span_processor(SimpleSpanProcessor(exporter))


def get_tracer(name: str) -> trace.Tracer:
    """
    Return a named :class:`~opentelemetry.trace.Tracer`.

    Args:
        name: Typically ``__name__`` of the calling module.
    """
    return trace.get_tracer(name)


def add_media_to_span(
    span: trace.Span,
    file_path: str,
    media_type: str,
    index: int,
) -> None:
    """
    Copy an uploaded media file to a local store and record its metadata on *span*.

    This lets Arize Phoenix display media thumbnails in the trace viewer.

    Args:
        span:       Active OpenTelemetry span to annotate.
        file_path:  Path to the uploaded file on disk.
        media_type: Logical media category (e.g. ``"image_moderation"``).
        index:      Zero-based index when multiple files are attached to one span.
    """
    try:
        uploads_dir = Path("./uploaded_media")
        uploads_dir.mkdir(exist_ok=True)

        source = Path(file_path)
        dest = uploads_dir / f"{uuid.uuid4().hex[:8]}_{source.name}"
        shutil.copy(file_path, dest)

        span.set_attributes(
            {
                f"input.{media_type}.{index}.url": f"file://{dest.resolve()}",
                f"input.{media_type}.{index}.filename": source.name,
                f"input.{media_type}.{index}.size_bytes": source.stat().st_size,
            }
        )
    except Exception:
        # Tracing must never break the application.
        pass
