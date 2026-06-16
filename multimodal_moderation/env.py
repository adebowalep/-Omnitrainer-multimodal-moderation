"""
Application configuration loaded from environment variables / .env file.

Design decision — no module-level raises:
    We read env vars with safe defaults at import time so that importing this module
    for type-checking or testing never fails.  Validation (raising ValueError for
    missing credentials) happens only inside ``get_default_model_choice()``, which is
    called at runtime when the app actually needs to talk to the Gemini API.

Required at runtime (set in .env or environment):
    GEMINI_API_KEY       -- Google Gemini API key
    USER_API_KEY         -- Bearer token accepted by the FastAPI service
    DEFAULT_GOOGLE_MODEL -- Gemini model name (e.g. "gemini-2.5-flash-lite")

Optional:
    API_BASE_URL      -- Base URL of the FastAPI service (default: http://localhost:8000)
    PHOENIX_URL       -- Arize Phoenix tracing URL  (default: http://127.0.0.1:6006)
    EVAL_JUDGE_MODEL  -- Model used as LLM judge in evals (defaults to DEFAULT_GOOGLE_MODEL)
    EVAL_NUM_REPEATS  -- How many times each eval case is repeated (default: 1)
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider

from multimodal_moderation.types.model_choice import ModelChoice

load_dotenv()

# ---------------------------------------------------------------------------
# Credentials -- empty string if not set; validated lazily at call time
# ---------------------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
USER_API_KEY: str = os.getenv("USER_API_KEY", "")
DEFAULT_GOOGLE_MODEL: str = os.getenv("DEFAULT_GOOGLE_MODEL", "gemini-2.5-flash-lite")

# ---------------------------------------------------------------------------
# Optional / non-sensitive config
# ---------------------------------------------------------------------------
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
PHOENIX_URL: str = os.getenv("PHOENIX_URL", "http://127.0.0.1:6006")
EVAL_JUDGE_MODEL: str = os.getenv("EVAL_JUDGE_MODEL", DEFAULT_GOOGLE_MODEL)
EVAL_NUM_REPEATS: int = int(os.getenv("EVAL_NUM_REPEATS", "1"))


def get_default_model_choice() -> ModelChoice:
    """
    Build the default :class:`ModelChoice` from the current environment.

    Raises:
        ValueError: If ``GEMINI_API_KEY`` or ``DEFAULT_GOOGLE_MODEL`` are not set.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required but not set")
    if not DEFAULT_GOOGLE_MODEL:
        raise ValueError("DEFAULT_GOOGLE_MODEL environment variable is required but not set")

    return ModelChoice(
        model=GoogleModel(
            DEFAULT_GOOGLE_MODEL,
            provider=GoogleProvider(api_key=GEMINI_API_KEY),
        ),
        model_settings=GoogleModelSettings(google_thinking_config={"thinking_budget": 0}),
    )
