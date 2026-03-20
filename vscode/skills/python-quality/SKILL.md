---
name: python-quality
description: "Python quality patterns — type hints, project structure, virtual environments, testing, error handling, logging"
---

# Python Quality Patterns

Opinionated patterns for Python projects. Use when writing or reviewing Python code.

## Project Structure

```
my-project/
├── src/
│   └── myproject/          # Package with __init__.py
│       ├── __init__.py
│       ├── main.py         # Entry point
│       ├── services/       # Business logic
│       ├── models/         # Data classes, Pydantic models
│       ├── api/            # FastAPI/Flask routes
│       └── utils/          # Shared utilities
├── tests/
│   ├── conftest.py         # Shared fixtures
│   ├── test_services.py
│   └── test_api.py
├── pyproject.toml          # Project metadata, dependencies, tool config
└── .python-version         # Pin Python version
```

Use `pyproject.toml` for everything — NOT `setup.py`, `setup.cfg`, or `requirements.txt` (except for Docker).

## Type Hints — Always

```python
# CORRECT — fully typed
def get_user_by_id(user_id: int) -> User | None:
    ...

def process_jobs(jobs: list[Job], *, max_retries: int = 3) -> ProcessResult:
    ...

# WRONG — no type hints
def get_user_by_id(user_id):
    ...
```

- Use `from __future__ import annotations` for modern syntax in Python 3.9+.
- Use `TypeAlias` for complex types.
- Use `TypedDict` for dictionary shapes.
- Use Pydantic `BaseModel` for validated data structures.

## Pydantic for Data Validation

```python
from pydantic import BaseModel, Field

class CreateJobRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    priority: int = Field(ge=1, le=5, default=3)
    tags: list[str] = Field(default_factory=list)

# FastAPI validates automatically
@app.post("/jobs")
async def create_job(request: CreateJobRequest) -> JobResponse:
    ...
```

Do NOT manually validate with if-checks when Pydantic can do it declaratively.

## Error Handling

```python
# CORRECT — specific exceptions, meaningful messages
class JobNotFoundError(Exception):
    def __init__(self, job_id: int):
        super().__init__(f"Job {job_id} not found")
        self.job_id = job_id

# WRONG
raise Exception("not found")  # Too generic
raise ValueError("error")      # Wrong exception type
```

- Define custom exceptions for domain errors.
- Catch specific exceptions — never bare `except:` or `except Exception:` without re-raising.
- Let unexpected exceptions propagate — the framework handles them.

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# CORRECT — structured, with context
logger.info("Processing job", extra={"job_id": job.id, "priority": job.priority})
logger.error("Job failed", exc_info=True, extra={"job_id": job.id})

# WRONG
print(f"Processing job {job.id}")       # Use logger, not print
logger.info(f"Processing {job}")         # Use extra dict, not f-strings in messages
```

Use `__name__` for logger names. Use `extra` for structured context. Do NOT use f-strings in log messages — they prevent log aggregation.

## Async

```python
# CORRECT — async for I/O-bound operations
async def fetch_jobs(client: httpx.AsyncClient) -> list[Job]:
    response = await client.get("/api/jobs")
    response.raise_for_status()
    return [Job(**j) for j in response.json()]

# WRONG — sync HTTP in async context
def fetch_jobs():
    response = requests.get("/api/jobs")  # Blocks the event loop
```

- Use `httpx` (async) instead of `requests` (sync) in async code.
- Use `asyncio.gather()` for concurrent I/O, not sequential awaits.
- Do NOT mix sync and async — pick one per module.

## Testing

```python
# tests/conftest.py — shared fixtures
import pytest

@pytest.fixture
def job_service(db_session):
    return JobService(session=db_session)

# tests/test_services.py
class TestJobService:
    async def test_create_job(self, job_service):
        job = await job_service.create(name="Test Job")
        assert job.name == "Test Job"
        assert job.id is not None

    async def test_create_job_empty_name_fails(self, job_service):
        with pytest.raises(ValidationError):
            await job_service.create(name="")
```

- Use `pytest` — not `unittest`.
- Use fixtures for setup — not `setUp()` methods.
- Test names describe expected behavior: `test_create_job_empty_name_fails`.
- Use `pytest.raises` for expected exceptions.

## Dependency Management

```toml
# pyproject.toml
[project]
dependencies = [
    "fastapi>=0.100",
    "pydantic>=2.0",
    "httpx>=0.25",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "mypy>=1.10",
]
```

- Use `uv` or `pip-tools` for dependency resolution.
- Pin major versions, allow minor updates.
- Separate dev dependencies from runtime.
- Run `ruff` for linting and formatting (replaces flake8, isort, black).
- Run `mypy` for type checking.
