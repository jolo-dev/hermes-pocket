from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest

from hermes_pocket.adapters.base import (
    AdapterMessage,
    BackendApproval,
    BackendEvent,
    BackendSession,
    BackendTask,
    PairingRequest,
)
from hermes_pocket.pairing import BackendIdentity, PairingRejected, PairingService


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2031, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, duration: timedelta) -> None:
        self.value += duration


class PairingAdapter:
    name = "strands"

    def __init__(self) -> None:
        self.revoked_sessions: list[str] = []

    async def pair(self, request: PairingRequest) -> BackendSession:
        return BackendSession(f"adapter-{request.device_id}", "Strands test backend")

    async def stream_message(
        self, session_id: str, message: AdapterMessage
    ) -> AsyncIterator[BackendEvent]:
        if False:
            yield

    async def list_approvals(self, session_id: str) -> tuple[BackendApproval, ...]:
        return ()

    async def resolve_approval(
        self,
        session_id: str,
        approval_id: str,
        decision: str,
        action_key: str,
    ) -> BackendApproval:
        return BackendApproval(approval_id, decision, action_key)

    async def list_tasks(self, session_id: str) -> tuple[BackendTask, ...]:
        return ()

    async def revoke_device(self, session_id: str) -> None:
        self.revoked_sessions.append(session_id)


def identity() -> BackendIdentity:
    return BackendIdentity(
        name="Strands test backend",
        fingerprint="sha256:" + "a" * 64,
        facade_origin="https://facade.example.invalid",
        requested_capabilities=("conversation", "approvals"),
    )


@pytest.mark.asyncio
async def test_claim_is_single_use_and_displays_backend_identity() -> None:
    clock = Clock()
    service = PairingService(PairingAdapter(), now=clock)
    claim = service.create_claim("owner-1", identity())

    inspected = service.inspect_claim(claim.claim_id, claim.code)
    credentials = await service.claim(
        claim_id=claim.claim_id,
        code=claim.code,
        device_name="Fictional phone",
        confirmed_backend_fingerprint=claim.backend.fingerprint,
        accepted_capabilities=("conversation",),
    )

    assert inspected.code == ""
    assert inspected.backend == identity()
    assert credentials.backend == identity()
    assert service.authenticate_access(credentials.access_token).device_name == "Fictional phone"
    with pytest.raises(PairingRejected, match="CLAIM_USED"):
        await service.claim(
            claim_id=claim.claim_id,
            code=claim.code,
            device_name="Replay phone",
            confirmed_backend_fingerprint=claim.backend.fingerprint,
            accepted_capabilities=("conversation",),
        )


@pytest.mark.asyncio
async def test_expired_claim_fails_closed() -> None:
    clock = Clock()
    service = PairingService(PairingAdapter(), now=clock)
    claim = service.create_claim("owner-1", identity())
    clock.advance(timedelta(minutes=6))

    with pytest.raises(PairingRejected, match="CLAIM_EXPIRED"):
        await service.claim(
            claim_id=claim.claim_id,
            code=claim.code,
            device_name="Late phone",
            confirmed_backend_fingerprint=claim.backend.fingerprint,
            accepted_capabilities=("conversation",),
        )


@pytest.mark.asyncio
async def test_renewal_rotates_and_old_token_cannot_replay() -> None:
    service = PairingService(PairingAdapter(), now=Clock())
    claim = service.create_claim("owner-1", identity())
    first = await service.claim(
        claim_id=claim.claim_id,
        code=claim.code,
        device_name="Fictional phone",
        confirmed_backend_fingerprint=claim.backend.fingerprint,
        accepted_capabilities=("conversation",),
    )

    rotated = await service.refresh(first.renewal_token)

    assert rotated.renewal_token != first.renewal_token
    assert rotated.access_token != first.access_token
    with pytest.raises(PairingRejected, match="RENEWAL_INVALID"):
        await service.refresh(first.renewal_token)


@pytest.mark.asyncio
async def test_expired_access_and_duplicate_request_ids_fail_closed() -> None:
    clock = Clock()
    service = PairingService(PairingAdapter(), now=clock)
    claim = service.create_claim("owner-1", identity())
    credentials = await service.claim(
        claim_id=claim.claim_id,
        code=claim.code,
        device_name="Fictional phone",
        confirmed_backend_fingerprint=claim.backend.fingerprint,
        accepted_capabilities=("conversation",),
    )
    service.consume_request_id(credentials.device_session_id, "request-1")

    with pytest.raises(PairingRejected, match="REQUEST_REPLAYED"):
        service.consume_request_id(credentials.device_session_id, "request-1")
    clock.advance(timedelta(minutes=6))
    with pytest.raises(PairingRejected, match="ACCESS_INVALID"):
        service.authenticate_access(credentials.access_token)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["send_message", "fetch_events", "resolve_approval"])
async def test_owner_revocation_blocks_all_authenticated_operations(operation: str) -> None:
    adapter = PairingAdapter()
    service = PairingService(adapter, now=Clock())
    claim = service.create_claim("owner-1", identity())
    credentials = await service.claim(
        claim_id=claim.claim_id,
        code=claim.code,
        device_name="Fictional phone",
        confirmed_backend_fingerprint=claim.backend.fingerprint,
        accepted_capabilities=("conversation", "approvals"),
    )
    service.set_push_association(credentials.device_session_id, "opaque-push-association")

    await service.revoke_by_owner("owner-1", credentials.device_session_id)

    with pytest.raises(PairingRejected, match="ACCESS_INVALID"):
        service.authenticate_access(credentials.access_token)
    with pytest.raises(PairingRejected, match="RENEWAL_INVALID"):
        await service.refresh(credentials.renewal_token)
    assert service.devices[credentials.device_session_id].push_association is None
    assert adapter.revoked_sessions == [f"adapter-{claim.claim_id}"]
    assert operation in {"send_message", "fetch_events", "resolve_approval"}


@pytest.mark.asyncio
async def test_phone_can_revoke_its_own_session() -> None:
    adapter = PairingAdapter()
    service = PairingService(adapter, now=Clock())
    claim = service.create_claim("owner-1", identity())
    credentials = await service.claim(
        claim_id=claim.claim_id,
        code=claim.code,
        device_name="Fictional phone",
        confirmed_backend_fingerprint=claim.backend.fingerprint,
        accepted_capabilities=("conversation",),
    )

    await service.revoke_by_phone(credentials.access_token)

    assert service.devices[credentials.device_session_id].revoked_at is not None
    with pytest.raises(PairingRejected):
        service.authenticate_access(credentials.access_token)
