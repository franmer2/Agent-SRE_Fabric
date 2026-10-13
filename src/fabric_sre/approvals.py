from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class ActionPlan:
    action: str
    resource_id: str
    current_state: dict[str, Any]
    target_state: dict[str, Any]
    impact: str
    rollback: str
    expires_at_utc: datetime

    @property
    def approval_id(self) -> str:
        canonical = json.dumps(
            {
                "action": self.action,
                "resourceId": self.resource_id,
                "currentState": self.current_state,
                "targetState": self.target_state,
                "impact": self.impact,
                "rollback": self.rollback,
                "expiresAtUtc": self.expires_at_utc.astimezone(UTC).isoformat(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def require_valid_approval(
    plan: ActionPlan,
    approved_id: str,
    *,
    now: datetime | None = None,
) -> None:
    current_time = now or datetime.now(UTC)
    if current_time >= plan.expires_at_utc.astimezone(UTC):
        raise PermissionError("Approval has expired")
    if approved_id != plan.approval_id:
        raise PermissionError("Approval does not match the proposed action plan")

