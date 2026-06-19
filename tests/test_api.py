"""
Tests for the FastAPI moderation endpoints.

Uses ``httpx.AsyncClient`` with the ASGI transport so no real server is needed.
All agents are overridden with ``TestModel`` so no Gemini API calls are made.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai.models.test import TestModel

from multimodal_moderation.agents.audio_agent import audio_moderation_agent
from multimodal_moderation.agents.image_agent import image_moderation_agent
from multimodal_moderation.agents.text_agent import text_moderation_agent
from multimodal_moderation.agents.video_agent import video_moderation_agent
from multimodal_moderation.fastapi_app import app


_AUTH = {"Authorization": "Bearer test-user-api-key"}


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health_check(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health", headers=_AUTH)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_moderate_text_endpoint(client: AsyncClient) -> None:
    with text_moderation_agent.override(model=TestModel()):
        resp = await client.post(
            "/api/v1/moderate_text",
            json={"text": "Hello, how can I help you today?"},
            headers=_AUTH,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "rationale" in data
    assert "contains_pii" in data
    assert "is_unfriendly" in data
    assert "is_unprofessional" in data


async def test_moderate_image_endpoint(client: AsyncClient, test_data_dir: Path) -> None:
    image_bytes = (test_data_dir / "simple_image.jpg").read_bytes()
    with image_moderation_agent.override(model=TestModel()):
        resp = await client.post(
            "/api/v1/moderate_image_file",
            files={"file": ("simple_image.jpg", image_bytes, "image/jpeg")},
            headers=_AUTH,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "is_disturbing" in data
    assert "is_low_quality" in data


async def test_moderate_audio_endpoint(client: AsyncClient, test_data_dir: Path) -> None:
    audio_bytes = (test_data_dir / "simple_audio.mp3").read_bytes()
    with audio_moderation_agent.override(model=TestModel()):
        resp = await client.post(
            "/api/v1/moderate_audio_file",
            files={"file": ("simple_audio.mp3", audio_bytes, "audio/mpeg")},
            headers=_AUTH,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "transcription" in data


async def test_moderate_video_endpoint(client: AsyncClient, test_data_dir: Path) -> None:
    video_bytes = (test_data_dir / "simple_video.mp4").read_bytes()
    with video_moderation_agent.override(model=TestModel()):
        resp = await client.post(
            "/api/v1/moderate_video_file",
            files={"file": ("simple_video.mp4", video_bytes, "video/mp4")},
            headers=_AUTH,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "is_disturbing" in data


async def test_invalid_api_key_rejected(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/moderate_text",
        json={"text": "Hello"},
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert resp.status_code == 401
