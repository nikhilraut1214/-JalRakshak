from typing import Dict, Any
from backend.app.schemas import EvidenceDetail

def build_evidence_packet(
    analytics_dict: Dict[str, Any]
) -> EvidenceDetail:
    """
    Constructs the canonical evidence model from analytics output.
    """
    return EvidenceDetail(
        current_usage_liters=analytics_dict["current_usage_liters"],
        baseline_liters=analytics_dict["baseline_liters"],
        deviation_pct=analytics_dict["deviation_pct"],
        persistence_intervals=analytics_dict["persistence_intervals"],
        trend=analytics_dict["trend"],
        estimated_excess_liters=analytics_dict["estimated_excess_liters"],
        risk_score=analytics_dict["risk_score"],
        severity=analytics_dict["severity"],
        verification_required=analytics_dict["verification_required"],
        robust_z=analytics_dict.get("robust_z"),
        mad=analytics_dict.get("mad"),
        deviation_score=analytics_dict.get("deviation_score"),
        persistence_score=analytics_dict.get("persistence_score"),
        trend_score=analytics_dict.get("trend_score"),
        loss_score=analytics_dict.get("loss_score"),
    )
