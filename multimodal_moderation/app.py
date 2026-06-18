"""
OmniTrainer launcher.

Starts three services in parallel:
  1. Arize Phoenix   — observability UI at http://localhost:6006
  2. Moderation API  — FastAPI backend at http://localhost:8000
  3. Chat UI         — Gradio frontend at http://localhost:7860

Usage::

    uv run multimodal-moderation
"""

from __future__ import annotations

import signal
import subprocess
import sys

import phoenix as px


def main() -> None:
    """Launch Phoenix, FastAPI, and Gradio; block until Ctrl-C."""
    session = px.launch_app(port=6006)
    if not session:
        raise RuntimeError("Failed to launch Arize Phoenix session.")

    print(f"🔍  Phoenix UI : {session.url}")
    print("🚀  Starting API and Chat services…")

    api_proc = subprocess.Popen(["multimodal-moderation-api"])
    chat_proc = subprocess.Popen(["multimodal-moderation-chat"])

    def _shutdown(sig: int, frame: object) -> None:
        print("\nShutting down…")
        api_proc.terminate()
        chat_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)

    try:
        api_proc.wait()
        chat_proc.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
