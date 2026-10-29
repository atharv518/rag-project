# RAG Project

A multi-tenant public, personal, and enterprise AI/RAG knowledge platform.

> **Status:** Phase 1 Complete — Project scaffold, database foundation, structured logging, error handling, health checks, and Critical Privacy Gate.

---

## Architecture Overview

```
User
 ├── Public AI / Guest       (no login, anonymous quota)
 ├── Personal AI             (authenticated, personal workspace, no org required)
 └── Organization AI         (tenant-scoped, RBAC-filtered, enterprise-governed)
```

- **Backend:** FastAPI (Python 3.11+), SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Database:** Supabase managed PostgreSQL with `pgvector`
- **Frontend:** Vite + React + TypeScript + Tailwind CSS
- **LLM Provider:** Google Gemini API (`gemini-2.0-flash`)
- **Embedding Provider:** Google Gemini (`gemini-embedding-001` with 768 MRL dimensions)
- **Object Storage:** Supabase Storage (private buckets)
- **Background Jobs:** FastAPI BackgroundTasks (MVP) with planned Celery/Redis queue abstraction

---

## Critical Privacy Gate

> [!IMPORTANT]
> **Free-tier External AI Provider Data Handling Policy:**
> - Gemini API free tier is permitted **only** with synthetic, public, or explicitly approved non-confidential test data.
> - Confidential organizational documents, personal data, and PII are strictly prevented from reaching unpaid AI providers.
> - Upgrading to an approved paid enterprise tier with contractual zero-data-retention is required before live organization tenants are onboarded.

---

## Quick Start (Local Setup)

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- Supabase Project with `pgvector` enabled (`CREATE EXTENSION IF NOT EXISTS vector;`)
- Google AI Studio API Key

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
# Activate:
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase connection string and Gemini API key

# Run migrations to create database schema
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

Verify backend health:
```bash
curl http://localhost:8000/api/v1/health
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

---

## Running Automated Tests

```bash
cd backend
pytest
```
