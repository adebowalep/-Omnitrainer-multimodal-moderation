"""
OmniTrainer Moderation API

FastAPI application exposing the four moderation agents as REST endpoints.
All routes require Bearer-token authentication (``USER_API_KEY`` from environment).

Endpoints::

    POST /api/v1/moderate_text          — text moderation
    POST /api/v1/moderate_image_file    — image moderation (multipart upload)
    POST /api/v1/moderate_video_file    — video moderation (multipart upload)
    POST /api/v1/moderate_audio_file    — audio moderation (multipart upload)
    GET  /api/v1/health                 — liveness check

Run directly::

    uv run multimodal-moderation-api
    # or: uvicorn multimodal_moderation.fastapi_app:app --reload
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from multimodal_moderation.agents.audio_agent import moderate_audio
from multimodal_moderation.agents.image_agent import moderate_image
from multimodal_moderation.agents.text_agent import moderate_text
from multimodal_moderation.agents.video_agent import moderate_video
from multimodal_moderation.env import USER_API_KEY, get_default_model_choice
from multimodal_moderation.types.moderation_result import (
    AudioModerationResult,
    ImageModerationResult,
    TextModerationResult,
    VideoModerationResult,
)
from multimodal_moderation.utils import detect_file_type

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
_security = HTTPBearer()


def validate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    """Validate the Bearer token against ``USER_API_KEY``.

    Raises:
        HTTPException: 401 if the token is invalid.
    """
    if credentials.credentials != USER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


# ---------------------------------------------------------------------------
# App and request models
# ---------------------------------------------------------------------------

class TextRequest(BaseModel):
    """Request body for the text moderation endpoint."""
    text: str


app = FastAPI(
    title="OmniTrainer Moderation API",
    description="Multimodal content moderation for ACME customer-service training.",
    version="1.0.0",
    dependencies=[Depends(validate_api_key)],
)

_default_model = get_default_model_choice()

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v1/moderate_text", response_model=TextModerationResult)
async def moderate_text_endpoint(request: TextRequest) -> TextModerationResult:
    """Moderate a plain-text customer-service message."""
    return await moderate_text(_default_model, request.text)


@app.post("/api/v1/moderate_image_file", response_model=ImageModerationResult)
async def moderate_image_file_endpoint(
    file: UploadFile = File(...),
) -> ImageModerationResult:
    """Moderate an uploaded image file."""
    data = await file.read()
    mime = detect_file_type(data, context=file.filename or "image file")
    return await moderate_image(_default_model, data, mime)


@app.post("/api/v1/moderate_video_file", response_model=VideoModerationResult)
async def moderate_video_file_endpoint(
    file: UploadFile = File(...),
) -> VideoModerationResult:
    """Moderate an uploaded video file."""
    data = await file.read()
    mime = detect_file_type(data, context=file.filename or "video file")
    return await moderate_video(_default_model, data, mime)


@app.post("/api/v1/moderate_audio_file", response_model=AudioModerationResult)
async def moderate_audio_file_endpoint(
    file: UploadFile = File(...),
) -> AudioModerationResult:
    """Moderate an uploaded audio file."""
    data = await file.read()
    mime = detect_file_type(data, context=file.filename or "audio file")
    return await moderate_audio(_default_model, data, mime)


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Start the API server (called via the ``multimodal-moderation-api`` script)."""
    import uvicorn

    uvicorn.run(
        "multimodal_moderation.fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
