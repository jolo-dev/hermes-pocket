from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path

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
from hermes_pocket.adapters.registry import (
    AdapterEvidence,
    AdapterRegistrationRejected,
    AdapterRegistry,
    release_registry,
)
from hermes_pocket.facade import FacadeState
from hermes_pocket.pairing import PairingService


class ConformantCandidate:
    name = "candidate"

    def __init__(self) -> None:
        self.active_sessions: set[str] = set()
        self.resolutions: dict[str, BackendApproval] = {}

    def require_session(self, session_id: str) -> None:
        if session_id not in self.active_sessions:
            raise BackendFailure("SESSION_INVALID", BackendErrorCategory.AUTHENTICATION)

    async def pair(self, request: PairingRequest) -> BackendSession:
        session_id = f"candidate-{request.device_id}"
        self.active_sessions.add(session_id)
        return BackendSession(session_id, "Conformance candidate")

    async def stream_message(
        self, session_id: str, message: AdapterMessage
    ) -> AsyncIterator[BackendEvent]:
        self.require_session(session_id)
        yield BackendEvent("candidate-1", 1, EventType.STARTED, message.correlation_id)
        yield BackendEvent("candidate-2", 2, EventType.COMPLETED, message.correlation_id)

    async def list_approvals(self, session_id: str) -> tuple[BackendApproval, ...]:
        self.require_session(session_id)
        return (BackendApproval("approval-1", "pending", "action-1"),)

    async def resolve_approval(
        self,
        session_id: str,
        approval_id: str,
        decision: str,
        action_key: str,
    ) -> BackendApproval:
        self.require_session(session_id)
        result = self.resolutions.get(action_key) or BackendApproval(
            approval_id, "denied" if decision == "deny" else "allowed", action_key
        )
        self.resolutions[action_key] = result
        return result

    async def list_tasks(self, session_id: str) -> tuple[BackendTask, ...]:
        self.require_session(session_id)
        return (BackendTask("task-1", "pending", "Review fictional notice"),)

    async def revoke_device(self, session_id: str) -> None:
        self.require_session(session_id)
        self.active_sessions.remove(session_id)


class FutureVerifiedAdapter(ConformantCandidate):
    name = "future-verified"


class DisabledOpenClawAdapter(ConformantCandidate):
    name = "openclaw"


def verified_evidence() -> AdapterEvidence:
    return AdapterEvidence(
        api_contract_reference="https://evidence.example.invalid/future/api",
        authentication_contract_reference="https://evidence.example.invalid/future/auth",
        api_contract_verified=True,
        authentication_contract_verified=True,
    )


def test_release_configuration_advertises_only_strands() -> None:
    configuration = json.loads(
        (Path(__file__).parents[2] / "config" / "release.json").read_text(encoding="utf-8")
    )

    assert configuration["enabled_adapters"] == ["strands"]
    assert configuration["advertised_compatibility"] == ["strands"]
    assert "hermes" not in json.dumps(configuration).lower()
    assert "openclaw" not in json.dumps(configuration).lower()


@pytest.mark.asyncio
async def test_release_registry_rejects_hermes_and_openclaw_selection() -> None:
    registry = release_registry()

    with pytest.raises(AdapterRegistrationRejected, match="ADAPTER_NOT_ENABLED"):
        await registry.register(DisabledOpenClawAdapter(), verified_evidence())
    with pytest.raises(AdapterRegistrationRejected, match="ADAPTER_UNAVAILABLE"):
        registry.select("openclaw")
    with pytest.raises(AdapterRegistrationRejected, match="ADAPTER_UNAVAILABLE"):
        registry.select("hermes")


@pytest.mark.asyncio
async def test_future_adapter_requires_evidence_and_live_conformance() -> None:
    registry = AdapterRegistry(frozenset({"future-verified"}))
    adapter = FutureVerifiedAdapter()
    unverified = AdapterEvidence(
        api_contract_reference="planned",
        authentication_contract_reference="planned",
        api_contract_verified=False,
        authentication_contract_verified=False,
    )

    with pytest.raises(AdapterRegistrationRejected, match="EVIDENCE_UNVERIFIED"):
        await registry.register(adapter, unverified)

    await registry.register(adapter, verified_evidence())

    assert registry.select("future-verified") is adapter
    assert registry.advertised_names == ("future-verified",)


def test_facade_fails_closed_for_non_release_adapter() -> None:
    adapter = DisabledOpenClawAdapter()

    with pytest.raises(ValueError, match="not enabled"):
        FacadeState(pairing=PairingService(adapter), adapter=adapter)
