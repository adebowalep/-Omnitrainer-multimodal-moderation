# OmniTrainer — System Architecture

## Overview

OmniTrainer is a three-tier web application:

| Tier | Component | Technology | Port |
|------|-----------|-----------|------|
| Observability | Arize Phoenix | OpenTelemetry / OTLP | 6006 |
| Backend | Moderation API | FastAPI + Uvicorn | 8000 |
| Frontend | Chat UI | Gradio | 7860 |

All three are started together by `uv run multimodal-moderation` (see `app.py`).

---

## Component Deep-Dive

### Moderation Agents (`multimodal_moderation/agents/`)

Four independent [Pydantic AI](https://ai.pydantic.dev/) agents, each backed by Google Gemini:

| Agent | Input | Key flags |
|-------|-------|-----------|
| `text_agent` | Plain text | `contains_pii`, `is_unfriendly`, `is_unprofessional` |
| `image_agent` | Raw image bytes (multimodal) | `contains_pii`, `is_disturbing`, `is_low_quality` |
| `video_agent` | Raw video bytes (multimodal) | `contains_pii`, `is_disturbing`, `is_low_quality` |
| `audio_agent` | Raw audio bytes (multimodal) + transcription | `contains_pii`, `is_unfriendly`, `is_unprofessional`, `transcription` |

All agents share the ACME company context/role preamble from `agents/_shared.py`, avoiding duplication. Each agent produces a typed Pydantic model (see `types/moderation_result.py`).

### Customer Simulation Agent (`agents/customer_agent.py`)

A Pydantic AI agent that roleplays an upset ACME customer. Created at module level so a single model instance is shared across all chat sessions. Configured with `instrument=True` so Pydantic AI automatically emits an `llm_customer` span.

### REST API (`fastapi_app.py`)

FastAPI app with four `POST` endpoints plus a health check. All routes require `Authorization: Bearer <USER_API_KEY>`. The `_default_model` is instantiated at startup from environment config.

### Chat UI (`gradio_app.py`)

Gradio `Blocks` layout with:
- `ChatSessionWithTracing` — holds a root `conversation` span across all turns
- `check_content_safety()` — routes text or media to the FastAPI backend and checks unsafe flags
- `chat_with_gemini()` — per-turn handler: moderate → (if safe) forward to customer agent → return reply

Span hierarchy produced per turn:
```
conversation
└── chat_turn
    ├── moderate_text  (or moderate_image / moderate_audio / moderate_video)
    └── feedback       (only if content was flagged)
        llm_customer   (only if content was safe)
```

### Tracing (`tracing.py`)

- `setup_tracing()` — registers a global `TracerProvider` with two processors:
  - `OpenInferenceSpanProcessor` — enriches AI spans with LLM-specific attributes
  - `SimpleSpanProcessor + OTLPSpanExporter` — ships traces to Phoenix at `PHOENIX_URL`
- `add_media_to_span()` — copies uploaded files to `./uploaded_media/` and records `file://` URLs on the span so Phoenix can display thumbnails

### Configuration (`env.py`)

Environment variables are read with `os.getenv(…, "")` at import time (no raises). Validation only happens inside `get_default_model_choice()` at runtime. This design allows the module to be safely imported in tests without a `.env` file.

---

## Request Lifecycle

```
Trainee types "Hello" + uploads photo.jpg
        │
        ▼
Gradio chat_with_gemini()
  ├── [text] check_content_safety(text="Hello")
  │     └── POST /api/v1/moderate_text  →  TextModerationResult(is_unfriendly=False …)
  └── [file] check_content_safety(media="photo.jpg")
        ├── detect_file_type("photo.jpg") → "image/jpeg"
        └── POST /api/v1/moderate_image_file  →  ImageModerationResult(contains_pii=True …)
              ↓  content flagged
        return feedback to trainee (NOT sent to customer agent)
```

---

## Testing Strategy

| Layer | Tool | Notes |
|-------|------|-------|
| Agent unit tests | `pytest` + `pydantic_ai.models.test.TestModel` | No API calls; validates schema and return types |
| API endpoint tests | `pytest` + `httpx.AsyncClient` (ASGI transport) | No real server needed |
| Utility tests | `pytest` | Tests `detect_file_type` with real binary files |
| Evaluation | `pydantic_evals` | Requires Gemini API key; measures real accuracy |

`tests/conftest.py` sets dummy credentials before any import, making the entire `pytest tests/` suite runnable without a `.env` file.
