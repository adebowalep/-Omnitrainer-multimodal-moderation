"""
ModelChoice — a simple container that pairs a Pydantic AI :class:`~pydantic_ai.models.Model`
with its :class:`~pydantic_ai.settings.ModelSettings` so both can be threaded through the
moderation pipeline as a single argument.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings


class ModelChoice(BaseModel):
    """Bundles a Pydantic AI model instance with its call-time settings."""

    model: Model | str
    model_settings: ModelSettings | None = None

    # Required because pydantic_ai.models.Model is an abstract class, not a plain dict.
    model_config = ConfigDict(arbitrary_types_allowed=True)
