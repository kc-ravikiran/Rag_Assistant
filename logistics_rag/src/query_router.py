"""
Query Router
Classifies incoming questions into logistics intent categories.
"""

import re
from typing import Literal

Intent = Literal["shipment_status", "sla_breach", "driver_performance", "route_info", "sop_policy", "general"]


class QueryRouter:
    """Lightweight rule-based intent classifier for logistics queries."""

    PATTERNS = {
        "shipment_status": [
            r"\b(shipment|order|package|parcel|delivery)\b.*\b(status|track|where|delayed|late|missing|lost)\b",
            r"\b(delayed|on.time|in.transit|out.for.delivery|delivered|undelivered)\b",
            r"\bshipment[_\s]?id\b",
        ],
        "sla_breach": [
            r"\bsla\b",
            r"\b(breach|breached|violation|miss|missed|at.risk)\b",
            r"\b(service.level|commitment|promised.time|deadline)\b",
            r"\b(overdue|past.due)\b",
        ],
        "driver_performance": [
            r"\bdriver\b",
            r"\b(performance|rating|score|efficiency|on.time.rate|delivery.rate)\b",
            r"\b(best|worst|top|bottom|slowest|fastest)\b.*\bdriver\b",
            r"\broute\b.*\b(performance|efficiency|time)\b",
        ],
        "route_info": [
            r"\broute\b",
            r"\bzone\b",
            r"\b(coverage|area|region|sector|hub|depot)\b",
            r"\b(distance|km|miles|eta|estimated.time)\b",
        ],
        "sop_policy": [
            r"\b(sop|policy|procedure|protocol|guideline|standard)\b",
            r"\b(exception|escalation|process|how.to|step)\b",
            r"\b(handle|manage|deal.with)\b.*\b(damage|return|refund|complaint)\b",
        ],
    }

    def classify(self, question: str) -> Intent:
        q = question.lower()
        scores: dict = {intent: 0 for intent in self.PATTERNS}

        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, q):
                    scores[intent] += 1

        best_intent = max(scores, key=scores.get)
        if scores[best_intent] == 0:
            return "general"
        return best_intent  # type: ignore

    def get_intent_label(self, intent: Intent) -> str:
        labels = {
            "shipment_status": "🚚 Shipment Status & Delays",
            "sla_breach": "⚠️  SLA Breach Analysis",
            "driver_performance": "👤 Driver/Route Performance",
            "route_info": "🗺️  Route & Zone Info",
            "sop_policy": "📋 SOP / Policy",
            "general": "💬 General Query",
        }
        return labels.get(intent, "💬 General Query")
