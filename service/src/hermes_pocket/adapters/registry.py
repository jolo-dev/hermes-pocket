from __future__ import annotations

from dataclasses import dataclass

from hermes_pocket.adapters.base import AgentBackend
from hermes_pocket.adapters.conformance import assert_adapter_conformance

REQUIRED_CONFORMANCE_CASES = frozenset(
    {
        "pairing",
        "ordered_streaming",
        "correlated_events",
        "approval_listing",
        "idempotent_resolution",
        "task_listing",
        "normalized_errors",
        "revocation",
    }
)
RELEASE_ADAPTERS = frozenset({"strands"})


@dataclass(frozen=True, slots=True)
class AdapterEvidence:
    api_contract_reference: str
    authentication_contract_reference: str
    api_contract_verified: bool
    authentication_contract_verified: bool


class AdapterRegistrationRejected(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Adapter registration rejected ({code}).")


class AdapterRegistry:
    def __init__(self, enabled_names: frozenset[str]) -> None:
        self._enabled_names = enabled_names
        self._adapters: dict[str, AgentBackend] = {}

    async def register(self, adapter: AgentBackend, evidence: AdapterEvidence) -> None:
        if adapter.name not in self._enabled_names:
            raise AdapterRegistrationRejected("ADAPTER_NOT_ENABLED")
        if (
            not evidence.api_contract_verified
            or not evidence.authentication_contract_verified
            or not evidence.api_contract_reference.startswith("https://")
            or not evidence.authentication_contract_reference.startswith("https://")
        ):
            raise AdapterRegistrationRejected("EVIDENCE_UNVERIFIED")
        completed_cases = frozenset(await assert_adapter_conformance(adapter))
        if not REQUIRED_CONFORMANCE_CASES.issubset(completed_cases):
            raise AdapterRegistrationRejected("CONFORMANCE_INCOMPLETE")
        self._adapters[adapter.name] = adapter

    def select(self, name: str) -> AgentBackend:
        adapter = self._adapters.get(name)
        if adapter is None:
            raise AdapterRegistrationRejected("ADAPTER_UNAVAILABLE")
        return adapter

    @property
    def advertised_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))


def release_registry() -> AdapterRegistry:
    return AdapterRegistry(RELEASE_ADAPTERS)
