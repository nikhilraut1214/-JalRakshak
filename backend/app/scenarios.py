import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple, Optional

# Canonical scenario specification contract for JalRakshak AI
CANONICAL_SCENARIO_SPECS: Dict[str, Dict[str, Any]] = {
    "NORMAL_HOME": {
        "scenario_name": "NORMAL_HOME",
        "semantic_category": "BINARY_CLASSIFICATION",
        "purpose": "Verify non-anomalous domestic diurnal baseline consumption without triggering spurious false alerts.",
        "expected_behavior": "Diurnal domestic usage with typical morning (06:00-09:00) and evening (18:00-21:00) peaks and lower night usage.",
        "generated_profile": "24 hourly readings: day peaks (180-240 L/hr), base daytime (60-110 L/hr), night (5-25 L/hr).",
        "expected_persistence": 0,
        "expected_alert": False,
        "expected_severity": "LOW",
        "contextual_requirements": None,
        "participates_in_binary_evaluation": True,
        "ground_truth": "NORMAL",
        "description": "Normal household diurnal water usage with typical morning and evening domestic peaks.",
    },
    "SINGLE_SPIKE": {
        "scenario_name": "SINGLE_SPIKE",
        "semantic_category": "BINARY_CLASSIFICATION",
        "purpose": "Verify detection of an isolated transient domestic usage surge requiring verification without resembling a persistent leak.",
        "expected_behavior": "Stable domestic baseline followed by a single transient spike in the final interval; persistence approximately 1; warning/MEDIUM severity.",
        "generated_profile": "24 hourly readings: 23 baseline intervals (70-130 L/hr) followed by a 210.0 L single spike (~2.2x baseline).",
        "expected_persistence": 1,
        "expected_alert": True,
        "expected_severity": "MEDIUM",
        "contextual_requirements": None,
        "participates_in_binary_evaluation": True,
        "ground_truth": "ISOLATED_EVENT",
        "description": "Normal household consumption followed by a single transient high-volume usage spike.",
    },
    "PERSISTENT_LEAK": {
        "scenario_name": "PERSISTENT_LEAK",
        "semantic_category": "BINARY_CLASSIFICATION",
        "purpose": "Verify detection of continuous sustained low-demand elevation indicative of physical pipe defect or leak.",
        "expected_behavior": "Normal historical baseline followed by continuous sustained elevation across multiple intervals through low-demand periods.",
        "generated_profile": "24 hourly readings: first 12 intervals normal (70-100 L/hr), last 12 intervals elevated with continuous +180 L/hr leak.",
        "expected_persistence": 12,
        "expected_alert": True,
        "expected_severity": "HIGH",
        "contextual_requirements": None,
        "participates_in_binary_evaluation": True,
        "ground_truth": "SUSPECTED_PERSISTENT_LEAK",
        "description": "Normal historical baseline followed by continuous elevated consumption persisting through low-demand intervals.",
    },
    "BURST_USE": {
        "scenario_name": "BURST_USE",
        "semantic_category": "BINARY_CLASSIFICATION",
        "purpose": "Verify acute severe consumption surge lasting 2-3 intervals with demonstrable return to baseline (recovery).",
        "expected_behavior": "Baseline usage -> sudden acute surge lasting 2-3 intervals -> explicit recovery returning toward baseline.",
        "generated_profile": "24 hourly readings: intervals 0-17 baseline (80-120 L/hr), intervals 18-20 burst (850-950 L/hr), intervals 21-23 recovery (80-120 L/hr).",
        "expected_persistence": 3,
        "expected_alert": True,
        "expected_severity": "CRITICAL",
        "contextual_requirements": None,
        "participates_in_binary_evaluation": True,
        "ground_truth": "HIGH_VOLUME_BURST",
        "description": "Sudden extreme consumption surge spanning 2-3 consecutive intervals followed by return to baseline.",
    },
    "FARM_IRRIGATION": {
        "scenario_name": "FARM_IRRIGATION",
        "semantic_category": "CONTEXTUAL_DOMAIN",
        "purpose": "Verify contextual recognition of scheduled cyclical agricultural pump operations distinct from domestic leaks.",
        "expected_behavior": "High-volume pumping run during scheduled morning window (04:00-08:00) with low standby draw outside pumping hours.",
        "generated_profile": "24 hourly readings: morning pumping run 1500-1800 L/hr (04:00-08:00), off-pump standby 10-40 L/hr (other hours).",
        "expected_persistence": 5,
        "expected_alert": None,
        "expected_severity": "CONTEXTUAL",
        "contextual_requirements": {
            "meter_type": "agricultural",
            "operational_schedule": "04:00-08:00",
            "domain_context": "Scheduled agricultural pump draw; requires operational schedule awareness rather than domestic leak classification."
        },
        "participates_in_binary_evaluation": False,
        "ground_truth": "SCHEDULED_IRRIGATION",
        "description": "Large scheduled cyclical irrigation volumes typical of agricultural farm pumps requiring contextual verification.",
    },
    "DATA_QUALITY": {
        "scenario_name": "DATA_QUALITY",
        "semantic_category": "DATA_QUALITY_GUARD",
        "purpose": "Verify safe-failure guardrails on sparse or invalid data with fewer than required minimum readings.",
        "expected_behavior": "Halt analysis gracefully with INSUFFICIENT_HISTORY; do not compute spurious baseline or raise ungrounded alert.",
        "generated_profile": "3 hourly readings (50-100 L/hr), below minimum baseline threshold of 5 readings.",
        "expected_persistence": 0,
        "expected_alert": None,
        "expected_severity": "NONE",
        "contextual_requirements": None,
        "participates_in_binary_evaluation": False,
        "ground_truth": "INSUFFICIENT_HISTORY",
        "description": "Sparse dataset with fewer than required minimum readings to test data-quality safeguards.",
    },
}


def generate_scenario_readings(
    scenario: str,
    seed: int = 42,
    base_time: Optional[datetime] = None
) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Generates synthetic water consumption readings for a given scenario.
    Returns: (readings_list, ground_truth, description)
    Each reading has: 'timestamp', 'reading_liters'.
    """
    if scenario not in CANONICAL_SCENARIO_SPECS:
        raise ValueError(
            f"Unknown scenario '{scenario}'. Allowed: {', '.join(CANONICAL_SCENARIO_SPECS.keys())}"
        )

    spec = CANONICAL_SCENARIO_SPECS[scenario]
    ground_truth = spec["ground_truth"]
    desc = spec["description"]

    random.seed(seed)
    if not base_time:
        # Anchor to midnight to ensure consistent diurnal cycles (0h to 23h) regardless of execution hour
        base_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

    readings = []

    if scenario == "NORMAL_HOME":
        # Regular household diurnal cycle, baseline ~ 150-250 L/hr during day, 10-30 L/hr night
        for i in range(24):
            t = base_time + timedelta(hours=i)
            hour = t.hour
            if 6 <= hour <= 9 or 18 <= hour <= 21:
                liters = random.uniform(180, 240)
            elif 23 <= hour or hour <= 5:
                liters = random.uniform(5, 25)
            else:
                liters = random.uniform(60, 110)
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "SINGLE_SPIKE":
        # Calibrated isolated domestic spike (~2.2x baseline median)
        # Yields persistence = 1, estimated excess > 0, and risk in MEDIUM band (40-69)
        for i in range(24):
            t = base_time + timedelta(hours=i)
            if i == 23:
                liters = 210.0  # Calibrated isolated transient spike
            else:
                liters = random.uniform(70, 130)
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "PERSISTENT_LEAK":
        # Normal baseline ~85L followed by continuous elevated leak (+180L) persisting through low-demand intervals
        for i in range(24):
            t = base_time + timedelta(hours=i)
            normal = random.uniform(70, 100)
            leak = 180.0 if i >= 12 else 0.0
            readings.append({"timestamp": t, "reading_liters": round(normal + leak, 1)})

    elif scenario == "BURST_USE":
        # Demonstrates baseline -> acute 3-interval burst (850-950 L/hr) -> explicit recovery returning to baseline
        for i in range(24):
            t = base_time + timedelta(hours=i)
            if 18 <= i <= 20:
                liters = random.uniform(850, 950)  # Acute 3-interval burst
            else:
                liters = random.uniform(80, 120)   # Baseline (0..17) and recovery (21..23)
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "FARM_IRRIGATION":
        # Cyclical agricultural irrigation with high morning pump draw (04:00-08:00) and low standby
        for i in range(24):
            t = base_time + timedelta(hours=i)
            if 4 <= t.hour <= 8:
                liters = random.uniform(1500, 1800)  # Morning irrigation run
            else:
                liters = random.uniform(10, 40)      # Off-pump standby
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "DATA_QUALITY":
        # Insufficient readings (3 readings < 5 required minimum) to test data-quality safeguards
        for i in range(3):
            t = base_time + timedelta(hours=i)
            readings.append({"timestamp": t, "reading_liters": round(random.uniform(50, 100), 1)})

    return readings, ground_truth, desc
