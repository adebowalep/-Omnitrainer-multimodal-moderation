"""
Pydantic output schemas for the OmniTrainer moderation agents.

Hierarchy::

    ModerationResult          (base — common fields shared by all agents)
    ├── TextModerationResult  (text-specific flags)
    ├── ImageModerationResult (image-specific flags)
    ├── VideoModerationResult (video-specific flags)
    └── AudioModerationResult (audio-specific flags + transcription)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModerationResult(BaseModel):
    """Shared fields returned by every moderation agent."""

    rationale: str = Field(
        description="Explanation of what was found and why the content was or was not flagged."
    )
    contains_pii: bool = Field(
        default=False,
        description="Whether the content contains personally-identifiable information (PII).",
    )
    is_unfriendly: bool = Field(
        default=False,
        description="Whether an unfriendly tone or message was detected.",
    )
    is_unprofessional: bool = Field(
        default=False,
        description="Whether unprofessional language or behaviour was detected.",
    )

    def is_flagged(self) -> bool:
        """Return ``True`` if any moderation flag is set."""
        return self.contains_pii or self.is_unfriendly or self.is_unprofessional


class TextModerationResult(ModerationResult):
    """Moderation result for plain-text customer-service messages."""

    contains_pii: bool = Field(
        description="Whether the message contains personally-identifiable information (PII)."
    )
    is_unfriendly: bool = Field(
        description="Whether an unfriendly tone was detected."
    )
    is_unprofessional: bool = Field(
        description="Whether unprofessional language was detected."
    )


class ImageModerationResult(ModerationResult):
    """Moderation result for image content."""

    contains_pii: bool = Field(
        description=(
            "Whether the image shows a person, part of a person, or any other "
            "personally-identifiable information (PII)."
        )
    )
    is_disturbing: bool = Field(
        description="Whether the image is disturbing or inappropriate."
    )
    is_low_quality: bool = Field(
        description="Whether the image is of low quality (blurry, pixelated, poor exposure, etc.)."
    )

    def is_flagged(self) -> bool:
        return self.contains_pii or self.is_disturbing or self.is_low_quality


class VideoModerationResult(ModerationResult):
    """Moderation result for video content."""

    contains_pii: bool = Field(
        description=(
            "Whether the video shows a person or personally-identifiable information (PII)."
        )
    )
    is_disturbing: bool = Field(
        description="Whether the video contains disturbing or inappropriate content."
    )
    is_low_quality: bool = Field(
        description="Whether the majority of the video is of low quality."
    )

    def is_flagged(self) -> bool:
        return self.contains_pii or self.is_disturbing or self.is_low_quality


class AudioModerationResult(ModerationResult):
    """Moderation result for audio content (includes transcription)."""

    transcription: str = Field(
        description="Full transcription of the audio content."
    )
    contains_pii: bool = Field(
        description=(
            "Whether the audio contains personally-identifiable information (PII) "
            "such as names, addresses, or phone numbers."
        )
    )
    is_unfriendly: bool = Field(
        description="Whether an unfriendly tone was detected in the audio."
    )
    is_unprofessional: bool = Field(
        description="Whether unprofessional language was detected in the audio."
    )
