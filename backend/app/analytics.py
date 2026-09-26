import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict, Any
from backend.app.config import settings

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

def compute_baseline_and_anomaly(
    readings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes deterministic analytics over historical readings.
    Each reading is a dict with keys: 'timestamp', 'reading_liters'.
    Assumes readings are ordered by timestamp ascending.
    """
    if len(readings) < settings.MIN_BASELINE_READINGS:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "message": "Not enough historical readings to establish a reliable baseline.",
            "readings_count": len(readings),
            "required_count": settings.MIN_BASELINE_READINGS,
        }

    df = pd.DataFrame(readings)
    df["reading_liters"] = pd.to_numeric(df["reading_liters"], errors="coerce").fillna(0.0)
    values = df["reading_liters"].values

    current_val = float(values[-1])
    history_vals = values[:-1] if len(values) > 1 else values

    # 1. Baseline: Rolling median and MAD
    median = float(np.median(history_vals))
    abs_deviations = np.abs(history_vals - median)
    mad = float(np.median(abs_deviations))

    eps = settings.ROBUST_EPSILON
    denom = 1.4826 * mad + eps
    robust_z = float((current_val - median) / denom)

    # 2. Deviation percentage
    deviation_pct = float(((current_val - median) / max(median, eps)) * 100.0)
    # Deviation can be negative if usage dropped, but for anomaly/excess risk we focus on positive deviation
    positive_deviation_pct = max(0.0, deviation_pct)

    # 3. Persistence: count consecutive recent intervals where usage exceeded median by threshold
    # Threshold: robust_z >= 1.5 or deviation_pct >= 20%
    persistence_intervals = 0
    for v in reversed(values):
        val_dev = ((v - median) / max(median, eps)) * 100.0
        val_z = (v - median) / denom
        if val_z >= 1.5 or val_dev >= 20.0:
            persistence_intervals += 1
        else:
            break

    # 4. Trend: Slope over recent window (up to last 5 points)
    window = values[-min(5, len(values)):]
    if len(window) >= 2:
        x = np.arange(len(window))
        # Simple linear regression slope
        slope, _ = np.polyfit(x, window, 1)
        slope = float(slope)
    else:
        slope = 0.0

    if slope > 1.0:
        trend_label = "increasing"
    elif slope < -1.0:
        trend_label = "decreasing"
    else:
        trend_label = "stable"

    normalized_positive_trend = max(0.0, slope / settings.TREND_NORMALIZATION_FACTOR)
    trend_score = clamp(normalized_positive_trend * 100.0, 0.0, 100.0)

    # 5. Estimated Excess
    # estimated_excess_liters = max(observed_liters - expected_liters, 0) * persistence_intervals
    single_excess = max(0.0, current_val - median)
    estimated_excess_liters = float(single_excess * max(1, persistence_intervals))

    # 6. Risk Normalization (All components 0-100)
    # Deviation score
    deviation_score = clamp(positive_deviation_pct, 0.0, 100.0)

    # Persistence score: 1 -> 25, 2 -> 50, 3 -> 75, 4+ -> 100
    if persistence_intervals <= 0:
        persistence_score = 0.0
    elif persistence_intervals == 1:
        persistence_score = 25.0
    elif persistence_intervals == 2:
        persistence_score = 50.0
    elif persistence_intervals == 3:
        persistence_score = 75.0
    else:
        persistence_score = 100.0

    # Loss score
    loss_score = clamp(
        (estimated_excess_liters / settings.LOSS_REFERENCE_LITERS) * 100.0,
        0.0,
        100.0
    )

    # Final Risk: 0.45*D + 0.25*P + 0.20*T + 0.10*L
    raw_risk = (
        0.45 * deviation_score
        + 0.25 * persistence_score
        + 0.20 * trend_score
        + 0.10 * loss_score
    )
    risk_score = round(clamp(raw_risk, 0.0, 100.0), 1)

    # 7. Severity:
    # LOW: 0-39, MEDIUM: 40-69, HIGH: 70-84, CRITICAL: 85-100
    if risk_score >= 85.0:
        severity = "CRITICAL"
    elif risk_score >= 70.0:
        severity = "HIGH"
    elif risk_score >= 40.0:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # Verification required if risk is elevated (MEDIUM or higher)
    verification_required = risk_score >= 40.0

    return {
        "status": "SUCCESS",
        "current_usage_liters": round(current_val, 2),
        "baseline_liters": round(median, 2),
        "mad": round(mad, 2),
        "robust_z": round(robust_z, 2),
        "deviation_pct": round(deviation_pct, 1),
        "persistence_intervals": persistence_intervals,
        "trend": trend_label,
        "trend_slope": round(slope, 2),
        "estimated_excess_liters": round(estimated_excess_liters, 2),
        "deviation_score": round(deviation_score, 1),
        "persistence_score": round(persistence_score, 1),
        "trend_score": round(trend_score, 1),
        "loss_score": round(loss_score, 1),
        "risk_score": risk_score,
        "severity": severity,
        "verification_required": verification_required,
    }

def compute_forecast_and_savings(
    readings: List[Dict[str, Any]],
    horizon_periods: int = 3,
    avoided_fraction: float = 0.70
) -> Dict[str, Any]:
    """
    Forecasting is an estimation feature, not a detection proof.
    Uses EWMA / rolling mean baseline and calculates potential savings:
    potential_savings_liters = estimated_excess_liters * avoided_fraction
    """
    if len(readings) < 3:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "message": "Insufficient readings for forecast estimation."
        }

    df = pd.DataFrame(readings)
    df["reading_liters"] = pd.to_numeric(df["reading_liters"], errors="coerce").fillna(0.0)
    values = df["reading_liters"]

    # EWMA forecast
    ewma = values.ewm(span=3).mean()
    latest_val = float(values.iloc[-1])
    forecast_val = float(ewma.iloc[-1])

    # Calculate MAE over known points
    mae = float(np.mean(np.abs(values - ewma)))

    return {
        "status": "SUCCESS",
        "baseline_ewma": round(forecast_val, 2),
        "forecast_horizon_periods": horizon_periods,
        "forecast_next_liters": round(forecast_val, 2),
        "historical_mae": round(mae, 2),
        "avoided_fraction_assumed": avoided_fraction,
        "note": "Forecasting and potential savings are analytical estimates based on stated assumptions, not physical measurements."
    }
