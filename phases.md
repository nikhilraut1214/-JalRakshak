# JalRakshak AI — Development Phases

The sequence below is designed to produce one complete, reliable MVP and keeps implementation decisions aligned with the context package.

## Phase 0 — Foundation

### Goal
Create a reproducible repository and runtime foundation.

### Tasks
- React/Vite/TypeScript shell;
- FastAPI/Uvicorn;
- PostgreSQL;
- Docker;
- Alembic;
- environment configuration;
- shared API schemas/types where useful;
- `/api/health`;
- base README.

### Exit
Fresh clone can start locally with documented setup; migrations work; no secrets committed.

---

## Phase 1 — Authentication, Authorization, Meters and Ingestion

### Goal
Securely establish the data path.

### Tasks
- Supabase Auth;
- JWT verification;
- role/resource authorization;
- meter creation/listing;
- reading submission;
- CSV upload;
- Pydantic validation;
- PostgreSQL persistence;
- ownership/group access checks.

### Canonical API

```text
GET  /api/meters
POST /api/meters
GET  /api/meters/{id}/readings
POST /api/readings
POST /api/readings/upload
```

### Exit
Authorized users can only access authorized meters; valid readings persist; invalid input produces useful errors.

---

## Phase 2 — Deterministic Analytics and Alerts

### Goal
Implement the numerical core before AI.

### Tasks
- rolling median;
- MAD;
- robust z-score;
- deviation;
- persistence;
- trend;
- estimated excess;
- risk normalization;
- severity;
- insufficient-history guard;
- evidence;
- alert creation;
- optional advisory Isolation Forest only if time permits.

### Canonical formulas

```text
robust_z = (current - median) / (1.4826 × MAD + ε)

deviation_pct = ((current - median) / max(median, ε)) × 100

estimated_excess =
    max(observed - expected, 0) × persistence_intervals
```

### Risk

```text
0.45 × deviation_score
+ 0.25 × persistence_score
+ 0.20 × trend_score
+ 0.10 × loss_score
```

### Severity

```text
LOW       0–39
MEDIUM   40–69
HIGH     70–84
CRITICAL 85–100
```

### Canonical API

```text
POST /api/analyze/{meter_id}
GET  /api/alerts
GET  /api/alerts/{id}
```

### Exit
Same input/configuration produces reproducible analytics; insufficient history is explicit; alerts carry evidence.

---

## Phase 3 — Dashboard and Alert Workflow

### Goal
Make the analytical result usable.

### Tasks
- dashboard KPIs;
- consumption/baseline chart;
- alert list and filters;
- incident detail;
- evidence view;
- acknowledge;
- verifying/investigating;
- confirm/false-alarm;
- resolve;
- audit events.

### State machine

```text
DETECTED → ACKNOWLEDGED → VERIFYING
                         ├→ CONFIRMED → RESOLVED
                         ├→ FALSE_ALARM → RESOLVED
                         └→ INVESTIGATING → RESOLVED
```

### Exit
A user can complete the workflow without direct database edits.

---

## Phase 4 — Forecasting and Impact Estimation

### Goal
Add documented estimates without confusing them with measured evidence.

### Tasks
- rolling mean/EWMA;
- optional seasonal naive day/time bucket;
- MAE evaluation;
- estimated excess display;
- potential savings using explicit avoided-fraction assumption.

```text
potential_savings_liters =
    estimated_excess_liters × avoided_fraction
```

### Exit
Every forecast/savings value is labeled as an estimate/assumption.

---

## Phase 5 — Groq Explanation and Multilingual Experience

### Goal
Add AI without moving numerical authority into the model.

### Tasks
- structured evidence packet;
- Groq API integration;
- Pydantic response validation;
- deterministic fallback;
- explanation;
- verification recommendation;
- English/Marathi/Hindi;
- language-preserving numerical evidence.

### Canonical API

```text
POST /api/explain
```

### Exit
Groq success and failure paths both work; no model output can override backend evidence.

---

## Phase 6 — Synthetic Evaluation, Testing and Deployment

### Goal
Make the MVP reproducible and demo-ready.

### Scenarios

```text
NORMAL_HOME
SINGLE_SPIKE
PERSISTENT_LEAK
BURST_USE
FARM_IRRIGATION
DATA_QUALITY
```

### Tasks
- seeded generator;
- ground truth;
- development/validation split;
- precision;
- recall;
- F1;
- false alert rate;
- alert latency;
- MAE where applicable;
- AI structured-output success;
- fallback coverage;
- workflow completion;
- unit/schema/integration/API/frontend/E2E/AI-contract tests;
- security/dependency review;
- Docker deployment;
- Netlify frontend;
- managed PostgreSQL;
- local Docker judging fallback;
- final rehearsal.

### Exit
Measured results are shown honestly; unmeasured metrics say **Not yet measured**; complete demo repeats reliably.

---

## Recommended Dependency Order

```text
Foundation
   ↓
Auth + Authorization + Ingestion
   ↓
Core Analytics
   ↓
Evidence + Alerts + Dashboard
   ├──────────────→ Groq + Multilingual
   └──────────────→ Forecasting/Impact
                    ↓
              Synthetic Evaluation
                    ↓
             Testing + Deployment
```

Groq must not block deterministic analytics.

---

## Seven-Day Mapping

| Day | Primary deliverable |
|---|---|
| 1 | repository, architecture, Docker, DB schema, React shell |
| 2 | Supabase Auth, authorization, meters, readings, CSV |
| 3 | baseline, anomaly engine, risk, evidence, alerts |
| 4 | dashboard, charts, alert lifecycle |
| 5 | Groq explanation, fallback, multilingual UI |
| 6 | synthetic generator, evaluation, tests |
| 7 | deployment, polish, complete demo |

If time is limited, prioritize one complete reliable workflow over advanced analytics or excluded features.

## Phase Completion Rule

A phase is complete only when:
- implementation exists;
- critical behavior works;
- errors are handled;
- relevant tests exist;
- design is consistent;
- documentation is updated;
- `memory.md` reflects actual state.
