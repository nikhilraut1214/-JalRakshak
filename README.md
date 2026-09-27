# JalRakshak AI — AI-Assisted Water Consumption Monitoring & Early Warning Platform

Hardware-independent water-consumption early-warning and decision-support platform.

> **Core Principle:** Analytics detects. Evidence supports. AI explains. Humans verify.

---

## 1. Architecture & Boundaries

* **Frontend:** React + Vite + TypeScript (SPA)
* **Backend:** FastAPI (Python 3.11+)
* **Database:** PostgreSQL (production / Docker) or SQLite (local development default)
* **AI Explanation:** Groq LLM (bounded natural-language explanation with deterministic multilingual offline fallbacks)
* **Authentication & Authorization:** Supabase Auth (JWT cryptographic signature verification) with strict RBAC (Resident, Operator, Admin) and meter ownership scoping
* **Telemetry Ingestion:** REST JSON API & chunked CSV upload with schema validation, rate-limiting, and atomicity
* **Localization:** Trilingual support for English (`en-IN`), Marathi (`mr-IN`), and Hindi (`hi-IN`)

### MVP Boundary & Safety Disclaimers
* JalRakshak is a decision-support system, not an automated shutoff or physical leak localization tool.
* Anomaly alerts represent a **suspected anomaly** or **possible leak**; physical on-site inspection is required.
* Potential water savings are analytical projections based on user-configured assumption fractions; they are never presented as guaranteed physical measurements.

---

## 2. Prerequisites

* **Node.js:** v18.0.0+ (v20+ recommended) and `npm`
* **Python:** 3.11+
* **Database:** PostgreSQL 15+ (for production) or Docker / Docker Compose, or SQLite (for quick local development)
* **Environment Configuration:** `.env` file copied from `.env.example`

---

## 3. Backend Setup

### 3.1 Virtual Environment & Dependencies

```bash
# Navigate to repository root
cd JalRakshyak

# Create and activate Python virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt
```

### 3.2 Environment Configuration

Copy the example environment file and configure variables:

```bash
cp .env.example .env
```

Key environment variables:
* `DATABASE_URL`: `sqlite:///./jalrakshak.db` (local dev) or `postgresql://user:pass@host:5432/dbname` (production)
* `ENVIRONMENT`: `development` or `production`
* `SUPABASE_JWT_SECRET`: High-entropy secret for JWT signature verification (required >= 32 chars in production)
* `GROQ_API_KEY`: Groq API key for natural language explanations (optional; deterministic fallback active if omitted)
* `ALLOWED_ORIGINS`: Comma-separated CORS origins (e.g. `http://localhost:3000,http://127.0.0.1:3000` or production frontend URL)

### 3.3 Database Migrations

Apply Alembic migrations to set up or update the database schema:

```bash
# Run migrations to latest revision
alembic upgrade head

# Verify zero schema drift
alembic check
```

### 3.4 Startup Command

```bash
# Run FastAPI with live reload
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be accessible at `http://localhost:8000`. Health check is available at `GET /api/health`.

---

## 4. Frontend Setup

### 4.1 Dependency Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 4.2 API URL Configuration

* **Local Development:** By default, Vite proxies `/api` requests to `http://localhost:8000`. No extra configuration needed.
* **Production Build:** If frontend is hosted separately from the backend (e.g., Netlify), set `VITE_API_URL` to your backend domain:
  ```bash
  cp .env.example .env.production
  # In .env.production or Netlify UI environment variables:
  VITE_API_URL=https://api.yourdomain.com
  ```

### 4.3 Development Server

```bash
npm run dev
```

Frontend runs at `http://localhost:3000`.

### 4.4 Production Build

```bash
npm run build
```

Compiled assets are written to `frontend/dist/`.

---

## 5. End-to-End Demonstration Flow

The platform is designed to be demonstrated completely through the user interface and APIs without requiring developer-only database interventions:

1. **Sign In:** Navigate to `/login`. Use one of the pre-seeded demo personas (Resident, Utility Operator, Municipal Admin) to obtain a cryptographically signed JWT.
2. **Establish / Select Meter:** On the **Meters** tab, view authorized meters or register a new meter (`POST /api/meters`).
3. **Show Normal Usage:** View baseline consumption, median, and median absolute deviation (MAD) on the Dashboard.
4. **Run Synthetic Scenario:** Navigate to **Scenario Lab**. Select a standard canonical scenario (e.g., `PERSISTENT_LEAK`, `BURST_USE`, `SINGLE_SPIKE`, `FARM_IRRIGATION`) and click **Run Scenario**.
5. **Show Evidence:** Inspect the structured deterministic evidence packet showing:
   * Observed consumption vs. Expected baseline
   * Deviation percentage
   * Persistence intervals
   * Trend direction
   * Estimated excess liters
6. **Show Risk / Severity:** View the objective 0–100 risk score and associated severity level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
7. **Generate Explanation:** Click **Generate Explanation** to view the structured explanation. If Groq is configured, the LLM explains what changed citing exact evidence; if offline or unconfigured, the deterministic fallback renders instantly.
8. **Switch Language:** Use the language selector in the header to switch to Marathi (`mr-IN`) or Hindi (`hi-IN`). All copy, labels, and explanations adapt while numbers remain immutable.
9. **Follow Verification Workflow:** Review the on-site physical verification checklist (fixture checks, zero-consumption meter tests, line inspection).
10. **Acknowledge / Resolve:** Follow lifecycle actions: transition alert from `DETECTED` → `ACKNOWLEDGED` → `VERIFYING` → `CONFIRMED` / `INVESTIGATING` → `RESOLVED`.
11. **Show Estimated Impact:** On the **Water Impact** view, adjust the avoided-fraction slider to see projected avoided water loss, financial impact estimates, and equivalency metrics (20L cans saved).

---

## 6. Testing & Quality Assurance

Run the test suite and validation gates across the codebase:

```bash
# 1. Backend Python Unit & Security Regression Tests
pytest -v

# 2. Database Schema Migration Verification
alembic check

# 3. Frontend Code Quality & Linter
cd frontend
npm run lint

# 4. Frontend Type Check & Production Build
npm run build
```

---

## 7. Deployment Configuration

### 7.1 Frontend Deployment (Target: Netlify)
* **Build Command:** `npm run build`
* **Publish Directory:** `dist`
* **Base Directory:** `frontend`
* **Environment Variables:** Set `VITE_API_URL=https://<your-backend-api-domain>`
* **SPA Routing:** Configured via `netlify.toml` and `frontend/public/_redirects` (`/*  /index.html  200`).

### 7.2 Backend Deployment (Target: Dockerized FastAPI)
Build and run the production container:

```bash
# Build the backend container image
docker build -f backend/Dockerfile -t jalrakshak-backend .

# Run container with environment configuration
docker run -d \
  -p 8000:8000 \
  --name jalrakshak-backend \
  -e DATABASE_URL="postgresql://user:password@postgres-host:5432/jalrakshak_db" \
  -e ENVIRONMENT="production" \
  -e SUPABASE_JWT_SECRET="your-production-jwt-secret-at-least-32-chars" \
  -e ALLOWED_ORIGINS="https://your-frontend.netlify.app" \
  -e GROQ_API_KEY="your-groq-key" \
  jalrakshak-backend
```

### 7.3 Full-Stack Docker Compose (Local & Self-Hosted)
Run all three tiers (PostgreSQL + FastAPI backend + Nginx frontend) simultaneously:

```bash
docker compose up -d --build
```
* Frontend: `http://localhost:3000`
* Backend API: `http://localhost:8000`
* Database: PostgreSQL on port `5432`

---

## 8. Safety & Compliance Rules

* **Analytics First:** Analytics detects. Evidence supports. AI explains. Humans verify.
* **No Software Confirmations:** Software never states that a physical leak is confirmed or localized.
* **Deterministic Numbers:** AI never calculates, generates, or alters numerical evidence, risk scores, or water volumes.
* **Zero Leakage:** No credentials or API keys exist in source control. All production secrets must be supplied via server-side environment variables.
