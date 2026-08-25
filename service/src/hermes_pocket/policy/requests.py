from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hermes_pocket.policy.sensitive import sanitize_for_model


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class SourceClass(StrEnum):
    USER_TEXT = "user_text"
    EXPLICIT_SHARE = "explicit_share"
    DOCUMENT_OCR = "document_ocr"
    SCREEN_HELP = "screen_help"
    VOICE_NOTE = "voice_note"


class Capability(StrEnum):
    EXPLAIN = "explain"
    TRANSLATE = "translate"
    SUMMARIZE = "summarize"
    DRAFT = "draft"
    PROPOSE_REMINDER = "propose_reminder"
    OPEN_CONFIRMED_DESTINATION = "open_confirmed_destination"


class RequestMetadata(StrictModel):
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    device_session_id: str = Field(
        min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"
    )
    policy_version: str = Field(pattern=r"^v[1-9][0-9]{0,3}$")
    interface_locale: str = Field(pattern=r"^(en|vi|de)$")
    reply_locale: str = Field(pattern=r"^(en|vi|de)$")


class AgentInput(StrictModel):
    metadata: RequestMetadata
    conversation_id: str = Field(min_length=1, max_length=128)
    source: SourceClass
    user_intent: str = Field(min_length=1, max_length=2000)
    content: str = Field(min_length=1, max_length=65536)
    approved_capabilities: tuple[Capability, ...] = Field(min_length=1, max_length=8)
    selected_part_ids: tuple[str, ...] = Field(default=(), max_length=12)
    selected_page_ids: tuple[str, ...] = Field(default=(), max_length=20)
    foreground_category: str | None = Field(
        default=None,
        pattern=r"^(communication|document|browser|commerce|travel|other)$",
    )

    @model_validator(mode="after")
    def enforce_source_shape(self) -> AgentInput:
        if self.source is SourceClass.SCREEN_HELP:
            if self.foreground_category is None:
                raise ValueError("screen_help requires a coarse foreground category")
            if len(self.content) > 12000:
                raise ValueError("screen_help sanitized text exceeds its source bound")
        elif self.foreground_category is not None:
            raise ValueError("foreground category is allowed only for screen_help")

        if self.source is SourceClass.DOCUMENT_OCR and not self.selected_page_ids:
            raise ValueError("document_ocr requires selected page identifiers")
        if self.source is SourceClass.EXPLICIT_SHARE and not self.selected_part_ids:
            raise ValueError("explicit_share requires selected part identifiers")
        return self


Result = TypeVar("Result")


class InboundPolicyGateway(Generic[Result]):
    def __init__(self, invoke_backend: Callable[[AgentInput], Result]) -> None:
        self._invoke_backend = invoke_backend

    def submit(self, payload: Mapping[str, Any]) -> Result:
        validated = AgentInput.model_validate(payload)
        sanitized = sanitize_for_model(validated.content)
        return self._invoke_backend(validated.model_copy(update={"content": sanitized.text}))
