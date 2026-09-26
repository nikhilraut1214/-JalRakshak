# JalRakshak AI — Development Rules

**Authority:** Final Technical Document + explicit implementation decisions in this context package.

## 0. Rule Hierarchy

1. Final Technical Document
2. PRD
3. Architecture
4. Rules
5. Phases
6. Design
7. Memory

`memory.md` records state; it cannot override requirements.

If a coding agent encounters an ambiguity resolved in `architecture.md`, use that decision consistently.

## 1. Product Boundary

MVP:
- hardware-independent;
- water-consumption monitoring;
- deterministic anomaly/evidence/risk;
- alert workflow;
- controlled AI explanation;
- human verification.

Not MVP requirements:
- physical leak proof;
- automatic valve control;
- certified leak localization;
- utility billing;
- weather dependency;
- smart-meter dependency;
- notifications;
- Reports subsystem;
- large-scale streaming.

## 2. Backend Authority

The backend is the source of truth for:
- baseline;
- deviation;
- persistence;
- trend;
- estimated excess;
- risk score;
- severity;
- alert status;
- evidence;
- dashboard analytical totals.

Frontend may format, visualize and filter returned data, but must not create a competing authoritative calculation.

## 3. API Rules

Use REST + JSON and the canonical endpoints from `architecture.md`.

Success:

```json
{"data": {}, "error": null}
```

Error:

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

Do not expose stack traces or secrets.

## 4. Authentication Rules

MVP authentication choice: **Supabase Auth**.

Required flow:

```text
Supabase Auth → JWT → FastAPI verification → authorization → resource
```

Never:
- trust frontend-supplied user identity;
- trust frontend-only roles;
- expose `SUPABASE_SERVICE_ROLE_KEY`;
- use service-role credentials in browser code.

## 5. Authorization Rules

Roles:

```text
RESIDENT
SOCIETY_MANAGER
FARM_OPERATOR
INSTITUTION_ADMIN
ADMINISTRATOR
```

Authorization is:

```text
role + organization/group membership + ownership/assignment + action
```

Do not authorize based on role alone.

Never trust client-supplied `owner_id`, `organization_id`, `group_id`, or equivalent security fields.

## 6. Reading Validation

Validate server-side:
- required fields;
- timestamp;
- units;
- finite numeric value;
- non-negative consumption where appropriate;
- meter existence;
- access to meter;
- duplicates;
- CSV schema and file size.

Client validation improves UX but never replaces backend validation.

## 7. Analytics Rules

Baseline:

```text
rolling median + MAD
```

Robust z:

```text
(current - median) / (1.4826 × MAD + ε)
```

Deviation:

```text
((current - median) / max(median, ε)) × 100
```

Estimated excess:

```text
max(observed - expected, 0) × persistence_intervals
```

Risk:

```text
45% deviation
25% persistence
20% trend
10% loss
```

Severity:

```text
0–39   LOW
40–69  MEDIUM
70–84  HIGH
85–100 CRITICAL
```

Risk is not leak probability.

## 8. Risk Normalization Rules

Deviation:

```text
clamp(deviation_pct, 0, 100)
```

Persistence:

```text
1 → 25
2 → 50
3 → 75
4+ → 100
```

Trend:

```text
clamp(normalized_positive_trend × 100, 0, 100)
```

Loss:

```text
clamp(estimated_excess_liters / loss_reference_liters × 100, 0, 100)
```

Final:

```text
0.45D + 0.25P + 0.20T + 0.10L
```

Clamp final score to 0–100.

The loss reference and trend normalization are backend configuration, not frontend constants.

## 9. Insufficient-History Rules

There is no universal fixed observation count.

When insufficient history:
- do not invent a baseline;
- do not invent confidence;
- do not calculate misleading authoritative risk;
- do not generate High/Critical solely because of insufficient history;
- expose an explicit state/message.

Example:

```text
INSUFFICIENT_HISTORY
Not enough historical readings to establish a reliable baseline.
```

The persistence mapping is a risk-score component only; it does not define minimum history.

## 10. Alert Lifecycle Rules

Allowed transitions only:

```text
DETECTED → ACKNOWLEDGED
ACKNOWLEDGED → VERIFYING
VERIFYING → CONFIRMED
VERIFYING → FALSE_ALARM
VERIFYING → INVESTIGATING
INVESTIGATING → RESOLVED
CONFIRMED → RESOLVED
FALSE_ALARM → RESOLVED
```

Reject every other transition.

`CONFIRMED` is a human workflow outcome, not an AI result.

Do not auto-confirm a physical leak.

## 11. AI Rules

AI may:
- explain;
- translate;
- summarize supported interpretations;
- recommend verification actions.

AI may not:
- calculate authoritative risk;
- modify severity;
- invent readings;
- invent baselines;
- invent timestamps;
- invent savings;
- claim physical inspection;
- confirm physical leakage;
- localize leakage;
- override backend evidence.

Validate Groq output with Pydantic.

Fallback deterministically on:
- timeout;
- unavailable API;
- malformed output;
- schema validation failure;
- missing configuration.

## 12. Language Rules

Supported:

```text
en-IN
mr-IN
hi-IN
```

Translation must not change:
- numbers;
- units;
- timestamps;
- risk score;
- severity;
- evidence values.

## 13. Synthetic Scenario Rules

Allowed:

```text
NORMAL_HOME
SINGLE_SPIKE
PERSISTENT_LEAK
BURST_USE
FARM_IRRIGATION
DATA_QUALITY
```

Each reproducible scenario should record:
- scenario name;
- seed;
- generated readings;
- ground truth.

Do not call a synthetic `PERSISTENT_LEAK` result proof of a real leak.

## 14. UI Rules

Evidence first.

Show:
- current reading;
- expected/baseline;
- deviation;
- persistence;
- trend;
- estimated excess;
- risk + severity;
- verification requirement.

Never imply:
- risk score = probability;
- AI = sensor;
- estimate = measured physical loss;
- confirmation = automated proof.

Never use color alone to convey severity.

## 15. Memory Rules

Update `memory.md` only with actual repository state.

Use:
- `PLANNED` for not-yet-built items;
- `IMPLEMENTED` only after verified implementation;
- `TESTED` only after actual tests;
- `DECIDED` for locked design/implementation choices.

Do not claim deployment, authentication, metrics or tests are complete merely because the context says they should be.

## 16. Testing Rules

Required coverage should include:
- analytics unit tests;
- schema tests;
- API auth/authorization tests;
- lifecycle transition tests;
- CSV ingestion tests;
- integration flow;
- AI malformed/timeout/fallback tests;
- frontend critical workflow tests;
- E2E scenario-to-resolution test.

## 17. Scope Guard

Do not add Reports, notifications, weather, maps, hardware control, utility billing, or leak localization as MVP requirements.

If a new capability is useful but outside scope, document it as future work rather than silently expanding the MVP.
