from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from hermes_pocket.adapters.base import (
    AdapterMessage,
    BackendApproval,
    BackendErrorCategory,
    BackendEvent,
    BackendFailure,
    BackendSession,
    BackendTask,
    EventType,
    PairingRequest,
)
from hermes_pocket.adapters.conformance import assert_adapter_conformance


class FakeAdapter:
    name = "fake"

    def __init__(self) -> None:
        self.active_sessions: set[str] = set()
        self.resolutions: dict[str, BackendApproval] = {}

    def _require_session(self, session_id: str) -> None:
        if session_id not in self.active_sessions:
            raise BackendFailure("SESSION_REVOKED", BackendErrorCategory.AUTHENTICATION)

    async def pair(self, request: PairingRequest) -> BackendSession:
        session_id = f"fake-{request.device_id}"
        self.active_sessions.add(session_id)
        return BackendSession(session_id=session_id, backend_identity="Fake conformance backend")

    async def stream_message(
        self,
        session_id: str,
        message: AdapterMessage,
    ) -> AsyncIterator[BackendEvent]:
        self._require_session(session_id)
        yield BackendEvent("event-1", 1, EventType.STARTED, message.correlation_id)
        yield BackendEvent(
            "event-2",
            2,
            EventType.FRAGMENT,
            message.correlation_id,
            fragment="Safe fictional response.",
        )
        yield BackendEvent("event-3", 3, EventType.COMPLETED, message.correlation_id)

    async def list_approvals(self, session_id: str) -> tuple[BackendApproval, ...]:
        self._require_session(session_id)
        return (BackendApproval("approval-1", "pending", "action-1"),)

    async def resolve_approval(
        self,
        session_id: str,
        approval_id: str,
        decision: str,
        action_key: str,
    ) -> BackendApproval:
        self._require_session(session_id)
        existing = self.resolutions.get(action_key)
        if existing is not None:
            return existing
        resolved = BackendApproval(
            approval_id, "denied" if decision == "deny" else "allowed", action_key
        )
        self.resolutions[action_key] = resolved
        return resolved

    async def list_tasks(self, session_id: str) -> tuple[BackendTask, ...]:
        self._require_session(session_id)
        return (BackendTask("task-1", "pending", "Review fictional notice"),)

    async def revoke_device(self, session_id: str) -> None:
        self._require_session(session_id)
        self.active_sessions.remove(session_id)


@pytest.mark.asyncio
async def test_fake_adapter_passes_backend_neutral_conformance_suite() -> None:
    completed_cases = await assert_adapter_conformance(FakeAdapter())

    assert completed_cases == (
        "pairing",
        "ordered_streaming",
        "correlated_events",
        "approval_listing",
        "idempotent_resolution",
        "task_listing",
        "normalized_errors",
        "revocation",
    )
