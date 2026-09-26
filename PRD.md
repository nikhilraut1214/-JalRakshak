# JalRakshak AI — Product Requirements Document

**Product:** JalRakshak AI  
**Purpose:** hardware-independent water-consumption monitoring, anomaly detection and human verification support.

## 1. Product Principle

> **Analytics detects. Evidence supports. AI explains. Humans verify.**

JalRakshak analyzes water-consumption readings, identifies abnormal patterns, attaches numerical evidence, assigns an analytical risk/severity level, provides a controlled explanation, and guides a human verification workflow.

The platform must never represent an analytical anomaly as physical proof of a leak.

## 2. Problem

Water loss can be difficult to notice when users only see raw consumption readings. A useful MVP should turn time-series consumption into understandable evidence: what is unusual, how persistent it is, how it differs from expected usage, and what should be checked next.

## 3. Target Users

### Resident
Views household consumption, baseline, alerts, evidence and verification guidance for meters they own or are assigned.

### Society / Building Manager
Reviews multiple assigned meters, prioritizes alerts, and uses aggregated consumption insights.

### Farm Operator
Reviews irrigation-related consumption patterns conservatively and in context.

### Institution Administrator
Reviews assigned/group meters, alerts and aggregated consumption insights.

### Administrator
Performs system-level administration and authorized aggregated oversight.

## 4. Primary User Journey

1. Sign in.
2. Access an authorized meter.
3. View or import readings.
4. Establish/view the per-meter baseline when sufficient history exists.
5. Run deterministic analysis.
6. Review deviation, persistence, trend, estimated excess, risk, severity and evidence.
7. If an alert exists, acknowledge it.
8. Enter verification/investigation workflow.
9. Optionally request a natural-language explanation.
10. Human verifies the situation.
11. Mark the appropriate resolution state and close the incident.

## 5. Functional Requirements

### FR-01 Authentication
Users authenticate through the selected authentication provider. For the MVP, **Supabase Auth is the implementation choice**. FastAPI must verify the access token server-side.

### FR-02 Meter Management
Authorized users can list and create meters. Meter access must be enforced by backend authorization.

### FR-03 Reading Ingestion
Support:
- manual/API reading submission;
- CSV upload;
- reproducible synthetic demo scenarios.

Required canonical reading fields:

```json
{
  "meter_id": "uuid",
  "timestamp": "2026-09-26T10:00:00Z",
  "reading_liters": 1860.0
}
```

CSV required columns:

```text
meter_id,timestamp,reading_liters
```

### FR-04 Deterministic Analytics
For sufficient history, the backend computes:
- rolling median baseline;
- MAD;
- robust z-score;
- deviation percentage;
- persistence;
- recent-window trend;
- estimated excess;
- normalized risk score;
- severity.

### FR-05 Insufficient History
There is no universal fixed observation count imposed by this context.

When history is insufficient:
- do not fabricate a baseline;
- do not fabricate anomaly confidence;
- do not produce a misleading authoritative risk score;
- do not create a High/Critical alert solely because history is insufficient;
- return an explicit analytical/data-quality state such as:

```json
{
  "status": "INSUFFICIENT_HISTORY",
  "message": "Not enough historical readings to establish a reliable baseline."
}
```

The backend owns the actual threshold/configuration used to determine sufficiency.

### FR-06 Risk
Risk is a 0–100 analytical prioritization score, not a probability of leakage.

Authoritative weights:

```text
45% deviation
25% persistence
20% trend
10% estimated-loss component
```

Normalization is defined in `architecture.md`.

### FR-07 Alert Lifecycle
Supported states:

```text
DETECTED
ACKNOWLEDGED
VERIFYING
INVESTIGATING
CONFIRMED
FALSE_ALARM
RESOLVED
```

Only documented transitions are allowed. `CONFIRMED` means an authorized human verified the abnormal event through the workflow; it does not mean the algorithm physically proved a leak.

### FR-08 Evidence
Alerts must retain evidence sufficient to explain why they were generated, including relevant readings/baseline, deviation, persistence, trend, estimated excess, risk and severity.

### FR-09 AI Explanation
Groq is an explanation layer only. It may:
- explain supported evidence;
- translate;
- summarize supported interpretations;
- recommend verification actions.

It may not:
- calculate authoritative risk;
- change severity;
- invent readings, timestamps, baselines or savings;
- claim physical inspection;
- confirm a physical leak;
- localize a leak;
- override backend evidence.

If Groq fails, deterministic fallback text must be used.

### FR-10 Languages
Supported explanation/UI languages:

```text
en-IN
mr-IN
hi-IN
```

The numerical evidence must remain identical across languages.

### FR-11 Dashboard
The dashboard may show backend-provided KPIs, charts, alerts, risk and evidence. It must not independently calculate authoritative risk/severity.

### FR-12 Demo Scenarios
Supported scenario identifiers:

```text
NORMAL_HOME
SINGLE_SPIKE
PERSISTENT_LEAK
BURST_USE
FARM_IRRIGATION
DATA_QUALITY
```

Synthetic scenarios must support reproducible seeds and ground-truth labels.

## 6. Authorization Requirements

Roles:

```text
RESIDENT
SOCIETY_MANAGER
FARM_OPERATOR
INSTITUTION_ADMIN
ADMINISTRATOR
```

Permission model:

| Capability | Resident | Society Manager | Farm Operator | Institution Admin | Administrator |
|---|---:|---:|---:|---:|---:|
| View own/assigned meter readings | ✓ | ✓ | ✓ | ✓ | ✓ |
| Create meter | ✓ | ✓ | ✓ | ✓ | ✓ |
| Upload readings | ✓ | ✓ | ✓ | ✓ | ✓ |
| Analyze authorized meter | ✓ | ✓ | ✓ | ✓ | ✓ |
| View group meters | — | ✓ | ✓ | ✓ | ✓ |
| View group alerts | — | ✓ | ✓ | ✓ | ✓ |
| Acknowledge/resolve group alerts | — | ✓ | ✓ | ✓ | ✓ |
| View aggregated community insights | — | ✓ | — | ✓ | ✓ |
| Manage users | — | — | — | limited | ✓ |
| System administration | — | — | — | — | ✓ |

Role alone is insufficient. The backend must also check organization/group membership and meter ownership or assignment.

## 7. Non-Functional Requirements

- deterministic analytics is reproducible for the same inputs/configuration;
- Groq outage must not stop core detection and alerting;
- secrets remain server-side;
- protected APIs require verified authentication;
- authorization is enforced server-side;
- PostgreSQL is the persistence baseline;
- Docker deployment is supported;
- frontend can be deployed to Netlify;
- HTTPS is used in deployment;
- application errors are explicit and actionable;
- raw readings and derived analytics remain distinguishable;
- important alert transitions are auditable.

## 8. Explicit Exclusions

Do not make these MVP requirements:
- Reports subsystem;
- automatic notifications;
- smart-meter hardware dependency;
- weather dependency;
- automatic valve control;
- guaranteed physical leak localization;
- utility billing integration;
- large-scale streaming;
- certified hardware.

## 9. Success Criteria

A complete MVP should allow a judge/user to:

1. authenticate;
2. create/access a meter;
3. ingest readings;
4. run analysis;
5. inspect evidence;
6. see a risk/severity result when history is sufficient;
7. see an explicit insufficient-history state when it is not;
8. receive an alert when configured criteria are met;
9. acknowledge and verify an alert using valid lifecycle transitions;
10. obtain a deterministic or Groq explanation;
11. complete resolution;
12. reproduce demo scenarios.

Metrics such as precision, recall, F1, false alert rate, MAE, alert latency, AI structured-output success, fallback coverage and workflow completion must be reported only when actually measured; otherwise label them **Not yet measured**.
