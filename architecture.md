# JalRakshak AI — Architecture

**Architecture source:** `JalRakshak_AI_Final_Technical_Document.docx`  
**Role:** implementation architecture plus locked interface/behavior contracts.

## 0. Source-of-Truth Rule

The technical document is authoritative. This file operationalizes it and records explicit implementation decisions where the source permits a choice.

**Implementation decisions in this file are not claims that the technical document specified them.**

---

## 1. Architecture Principles

1. Deterministic analytics is authoritative for numerical evidence and risk.
2. Evidence is assembled before AI explanation.
3. AI explains; it does not detect or physically confirm leaks.
4. Human verification is part of the incident workflow.
5. The MVP is hardware-independent.
6. Secrets remain server-side.
7. Numerical evidence is identical across supported languages.
8. Core detection and alerting continue when Groq is unavailable.
9. Raw readings and derived analytics remain distinguishable.
10. Synthetic scenarios provide reproducible evaluation ground truth.
11. Frontend never becomes the authority for analytical values.
12. Authorization is enforced on the backend for every protected resource.

## 2. Technology Baseline

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TypeScript |
| Styling | Tailwind CSS |
| Charts | Recharts or Apache ECharts |
| Routing | React Router |
| Client validation | Zod |
| API | FastAPI + Uvicorn |
| Validation | Pydantic |
| Analytics | Pandas + NumPy + scikit-learn |
| Database | PostgreSQL |
| ORM/migrations | SQLAlchemy/SQLModel + Alembic |
| AI | Groq API |
| Authentication | **Supabase Auth — locked MVP implementation choice** |
| Containerization | Docker |
| Frontend hosting | Netlify baseline |
| Backend hosting | Docker-compatible host |
| Database hosting | Managed PostgreSQL |

## 3. High-Level Architecture

```text
React/Vite/TypeScript
        │ HTTPS + JSON
        ▼
FastAPI
 ├── JWT verification
 ├── RBAC/resource authorization
 ├── request validation
 └── application API
        │
        ├───────────────┐
        ▼               ▼
   PostgreSQL      Analytics/Evidence
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     baseline       anomaly/risk    forecast
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 Alert lifecycle
                       │
                       ▼
             Evidence packet → Groq
                       │           │
                       │       fallback
                       ▼           ▼
                    Explanation
                       │
                       ▼
                Human verification
```

## 4. Backend Module Boundaries

- `auth`: Supabase JWT verification and identity extraction.
- `authorization`: role + organization/group + ownership/assignment checks.
- `meters`: meter CRUD/access.
- `readings`: validated ingestion and history.
- `analytics`: baseline, anomaly features, persistence, trend, risk, excess, forecasting.
- `evidence`: canonical evidence packet.
- `alerts`: lifecycle and transitions.
- `explanations`: Groq + Pydantic validation + deterministic fallback.
- `scenarios`: seeded synthetic data.
- `audit`: important state transitions.

## 5. Authentication Boundary — Locked Implementation Decision

Flow:

```text
Supabase Auth
     ↓
access JWT
     ↓
FastAPI JWT verification
     ↓
authenticated user identity
     ↓
role + organization/group + resource authorization
     ↓
application resource
```

Conceptual server configuration:

```text
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
```

Rules:
- service-role credentials are backend-only;
- the frontend never receives the service-role key;
- FastAPI never trusts a client-supplied `user_id` as the authenticated identity;
- role information supplied only by the frontend is never trusted;
- every protected endpoint derives the authenticated identity from the verified token.

The exact JWT verification library/mechanism is an implementation detail, but verification must be cryptographically/server-side valid for the configured Supabase project.

## 6. Authorization Model — Locked Implementation Decision

A request is authorized only after all relevant checks pass:

```text
authenticated?
    ↓
role allowed?
    ↓
organization/group membership valid?
    ↓
meter/resource owned or assigned to user/group?
    ↓
action permitted?
```

A role does not automatically grant access to every meter.

Never trust `owner_id`, `organization_id`, or similar authorization fields supplied by the client.

## 7. Analytics

### 7.1 Baseline

Use rolling median and MAD.

```text
median = rolling_median(history)
MAD = median(abs(history - median))

robust_z = (current - median) / (1.4826 × MAD + ε)

deviation_pct = ((current - median) / max(median, ε)) × 100
```

### 7.2 Insufficient History — Locked Behavior

No universal fixed observation count is imposed.

The backend determines whether history is sufficient using configurable analytical rules.

When insufficient:

```json
{
  "status": "INSUFFICIENT_HISTORY",
  "message": "Not enough historical readings to establish a reliable baseline."
}
```

Do not:
- fabricate baseline;
- fabricate anomaly confidence;
- fabricate risk;
- create High/Critical alert solely from insufficient history.

A data-quality/insufficient-history status may be displayed to the user.

### 7.3 Persistence

Count consecutive abnormal intervals according to the configured anomaly threshold.

For risk normalization only:

```text
1 interval → 25
2 intervals → 50
3 intervals → 75
4+ intervals → 100
```

This is **not** a minimum-history requirement.

### 7.4 Trend

Use the recent-window slope. Convert the positive normalized trend into a 0–100 component:

```text
trend_score = clamp(normalized_positive_trend × 100, 0, 100)
```

The normalization constant/configuration is backend-owned.

### 7.5 Estimated Excess

```text
estimated_excess_liters =
    max(observed_liters - expected_liters, 0)
    × persistence_intervals
```

This is an analytical estimate, not a physical measurement of leaked water.

## 8. Risk Normalization — Locked Implementation Decision

All four components are 0–100.

### Deviation

```text
deviation_score =
    clamp(deviation_pct, 0, 100)
```

Thus 0–100% deviation maps directly to 0–100 score and anything above 100% is capped.

### Persistence

```text
1 → 25
2 → 50
3 → 75
4+ → 100
```

### Trend

```text
trend_score = clamp(normalized_positive_trend × 100, 0, 100)
```

### Estimated loss

Use a backend-configured reference amount:

```text
loss_score =
    clamp(
      estimated_excess_liters / loss_reference_liters × 100,
      0,
      100
    )
```

`loss_reference_liters` is configuration, not a frontend constant.

### Final risk

```text
risk_score =
    0.45 × deviation_score
  + 0.25 × persistence_score
  + 0.20 × trend_score
  + 0.10 × loss_score

risk_score = clamp(risk_score, 0, 100)
```

Risk is analytical prioritization, not leak probability.

## 9. Severity

```text
LOW       0–39
MEDIUM   40–69
HIGH     70–84
CRITICAL 85–100
```

Severity is generated by the backend from the authoritative risk score.

## 10. Evidence Model

A canonical evidence object should include, where available:

```json
{
  "current_usage_liters": 1860.0,
  "baseline_liters": 1040.0,
  "deviation_pct": 78.3,
  "persistence_intervals": 4,
  "trend": "increasing",
  "estimated_excess_liters": 820.0,
  "risk_score": 91,
  "severity": "CRITICAL",
  "verification_required": true
}
```

Possible causes must remain interpretations, not physical facts.

## 11. Alert Lifecycle — Locked Transition Matrix

Allowed states:

```text
DETECTED
ACKNOWLEDGED
VERIFYING
INVESTIGATING
CONFIRMED
FALSE_ALARM
RESOLVED
```

Allowed transitions only:

```text
DETECTED       → ACKNOWLEDGED
ACKNOWLEDGED   → VERIFYING
VERIFYING      → CONFIRMED
VERIFYING      → FALSE_ALARM
VERIFYING      → INVESTIGATING
INVESTIGATING  → RESOLVED
CONFIRMED      → RESOLVED
FALSE_ALARM    → RESOLVED
```

All other transitions are invalid and must be rejected by the backend.

`CONFIRMED` means an authorized human has confirmed the abnormal event through the workflow. It does not mean the software has physically proven a leak.

## 12. API Contract

All application APIs use REST + JSON.

### Standard success envelope

```json
{
  "data": {},
  "error": null
}
```

### Standard error envelope

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

Do not expose internal stack traces in API responses.

### Canonical endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | health |
| GET | `/api/meters` | authorized meters |
| POST | `/api/meters` | create meter |
| GET | `/api/meters/{id}/readings` | meter history |
| POST | `/api/readings` | single reading |
| POST | `/api/readings/upload` | CSV |
| POST | `/api/analyze/{meter_id}` | analysis |
| GET | `/api/alerts` | alerts + filters |
| GET | `/api/alerts/{id}` | alert + evidence |
| POST | `/api/alerts/{id}/acknowledge` | acknowledge |
| POST | `/api/alerts/{id}/resolve` | lifecycle transition |
| POST | `/api/explain` | explanation |
| POST | `/api/demo/scenario` | seeded scenario |
| GET | `/api/dashboard/summary` | dashboard summary |

### Meter create

```json
{
  "name": "Home Meter 01",
  "location_label": "Building A",
  "meter_type": "water"
}
```

### Reading create

```json
{
  "meter_id": "uuid",
  "timestamp": "2026-09-26T10:00:00Z",
  "reading_liters": 1860.0
}
```

### CSV

Required columns:

```text
meter_id,timestamp,reading_liters
```

### Analyze

`POST /api/analyze/{meter_id}` has no required body.

The backend performs:

```text
history validation
→ baseline
→ anomaly features
→ persistence
→ trend
→ estimated excess
→ risk
→ severity
→ evidence
→ alert decision
```

### Alert filters

`GET /api/alerts` supports:

```text
meter_id
severity
status
from
to
```

### Resolve/transition request

```json
{
  "resolution": "CONFIRMED",
  "note": "User verified abnormal consumption."
}
```

Allowed `resolution` values:

```text
CONFIRMED
FALSE_ALARM
RESOLVED
```

The backend must validate whether the requested transition is legal from the current state. If the implementation needs `INVESTIGATING`, it must be entered through the defined workflow and then resolved.

### Explain request

```json
{
  "alert_id": "uuid",
  "language": "en-IN"
}
```

Response data includes:

```json
{
  "alert_id": "uuid",
  "language": "en-IN",
  "explanation": "...",
  "source": "groq"
}
```

`source` is either `groq` or `deterministic`.

### Demo scenario request

```json
{
  "scenario": "PERSISTENT_LEAK",
  "seed": 42,
  "meter_id": "uuid"
}
```

Allowed scenarios:

```text
NORMAL_HOME
SINGLE_SPIKE
PERSISTENT_LEAK
BURST_USE
FARM_IRRIGATION
DATA_QUALITY
```

### Dashboard authority

Dashboard statistics returned by the backend are authoritative. The frontend may format/display them but must not independently recompute risk, severity, estimated excess or alert status as a second source of truth.

## 13. AI Architecture

Groq receives a structured evidence packet.

Allowed:
- explanation;
- translation;
- summary of supported interpretations;
- verification recommendation.

Forbidden:
- numerical recalculation as authority;
- changing risk/severity;
- inventing evidence;
- physical confirmation;
- leak localization;
- guaranteed savings.

Pydantic validates structured model output before it is returned.

Fallback is deterministic and must work when Groq is:
- unavailable;
- unconfigured;
- timed out;
- malformed;
- rejected by schema validation.

`GROQ_API_KEY` is server-side only.

## 14. Forecasting

Forecasting is an estimation feature, not a detection proof.

Baseline MVP options from the technical source:

```text
rolling mean / EWMA
```

Optional improvement:

```text
seasonal naive by day/time bucket
```

Forecast evaluation uses MAE where applicable.

## 15. Database Entities

```text
users
meters
readings
alerts
alert_evidence
explanations
audit_events
```

Important requirements:
- consistent timestamp convention;
- explicit units;
- indexed meter/time queries;
- raw vs derived data distinction;
- auditable lifecycle transitions.

## 16. Security

- verify authentication server-side;
- enforce resource authorization server-side;
- validate all input;
- reject oversized/malformed CSV;
- avoid SQL injection via parameterized ORM/database access;
- do not expose service-role or Groq secrets;
- use HTTPS in deployment;
- log important security/workflow events without leaking secrets.

## 17. Deployment

Baseline:

```text
Frontend → Netlify
Backend  → Docker-compatible host
Database → managed PostgreSQL
```

Local judging fallback:

```text
Docker Compose / local Docker
```

Environment configuration must be documented and secrets must not be committed.
