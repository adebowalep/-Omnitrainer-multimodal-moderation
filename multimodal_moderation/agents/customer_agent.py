"""
Customer Simulation Agent

Simulates an ACME Enterprise customer who is upset about a malfunctioning product.
Used by the Gradio training interface so that trainee agents can practice handling
difficult customer interactions.

The agent is intentionally instantiated at module level so the model is created once
and shared across all chat sessions.
"""

from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.capabilities import Instrumentation
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider

from multimodal_moderation.env import GEMINI_API_KEY, DEFAULT_GOOGLE_MODEL

_SYSTEM_PROMPT = """\
ROLE
You are an ACME Enterprise customer contacting support about a faulty product.

SCENARIO
Your ACME Power Widget Pro stopped working without explanation and you want a full
refund.  You might accept an alternative offer if the agent is persuasive enough —
consider anything 2–3× more valuable than your original purchase.

BEHAVIOUR
- Start out mildly over-the-top but never abusive.
- If the agent remains polite and professional, gradually calm down.
- Keep your responses concise.
"""

_gemini_model = GoogleModel(
    DEFAULT_GOOGLE_MODEL,
    provider=GoogleProvider(api_key=GEMINI_API_KEY),
)
_model_settings = GoogleModelSettings(google_thinking_config={"thinking_budget": 0})

customer_agent: Agent[None, str] = Agent(
    system_prompt=_SYSTEM_PROMPT,
    output_type=str,
    model=_gemini_model,
    model_settings=_model_settings,
    capabilities=[Instrumentation()],
)
