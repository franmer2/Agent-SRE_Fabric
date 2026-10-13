from datetime import UTC, datetime, timedelta

import pytest

from fabric_sre.approvals import ActionPlan, require_valid_approval


def _plan(expires: datetime) -> ActionPlan:
    return ActionPlan(
        action="capacity.suspend",
        resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Fabric/capacities/cap",
        current_state={"state": "Active"},
        target_state={"state": "Paused"},
        impact="New workloads cannot run.",
        rollback="Resume the capacity.",
        expires_at_utc=expires,
    )


def test_matching_unexpired_approval_is_accepted() -> None:
    now = datetime.now(UTC)
    plan = _plan(now + timedelta(minutes=30))
    require_valid_approval(plan, plan.approval_id, now=now)


def test_mismatched_approval_is_rejected() -> None:
    now = datetime.now(UTC)
    with pytest.raises(PermissionError, match="does not match"):
        require_valid_approval(_plan(now + timedelta(minutes=30)), "wrong", now=now)


def test_expired_approval_is_rejected() -> None:
    now = datetime.now(UTC)
    plan = _plan(now - timedelta(seconds=1))
    with pytest.raises(PermissionError, match="expired"):
        require_valid_approval(plan, plan.approval_id, now=now)
