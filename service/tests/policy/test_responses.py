from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from hermes_pocket.policy.responses import ResponsePolicyRejected, validate_model_response
from hermes_pocket.policy.sensitive import SensitiveDataRejected


def valid_response() -> dict[str, Any]:
    return {
        "language": "en",
        "facts": [
            {
                "text": "The fictional notice names a deadline.",
                "confidence": "high",
                "source_support": "supported",
            }
        ],
        "suggestions": ["Verify the date in the original notice."],
        "warnings": [],
        "uncertainties": [],
        "proposed_actions": [],
    }


@pytest.mark.parametrize(
    "action_class",
    [
        "payment",
        "purchase",
        "contract_acceptance",
        "claim_submission",
        "form_submission",
        "credential_entry",
        "cross_app_typing",
        "account_change",
        "send_message",
    ],
)
def test_prohibited_action_outputs_are_blocked(action_class: str) -> None:
    payload = {
        **valid_response(),
        "proposed_actions": [{"action_class": action_class, "summary": "Do it now."}],
    }

    with pytest.raises(ResponsePolicyRejected) as error:
        validate_model_response(payload)

    assert error.value.blocked_classes == (action_class,)


def test_unknown_action_output_fails_closed() -> None:
    payload = {
        **valid_response(),
        "proposed_actions": [{"action_class": "future_tool", "summary": "Unknown effect."}],
    }

    with pytest.raises(ResponsePolicyRejected):
        validate_model_response(payload)


def test_low_or_unsupported_claims_are_downgraded_to_uncertainty() -> None:
    payload = {
        **valid_response(),
        "facts": [
            {
                "text": "The deadline may be 3 November.",
                "confidence": "low",
                "source_support": "supported",
            },
            {"text": "The amount is 20 units.", "confidence": "high", "source_support": "partial"},
            {
                "text": "The issuer is Example Workshop.",
                "confidence": "medium",
                "source_support": "supported",
            },
        ],
    }

    result = validate_model_response(payload)

    assert result.facts == ("The issuer is Example Workshop.",)
    assert result.uncertainties == (
        "Requires verification: The deadline may be 3 November.",
        "Requires verification: The amount is 20 units.",
    )


def test_structured_response_rejects_undeclared_fields() -> None:
    with pytest.raises(ValidationError):
        validate_model_response({**valid_response(), "tool_calls": ["send"]})


def test_sensitive_model_output_is_not_returned() -> None:
    sensitive_value = "Fictional!Secret27"
    payload = {
        **valid_response(),
        "suggestions": [f"Use password: {sensitive_value}"],
    }

    with pytest.raises(SensitiveDataRejected) as error:
        validate_model_response(payload)

    assert sensitive_value not in str(error.value)
