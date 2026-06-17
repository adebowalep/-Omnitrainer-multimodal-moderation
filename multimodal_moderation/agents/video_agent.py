"""
Video Moderation Agent

Analyses video for disturbing content, PII, and quality issues using a Pydantic AI
multimodal agent backed by Google Gemini.
"""

from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from multimodal_moderation.agents._shared import ACME_CONTEXT
from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import VideoModerationResult

_INSTRUCTIONS = (
    ACME_CONTEXT
    + """
<input>
You will receive a video submitted during a customer-service interaction.
</input>

<instructions>
Determine whether the video:
  - is disturbing in any way
  - shows a person's face or any other personally-identifiable information (PII)
  - is predominantly low quality (low-resolution, blurry, pixelated, under- or
    over-exposed).  Ignore incidental low-quality segments that are not the majority
    of the video.
</instructions>

<output>
Set the appropriate boolean flags and provide a detailed rationale explaining your decision.
</output>
"""
)

video_moderation_agent: Agent[None, VideoModerationResult] = Agent(
    system_prompt=_INSTRUCTIONS,
    output_type=VideoModerationResult,
)


async def moderate_video(
    model_choice: ModelChoice,
    video_source: bytes,
    media_type: str,
) -> VideoModerationResult:
    """
    Run the video moderation agent on raw video bytes.

    Args:
        model_choice: Model and settings to use for this call.
        video_source: Raw video data.
        media_type: MIME type of the video (e.g. ``"video/mp4"``).

    Returns:
        A :class:`VideoModerationResult` with flags and rationale.
    """
    video_input = BinaryContent(data=video_source, media_type=media_type)
    result = await video_moderation_agent.run(
        ["Analyse this video for harmful content.", video_input],
        message_history=[],
        model=model_choice.model,
        model_settings=model_choice.model_settings,
    )
    return result.output
