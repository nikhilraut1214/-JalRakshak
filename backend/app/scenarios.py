import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple

def generate_scenario_readings(
    scenario: str,
    seed: int = 42,
    base_time: datetime = None
) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Generates synthetic water consumption readings for a given scenario.
    Returns: (readings_list, ground_truth, description)
    Each reading has: 'timestamp', 'reading_liters'.
    """
    random.seed(seed)
    if not base_time:
        base_time = datetime.now(timezone.utc) - timedelta(hours=24)

    readings = []
    
    if scenario == "NORMAL_HOME":
        # Regular household diurnal cycle, baseline ~ 150-250 L/hr during day, 10-30 L/hr night
        ground_truth = "NORMAL"
        desc = "Normal household diurnal water usage with typical morning and evening peaks."
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
        # Normal baseline with a single one-off spike (e.g., car wash / filling a tank)
        ground_truth = "ISOLATED_EVENT"
        desc = "Normal household consumption followed by a single transient high-volume usage spike."
        for i in range(24):
            t = base_time + timedelta(hours=i)
            if i == 23:
                liters = 680.0  # Big spike on latest reading
            else:
                liters = random.uniform(70, 130)
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "PERSISTENT_LEAK":
        # First half has normal baseline ~90L, second half has persistent leak (+180L) persisting through night
        ground_truth = "SUSPECTED_PERSISTENT_LEAK"
        desc = "Normal historical baseline followed by continuous elevated consumption persisting through low-demand intervals."
        for i in range(24):
            t = base_time + timedelta(hours=i)
            normal = random.uniform(70, 100)
            leak = 180.0 if i >= 12 else 0.0
            readings.append({"timestamp": t, "reading_liters": round(normal + leak, 1)})

    elif scenario == "BURST_USE":
        # Sudden huge jump lasting 2-3 intervals
        ground_truth = "HIGH_VOLUME_BURST"
        desc = "Sudden extreme consumption surge spanning 2-3 consecutive intervals."
        for i in range(24):
            t = base_time + timedelta(hours=i)
            if i >= 21:
                liters = random.uniform(850, 950)
            else:
                liters = random.uniform(80, 120)
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "FARM_IRRIGATION":
        # Cyclic agricultural irrigation with high seasonal/scheduled pump draw
        ground_truth = "SCHEDULED_IRRIGATION"
        desc = "Large scheduled cyclical irrigation volumes typical of agricultural farm pumps."
        for i in range(24):
            t = base_time + timedelta(hours=i)
            if 4 <= t.hour <= 8:
                liters = random.uniform(1500, 1800)  # Morning irrigation run
            else:
                liters = random.uniform(10, 40)
            readings.append({"timestamp": t, "reading_liters": round(liters, 1)})

    elif scenario == "DATA_QUALITY":
        # Insufficient readings or missing timestamps
        ground_truth = "INSUFFICIENT_HISTORY"
        desc = "Sparse dataset with fewer than required minimum readings to test data-quality safeguards."
        for i in range(3):  # Only 3 readings, below baseline threshold of 5
            t = base_time + timedelta(hours=i)
            readings.append({"timestamp": t, "reading_liters": round(random.uniform(50, 100), 1)})

    else:
        raise ValueError(f"Unknown scenario '{scenario}'. Allowed: NORMAL_HOME, SINGLE_SPIKE, PERSISTENT_LEAK, BURST_USE, FARM_IRRIGATION, DATA_QUALITY")

    return readings, ground_truth, desc
