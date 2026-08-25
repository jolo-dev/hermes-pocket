from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from pydantic import ValidationError

from hermes_pocket.policy.requests import AgentInput, InboundPolicyGateway


def valid_payload() -> dict[str, Any]:
    return {
        "metadata": {
            "request_id": "request-1",
            "device_session_id": "device-1",
            "policy_version": "v1",
            "interface_locale": "en",
            "reply_locale": "de",
        },
        "conversation_id": "conversation-1",
        "source": "user_text",
        "user_intent": "Explain the next safe step.",
        "content": "A bounded fictional notice.",
        "approved_capabilities": ["explain"],
    }


def test_validates_before_backend_invocation() -> None:
    received: list[AgentInput] = []
    gateway = InboundPolicyGateway(lambda request: received.append(request) or "accepted")

    result = gateway.submit(valid_payload())

    assert result == "accepted"
    assert len(received) == 1
    assert isinstance(received[0], AgentInput)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("raw_screen", "screen contents"),
        ("accessibility_tree", {"node": "unbounded"}),
        ("installed_apps", ["com.fictional.private"]),
        ("raw_document", "document dump"),
    ],
)
def test_undeclared_device_dumps_never_reach_backend(field: str, value: object) -> None:
    calls: list[Mapping[str, Any]] = []
    gateway = InboundPolicyGateway(lambda request: calls.append(request.model_dump()))
    payload = {**valid_payload(), field: value}

    with pytest.raises(ValidationError):
        gateway.submit(payload)

    assert calls == []


@pytest.mark.parametrize(
    "payload",
    [
        {**valid_payload(), "content": "x" * 65537},
        {
            **valid_payload(),
            "source": "screen_help",
            "content": "x" * 12001,
            "foreground_category": "browser",
        },
        {**valid_payload(), "source": "screen_help", "content": "safe"},
        {**valid_payload(), "source": "document_ocr", "content": "safe"},
        {
            **valid_payload(),
            "source": "explicit_share",
            "selected_part_ids": [f"part-{index}" for index in range(13)],
        },
        {**valid_payload(), "source": "continuous_accessibility"},
    ],
)
def test_unbounded_or_unclassified_sources_never_reach_backend(payload: dict[str, Any]) -> None:
    calls: list[AgentInput] = []
    gateway = InboundPolicyGateway(lambda request: calls.append(request))

    with pytest.raises(ValidationError):
        gateway.submit(payload)

    assert calls == []
