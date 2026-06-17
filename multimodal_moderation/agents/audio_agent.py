"""
Audio Moderation Agent

Transcribes audio and analyses it for unfriendly/unprofessional content and PII
using a Pydantic AI multimodal agent backed by Google Gemini.
"""

from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from multimodal_moderation.agents._shared import ACME_CONTEXT
from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import AudioModerationResult

_INSTRUCTIONS = (
    ACME_CONTEXT
    + """
<input>
You will receive an audio recording from a customer-service interaction.
</input>

<instructions>
1. Provide an accurate transcription of the audio.
2. Analyse the transcription and detect whether it:
   - has an unfriendly tone
   - uses unprofessional language
   - contains personally-identifiable information (PII) such as names, addresses,
     or phone numbers
</instructions>

<output>
Return the full transcription, set the appropriate boolean flags, and provide a
detailed rationale explaining your moderation decision.
</output>
"""
)

audio_moderation_agent: Agent[None, AudioModerationResult] = Agent(
    system_prompt=_INSTRUCTIONS,
    output_type=AudioModerationResult,
)


async def moderate_audio(
    model_choice: ModelChoice,
    audio_source: bytes,
    media_type: str,
) -> AudioModerationResult:
    """
    Run the audio moderation agent on raw audio bytes.

    Args:
        model_choice: Model and settings to use for this call.
        audio_source: Raw audio data.
        media_type: MIME type of the audio (e.g. ``"audio/mpeg"``).

    Returns:
        An :class:`AudioModerationResult` with transcription, flags, and rationale.
    """
    audio_input = BinaryContent(data=audio_source, media_type=media_type)
    result = await audio_moderation_agent.run(
        ["Analyse this audio for harmful content.", audio_input],
        message_history=[],
        model=model_choice.model,
        model_settings=model_choice.model_settings,
    )
    return result.output
