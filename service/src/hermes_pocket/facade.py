from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pydantic import Field

from hermes_pocket.adapters.base import AdapterMessage, AgentBackend, BackendEvent
from hermes_pocket.adapters.registry import RELEASE_ADAPTERS
from hermes_pocket.pairing import (
    DeviceRecord,
    PairingRejected,
    PairingService,
    SessionCredentials,
)
from hermes_pocket.policy.requests import (
    AgentInput,
    Capability,
    InboundPolicyGateway,
    RequestMetadata,
    SourceClass,
    StrictModel,
)


class PairingInspectBody(StrictModel):
    claim_id: str = Field(min_length=1, max_length=128)
    pairing_code: str = Field(min_length=16, max_length=256)


class PairingClaimBody(PairingInspectBody):
    device_name: str = Field(min_length=1, max_length=80)
    confirmed_backend_fingerprint: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    accepted_capabilities: tuple[str, ...] = Field(max_length=16)


class RenewalBody(StrictModel):
    renewal_token: str = Field(min_length=32, max_length=4096)


class MessageBody(StrictModel):
    metadata: RequestMetadata
    conversation_id: str = Field(min_length=1, max_length=128)
    client_message_id: str = Field(min_length=1, max_length=128)
    source: SourceClass
    text: str = Field(min_length=1, max_length=16000)
    approved_capabilities: tuple[Capability, ...] = Field(max_length=8)


class ContextPart(StrictModel):
    part_id: str = Field(min_length=1, max_length=128)
    kind: str = Field(pattern=r"^(text|url|image|screenshot|pdf|voice_note)$")
    text: str | None = Field(default=None, max_length=65536)
    upload_id: str | None = Field(default=None, max_length=128)


class ConsentReceipt(StrictModel):
    receipt_id: str = Field(min_length=1, max_length=128)
    content_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    purpose: str = Field(pattern=r"^(explain|translate|summarize|conversation)$")
    destination_session_id: str = Field(min_length=1, max_length=128)
    approved_part_ids: tuple[str, ...] = Field(min_length=1, max_length=12)
    issued_at: datetime
    expires_at: datetime


class ContextShareBody(StrictModel):
    metadata: RequestMetadata
    conversation_id: str = Field(min_length=1, max_length=128)
    source: SourceClass
    purpose: str = Field(pattern=r"^(explain|translate|summarize|conversation)$")
    parts: tuple[ContextPart, ...] = Field(min_length=1, max_length=12)
    consent: ConsentReceipt


class ApprovalDecisionBody(StrictModel):
    metadata: RequestMetadata
    decision: str = Field(pattern=r"^(allow|deny)$")
    scope: str | None = Field(default=None, pattern=r"^(one_time|conversation|bounded_duration)$")
    action_key: str = Field(min_length=1, max_length=128)


class PrivacyDeleteBody(StrictModel):
    metadata: RequestMetadata
    category: str = Field(pattern=r"^(conversation|document|share|memory)$")
    record_ids: tuple[str, ...] = Field(min_length=1, max_length=100)
    delete_remote: bool


class MemoryConsentBody(StrictModel):
    metadata: RequestMetadata
    category: str = Field(pattern=r"^(reminder_summary|conversation_preference)$")
    enabled: bool
    retention_days: int = Field(ge=1, le=365)


@dataclass(slots=True)
class FacadeState:
    pairing: PairingService
    adapter: AgentBackend
    events: dict[str, list[BackendEvent]] = field(default_factory=dict)
    conversations: dict[str, set[str]] = field(default_factory=dict)
    privacy_records: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)
    memory_consents: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.adapter.name not in RELEASE_ADAPTERS:
            raise ValueError("The selected adapter is not enabled in release configuration")


def _credentials_payload(credentials: SessionCredentials) -> dict[str, Any]:
    return cast(dict[str, Any], jsonable_encoder(asdict(credentials)))


def create_facade_router(state: FacadeState) -> APIRouter:
    router = APIRouter(prefix="/v1")

    def authenticate(authorization: str | None = Header(default=None)) -> DeviceRecord:
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        try:
            return state.pairing.authenticate_access(authorization.removeprefix("Bearer "))
        except PairingRejected as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED) from error

    def verify_metadata(device: DeviceRecord, metadata: RequestMetadata) -> None:
        if metadata.device_session_id != device.device_session_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
        state.pairing.consume_request_id(device.device_session_id, metadata.request_id)

    @router.get("/version")
    async def version(x_api_version: Annotated[str, Header()] = "v1") -> dict[str, Any]:
        if x_api_version != "v1":
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE)
        return {
            "supported_versions": ["v1"],
            "minimum_client_version": "0.1.0",
            "enabled_capabilities": [
                "conversation",
                "explicit_share",
                "documents",
                "approvals",
                "tasks",
                "privacy",
            ],
            "available_adapters": [state.adapter.name],
        }

    @router.post("/pairing/inspect")
    async def inspect_pairing(body: PairingInspectBody) -> dict[str, Any]:
        try:
            claim = state.pairing.inspect_claim(body.claim_id, body.pairing_code)
        except PairingRejected as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST) from error
        return cast(
            dict[str, Any],
            jsonable_encoder(
                {
                    "claim_id": claim.claim_id,
                    "backend": asdict(claim.backend),
                    "expires_at": claim.expires_at,
                }
            ),
        )

    @router.post("/pairing/claim", status_code=status.HTTP_201_CREATED)
    async def claim_pairing(body: PairingClaimBody) -> dict[str, Any]:
        try:
            credentials = await state.pairing.claim(
                claim_id=body.claim_id,
                code=body.pairing_code,
                device_name=body.device_name,
                confirmed_backend_fingerprint=body.confirmed_backend_fingerprint,
                accepted_capabilities=body.accepted_capabilities,
            )
        except PairingRejected as error:
            raise HTTPException(status.HTTP_409_CONFLICT) from error
        return _credentials_payload(credentials)

    @router.post("/sessions/renew")
    async def renew_session(body: RenewalBody) -> dict[str, Any]:
        try:
            return _credentials_payload(await state.pairing.refresh(body.renewal_token))
        except PairingRejected as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED) from error

    @router.get("/conversations")
    async def list_conversations(
        device: DeviceRecord = Depends(authenticate),
    ) -> list[str]:
        return sorted(state.conversations.get(device.device_session_id, set()))

    @router.post("/conversations/{conversation_id}/messages", status_code=status.HTTP_202_ACCEPTED)
    async def send_message(
        body: MessageBody,
        conversation_id: Annotated[str, Path(max_length=128)],
        device: DeviceRecord = Depends(authenticate),
    ) -> list[dict[str, Any]]:
        verify_metadata(device, body.metadata)
        if body.conversation_id != conversation_id:
            raise HTTPException(status.HTTP_409_CONFLICT)
        sanitized = InboundPolicyGateway[AgentInput](lambda request: request).submit(
            {
                "metadata": body.metadata.model_dump(),
                "conversation_id": conversation_id,
                "source": body.source,
                "user_intent": body.text,
                "content": body.text,
                "approved_capabilities": body.approved_capabilities,
            }
        )
        adapter_message = AdapterMessage(
            request_id=body.metadata.request_id,
            correlation_id=body.metadata.request_id,
            conversation_id=conversation_id,
            reply_language=body.metadata.reply_locale,
            intent=sanitized.user_intent,
            content=sanitized.content,
            approved_capabilities=tuple(sanitized.approved_capabilities),
        )
        events = [
            event
            async for event in state.adapter.stream_message(
                device.adapter_session_id, adapter_message
            )
        ]
        state.events.setdefault(device.device_session_id, []).extend(events)
        state.conversations.setdefault(device.device_session_id, set()).add(conversation_id)
        return cast(
            list[dict[str, Any]], jsonable_encoder([asdict(event) for event in events])
        )

    @router.post(
        "/conversations/{conversation_id}/context-shares",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def share_context(
        body: ContextShareBody,
        conversation_id: Annotated[str, Path(max_length=128)],
        device: DeviceRecord = Depends(authenticate),
    ) -> dict[str, str]:
        verify_metadata(device, body.metadata)
        if body.conversation_id != conversation_id:
            raise HTTPException(status.HTTP_409_CONFLICT)
        if body.consent.expires_at <= datetime.now(body.consent.expires_at.tzinfo):
            raise HTTPException(status.HTTP_409_CONFLICT)
        selected = set(body.consent.approved_part_ids)
        if selected != {part.part_id for part in body.parts}:
            raise HTTPException(status.HTTP_409_CONFLICT)
        joined_text = "\n".join(part.text or "[BINARY_PART]" for part in body.parts)
        InboundPolicyGateway[AgentInput](lambda request: request).submit(
            {
                "metadata": body.metadata.model_dump(),
                "conversation_id": conversation_id,
                "source": body.source,
                "user_intent": body.purpose,
                "content": joined_text,
                "approved_capabilities": [body.purpose],
                "selected_part_ids": body.consent.approved_part_ids,
                "selected_page_ids": body.consent.approved_part_ids
                if body.source is SourceClass.DOCUMENT_OCR
                else [],
                "foreground_category": "other"
                if body.source is SourceClass.SCREEN_HELP
                else None,
            }
        )
        record_id = body.consent.receipt_id
        state.privacy_records.setdefault(device.device_session_id, {})[record_id] = {
            "record_id": record_id,
            "category": "share",
            "location": "facade",
        }
        state.conversations.setdefault(device.device_session_id, set()).add(conversation_id)
        return {"record_id": record_id, "status": "accepted"}

    @router.get("/events/sync")
    async def sync_events(
        after_sequence: int = 0,
        device: DeviceRecord = Depends(authenticate),
    ) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            jsonable_encoder(
                [
                    asdict(event)
                    for event in state.events.get(device.device_session_id, [])
                    if event.sequence > after_sequence
                ]
            ),
        )

    @router.get("/events")
    async def stream_events(
        device: DeviceRecord = Depends(authenticate),
    ) -> StreamingResponse:
        async def encoded_events() -> AsyncIterator[str]:
            for event in state.events.get(device.device_session_id, []):
                encoded = json.dumps(jsonable_encoder(asdict(event)))
                yield f"id: {event.event_id}\ndata: {encoded}\n\n"

        return StreamingResponse(encoded_events(), media_type="text/event-stream")

    @router.get("/approvals")
    async def list_approvals(
        device: DeviceRecord = Depends(authenticate),
    ) -> list[dict[str, Any]]:
        approvals = await state.adapter.list_approvals(device.adapter_session_id)
        return cast(
            list[dict[str, Any]],
            jsonable_encoder([asdict(approval) for approval in approvals]),
        )

    @router.post("/approvals/{approval_id}/decision")
    async def resolve_approval(
        body: ApprovalDecisionBody,
        approval_id: Annotated[str, Path(max_length=128)],
        device: DeviceRecord = Depends(authenticate),
    ) -> dict[str, Any]:
        verify_metadata(device, body.metadata)
        result = await state.adapter.resolve_approval(
            device.adapter_session_id,
            approval_id,
            body.decision,
            body.action_key,
        )
        return cast(dict[str, Any], jsonable_encoder(asdict(result)))

    @router.get("/tasks")
    async def list_tasks(
        device: DeviceRecord = Depends(authenticate),
    ) -> list[dict[str, Any]]:
        tasks = await state.adapter.list_tasks(device.adapter_session_id)
        return cast(
            list[dict[str, Any]], jsonable_encoder([asdict(task) for task in tasks])
        )

    @router.get("/privacy/records")
    async def list_privacy_records(
        device: DeviceRecord = Depends(authenticate),
    ) -> list[dict[str, str]]:
        return list(state.privacy_records.get(device.device_session_id, {}).values())

    @router.delete(
        "/privacy/records",
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
    )
    async def delete_privacy_records(
        body: Annotated[PrivacyDeleteBody, Body()],
        device: DeviceRecord = Depends(authenticate),
    ) -> None:
        verify_metadata(device, body.metadata)
        records = state.privacy_records.setdefault(device.device_session_id, {})
        for record_id in body.record_ids:
            records.pop(record_id, None)

    @router.put(
        "/privacy/memory-consent",
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
    )
    async def set_memory_consent(
        body: MemoryConsentBody,
        device: DeviceRecord = Depends(authenticate),
    ) -> None:
        verify_metadata(device, body.metadata)
        state.memory_consents.setdefault(device.device_session_id, {})[body.category] = {
            "enabled": body.enabled,
            "retention_days": body.retention_days,
        }

    @router.delete(
        "/devices/me",
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
    )
    async def revoke_current_device(
        authorization: Annotated[str, Header()],
        device: DeviceRecord = Depends(authenticate),
    ) -> None:
        del device
        await state.pairing.revoke_by_phone(authorization.removeprefix("Bearer "))

    return router
