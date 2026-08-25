from __future__ import annotations

import asyncio
import hashlib
import hmac
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from hermes_pocket.adapters.base import AgentBackend, PairingRequest


@dataclass(frozen=True, slots=True)
class BackendIdentity:
    name: str
    fingerprint: str
    facade_origin: str
    requested_capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PairingClaim:
    claim_id: str
    code: str
    backend: BackendIdentity
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class SessionCredentials:
    device_session_id: str
    access_token: str
    access_expires_at: datetime
    renewal_token: str
    renewal_expires_at: datetime
    backend: BackendIdentity


@dataclass(slots=True)
class DeviceRecord:
    device_session_id: str
    device_name: str
    owner_subject: str
    adapter_session_id: str
    backend: BackendIdentity
    accepted_capabilities: tuple[str, ...]
    revoked_at: datetime | None = None
    push_association: str | None = None
    consumed_request_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class _ClaimRecord:
    claim_id: str
    code_hash: str
    owner_subject: str
    backend: BackendIdentity
    expires_at: datetime
    claimed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class _AccessRecord:
    device_session_id: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class _RenewalRecord:
    device_session_id: str
    expires_at: datetime


class PairingRejected(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Pairing or session credential rejected ({code}).")


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class PairingService:
    def __init__(
        self,
        adapter: AgentBackend,
        *,
        now: Callable[[], datetime] | None = None,
        claim_ttl: timedelta = timedelta(minutes=5),
        access_ttl: timedelta = timedelta(minutes=5),
        renewal_ttl: timedelta = timedelta(days=30),
    ) -> None:
        self._adapter = adapter
        self._now = now or (lambda: datetime.now(UTC))
        self._claim_ttl = claim_ttl
        self._access_ttl = access_ttl
        self._renewal_ttl = renewal_ttl
        self._claims: dict[str, _ClaimRecord] = {}
        self._access: dict[str, _AccessRecord] = {}
        self._renewals: dict[str, _RenewalRecord] = {}
        self.devices: dict[str, DeviceRecord] = {}
        self._lock = asyncio.Lock()

    def create_claim(self, owner_subject: str, backend: BackendIdentity) -> PairingClaim:
        claim_id = token_urlsafe(18)
        code = token_urlsafe(32)
        expires_at = self._now() + self._claim_ttl
        self._claims[claim_id] = _ClaimRecord(
            claim_id=claim_id,
            code_hash=_token_hash(code),
            owner_subject=owner_subject,
            backend=backend,
            expires_at=expires_at,
        )
        return PairingClaim(claim_id=claim_id, code=code, backend=backend, expires_at=expires_at)

    def inspect_claim(self, claim_id: str, code: str) -> PairingClaim:
        record = self._valid_claim(claim_id, code)
        return PairingClaim(
            claim_id=record.claim_id,
            code="",
            backend=record.backend,
            expires_at=record.expires_at,
        )

    def _valid_claim(self, claim_id: str, code: str) -> _ClaimRecord:
        record = self._claims.get(claim_id)
        if record is None or not hmac.compare_digest(record.code_hash, _token_hash(code)):
            raise PairingRejected("CLAIM_INVALID")
        if record.claimed_at is not None:
            raise PairingRejected("CLAIM_USED")
        if record.expires_at <= self._now():
            raise PairingRejected("CLAIM_EXPIRED")
        return record

    def _issue_credentials(self, device: DeviceRecord) -> SessionCredentials:
        now = self._now()
        access_token = token_urlsafe(32)
        renewal_token = token_urlsafe(48)
        access_expires_at = now + self._access_ttl
        renewal_expires_at = now + self._renewal_ttl
        self._access[_token_hash(access_token)] = _AccessRecord(
            device.device_session_id, access_expires_at
        )
        self._renewals[_token_hash(renewal_token)] = _RenewalRecord(
            device.device_session_id, renewal_expires_at
        )
        return SessionCredentials(
            device_session_id=device.device_session_id,
            access_token=access_token,
            access_expires_at=access_expires_at,
            renewal_token=renewal_token,
            renewal_expires_at=renewal_expires_at,
            backend=device.backend,
        )

    async def claim(
        self,
        *,
        claim_id: str,
        code: str,
        device_name: str,
        confirmed_backend_fingerprint: str,
        accepted_capabilities: tuple[str, ...],
    ) -> SessionCredentials:
        async with self._lock:
            record = self._valid_claim(claim_id, code)
            if not hmac.compare_digest(
                record.backend.fingerprint, confirmed_backend_fingerprint
            ):
                raise PairingRejected("BACKEND_IDENTITY_MISMATCH")
            if not set(accepted_capabilities).issubset(record.backend.requested_capabilities):
                raise PairingRejected("CAPABILITY_SCOPE_INVALID")
            backend_session = await self._adapter.pair(
                PairingRequest(
                    device_id=claim_id,
                    owner_subject=record.owner_subject,
                    requested_capabilities=accepted_capabilities,
                )
            )
            now = self._now()
            record.claimed_at = now
            device_session_id = token_urlsafe(24)
            device = DeviceRecord(
                device_session_id=device_session_id,
                device_name=device_name[:80],
                owner_subject=record.owner_subject,
                adapter_session_id=backend_session.session_id,
                backend=record.backend,
                accepted_capabilities=accepted_capabilities,
            )
            self.devices[device_session_id] = device
            return self._issue_credentials(device)

    def authenticate_access(self, access_token: str) -> DeviceRecord:
        token_digest = _token_hash(access_token)
        record = self._access.get(token_digest)
        if record is None or record.expires_at <= self._now():
            self._access.pop(token_digest, None)
            raise PairingRejected("ACCESS_INVALID")
        device = self.devices.get(record.device_session_id)
        if device is None or device.revoked_at is not None:
            raise PairingRejected("DEVICE_REVOKED")
        return device

    async def refresh(self, renewal_token: str) -> SessionCredentials:
        async with self._lock:
            token_digest = _token_hash(renewal_token)
            record = self._renewals.pop(token_digest, None)
            if record is None or record.expires_at <= self._now():
                raise PairingRejected("RENEWAL_INVALID")
            device = self.devices.get(record.device_session_id)
            if device is None or device.revoked_at is not None:
                raise PairingRejected("DEVICE_REVOKED")
            return self._issue_credentials(device)

    def consume_request_id(self, device_session_id: str, request_id: str) -> None:
        device = self.devices.get(device_session_id)
        if device is None or device.revoked_at is not None:
            raise PairingRejected("DEVICE_REVOKED")
        if request_id in device.consumed_request_ids:
            raise PairingRejected("REQUEST_REPLAYED")
        if len(device.consumed_request_ids) >= 2048:
            raise PairingRejected("REPLAY_WINDOW_EXHAUSTED")
        device.consumed_request_ids.add(request_id)

    def set_push_association(self, device_session_id: str, association: str) -> None:
        device = self.devices.get(device_session_id)
        if device is None or device.revoked_at is not None:
            raise PairingRejected("DEVICE_REVOKED")
        device.push_association = association

    async def _revoke(self, device: DeviceRecord) -> None:
        if device.revoked_at is not None:
            return
        device.revoked_at = self._now()
        device.push_association = None
        self._access = {
            digest: record
            for digest, record in self._access.items()
            if record.device_session_id != device.device_session_id
        }
        self._renewals = {
            digest: record
            for digest, record in self._renewals.items()
            if record.device_session_id != device.device_session_id
        }
        await self._adapter.revoke_device(device.adapter_session_id)

    async def revoke_by_phone(self, access_token: str) -> None:
        async with self._lock:
            device = self.authenticate_access(access_token)
            await self._revoke(device)

    async def revoke_by_owner(self, owner_subject: str, device_session_id: str) -> None:
        async with self._lock:
            device = self.devices.get(device_session_id)
            if device is None or not hmac.compare_digest(device.owner_subject, owner_subject):
                raise PairingRejected("DEVICE_NOT_FOUND")
            await self._revoke(device)
