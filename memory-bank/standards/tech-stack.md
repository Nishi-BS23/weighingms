# Tech Stack

## Overview
WeighingMS is a full-stack web application: a Python FastAPI backend holding the weighing domain logic and serving the training Dummy APIs (OrgaTEX, Scale, Scanner, Printer), and a React + TypeScript operator UI that reproduces the supplied prototype (`docs/customize-weighing-station.html`). It runs locally for training; no real OrgaTEX or hardware is connected.

## Languages
**Backend:** Python 3.13
**Frontend:** TypeScript (strict mode)

Python's standard `decimal.Decimal` satisfies NFR-16 (fixed-point arithmetic for all quantities; floating point not permitted) without an extra library, and Pydantic validates `Decimal` fields at the API boundary. TypeScript keeps the operator UI type-checked.

Using two languages means backend and frontend do not share types natively. The FastAPI-generated OpenAPI schema is the single API contract; frontend types are derived from it (approach defined in coding-standards).

## Framework
**Backend:** FastAPI, served by Uvicorn
**Frontend:** React, built with Vite

FastAPI generates an OpenAPI contract and interactive docs from the code, which documents the training Dummy API contracts. Pydantic models validate every request and response. Native WebSocket/SSE support keeps the option open to stream live weight (NFR-01: ≤200 ms display lag; IR-10: ≥10 readings/s) instead of polling; the transport is decided in system architecture / the API contract during Inception.

React components map to the prototype's three views (Select batch, Weigh, Confirm & print) and its repeated widgets (component list, weight readout, tolerance bar, ticket). During development the Vite dev server proxies `/api` to FastAPI.

## Authentication
Simple built-in identification (training-grade):
- Operator identified at session start by badge ID (FR-34)
- Supervisor PIN required for override, manual scale reselection and calibration bypass (FR-35)

No external identity provider. This is not production security. Integration with FCI's real directory remains an open question (Product Brief assumption A-09).

## Infrastructure & Deployment
Local only.
- **`npm run dev` at the repository root is the required start command** (course submission instruction). It starts the FastAPI backend (Uvicorn with reload) and the Vite dev server together, and the terminal prints the URL to open. Vite proxies `/api` to FastAPI, so the operator opens a single URL.
- **Demo / run mode (optional):** a single Uvicorn process serves the built React app and all APIs on one port (default `http://localhost:8000`).

No cloud hosting or containers for now. Docker may be added later if the training environment requires it.

## Package Manager
**Backend:** Poetry, with a project-local `.venv` (do not reuse any other project's virtual environment)
**Frontend:** npm

Both are already installed on the training machine. Poetry provides a lockfile and separates runtime from development/test dependencies.

## Decision Relationships
- **Decimal arithmetic ↔ Python + Pydantic:** quantities are `Decimal` end to end in the backend; the API serialises them in a form that does not lose precision (format defined in coding-standards / API contract).
- **OpenAPI ↔ two languages:** FastAPI's schema is the contract between backend and frontend, and the basis for frontend type generation.
- **Single-port demo ↔ workbook:** satisfies `curl http://localhost:<PORT>/api/...` and "open `http://localhost:<PORT>`" with one URL.
- **Dummy APIs ↔ backend:** the Dummy OrgaTEX, Scale, Scanner and Printer services are implemented in Python/FastAPI. Whether they live in the same process as WeighingMS or separately, and how OrgaTEX access is isolated behind an adapter (IR-07), is decided in system architecture / Inception.
- **Next standards:** data-stack (persistence, likely SQLite) and coding-standards (pytest, Vitest, Playwright, formatting, linting) build on these choices.
