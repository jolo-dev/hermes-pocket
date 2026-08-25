from __future__ import annotations

import logging
from typing import Any

import pytest

from hermes_pocket.policy.requests import AgentInput, InboundPolicyGateway
from hermes_pocket.policy.sensitive import (
    SensitiveCategory,
    SensitiveDataRejected,
    sanitize_for_model,
)


def payload_with(content: str) -> dict[str, Any]:
    return {
        "metadata": {
            "request_id": "sensitive-test-1",
            "device_session_id": "device-1",
            "policy_version": "v1",
            "interface_locale": "en",
            "reply_locale": "en",
        },
        "conversation_id": "conversation-1",
        "source": "user_text",
        "user_intent": "Explain this safely.",
        "content": content,
        "approved_capabilities": ["explain"],
    }


@pytest.mark.parametrize(
    ("content", "value", "category"),
    [
        ("password: Fictional!Secret27", "Fictional!Secret27", SensitiveCategory.PASSWORD),
        ("verification code is 483921", "483921", SensitiveCategory.OTP),
        ("recovery code ABCD-EFGH-IJKL", "ABCD-EFGH-IJKL", SensitiveCategory.RECOVERY_CODE),
        ("CVV: 731", "731", SensitiveCategory.CARD),
        ("account number: 12345678901", "12345678901", SensitiveCategory.BANK),
    ],
)
def test_labeled_secret_values_are_redacted(
    content: str, value: str, category: SensitiveCategory
) -> None:
    result = sanitize_for_model(content)

    assert value not in result.text
    assert category in result.categories
    assert f"[REDACTED:{category.value.upper()}]" in result.text


def test_valid_card_and_iban_are_redacted_without_labels() -> None:
    card = "".join(["4242"] * 4)
    iban = "".join(["DE89", "3704", "0044", "0532", "0130", "00"])

    result = sanitize_for_model(f"Values {card} and {iban}")

    assert card not in result.text
    assert iban not in result.text
    assert set(result.categories) == {SensitiveCategory.CARD, SensitiveCategory.BANK}


def test_sensitive_values_never_reach_model_mock_logs_or_errors(
    caplog: logging.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    sensitive_value = "Fictional!Secret27"
    model_inputs: list[AgentInput] = []
    gateway = InboundPolicyGateway(lambda request: model_inputs.append(request))

    gateway.submit(payload_with(f"password: {sensitive_value}"))
    logging.getLogger("hermes_pocket.policy").info(
        "content_sanitized",
        extra={"request_id": "sensitive-test-1", "category": "password"},
    )

    assert sensitive_value not in model_inputs[0].content
    assert sensitive_value not in caplog.text

    with pytest.raises(SensitiveDataRejected) as error:
        sanitize_for_model("password: " + "x" * 130)
    assert sensitive_value not in str(error.value)
    assert "x" * 20 not in str(error.value)


def test_many_sensitive_values_fail_closed_before_model_mock() -> None:
    model_inputs: list[AgentInput] = []
    gateway = InboundPolicyGateway(lambda request: model_inputs.append(request))
    content = " ".join(f"OTP: {1000 + index}" for index in range(21))

    with pytest.raises(SensitiveDataRejected):
        gateway.submit(payload_with(content))

    assert model_inputs == []
