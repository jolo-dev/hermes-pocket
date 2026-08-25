# Hermes Pocket

Hermes Pocket is a consent-first iOS and Android companion for a user-controlled agent. The repository is split into independently testable projects:

- `mobile/`: Flutter application and narrow Android/iOS integrations.
- `service/`: FastAPI facade, deterministic policy, and backend adapters.
- `contracts/`: versioned mobile API schemas and shared fictional fixtures.
- `infra/`: AWS CDK deployment definitions.
- `docs/`: threat model, platform disclosures, and operator documentation.

Toolchain versions are pinned in `.tool-versions`. No mobile binary or pairing payload may contain AWS, AgentCore, model-provider, push-provider, or signing credentials.
