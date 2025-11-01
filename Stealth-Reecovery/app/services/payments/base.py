from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PaymentIntent:
    id: str
    client_secret: str
    amount: int
    currency: str
    status: str


class PSPAdapter:
    def create_intent(self, *, amount: int, currency: str, description: Optional[str] = None) -> PaymentIntent:
        raise NotImplementedError
