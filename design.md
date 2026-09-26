# JalRakshak AI — Design System

**Purpose:** visual implementation guidance.  
**Principle:** the interface must make evidence understandable without overstating capability.

## 1. Design Objective

The product should feel calm, trustworthy and evidence-first.

Every major screen should answer:

1. What is happening?
2. What is expected?
3. Why is this considered unusual?
4. What should be verified?

## 2. Information Hierarchy

```text
MEASURED DATA
    ↓
DETERMINISTIC EVIDENCE
    ↓
RISK / SEVERITY
    ↓
AI EXPLANATION
    ↓
HUMAN VERIFICATION
```

AI must never look like the source of measured values.

## 3. Visual Language

Use:
- clean layouts;
- readable typography;
- restrained surfaces;
- subtle water-inspired accents;
- strong information hierarchy;
- clear status labels;
- charts with units and meaningful axes.

Avoid:
- cyberpunk/neon aesthetics;
- fake AI glow;
- decorative dashboards;
- unsupported hardware imagery;
- fake probability meters.

## 4. Severity

Use semantic visual styling for:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Always display the text label and never rely on color alone.

Risk must be displayed as an analytical score, not a leak probability.

Recommended:

```text
91 / 100 · CRITICAL
```

## 5. Layout

Desktop:

```text
┌──────────────┬────────────────────────────────────┐
│ Sidebar      │ Main analytical content            │
│              │                                    │
└──────────────┴────────────────────────────────────┘
```

Mobile uses a single-column flow.

## 6. Navigation

Use only implemented product modules:

1. Dashboard
2. Meters
3. Readings / Import
4. Alerts
5. Incident / Evidence
6. Verification
7. Scenario Lab
8. Evaluation
9. Water Impact
10. Settings

Do not add Reports.

## 7. Dashboard

Recommended sections:
- current consumption;
- expected/baseline;
- recent trend;
- alert summary;
- risk/severity;
- evidence highlights;
- next verification action.

The values come from backend APIs.

## 8. Insufficient History UI

When baseline history is inadequate, do not show a fabricated chart/baseline.

Use a clear state such as:

```text
Insufficient history

Not enough historical readings to establish a reliable baseline.
Add more readings to enable baseline-based anomaly analysis.
```

Do not show a guessed risk score as though it were authoritative.

## 9. Evidence Panel

Show evidence in this order:

```text
Current reading
Expected/baseline
Deviation
Persistence
Trend
Estimated excess
Risk score + severity
Verification required
```

Where applicable, include timestamps and source information.

## 10. Alert Detail

Recommended structure:

```text
┌──────────────────────────────────────────────┐
│ Severity + Risk                              │
├──────────────────────────────────────────────┤
│ What changed                                 │
│ Current vs baseline                          │
├──────────────────────────────────────────────┤
│ Evidence timeline                             │
│ Reading → deviation → persistence → trend    │
├──────────────────────────────────────────────┤
│ AI explanation / deterministic fallback      │
├──────────────────────────────────────────────┤
│ Verification checklist                       │
├──────────────────────────────────────────────┤
│ Lifecycle actions                             │
└──────────────────────────────────────────────┘
```

## 11. Alert Lifecycle UI

Only show actions valid for the current state.

```text
DETECTED
   ↓ acknowledge
ACKNOWLEDGED
   ↓ begin verification
VERIFYING
   ├→ confirm
   ├→ false alarm
   └→ investigate
         ↓
     RESOLVED
```

Do not expose impossible transitions.

## 12. Risk Display

Show:

```text
Risk score: 91 / 100
Severity: CRITICAL
```

Optionally show a component breakdown:

```text
Deviation      78
Persistence   100
Trend          70
Loss           65
```

Do not label any of these as probabilities.

## 13. AI Explanation Card

Clearly label:

```text
AI explanation
Source: Groq
```

or:

```text
Explanation
Source: Deterministic fallback
```

The card should quote/describe backend evidence rather than introduce new measurements.

## 14. Multilingual UI

Supported:

```text
English (en-IN)
मराठी (mr-IN)
हिन्दी (hi-IN)
```

Changing language must not change numerical values.

## 15. Forms and Validation

Show:
- field labels;
- units;
- timestamp format;
- validation errors;
- upload schema requirements.

Client validation is for usability. Backend validation remains authoritative.

## 16. Accessibility

- readable contrast;
- keyboard-accessible controls;
- labels for inputs;
- text equivalents for status;
- charts with supporting textual values;
- no severity conveyed by color alone.

## 17. Trust Rules

Never visually imply:
- physical inspection happened;
- leak location is known;
- savings are guaranteed;
- AI detected the leak;
- risk score is leak probability;
- estimated excess is measured physical loss.

The product should look precise about what it knows and explicit about what requires human verification.
