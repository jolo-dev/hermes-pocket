# Hermes Pocket

Hermes Pocket is a consent-first iOS and Android companion for a user-controlled agent. The repository is split into independently testable projects:

- `mobile/`: React Native 0.87 and TypeScript application with owned Android and iOS projects.
- `service/`: FastAPI facade, deterministic policy, and backend adapters.
- `contracts/`: versioned mobile API schemas and shared fictional fixtures.
- `infra/`: AWS CDK deployment definitions.
- `docs/`: threat model, platform disclosures, and operator documentation.

Toolchain versions are pinned in `.tool-versions`. No mobile binary or pairing payload may contain AWS, AgentCore, model-provider, push-provider, or signing credentials.

The mobile project does not use Expo Go. Its Gradle project, Xcode application target, and Xcode Share Extension target are committed source. The current development build provides a tested local shell and typed privacy boundaries; pairing, remote conversations, share staging, and native device integrations remain incomplete unless their OpenSpec tasks are checked.

## Install on a phone

Hermes Pocket is currently an in-development scaffold; it is not a released or pairable consumer app yet. See [the development-preview installation guide](docs/install-on-phone.md) for accurate Android and iPhone build/install steps, platform limits, and safety notes.
