"""
Tests for multimodal_moderation.utils.detect_file_type.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from multimodal_moderation.utils import detect_file_type


def test_detect_image_from_bytes(test_data_dir: Path) -> None:
    data = (test_data_dir / "simple_image.jpg").read_bytes()
    mime = detect_file_type(data, context="simple_image.jpg")
    assert mime.startswith("image/"), f"Expected image/* MIME, got {mime}"


def test_detect_audio_from_bytes(test_data_dir: Path) -> None:
    data = (test_data_dir / "simple_audio.mp3").read_bytes()
    mime = detect_file_type(data, context="simple_audio.mp3")
    assert mime.startswith("audio/"), f"Expected audio/* MIME, got {mime}"


def test_detect_video_from_bytes(test_data_dir: Path) -> None:
    data = (test_data_dir / "simple_video.mp4").read_bytes()
    mime = detect_file_type(data, context="simple_video.mp4")
    assert mime.startswith("video/"), f"Expected video/* MIME, got {mime}"


def test_detect_file_from_path(test_data_dir: Path) -> None:
    path = str(test_data_dir / "simple_image.jpg")
    mime = detect_file_type(path, context=path)
    assert mime.startswith("image/")


def test_detect_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        detect_file_type(b"not a real file", context="fake.bin")
