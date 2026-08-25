from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import StrEnum
from secrets import token_urlsafe
from typing import Any, Protocol

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
from hermes_pocket.policy.prompt import ModelRequest, build_model_request
from hermes_pocket.policy.requests import AgentInput
from hermes_pocket.policy.responses import validate_model_response


class RuntimeChunkType(StrEnum):
    FRAGMENT = "fragment"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RuntimeChunk:
    chunk_type: RuntimeChunkType
    text: str | None = None
    structured_output: dict[str, Any] | None = None
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class AgentCoreInvocation:
    runtime_agent_id: str
    backend_session_id: str
    request_id: str
    correlation_id: str
    reply_language: str
    messages: tuple[dict[str, str], dict[str, str]]
    required_output_fields: tuple[str, ...]
    tools: tuple[()] = ()


class AgentCoreRuntime(Protocol):
    def invoke_agent(self, invocation: AgentCoreInvocation) -> AsyncIterator[RuntimeChunk]: ...


class StrandsAdapter:
    name = "strands"
    _supported_languages = frozenset({"en", "vi", "de"})

    def __init__(self, runtime: AgentCoreRuntime, *, runtime_agent_id: str) -> None:
        if not runtime_agent_id:
            raise ValueError("AgentCore runtime agent ID is required")
        self._runtime = runtime
        self._runtime_agent_id = runtime_agent_id
        self._sessions: set[str] = set()
        self._approvals: dict[str, BackendApproval] = {}
        self._tasks: dict[str, BackendTask] = {}

    def _require_session(self, session_id: str) -> None:
        if session_id not in self._sessions:
            raise BackendFailure("SESSION_INVALID", BackendErrorCategory.AUTHENTICATION)

    async def pair(self, request: PairingRequest) -> BackendSession:
        session_id = f"strands-{token_urlsafe(24)}"
        self._sessions.add(session_id)
        return BackendSession(session_id=session_id, backend_identity="Strands on AgentCore")

    def _model_request(self, message: AdapterMessage) -> ModelRequest:
        if message.reply_language not in self._supported_languages:
            raise BackendFailure("LANGUAGE_UNSUPPORTED", BackendErrorCategory.INVALID_RESPONSE)
        request = AgentInput.model_validate(
            {
                "metadata": {
                    "request_id": message.request_id,
                    "device_session_id": "adapter-session",
                    "policy_version": "v1",
                    "interface_locale": "en",
                    "reply_locale": message.reply_language,
                },
                "conversation_id": message.conversation_id,
                "source": "user_text",
                "user_intent": message.intent,
                "content": message.content,
                "approved_capabilities": message.approved_capabilities,
            }
        )
        return build_model_request(request)

    async def stream_message(
        self,
        session_id: str,
        message: AdapterMessage,
    ) -> AsyncIterator[BackendEvent]:
        self._require_session(session_id)
        model_request = self._model_request(message)
        invocation = AgentCoreInvocation(
            runtime_agent_id=self._runtime_agent_id,
            backend_session_id=session_id,
            request_id=message.request_id,
            correlation_id=message.correlation_id,
            reply_language=message.reply_language,
            messages=model_request.messages(),
            required_output_fields=(
                "language",
                "facts",
                "suggestions",
                "warnings",
                "uncertainties",
                "proposed_actions",
            ),
        )
        sequence = 1
        yield BackendEvent(
            event_id=f"{message.correlation_id}:{sequence}",
            sequence=sequence,
            event_type=EventType.STARTED,
            correlation_id=message.correlation_id,
        )
        completed = False
        async for chunk in self._runtime.invoke_agent(invocation):
            sequence += 1
            if chunk.chunk_type is RuntimeChunkType.FRAGMENT and chunk.text is not None:
                yield BackendEvent(
                    event_id=f"{message.correlation_id}:{sequence}",
                    sequence=sequence,
                    event_type=EventType.FRAGMENT,
                    correlation_id=message.correlation_id,
                    fragment=chunk.text,
                )
            elif (
                chunk.chunk_type is RuntimeChunkType.COMPLETED
                and chunk.structured_output is not None
            ):
                validate_model_response(chunk.structured_output)
                completed = True
                yield BackendEvent(
                    event_id=f"{message.correlation_id}:{sequence}",
                    sequence=sequence,
                    event_type=EventType.COMPLETED,
                    correlation_id=message.correlation_id,
                )
                break
            else:
                yield BackendEvent(
                    event_id=f"{message.correlation_id}:{sequence}",
                    sequence=sequence,
                    event_type=EventType.FAILED,
                    correlation_id=message.correlation_id,
                    error_code=chunk.error_code or "RUNTIME_STREAM_INVALID",
                )
                break
        if not completed and sequence == 1:
            yield BackendEvent(
                event_id=f"{message.correlation_id}:2",
                sequence=2,
                event_type=EventType.FAILED,
                correlation_id=message.correlation_id,
                error_code="RUNTIME_STREAM_ENDED",
            )

    async def list_approvals(self, session_id: str) -> tuple[BackendApproval, ...]:
        self._require_session(session_id)
        return tuple(self._approvals.values())

    async def resolve_approval(
        self,
        session_id: str,
        approval_id: str,
        decision: str,
        action_key: str,
    ) -> BackendApproval:
        self._require_session(session_id)
        existing = self._approvals.get(action_key)
        if existing is not None and existing.status != "pending":
            return existing
        resolved = BackendApproval(
            approval_id=approval_id,
            status="denied" if decision == "deny" else "allowed",
            action_key=action_key,
        )
        self._approvals[action_key] = resolved
        return resolved

    async def list_tasks(self, session_id: str) -> tuple[BackendTask, ...]:
        self._require_session(session_id)
        return tuple(self._tasks.values())

    async def revoke_device(self, session_id: str) -> None:
        self._require_session(session_id)
        self._sessions.remove(session_id)
