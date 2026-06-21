# Contributing to OmniTrainer

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/your-username/omnitrainer.git
cd omnitrainer
uv sync --dev
uv pip install -e .
cp .env.example .env   # fill in your GEMINI_API_KEY
```

## Running Tests

Tests require no credentials — `conftest.py` sets up dummy env vars and all agent calls are intercepted by `TestModel`.

```bash
uv run pytest tests/ -v
```

## Code Style

```bash
uv run black .
uv run isort .
uv run flake8 .
```

## Pull Request Guidelines

1. Fork and create a feature branch from `main`
2. Add tests for any new behaviour
3. Ensure `pytest tests/ -v` passes with zero failures
4. Run the formatters before opening a PR
5. Keep PRs focused — one logical change per PR

## Adding a New Moderation Agent

1. Add a new result type in `multimodal_moderation/types/moderation_result.py`
2. Create `multimodal_moderation/agents/<modality>_agent.py` following the pattern in existing agents; import `ACME_CONTEXT` from `_shared.py`
3. Add a FastAPI endpoint in `fastapi_app.py`
4. Wire up content routing in `gradio_app.py`
5. Add unit tests in `tests/test_<modality>_agent.py` and API tests in `tests/test_api.py`
6. Add an eval suite under `evals/<modality>/`

## Reporting Issues

Please open a GitHub issue describing the problem, steps to reproduce, and the Python / dependency versions you are using.
