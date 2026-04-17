# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run tests
pytest test_main.py -v

# Health check
curl http://127.0.0.1:8000/health
```

## Architecture

This is a **FastAPI** demographic analysis API that accepts a name and returns predicted gender, age, and nationality by concurrently calling three external services (genderize.io, agify.io, nationalize.io), then persists the result to MongoDB Atlas.

### Request flow for `POST /api/profiles`

1. Validate and normalize name (strip non-alpha chars, lowercase)
2. Fire three async calls in parallel via `asyncio.gather`: `fetch_genderize_property`, `fetch_Agify_property`, `fetch_nationalize_property`
3. Merge results with `config/model.py:extract_gender()`
4. Persist to MongoDB (`config/database.py` — collection `users` in database `hng14_1`)
5. Return 201 with the stored profile

### Directory layout

- `main.py` — app factory, lifespan (rate limiter init), all route handlers
- `core/` — `config.py` (pydantic Settings from `.env`), `exceptions.py` (custom exception hierarchy), `error_handlers.py` (global FastAPI exception handlers)
- `services/` — one file per external API (`genderize_service.py`, `agify_service.py`, `nationalize_service.py`) plus `http_client.py` (shared httpx AsyncClient with HTTP/2, 1.5 s timeout)
- `config/` — `database.py` (MongoDB client), `schema.py` (Pydantic `profile` model), `model.py` (`extract_gender`, `create_profile` transformers)

### Key conventions

- External HTTP calls go through `services/http_client.py:safe_http_request()` — never call httpx directly in a service.
- All service failures raise `ExternalServiceException` (→ 502). Input errors raise `BadRequestException` (400) or `UnprocessableException` (422).
- Rate limit: 8 requests/minute per IP via SlowAPI, enforced on `POST /api/profiles`.
- Age groupings: child ≤ 12, teenager 13–19, adult 20–59, senior 60+.

## Environment

Requires a `.env` file at the repo root:

```
GENDERIZE_API="https://api.genderize.io"
AGIFY_API="https://api.agify.io"
NATIONALIZE_API="https://api.nationalize.io"
```

MongoDB URI is currently hardcoded in `config/database.py` — move it to `.env` before deploying to a new environment.
