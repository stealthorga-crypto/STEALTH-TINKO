from __future__ import annotations

from typing import Any, Dict, Optional

from .. import rules


def classify_event(code: Optional[str], message: Optional[str]) -> Dict[str, Any]:
    """
    Contract:
    - Inputs: gateway failure code (string|None), message (string|None)
    - Output: { category: str, recommendation: str, alt: list[str], cooldown_seconds?: int }
    - Errors: never raises; unknown maps to sensible defaults
    """
    category = rules.classify_failure(code, message)
    options = rules.next_retry_options(category)
    payload: Dict[str, Any] = {
        "category": category,
        **options,
    }
    return payload
