# TestHub — AI-assisted Test Platform

## Summary

TestHub is a project that combines:

- FastAPI backend (users, projects, bugs, auth)
- React + Vite frontend
- Pytest API tests and Playwright UI tests
- AI helpers (Gemini integration) to generate API/UI tests and analyze failures

This repository is intended as a local experimentation environment for building, testing, and enhancing test automation using classical and AI-assisted techniques.

## Repository root

Top-level folders:

- backend/ — FastAPI application, DB models, CRUD, routes, AI-related API routes
- frontend/ — React + Vite frontend and unit tests (Vitest + Testing Library)
- ai_tools/ — AI utilities (Gemini wrapper, test generators, failure analyzer)
- tests/ — End-to-end tests (api/ and ui/)
- reports/ — Test run reports (HTML, JUnit XML)
- requirements.txt — Python deps
- frontend/.env — frontend environment (API base URL)
- .env (repo root) — backend env (GEMINI_API_KEY, etc.)

## High-level architecture

- Backend: FastAPI application exposing REST endpoints for auth, projects, bugs, AI endpoints.
  - Uses SQLAlchemy for models (SQLite by default).
  - JWT-based auth with OAuth2 password flow.
  - AI endpoints call ai_tools to generate tests using the OpenAPI schema and Gemini (if configured).
- Frontend: React + Vite
  - Lightweight UI components for auth, projects, bugs, AI dashboard.
  - apiClient wrapper used to call backend endpoints.
  - Unit tests with Vitest + Testing Library.
- Tests:
  - tests/api: pytest API tests using an APIClient wrapper and fixtures.
  - tests/ui: pytest-playwright UI tests using Playwright page objects.
  - Generated UI tests (ai) saved under tests/ui/generated/.
- AI tooling:
  - ai_tools/gemini_client.py — wrapper for Google Generative AI (Gemini).
  - ai_tools/test_generator.py — creates candidate API tests from OpenAPI.
  - ai_tools/ui_test_generator.py — inspects a live UI with Playwright and generates Playwright test code.
  - ai_tools/ai_test_executor.py — (executor skeleton) run/generated API tests automatically.
  - ai_tools/failure_analyzer.py — parse JUnit XML & produce a human-friendly analysis via Gemini.

## Quick start (Windows)

Prereqs:

- Python 3.10+
- Node 16+
- npm or yarn
- (Optional) Playwright browsers for UI tests
- (Optional) Gemini API key for AI features

1. Clone & enter repo

- Open PowerShell / CMD:
  cd C:\Users\Yash2.Garg\testhub

2. Python environment & dependencies

- Create & activate virtualenv:
  - PowerShell:
    .venv\Scripts\Activate.ps1
  - cmd.exe:
    .venv\Scripts\activate.bat
- Install Python packages:
  pip install -r requirements.txt

3. Backend configuration

- Place environment variables in `.env` at repo root or set them in the environment.
  Required/important keys:
  - GEMINI_API_KEY (only if you want AI features)
  - SQLALCHEMY_DATABASE_URL (optional; default: sqlite:///./testhub.db)
  - JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES (defaults are provided)
- Start backend (reload mode):
  uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

4. Frontend

- Install JS deps:
  cd frontend
  npm install
- Start dev server:
  npm run dev
- By default the frontend expects the backend at http://127.0.0.1:8000 (see frontend/.env)

5. Playwright (for UI tests / inspection)

- From repo root:
  npx playwright install
- Run Playwright tests via pytest:
  pytest tests/ui

## Running tests

- API tests:
  pytest tests/api

  - Tests read config from tests/api/config/config.yaml (base_url etc.)
  - Uses tests/api/utils/api_client.py and fixtures in tests/api/conftest.py

- UI tests (pytest + pytest-playwright):
  pytest tests/ui

  - Page objects are in tests/ui/pages/
  - Generated UI tests appear under tests/ui/generated/

- Frontend unit tests (Vitest):
  cd frontend
  npm run test # or npx vitest

## Test reports

- HTML and JUnit outputs (if configured) are located under the `reports/` folder:
  - reports/api-report.html
  - reports/api-results.xml
  - reports/ui-report.html

## Key files & brief descriptions

Backend

- backend/main.py — app bootstrap, router registration
- backend/core/config.py — pydantic settings (env_file .env)
- backend/core/security.py — password hashing and JWT token creation
- backend/db/session.py — SQLAlchemy engine and Base
- backend/models/\*.py — SQLAlchemy models (User, Project, Bug, TestRun)
- backend/schemas/\*.py — Pydantic request/response schemas
- backend/crud/\*.py — DB helper functions for entities
- backend/api/routes/\*.py — FastAPI routes including AI routes (ai_tests, ai_ui_tests, ai_dashboard)

Frontend

- frontend/src/App.jsx — root component / auth / token handling
- frontend/src/apiClient.js — fetch wrapper for the backend
- frontend/src/components/\* — UI components (AuthSection, ProjectsPanel, BugsPanel, AiDashboard)
- frontend/vite.config.js & frontend/src/setupTests.js — Vitest config / setup

AI tooling

- ai_tools/gemini_client.py — configure & return Gemini model wrapper (requires GEMINI_API_KEY)
- ai_tools/test_generator.py — fetch OpenAPI and create test-case suggestions
- ai_tools/ui_test_generator.py — Playwright-based UI inspection and test code generation
- ai_tools/ai_test_executor.py — execute AI-generated tests against the running API (skeleton)
- ai_tools/failure_analyzer.py — parse JUnit XML and analyze failures via Gemini (skeleton)

Tests & fixtures (high level)

- tests/api/conftest.py — session fixtures (config, base_url, api_client, auth fixtures)
- tests/api/utils/api_client.py — thin wrapper for requests to the API under test
- tests/api/test\_\*.py — functional API tests (auth, projects, bugs lifecycle)
- tests/ui/pages/\* — Playwright page objects used by UI tests
- tests/ui/test_e2e_bug_flow.py — example end-to-end UI scenario

## Database & migrations

- Default: SQLite (SQLALCHEMY_DATABASE_URL default in backend/core/config.py)
- For production or CI consider using Postgres or another server DB.
- Alembic is included in requirements.txt; migrations are not fully scaffolded in this demo. If you add alembic config, migrate with alembic upgrade head.

## AI / Gemini usage

- Gemini integration is used in ai_tools/gemini_client.py. The project expects `GEMINI_API_KEY` available to the backend process (via `.env` or system env).
- If the key is missing, attempts to obtain a Gemini model will raise an error.
- The AI endpoints in the backend are:
  - GET /ai/generate-tests — generate candidate API tests (uses OpenAPI)
  - POST /ai/ui/generate-tests — generate Playwright UI test code for a URL
  - Extra endpoints under /ai/dashboard for orchestration and execution

## Developer notes & TODOs (observations from workspace)

- Several ai_tools modules (ai_test_executor.py, test_generator.py, ui_test_generator.py, failure_analyzer.py) include scaffolds/skeletons that need completion before full AI/test execution works.
- Backend routes for projects, bugs, auth, and ai-dashboard contain decorators and signatures; some route bodies are incomplete and need implementation.
- Some CRUD helpers and schemas include placeholder or incomplete implementations.
- Tests include useful fixtures but rely on fully-implemented API endpoints.
- Frontend components contain ellipses in code summarizations — ensure components import and react hooks (useState, useEffect) are included if missing.
- The repo contains an example `.env` with a GEMINI_API_KEY — rotate and remove any real keys before sharing.

## Troubleshooting & hints

- Backend fails to start (DB errors): check SQLALCHEMY_DATABASE_URL and migrations / Base.metadata.create_all.
- Playwright tests flaky: add explicit waits / increase timeouts; ensure the frontend server and backend are reachable.
- AI endpoints failing: confirm GEMINI_API_KEY is set and network access to Gemini is allowed.
- Frontend tests (Vitest) complaining about jsdom: ensure vite.config.js test.environment is "jsdom" and setupFiles points to src/setupTests.js.
