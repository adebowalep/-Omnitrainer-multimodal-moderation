"""
Image Moderation Agent

Analyses images for disturbing content, PII (faces / identifiable details), and
quality issues using a Pydantic AI multimodal agent backed by Google Gemini.
"""

from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from multimodal_moderation.agents._shared import ACME_CONTEXT
from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import ImageModerationResult

_INSTRUCTIONS = (
    ACME_CONTEXT
    + """
<input>
You will receive an image submitted during a customer-service interaction.
</input>

<instructions>
Determine whether the image:
  - is disturbing in any way
  - contains a person, part of a person, or any other personally-identifiable
    information (PII) — if so, set contains_pii to True
  - is of low quality (blurry, pixelated, under- or over-exposed, etc.)
</instructions>

<output>
Set the appropriate boolean flags and provide a detailed rationale explaining your decision.
</output>
"""
)

image_moderation_agent: Agent[None, ImageModerationResult] = Agent(
    system_prompt=_INSTRUCTIONS,
    output_type=ImageModerationResult,
)


async def moderate_image(
    model_choice: ModelChoice,
    image_source: bytes,
    media_type: str,
) -> ImageModerationResult:
    """
    Run the image moderation agent on raw image bytes.

    Args:
        model_choice: Model and settings to use for this call.
        image_source: Raw image data.
        media_type: MIME type of the image (e.g. ``"image/jpeg"``).

    Returns:
        An :class:`ImageModerationResult` with flags and rationale.
    """
    image_input = BinaryContent(data=image_source, media_type=media_type)
    result = await image_moderation_agent.run(
        ["Analyse this image for harmful content.", image_input],
        model=model_choice.model,
        model_settings=model_choice.model_settings,
    )
    return result.output
