from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from hermes_pocket.policy.requests import StrictModel
from hermes_pocket.policy.sensitive import SensitiveDataRejected, sanitize_for_model


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceSupport(StrEnum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class Claim(StrictModel):
    text: str = Field(min_length=1, max_length=2000)
    confidence: Confidence
    source_support: SourceSupport


class ProposedAction(StrictModel):
    action_class: str = Field(min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9_]*$")
    summary: str = Field(min_length=1, max_length=1000)


class ModelResponse(StrictModel):
    language: str = Field(pattern=r"^(en|vi|de)$")
    facts: tuple[Claim, ...] = Field(default=(), max_length=32)
    suggestions: tuple[str, ...] = Field(default=(), max_length=16)
    warnings: tuple[str, ...] = Field(default=(), max_length=16)
    uncertainties: tuple[str, ...] = Field(default=(), max_length=16)
    proposed_actions: tuple[ProposedAction, ...] = Field(default=(), max_length=8)


class SafeResponse(StrictModel):
    language: str
    facts: tuple[str, ...]
    suggestions: tuple[str, ...]
    warnings: tuple[str, ...]
    uncertainties: tuple[str, ...]
    proposed_actions: tuple[ProposedAction, ...]


PROHIBITED_ACTIONS = frozenset(
    {
        "payment",
        "purchase",
        "contract_acceptance",
        "claim_submission",
        "form_submission",
        "credential_entry",
        "cross_app_typing",
        "account_change",
        "send_message",
    }
)
ALLOWED_PROPOSALS = frozenset(
    {
        "create_local_reminder_draft",
        "open_destination_proposal",
        "bounded_backend_read_proposal",
    }
)


class ResponsePolicyRejected(ValueError):
    def __init__(self, blocked_classes: tuple[str, ...]) -> None:
        self.blocked_classes = blocked_classes
        super().__init__("The backend response contains a blocked action class.")


def _assert_content_safe(values: tuple[str, ...]) -> None:
    for value in values:
        result = sanitize_for_model(value)
        if result.redaction_count:
            raise SensitiveDataRejected(result.categories)


def validate_model_response(payload: dict[str, Any]) -> SafeResponse:
    response = ModelResponse.model_validate(payload)
    blocked = tuple(
        sorted(
            {
                action.action_class
                for action in response.proposed_actions
                if action.action_class in PROHIBITED_ACTIONS
                or action.action_class not in ALLOWED_PROPOSALS
            }
        )
    )
    if blocked:
        raise ResponsePolicyRejected(blocked)

    fact_text: list[str] = []
    uncertainties = list(response.uncertainties)
    for claim in response.facts:
        if (
            claim.confidence is Confidence.LOW
            or claim.source_support is not SourceSupport.SUPPORTED
        ):
            uncertainties.append(f"Requires verification: {claim.text}")
        else:
            fact_text.append(claim.text)

    all_text = (
        tuple(fact_text)
        + response.suggestions
        + response.warnings
        + tuple(uncertainties)
        + tuple(action.summary for action in response.proposed_actions)
    )
    _assert_content_safe(all_text)

    return SafeResponse(
        language=response.language,
        facts=tuple(fact_text),
        suggestions=response.suggestions,
        warnings=response.warnings,
        uncertainties=tuple(uncertainties),
        proposed_actions=response.proposed_actions,
    )
