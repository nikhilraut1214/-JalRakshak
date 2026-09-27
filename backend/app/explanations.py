import json
import logging
import httpx
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.schemas import EvidenceDetail

logger = logging.getLogger("jalrakshak.explanations")

class StructuredGroqExplanation(BaseModel):
    summary: str = Field(..., description="Objective summary of what changed quoting exact evidence")
    potential_reasons: list[str] = Field(..., description="Possible interpretations (not physical facts)")
    recommended_checks: list[str] = Field(..., description="Actionable human verification steps")

def generate_deterministic_fallback(
    evidence: EvidenceDetail,
    language: str = "en-IN"
) -> str:
    """
    Produces deterministic natural language explanation in en-IN, mr-IN, or hi-IN.
    Ensures zero reliance on Groq when unavailable/unconfigured.
    Preserves exact numerical evidence.
    """
    curr = evidence.current_usage_liters
    base = evidence.baseline_liters
    dev = evidence.deviation_pct
    pers = evidence.persistence_intervals
    trend = evidence.trend
    risk = evidence.risk_score
    sev = evidence.severity
    excess = evidence.estimated_excess_liters

    if language == "mr-IN":
        text = (
            f"पाणी वापर विश्लेषण अहवाल (जोखीम: {risk}/100 - {sev}):\n"
            f"• सध्याचा वापर: {curr} लीटर (अपेक्षित आधारभूत वापर: {base} लीटर).\n"
            f"• विचलन (Deviation): {dev:+.1f}% वाढ, सलग {pers} कालावधीपासून टिकून आहे ({trend} कल).\n"
            f"• अंदाजे संभाव्य अतिरिक्त वापर: {excess} लीटर.\n"
            f"• संभाव्य कारणे: नळाची गळती, फ्लश टँक चालू राहणे, किंवा अनपेक्षित सततचा पाण्याचा प्रवाह.\n"
            f"• पुढील पडताळणी: मुख्य मीटर बंद असताना मीटर फिरत आहे का ते तपासा आणि घरातील/परिसरातील सर्व नळ व व्हॉल्व्ह तपासा."
        )
    elif language == "hi-IN":
        text = (
            f"जल खपत विश्लेषण रिपोर्ट (जोखिम: {risk}/100 - {sev}):\n"
            f"• वर्तमान खपत: {curr} लीटर (अपेक्षित बेसलाइन: {base} लीटर)।\n"
            f"• विचलन (Deviation): {dev:+.1f}% की वृद्धि, लगातार {pers} अंतरालों से जारी ({trend} प्रवृत्ति)।\n"
            f"• अनुमानित अतिरिक्त खपत: {excess} लीटर।\n"
            f"• संभावित कारण: नल में रिसाव, फ्लश टैंक का लगातार चलना, या अज्ञात निरंतर प्रवाह।\n"
            f"• भौतिक सत्यापन कदम: मुख्य वॉल्व बंद करके जांचें कि मीटर घूम रहा है या नहीं, और आंतरिक पाइपलाइन का भौतिक निरीक्षण करें।"
        )
    else:  # en-IN default
        text = (
            f"Water Consumption Evidence Report (Risk Score: {risk}/100 · {sev}):\n"
            f"• Current Reading: {curr:.1f} L (Baseline expected: {base:.1f} L).\n"
            f"• Deviation: {dev:+.1f}% above expected baseline, persisting for {pers} interval(s) with an {trend} trend.\n"
            f"• Estimated Excess Consumption: {excess:.1f} L.\n"
            f"• Possible Explanations: Potential concealed fixture leak, running toilet valve, irrigation overrun, or unusual continuous draw.\n"
            f"• Human Verification Checklist: Inspect fixtures, conduct a zero-consumption meter test (observe meter movement with all taps shut), and verify physical shutoff valves."
        )
    return text

def generate_explanation(
    evidence: EvidenceDetail,
    language: str = "en-IN"
) -> Tuple[str, str]:
    """
    Returns (explanation_text, source) where source is 'groq' or 'deterministic'.
    If GROQ_API_KEY is not configured or any error/timeout occurs, falls back to deterministic.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.strip() == "":
        return generate_deterministic_fallback(evidence, language), "deterministic"

    prompt = f"""
You are the AI explanation engine for JalRakshak AI.
IMPORTANT RULES:
1. You are an EXPLANATION layer only.
2. DO NOT recalculate or modify any numbers, risk scores, or severity.
3. DO NOT state that a leak is physically confirmed or localized.
4. QUOTE the provided evidence accurately:
   - Current: {evidence.current_usage_liters} L
   - Baseline: {evidence.baseline_liters} L
   - Deviation: {evidence.deviation_pct}%
   - Persistence: {evidence.persistence_intervals} intervals
   - Trend: {evidence.trend}
   - Estimated excess: {evidence.estimated_excess_liters} L
   - Risk score: {evidence.risk_score}/100 ({evidence.severity})
5. Language to respond in: {language} (en-IN: Indian English, mr-IN: Marathi, hi-IN: Hindi).
Respond in pure JSON matching this schema:
{{
  "summary": "Concise summary citing the numbers",
  "potential_reasons": ["interpretation 1", "interpretation 2"],
  "recommended_checks": ["verification action 1", "verification action 2"]
}}
"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are JalRakshak AI explanation system. Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        with httpx.Client(timeout=5.0) as client:
            resp = client.post(url, headers=headers, json=body)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                structured = StructuredGroqExplanation(**parsed)

                # Format formatted output
                explanation_str = (
                    f"{structured.summary}\n\n"
                    f"Possible Interpretations:\n" +
                    "\n".join([f"• {r}" for r in structured.potential_reasons]) +
                    f"\n\nRecommended Physical Checks:\n" +
                    "\n".join([f"• {c}" for c in structured.recommended_checks])
                )
                return explanation_str, "groq"
            else:
                logger.warning(f"Groq API returned status {resp.status_code}, falling back to deterministic.")
    except Exception as e:
        logger.warning(f"Groq explanation failed: {e}. Using deterministic fallback.")

    return generate_deterministic_fallback(evidence, language), "deterministic"
