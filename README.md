# JalRakshak AI — AI Coding Agent Context

This directory contains the implementation context for JalRakshak AI.

## Source of Truth

The authoritative product source is:

`JalRakshak_AI_Final_Technical_Document.docx`

These context files operationalize that document. Where the technical document leaves an implementation detail open, the decisions explicitly marked **Implementation Decision** in this package make the choice deterministic for an AI coding agent. They must not be mistaken for claims that the technical document itself specified that choice.

## Read Order

1. `PRD.md`
2. `architecture.md`
3. `rules.md`
4. `phases.md`
5. `design.md`
6. `memory.md`

`CHANGELOG_ALIGNMENT.md` records what was changed in this reconciliation.

## Core Invariant

> **Analytics detects. Evidence supports. AI explains. Humans verify.**

## MVP Boundary

JalRakshak is a hardware-independent water-consumption early-warning and decision-support platform. It does not physically prove leaks, control infrastructure, guarantee savings, provide certified leak localization, or require smart-meter hardware.

## Canonical Workflow

```text
DETECT → EVIDENCE → EXPLAIN → VERIFY → RESOLVE
```

## Canonical API

```text
GET  /api/health
GET  /api/meters
POST /api/meters
GET  /api/meters/{id}/readings
POST /api/readings
POST /api/readings/upload
POST /api/analyze/{meter_id}
GET  /api/alerts
GET  /api/alerts/{id}
POST /api/alerts/{id}/acknowledge
POST /api/alerts/{id}/resolve
POST /api/explain
POST /api/demo/scenario
GET  /api/dashboard/summary
```

## Locked Implementation Decisions

- REST + JSON is the application API convention.
- Standard success/error envelopes are defined in `architecture.md`.
- Supabase Auth is the MVP authentication choice.
- Authorization is role + organization/group membership + meter ownership/assignment; a role alone does not grant unrestricted access.
- Risk components are normalized to 0–100 using the formulas defined in `architecture.md`.
- Alert transitions are explicitly constrained by the state machine in `architecture.md`.
- Insufficient history is a first-class analytical/data-quality state; the system must not fabricate a baseline or misleading risk.
- Frontend displays backend-authoritative analytics and does not calculate authoritative risk/severity itself.

## Safety Language

Prefer:

- “suspected anomaly”
- “possible leak”
- “estimated excess consumption”
- “physical verification required”

Do not claim:

- “leak confirmed” as an automated analytical result
- “100% leak detection”
- “guaranteed savings”
- physical leak localization unless independently verified outside the MVP
