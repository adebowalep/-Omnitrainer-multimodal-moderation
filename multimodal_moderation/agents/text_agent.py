"""
Text Moderation Agent

Analyses customer-service messages for unfriendly tone, unprofessional language,
and personally-identifiable information (PII) using a Pydantic AI agent backed by
Google Gemini.
"""

from __future__ import annotations

from pydantic_ai import Agent

from multimodal_moderation.agents._shared import ACME_CONTEXT
from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import TextModerationResult

_INSTRUCTIONS = (
    ACME_CONTEXT
    + """
<input>
You will receive a message written by a customer-service representative to a customer.
</input>

<instructions>
Analyse the message and detect whether it:
  - has an unfriendly tone
  - uses unprofessional language
  - contains personally-identifiable information (PII)
</instructions>

<output>
Set the appropriate boolean flags and provide a detailed rationale explaining your decision.
</output>
"""
)

text_moderation_agent: Agent[None, TextModerationResult] = Agent(
    system_prompt=_INSTRUCTIONS,
    output_type=TextModerationResult,
)


async def moderate_text(model_choice: ModelChoice, text: str) -> TextModerationResult:
    """
    Run the text moderation agent on *text*.

    Args:
        model_choice: Model and settings to use for this call.
        text: The customer-service message to moderate.

    Returns:
        A :class:`TextModerationResult` with flags and rationale.
    """
    result = await text_moderation_agent.run(
        f"Analyse this customer-service message for moderation:\n\n{text}",
        model=model_choice.model,
        model_settings=model_choice.model_settings,
    )
    return result.output
