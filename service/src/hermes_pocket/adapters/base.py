from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class BackendErrorCategory(StrEnum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    UNAVAILABLE = "unavailable"
    INVALID_RESPONSE = "invalid_response"
    INTERNAL = "internal"


class BackendFailure(RuntimeError):
    def __init__(
        self,
        code: str,
        category: BackendErrorCategory,
        *,
        retryable: bool = False,
    ) -> None:
        self.code = code
        self.category = category
        self.retryable = retryable
        super().__init__(f"Backend operation failed ({code}).")


@dataclass(frozen=True, slots=True)
class PairingRequest:
    device_id: str
    owner_subject: str
    requested_capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BackendSession:
    session_id: str
    backend_identity: str


@dataclass(frozen=True, slots=True)
class AdapterMessage:
    request_id: str
    correlation_id: str
    conversation_id: str
    reply_language: str
    intent: str
    content: str
    approved_capabilities: tuple[str, ...]


class EventType(StrEnum):
    STARTED = "response_started"
    FRAGMENT = "response_fragment"
    COMPLETED = "response_completed"
    FAILED = "response_failed"


@dataclass(frozen=True, slots=True)
class BackendEvent:
    event_id: str
    sequence: int
    event_type: EventType
    correlation_id: str
    fragment: str | None = None
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class BackendApproval:
    approval_id: str
    status: str
    action_key: str


@dataclass(frozen=True, slots=True)
class BackendTask:
    task_id: str
    status: str
    title: str


class AgentBackend(Protocol):
    name: str

    async def pair(self, request: PairingRequest) -> BackendSession: ...

    def stream_message(
        self,
        session_id: str,
        message: AdapterMessage,
    ) -> AsyncIterator[BackendEvent]: ...

    async def list_approvals(self, session_id: str) -> tuple[BackendApproval, ...]: ...

    async def resolve_approval(
        self,
        session_id: str,
        approval_id: str,
        decision: str,
        action_key: str,
    ) -> BackendApproval: ...

    async def list_tasks(self, session_id: str) -> tuple[BackendTask, ...]: ...

    async def revoke_device(self, session_id: str) -> None: ...
