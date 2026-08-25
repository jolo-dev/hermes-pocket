from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from hermes_pocket.adapters.base import AdapterMessage, EventType, PairingRequest
from hermes_pocket.adapters.strands import (
    AgentCoreInvocation,
    RuntimeChunk,
    RuntimeChunkType,
    StrandsAdapter,
)


def structured_output(language: str) -> dict[str, object]:
    return {
        "language": language,
        "facts": [
            {
                "text": "A fictional notice is available.",
                "confidence": "high",
                "source_support": "supported",
            }
        ],
        "suggestions": [],
        "warnings": [],
        "uncertainties": [],
        "proposed_actions": [],
    }


class MockAgentCoreRuntime:
    def __init__(self, chunks: tuple[RuntimeChunk, ...]) -> None:
        self.chunks = chunks
        self.invocations: list[AgentCoreInvocation] = []

    async def invoke_agent(self, invocation: AgentCoreInvocation) -> AsyncIterator[RuntimeChunk]:
        self.invocations.append(invocation)
        for chunk in self.chunks:
            yield chunk


@pytest.mark.asyncio
@pytest.mark.parametrize("reply_language", ["en", "vi", "de"])
async def test_strands_preserves_event_order_correlation_and_language(
    reply_language: str,
) -> None:
    runtime = MockAgentCoreRuntime(
        (
            RuntimeChunk(RuntimeChunkType.FRAGMENT, text="Safe "),
            RuntimeChunk(RuntimeChunkType.FRAGMENT, text="response."),
            RuntimeChunk(
                RuntimeChunkType.COMPLETED,
                structured_output=structured_output(reply_language),
            ),
        )
    )
    adapter = StrandsAdapter(runtime, runtime_agent_id="configured-runtime-id")
    session = await adapter.pair(PairingRequest("device-1", "owner-1", ("conversation",)))
    message = AdapterMessage(
        request_id="request-1",
        correlation_id="correlation-1",
        conversation_id="conversation-1",
        reply_language=reply_language,
        intent="Explain safely.",
        content="Fictional content.",
        approved_capabilities=("explain",),
    )

    events = [event async for event in adapter.stream_message(session.session_id, message)]

    assert [event.sequence for event in events] == [1, 2, 3, 4]
    assert [event.event_type for event in events] == [
        EventType.STARTED,
        EventType.FRAGMENT,
        EventType.FRAGMENT,
        EventType.COMPLETED,
    ]
    assert {event.correlation_id for event in events} == {"correlation-1"}
    invocation = runtime.invocations[0]
    assert invocation.reply_language == reply_language
    assert invocation.correlation_id == "correlation-1"
    assert invocation.runtime_agent_id == "configured-runtime-id"
    assert invocation.tools == ()
    assert "proposed_actions" in invocation.required_output_fields


@pytest.mark.asyncio
async def test_runtime_failure_never_fabricates_completion() -> None:
    runtime = MockAgentCoreRuntime(
        (
            RuntimeChunk(RuntimeChunkType.FRAGMENT, text="Partial"),
            RuntimeChunk(RuntimeChunkType.FAILED, error_code="RUNTIME_UNAVAILABLE"),
        )
    )
    adapter = StrandsAdapter(runtime, runtime_agent_id="configured-runtime-id")
    session = await adapter.pair(PairingRequest("device-1", "owner-1", ("conversation",)))
    message = AdapterMessage(
        request_id="request-2",
        correlation_id="correlation-2",
        conversation_id="conversation-1",
        reply_language="en",
        intent="Explain safely.",
        content="Fictional content.",
        approved_capabilities=("explain",),
    )

    events = [event async for event in adapter.stream_message(session.session_id, message)]

    assert [event.event_type for event in events] == [
        EventType.STARTED,
        EventType.FRAGMENT,
        EventType.FAILED,
    ]
    assert all(event.correlation_id == "correlation-2" for event in events)
