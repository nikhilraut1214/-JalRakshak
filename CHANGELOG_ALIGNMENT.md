# Context Reconciliation Changelog

This package is a rewritten version of the existing JalRakshak AI context ZIP, incorporating the implementation decisions locked after the technical-context audit.

## Reconciled Items

### 1. API Contracts
Added:
- REST + JSON convention;
- standard success envelope;
- standard error envelope;
- request schemas for meter, reading, resolve, explain and demo scenario;
- alert filters;
- backend-owned analysis flow;
- explicit frontend authority rule.

### 2. Risk Normalization
Added deterministic 0–100 normalization for:
- deviation;
- persistence;
- trend;
- estimated loss.

Preserved authoritative weights:

```text
45% deviation
25% persistence
20% trend
10% estimated loss
```

### 3. Authorization
Added explicit role/resource authorization model:
- RESIDENT;
- SOCIETY_MANAGER;
- FARM_OPERATOR;
- INSTITUTION_ADMIN;
- ADMINISTRATOR.

Clarified that role alone is not sufficient; ownership/group assignment must also be checked.

### 4. Alert Lifecycle
Added an explicit transition matrix and backend rejection rule for invalid transitions.

### 5. Authentication
Locked **Supabase Auth** as the MVP authentication implementation choice and documented the JWT/server-side authorization boundary.

### 6. Insufficient History
Made insufficient history a first-class analytical state without inventing a universal minimum observation count.

### 7. AI Boundary
Clarified that Groq is an explanation layer and deterministic fallback must preserve functionality when AI is unavailable.

### 8. Memory State
Changed memory guidance so it records actual repository state and does not claim implementation/test/deployment completion from planning documents alone.

### 9. Scope
Preserved the exclusion of a Reports subsystem and other explicitly out-of-scope MVP capabilities.

## Important Interpretation

These reconciliation decisions make the context package implementation-complete enough for an AI coding agent to proceed consistently. They do not mean the software itself has been implemented or tested.
