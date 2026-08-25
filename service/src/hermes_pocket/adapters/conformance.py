from __future__ import annotations

from collections.abc import Awaitable, Callable

from hermes_pocket.adapters.base import (
    AdapterMessage,
    AgentBackend,
    BackendErrorCategory,
    BackendFailure,
    EventType,
    PairingRequest,
)


class ConformanceFailure(RuntimeError):
    pass


async def _must_reject_revoked(operation: Callable[[], Awaitable[object]]) -> None:
    try:
        await operation()
    except BackendFailure as error:
        if error.category not in {
            BackendErrorCategory.AUTHENTICATION,
            BackendErrorCategory.AUTHORIZATION,
        }:
            raise ConformanceFailure("Revocation returned an unsafe error category") from error
    else:
        raise ConformanceFailure("Revoked session remained usable")


async def assert_adapter_conformance(adapter: AgentBackend) -> tuple[str, ...]:
    session = await adapter.pair(
        PairingRequest(
            device_id="conformance-device",
            owner_subject="conformance-owner",
            requested_capabilities=("conversation", "approvals", "tasks"),
        )
    )
    if not session.session_id or not session.backend_identity:
        raise ConformanceFailure("Pairing did not return a distinct backend session identity")

    message = AdapterMessage(
        request_id="conformance-request",
        correlation_id="conformance-correlation",
        conversation_id="conformance-conversation",
        reply_language="en",
        intent="Explain the fictional notice.",
        content="Bounded fictional content.",
        approved_capabilities=("explain",),
    )
    events = [event async for event in adapter.stream_message(session.session_id, message)]
    event_types = tuple(event.event_type for event in events)
    if not events or event_types[0] is not EventType.STARTED:
        raise ConformanceFailure("Stream did not start explicitly")
    if event_types[-1] is not EventType.COMPLETED:
        raise ConformanceFailure("Successful stream did not complete explicitly")
    if any(event.correlation_id != message.correlation_id for event in events):
        raise ConformanceFailure("Stream lost request correlation")
    if [event.sequence for event in events] != list(range(1, len(events) + 1)):
        raise ConformanceFailure("Stream events are not monotonically ordered")

    approvals = await adapter.list_approvals(session.session_id)
    if not approvals:
        raise ConformanceFailure("Approval listing did not return the conformance fixture")
    approval = approvals[0]
    first_resolution = await adapter.resolve_approval(
        session.session_id,
        approval.approval_id,
        "deny",
        approval.action_key,
    )
    repeated_resolution = await adapter.resolve_approval(
        session.session_id,
        approval.approval_id,
        "deny",
        approval.action_key,
    )
    if first_resolution != repeated_resolution:
        raise ConformanceFailure("Approval resolution is not idempotent")

    tasks = await adapter.list_tasks(session.session_id)
    if not tasks:
        raise ConformanceFailure("Task listing did not return the conformance fixture")

    await adapter.revoke_device(session.session_id)
    await _must_reject_revoked(lambda: adapter.list_approvals(session.session_id))
    await _must_reject_revoked(lambda: adapter.list_tasks(session.session_id))
    await _must_reject_revoked(
        lambda: adapter.resolve_approval(
            session.session_id,
            approval.approval_id,
            "deny",
            approval.action_key,
        )
    )

    async def consume_revoked_stream() -> object:
        return tuple(
            [event async for event in adapter.stream_message(session.session_id, message)]
        )

    await _must_reject_revoked(consume_revoked_stream)
    return (
        "pairing",
        "ordered_streaming",
        "correlated_events",
        "approval_listing",
        "idempotent_resolution",
        "task_listing",
        "normalized_errors",
        "revocation",
    )
