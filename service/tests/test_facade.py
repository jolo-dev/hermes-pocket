from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi.testclient import TestClient

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
from hermes_pocket.app import create_app
from hermes_pocket.facade import FacadeState
from hermes_pocket.pairing import BackendIdentity, PairingService


class FacadeAdapter:
    name = "strands"

    def __init__(self) -> None:
        self.active_sessions: set[str] = set()
        self.pair_calls = 0
        self.resolved: dict[str, BackendApproval] = {}

    def require_session(self, session_id: str) -> None:
        if session_id not in self.active_sessions:
            raise BackendFailure("SESSION_INVALID", BackendErrorCategory.AUTHENTICATION)

    async def pair(self, request: PairingRequest) -> BackendSession:
        self.pair_calls += 1
        session_id = f"facade-{request.device_id}"
        self.active_sessions.add(session_id)
        return BackendSession(session_id, "Strands facade test")

    async def stream_message(
        self, session_id: str, message: AdapterMessage
    ) -> AsyncIterator[BackendEvent]:
        self.require_session(session_id)
        yield BackendEvent("event-1", 1, EventType.STARTED, message.correlation_id)
        yield BackendEvent(
            "event-2",
            2,
            EventType.COMPLETED,
            message.correlation_id,
        )

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
        result = self.resolved.get(action_key) or BackendApproval(
            approval_id, "denied" if decision == "deny" else "allowed", action_key
        )
        self.resolved[action_key] = result
        return result

    async def list_tasks(self, session_id: str) -> tuple[BackendTask, ...]:
        self.require_session(session_id)
        return (BackendTask("task-1", "pending", "Review fictional notice"),)

    async def revoke_device(self, session_id: str) -> None:
        self.require_session(session_id)
        self.active_sessions.remove(session_id)


def setup_facade() -> tuple[TestClient, FacadeState, FacadeAdapter, dict[str, object]]:
    adapter = FacadeAdapter()
    pairing = PairingService(adapter)
    state = FacadeState(pairing=pairing, adapter=adapter)
    client = TestClient(create_app(configure_service_logging=False, facade=state))
    identity = BackendIdentity(
        name="Strands facade test",
        fingerprint="sha256:" + "b" * 64,
        facade_origin="https://facade.example.invalid",
        requested_capabilities=("conversation", "explicit_share", "approvals", "tasks"),
    )
    claim = pairing.create_claim("owner-1", identity)
    claim_response = client.post(
        "/v1/pairing/claim",
        json={
            "claim_id": claim.claim_id,
            "pairing_code": claim.code,
            "device_name": "Fictional phone",
            "confirmed_backend_fingerprint": identity.fingerprint,
            "accepted_capabilities": ["conversation", "explicit_share", "approvals", "tasks"],
        },
    )
    assert claim_response.status_code == 201
    return client, state, adapter, claim_response.json()


def metadata(session_id: object, request_id: str) -> dict[str, object]:
    return {
        "request_id": request_id,
        "device_session_id": session_id,
        "policy_version": "v1",
        "interface_locale": "en",
        "reply_locale": "de",
    }


def test_authorization_and_version_failure_are_structured() -> None:
    adapter = FacadeAdapter()
    state = FacadeState(pairing=PairingService(adapter), adapter=adapter)
    client = TestClient(create_app(configure_service_logging=False, facade=state))

    unsupported = client.get("/v1/version", headers={"x-api-version": "v99"})
    unauthorized = client.get("/v1/tasks")

    assert unsupported.status_code == 406
    assert unsupported.json()["error"]["category"] == "compatibility"
    assert unauthorized.status_code == 401
    assert unauthorized.json()["error"]["category"] == "authentication"
    assert adapter.pair_calls == 0


def test_facade_resources_and_revocation_end_to_end() -> None:
    client, state, adapter, credentials = setup_facade()
    access_token = str(credentials["access_token"])
    renewal_token = str(credentials["renewal_token"])
    session_id = credentials["device_session_id"]
    headers = {"authorization": f"Bearer {access_token}"}

    message_response = client.post(
        "/v1/conversations/conversation-1/messages",
        headers=headers,
        json={
            "metadata": metadata(session_id, "request-message-1"),
            "conversation_id": "conversation-1",
            "client_message_id": "client-message-1",
            "source": "user_text",
            "text": "Explain the fictional notice.",
            "approved_capabilities": ["explain"],
        },
    )
    assert message_response.status_code == 202
    assert [event["event_type"] for event in message_response.json()] == [
        "response_started",
        "response_completed",
    ]
    assert client.get("/v1/conversations", headers=headers).json() == ["conversation-1"]
    assert len(client.get("/v1/events/sync?after_sequence=0", headers=headers).json()) == 2

    context_response = client.post(
        "/v1/conversations/conversation-1/context-shares",
        headers=headers,
        json={
            "metadata": metadata(session_id, "request-share-1"),
            "conversation_id": "conversation-1",
            "source": "explicit_share",
            "purpose": "explain",
            "parts": [{"part_id": "part-1", "kind": "text", "text": "Safe text"}],
            "consent": {
                "receipt_id": "receipt-1",
                "content_digest": "sha256:" + "c" * 64,
                "purpose": "explain",
                "destination_session_id": session_id,
                "approved_part_ids": ["part-1"],
                "issued_at": "2099-01-01T00:00:00Z",
                "expires_at": "2099-01-01T00:05:00Z",
            },
        },
    )
    assert context_response.status_code == 202
    assert client.get("/v1/privacy/records", headers=headers).json() == [
        {"record_id": "receipt-1", "category": "share", "location": "facade"}
    ]

    assert client.get("/v1/approvals", headers=headers).status_code == 200
    approval_response = client.post(
        "/v1/approvals/approval-1/decision",
        headers=headers,
        json={
            "metadata": metadata(session_id, "request-approval-1"),
            "decision": "deny",
            "scope": "one_time",
            "action_key": "action-1",
        },
    )
    assert approval_response.json()["status"] == "denied"
    assert client.get("/v1/tasks", headers=headers).json()[0]["task_id"] == "task-1"

    memory_response = client.put(
        "/v1/privacy/memory-consent",
        headers=headers,
        json={
            "metadata": metadata(session_id, "request-memory-1"),
            "category": "reminder_summary",
            "enabled": True,
            "retention_days": 30,
        },
    )
    assert memory_response.status_code == 204
    assert state.memory_consents[str(session_id)]["reminder_summary"]["retention_days"] == 30

    delete_response = client.request(
        "DELETE",
        "/v1/privacy/records",
        headers=headers,
        json={
            "metadata": metadata(session_id, "request-delete-1"),
            "category": "share",
            "record_ids": ["receipt-1"],
            "delete_remote": True,
        },
    )
    assert delete_response.status_code == 204
    assert client.get("/v1/privacy/records", headers=headers).json() == []

    revoke_response = client.delete("/v1/devices/me", headers=headers)
    assert revoke_response.status_code == 204
    assert client.get("/v1/tasks", headers=headers).status_code == 401
    assert client.get("/v1/events/sync?after_sequence=0", headers=headers).status_code == 401
    assert client.post(
        "/v1/sessions/renew", json={"renewal_token": renewal_token}
    ).status_code == 401
    assert adapter.active_sessions == set()
